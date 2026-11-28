"""HistoryContext for training records. Uses backend/app/scoring/history.py directly (single source of the formulas), so
training and the live API cannot drift apart; tests/test_pipeline.py checks it against a stored export."""

import datetime as dt

from app.scoring import history
from app.scoring.history import KEYS, Prior  # noqa: F401  (re-exported)


def build(records: list["Record"]) -> None:  # noqa: F821
    """Fill `r.hist` for the records of ONE account, in time order (what the API would have stored at creation time)."""
    seen: list[Prior] = []
    for r in sorted(records, key=lambda r: r.t):
        now = dt.datetime.fromtimestamp(r.t, dt.timezone.utc)
        r.hist = history.compute(seen, r.device, now, r.attempt_meta)
        seen.append(Prior(now, r.device, r.is_enrollment, r.action))
