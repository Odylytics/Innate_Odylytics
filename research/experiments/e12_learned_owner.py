"""E12 (task A): a LEARNED owner verification model on real humans (StrokePIN), compared with the backend's equal-weight distance.

The backend currently treats all features equally: d = mean(|z|). Here weights/interactions are learned from data:
  - LR: logistic regression on the |z| vector (31 features) -> learned, interpretable weights
  - LightGBM: gradient-boosted trees on |z|
Procedure: split by PERSON (60% training / 40% test, 3 splits). The population prior is computed only from training people (no leakage).
Enrollment template from k=3 sessions; a data row = (|z| of one test session against the template, label owner / PIN-knowing impostor).
Paired comparison with the baseline on the SAME test rows, bootstrap by person.
"""

import random
import sys
from collections import defaultdict
from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, owner  # noqa: E402
import strokepin_loader  # noqa: E402

K, N_DRAW, N_IMP, BOOT, SPLITS = 3, 4, 15, 60, (11, 12, 13)
NO_CONTACT = "--no-contact" in sys.argv  # control: drop touch size (it carries DEVICE information and vanishes when the impostor holds the victim's own phone)
EXCL = {"tap_w_mean", "tap_h_mean"} if NO_CONTACT else set()
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
TK = sorted(k for k in S[0]["f"] if k.startswith(("pin_hold_", "pin_flight_")) or k == "pin_total")
grp, bpp = defaultdict(list), defaultdict(lambda: defaultdict(list))
for e in S:
    grp[(e["user"], e["pin"])].append(e)
    bpp[e["pin"]][e["user"]].append(e)
USERS = sorted({e["user"] for e in S})
WV = {g: np.var(np.array([[e["f"][k] for k in TK] for e in es]), axis=0, ddof=1) for g, es in grp.items() if len(es) >= 2}


def make_rows(users, train_users, seed):
    """Rows (|z|, label 0=owner 1=impostor, person). Prior only from training people."""
    rng = random.Random(seed)
    pv = np.mean([v for (u, _p), v in WV.items() if u in train_users], axis=0)
    owner._PRIOR = {"within_var": dict(zip(TK, pv.tolist())), "n_taps": 6, "nu": 5}
    X, y, who = [], [], []
    for (u, p), es in grp.items():
        if u not in users or len(es) < K:
            continue
        for _ in range(N_DRAW):
            enr = rng.sample(es, K)
            tpl = owner.build_template([e["f"] for e in enr])
            keys = sorted(k for k in tpl["mu"] if k not in EXCL)
            gen = [e for e in es if e not in enr]
            if not gen:
                continue
            pool = [e for v, ves in bpp[p].items() if v != u for e in ves]
            for lab, ents in ((0, gen), (1, rng.sample(pool, min(N_IMP, len(pool))))):
                for e in ents:
                    z = owner.score(e["f"], tpl)[1]
                    X.append([abs(z[k]) for k in keys])
                    y.append(lab); who.append(u)
    return np.array(X), np.array(y), np.array(who), keys


def metrics(s, y):
    gen, imp = s[y == 0], s[y == 1]
    ths = np.unique(np.quantile(s, np.linspace(0, 1, 300)))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return np.array([(frr[i] + far[i]) / 2, (imp <= np.quantile(gen, 0.95)).mean()])


def boot(scores, y, who, base):
    rng = np.random.default_rng(0)
    us = np.unique(who); idx = {u: np.where(who == u)[0] for u in us}
    d = []
    for _ in range(BOOT):
        r = np.concatenate([idx[u] for u in rng.choice(us, len(us))])
        d.append(metrics(scores[r], y[r]) - metrics(base[r], y[r]))
    m = np.array(d)
    return np.quantile(m, 0.025, axis=0), np.quantile(m, 0.975, axis=0)


out = {}
weights = None
for sp in SPLITS:
    rng = random.Random(sp); us = USERS[:]; rng.shuffle(us)
    tr, te = set(us[:58]), set(us[58:])
    Xtr, ytr, _, keys = make_rows(tr, tr, sp)
    Xte, yte, wte, _ = make_rows(te, tr, sp + 100)
    base = Xte.mean(1)
    sc = StandardScaler().fit(Xtr)
    lr = LogisticRegression(C=1.0, max_iter=500).fit(sc.transform(Xtr), ytr)
    gb = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=30, subsample=0.8,
                            subsample_freq=1, colsample_bytree=0.8, random_state=sp, verbose=-1).fit(Xtr, ytr)
    sco = {"baseline (mean |z|, backend)": base, "LR with learned weights": lr.decision_function(sc.transform(Xte)),
           "learned LightGBM": gb.predict_proba(Xte)[:, 1]}
    if weights is None:
        weights = sorted(zip(keys, lr.coef_[0] / sc.scale_), key=lambda t: -abs(t[1]))[:8]
    for name, s in sco.items():
        est = metrics(s, yte)
        lo, hi = boot(s, yte, wte, base) if name != "baseline (mean |z|, backend)" else (np.zeros(2), np.zeros(2))
        out.setdefault(name, []).append((est, lo, hi))

L = ["# E12 — learned owner verification model (StrokePIN, real people)", "",
     f"Split by PERSON (58 training people / {len(USERS) - 58} test people), {len(SPLITS)} splits, averaged. Enrollment k={K} sessions, PIN-knowing impostor. "
     f"Features = |z| of {len(keys)} backend features" + (" (touch size REMOVED: device control). " if NO_CONTACT else ". ")
     + "The delta columns are relative to the baseline on the same test rows (negative = better); bootstrap CI by person, averaged across splits.", "",
     "| Model | EER | FAR @ FRR 5% | dEER vs baseline | dFAR vs baseline |", "|---|---|---|---|---|"]
for name, v in out.items():
    est = np.mean([x[0] for x in v], axis=0); lo = np.mean([x[1] for x in v], axis=0); hi = np.mean([x[2] for x in v], axis=0)
    if name.startswith("baseline"):
        L.append(f"| {name} | {est[0]:.3f} | {est[1]:.3f} | — | — |")
    else:
        b = np.mean([o[0] for o in out['baseline (mean |z|, backend)']], axis=0)
        L.append(f"| {name} | {est[0]:.3f} | {est[1]:.3f} | {est[0]-b[0]:+.3f} [{lo[0]:+.3f}, {hi[0]:+.3f}] | {est[1]-b[1]:+.3f} [{lo[1]:+.3f}, {hi[1]:+.3f}] |")
L += ["", "Largest weights learned by LR (first split; positive = a larger |z| raises the likelihood of an impostor; units not normalized across features):", ""]
L += [f"- `{k}`: {w:+.3f}" for k, w in weights]
(ROOT / ("research/results/e12b_learned_owner_no_contact.md" if NO_CONTACT else "research/results/e12_learned_owner.md")).write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
