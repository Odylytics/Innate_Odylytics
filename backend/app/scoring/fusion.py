"""Model 3: fuse risk with a weighted sum. All inputs are already in [0,1]."""

import math
import os
from statistics import median

WEIGHTS = {"bot": 0.40, "owner": 0.35, "new_recipient": 0.15, "amount": 0.10}
THRESHOLD_A = float(os.environ.get("NHIP_THRESHOLD_A", 0.25))  # < A -> allow
THRESHOLD_B = float(os.environ.get("NHIP_THRESHOLD_B", 0.55))  # > B -> hold
HUMAN_HOLD = 0.3  # if it is clearly a machine, hold the order regardless of the other signals


def amount_anomaly(amount: float, history: list[float]) -> float:
    """0 when equal to the historical median, 1 when >= 10 times it. No history -> 0."""
    past = [a for a in history if a > 0]
    if amount <= 0 or not past:
        return 0.0
    return min(max(math.log10(amount / median(past)), 0.0), 1.0)


def fuse(human: float, owner: float | None, new_recipient: bool, amount_anom: float) -> tuple[float, str, dict]:
    parts = {
        "bot": WEIGHTS["bot"] * (1 - human),
        "owner": WEIGHTS["owner"] * (1 - (0.5 if owner is None else owner)),
        "new_recipient": WEIGHTS["new_recipient"] * float(new_recipient),
        "amount": WEIGHTS["amount"] * amount_anom,
    }
    risk = sum(parts.values())
    if human < HUMAN_HOLD or risk > THRESHOLD_B:
        action = "hold"
    elif risk >= THRESHOLD_A:
        action = "step_up"
    else:
        action = "allow"
    return risk, action, parts
