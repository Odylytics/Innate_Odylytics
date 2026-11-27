"""E4: LightGBM for the "human or bot" task, compared with the baseline rules, using LEAVE-ONE-TACTIC-OUT evaluation.

Data is entirely SYNTHETIC (humans: attacker/tactics.synth_humans, bots: the team's own 4 tactics).
So this (a) checks the pipeline and the evaluation procedure, (b) shows what the model learns and what it does NOT learn,
and is NOT a number for slides. The source must be replaced with real human sessions and real bots (adb, dispatchGesture).

Evaluation:
  - the threshold is chosen on humans in the validation set so that 5% of humans are mistaken for bots (FRR 5%), WITHOUT using the test-set bots
  - "all tactics": training sees all 4 tactics (optimistic)
  - "drop one tactic": training sees only 3, test on the remaining tactic (more realistic for unseen bots)
  - "no touch size": drop the w/h group, because a device may not measure it and a real bot sets arbitrary values
  - the attacker uses a SEPARATE pool of humans (not overlapping the training/test sets) for tactics 3 and 4
"""

import random
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker")]
from app.scoring import bot_features, features, human  # noqa: E402
from nhip_attacker import tactics  # noqa: E402

PIN, SEEDS, FRR = "159357", (1, 2, 3), 0.05
N_H = {"train": 1500, "val": 600, "test": 1000, "pool": 400}
N_BOT = {"train": 400, "val": 150, "test": 300}  # per tactic
TACTICS = (1, 2, 3, 4)
ALL = bot_features.FEATURE_NAMES
NO_CONTACT = [n for n in ALL if n not in bot_features.CONTACT_FEATURES]


def humans(n, seed):
    return tactics.synth_humans(n, PIN, tactics.DEFAULT_LAYOUT, seed=seed)


def bots(t, n, pool, seed):
    rng = random.Random(seed)
    return [tactics.generate(t, "victim", PIN, pool, rng) for _ in range(n)]


def vec(sessions, names):
    return np.array([[bot_features.extract(s)[k] for k in names] for s in sessions], dtype=float)


def rule_score(sessions):
    return np.array([human.score(features.extract(s))[0] for s in sessions])


def build(seed):
    pool = humans(N_H["pool"], 1000 + seed)
    d = {"H": {}, "B": {t: {} for t in TACTICS}}
    for i, split in enumerate(("train", "val", "test")):
        d["H"][split] = humans(N_H[split], 10 * seed + i)
        for t in TACTICS:
            d["B"][t][split] = bots(t, N_BOT[split], pool, 100 * seed + 10 * t + i)
    return d


def fit_lgb(Xh, Xb, seed):
    X = np.vstack([Xh, Xb])
    y = np.r_[np.ones(len(Xh)), np.zeros(len(Xb))]  # 1 = human
    m = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=20, subsample=0.8,
                           subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, random_state=seed, verbose=-1)
    return m.fit(X, y)


