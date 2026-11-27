"""E11: human/bot task on a FREE-TEXT FIELD (transfer note) with REAL HUMANS (Aalto) and generated bots.

Humans = real typing rhythm of 2,263 people (Aalto typing37k; only timing, event type, character class; NO content), split by person.
Bots = 4 tactics in attacker/nhip_attacker/fields.py, ONLY the `note` field (Aalto has no amount/recipient fields):
  1 set text directly (ACTION_SET_TEXT)   2 even typing via an automation tool   3 replay the rhythm of a real person (±5%)   4 sample from the population
Features: (a) the existing `fld_*` in backend/bot_features.py; (b) "extended" = (a) + a few rhythm statistics computed inside the experiment,
to learn what the backend feature set is missing. Evaluation: FRR 5% threshold on humans in the validation set; all tactics / drop one tactic.
Limitations: the bots are still synthetic; a single field; people typed English sample sentences on a phone, not Vietnamese transfer-note content.
"""

import json
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
from nhip_attacker import fields  # noqa: E402

SEEDS, FRR, TACTICS = (1, 2, 3), 0.05, (1, 2, 3, 4)
N_H = {"train": 4000, "val": 1000, "test": 3000, "pool": 500}
N_BOT = {"train": 600, "val": 150, "test": 500}
BASE = [n for n in bot_features.FEATURE_NAMES if n.startswith("fld_")]
EXTRA = ["gap_std", "gap_p10", "gap_p50", "gap_p90", "succ_diff_rel", "n_keys"]


def to_session(rec):
    ev = []
    for t, kind, n, cls in rec["events"]:
        e = {"t": t, "kind": kind, "n": n}
        if cls:
            e["cls"] = cls
        ev.append(e)
    return {"user_id": rec["participant"], "pin_taps": [], "swipes": [], "screens": [], "fields": [{"name": "note", "events": ev}]}


H_ALL = [(r["participant"], to_session(r)) for r in map(json.loads, open(ROOT / "research/data/aalto_note_events.jsonl"))]
PEOPLE = sorted({p for p, _ in H_ALL})


def extra(sess):
    ev = sorted(sess["fields"][0]["events"], key=lambda e: e["t"]) if sess.get("fields") else []
    ts = [e["t"] for e in ev if e["kind"] == "key"]
    g = np.diff(ts) if len(ts) > 3 else np.array([np.nan])
    sd = np.abs(np.diff(g)).mean() / g.mean() if len(g) > 2 and g.mean() > 0 else np.nan
    return [np.std(g), *np.nanpercentile(g, [10, 50, 90]), sd, float(len(ts))] if len(ts) > 3 else [np.nan] * 6


def vec(sessions, ext):
    rows = []
    for s in sessions:
        f = bot_features.extract(s)
        rows.append([f[k] for k in BASE] + (extra(s) if ext else []))
    return np.array(rows, dtype=float)


def build(seed):
    rng = random.Random(seed)
    ps = PEOPLE[:]
    rng.shuffle(ps)
    cut = {"pool": ps[:200], "train": ps[200:1400], "val": ps[1400:1700], "test": ps[1700:]}
    H = {}
    for k, who in cut.items():
        ses = [s for p, s in H_ALL if p in set(who)]
        H[k] = rng.sample(ses, min(N_H[k], len(ses)))
    pool = H["pool"]
    B = {t: {} for t in TACTICS}
    for t in TACTICS:
        for k in ("train", "val", "test"):
            out = []
            for _ in range(N_BOT[k]):
                src = rng.choice(pool)
                fl = [f for f in fields.for_tactic(t, rng, pool, src) if f["name"] == "note"]
                out.append({"user_id": "victim", "pin_taps": [], "swipes": [], "screens": [], "fields": fl})
            B[t][k] = out
    return H, B


def metrics(sc, thr, hum, bots):
    out = {"FRR": float((sc(hum) < thr).mean())}
    sh = sc(hum)
    for t, X in bots.items():
        sb = sc(X)
        out[t] = (float((sb < thr).mean()), float(roc_auc_score(np.r_[np.ones(len(sh)), np.zeros(len(sb))], np.r_[sh, sb])))
    return out


