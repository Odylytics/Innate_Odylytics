"""HistoryContext: per-session history parameters (counts, inter-attempt gaps, device continuity).

Computed from a user's earlier sessions (+ optional client `attempt_meta`); feeds layers 3/4 of the DL model.
Research code: the product does not store it (a parked design would put it in `raw["_history"]`, never in `features`).
Pure Python on purpose: no numpy on the request path.
"""

import datetime as dt
from statistics import fmean, pstdev
from typing import NamedTuple

SITTING_GAP_SEC = 30 * 60  # a pause longer than this starts a new sitting
RECENT = 6  # sessions (current included) used for the recent-gap statistics
FLAGGED = ("step_up", "hold")
KEYS = (
    "n_enroll", "n_sessions_total", "attempt_index_in_sitting", "n_attempts_10m", "n_attempts_1h", "n_attempts_24h",
    "n_recent_flagged", "client_retries", "dt_prev_session_sec", "dt_last_enroll_sec", "dt_mean_recent_sec",
    "dt_cv_recent", "enroll_span_sec", "client_dt_prev_ms", "same_device_as_enroll", "n_distinct_devices",
)


class Prior(NamedTuple):
    """One earlier session of the same user."""
    created_at: dt.datetime
    device_id: str
    is_enrollment: bool
    action: str | None


def _utc(t: dt.datetime) -> dt.datetime:
    return t.replace(tzinfo=dt.timezone.utc) if t.tzinfo is None else t  # SQLite returns naive datetimes


def _gap_stats(times: list[dt.datetime]) -> tuple[float | None, float | None]:
    gaps = [(b - a).total_seconds() for a, b in zip(times, times[1:])]
    if not gaps:
        return None, None
    m = fmean(gaps)
    return m, (pstdev(gaps) / m if m > 0 and len(gaps) >= 2 else None)


def compute(prior: list[Prior], device_id: str, now: dt.datetime, attempt_meta: dict | None = None) -> dict:
    """HistoryContext of a session created at `now`; `prior` = the user's earlier sessions (any order)."""
    now = _utc(now)
    rows = sorted(((_utc(p.created_at), p) for p in prior), key=lambda x: x[0])
    times = [t for t, _ in rows]
    enroll = [(t, p) for t, p in rows if p.is_enrollment]
    ago = lambda sec: sum((now - t).total_seconds() <= sec for t in times)  # noqa: E731

    chain = times + [now]
    sitting = 1  # 1-based index of this attempt in the current sitting
    for a, b in zip(reversed(chain[:-1]), reversed(chain[1:])):
        if (b - a).total_seconds() > SITTING_GAP_SEC:
            break
        sitting += 1
    meta = attempt_meta or {}
    mean, cv = _gap_stats(chain[-RECENT:])
    return {
        "n_enroll": len(enroll),
        "n_sessions_total": len(rows),
        "attempt_index_in_sitting": sitting,
        "n_attempts_10m": ago(600), "n_attempts_1h": ago(3600), "n_attempts_24h": ago(86400),
        "n_recent_flagged": sum(p.action in FLAGGED for _, p in rows[-10:]),
        "client_retries": int(meta.get("retries") or 0),
        "dt_prev_session_sec": (now - times[-1]).total_seconds() if times else None,
        "dt_last_enroll_sec": (now - enroll[-1][0]).total_seconds() if enroll else None,
        "dt_mean_recent_sec": mean, "dt_cv_recent": cv,
        "enroll_span_sec": (enroll[-1][0] - enroll[0][0]).total_seconds() if enroll else 0.0,
        "client_dt_prev_ms": meta.get("client_dt_prev_ms"),
        "same_device_as_enroll": (enroll[0][1].device_id == device_id) if enroll else None,
        "n_distinct_devices": len({p.device_id for _, p in rows} | {device_id}),
    }


def summary(prior_enroll: list[Prior], client_dt_ms: list[float | None]) -> dict:
    """Short enrolment telemetry shown in the phone app (entries so far, mean gap, steadiness of the gaps)."""
    times = sorted(_utc(p.created_at) for p in prior_enroll)
    mean, cv = _gap_stats(times)
    cd = [x for x in client_dt_ms if x is not None]
    return {"n_entries": len(times), "dt_mean_sec": mean, "dt_cv": cv,
            "span_sec": (times[-1] - times[0]).total_seconds() if times else 0.0,
            "client_dt_mean_ms": fmean(cd) if cd else None}
