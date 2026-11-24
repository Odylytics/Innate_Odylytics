"""Mô hình học (LightGBM) cho bài "người hay máy". TUỲ CHỌN: thiếu `lightgbm` hoặc thiếu file mô hình thì
`predict` trả None và backend dùng luật baseline (human.py).

Điểm trả về nằm trong [0,1] và đã ánh xạ để NGƯỠNG VẬN HÀNH (FRR 5% trên người ở tập validation) = 0.5,
khớp với chỗ explain.py coi < 0.5 là "có dấu hiệu máy".
"""

import json
import os
from pathlib import Path

from . import bot_features

MODEL_DIR = Path(os.environ.get("NHIP_MODEL_DIR", Path(__file__).parent.parent / "models"))
_state: dict = {}


def _load():
    if "m" not in _state:
        try:
            if os.environ.get("NHIP_HUMAN_MODEL", "on") == "off":
                raise RuntimeError("tắt bằng biến môi trường")
            import lightgbm as lgb  # noqa: PLC0415

            meta = json.loads((MODEL_DIR / "human_lgbm.json").read_text(encoding="utf-8"))
            _state["m"] = (lgb.Booster(model_file=str(MODEL_DIR / "human_lgbm.txt")), meta)
        except Exception:  # thiếu thư viện, thiếu file hoặc bị tắt: dùng luật
            _state["m"] = None
    return _state["m"]


def loaded() -> bool:
    return _load() is not None


def predict(raw: dict) -> float | None:
    """raw = phiên thô (SessionIn.model_dump()). -> điểm "là người" trong [0,1], hoặc None nếu không có mô hình."""
    m = _load()
    if m is None or not raw.get("pin_taps"):  # mô hình học trên phiên có PIN; thiếu PIN thì để owner.py báo missing_pin_evidence
        return None
    booster, meta = m
    f = bot_features.extract(raw)
    p = float(booster.predict([[f[k] for k in meta["features"]]])[0])  # P(người)
    thr = meta["threshold"]
    return 0.5 * p / thr if p < thr else 0.5 + 0.5 * (p - thr) / (1 - thr)
