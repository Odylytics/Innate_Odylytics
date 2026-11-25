"""Mô hình 1 bản baseline: luật "độ tự nhiên". Người 1 thay bằng RF/LightGBM train trên phiên người + bot."""

import math
from statistics import fmean, pstdev


def _clip(v: float) -> float:
    return min(max(v, 0.0), 1.0)


def _cv(xs: list[float]) -> float:
    m = fmean(xs)
    return pstdev(xs) / m if m > 0 else 0.0


def score(f: dict[str, float]) -> tuple[float, list[str]]:
    """-> (human_score 0..1, mã lý do nghi máy). 0.5 khi không đủ dữ liệu."""
    cues: dict[str, float] = {}

    holds = [v for k, v in f.items() if k.startswith("pin_hold_")]
    flights = [v for k, v in f.items() if k.startswith("pin_flight_")]
    if len(holds) >= 3:
        cv = min(_cv(holds), _cv(flights) if len(flights) >= 2 else math.inf)
        cues["timing_too_regular"] = _clip((0.08 - cv) / 0.08)  # người thật: CV thường > 0.15

    n = sum(1 for k in f if k.startswith("pin_dx_"))
    if n:
        dist = fmean(math.hypot(f[f"pin_dx_{i}"], f[f"pin_dy_{i}"]) for i in range(n))
        cues["tap_exact_center"] = _clip((0.06 - dist) / 0.06)  # người thật lệch tâm ~0.1–0.25 bề rộng phím

    if "swipe_robotic" in f:
        # E19 (Touchalytics, 20.896 nét người thật): vận tốc đều (CV < 0.3) gặp 0 lần ở người thật. Luật "thẳng > 0.999" cũ gắn cờ nhầm 13% phiên 3 nét.
        cues["swipe_uniform_speed"] = 0.7 * f["swipe_robotic"]

    if "vi_ime_coverage" in f:
        # câu thử thách có dấu mà không có phím biến đổi nào: đặt/dán/adb/bàn phím không có tiếng Việt. Tín hiệu MỀM (người dùng bàn phím gợi ý từ cũng vậy), chưa đo trên người Việt thật
        cues["challenge_no_ime"] = 0.3 * (1 - f["vi_ime_coverage"])

    # shortcut: ngưỡng chưa kiểm chứng trên máy thật (R9). Autofill/danh bạ cũng có thể đặt văn bản không qua phím,
    # nên chỉ ô số tiền (người thật không autofill số tiền) bị coi là bằng chứng mạnh; ô khác chỉ trừ điểm nhẹ.
    # câu thử thách: văn bản hiện trên màn hình, ngẫu nhiên mỗi lần; người thật gõ lại từng phím. Đặt thẳng/dán nguyên câu = máy (chưa kiểm chứng, R9)
    if f.get("fld_challenge_set_text", 0) >= 1:
        cues["text_set_without_keys"] = 0.95
    if f.get("fld_challenge_paste", 0) >= 1:
        cues["challenge_pasted"] = 0.8
    fl = f.get("fld_amount_set_text")
    if fl is not None and fl >= 1:
        cues["text_set_without_keys"] = max(cues.get("text_set_without_keys", 0), 0.9)
    elif f.get("fld_set_text_frac", 0) > 0.5:
        cues["text_set_without_keys"] = max(cues.get("text_set_without_keys", 0), 0.4)  # không được hạ giá trị của ô thử thách

    if not cues:
        return 0.5, ["insufficient_data"]
    return 1 - max(cues.values()), [k for k, v in cues.items() if v >= 0.25]
