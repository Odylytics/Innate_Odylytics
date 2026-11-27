"""E4b: the "human or bot" task with REAL HUMANS (StrokePIN) and generator-made bots, leave-one-tactic-out evaluation.

Unlike E4 (synthetic humans): the humans are real PIN sessions. The bots are still the team's 4 tactics (attacker/tactics.py) but built
on real PINs and the real human distribution (tactic 3 replays a real human session, tactic 4 samples from the real population).
Split by PERSON (no person appears in two sets): train / val / test / attacker pool.
Only the PIN part is compared: StrokePIN has no swipes/screens, so the bots also have swipes/screens removed (otherwise bots would differ from humans in an irrelevant way).
The actual FRR on humans in the test set can deviate from 5% because test people use different devices than validation people: that is a result, not a bug.
Limitation: the bots are still synthetic. No real bots yet (adb, dispatchGesture).
"""

import random
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker"), str(Path(__file__).parent)]
from app.scoring import bot_features, features, human  # noqa: E402
from nhip_attacker import tactics  # noqa: E402
import strokepin_loader  # noqa: E402

SEEDS, FRR, TACTICS = (1, 2, 3), 0.05, (1, 2, 3, 4)
N_H = {"train": 3000, "val": 1000, "test": 3000, "pool": 400}
N_BOT = {"train": 500, "val": 150, "test": 400}
ALL = bot_features.FEATURE_NAMES
NO_CONTACT = [n for n in ALL if n not in bot_features.CONTACT_FEATURES]

S = strokepin_loader.load()
USERS = sorted({e["user"] for e in S})
PINS = sorted({e["pin"] for e in S})


def clean(sess):
    return {**sess, "swipes": [], "screens": []}


def build(seed):
    rng = random.Random(seed)
    us = USERS[:]
    rng.shuffle(us)
    split = {"train": us[:40], "val": us[40:52], "test": us[52:82], "pool": us[82:]}
    H = {}
    for k, v in split.items():
        pool = [e["session"] for e in S if e["user"] in set(v)]
        H[k] = rng.sample(pool, min(N_H[k], len(pool)))
    d = {"H": H, "B": {t: {} for t in TACTICS}}
    for t in TACTICS:
        for k in ("train", "val", "test"):
            d["B"][t][k] = [clean(tactics.generate(t, "victim", rng.choice(PINS), H["pool"], rng)) for _ in range(N_BOT[k])]
    return d


def vec(sessions, names):
    return np.array([[bot_features.extract(s)[k] for k in names] for s in sessions], dtype=float)


def rule_score(sessions):
    return np.array([human.score(features.extract(s))[0] for s in sessions])


def fit_lgb(Xh, Xb, seed):
    X, y = np.vstack([Xh, Xb]), np.r_[np.ones(len(Xh)), np.zeros(len(Xb))]
    return lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=20, subsample=0.8,
                              subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, random_state=seed, verbose=-1).fit(X, y)


def metrics(sc, thr, hum, bots):
    out = {"FRR": float((sc(hum) < thr).mean())}
    for t, X in bots.items():
        sb = sc(X)
        out[t] = (float((sb < thr).mean()), float(roc_auc_score(np.r_[np.ones(len(hum)), np.zeros(len(sb))], np.r_[sc(hum), sb])))
    return out


def evaluate(d, seed):
    res = {}
    for names, tag in ((ALL, ""), (NO_CONTACT, " (no touch size)")):
        F = {("H", k): vec(d["H"][k], names) for k in ("train", "val", "test")}
        F.update({(t, k): vec(d["B"][t][k], names) for t in TACTICS for k in ("train", "val", "test")})
        for scen, held in [("all tactics", None)] + [(f"drop tactic {t}", t) for t in TACTICS]:
            tr = [t for t in TACTICS if t != held]
            m = fit_lgb(F[("H", "train")], np.vstack([F[(t, "train")] for t in tr]), seed)
            iso = IsolationForest(n_estimators=200, random_state=seed).fit(F[("H", "train")])
            sl, si = (lambda X, m=m: m.predict_proba(X)[:, 1]), (lambda X, iso=iso: iso.score_samples(X))
            test_b = {t: F[(t, "test")] for t in (TACTICS if held is None else [held])}
            for name, sc in (("LightGBM" + tag, sl), ("IsolationForest (humans only)" + tag, si)):
                res[(name, scen)] = metrics(sc, np.quantile(sc(F[("H", "val")]), FRR), F[("H", "test")], test_b)
            tl, ti = (np.quantile(f(F[("H", "val")]), 0.0267) for f in (sl, si))
            ens = lambda X: np.where((sl(X) < tl) | (si(X) < ti), 0.0, 1.0)  # noqa: E731
            res[("Combined" + tag, scen)] = metrics(ens, 0.5, F[("H", "test")], test_b)
    sv = rule_score(d["H"]["val"])
    thr = np.quantile(sv, FRR)
    sh = rule_score(d["H"]["test"])
    flag = (lambda s: s <= thr) if thr >= 1 else (lambda s: s < thr)
    row = {"FRR": float(flag(sh).mean())}
    for t in TACTICS:
        sb = rule_score(d["B"][t]["test"])
        row[t] = (float(flag(sb).mean()), float(roc_auc_score(np.r_[np.ones(len(sh)), np.zeros(len(sb))], np.r_[sh, sb])))
    res[("Baseline rules (human.py)", "no training")] = row
    return res


all_res = [evaluate(build(s), s) for s in SEEDS]
keys = list(all_res[0])


def cell(r, t):
    return f"{np.mean([x[t][0] for x in r]):.2f}" + ("" if np.isnan(np.mean([x[t][1] for x in r])) else f" ({np.mean([x[t][1] for x in r]):.2f})")


lines = ["# E4b — human/bot with REAL HUMANS (StrokePIN) and generator-made bots", "",
         f"{len(SEEDS)} different splits of people (train 40 / val 12 / test 30 / attacker pool 15 people, no person in two sets). "
         f"The threshold is chosen so that FRR = {FRR:.0%} on humans in the validation set. Each cell: **share of bots caught** (AUC). "
         "Only the PIN part is compared. The bots are still synthetic.", "",
         "## Training saw all 4 tactics", "", "| Model | Actual FRR (test humans) | T1 | T2 | T3 | T4 |", "|---|---|---|---|---|---|"]
for k in keys:
    if k[1] not in ("all tactics", "no training"):
        continue
    r = [x[k] for x in all_res]
    lines.append(f"| {k[0]} | {np.mean([x['FRR'] for x in r]):.3f} | " + " | ".join(cell(r, t) for t in TACTICS) + " |")
lines += ["", "## Drop exactly one tactic from training, test on that tactic (unseen bots)", "",
          "| Model | Actual FRR | Drop T1 | Drop T2 | Drop T3 | Drop T4 |", "|---|---|---|---|---|---|"]
for name in dict.fromkeys(k[0] for k in keys if k[1].startswith("drop")):
    cells, frr = [], []
    for t in TACTICS:
        r = [x[(name, f"drop tactic {t}")] for x in all_res]
        cells.append(cell(r, t))
        frr += [x["FRR"] for x in r]
    lines.append(f"| {name} | {np.mean(frr):.3f} | " + " | ".join(cells) + " |")
(ROOT / "research/results/e4b_human_bot_real.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
