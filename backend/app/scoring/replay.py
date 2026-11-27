"""Replay detection (tactic 3): a session nearly identical to an old session of this SAME account.

A real person does not repeat the PIN rhythm to the millisecond; malware that recorded the victim's session does.
"""

import math
import os
from statistics import fmean

# Calibrated on REAL PEOPLE (research/experiments/e5b_replay_real.py, StrokePIN): 0.07 -> FPR ~0.1% with 8 old sessions, ~0.7% extrapolated at 50;
# catches 100% of replays with noise up to ±10%, 29% at ±15%. The old threshold 0.085 (chosen on fake data) caught 86% at ±15% but with extrapolated FPR ~3.7%:
# a session judged a replay is held outright, so wrongly flagging the real owner costs more than missing a high-noise attacker. Recalibrate on team data.
REPLAY_THRESHOLD = float(os.environ.get("NHIP_REPLAY_THRESHOLD", 0.07))
MIN_FEATURES = 5
OFFSET_SCALE = 0.4  # off-center difference between two real-person sessions (~0.07 of the key width) converted to the scale of relative timing difference (~0.15–0.2)


def distance(a: dict[str, float], b: dict[str, float]) -> float | None:
    """Mean difference (0 = identical): hold/flight time (relative) + off-center dx/dy. None if features are missing."""
    parts = [abs(a[k] - b[k]) / max((abs(a[k]) + abs(b[k])) / 2, 1e-6)
             for k in a if k.startswith(("pin_hold_", "pin_flight_")) and k in b]
    if len(parts) < MIN_FEATURES:
        return None
    parts += [abs(a[k] - b[k]) / OFFSET_SCALE for k in a if k.startswith(("pin_dx_", "pin_dy_")) and k in b]
    return fmean(parts)


def nearest(features: dict[str, float], history: list[dict[str, float]]) -> float:
    """Distance to the nearest old session; inf if there is nothing to compare."""
    ds = [d for h in history if (d := distance(features, h)) is not None]
    return min(ds, default=math.inf)


def is_replay(features: dict[str, float], history: list[dict[str, float]]) -> bool:
    return nearest(features, history) < REPLAY_THRESHOLD
