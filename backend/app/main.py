import json
import os
import secrets
import time
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, Response, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import schemas
from .db import DATABASE_URL, Base, ChallengeNonce, SessionLocal, TouchSession, User, engine
from .scoring import challenge, explain, features, fusion, human, human_model, owner, owner_model, replay

def _keys(var: str, default: str = "") -> list[str]:
    return [k.strip() for k in os.environ.get(var, default).split(",") if k.strip()]


# Mỗi vai trò một bộ key: key SDK nằm trong app web (ai cũng xem được) nên không được mở dashboard hay export.
# Key ops/ml không có mặc định: chưa cấu hình thì các route đó đóng.
# Key SDK chỉ mặc định "demo-key" khi chạy local (SQLite); nối DB thật mà quên đặt biến thì đóng hết, không mở bằng key công khai.
SCOPE_KEYS = {
    "sdk": _keys("NHIP_API_KEYS", "demo-key" if DATABASE_URL.startswith("sqlite") else ""),  # gửi phiên, đăng ký nhịp, chấm điểm
    "ops": _keys("NHIP_OPS_KEYS"),  # dashboard: xem danh sách, gắn nhãn
    "ml": _keys("NHIP_ML_KEYS"),  # Người 1: xuất dữ liệu
}
CORS_ORIGINS = os.environ.get("NHIP_CORS_ORIGINS", "*").split(",")
MIN_ENROLL = 3
EXPORT_BYTE_BUDGET = 3 * 1024 * 1024  # mỗi trang export dừng ở ~3 MB dữ liệu thô: dưới giới hạn phản hồi 4,5 MB của Vercel
UPDATE_MIN_OWNER = 0.8  # chỉ cập nhật mẫu chuẩn sau phiên được cho qua với điểm khớp cao
UPDATE_MIN_HUMAN = 0.8
REPLAY_HISTORY = 50  # số phiên gần nhất dùng để so trùng; FPR tăng theo số phiên (E5: PIN 4 số; E5b: người thật, ngoại suy ~0.7% ở 50 với ngưỡng 0.07)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Innate API",
    version="0.1.0",
    description="Chấm điểm rủi ro hành vi cho ví điện tử. Bấm **Authorize** và nhập API key demo.",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response


_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)


def _match(key: str, keys: list[str]) -> bool:
    # so bytes: compare_digest với str chứa ký tự ngoài ASCII sẽ ném TypeError (500 thay vì 401)
    return any(secrets.compare_digest(key.encode(), k.encode()) for k in keys)


def require(scope: str):
    def dep(key: str | None = Security(_api_key)) -> None:
        if key and _match(key, SCOPE_KEYS[scope]):
            return
        if key and any(_match(key, ks) for ks in SCOPE_KEYS.values()):
            raise HTTPException(403, f"API key không có quyền '{scope}' cho thao tác này")
        raise HTTPException(401, "API key không hợp lệ")
    return Depends(dep)


SDK, OPS, ML = require("sdk"), require("ops"), require("ml")


def get_db():
    with SessionLocal() as db:
        yield db


def _get_session(db: Session, session_id: str) -> TouchSession:
    s = db.get(TouchSession, session_id)
    if s is None:
        raise HTTPException(404, "Không tìm thấy phiên")
    return s


def _enroll_status(db: Session, user: User) -> dict:
    n = len(db.scalars(select(TouchSession.id).where(
        TouchSession.user_id == user.id, TouchSession.is_enrollment)).all())
    return {"user_id": user.id, "enrolled_sessions": n, "template_ready": user.template is not None}


@app.get("/", include_in_schema=False)
def root():
    """Không còn ví demo web: trang gốc chuyển sang Swagger."""
    return RedirectResponse("/docs")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


v1 = APIRouter(prefix="/v1")


@v1.get("/challenge", tags=["sdk"], dependencies=[SDK])
def get_challenge():
    """Cấp câu thử thách tiếng Việt + token ký. App hiển thị câu, người dùng gõ lại, gửi events kèm `token` trong fields[name=challenge]."""
    return challenge.issue()


def _consume_challenge_tokens(db: Session, raw: dict) -> None:
    """Gắn `token_status` (ok | reused | expired | invalid) cho mỗi token câu thử thách; token hợp lệ chỉ dùng được MỘT lần."""
    for fl in raw.get("fields", []):
        if not fl.get("token"):
            continue
        p = challenge.parse(fl["token"])
        if p is None:
            fl["token_status"] = "invalid"
        elif p[1] < time.time():
            fl["token_status"] = "expired"
        else:
            try:
                with db.begin_nested():
                    db.add(ChallengeNonce(nonce=p[2]))
                fl["token_status"] = "ok"
            except IntegrityError:
                fl["token_status"] = "reused"


