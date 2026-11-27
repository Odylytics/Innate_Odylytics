"""E3: calibrate the distance -> owner score mapping of owner.py on real PINs (StrokePIN).

Uses owner.build_template/score as is. Enroll 3 sitting sessions; owner = the remaining sitting sessions; PIN-knowing impostor = another person, same PIN, same posture.
Split people into two halves: fit Platt (a,b) on half A, test on half B (no person leakage). Compare with the current mapping (d=2 -> 0.5).
"""
import math, random, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, owner  # noqa: E402
import strokepin_loader  # noqa: E402

rng = random.Random(0)
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
grp = defaultdict(list)
for e in S:
    if e["posture"] == "sit":
        grp[(e["user"], e["pin"])].append(e)
by_pin = defaultdict(list)
for (u, p), es in grp.items():
    by_pin[p] += [(u, e) for e in es]
users = sorted({u for u, _ in grp})
rng.shuffle(users)
half = {u: i % 2 for i, u in enumerate(users)}
rows = []  # (half, label, d)
for (u, p), es in grp.items():
    if len(es) < 5:
        continue
    enr = rng.sample(es, 3)
    tpl = owner.build_template([e["f"] for e in enr])
    def d(e):
        _, z = owner.score(e["f"], tpl)
        return float(np.mean([abs(v) for v in z.values()]))
    for e in es:
        if e not in enr:
            rows.append((half[u], 1, d(e)))
    imps = [e for v, e in by_pin[p] if v != u]
    for e in rng.sample(imps, min(20, len(imps))):
        rows.append((half[u], 0, d(e)))
R = np.array(rows)
def fit(x, y):  # Platt by gradient descent, no sklearn dependency
    a, b = -1.0, 2.0
    for _ in range(4000):
        p = 1 / (1 + np.exp(-(a * x + b)))
        w = np.where(y == 1, 0.5 / y.mean(), 0.5 / (1 - y.mean()))  # class balance: owner and impostor weigh the same
        a -= 0.05 * (w * (p - y) * x).mean(); b -= 0.05 * (w * (p - y)).mean()
    return a, b
A, B = R[R[:, 0] == 0], R[R[:, 0] == 1]
a, b = fit(A[:, 2], A[:, 1])
sig = lambda x, a, b: 1 / (1 + np.exp(-(a * x + b)))
old = lambda x: 1 / (1 + np.exp(np.minimum(2 * (x - 2), 700)))
out = [f"# E3 — owner score calibration (StrokePIN, 6-digit PIN, enrollment on 3 sitting sessions)", "",
       f"Platt fit on half A ({len(A)} sessions): score = sigmoid({a:.3f}·d + {b:.3f}). Tested on half B ({len(B)} sessions, entirely different people).", "",
       "| Mapping | Owner with score ≥ 0.5 | PIN-knowing impostor with score ≥ 0.5 |", "|---|---|---|"]
for name, f in (("current (d=2→0.5)", old), (f"Fitted Platt (class-balanced)", lambda x: sig(x, a, b))):
    s = f(B[:, 2]); g, i = s[B[:, 1] == 1], s[B[:, 1] == 0]
    out.append(f"| {name} | {(g >= .5).mean():.2f} | {(i >= .5).mean():.2f} |")
g = B[B[:, 1] == 1, 2]; i = B[B[:, 1] == 0, 2]
t = np.quantile(g, 0.95)
out += ["", f"d threshold for FRR 5% (half B): d={t:.2f}; FAR there = {(i <= t).mean():.2f}. Median d: owner {np.median(g):.2f}, impostor {np.median(i):.2f}.",
        "", "Conclusion: see the numbers above. Platt only shifts the threshold and adds no separation; FAR@FRR5% is still decided by the features (E9/E12b)."]
Path(ROOT / "research/results/e3_calibrate_owner.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
