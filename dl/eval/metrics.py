"""EER, FAR@FRR=5%, Gini and person-clustered bootstrap CIs, stratified by enrolment count k and time gap dt."""

import numpy as np

K_BUCKETS = ("2", "3", "4", "5+")
DT_BUCKETS = ("<=1h", "1h-1d", ">1d")


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    s = np.concatenate([pos, neg])
    r = s.argsort().argsort() + 1.0
    for v in np.unique(s):  # average ranks over ties
        m = s == v
        r[m] = r[m].mean()
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def far_at_frr(pos: np.ndarray, neg: np.ndarray, frr: float = 0.05) -> float:
    """Higher score = more genuine. Threshold rejects `frr` of genuine entries; returns the share of impostors accepted."""
    thr = np.quantile(pos, frr)
    return float((neg >= thr).mean())


def eer(pos: np.ndarray, neg: np.ndarray) -> float:
    ts = np.unique(np.concatenate([pos, neg]))
    frr = np.array([(pos < t).mean() for t in ts])
    far = np.array([(neg >= t).mean() for t in ts])
    i = np.argmin(abs(frr - far))
    return float((frr[i] + far[i]) / 2)


def gini(pos, neg) -> float:
    return 2 * auc(pos, neg) - 1


def stats(score, y) -> dict:
    pos, neg = score[y == 1], score[y == 0]
    if len(pos) < 2 or len(neg) < 2:
        return {"n_pos": len(pos), "n_neg": len(neg), "eer": None, "far@frr5": None, "gini": None}
    return {"n_pos": len(pos), "n_neg": len(neg), "eer": eer(pos, neg), "far@frr5": far_at_frr(pos, neg), "gini": gini(pos, neg)}


def k_bucket(k) -> np.ndarray:
    return np.array([str(min(int(x), 5)) if x < 5 else "5+" for x in k])


def dt_bucket(dt_h) -> np.ndarray:
    return np.where(dt_h <= 1, DT_BUCKETS[0], np.where(dt_h <= 24, DT_BUCKETS[1], DT_BUCKETS[2]))


def bootstrap(score, y, person, n: int = 200, seed: int = 0) -> dict:
    """95% CI of each metric, resampling PEOPLE (entries of one person are not independent)."""
    rng = np.random.default_rng(seed)
    people = np.unique(person)
    groups = {p: np.flatnonzero(person == p) for p in people}
    runs = []
    for _ in range(n):
        idx = np.concatenate([groups[p] for p in rng.choice(people, len(people))])
        s = stats(score[idx], y[idx])
        if s["eer"] is not None:
            runs.append((s["eer"], s["far@frr5"], s["gini"]))
    if not runs:
        return {}
    lo, hi = np.percentile(runs, [2.5, 97.5], axis=0)
    return {m: (round(float(a), 3), round(float(b), 3)) for m, a, b in zip(("eer", "far@frr5", "gini"), lo, hi)}


def report(score, y, person, k, dt_h, n_boot: int = 200) -> dict:
    """Overall + per k bucket + per dt bucket, each with a bootstrap CI."""
    out = {"all": {**stats(score, y), "ci": bootstrap(score, y, person, n_boot)}}
    for name, key in (("k", k_bucket(k)), ("dt", dt_bucket(dt_h))):
        for b in sorted(set(key)):
            m = key == b
            out[f"{name}={b}"] = {**stats(score[m], y[m]), "ci": bootstrap(score[m], y[m], person[m], n_boot)}
    return out


def fmt(rep: dict) -> str:
    f = lambda v: "  -  " if v is None else f"{v:.3f}"  # noqa: E731
    lines = [f"{'slice':10s} {'n+':>5s} {'n-':>5s} {'EER':>6s} {'FAR@FRR5':>9s} {'Gini':>6s}  95% CI(FAR@FRR5)"]
    for k, r in rep.items():
        lines.append(f"{k:10s} {r['n_pos']:5d} {r['n_neg']:5d} {f(r['eer']):>6s} {f(r['far@frr5']):>9s} {f(r['gini']):>6s}  {r['ci'].get('far@frr5', '')}")
    return "\n".join(lines)
