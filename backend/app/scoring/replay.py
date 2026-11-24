"""Phát hiện phát lại (chiến thuật 3): phiên gần như y hệt một phiên cũ của CHÍNH tài khoản này.

Người thật không lặp lại nhịp PIN sát từng mili-giây; mã độc đã ghi lại phiên của nạn nhân thì có.
"""

import math
import os
from statistics import fmean

# shortcut: ngưỡng chọn trên dữ liệu GIẢ (research/experiments/e5_replay.py, FPR ~1% với PIN 4 và 6 số); hiệu chỉnh lại trên dữ liệu người thật.
REPLAY_THRESHOLD = float(os.environ.get("NHIP_REPLAY_THRESHOLD", 0.085))
MIN_FEATURES = 5
OFFSET_SCALE = 0.4  # độ lệch tâm giữa hai phiên người thật (~0.07 bề rộng phím) đổi sang thang của sai khác tương đối thời gian (~0.15–0.2)


def distance(a: dict[str, float], b: dict[str, float]) -> float | None:
    """Sai khác trung bình (0 = trùng hệt): thời gian giữ/cách phím (tương đối) + lệch tâm dx/dy. None nếu thiếu đặc trưng."""
    parts = [abs(a[k] - b[k]) / max((abs(a[k]) + abs(b[k])) / 2, 1e-6)
             for k in a if k.startswith(("pin_hold_", "pin_flight_")) and k in b]
    if len(parts) < MIN_FEATURES:
        return None
    parts += [abs(a[k] - b[k]) / OFFSET_SCALE for k in a if k.startswith(("pin_dx_", "pin_dy_")) and k in b]
    return fmean(parts)


def nearest(features: dict[str, float], history: list[dict[str, float]]) -> float:
    """Khoảng cách tới phiên cũ gần nhất; inf nếu không có gì để so."""
    ds = [d for h in history if (d := distance(features, h)) is not None]
    return min(ds, default=math.inf)


def is_replay(features: dict[str, float], history: list[dict[str, float]]) -> bool:
    return nearest(features, history) < REPLAY_THRESHOLD