def evaluate(d, seed):
    """-> {(model, scenario): {tactic: (catch rate, AUC), 'FRR': ...}}"""
    res = {}
    H = {s: d["H"][s] for s in d["H"]}
    for names, tag in ((ALL, ""), (NO_CONTACT, " (no touch size)")):
        feats = {("H", s): vec(H[s], names) for s in H}
        feats.update({(t, s): vec(d["B"][t][s], names) for t in TACTICS for s in ("train", "val", "test")})
        for scen, held in [("all tactics", None)] + [(f"drop tactic {t}", t) for t in TACTICS]:
            train_t = [t for t in TACTICS if t != held]
            Xb = np.vstack([feats[(t, "train")] for t in train_t])
            m = fit_lgb(feats[("H", "train")], Xb, seed)
            iso = IsolationForest(n_estimators=200, random_state=seed).fit(feats[("H", "train")])
            scorers = {"LightGBM" + tag: lambda X, m=m: m.predict_proba(X)[:, 1],
                       "IsolationForest (humans only)" + tag: lambda X, iso=iso: iso.score_samples(X)}
            for name, sc in scorers.items():
                thr = np.quantile(sc(feats[("H", "val")]), FRR)  # flag if score < thr
                row = {"FRR": float((sc(feats[("H", "test")]) < thr).mean())}
                for t in (TACTICS if held is None else [held]):
                    s_b, s_h = sc(feats[(t, "test")]), sc(feats[("H", "test")])
                    row[t] = (float((s_b < thr).mean()), float(roc_auc_score(np.r_[np.ones(len(s_h)), np.zeros(len(s_b))],
                                                                               np.r_[s_h, s_b])))
                res[(name, scen)] = row
            # combined: flag if LightGBM OR IsolationForest flags; each model at FRR ~2.7% so the union is ~5%
            sl, si = scorers["LightGBM" + tag], scorers["IsolationForest (humans only)" + tag]
            tl, ti = (np.quantile(f(feats[("H", "val")]), 0.0267) for f in (sl, si))
            flag = lambda X: (sl(X) < tl) | (si(X) < ti)  # noqa: E731
            row = {"FRR": float(flag(feats[("H", "test")]).mean())}
            for t in (TACTICS if held is None else [held]):
                row[t] = (float(flag(feats[(t, "test")]).mean()), float("nan"))
            res[("Combined (LightGBM or IsolationForest)" + tag, scen)] = row
    # baseline rules: no training, so only one scenario
    sv = rule_score(d["H"]["val"])
    thr = np.quantile(sv, FRR)
    # many humans score 1.0 -> the threshold can tie; flip the sign with "<=" if thr == 1
    flag = (lambda s: s <= thr) if thr >= 1 else (lambda s: s < thr)
    sh = rule_score(d["H"]["test"])
    row = {"FRR": float(flag(sh).mean())}
    for t in TACTICS:
        sb = rule_score(d["B"][t]["test"])
        row[t] = (float(flag(sb).mean()), float(roc_auc_score(np.r_[np.ones(len(sh)), np.zeros(len(sb))], np.r_[sh, sb])))
    res[("Baseline rules (human.py)", "no training")] = row
    return res


all_res = [evaluate(build(s), s) for s in SEEDS]
keys = list(all_res[0])
lines = ["# E4 — LightGBM for the human/bot task (synthetic data)", "",
         f"{len(SEEDS)} independent data generations, averaged. The threshold is chosen on humans in the validation set so that FRR = {FRR:.0%}. "
         "Each cell is the **share of bots caught** (AUC in parentheses). Synthetic data: this only checks the pipeline.", ""]
for scen in ("all tactics",):
    lines += [f"## Training saw all 4 tactics (optimistic)", "", "| Model | Actual FRR | Tactic 1 | 2 | 3 | 4 |", "|---|---|---|---|---|---|"]
    for k in keys:
        if k[1] not in (scen, "no training"):
            continue
        r = [x[k] for x in all_res]
        cells = [f"{np.mean([x[t][0] for x in r]):.2f} ({np.mean([x[t][1] for x in r]):.2f})" for t in TACTICS]
        lines.append(f"| {k[0]} | {np.mean([x['FRR'] for x in r]):.3f} | " + " | ".join(cells) + " |")
lines += ["", "## Drop one tactic from training, test on exactly that tactic (more realistic for unseen bots)", "",
          "| Model | Actual FRR | Drop tactic 1 | Drop 2 | Drop 3 | Drop 4 |", "|---|---|---|---|---|---|"]
for name in dict.fromkeys(k[0] for k in keys if k[1].startswith("drop")):
    cells, frr = [], []
    for t in TACTICS:
        r = [x[(name, f"drop tactic {t}")] for x in all_res]
        cells.append(f"{np.mean([x[t][0] for x in r]):.2f} ({np.mean([x[t][1] for x in r]):.2f})")
        frr += [x["FRR"] for x in r]
    lines.append(f"| {name} | {np.mean(frr):.3f} | " + " | ".join(cells) + " |")

# feature importance of the full model (gain), to see what the model relies on
d = build(SEEDS[0])
Xh, Xb = vec(d["H"]["train"], ALL), np.vstack([vec(d["B"][t]["train"], ALL) for t in TACTICS])
m = fit_lgb(Xh, Xb, SEEDS[0])
gain = m.booster_.feature_importance("gain")
order = np.argsort(gain)[::-1][:8]
lines += ["", "## Which features the model relies on (gain, full model)", "", "| Feature | Gain share |", "|---|---|"]
lines += [f"| {ALL[i]} | {gain[i] / gain.sum():.2f} |" for i in order]
(ROOT / "research/models").mkdir(exist_ok=True)
m.booster_.save_model(str(ROOT / "research/models/human_lgbm_synthetic.txt"))
lines += ["", "The full model is saved at `research/models/human_lgbm_synthetic.txt` (trained on SYNTHETIC data, **not used for the submission**).", ""]
(ROOT / "research/results/e4_human_bot_lgbm.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
