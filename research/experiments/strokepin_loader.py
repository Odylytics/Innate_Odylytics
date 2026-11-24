"""Nạp StrokePIN (Yao & Wang, 2026; CC BY-NC-SA 4.0) thành phiên đúng định dạng SessionIn của backend.

Dữ liệu: 97 người, mỗi người 200 lần nhập, 20 PIN 6 số CHUNG cho mọi người, 2 tư thế (ngồi/đi). Bàn phím số
chuẩn, toạ độ px. Tâm phím KHÔNG có sẵn: ước lượng theo từng người và từng chữ số = trung vị toạ độ chạm
của người đó cho chữ số đó; kích thước phím = khoảng cách trung vị giữa các cột/hàng liền kề (cũng theo người).

Phiên trả về: {"user", "pin", "posture", "sample", "session": SessionIn-dict (không có swipe/screens)}
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).parents[1] / "data/StrokePIN"


def _entries(path: Path) -> list[dict]:
    d = pd.read_csv(path, dtype={"PIN": str})
    d["act"] = d.ACTION_TYPE.str.extract(r"^(Down|Up|Move)")[0]
    out = []
    for sid, e in d.groupby("Sample ID", sort=False):
        e = e.sort_values("Time")
        pin, taps, cur = e.PIN.iloc[0], [], None
        for r in e.itertuples():
            if r.act == "Down":
                cur = {"t_down": r.Time, "x": r.X, "y": r.Y, "w": r.SizeMajor, "h": r.SizeMinor}
            elif r.act == "Up" and cur is not None:
                cur["t_up"] = r.Time
                taps.append(cur)
                cur = None
        if len(taps) == len(pin) == 6:  # bỏ lượt thiếu sự kiện Up và PIN `10140` (5 số, 11 lượt; có thể mất số 0 đầu)
            out.append({"pin": pin, "posture": e.Posture.iloc[0], "sample": sid, "taps": taps})
    return out


def load(max_users: int | None = None) -> list[dict]:
    sessions = []
    for f in sorted(DATA.glob("user*_touch.csv"), key=lambda p: int(p.stem[4:].split("_")[0]))[:max_users]:
        user = f.stem.split("_")[0]
        ents = _entries(f)
        # tâm phím theo từng chữ số của người này
        pts: dict[str, list[tuple[float, float]]] = {}
        for e in ents:
            for ch, t in zip(e["pin"], e["taps"]):
                pts.setdefault(ch, []).append((t["x"], t["y"]))
        c = {ch: tuple(np.median(np.array(v), axis=0)) for ch, v in pts.items()}
        if not all(k in c for k in "1234567890"):
            continue
        key_w = float(np.median([abs(c["2"][0] - c["1"][0]), abs(c["3"][0] - c["2"][0]),
                                 abs(c["5"][0] - c["4"][0]), abs(c["6"][0] - c["5"][0])]))
        key_h = float(np.median([abs(c["4"][1] - c["1"][1]), abs(c["7"][1] - c["4"][1]),
                                 abs(c["5"][1] - c["2"][1]), abs(c["8"][1] - c["5"][1])]))
        for e in ents:
            t0 = e["taps"][0]["t_down"]
            taps = [{"key": ch, "t_down": (t["t_down"] - t0) / 1e6, "t_up": (t["t_up"] - t0) / 1e6, "x": t["x"], "y": t["y"],
                     "w": t["w"], "h": t["h"], "key_cx": c[ch][0], "key_cy": c[ch][1], "key_w": key_w, "key_h": key_h}
                    for ch, t in zip(e["pin"], e["taps"])]
            if any(t["t_up"] < t["t_down"] for t in taps):
                continue
            sessions.append({"user": user, "pin": e["pin"], "posture": e["posture"], "sample": e["sample"],
                             "session": {"user_id": user, "pin_taps": taps, "swipes": [], "screens": []}})
    return sessions


if __name__ == "__main__":
    s = load()
    users = {x["user"] for x in s}
    pins = {x["pin"] for x in s}
    print(f"{len(s)} lượt nhập hợp lệ, {len(users)} người, {len(pins)} PIN, tư thế: {pd.Series([x['posture'] for x in s]).value_counts().to_dict()}")
    t = s[0]["session"]["pin_taps"]
    print("ví dụ:", s[0]["user"], s[0]["pin"], [round(x["t_up"] - x["t_down"]) for x in t], "ms giữ;", "key_w/h:", round(t[0]["key_w"]), round(t[0]["key_h"]))
