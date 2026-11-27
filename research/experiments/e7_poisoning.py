"""E7: template poisoning attack ("gradual teaching") and defenses.

The attacker (Lovisotto 2020 style, strong: can craft arbitrary feature vectors) sends at each step a session lying
RIGHT AT THE UPDATE BOUNDARY (owner >= 0.8): x = mu + d*(x_impostor - mu) with the largest d still accepted,
so the template is gradually pulled toward the impostor. After n injections, measure:
  - impostor_accept: share of the impostor's REAL sessions (different persona) with owner >= 0.5
  - genuine_accept : share of the owner's new sessions with owner >= 0.5
Plus a "slowly drifting owner" scenario: the owner's habit changes by +15% in timing over 100 sessions, to test the cost of blocking updates.

Defenses (all use the same acceptance rule, differing in the update rule):
  none      : no cap
  cap1.0sd  : the current version of owner.py (each feature drifts at most 1 sd from enrollment)
  cap0.5sd, cap0.25sd : tighter caps
  freeze    : stop updating when the mean drift > 0.5 sd (directional drift), and raise a warning flag
SYNTHETIC personas (attacker/tactics.py): this checks the method, it is not a number for slides.
"""

import random
import sys
from pathlib import Path
from statistics import fmean

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker")]
from app.scoring import features, owner  # noqa: E402
from nhip_attacker import tactics  # noqa: E402

PIN, N_PAIRS, SEED = "159357", 100, 0
CHECKPOINTS = [0, 10, 25, 50, 100, 200]
ACCEPT, UPDATE_MIN = 0.5, 0.8  # UPDATE_MIN = the update threshold in main.py


def mean_drift_sd(tpl):
    return fmean(abs(tpl["mu"][k] - tpl["mu0"][k]) / tpl["sd"][k] for k in tpl["mu"])


def make_update(name):
    def upd(tpl, f):
        if name == "freeze":
            new = _raw_update(tpl, f, 1e9)
            return new if mean_drift_sd(new) <= 0.5 else tpl
        cap = {"none": 1e9, "cap1.0sd": 1.0, "cap0.5sd": 0.5, "cap0.25sd": 0.25}[name]
        return _raw_update(tpl, f, cap)
    return upd


def _raw_update(tpl, f, cap):
    old = owner.DRIFT_CAP
    owner.DRIFT_CAP = cap
    try:
        return owner.update(tpl, f)
    finally:
        owner.DRIFT_CAP = old


def craft(tpl, target):
    """The point closest to the impostor on the segment mu -> target where owner is still >= UPDATE_MIN (bisection)."""
    mu = tpl["mu"]
    lo, hi = 0.0, 1.0
    for _ in range(25):
        d = (lo + hi) / 2
        x = {k: mu[k] + d * (target[k] - mu[k]) for k in mu}
        s, _z = owner.score(x, tpl)
        lo, hi = (d, hi) if s >= UPDATE_MIN else (lo, d)
    return {k: mu[k] + lo * (target[k] - mu[k]) for k in mu}


def feats(sessions):
    return [features.extract(s) for s in sessions]


def rate(tpl, fs, thr=ACCEPT):
    return float(np.mean([owner.score(f, tpl)[0] >= thr for f in fs]))


DEFS = ["none", "cap1.0sd", "cap0.5sd", "cap0.25sd", "freeze"]
poison = {d: {c: {"imp": [], "gen": [], "drift": []} for c in CHECKPOINTS} for d in DEFS}
DRIFTS = [0.15, 0.30, 0.50]
drift_gen = {(d, g): [] for d in DEFS for g in DRIFTS}
drift_gen80 = {(d, g): [] for d in DEFS for g in DRIFTS}

