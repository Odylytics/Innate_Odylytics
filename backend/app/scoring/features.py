import math
from statistics import fmean, pstdev


def _swipe_stats(points: list[dict]) -> tuple[float, float, float, float, float]:
    """(thời gian, độ dài đường đi, độ thẳng, vận tốc TB, vận tốc đỉnh)."""
    seg = [
        (math.hypot(b["x"] - a["x"], b["y"] - a["y"]), b["t"] - a["t"])
        for a, b in zip(points, points[1:])
    ]
    path = sum(d for d, _ in seg)
    dur = points[-1]["t"] - points[0]["t"]
    chord = math.hypot(points[-1]["x"] - points[0]["x"], points[-1]["y"] - points[0]["y"])
    straight = chord / path if path > 0 else 1.0
    v_mean = path / dur if dur > 0 else 0.0
    v_peak = max((d / dt for d, dt in seg if dt > 0), default=0.0)
    return dur, path, straight, v_mean, v_peak


def extract(raw: dict) -> dict[str, float]:
    """Phiên thô (SessionIn.model_dump()) -> đặc trưng. Thời gian ms, vị trí chạm chuẩn hoá theo kích thước phím."""
    f: dict[str, float] = {}

    taps = sorted(raw.get("pin_taps", []), key=lambda t: t["t_down"])
    for i, t in enumerate(taps):
        f[f"pin_hold_{i}"] = t["t_up"] - t["t_down"]
        f[f"pin_dx_{i}"] = (t["x"] - t["key_cx"]) / t["key_w"]
        f[f"pin_dy_{i}"] = (t["y"] - t["key_cy"]) / t["key_h"]
    for i in range(len(taps) - 1):
        f[f"pin_flight_{i}"] = taps[i + 1]["t_down"] - taps[i]["t_up"]
    if taps:
        f["pin_total"] = taps[-1]["t_up"] - taps[0]["t_down"]
        f["tap_w_mean"] = fmean(t["w"] for t in taps)
        f["tap_h_mean"] = fmean(t["h"] for t in taps)
        f["tap_w_std"] = pstdev([t["w"] for t in taps])

    stats = [_swipe_stats(s["points"]) for s in raw.get("swipes", [])]
    if stats:
        f["swipe_count"] = len(stats)
        for j, name in enumerate(["dur", "len", "straight", "v_mean", "v_peak"]):
            f[f"swipe_{name}_mean"] = fmean(s[j] for s in stats)
        f["swipe_straight_max"] = max(s[2] for s in stats)

    waits = [s["t_first_touch"] - s["t_enter"] for s in raw.get("screens", []) if s.get("t_first_touch") is not None]
    if waits:
        f["screen_first_touch_mean"] = fmean(waits)

    return f
