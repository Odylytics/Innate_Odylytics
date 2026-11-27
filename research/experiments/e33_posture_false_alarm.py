"""E33: báo động nhầm (chủ bị hỏi thêm / bị giữ lệnh) theo tư thế ngồi/đi, và đăng ký trộn tư thế có giảm được không.

Chạy đúng chuỗi `/score` của backend (giống E24): human.score + human_model, replay, owner.score + owner_model, fusion.fuse.
Dữ liệu StrokePIN: mỗi (người, PIN) có 5 lượt ngồi + 5 lượt đi, PIN 6 số chung. Tập kiểm thử CỐ ĐỊNH cho mọi cách đăng ký:
2 lượt ngồi cuối + 2 lượt đi cuối của chủ; kẻ biết PIN = 3 lượt ngồi + 3 lượt đi của người khác cùng PIN (máy của họ).
Đăng ký chỉ lấy từ 3 lượt ngồi đầu và 3 lượt đi đầu, nên không lượt kiểm thử nào nằm trong mẫu.

Hai bảng:
 - "full": đủ mô hình học, chỉ trên người chưa từng thấy bởi cả hai mô hình (như E24) -> ít người, CI rộng.
 - "rules": tắt mô hình học (luật người/máy + khoảng cách chủ), trên mọi người -> nhiều người hơn, không rò dữ liệu.
CI 95% bootstrap theo người. Người nhận quen, số tiền bình thường (và một cột người nhận mới).
Chạy: cd backend; uv run --with pandas python ../research/experiments/e33_posture_false_alarm.py
"""
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, fusion, human, human_model, owner, owner_model, replay  # noqa: E402
import strokepin_loader  # noqa: E402

rng = random.Random(0)
S = strokepin_loader.load()
USERS = sorted({e["user"] for e in S})
a = USERS[:]; random.Random(7).shuffle(a); not_h = set(a[62:])
b = USERS[:]; random.Random(21).shuffle(b); not_o = set(b[68:])
EVAL = sorted(not_h & not_o)
for e in S:
    e["f"] = features.extract(e["session"])
by = defaultdict(lambda: defaultdict(list))
for e in S:
    by[(e["user"], e["pin"])][e["posture"]].append(e)
by_pin = defaultdict(list)
for e in S:
    by_pin[e["pin"]].append(e)

CONFIGS = {  # tên -> (số lượt ngồi, số lượt đi) dùng để đăng ký
    "ngồi 3 (hiện tại ~ app)": (3, 0),
    "đi 3": (0, 3),
    "ngồi 2 + đi 1 (k=3)": (2, 1),
    "ngồi 2 + đi 2 (k=4)": (2, 2),
    "ngồi 3 + đi 1 (k=4)": (3, 1),
    "ngồi 3 + đi 3 (k=6)": (3, 3),
}


def decide(raw, f, tpl, hist, new_recipient, use_models):
    h, br = human.score(f)
    p = human_model.predict(raw) if use_models else None
    if p is not None:
        h = p if br == ["insufficient_data"] else min(h, p)
    if replay.is_replay(f, hist[-50:]):
        h = min(h, 0.1)
    o, z = owner.score(f, tpl) if tpl else (None, {})
    if o and use_models:
        m = owner_model.predict(z)
        o = o if m is None else m
    _, action, _ = fusion.fuse(h, o, new_recipient, 0.0)
    return action, h < fusion.HUMAN_HOLD


def run(users, use_models):
    # res[config][group] -> list of (user, action_known, action_new, bot_hold)
    res = defaultdict(lambda: defaultdict(list))
    for (u, pin), post in by.items():
        if u not in users or len(post["sit"]) < 5 or len(post["walk"]) < 5:
            continue
        sit, walk = post["sit"][:], post["walk"][:]
        rng.shuffle(sit); rng.shuffle(walk)
        tests = {"chủ ngồi": sit[3:5], "chủ đi": walk[3:5]}
        others = [e for e in by_pin[pin] if e["user"] != u]
        osit = [e for e in others if e["posture"] == "sit"]; owalk = [e for e in others if e["posture"] == "walk"]
        tests["kẻ biết PIN (ngồi)"] = rng.sample(osit, min(3, len(osit)))
        tests["kẻ biết PIN (đi)"] = rng.sample(owalk, min(3, len(owalk)))
        for name, (ns, nw) in CONFIGS.items():
            enr = sit[:ns] + walk[:nw]
            tpl = owner.build_template([e["f"] for e in enr])
            hist = [e["f"] for e in enr]
            for g, es in tests.items():
                for e in es:
                    raw = e["session"] if g.startswith("chủ") else {**e["session"], "user_id": u}
                    ak, bh = decide(raw, e["f"], tpl, hist, False, use_models)
                    an, _ = decide(raw, e["f"], tpl, hist, True, use_models)
                    res[name][g].append((u, ak, an, bh))
    return res


