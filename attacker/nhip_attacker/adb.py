"""Real attack: use adb to tap the PIN into the demo wallet open on a phone (USB attached, USB debugging on).

`adb shell input tap` creates a touch at system level, like Accessibility malware tapping on the user's behalf: exact coordinates,
fixed touch size. Each adb command takes ~50–300 ms, so the time between two keys is not perfectly exact.
"""

import json
import random
import shutil
import subprocess
import time


def load_layout(path: str) -> dict[str, tuple[int, int]]:
    """layout.json: {"1": [x, y], "5": [x, y], ...} — DEVICE PIXEL coordinates (see the README for how to get them)."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {str(k): (int(v[0]), int(v[1])) for k, v in raw.items()}


def _adb(args: list[str], serial: str | None) -> None:
    cmd = ["adb"] + (["-s", serial] if serial else []) + args
    subprocess.run(cmd, check=True, capture_output=True, timeout=15)


def attack(pin: str, layout: dict[str, tuple[int, int]], tactic: int, serial: str | None = None,
           swipe: tuple[int, int, int, int] | None = None, dry_run: bool = False) -> list[list[str]]:
    """Tap the PIN (and swipe if given). tactic 1: even rhythm; tactic 2: random rhythm. Returns the commands that were run."""
    if tactic not in (1, 2):
        raise ValueError("adb only supports tactics 1 and 2 (exact key centers)")
    missing = [k for k in pin if k not in layout]
    if missing:
        raise ValueError(f"layout is missing keys: {missing}")
    if not dry_run and shutil.which("adb") is None:
        raise RuntimeError("adb not found. Install Android platform-tools and add it to PATH")

    rng = random.Random()
    done = []
    if swipe:
        cmd = ["shell", "input", "swipe", *map(str, swipe), "120"]
        done.append(cmd)
        if not dry_run:
            _adb(cmd, serial)
        time.sleep(0 if dry_run else 0.5)
    for i, key in enumerate(pin):
        x, y = layout[key]
        cmd = ["shell", "input", "tap", str(x), str(y)]
        done.append(cmd)
        if not dry_run:
            _adb(cmd, serial)
        if i < len(pin) - 1 and not dry_run:
            time.sleep(0.15 if tactic == 1 else rng.uniform(0.08, 0.35))
    return done
