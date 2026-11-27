"""E19: checks the backend SWIPE features on real people (Touchalytics, 41 people, Android phones, data.zip).

(a) The "perfectly straight swipe" bot rule (human.py: swipe_straight_max > 0.999): the share of real people wrongly flagged, and whether the attacker's `_straight_swipe` bot is caught.
(b) Owner verification by swiping (original owner.py): enroll with day-1 sessions (doc 1-5), test on doc 6-7 (7-14 days later); impostor = another person on the SAME phone.
Simulated session = 3 consecutive strokes of the same document. Only swipes with displacement (the dataset's definition). No real bots: the bot is the team's generator. Pixels differ by phone, so comparisons are within the same phone.
Usage: python research/experiments/e19_touchalytics.py
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
print(f"swipe strokes: {sum(map(len, strokes.values()))}, people: {len({k[:2] for k in strokes})}")

# (a) absolute straightness rule
st = [features._swipe_stats(p) for v in strokes.values() for p in v]
straight = np.array([s[2] for s in st])
print(f"\n(a) straightness of real-person strokes: median {np.median(straight):.3f}, p99 {np.percentile(straight, 99):.4f}, share > 0.999: {np.mean(straight > 0.999):.4%}")
sess = [max(features._swipe_stats(p)[2] for p in v[i : i + 3]) for v in strokes.values() for i in range(0, len(v) - 2, 3)]
print(f"    3-stroke sessions with max-straightness > 0.999 (flagged by the rule): {np.mean(np.array(sess) > 0.999):.4%} of {len(sess)} sessions")
bot = [features._swipe_stats(tactics._straight_swipe(rng, j)["points"])[2] for j in (False, True) for _ in range(200)]
print(f"    attacker straight-swipe bot: min straightness {min(bot):.4f} -> caught by the rule {np.mean(np.array(bot) > 0.999):.0%}")
# smarter bot: add 2 px lateral noise, still ~0.999+ straight? measure straightness as lateral noise grows
for noise in (0, 1, 2, 5, 10):
    s = []
    for _ in range(200):
        pts = tactics._straight_swipe(rng, True)["points"]
        for q in pts:
            q["x"] += rng.gauss(0, noise)
        s.append(features._swipe_stats(pts)[2])
    print(f"    bot + lateral noise σ={noise:>2}px: caught by the rule {np.mean(np.array(s) > 0.999):.0%}, median straightness {np.median(s):.4f}")

# (a2) rule errors by number of points in the stroke: strokes with few points are "straight" almost naturally
lens = np.array([len(p) for v in strokes.values() for p in v])
for lo, hi in ((3, 5), (6, 9), (10, 19), (20, 10**6)):
    m = (lens >= lo) & (lens <= hi)
    print(f"    strokes {lo}-{hi if hi < 10**6 else '+'} points: {m.sum():>6} strokes, share straight > 0.999 = {np.mean(straight[m] > 0.999):.2%}")

# (b) owner verification by swiping
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
        print(f"    {name}: not enough people")
        return
    gen = np.concatenate([g for g, _ in res]); imp = np.concatenate([i for _, i in res])
    far = np.mean(imp >= np.percentile(gen, 5))  # FRR 5%
    auc = np.mean([np.mean([(a > b) + 0.5 * (a == b) for a in g for b in i]) for g, i in res])
    print(f"    {name}: {len(res)} people, FAR@FRR5% = {far:.3f}, AUC = {auc:.3f}")


print("\n(b) owner verification by swiping (backend features: dur, len, straight, v_mean, v_peak)")
report("enroll doc1-5, test doc6-7 (7-14 days later, different task type)", run(range(1, 6), (6, 7)))
report("same reading task: enroll doc1-3, test doc6", run((1, 2, 3), (6,)))
report("same image task: enroll doc4-5, test doc7", run((4, 5), (7,)))
report("same day, same task: enroll doc1-2, test doc3", run((1, 2), (3,)))
report("v_peak + v_mean only", run(range(1, 6), (6, 7), {"swipe_v_peak_mean", "swipe_v_mean_mean"}))


# (c) fix the rule: absolutely straight AND uniform velocity. Measured on real people and on bots (with/without timing noise)
def vcv(p):
    sp = [np.hypot(b["x"] - a["x"], b["y"] - a["y"]) / (b["t"] - a["t"]) for a, b in zip(p, p[1:]) if b["t"] > a["t"]]
    return float(np.std(sp) / np.mean(sp)) if len(sp) >= 2 and np.mean(sp) > 0 else 1.0


allp = [p for v in strokes.values() for p in v]
cv = np.array([vcv(p) for p in allp])
print("\n(c) new rule: straight > 0.999 AND velocity variation < threshold (real people have straight strokes but non-uniform velocity)")
bots = {j: [tactics._straight_swipe(rng, j)["points"] for _ in range(300)] for j in (False, True)}
for thr in (0.05, 0.1, 0.2, 0.3):
    hum = np.mean((straight > 0.999) & (cv < thr))
    b = {j: np.mean([features._swipe_stats(p)[2] > 0.999 and vcv(p) < thr for p in bots[j]]) for j in bots}
    print(f"    cv<{thr}: real people flagged {hum:.2%} of strokes | uniform bot {b[False]:.0%}, bot with ±6ms timing noise {b[True]:.0%}")

m6 = lens >= 6
print("    velocity uniformity alone (strokes >= 6 points), share of real people: " + ", ".join(f"cv<{t}: {np.mean(cv[m6] < t):.2%}" for t in (0.1, 0.2, 0.3)))
print("    strokes >= 3 points: " + ", ".join(f"cv<{t}: {np.mean(cv < t):.3%}" for t in (0.1, 0.2, 0.3)) + f" (n={len(cv)}); bot with timing noise has median cv {np.median([vcv(p) for p in bots[True]]):.2f}")
