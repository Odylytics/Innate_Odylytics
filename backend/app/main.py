import hashlib
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
from .db import DATABASE_URL, Account, Base, ChallengeNonce, Participant, SessionLocal, TouchSession, User, engine
from .scoring import challenge, explain, features, fusion, human, human_model, owner, owner_model, replay

# preload both learned models at startup: avoids ~1 s on the first /score call (E26); if the library or file is missing, _load() falls back to the rules
human_model.loaded()
owner_model.loaded()

def _keys(var: str, default: str = "") -> list[str]:
    return [k.strip() for k in os.environ.get(var, default).split(",") if k.strip()]


# One key set per role: the SDK key sits in the web app (anyone can see it), so it must not open the dashboard or export.
# The ops/ml keys have no default: until configured, those routes stay closed.
# The SDK key defaults to "demo-key" only when running locally (SQLite); with a real DB and the variable unset, everything stays closed instead of opening with a public key.
SCOPE_KEYS = {
    "sdk": _keys("NHIP_API_KEYS", "demo-key" if DATABASE_URL.startswith("sqlite") else ""),  # submit sessions, rhythm enrollment, scoring
    "ops": _keys("NHIP_OPS_KEYS"),  # dashboard: list sessions, label them
    "ml": _keys("NHIP_ML_KEYS"),  # Member 1: data export
}
CORS_ORIGINS = os.environ.get("NHIP_CORS_ORIGINS", "*").split(",")
MIN_ENROLL = 3
MAX_ENROLL = 10  # open enrollment (keep_open) locks itself at this attempt
EXPORT_BYTE_BUDGET = 3 * 1024 * 1024  # each export page stops at ~3 MB of raw data: under Vercel's 4.5 MB response limit
UPDATE_MIN_OWNER = 0.8  # update the template only after a session that was allowed through with a high match score
UPDATE_MIN_HUMAN = 0.8
REPLAY_HISTORY = 50  # number of most recent sessions used for matching; FPR grows with the session count (E5: 4-digit PIN; E5b: real people, extrapolated ~0.7% at 50 with threshold 0.07)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Innate API",
    version="0.1.0",
    description="Behavioral risk scoring for e-wallets. Click **Authorize** and enter the demo API key.",
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
    # compare bytes: compare_digest on a str with non-ASCII characters raises TypeError (500 instead of 401)
    return any(secrets.compare_digest(key.encode(), k.encode()) for k in keys)


def require(scope: str):
    def dep(key: str | None = Security(_api_key)) -> None:
        if key and _match(key, SCOPE_KEYS[scope]):
            return
        if key and any(_match(key, ks) for ks in SCOPE_KEYS.values()):
            raise HTTPException(403, f"API key lacks the '{scope}' scope for this operation")
        raise HTTPException(401, "Invalid API key")
    return Depends(dep)


SDK, OPS, ML = require("sdk"), require("ops"), require("ml")


def get_db():
    with SessionLocal() as db:
        yield db


def _get_session(db: Session, session_id: str) -> TouchSession:
    s = db.get(TouchSession, session_id)
    if s is None:
        raise HTTPException(404, "Session not found")
    return s


def _enrolled(db: Session, user_id: str) -> list[TouchSession]:
    return db.scalars(select(TouchSession).where(
        TouchSession.user_id == user_id, TouchSession.is_enrollment).order_by(TouchSession.created_at)).all()


def _enroll_closed(user: User) -> bool:
    # an old template without the "open" flag => treat as locked (keeps the 409 security fix)
    return user.template is not None and not user.template.get("open", False)


def _enroll_status(db: Session, user: User) -> dict:
    enrolled = _enrolled(db, user.id)
    return {"user_id": user.id, "enrolled_sessions": len(enrolled), "template_ready": user.template is not None,
            "enroll_open": not _enroll_closed(user), "consistency": owner.consistency([e.features for e in enrolled])}


@app.get("/", include_in_schema=False)
def root():
    """The web demo wallet is gone: the root page redirects to Swagger."""
    return RedirectResponse("/docs")


