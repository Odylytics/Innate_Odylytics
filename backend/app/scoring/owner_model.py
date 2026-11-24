"""Mô hình học (LightGBM) cho bài "có phải chủ": học trọng số/tương tác của độ lệch |z| thay vì coi mọi đặc trưng ngang nhau.
TUỲ CHỌN: thiếu lightgbm, thiếu file, thiếu đặc trưng (vd. PIN không đủ 6 phím) hoặc NHIP_OWNER_MODEL=off thì `predict` trả None
và backend dùng điểm khoảng cách của owner.py.

Huấn luyện KHÔNG dùng kích thước chạm (mang thông tin thiết bị; kẻ gian cầm đúng máy nạn nhân thì mất): xem research/experiments/e12*.py.
Điểm trả về [0,1] được ánh xạ để ngưỡng FRR 5% (trên người kiểm thử) = 0.5.
"""

import json
import os
from pathlib import Path

MODEL_DIR = Path(os.environ.get("NHIP_MODEL_DIR", Path(__file__).parent.parent / "models"))
_state: dict = {}


def _load():
    if "m" not in _state:
        try:
            if os.environ.get("NHIP_OWNER_MODEL", "on") == "off":
                raise RuntimeError("tắt bằng biến môi trường")
            import lightgbm as lgb  # noqa: PLC0415

            meta = json.loads((MODEL_DIR / "owner_lgbm.json").read_text(encoding="utf-8"))
            _state["m"] = (lgb.Booster(model_file=str(MODEL_DIR / "owner_lgbm.txt")), meta)
        except Exception:
            _state["m"] = None
    return _state["m"]


def loaded() -> bool:
    return _load() is not None


def predict(z: dict[str, float]) -> float | None:
    """z = độ lệch chuẩn hoá từng đặc trưng (owner.score trả về). -> điểm khớp chủ [0,1] hoặc None nếu không áp dụng được."""
    m = _load()
    if m is None:
        return None
    booster, meta = m
    if any(k not in z for k in meta["features"]):
        return None
    p = float(booster.predict([[abs(z[k]) for k in meta["features"]]])[0])  # P(kẻ gian)
    thr = meta["threshold"]
    return 1 - 0.5 * p / thr if p <= thr else 0.5 * (1 - p) / (1 - thr)
