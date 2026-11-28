from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

Num = Annotated[float, Field(allow_inf_nan=False)]
Ms = Annotated[float, Field(allow_inf_nan=False, ge=0)]


class PinTap(BaseModel):
    """One PIN key tap. Time in ms, coordinates in px."""

    key: str = Field(max_length=2)
    t_down: Ms
    t_up: Ms
    x: Num
    y: Num
    w: Num = 0  # touch area size (PointerEvent.width/height)
    h: Num = 0
    key_cx: Num  # key center
    key_cy: Num
    key_w: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    key_h: Annotated[float, Field(gt=0, allow_inf_nan=False)]

    @model_validator(mode="after")
    def _order(self):
        if self.t_up < self.t_down:
            raise ValueError("t_up must be >= t_down")
        return self


class Point(BaseModel):
    t: Ms
    x: Num
    y: Num


class Swipe(BaseModel):
    points: list[Point] = Field(min_length=2, max_length=200)  # ~3 s of swiping at 60 Hz; longer ones are truncated by the SDK


class ScreenVisit(BaseModel):
    name: str = Field(max_length=32)
    t_enter: Ms
    t_first_touch: Ms | None = None


class InputEvent(BaseModel):
    """One change in an input field. Carries NO content: only time, kind and character count."""

    t: Ms  # ms since session start
    # key: typed character; paste: pasted; delete: deleted; set_text: text changed with NO key event (e.g. Accessibility ACTION_SET_TEXT)
    kind: Literal["key", "paste", "delete", "set_text"]
    n: int = Field(default=1, ge=0, le=500)  # number of characters changed
    cls: Literal["digit", "letter", "space", "symbol"] | None = None  # character class (key only), the character itself is not sent


class TextField(BaseModel):
    """One input field of the transaction: amount, recipient, transfer note, name."""

    # challenge = phrase generated and shown by the system, retyped by the user (see docs/plan/innate-challenge.md)
    name: Literal["amount", "recipient", "note", "name", "challenge"]
    expected_len: int | None = Field(default=None, ge=1, le=200)  # length of the challenge phrase (only to detect paste/direct set)
    token: str | None = Field(default=None, max_length=200)  # token from GET /challenge: the server knows the phrase without the typed content
    token_status: Literal["ok", "reused", "expired", "invalid"] | None = None  # set by the server when a token is present; a client-sent value is overwritten
    events: list[InputEvent] = Field(default_factory=list, max_length=600)


Ident = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.\-]+$")]


class ParticipantIn(BaseModel):
    """Data-collection volunteer: only email and full name. Never a PIN."""

    participant_id: Ident
    email: Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
    full_name: str = Field(min_length=2, max_length=100)

    @model_validator(mode="after")
    def _clean_name(self):
        self.full_name = " ".join(self.full_name.split())
        if any(c.isdigit() for c in self.full_name):
            raise ValueError("full name must not contain digits")
        self.email = self.email.strip().lower()
        return self


class CollectionMeta(BaseModel):
    """Data-collection label. user_id = the account being operated; participant_id = the real person holding the device."""

    participant_id: Ident
    sitting: int = Field(ge=1, le=20)  # which collection round (1 = enrollment, 2+ = tests over time)
    # impostor: knows the PIN, tries to tap like the account owner; bot: session produced by the attacker simulator
    role: Literal["genuine", "impostor", "bot"]
    tactic: int | None = Field(default=None, ge=1, le=4)  # bot tactic 1–4 (only when role = bot)
    note: str | None = Field(default=None, max_length=200)
    # the collection page (#/collect) writes the participant's full name + email straight into the session (with consent); /v1/export returns both
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @model_validator(mode="after")
    def _tactic_only_for_bot(self):
        if (self.role == "bot") != (self.tactic is not None):
            raise ValueError("tactic is required when role = bot and is only allowed for bots")
        return self


class AttemptMeta(BaseModel):
    """Client-side attempt telemetry (no content): which flow, wrong/aborted tries before this entry, gap to the previous entry."""

    flow_stage: Literal["signup_enroll", "login_enroll", "transfer"] | None = None
    retries: int = Field(default=0, ge=0, le=50)
    client_dt_prev_ms: Annotated[float, Field(allow_inf_nan=False, ge=0, le=7 * 24 * 3600 * 1000)] | None = None


