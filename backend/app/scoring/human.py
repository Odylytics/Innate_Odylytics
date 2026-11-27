"""Model 1 baseline: "naturalness" rules. Member 1 replaces it with an RF/LightGBM trained on human + bot sessions."""

import math
from statistics import fmean, pstdev


def _clip(v: float) -> float:
    return min(max(v, 0.0), 1.0)


def _cv(xs: list[float]) -> float:
    m = fmean(xs)
    return pstdev(xs) / m if m > 0 else 0.0


def score(f: dict[str, float]) -> tuple[float, list[str]]:
    """-> (human_score 0..1, reason codes for suspected machine). 0.5 when there is not enough data."""
    cues: dict[str, float] = {}

    holds = [v for k, v in f.items() if k.startswith("pin_hold_")]
    flights = [v for k, v in f.items() if k.startswith("pin_flight_")]
    if len(holds) >= 3:
        cv = min(_cv(holds), _cv(flights) if len(flights) >= 2 else math.inf)
        cues["timing_too_regular"] = _clip((0.08 - cv) / 0.08)  # real person: CV usually > 0.15

    n = sum(1 for k in f if k.startswith("pin_dx_"))
    if n:
        dist = fmean(math.hypot(f[f"pin_dx_{i}"], f[f"pin_dy_{i}"]) for i in range(n))
        cues["tap_exact_center"] = _clip((0.06 - dist) / 0.06)  # a real person is off-center by ~0.1–0.25 of the key width

    if "swipe_robotic" in f:
        # E19 (Touchalytics, 20,896 real-person strokes): uniform velocity (CV < 0.3) was seen 0 times in real people. The old "straight > 0.999" rule wrongly flagged 13% of 3-stroke sessions.
        cues["swipe_uniform_speed"] = 0.7 * f["swipe_robotic"]

    if f.get("fld_challenge_token_bad", 0) >= 1:
        cues["challenge_token_replayed"] = 0.8  # forged, expired or already-used challenge token: replay of a recorded session

    if "vi_ime_coverage" in f:
        # accented challenge phrase with no transform key at all: set/pasted/adb/keyboard without Vietnamese. A SOFT signal (users of a word-suggestion keyboard look the same), not yet measured on real Vietnamese users
        cues["challenge_no_ime"] = 0.3 * (1 - f["vi_ime_coverage"])

    # shortcut: threshold not verified on real devices (R9). Autofill/contacts can also set text without keys,
    # so only the amount field (a real person does not autofill the amount) counts as strong evidence; other fields only cost a small penalty.
    # challenge phrase: text shown on screen, random each time; a real person retypes it key by key. Setting/pasting the whole phrase = machine (unverified, R9)
    if f.get("fld_challenge_set_text", 0) >= 1:
        cues["text_set_without_keys"] = 0.95
    if f.get("fld_challenge_paste", 0) >= 1:
        cues["challenge_pasted"] = 0.8
    fl = f.get("fld_amount_set_text")
    if fl is not None and fl >= 1:
        cues["text_set_without_keys"] = max(cues.get("text_set_without_keys", 0), 0.9)
    elif f.get("fld_set_text_frac", 0) > 0.5:
        cues["text_set_without_keys"] = max(cues.get("text_set_without_keys", 0), 0.4)  # must not lower the value of the challenge field

    if not cues:
        return 0.5, ["insufficient_data"]
    return 1 - max(cues.values()), [k for k, v in cues.items() if v >= 0.25]