@app.get("/health", tags=["system"])
def health():
    # models: whether the learned models loaded (false = running on rules/distance only, e.g. lightgbm or libgomp missing on the server)
    return {"status": "ok", "models": {"human": human_model.loaded(), "owner": owner_model.loaded()}}


v1 = APIRouter(prefix="/v1")


@v1.get("/challenge", tags=["sdk"], dependencies=[SDK])
def get_challenge():
    """Issue a Vietnamese challenge phrase + a signed token. The app shows the phrase, the user retypes it, and sends the events with `token` in fields[name=challenge]."""
    return challenge.issue()


@v1.post("/participants", tags=["sdk"], dependencies=[SDK])
def register_participant(body: schemas.ParticipantIn, db: Session = Depends(get_db)):
    """Data-collection page: stores the volunteer's email + full name (write-only, no read route for the SDK key)."""
    p = db.get(Participant, body.participant_id)
    if p is None:
        db.add(Participant(id=body.participant_id, email=body.email, full_name=body.full_name))
    else:
        p.email, p.full_name = body.email, body.full_name
    db.commit()
    return {"participant_id": body.participant_id}


def _consume_challenge_tokens(db: Session, raw: dict) -> None:
    """Set `token_status` (ok | reused | expired | invalid) on each challenge token; a valid token can be used only ONCE."""
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
    """The SDK submits an interaction session (PIN taps, swipes, screen rhythm)."""
    raw = body.model_dump()
    _consume_challenge_tokens(db, raw)
    feats = features.extract(raw)
    if db.get(User, body.user_id) is None:
        try:
            with db.begin_nested():  # flush now so the users row exists before inserting sessions (foreign key)
                db.add(User(id=body.user_id))
        except IntegrityError:
            pass  # another request just created the same user
    sid = "s_" + secrets.token_hex(6)
    db.add(TouchSession(id=sid, user_id=body.user_id, device_id=body.device_id, raw=raw, features=feats))
    db.commit()
    return {"session_id": sid, "n_features": len(feats)}


