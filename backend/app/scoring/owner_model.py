"""Learned model (LightGBM) for the "is it the owner" task: learns weights/interactions of the deviation |z| instead of treating all features equally.
OPTIONAL: if lightgbm is missing, the file is missing, a feature is missing (e.g. PIN shorter than 6 keys) or NHIP_OWNER_MODEL=off, `predict` returns None
and the backend uses the distance score of owner.py.

Training does NOT use touch size (it carries device information; it is lost when an impostor holds the victim's own device): see research/experiments/e12*.py.
The returned score in [0,1] is mapped so the FRR 5% threshold (on test people) = 0.5.
"""

import json
import os
from pathlib import Path

from .lgbm_text import TextBooster

MODEL_DIR = Path(os.environ.get("NHIP_MODEL_DIR", Path(__file__).parent.parent / "models"))
_state: dict = {}


def _load():
    if "m" not in _state:
        try:
            if os.environ.get("NHIP_OWNER_MODEL", "on") == "off":
                raise RuntimeError("disabled by environment variable")
            meta = json.loads((MODEL_DIR / "owner_lgbm.json").read_text(encoding="utf-8"))
            _state["m"] = (TextBooster.from_file(MODEL_DIR / "owner_lgbm.txt"), meta)
        except Exception:
            _state["m"] = None
    return _state["m"]


def loaded() -> bool:
    return _load() is not None


def predict(z: dict[str, float]) -> float | None:
    """z = per-feature normalized deviation (returned by owner.score). -> owner match score in [0,1], or None if not applicable."""
    m = _load()
    if m is None:
        return None
    booster, meta = m
    if any(k not in z for k in meta["features"]):
        return None
    p = float(booster.predict([[abs(z[k]) for k in meta["features"]]])[0])  # P(impostor)
    thr = meta["threshold"]
    return 1 - 0.5 * p / thr if p <= thr else 0.5 * (1 - p) / (1 - thr)
