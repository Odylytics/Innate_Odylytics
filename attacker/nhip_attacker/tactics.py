"""4 chiến thuật sinh phiên bot (dễ -> khó), theo mục 5.1 kế hoạch.

1. Bấm cách đều, đúng tâm nút
2. Thêm nhiễu ngẫu nhiên vào thời gian (vẫn đúng tâm)
3. Phát lại phiên người thật có thêm nhiễu
4. Lấy mẫu thời gian và vị trí từ phân bố của người thật

Phiên trả về đúng định dạng SessionIn của backend (không kèm meta).
"""

import copy
import random

# phím -> (tâm x, tâm y, rộng, cao), px. Khớp tests/synth.py của backend; app thật thì lấy từ phiên người (layout_from_sessions).
DEFAULT_LAYOUT: dict[str, tuple[float, float, float, float]] = {
    str(d): (60 + 120 * ((d - 1) % 3), 400 + 80 * ((d - 1) // 3), 100, 70) for d in range(1, 10)
} | {"0": (180, 640, 100, 70)}


def layout_from_sessions(sessions: list[dict]) -> dict[str, tuple[float, float, float, float]]:
    layout = {}
    for s in sessions:
        for t in s.get("pin_taps", []):
            layout.setdefault(t["key"], (t["key_cx"], t["key_cy"], t["key_w"], t["key_h"]))
    return layout


def _taps(pin: str, layout, holds, flights, offsets, sizes) -> list[dict]:
    taps, t = [], 0.0
    for i, key in enumerate(pin):
        cx, cy, kw, kh = layout[key]
        dx, dy = offsets[i]
        w, h = sizes[i]
        taps.append({"key": key, "t_down": round(t, 2), "t_up": round(t + holds[i], 2),
                     "x": round(cx + dx * kw, 2), "y": round(cy + dy * kh, 2), "w": w, "h": h,
                     "key_cx": cx, "key_cy": cy, "key_w": kw, "key_h": kh})
        if i < len(pin) - 1:
            t += holds[i] + flights[i]
    return taps


def _straight_swipe(rng: random.Random, jitter_t: bool) -> dict:
    """Vuốt thẳng tuyệt đối, vận tốc đều — kiểu `input swipe` / dispatchGesture một đường."""
    step = 20.0
    pts, t = [], 0.0
    for i in range(6):
        pts.append({"t": round(t, 2), "x": 200.0, "y": 600.0 - 50 * i})
        t += step + (rng.uniform(-6, 6) if jitter_t else 0)
    return {"points": pts}


def _session(user_id: str, taps: list[dict], swipes: list[dict], first_touch: float) -> dict:
    return {"user_id": user_id, "device_id": "demo_phone", "pin_taps": taps, "swipes": swipes,
            "screens": [{"name": "transfer", "t_enter": 0, "t_first_touch": round(first_touch, 2)}]}


def tactic1(user_id: str, pin: str, layout=DEFAULT_LAYOUT, rng: random.Random | None = None) -> dict:
    n = len(pin)
    taps = _taps(pin, layout, [60.0] * n, [140.0] * (n - 1), [(0.0, 0.0)] * n, [(1.0, 1.0)] * n)
    return _session(user_id, taps, [_straight_swipe(rng or random.Random(), False)], 300.0)


def tactic2(user_id: str, pin: str, layout=DEFAULT_LAYOUT, rng: random.Random | None = None) -> dict:
    rng = rng or random.Random()
    n = len(pin)
    holds = [rng.uniform(40, 140) for _ in range(n)]
    flights = [rng.uniform(80, 350) for _ in range(n - 1)]
    taps = _taps(pin, layout, holds, flights, [(0.0, 0.0)] * n, [(1.0, 1.0)] * n)
    return _session(user_id, taps, [_straight_swipe(rng, True)], rng.uniform(300, 2500))


def tactic3(user_id: str, source: dict, rng: random.Random | None = None) -> dict:
    """Phát lại một phiên người thật (vd. mã độc đã ghi lại phiên của nạn nhân), thêm nhiễu nhỏ."""
    rng = rng or random.Random()
    s = copy.deepcopy(source)
    s.pop("meta", None)
    s["user_id"] = user_id
    taps = sorted(s["pin_taps"], key=lambda t: t["t_down"])
    t = 0.0
    for i, tap in enumerate(taps):
        hold = (tap["t_up"] - tap["t_down"]) * rng.uniform(0.95, 1.05)
        gap = (taps[i + 1]["t_down"] - tap["t_up"]) * rng.uniform(0.95, 1.05) if i < len(taps) - 1 else 0
        tap["x"] += rng.uniform(-2, 2)
        tap["y"] += rng.uniform(-2, 2)
        tap["t_down"], tap["t_up"] = round(t, 2), round(t + hold, 2)
        t += hold + max(gap, 0)
    s["pin_taps"] = taps
    for sw in s.get("swipes", []):
        for p in sw["points"]:
            p["x"] += rng.uniform(-2, 2)
            p["y"] += rng.uniform(-2, 2)
    return s


def tactic4(user_id: str, pin: str, population: list[dict], layout=None, rng: random.Random | None = None) -> dict:
    """Mỗi giá trị (giữ phím, khoảng cách, lệch tâm, kích thước chạm) lấy mẫu độc lập từ toàn bộ người thật."""
    rng = rng or random.Random()
    layout = layout or layout_from_sessions(population) or DEFAULT_LAYOUT
    holds, flights, offsets, sizes, swipes, waits = [], [], [], [], [], []
    for s in population:
        taps = sorted(s.get("pin_taps", []), key=lambda t: t["t_down"])
        for i, t in enumerate(taps):
            holds.append(t["t_up"] - t["t_down"])
            offsets.append(((t["x"] - t["key_cx"]) / t["key_w"], (t["y"] - t["key_cy"]) / t["key_h"]))
            sizes.append((t["w"], t["h"]))
            if i < len(taps) - 1:
                flights.append(taps[i + 1]["t_down"] - t["t_up"])
        swipes += s.get("swipes", [])
        waits += [v["t_first_touch"] - v["t_enter"] for v in s.get("screens", []) if v.get("t_first_touch") is not None]
    if not holds or not flights:
        raise ValueError("Chiến thuật 4 cần phiên người thật có nhập PIN")

    n = len(pin)
    jit = lambda v, r: v * rng.uniform(1 - r, 1 + r)  # noqa: E731
    taps = _taps(pin, layout,
                 [jit(rng.choice(holds), 0.05) for _ in range(n)],
                 [max(jit(rng.choice(flights), 0.05), 0) for _ in range(n - 1)],
                 [rng.choice(offsets) for _ in range(n)],
                 [rng.choice(sizes) for _ in range(n)])
    sw = copy.deepcopy(rng.choice(swipes)) if swipes else _straight_swipe(rng, True)
    for p in sw["points"]:
        p["x"] += rng.uniform(-3, 3)
    return _session(user_id, taps, [sw], rng.choice(waits) if waits else rng.uniform(500, 2500))


def _persona(rng: random.Random) -> dict:
    return {"hold": rng.uniform(70, 140), "flight": rng.uniform(150, 350), "dx": rng.uniform(-0.2, 0.2),
            "dy": rng.uniform(-0.2, 0.2), "curve": rng.uniform(10, 40), "v": rng.uniform(1.2, 3.0)}


def _persona_session(user_id: str, p: dict, pin: str, layout, rng: random.Random) -> dict:
    k = len(pin)
    taps = _taps(pin, layout,
                 [max(30, rng.gauss(p["hold"], p["hold"] * 0.15)) for _ in range(k)],
                 [max(20, rng.gauss(p["flight"], p["flight"] * 0.25)) for _ in range(k - 1)],
                 [(rng.gauss(p["dx"], 0.06), rng.gauss(p["dy"], 0.06)) for _ in range(k)],
                 [(round(rng.gauss(40, 3), 1), round(rng.gauss(40, 3), 1)) for _ in range(k)])
    pts = [{"t": i * 20.0, "x": 200 + p["curve"] * (i / 5) ** 2 + rng.gauss(0, 1), "y": 600 - p["v"] * 20 * i}
           for i in range(6)]
    return _session(user_id, taps, [{"points": pts}], rng.uniform(600, 2500))


def synth_humans(n: int, pin: str = "1593", layout=DEFAULT_LAYOUT, seed: int = 0) -> list[dict]:
    """Phiên người GIẢ, mỗi phiên một "tính cách" ngẫu nhiên — chỉ dùng khi chưa thu được dữ liệu thật."""
    rng = random.Random(seed)
    return [_persona_session(f"synth_{i}", _persona(rng), pin, layout, rng) for i in range(n)]


def synth_owner(user_id: str, k: int, pin: str = "1593", layout=DEFAULT_LAYOUT, seed: int = 0) -> list[dict]:
    """k phiên GIẢ của cùng một người (để tạo tài khoản mục tiêu đã đăng ký)."""
    rng = random.Random(seed)
    p = _persona(rng)
    return [_persona_session(user_id, p, pin, layout, rng) for _ in range(k)]


def generate(tactic: int, user_id: str, pin: str, humans: list[dict], rng: random.Random) -> dict:
    layout = layout_from_sessions(humans) or DEFAULT_LAYOUT
    if tactic == 1:
        return tactic1(user_id, pin, layout, rng)
    if tactic == 2:
        return tactic2(user_id, pin, layout, rng)
    if tactic == 3:
        same_pin = [h for h in humans if "".join(t["key"] for t in h.get("pin_taps", [])) == pin]
        if not same_pin:
            raise ValueError("Chiến thuật 3 cần phiên người thật nhập đúng PIN này")
        return tactic3(user_id, rng.choice(same_pin), rng)
    if tactic == 4:
        return tactic4(user_id, pin, humans, layout, rng)
    raise ValueError(f"Không có chiến thuật {tactic}")
