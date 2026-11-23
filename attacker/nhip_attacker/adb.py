"""Tấn công thật: dùng adb bấm PIN vào ví demo đang mở trên điện thoại (cắm USB, bật USB debugging).

`adb shell input tap` tạo chạm ở tầng hệ thống, giống cách mã độc Trợ năng bấm hộ: toạ độ chính xác,
kích thước chạm cố định. Mỗi lệnh adb mất ~50–300 ms nên thời gian giữa hai phím không chính xác tuyệt đối.
"""

import json
import random
import shutil
import subprocess
import time


def load_layout(path: str) -> dict[str, tuple[int, int]]:
    """layout.json: {"1": [x, y], "5": [x, y], ...} — toạ độ PIXEL THIẾT BỊ (xem README để lấy)."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {str(k): (int(v[0]), int(v[1])) for k, v in raw.items()}


def _adb(args: list[str], serial: str | None) -> None:
    cmd = ["adb"] + (["-s", serial] if serial else []) + args
    subprocess.run(cmd, check=True, capture_output=True, timeout=15)


def attack(pin: str, layout: dict[str, tuple[int, int]], tactic: int, serial: str | None = None,
           swipe: tuple[int, int, int, int] | None = None, dry_run: bool = False) -> list[list[str]]:
    """Bấm PIN (và vuốt nếu có). tactic 1: nhịp đều; tactic 2: nhịp ngẫu nhiên. Trả về các lệnh đã chạy."""
    if tactic not in (1, 2):
        raise ValueError("adb chỉ hỗ trợ chiến thuật 1 và 2 (đúng tâm nút)")
    missing = [k for k in pin if k not in layout]
    if missing:
        raise ValueError(f"layout thiếu phím: {missing}")
    if not dry_run and shutil.which("adb") is None:
        raise RuntimeError("Không tìm thấy adb. Cài Android platform-tools và thêm vào PATH")

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