rng = random.Random(SEED)
for i in range(N_PAIRS):
    own = tactics.synth_owner(f"o{i}", 5 + 20, PIN, tactics.DEFAULT_LAYOUT, seed=2 * i)
    imp = tactics.synth_owner(f"i{i}", 40, PIN, tactics.DEFAULT_LAYOUT, seed=2 * i + 1)
    f_enr, f_gen = feats(own[:5]), feats(own[5:])
    f_imp = feats(imp)
    base = owner.build_template(f_enr)
    target = {k: fmean(f[k] for f in f_imp if k in f) for k in base["mu"]}
    for d in DEFS:
        upd, tpl = make_update(d), base
        for n in range(max(CHECKPOINTS) + 1):
            if n in CHECKPOINTS:
                poison[d][n]["imp"].append(rate(tpl, f_imp))
                poison[d][n]["gen"].append(rate(tpl, f_gen))
                poison[d][n]["drift"].append(mean_drift_sd(tpl))
            tpl = upd(tpl, craft(tpl, target))
    # slowly drifting owner: the persona changes habit by +g in timing over 100 sessions, updating on each session that scores high enough
    p0 = tactics._persona(random.Random(2 * i))
    for g in DRIFTS:
        for d in DEFS:
            upd, tpl, r = make_update(d), base, random.Random(i)
            for t in range(100):
                p = {**p0, "hold": p0["hold"] * (1 + g * t / 99), "flight": p0["flight"] * (1 + g * t / 99)}
                f = features.extract(tactics._persona_session(f"o{i}", p, PIN, tactics.DEFAULT_LAYOUT, r))
                if owner.score(f, tpl)[0] >= UPDATE_MIN:
                    tpl = upd(tpl, f)
            p = {**p0, "hold": p0["hold"] * (1 + g), "flight": p0["flight"] * (1 + g)}
            fresh = feats([tactics._persona_session(f"o{i}", p, PIN, tactics.DEFAULT_LAYOUT, r) for _ in range(20)])
            drift_gen[(d, g)].append(rate(tpl, fresh))
            drift_gen80[(d, g)].append(rate(tpl, fresh, UPDATE_MIN))

lines = ["# E7 — template poisoning attack (synthetic data)", "",
         f"{N_PAIRS} (owner, impostor) pairs; the attacker injects sessions right at the update threshold (owner >= {UPDATE_MIN}). "
         f"'Accepted' = owner >= {ACCEPT}. Synthetic personas, this only checks the method.", "",
         "## Share of the impostor's REAL sessions accepted after n injections (lower is better)", "",
         "| Defense | " + " | ".join(f"n={c}" for c in CHECKPOINTS) + " |", "|---|" + "---|" * len(CHECKPOINTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(poison[d][c]['imp']):.2f}" for c in CHECKPOINTS) + " |")
lines += ["", "## Share of the owner's new sessions accepted after n injections (higher is better)", "",
          "| Defense | " + " | ".join(f"n={c}" for c in CHECKPOINTS) + " |", "|---|" + "---|" * len(CHECKPOINTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(poison[d][c]['gen']):.2f}" for c in CHECKPOINTS) + " |")
lines += ["", "## Mean drift of the template (in sd units) after n injections", "",
          "| Defense | " + " | ".join(f"n={c}" for c in CHECKPOINTS) + " |", "|---|" + "---|" * len(CHECKPOINTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(poison[d][c]['drift']):.2f}" for c in CHECKPOINTS) + " |")
lines += ["", "## The cost: a real owner who drifts slowly (hold/flight times grow gradually over 100 sessions) — share of the owner's new sessions accepted", "",
          "| Defense | " + " | ".join(f"+{int(g*100)}%" for g in DRIFTS) + " |", "|---|" + "---|" * len(DRIFTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(drift_gen[(d, g)]):.2f}" for g in DRIFTS) + " |")
lines += ["", f"Same scenario, but counting acceptance as owner >= {UPDATE_MIN} (the update threshold; more sensitive to the template failing to keep up with the owner):", "",
          "| Defense | " + " | ".join(f"+{int(g*100)}%" for g in DRIFTS) + " |", "|---|" + "---|" * len(DRIFTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(drift_gen80[(d, g)]):.2f}" for g in DRIFTS) + " |")
lines.append("")
out = ROOT / "research/results/e7_poisoning.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