def _hash_pw(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    h = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${h.hex()}"


def _check_pw(password: str, stored: str) -> bool:
    _, salt, _ = stored.split("$")
    return secrets.compare_digest(_hash_pw(password, bytes.fromhex(salt)).encode(), stored.encode())


def _account_out(db: Session, a: Account) -> dict:
    return {**_enroll_status(db, db.get(User, a.user_id)), "email": a.email, "full_name": a.full_name}


@v1.post("/accounts/signup", response_model=schemas.AccountOut, tags=["sdk"], dependencies=[SDK])
def signup(body: schemas.SignupIn, db: Session = Depends(get_db)):
    """Create a demo app account: one account per email. The app then enrolls the rhythm for the returned user_id."""
    if db.get(Account, body.email) is not None:
        raise HTTPException(409, "This email already has an account")
    uid = "acct_" + secrets.token_hex(6)
    db.add(User(id=uid))
    db.flush()  # the users row must exist before accounts' foreign key
    a = Account(email=body.email, user_id=uid, full_name=body.full_name, password_hash=_hash_pw(body.password))
    db.add(a)
    try:
        db.commit()
    except IntegrityError:  # another request just registered the same email
        db.rollback()
        raise HTTPException(409, "This email already has an account")
    return _account_out(db, a)


@v1.post("/accounts/login", response_model=schemas.AccountOut, tags=["sdk"], dependencies=[SDK])
def login(body: schemas.LoginIn, db: Session = Depends(get_db)):
    """Log in with email + password. A wrong email and a wrong password return the same error."""
    a = db.get(Account, body.email.strip().lower())
    if a is None or not _check_pw(body.password, a.password_hash):
        raise HTTPException(401, "Wrong email or password")
    return _account_out(db, a)


@v1.post("/users/{user_id}/enroll", response_model=schemas.EnrollOut, tags=["sdk"], dependencies=[SDK])
def enroll(user_id: str, body: schemas.EnrollIn, db: Session = Depends(get_db)):
    """Mark a session as a rhythm enrollment attempt. After 3 attempts the template is built and enrollment is locked,
    unless keep_open=true: then each attempt rebuilds the template, locked when /enroll/finish is called or MAX_ENROLL attempts are reached."""
    s = _get_session(db, body.session_id)
    if s.user_id != user_id:
        raise HTTPException(400, "This session does not belong to this user")
    if "pin_hold_0" not in s.features:
        raise HTTPException(400, "An enrollment session must contain PIN taps")
    user = db.get(User, user_id)
    if _enroll_closed(user):
        # stop an attacker from injecting their own rhythm into an existing template; re-enrollment must go through an authenticated reset flow
        raise HTTPException(409, "This account is already enrolled; no more enrollment entries can be added")
    s.is_enrollment = True
    db.flush()
    enrolled = _enrolled(db, user_id)
    if len(enrolled) >= MIN_ENROLL:
        keep = body.keep_open and len(enrolled) < MAX_ENROLL
        user.template = {**owner.build_template([e.features for e in enrolled]), **({"open": True} if keep else {})}
    db.commit()
    return _enroll_status(db, user)


@v1.post("/users/{user_id}/enroll/finish", response_model=schemas.EnrollOut, tags=["sdk"], dependencies=[SDK])
def finish_enroll(user_id: str, db: Session = Depends(get_db)):
    """Lock open enrollment. Needs at least MIN_ENROLL attempts (a template exists)."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    if user.template is None:
        raise HTTPException(400, f"At least {MIN_ENROLL} enrollment entries are required")
    user.template = {k: v for k, v in user.template.items() if k != "open"}
    db.commit()
    return _enroll_status(db, user)


@v1.get("/users/{user_id}", response_model=schemas.UserOut, tags=["sdk"], dependencies=[SDK])
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    return {**_enroll_status(db, user), "template_updates": (user.template or {}).get("updates", 0)}


@v1.post("/sessions/{session_id}/score", response_model=schemas.ScoreOut, tags=["sdk"], dependencies=[SDK])
def score_session(session_id: str, ctx: schemas.ScoreContext, db: Session = Depends(get_db)):
    """Score the session at the transaction confirmation step. The system only recommends; it never locks the account itself."""
    s = _get_session(db, session_id)
    user = db.get(User, s.user_id)
    tpl = user.template
    feats = s.features

    h, bot_reasons = human.score(feats)
    # learned model (optional): replaces the rule only when the rule lacks data, otherwise take the more pessimistic score
    p = human_model.predict(s.raw)
    if p is not None:
        h = p if bot_reasons == ["insufficient_data"] else min(h, p)
        if p < 0.5 and not [r for r in bot_reasons if r in explain._BOT_VI]:
            bot_reasons = [*bot_reasons, "ml_bot_pattern"]
    # replay: nearly identical to an old session of this same account (a real person does not repeat the rhythm)
    past = db.scalars(select(TouchSession.features).where(
        TouchSession.user_id == s.user_id, TouchSession.id != s.id)
        .order_by(TouchSession.created_at.desc()).limit(REPLAY_HISTORY)).all()
    if replay.is_replay(feats, past):
        h, bot_reasons = min(h, 0.1), [*bot_reasons, "replayed_session"]
    o, z = owner.score(feats, tpl) if tpl else (None, {})
    if o:  # learned model (optional) replaces the distance score when applicable; o == 0 means missing PIN evidence: keep it as is
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
    """Session list for the dashboard. flagged=true: only step_up/hold sessions."""
    # filter by action (string column): the JSON column stores None as 'null', so IS NOT NULL would not exclude unscored sessions
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
    """Export sessions for Member 1, oldest first, paged.

    While data remains, the `X-Next-Offset` header gives the offset of the next page; no header means the end.
    """
    # shortcut: filter meta in Python per page; the page and byte budget keep memory bounded
    q = select(TouchSession).order_by(TouchSession.created_at, TouchSession.id).offset(offset).limit(limit)
    out, size, scanned = [], 0, 0
    for r in db.scalars(q, execution_options={"yield_per": 100}):  # load incrementally, not .all() for the whole page
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
    """An analyst marks it correct (fraud) / wrong (legit). Stored for later training."""
    s = _get_session(db, session_id)
    s.label = body.label
    db.commit()
    return {"session_id": s.id, "label": s.label}


app.include_router(v1)
