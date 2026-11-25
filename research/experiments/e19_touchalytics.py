"""E19: kiểm đặc trưng VUỐT của backend trên người thật (Touchalytics, 41 người, điện thoại Android, data.zip).

(a) Luật bot "vuốt thẳng tuyệt đối" (human.py: swipe_straight_max > 0.999): tỉ lệ người thật bị gắn cờ nhầm, và bot `_straight_swipe` của attacker có bị bắt không.
(b) Xác minh chủ bằng vuốt (owner.py nguyên bản): đăng ký bằng phiên ngày 1 (doc 1-5), thử ở doc 6-7 (7-14 ngày sau); kẻ gian = người khác CÙNG điện thoại.
Phiên giả lập = 3 nét liên tiếp cùng tài liệu. Chỉ vuốt có dịch chuyển (định nghĩa của bộ dữ liệu). Không có bot thật: bot là bộ sinh của đội. Pixel khác nhau theo điện thoại nên so trong cùng điện thoại.
Dùng: python research/experiments/e19_touchalytics.py
"""
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path
from statistics import fmean

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker")]
from app.scoring import features, owner  # noqa: E402
from nhip_attacker import tactics  # noqa: E402

rng = random.Random(0)
strokes = defaultdict(list)  # (phone, user, doc) -> [points]
cur = {}
for r in csv.reader(open(ROOT / "research/data/touchalytics/data/data.csv")):
    ph, u, d, t, a, x, y = r[0], r[1], int(r[2]), int(r[3]), int(r[4]), float(r[6]), float(r[7])
    k = (ph, u)
    if a == 0:
        cur[k] = [{"t": t, "x": x, "y": y, "d": d}]
    elif k in cur:
        cur[k].append({"t": t, "x": x, "y": y, "d": d})
        if a == 1:
            p = cur.pop(k)
            if len(p) >= 3 and (p[0]["x"], p[0]["y"]) != (p[-1]["x"], p[-1]["y"]):
                t0 = p[0]["t"]
                strokes[(ph, u, d)].append([{"t": q["t"] - t0, "x": q["x"], "y": q["y"]} for q in p])
print(f"nét vuốt: {sum(map(len, strokes.values()))}, người: {len({k[:2] for k in strokes})}")

# (a) luật thẳng tuyệt đối
st = [features._swipe_stats(p) for v in strokes.values() for p in v]
straight = np.array([s[2] for s in st])
print(f"\n(a) độ thẳng nét người thật: trung vị {np.median(straight):.3f}, p99 {np.percentile(straight, 99):.4f}, tỉ lệ > 0.999: {np.mean(straight > 0.999):.4%}")
sess = [max(features._swipe_stats(p)[2] for p in v[i : i + 3]) for v in strokes.values() for i in range(0, len(v) - 2, 3)]
print(f"    phiên 3 nét có max-thẳng > 0.999 (luật gắn cờ): {np.mean(np.array(sess) > 0.999):.4%} của {len(sess)} phiên")
bot = [features._swipe_stats(tactics._straight_swipe(rng, j)["points"])[2] for j in (False, True) for _ in range(200)]
print(f"    bot vuốt thẳng của attacker: thẳng min {min(bot):.4f} -> bị luật bắt {np.mean(np.array(bot) > 0.999):.0%}")
# bot khôn hơn: thêm nhiễu ngang 2 px, vẫn thẳng ~0.999+? đo độ thẳng khi nhiễu ngang tăng
for noise in (0, 1, 2, 5, 10):
    s = []
    for _ in range(200):
        pts = tactics._straight_swipe(rng, True)["points"]
        for q in pts:
            q["x"] += rng.gauss(0, noise)
        s.append(features._swipe_stats(pts)[2])
    print(f"    bot + nhiễu ngang σ={noise:>2}px: bị luật bắt {np.mean(np.array(s) > 0.999):.0%}, thẳng trung vị {np.median(s):.4f}")

# (a2) lỗi của luật theo số điểm của nét: nét ít điểm thì "thẳng" gần như tự nhiên
lens = np.array([len(p) for v in strokes.values() for p in v])
for lo, hi in ((3, 5), (6, 9), (10, 19), (20, 10**6)):
    m = (lens >= lo) & (lens <= hi)
    print(f"    nét {lo}-{hi if hi < 10**6 else '+'} điểm: {m.sum():>6} nét, tỉ lệ thẳng > 0.999 = {np.mean(straight[m] > 0.999):.2%}")