def boot(rows, stat, n=1000):
    us = sorted({r[0] for r in rows})
    byu = defaultdict(list)
    for r in rows:
        byu[r[0]].append(r)
    point = stat(rows)
    if len(us) < 2:
        return point, point, point
    rs = np.random.default_rng(1)
    vals = []
    for _ in range(n):
        pick = rs.choice(len(us), len(us))
        vals.append(stat([r for i in pick for r in byu[us[i]]]))
    return point, np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def fmt(t):
    p, lo, hi = t
    return f"{100 * p:.0f}% [{100 * lo:.0f}, {100 * hi:.0f}]"


not_allow = lambda rows: np.mean([r[1] != "allow" for r in rows])  # noqa: E731
hold = lambda rows: np.mean([r[1] == "hold" for r in rows])  # noqa: E731
bot_hold = lambda rows: np.mean([r[3] for r in rows])  # noqa: E731
allow = lambda rows: np.mean([r[1] == "allow" for r in rows])  # noqa: E731
not_allow_new = lambda rows: np.mean([r[2] != "allow" for r in rows])  # noqa: E731
allow_new = lambda rows: np.mean([r[2] == "allow" for r in rows])  # noqa: E731

L = ["# E33 — báo động nhầm theo tư thế (ngồi/đi) và đăng ký trộn tư thế (StrokePIN)", "",
     "Báo động nhầm = chủ thật KHÔNG được `allow` (bị `step_up` hoặc `hold`). Lọt = kẻ biết PIN được `allow`. "
     "Tập kiểm thử cố định cho mọi cách đăng ký (2 ngồi + 2 đi của chủ; 3 ngồi + 3 đi của kẻ biết PIN, máy khác). "
     f"Ngưỡng A={fusion.THRESHOLD_A}, B={fusion.THRESHOLD_B}. CI 95% bootstrap theo người.", ""]
for label, users, models in (("full: đủ mô hình học, người chưa từng thấy", set(EVAL), True), ("rules: tắt mô hình học, mọi người", set(USERS), False)):
    res = run(users, models)
    nu = len({r[0] for r in next(iter(res.values()))["chủ ngồi"]})
    L += [f"## {label} ({nu} người)", "",
          "### Người nhận quen", "",
          "| Đăng ký | Chủ ngồi: báo nhầm | Chủ ngồi: bị giữ | Chủ đi: báo nhầm | Chủ đi: bị giữ | trong đó giữ vì 'giống bot' (đi) | Kẻ biết PIN ngồi: lọt | Kẻ biết PIN đi: lọt |",
          "|---|---|---|---|---|---|---|---|"]
    for name in CONFIGS:
        g = res[name]
        L.append(f"| {name} | {fmt(boot(g['chủ ngồi'], not_allow))} | {fmt(boot(g['chủ ngồi'], hold))} | {fmt(boot(g['chủ đi'], not_allow))} | "
                 f"{fmt(boot(g['chủ đi'], hold))} | {fmt(boot(g['chủ đi'], bot_hold))} | {fmt(boot(g['kẻ biết PIN (ngồi)'], allow))} | {fmt(boot(g['kẻ biết PIN (đi)'], allow))} |")
    L += ["", "### Người nhận MỚI", "", "| Đăng ký | Chủ ngồi: báo nhầm | Chủ đi: báo nhầm | Kẻ biết PIN (ngồi+đi): lọt |", "|---|---|---|---|"]
    for name in CONFIGS:
        g = res[name]
        L.append(f"| {name} | {fmt(boot(g['chủ ngồi'], not_allow_new))} | {fmt(boot(g['chủ đi'], not_allow_new))} | "
                 f"{fmt(boot(g['kẻ biết PIN (ngồi)'] + g['kẻ biết PIN (đi)'], allow_new))} |")
    L.append("")
out = ROOT / "research/results/e33_posture_false_alarm.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
