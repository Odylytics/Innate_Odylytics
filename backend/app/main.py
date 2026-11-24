import os
import secrets
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import schemas
from .db import Base, SessionLocal, TouchSession, User, engine
from .scoring import explain, features, fusion, human, owner, replay

API_KEYS = [k.strip() for k in os.environ.get("NHIP_API_KEYS", "demo-key").split(",") if k.strip()]
CORS_ORIGINS = os.environ.get("NHIP_CORS_ORIGINS", "*").split(",")
MIN_ENROLL = 3
UPDATE_MIN_OWNER = 0.8  # chỉ cập nhật mẫu chuẩn sau phiên được cho qua với điểm khớp cao
UPDATE_MIN_HUMAN = 0.8
REPLAY_HISTORY = 50  # số phiên gần nhất dùng để so trùng; nhiều hơn thì FPR của PIN 4 số tăng (research/results/e5_replay.md)


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


def require_key(key: str | None = Security(_api_key)) -> None:
    if not key or not any(secrets.compare_digest(key, k) for k in API_KEYS):
        raise HTTPException(401, "API key không hợp lệ")


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


_WALLET = (Path(__file__).parent / "static" / "wallet.html").read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def wallet():
    """Ví demo + SDK thu tín hiệu (một trang tĩnh)."""
    return _WALLET


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


v1 = APIRouter(prefix="/v1", dependencies=[Depends(require_key)])


@v1.post("/sessions", response_model=schemas.SessionCreated, tags=["sdk"])
def create_session(body: schemas.SessionIn, db: Session = Depends(get_db)):
    """SDK gửi phiên thao tác (chạm PIN, vuốt, nhịp màn hình)."""
    raw = body.model_dump()
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


@v1.post("/users/{user_id}/enroll", response_model=schemas.EnrollOut, tags=["sdk"])
def enroll(user_id: str, body: schemas.EnrollIn, db: Session = Depends(get_db)):
    """Đánh dấu một phiên là lượt đăng ký nhịp. Từ lượt thứ 3 trở đi, mẫu chuẩn được dựng lại từ mọi lượt đăng ký."""
    s = _get_session(db, body.session_id)
    if s.user_id != user_id:
        raise HTTPException(400, "Phiên không thuộc người dùng này")
    if "pin_hold_0" not in s.features:
        raise HTTPException(400, "Phiên đăng ký phải có thao tác nhập PIN")
    s.is_enrollment = True
    db.flush()
    enrolled = db.scalars(select(TouchSession).where(
        TouchSession.user_id == user_id, TouchSession.is_enrollment)).all()
    user = db.get(User, user_id)
    if len(enrolled) >= MIN_ENROLL:
        user.template = owner.build_template([e.features for e in enrolled])
    db.commit()
    return _enroll_status(db, user)


@v1.get("/users/{user_id}", response_model=schemas.UserOut, tags=["sdk"])
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "Không tìm thấy người dùng")
    return {**_enroll_status(db, user), "template_updates": (user.template or {}).get("updates", 0)}


@v1.post("/sessions/{session_id}/score", response_model=schemas.ScoreOut, tags=["sdk"])
def score_session(session_id: str, ctx: schemas.ScoreContext, db: Session = Depends(get_db)):
    """Chấm điểm phiên ở bước xác nhận giao dịch. Hệ thống chỉ đề xuất, không tự khoá tài khoản."""
    s = _get_session(db, session_id)
    user = db.get(User, s.user_id)
    tpl = user.template
    feats = s.features

    h, bot_reasons = human.score(feats)
    # phát lại: gần như y hệt một phiên cũ của chính tài khoản này (người thật không lặp lại nhịp)
    past = db.scalars(select(TouchSession.features).where(
        TouchSession.user_id == s.user_id, TouchSession.id != s.id)
        .order_by(TouchSession.created_at.desc()).limit(REPLAY_HISTORY)).all()
    if replay.is_replay(feats, past):
        h, bot_reasons = min(h, 0.1), [*bot_reasons, "replayed_session"]
    o, z = owner.score(feats, tpl) if tpl else (None, {})
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


@v1.get("/sessions", response_model=list[schemas.SessionSummary], tags=["dashboard"])
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


@v1.get("/export", tags=["data"])
def export_sessions(participant_id: str | None = None, collected_only: bool = True,
                    limit: int = Query(5000, ge=1, le=20000), db: Session = Depends(get_db)):
    """Xuất phiên cho Người 1 (dữ liệu thô + đặc trưng + nhãn thu dữ liệu), cũ nhất trước."""
    # shortcut: lọc meta bằng Python sau khi lấy; đủ cho vài nghìn phiên, nhiều hơn thì chuyển sang lọc trong SQL
    rows = db.scalars(select(TouchSession).order_by(TouchSession.created_at).limit(limit)).all()
    out = []
    for r in rows:
        meta = r.raw.get("meta")
        if collected_only and not meta:
            continue
        if participant_id and (meta or {}).get("participant_id") != participant_id:
            continue
        out.append({"session_id": r.id, "user_id": r.user_id, "device_id": r.device_id,
                    "created_at": r.created_at.isoformat(), "meta": meta, "raw": r.raw,
                    "features": r.features, "is_enrollment": r.is_enrollment, "result": r.result,
                    "label": r.label})
    return out


@v1.post("/sessions/{session_id}/label", tags=["dashboard"])
def label_session(session_id: str, body: schemas.LabelIn, db: Session = Depends(get_db)):
    """Chuyên viên đánh dấu đúng (fraud) / sai (legit). Lưu lại để huấn luyện sau."""
    s = _get_session(db, session_id)
    s.label = body.label
    db.commit()
    return {"session_id": s.id, "label": s.label}


app.include_router(v1)
