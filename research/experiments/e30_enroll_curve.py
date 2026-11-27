"""E30: number of enrollment sessions k (2, 3, 4) and error distribution by victim, owner recognition by the backend distance (owner.py), StrokePIN.

StrokePIN has at most 5 sessions per (person, PIN): k=4 leaves 1 test session; k=1 has no standard deviation (dropped); k=5 leaves no test session.
Population prior: the backend's population_prior.json file (computed from a subset of people, without excluding each victim individually: may be slightly optimistic).
Impostor = another person entering the same PIN on their own device (confounded with device noise). Score = mean |z|; a common threshold is chosen for FRR 5%.
Gini by victim: FAR of each victim at the common threshold (Eberz 2017: the average hides people who are "always let through").
Run (from backend/): uv run --with pandas --with numpy --with scikit-learn --with lightgbm python ../research/experiments/e30_enroll_curve.py
"""
import random, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, owner  # noqa: E402
import strokepin_loader  # noqa: E402

rng = random.Random(30)
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
grp = defaultdict(list); by_pin = defaultdict(list)
for e in S:
    grp[(e["user"], e["pin"])].append(e); by_pin[e["pin"]].append(e)
USERS = sorted({u for u, _ in grp})


def dist(e, tpl):
    return float(np.mean([abs(v) for v in owner.score(e["f"], tpl)[1].values()]))


def eer_far(gen, imp):
    thr = np.quantile(gen, 0.95)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 400)))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths]); i = np.argmin(abs(frr - far))
    return (frr[i] + far[i]) / 2, thr


def gini(x):
    x = np.sort(np.asarray(x)); n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum())) if x.sum() else 0.0


L = ["# E30 — number of enrollment sessions and error distribution by victim (StrokePIN, backend distance)", "",
     "k=1 has no standard deviation; k=5 leaves no test session (at most 5 sessions per person-PIN). 95% CI by bootstrap over people. "
     "FAR@FRR5% uses a common threshold; the Gini and 'victims with FAR>90%' columns are per victim (the account owner).", "",
     "| k | EER | FAR@FRR5% | Gini of FAR by victim | victims with FAR > 90% | median victim FAR |", "|---|---|---|---|---|---|"]
for k in (2, 3, 4):
    G, I = defaultdict(list), defaultdict(list)
    for (u, p), es in grp.items():
        if len(es) < 5: continue
        for _ in range(5):
            enr = rng.sample(es, k); tpl = owner.build_template([e["f"] for e in enr])
            G[u] += [dist(e, tpl) for e in es if e not in enr]
            others = [e for e in by_pin[p] if e["user"] != u]
            I[u] += [dist(e, tpl) for e in rng.sample(others, min(15, len(others)))]
    def pooled(us): return np.concatenate([G[u] for u in us]), np.concatenate([I[u] for u in us])
    def metr(us):
        g, i = pooled(us); eer, thr = eer_far(g, i); return eer, float((i <= thr).mean())
    est = metr(USERS); bs = np.array([metr([USERS[rng.randrange(len(USERS))] for _ in USERS]) for _ in range(100)])
    g, i = pooled(USERS); thr = np.quantile(g, 0.95)
    far_u = np.array([(np.array(I[u]) <= thr).mean() for u in USERS])
    ci = lambda j: f"{est[j]:.3f} [{np.quantile(bs[:, j], .025):.3f}, {np.quantile(bs[:, j], .975):.3f}]"  # noqa: E731
    L.append(f"| {k} | {ci(0)} | {ci(1)} | {gini(far_u):.2f} | {(far_u > 0.9).sum()}/{len(USERS)} | {np.median(far_u):.2f} |")
    print(L[-1], flush=True)
Path(ROOT / "research/results/e30_enroll_curve.md").write_text("\n".join(L) + "\n", encoding="utf-8")
