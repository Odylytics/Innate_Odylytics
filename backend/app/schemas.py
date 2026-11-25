from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Num = Annotated[float, Field(allow_inf_nan=False)]
Ms = Annotated[float, Field(allow_inf_nan=False, ge=0)]


class PinTap(BaseModel):
    """Một lần chạm phím PIN. Thời gian tính bằng ms, toạ độ bằng px."""

    key: str = Field(max_length=2)
    t_down: Ms
    t_up: Ms
    x: Num
    y: Num
    w: Num = 0  # kích thước vùng chạm (PointerEvent.width/height)
    h: Num = 0
    key_cx: Num  # tâm phím
    key_cy: Num
    key_w: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    key_h: Annotated[float, Field(gt=0, allow_inf_nan=False)]

    @model_validator(mode="after")
    def _order(self):
        if self.t_up < self.t_down:
            raise ValueError("t_up phải >= t_down")
        return self


class Point(BaseModel):
    t: Ms
    x: Num
    y: Num


class Swipe(BaseModel):
    points: list[Point] = Field(min_length=2, max_length=200)  # ~3 s vuốt ở 60 Hz; dài hơn thì SDK cắt bớt


class ScreenVisit(BaseModel):
    name: str = Field(max_length=32)
    t_enter: Ms
    t_first_touch: Ms | None = None


class InputEvent(BaseModel):
    """Một thay đổi trong ô nhập. KHÔNG chứa nội dung: chỉ thời gian, loại và số ký tự."""

    t: Ms  # ms từ đầu phiên
    # key: gõ ký tự; paste: dán; delete: xoá; set_text: văn bản đổi mà KHÔNG có sự kiện phím (vd. Trợ năng ACTION_SET_TEXT)
    kind: Literal["key", "paste", "delete", "set_text"]
    n: int = Field(default=1, ge=0, le=500)  # số ký tự thay đổi
    cls: Literal["digit", "letter", "space", "symbol"] | None = None  # lớp ký tự (chỉ với key), không gửi ký tự


class TextField(BaseModel):
    """Một ô nhập của giao dịch: số tiền, người nhận, nội dung chuyển khoản, tên."""

    # challenge = câu thử thách do hệ thống sinh và hiển thị, người dùng gõ lại (xem docs/plan/innate-challenge.md)
    name: Literal["amount", "recipient", "note", "name", "challenge"]
    expected_len: int | None = Field(default=None, ge=1, le=200)  # độ dài câu thử thách (chỉ để phát hiện dán/đặt thẳng)
    token: str | None = Field(default=None, max_length=200)  # token từ GET /challenge: máy chủ biết câu mà không cần nội dung gõ
    events: list[InputEvent] = Field(default_factory=list, max_length=600)


Ident = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.\-]+$")]


class CollectionMeta(BaseModel):
    """Nhãn thu dữ liệu. user_id = tài khoản bị thao tác; participant_id = người thật đang cầm máy."""

    participant_id: Ident
    sitting: int = Field(ge=1, le=20)  # lần ngồi thứ mấy (1 = đăng ký, 2+ = kiểm thử theo thời gian)
    # impostor: biết PIN, cố bấm giống chủ tài khoản; bot: phiên do bộ giả lập hacker sinh ra
    role: Literal["genuine", "impostor", "bot"]
    tactic: int | None = Field(default=None, ge=1, le=4)  # chiến thuật bot 1–4 (chỉ khi role = bot)
    note: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def _tactic_only_for_bot(self):
        if (self.role == "bot") != (self.tactic is not None):
            raise ValueError("tactic bắt buộc khi role = bot và chỉ dùng cho bot")
        return self


class SessionIn(BaseModel):
    """Phiên thao tác do SDK gửi lên. Chỉ thời gian + toạ độ, không có nội dung PIN."""

    user_id: Ident
    device_id: str = Field(default="unknown", max_length=64)
    pin_taps: list[PinTap] = Field(default_factory=list, max_length=12)
    swipes: list[Swipe] = Field(default_factory=list, max_length=30)
    screens: list[ScreenVisit] = Field(default_factory=list, max_length=50)
    fields: list[TextField] = Field(default_factory=list, max_length=10)  # ô nhập ngoài PIN
    meta: CollectionMeta | None = None  # chỉ gửi khi thu dữ liệu

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


class EnrollOut(BaseModel):
    user_id: str
    enrolled_sessions: int
    template_ready: bool


class UserOut(EnrollOut):
    template_updates: int


class ScoreContext(BaseModel):
    recipient_is_new: bool = False
    amount: Annotated[float, Field(ge=0, allow_inf_nan=False)] = 0


Action = Literal["allow", "step_up", "hold"]


class ScoreOut(BaseModel):
    session_id: str
    human_score: float
    owner_match: float | None  # None khi người dùng chưa đăng ký đủ lượt
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
