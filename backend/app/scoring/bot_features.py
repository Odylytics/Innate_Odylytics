"""FIXED-length feature vector for the "human or machine" task (used by LightGBM).

Unlike features.py (per-key features, to compare against the owner's template): here we aggregate statistics
independent of PIN length, focused on how "natural" the interaction is. Missing data -> NaN (LightGBM handles it).
"""

import math
from statistics import fmean, pstdev

NAN = float("nan")
# Touch-size group: devices that cannot measure it always report 1, and a real bot source can set any value.
# Kept separate so training can run WITHOUT this group (stops the model from "cheating" through an easily faked field).
CONTACT_FEATURES = ("tap_w_mean", "tap_h_mean", "tap_w_std", "tap_h_std")


def _cv(xs: list[float]) -> float:
    m = fmean(xs) if xs else 0.0
    return pstdev(xs) / m if len(xs) > 1 and m > 0 else NAN


def _swipe(points: list[dict]) -> tuple[float, float, float, float, float]:
    """(straightness, mean velocity, peak/mean, normalized lateral deviation, time-step variation)"""
    seg = [(math.hypot(b["x"] - a["x"], b["y"] - a["y"]), b["t"] - a["t"]) for a, b in zip(points, points[1:])]
    path = sum(d for d, _ in seg)
    dur = points[-1]["t"] - points[0]["t"]
    x0, y0, x1, y1 = points[0]["x"], points[0]["y"], points[-1]["x"], points[-1]["y"]
    chord = math.hypot(x1 - x0, y1 - y0)
    v = [d / dt for d, dt in seg if dt > 0]
    v_mean = path / dur if dur > 0 else NAN
    # deviation of each point from the start-end straight line, normalized by path length
    dev = [abs((x1 - x0) * (y0 - p["y"]) - (x0 - p["x"]) * (y1 - y0)) / chord for p in points] if chord > 0 else [0.0]
    return (chord / path if path > 0 else NAN, v_mean, (max(v) / v_mean) if v and v_mean else NAN,
            pstdev(dev) / chord if chord > 0 and len(dev) > 1 else NAN, _cv([dt for _, dt in seg]))


def extract(raw: dict) -> dict[str, float]:
    f: dict[str, float] = {}
    taps = sorted(raw.get("pin_taps", []), key=lambda t: t["t_down"])
    holds = [t["t_up"] - t["t_down"] for t in taps]
    flights = [b["t_down"] - a["t_up"] for a, b in zip(taps, taps[1:])]
    off = [(((t["x"] - t["key_cx"]) / t["key_w"]), ((t["y"] - t["key_cy"]) / t["key_h"])) for t in taps]

    f["n_taps"] = float(len(taps))
    for name, xs in (("hold", holds), ("flight", flights)):
        f[f"{name}_mean"] = fmean(xs) if xs else NAN
        f[f"{name}_std"] = pstdev(xs) if len(xs) > 1 else NAN
        f[f"{name}_cv"] = _cv(xs)
        f[f"{name}_min"] = min(xs) if xs else NAN
        f[f"{name}_max"] = max(xs) if xs else NAN
    f["total_time"] = taps[-1]["t_up"] - taps[0]["t_down"] if taps else NAN
    # regularity of the rhythm: consecutive differences between intervals (an evenly spaced bot -> ~0)
    f["flight_succ_diff_rel"] = (fmean(abs(b - a) for a, b in zip(flights, flights[1:])) / fmean(flights)
                                 if len(flights) > 1 and fmean(flights) > 0 else NAN)

    dist = [math.hypot(dx, dy) for dx, dy in off]
    f["off_mean"] = fmean(dist) if dist else NAN
    f["off_min"] = min(dist) if dist else NAN
    f["dx_std"] = pstdev([d for d, _ in off]) if len(off) > 1 else NAN
    f["dy_std"] = pstdev([d for _, d in off]) if len(off) > 1 else NAN
    f["exact_center_frac"] = fmean(d < 0.02 for d in dist) if dist else NAN

    for name, key in (("tap_w_mean", "w"), ("tap_h_mean", "h")):
        f[name] = fmean(t[key] for t in taps) if taps else NAN
    f["tap_w_std"] = pstdev([t["w"] for t in taps]) if len(taps) > 1 else NAN
    f["tap_h_std"] = pstdev([t["h"] for t in taps]) if len(taps) > 1 else NAN

    sw = [_swipe(s["points"]) for s in raw.get("swipes", []) if len(s.get("points", [])) >= 2]
    f["swipe_count"] = float(len(sw))
    for j, name in enumerate(("straight", "v_mean", "v_peak_ratio", "lateral_dev", "dt_cv")):
        xs = [s[j] for s in sw if not math.isnan(s[j])]
        f[f"swipe_{name}"] = fmean(xs) if xs else NAN
    # input fields other than the PIN (amount, recipient, note): bots often set the text directly or type very evenly
    flds = raw.get("fields", [])
    ev = [(fl["name"], e) for fl in flds for e in fl.get("events", [])]
    chars = {k: sum(e["n"] for _, e in ev if e["kind"] == k) for k in ("key", "paste", "set_text", "delete")}
    total = chars["key"] + chars["paste"] + chars["set_text"]
    f["fld_count"] = float(len(flds))
    f["fld_set_text_frac"] = chars["set_text"] / total if total else NAN
    f["fld_paste_frac"] = chars["paste"] / total if total else NAN
    f["fld_delete_frac"] = chars["delete"] / (chars["key"] + chars["delete"]) if chars["key"] + chars["delete"] else NAN
    f["fld_amount_set_text"] = (float(any(n == "amount" and e["kind"] == "set_text" for n, e in ev))
                                if any(n == "amount" for n in (fl["name"] for fl in flds)) else NAN)
    gaps = []
    for fl in flds:
        ts = sorted(e["t"] for e in fl.get("events", []) if e["kind"] == "key")
        gaps.append([b - a for a, b in zip(ts, ts[1:])])
    gaps = [g for g in gaps if len(g) >= 3]
    f["fld_key_gap_mean"] = fmean(fmean(g) for g in gaps) if gaps else NAN
    f["fld_key_gap_cv"] = fmean(_cv(g) for g in gaps) if gaps else NAN
    waits = [v["t_first_touch"] - v["t_enter"] for v in raw.get("screens", []) if v.get("t_first_touch") is not None]
    f["first_touch_wait"] = fmean(waits) if waits else NAN
    return f


FEATURE_NAMES = list(extract({}).keys())
