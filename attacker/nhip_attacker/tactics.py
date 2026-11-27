"""4 tactics for generating bot sessions (easy -> hard), per section 5.1 of the plan.

1. Evenly spaced taps, exactly on the key center
2. Add random noise to the timing (still on the key center)
3. Replay a real human session with added noise
4. Sample timing and position from the real human distribution

Returned sessions use the backend SessionIn format (without meta).
"""

import copy
import random

from . import fields

# key -> (center x, center y, width, height), px. Matches the backend tests/synth.py; the real app takes it from human sessions (layout_from_sessions).
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
    """Perfectly straight swipe at constant velocity, like `input swipe` / a single-path dispatchGesture."""
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
    """Replay a real human session (e.g. malware that recorded the victim's session), with small noise added."""
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
    """Each value (key hold, gap, center offset, touch size) is sampled independently from all real humans."""
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
        raise ValueError("Tactic 4 needs real human sessions with PIN entry")

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
    """SYNTHETIC human sessions, each with a random "personality" — use only when no real data has been collected yet."""
    rng = random.Random(seed)
    return [_persona_session(f"synth_{i}", _persona(rng), pin, layout, rng) for i in range(n)]


def synth_owner(user_id: str, k: int, pin: str = "1593", layout=DEFAULT_LAYOUT, seed: int = 0) -> list[dict]:
    """k SYNTHETIC sessions of the same person (to create an enrolled target account)."""
    rng = random.Random(seed)
    p = _persona(rng)
    return [_persona_session(user_id, p, pin, layout, rng) for _ in range(k)]


def generate(tactic: int, user_id: str, pin: str, humans: list[dict], rng: random.Random, with_fields: bool = False) -> dict:
    """with_fields=True adds input fields (amount, recipient, note) per tactic: see fields.py."""
    layout = layout_from_sessions(humans) or DEFAULT_LAYOUT
    source = None
    if tactic == 1:
        s = tactic1(user_id, pin, layout, rng)
    elif tactic == 2:
        s = tactic2(user_id, pin, layout, rng)
    elif tactic == 3:
        same_pin = [h for h in humans if "".join(t["key"] for t in h.get("pin_taps", [])) == pin]
        if not same_pin:
            raise ValueError("Tactic 3 needs a real human session that entered this exact PIN")
        source = rng.choice(same_pin)
        s = tactic3(user_id, source, rng)
    elif tactic == 4:
        s = tactic4(user_id, pin, humans, layout, rng)
    else:
        raise ValueError(f"No such tactic {tactic}")
    if with_fields:
        s["fields"] = fields.for_tactic(tactic, rng, humans, source)
    return s
