"""Generate fake sessions for testing: humans (by tapping "personality") and tactic-1 bot."""

import random
from dataclasses import dataclass

KEY_W, KEY_H = 100, 70
CENTERS = {"1": (60, 400), "5": (180, 480), "9": (300, 560), "3": (300, 400)}
PIN = "1593"


@dataclass
class Persona:
    hold: float  # ms
    flight: float  # ms
    dx: float  # off-center offset, in key widths
    dy: float
    swipe_v: float  # px/ms
    curve: float  # swipe curvature (px)


OWNER = Persona(hold=95, flight=180, dx=0.15, dy=-0.10, swipe_v=2.5, curve=25)
IMPOSTOR = Persona(hold=130, flight=320, dx=-0.12, dy=0.14, swipe_v=1.4, curve=8)


def _tap(key, t_down, hold, x, y, w=40, h=40):
    cx, cy = CENTERS[key]
    return {"key": key, "t_down": t_down, "t_up": t_down + hold, "x": x, "y": y, "w": w, "h": h,
            "key_cx": cx, "key_cy": cy, "key_w": KEY_W, "key_h": KEY_H}


def human_session(user_id: str, p: Persona, rng: random.Random) -> dict:
    taps, t = [], 0.0
    for key in PIN:
        cx, cy = CENTERS[key]
        hold = max(30.0, rng.gauss(p.hold, p.hold * 0.15))
        x = cx + rng.gauss(p.dx, 0.06) * KEY_W
        y = cy + rng.gauss(p.dy, 0.06) * KEY_H
        taps.append(_tap(key, t, hold, x, y, rng.gauss(40, 3), rng.gauss(40, 3)))
        t += hold + max(20.0, rng.gauss(p.flight, p.flight * 0.25))
    swipes = []
    for _ in range(2):
        v = max(0.3, rng.gauss(p.swipe_v, p.swipe_v * 0.1))
        pts = [{"t": i * 20.0, "x": 200 + p.curve * (i / 5) ** 2 + rng.gauss(0, 1),
                "y": 600 - v * 100 * (i / 5) ** 2 * (3 - 2 * i / 5)} for i in range(6)]  # speeds up then slows down like a finger (E19: real people do not swipe uniformly)
        swipes.append({"points": pts})
    return {"user_id": user_id, "device_id": "demo_phone", "pin_taps": taps, "swipes": swipes,
            "screens": [{"name": "transfer", "t_enter": 0, "t_first_touch": rng.gauss(1200, 200) % 3000}]}


def bot_session(user_id: str) -> dict:
    """Tactic 1: evenly spaced taps, exactly on the button center, straight swipe."""
    taps, t = [], 0.0
    for key in PIN:
        cx, cy = CENTERS[key]
        taps.append(_tap(key, t, 50, cx, cy))
        t += 150
    pts = [{"t": i * 20.0, "x": 200, "y": 600 - 50 * i} for i in range(6)]
    return {"user_id": user_id, "device_id": "demo_phone", "pin_taps": taps, "swipes": [{"points": pts}]}