@v1.post("/sessions", response_model=schemas.SessionCreated, tags=["sdk"], dependencies=[SDK])
def create_session(body: schemas.SessionIn, db: Session = Depends(get_db)):
    """SDK gửi phiên thao tác (chạm PIN, vuốt, nhịp màn hình)."""
    raw = body.model_dump()
    _consume_challenge_tokens(db, raw)
    feats = features.extract(raw)
    if db.get(User, body.user_id) is None:
        try:
            with db.begin_nested():  # flush ngay để hàng users có trước khi chèn sessions (khoá ngoại)
                db.add(User(id=body.user_id))
        except IntegrityError:
            pass  # request khác vừa tạo cùng user
    sid = "s_" + secrets.token_hex(6)
    db.add(TouchSession(id=sid, user_id=body.user_id, device_id=body.device_id, raw=raw, features=feats))
    db.commit()
    return {"session_id": sid, "n_features": len(feats)}


@v1.post("/users/{user_id}/enroll", response_model=schemas.EnrollOut, tags=["sdk"], dependencies=[SDK])
def enroll(user_id: str, body: schemas.EnrollIn, db: Session = Depends(get_db)):
    """Đánh dấu một phiên là lượt đăng ký nhịp. Đủ 3 lượt thì dựng mẫu chuẩn và khoá đăng ký."""
    s = _get_session(db, body.session_id)
    if s.user_id != user_id:
        raise HTTPException(400, "Phiên không thuộc người dùng này")
    if "pin_hold_0" not in s.features:
        raise HTTPException(400, "Phiên đăng ký phải có thao tác nhập PIN")
    user = db.get(User, user_id)
    if user.template is not None:
        # chặn kẻ gian chèn nhịp của mình vào mẫu chuẩn đã có; đăng ký lại phải qua luồng đặt lại có xác thực
        raise HTTPException(409, "Tài khoản đã đăng ký nhịp, không thể thêm lượt đăng ký")
    s.is_enrollment = True
    db.flush()
    enrolled = db.scalars(select(TouchSession).where(
        TouchSession.user_id == user_id, TouchSession.is_enrollment)).all()
    if len(enrolled) >= MIN_ENROLL:
        user.template = owner.build_template([e.features for e in enrolled])
    db.commit()
    return _enroll_status(db, user)


@v1.get("/users/{user_id}", response_model=schemas.UserOut, tags=["sdk"], dependencies=[SDK])
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "Không tìm thấy người dùng")
    return {**_enroll_status(db, user), "template_updates": (user.template or {}).get("updates", 0)}


@v1.post("/sessions/{session_id}/score", response_model=schemas.ScoreOut, tags=["sdk"], dependencies=[SDK])
def score_session(session_id: str, ctx: schemas.ScoreContext, db: Session = Depends(get_db)):
    """Chấm điểm phiên ở bước xác nhận giao dịch. Hệ thống chỉ đề xuất, không tự khoá tài khoản."""
    s = _get_session(db, session_id)
    user = db.get(User, s.user_id)
    tpl = user.template
    feats = s.features

    h, bot_reasons = human.score(feats)
    # mô hình học (tuỳ chọn): chỉ thay luật khi luật không có đủ dữ liệu, còn lại lấy điểm bi quan hơn
    p = human_model.predict(s.raw)
    if p is not None:
        h = p if bot_reasons == ["insufficient_data"] else min(h, p)
        if p < 0.5 and not [r for r in bot_reasons if r in explain._BOT_VI]:
            bot_reasons = [*bot_reasons, "ml_bot_pattern"]
    # phát lại: gần như y hệt một phiên cũ của chính tài khoản này (người thật không lặp lại nhịp)
    past = db.scalars(select(TouchSession.features).where(
        TouchSession.user_id == s.user_id, TouchSession.id != s.id)
        .order_by(TouchSession.created_at.desc()).limit(REPLAY_HISTORY)).all()
    if replay.is_replay(feats, past):
        h, bot_reasons = min(h, 0.1), [*bot_reasons, "replayed_session"]
    o, z = owner.score(feats, tpl) if tpl else (None, {})
    if o:  # mô hình học (tuỳ chọn) thay điểm khoảng cách khi áp dụng được; o == 0 là thiếu bằng chứng PIN: giữ nguyên
        m = owner_model.predict(z)
        o = o if m is None else m
    history = [c["amount"] for c in db.scalars(select(TouchSession.context).where(
        TouchSession.user_id == s.user_id, TouchSession.action == "allow",
        TouchSession.id != s.id)).all() if c]
    amt = fusion.amount_anomaly(ctx.amount, history)
    risk, action, _ = fusion.fuse(h, o, ctx.recipient_is_new, amt)
    reasons, text = explain.explain(h, bot_reasons, o, feats, tpl, z, ctx.recipient_is_new, amt, action)

    result = {
        "session_id": s.id,
        "human_score": round(h, 3),
        "owner_match": None if o is None else round(o, 3),
        "risk": {"allow": "low", "step_up": "medium", "hold": "high"}[action],
        "risk_score": round(risk, 3),
        "action": action,
        "reasons": reasons,
        "explanation_vi": text,
    }

    first_score = s.result is None
    s.context, s.result, s.risk, s.action = ctx.model_dump(), result, risk, action
    if (first_score and tpl and not s.is_enrollment and action == "allow"
            and o is not None and o >= UPDATE_MIN_OWNER and h >= UPDATE_MIN_HUMAN):
        user.template = owner.update(tpl, feats)
    db.commit()
    return result