def evaluate(seed):
    H, B = build(seed)
    res = {}
    for ext, tag in ((False, "backend (fld_*)"), (True, "extended")):
        F = {("H", k): vec(H[k], ext) for k in ("train", "val", "test")}
        F.update({(t, k): vec(B[t][k], ext) for t in TACTICS for k in ("train", "val", "test")})
        for scen, held in [("all", None)] + [(f"drop T{t}", t) for t in TACTICS]:
            tr = [t for t in TACTICS if t != held]
            m = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=20, subsample=0.8,
                                   subsample_freq=1, colsample_bytree=0.8, random_state=seed, verbose=-1)
            m.fit(np.vstack([F[("H", "train")]] + [F[(t, "train")] for t in tr]),
                  np.r_[np.ones(len(F[("H", "train")])), np.zeros(sum(len(F[(t, "train")]) for t in tr))])
            iso = IsolationForest(n_estimators=200, random_state=seed).fit(np.nan_to_num(F[("H", "train")], nan=-1))
            test_b = {t: F[(t, "test")] for t in (TACTICS if held is None else [held])}
            for name, sc in ((f"LightGBM, {tag}", lambda X, m=m: m.predict_proba(X)[:, 1]),
                             (f"IsolationForest, {tag}", lambda X, iso=iso: iso.score_samples(np.nan_to_num(X, nan=-1)))):
                res[(name, scen)] = metrics(sc, np.quantile(sc(F[("H", "val")]), FRR), F[("H", "test")], test_b)
    # current backend rules on these very sessions (a new amount field is treated as a bot; the note field only gets a mild deduction)
    rs = lambda S: np.array([human.score(features.extract(s))[0] for s in S])  # noqa: E731
    row = {"FRR": float((rs(H["test"]) < 0.5).mean())}
    for t in TACTICS:
        row[t] = (float((rs(B[t]["test"]) < 0.5).mean()), float("nan"))
    res[("Current backend rules (flag when score < 0.5)", "no training")] = row
    return res


all_res = [evaluate(s) for s in SEEDS]
keys = list(all_res[0])


def cell(r, t):
    return f"{np.mean([x[t][0] for x in r]):.2f}" + ("" if np.isnan(np.mean([x[t][1] for x in r])) else f" ({np.mean([x[t][1] for x in r]):.2f})")


L = ["# E11 — human/bot task on a free-text field (real Aalto humans + generated bots)", "",
     f"{len(SEEDS)} different splits of people. Humans: {len(H_ALL)} real typed sentences from {len(PEOPLE)} people, split by person (attacker pool 200 / train 1200 / val 300 / test the rest). "
     f"FRR {FRR:.0%} threshold on humans in the validation set. Each cell: **share of bots caught** (AUC). Only the `note` field. The bots are still synthetic.", "",
     "## Training saw all 4 tactics", "", "| Model | Actual FRR | T1 set text directly | T2 even typing | T3 replay | T4 population sampling |", "|---|---|---|---|---|---|"]
for k in keys:
    if k[1] not in ("all", "no training"):
        continue
    r = [x[k] for x in all_res]
    L.append(f"| {k[0]} | {np.mean([x['FRR'] for x in r]):.3f} | " + " | ".join(cell(r, t) for t in TACTICS) + " |")
L += ["", "## Drop exactly one tactic from training (unseen bots)", "", "| Model | Actual FRR | Drop T1 | Drop T2 | Drop T3 | Drop T4 |", "|---|---|---|---|---|---|"]
for name in dict.fromkeys(k[0] for k in keys if k[1].startswith("drop")):
    cells, frr = [], []
    for t in TACTICS:
        r = [x[(name, f"drop T{t}")] for x in all_res]
        cells.append(cell(r, t))
        frr += [x["FRR"] for x in r]
    L.append(f"| {name} | {np.mean(frr):.3f} | " + " | ".join(cells) + " |")
(ROOT / "research/results/e11_text_field_bots.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