class SessionIn(BaseModel):
    """Interaction session sent by the SDK. Only time + coordinates, no PIN content."""

    user_id: Ident
    device_id: str = Field(default="unknown", max_length=64)
    pin_taps: list[PinTap] = Field(default_factory=list, max_length=12)
    swipes: list[Swipe] = Field(default_factory=list, max_length=30)
    screens: list[ScreenVisit] = Field(default_factory=list, max_length=50)
    fields: list[TextField] = Field(default_factory=list, max_length=10)  # input fields other than the PIN
    meta: CollectionMeta | None = None  # sent only during data collection
    attempt_meta: AttemptMeta | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "demo_user",
                "device_id": "demo_phone",
                "pin_taps": [
                    {"key": "1", "t_down": 0, "t_up": 95, "x": 66, "y": 395, "w": 40, "h": 40,
                     "key_cx": 60, "key_cy": 400, "key_w": 100, "key_h": 70},
                    {"key": "5", "t_down": 280, "t_up": 408, "x": 192, "y": 474, "w": 42, "h": 41,
                     "key_cx": 180, "key_cy": 480, "key_w": 100, "key_h": 70},
                    {"key": "9", "t_down": 640, "t_up": 722, "x": 313, "y": 553, "w": 39, "h": 40,
                     "key_cx": 300, "key_cy": 560, "key_w": 100, "key_h": 70},
                    {"key": "3", "t_down": 1010, "t_up": 1120, "x": 309, "y": 396, "w": 41, "h": 40,
                     "key_cx": 300, "key_cy": 400, "key_w": 100, "key_h": 70},
                ],
                "swipes": [
                    {"points": [{"t": 0, "x": 200, "y": 600}, {"t": 40, "x": 230, "y": 470},
                                {"t": 90, "x": 240, "y": 330}]}
                ],
                "screens": [{"name": "transfer", "t_enter": 0, "t_first_touch": 1200}],
            }
        }
    )


class SessionCreated(BaseModel):
    session_id: str
    n_features: int


class EnrollIn(BaseModel):
    session_id: str
    keep_open: bool = False  # true: do not lock at the 3rd attempt, wait for /enroll/finish (up to MAX_ENROLL attempts)


class EnrollOut(BaseModel):
    user_id: str
    enrolled_sessions: int
    template_ready: bool
    enroll_open: bool = True
    history_summary: dict | None = None  # enrolment telemetry: n_entries, dt_mean_sec, dt_cv, span_sec, client_dt_mean_ms
    consistency: float | None = None  # mean match score of each attempt against the template built from the other attempts


class SignupIn(BaseModel):
    email: str = Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=6, max_length=128)  # kept as is, including whitespace (login compares exactly as typed)
    full_name: str | None = Field(default=None, max_length=100)

    @field_validator("email", mode="before")
    @classmethod
    def _strip_email(cls, v):
        return v.strip() if isinstance(v, str) else v

    @model_validator(mode="after")
    def _norm(self):
        self.email = self.email.strip().lower()
        self.full_name = " ".join(self.full_name.split()) or None if self.full_name else None
        return self


class LoginIn(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class AccountOut(EnrollOut):
    email: str
    full_name: str | None = None


class UserOut(EnrollOut):
    template_updates: int


class ScoreContext(BaseModel):
    recipient_is_new: bool = False
    amount: Annotated[float, Field(ge=0, allow_inf_nan=False)] = 0


Action = Literal["allow", "step_up", "hold"]


class ScoreOut(BaseModel):
    session_id: str
    human_score: float
    owner_match: float | None  # None when the user has not completed enough enrollment attempts
    risk: Literal["low", "medium", "high"]
    risk_score: float
    action: Action
    reasons: list[str]
    explanation_vi: str


class LabelIn(BaseModel):
    label: Literal["fraud", "legit"]


class SessionSummary(BaseModel):
    session_id: str
    user_id: str
    created_at: str
    action: Action | None
    risk_score: float | None
    reasons: list[str]
    explanation_vi: str | None
    label: str | None