# (b) xác minh chủ bằng vuốt
def chunks(p, v):
    return [{f"swipe_{n}_mean": fmean(features._swipe_stats(q)[j] for q in v[i : i + 3]) for j, n in enumerate(["dur", "len", "straight", "v_mean", "v_peak"])}
            for i in range(0, len(v) - 2, 3)]

by = defaultdict(lambda: defaultdict(list))  # phone -> user -> {"enr": [...], "test": [...]}
for (ph, u, d), v in strokes.items():
    by[ph][u] += [(d, c) for c in chunks(ph, v)]
def run(enr_docs, tst_docs, keys=None):
    sel = lambda c: {k: v for k, v in c.items() if keys is None or k in keys}
    res = []
    for ph, users in by.items():
        enr = {u: [sel(c) for d, c in cs if d in enr_docs] for u, cs in users.items()}
        tst = {u: [sel(c) for d, c in cs if d in tst_docs] for u, cs in users.items()}
        ok = [u for u in users if len(enr[u]) >= 6 and len(tst[u]) >= 3]
        if len(ok) < 3:
            continue
        for u in ok:
            tpl = owner.build_template(rng.sample(enr[u], min(10, len(enr[u]))))
            res.append(([owner.score(c, tpl)[0] for c in tst[u]], [owner.score(c, tpl)[0] for v in ok if v != u for c in tst[v][:5]]))
    return res


def report(name, res):
    if not res:
        print(f"    {name}: không đủ người")
        return
    gen = np.concatenate([g for g, _ in res]); imp = np.concatenate([i for _, i in res])
    far = np.mean(imp >= np.percentile(gen, 5))  # FRR 5%
    auc = np.mean([np.mean([(a > b) + 0.5 * (a == b) for a in g for b in i]) for g, i in res])
    print(f"    {name}: {len(res)} người, FAR@FRR5% = {far:.3f}, AUC = {auc:.3f}")


print("\n(b) xác minh chủ bằng vuốt (đặc trưng backend: dur, len, straight, v_mean, v_peak)")
report("đăng ký doc1-5, thử doc6-7 (7-14 ngày sau, khác loại tác vụ)", run(range(1, 6), (6, 7)))
report("cùng tác vụ đọc: đăng ký doc1-3, thử doc6", run((1, 2, 3), (6,)))
report("cùng tác vụ ảnh: đăng ký doc4-5, thử doc7", run((4, 5), (7,)))
report("cùng ngày, cùng tác vụ: đăng ký doc1-2, thử doc3", run((1, 2), (3,)))
report("chỉ v_peak + v_mean", run(range(1, 6), (6, 7), {"swipe_v_peak_mean", "swipe_v_mean_mean"}))


# (c) sửa luật: thẳng tuyệt đối VÀ vận tốc đều. Đo trên người thật và trên bot (có/không nhiễu thời gian)
def vcv(p):
    sp = [np.hypot(b["x"] - a["x"], b["y"] - a["y"]) / (b["t"] - a["t"]) for a, b in zip(p, p[1:]) if b["t"] > a["t"]]
    return float(np.std(sp) / np.mean(sp)) if len(sp) >= 2 and np.mean(sp) > 0 else 1.0


allp = [p for v in strokes.values() for p in v]
cv = np.array([vcv(p) for p in allp])
print("\n(c) luật mới: thẳng > 0.999 VÀ độ biến thiên vận tốc < ngưỡng (người thật có nét thẳng nhưng vận tốc không đều)")
bots = {j: [tactics._straight_swipe(rng, j)["points"] for _ in range(300)] for j in (False, True)}
for thr in (0.05, 0.1, 0.2, 0.3):
    hum = np.mean((straight > 0.999) & (cv < thr))
    b = {j: np.mean([features._swipe_stats(p)[2] > 0.999 and vcv(p) < thr for p in bots[j]]) for j in bots}
    print(f"    cv<{thr}: người thật bị gắn cờ {hum:.2%} nét | bot đều {b[False]:.0%}, bot nhiễu thời gian ±6ms {b[True]:.0%}")

m6 = lens >= 6
print("    chỉ riêng độ đều vận tốc (nét >= 6 điểm), tỉ lệ người thật: " + ", ".join(f"cv<{t}: {np.mean(cv[m6] < t):.2%}" for t in (0.1, 0.2, 0.3)))
print("    nét >= 3 điểm: " + ", ".join(f"cv<{t}: {np.mean(cv < t):.3%}" for t in (0.1, 0.2, 0.3)) + f" (n={len(cv)}); bot nhiễu thời gian lệch cv trung vị {np.median([vcv(p) for p in bots[True]]):.2f}")
