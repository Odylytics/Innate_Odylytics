"""Load sessions into `Record`s: /v1/export (JSON list or JSONL), StrokePIN (public humans) and attacker/ bot sessions."""

import datetime as dt
import json
import random
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Record:
    person: str  # identity label: participant_id for people, "bot" for generated sessions
    account: str  # the account (user_id) the session was made on
    t: float  # epoch seconds
    raw: dict
    role: str = "genuine"  # genuine | impostor | bot
    tactic: int | None = None
    device: str = "unknown"
    is_enrollment: bool = False
    action: str | None = None
    attempt_meta: dict | None = None
    hist: dict | None = None  # HistoryContext
    pin: str = field(default="")

    def __post_init__(self):
        self.pin = self.pin or "".join(t["key"] for t in sorted(self.raw.get("pin_taps", []), key=lambda t: t["t_down"]))


def _ts(s: str) -> float:
    d = dt.datetime.fromisoformat(s)
    return (d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)).timestamp()


def from_export(path: str | Path) -> list[Record]:
    """/v1/export output saved as a JSON list or one JSON object per line. Rows without `meta` (live transfers) are skipped:
    only collected sessions carry a person label."""
    text = Path(path).read_text(encoding="utf-8").strip()
    rows = json.loads(text) if text.startswith("[") else [json.loads(x) for x in text.splitlines() if x.strip()]
    out = []
    for r in rows:
        m = r.get("meta")
        if not m or not r["raw"].get("pin_taps"):
            continue
        raw = {k: v for k, v in r["raw"].items() if k != "_history"}
        out.append(Record(person=m["participant_id"] if m["role"] != "bot" else "bot", account=r["user_id"], t=_ts(r["created_at"]),
                          raw=raw, role=m["role"], tactic=m.get("tactic"), device=r.get("device_id", "unknown"),
                          is_enrollment=r.get("is_enrollment", False), action=(r.get("result") or {}).get("action"),
                          attempt_meta=raw.get("attempt_meta"), hist=r.get("history") or r["raw"].get("_history")))
    # the product does not store HistoryContext: rebuild it offline from created_at/device/is_enrollment/action (only over the
    # exported, i.e. collected, sessions of each account; live transfers are not in the export, so counts are lower bounds)
    from .history_features import build

    by_acct: dict[str, list[Record]] = {}
    for r in out:
        by_acct.setdefault(r.account, []).append(r)
    for recs in by_acct.values():
        if any(r.hist is None for r in recs):
            build(recs)
    return out


def from_strokepin(max_users: int | None = None, gap_sec: float = 3600.0) -> list[Record]:
    """StrokePIN humans (research/experiments/strokepin_loader.py). The dataset has no calendar time between entries:
    entry i of a person gets t = i * gap_sec (an ASSUMPTION; real time-decay needs real timestamps)."""
    import sys
    sys.path.insert(0, str(Path(__file__).parents[2] / "research" / "experiments"))
    import strokepin_loader  # needs pandas

    n: dict[str, int] = {}
    out = []
    for s in strokepin_loader.load(max_users):
        i = n[s["user"]] = n.get(s["user"], -1) + 1
        out.append(Record(person=s["user"], account=s["user"], t=i * gap_sec, raw=s["session"], device=s["user"]))
    return out


def from_attacker(sessions: list[dict], tactics: list[int | None] | None = None, t0: float = 0.0) -> list[Record]:
    """Bot sessions (attacker/ `generate` output or `adb` captures) as role=bot records."""
    rng = random.Random(0)
    return [Record(person="bot", account=s.get("user_id", "bot"), t=t0 + rng.random() * 86400, raw=s, role="bot",
                   tactic=(tactics[i] if tactics else None), device="bot") for i, s in enumerate(sessions)]