@v1.get("/sessions", response_model=list[schemas.SessionSummary], tags=["dashboard"], dependencies=[OPS])
def list_sessions(flagged: bool = True, limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    """Danh sách phiên cho dashboard. flagged=true: chỉ phiên step_up/hold."""
    # lọc theo action (cột chuỗi): cột JSON lưu None thành 'null' nên IS NOT NULL không loại được phiên chưa chấm
    q = select(TouchSession).where(TouchSession.action.is_not(None))
    if flagged:
        q = q.where(TouchSession.action.in_(["step_up", "hold"]))
    rows = db.scalars(q.order_by(TouchSession.created_at.desc()).limit(limit)).all()
    return [{
        "session_id": r.id,
        "user_id": r.user_id,
        "created_at": r.created_at.isoformat(),
        "action": r.action,
        "risk_score": r.risk,
        "reasons": r.result["reasons"],
        "explanation_vi": r.result["explanation_vi"],
        "label": r.label,
    } for r in rows]


@v1.get("/export", tags=["data"], dependencies=[ML])
def export_sessions(response: Response, participant_id: str | None = None, collected_only: bool = True,
                    limit: int = Query(500, ge=1, le=2000), offset: int = Query(0, ge=0),
                    db: Session = Depends(get_db)):
    """Xuất phiên cho Người 1, cũ nhất trước, theo trang.

    Còn dữ liệu thì header `X-Next-Offset` cho biết offset của trang sau; không có header là hết.
    """
    # shortcut: lọc meta bằng Python trên từng trang; trang và ngân sách byte giữ bộ nhớ có giới hạn
    q = select(TouchSession).order_by(TouchSession.created_at, TouchSession.id).offset(offset).limit(limit)
    out, size, scanned = [], 0, 0
    for r in db.scalars(q, execution_options={"yield_per": 100}):  # nạp dần, không .all() cả trang
        scanned += 1
        meta = r.raw.get("meta")
        if collected_only and not meta:
            continue
        if participant_id and (meta or {}).get("participant_id") != participant_id:
            continue
        out.append({"session_id": r.id, "user_id": r.user_id, "device_id": r.device_id,
                    "created_at": r.created_at.isoformat(), "meta": meta, "raw": r.raw,
                    "features": r.features, "is_enrollment": r.is_enrollment, "result": r.result,
                    "label": r.label})
        size += len(json.dumps(r.raw)) + len(json.dumps(r.features))
        if size >= EXPORT_BYTE_BUDGET:
            break
    if scanned == limit or size >= EXPORT_BYTE_BUDGET:
        response.headers["X-Next-Offset"] = str(offset + scanned)
    return out


@v1.post("/sessions/{session_id}/label", tags=["dashboard"], dependencies=[OPS])
def label_session(session_id: str, body: schemas.LabelIn, db: Session = Depends(get_db)):
    """Chuyên viên đánh dấu đúng (fraud) / sai (legit). Lưu lại để huấn luyện sau."""
    s = _get_session(db, session_id)
    s.label = body.label
    db.commit()
    return {"session_id": s.id, "label": s.label}


app.include_router(v1)
