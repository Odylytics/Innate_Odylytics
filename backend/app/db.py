import datetime as dt
import os

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# SQLite khi chạy local; trên Vercel, Neon tự đặt DATABASE_URL (postgres://... hoặc postgresql://...)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./nhip.db")
for _prefix in ("postgres://", "postgresql://"):
    if DATABASE_URL.startswith(_prefix):
        DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len(_prefix):]

if DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}
else:
    _connect_args = {"prepare_threshold": None}  # URL pooled của Neon chạy pgbouncer chế độ transaction, không giữ được prepared statement

engine = create_engine(DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _sqlite_fk(dbapi_conn, _):
        # SQLite mặc định không kiểm tra khoá ngoại; bật để test bắt được lỗi giống Postgres
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(engine, expire_on_commit=False)


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    # {"mu": {...}, "sd": {...}, "mu0": {...}, "n": int, "updates": int}
    template: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Participant(Base):
    """Người tình nguyện thu dữ liệu. Tách khỏi `sessions` để export huấn luyện (gắn bằng participant_id) không mang email hay họ tên."""
    __tablename__ = "participants"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # = meta.participant_id
    email: Mapped[str] = mapped_column(String(254), index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TouchSession(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    device_id: Mapped[str] = mapped_column(String(64))
    raw: Mapped[dict] = mapped_column(JSON)
    features: Mapped[dict] = mapped_column(JSON)
    is_enrollment: Mapped[bool] = mapped_column(Boolean, default=False)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    risk: Mapped[float | None] = mapped_column(Float, nullable=True)
    action: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    label: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class ChallengeNonce(Base):
    """Token câu thử thách đã dùng (dùng một lần): dùng lại là dấu hiệu phát lại phiên ghi sẵn."""

    __tablename__ = "challenge_nonces"
    nonce: Mapped[str] = mapped_column(String(32), primary_key=True)
    used_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
