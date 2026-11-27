"""Learned model (LightGBM) for the "human or machine" task. OPTIONAL: if `lightgbm` or the model file is missing,
`predict` returns None and the backend uses the baseline rules (human.py).

The returned score is in [0,1] and mapped so the OPERATING THRESHOLD (FRR 5% on humans in the validation set) = 0.5,
matching where explain.py treats < 0.5 as "signs of a machine".
"""

import json
import os
from pathlib import Path

from .lgbm_text import TextBooster

from . import bot_features

MODEL_DIR = Path(os.environ.get("NHIP_MODEL_DIR", Path(__file__).parent.parent / "models"))
_state: dict = {}


def _load():
    if "m" not in _state:
        try:
            if os.environ.get("NHIP_HUMAN_MODEL", "on") == "off":
                raise RuntimeError("disabled by environment variable")
            meta = json.loads((MODEL_DIR / "human_lgbm.json").read_text(encoding="utf-8"))
            _state["m"] = (TextBooster.from_file(MODEL_DIR / "human_lgbm.txt"), meta)
        except Exception:  # library missing, file missing or disabled: use the rules
            _state["m"] = None
    return _state["m"]


def loaded() -> bool:
    return _load() is not None


def predict(raw: dict) -> float | None:
    """raw = raw session (SessionIn.model_dump()). -> "is human" score in [0,1], or None if there is no model."""
    m = _load()
    if m is None or not raw.get("pin_taps"):  # the model was trained on sessions with a PIN; without a PIN let owner.py report missing_pin_evidence
        return None
    booster, meta = m
    f = bot_features.extract(raw)
    p = float(booster.predict([[f[k] for k in meta["features"]]])[0])  # P(human)
    thr = meta["threshold"]
    return 0.5 * p / thr if p < thr else 0.5 + 0.5 * (p - thr) / (1 - thr)
