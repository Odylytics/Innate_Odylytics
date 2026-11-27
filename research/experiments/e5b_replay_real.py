"""E5b: calibrate the replay check on REAL HUMANS (StrokePIN), using the backend's own replay.distance.

Account history = the entries of the SAME PIN by the SAME person (~5 entries; a real user enters one PIN).
 - Real human: each entry is compared with the remaining entries of the same group -> nearest distance. At which threshold is it mistaken for a replay?
 - Replay: take one entry from the history, add timing noise ±n and coordinate noise ±max(0.02, 0.4n) key widths (as in E5, converted to units of
   key width so it does not depend on the device), compare with the whole history (including the original). How many are caught?
The history is only ~4 entries, so the "more old sessions raise FPR" effect of E5 (seen at 4-digit PIN, history 200) can NOT be measured: see the limits.
"""

import copy
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, replay  # noqa: E402
import strokepin_loader  # noqa: E402

SEED, NOISES, CUR_THR = 0, (0.025, 0.05, 0.10, 0.15, 0.20, 0.30), replay.REPLAY_THRESHOLD
rng = random.Random(SEED)
S = strokepin_loader.load()
grp = defaultdict(list)
for e in S:
    grp[(e["user"], e["pin"])].append(e)
grp = {k: v for k, v in grp.items() if len(v) >= 4}


def replay_of(sess, noise):
    s = copy.deepcopy(sess)
    taps, t = sorted(s["pin_taps"], key=lambda x: x["t_down"]), 0.0
    jit = max(0.02, 0.4 * noise)
    for i, tap in enumerate(taps):
        hold = (tap["t_up"] - tap["t_down"]) * rng.uniform(1 - noise, 1 + noise)
        gap = (taps[i + 1]["t_down"] - tap["t_up"]) * rng.uniform(1 - noise, 1 + noise) if i < len(taps) - 1 else 0
        tap["x"] += rng.uniform(-jit, jit) * tap["key_w"]
        tap["y"] += rng.uniform(-jit, jit) * tap["key_h"]
        tap["t_down"], tap["t_up"] = t, t + hold
        t += hold + max(gap, 0)
    s["pin_taps"] = taps
    return s


def nearest(f, hist):
    ds = [d for h in hist if (d := replay.distance(f, h)) is not None]
    return min(ds) if ds else np.inf


# 1) new real human vs history, by history size
gen = {h: [] for h in (2, 3, 4)}  # each pair has ~5 entries, so history is at most 4
for (u, p), es in grp.items():
    for i, e in enumerate(es):
        others = [x["f"] if "f" in x else features.extract(x["session"]) for j, x in enumerate(es) if j != i]
        f = features.extract(e["session"])
        for h in gen:
            if len(others) >= h:
                gen[h].append(nearest(f, rng.sample(others, h)))
allg = np.concatenate([np.array(v) for v in gen.values()])
thr1 = float(np.quantile(allg, 0.01))
thr5 = float(np.quantile(allg, 0.05))

# 2) replay vs the whole history (including the original)
rep = {n: [] for n in NOISES}
for (u, p), es in grp.items():
    hist = [features.extract(x["session"]) for x in es]
    src = rng.choice(es)
    for n in NOISES:
        rep[n].append(nearest(features.extract(replay_of(src["session"], n)), hist))

lines = ["# E5b — calibrating the replay check on real humans (StrokePIN)", "",
         f"{len(grp)} (person, PIN) pairs, each with ~5 entries of the same PIN. Current threshold in the backend: **{CUR_THR}** "
         "(chosen on synthetic data in E5). Distance = the backend's `replay.distance`.", "",
         "## Are new real humans mistaken for replays? (nearest distance to their own history)", "",
         "| Old sessions compared | Trials | Median distance | FPR at current threshold | FPR at 0.5x threshold |", "|---|---|---|---|---|"]
for h, v in gen.items():
    a = np.array(v)
    lines.append(f"| {h} | {len(a)} | {np.median(a):.3f} | {(a < CUR_THR).mean():.4f} | {(a < CUR_THR / 2).mean():.4f} |")
q = {x: float(np.quantile(allg, x)) for x in (0.001, 0.005, 0.01, 0.05)}
slope = float((np.array(gen[4]) < CUR_THR).mean() - (np.array(gen[2]) < CUR_THR).mean()) / 2
fpr50 = float((np.array(gen[4]) < CUR_THR).mean()) + slope * (50 - 4)
lines += ["", f"Real-human distance percentiles: 0.1% = {q[0.001]:.3f}; 0.5% = {q[0.005]:.3f}; 1% = {q[0.01]:.3f}; 5% = {q[0.05]:.3f}. "
          f"Median distance of replayed sessions by noise: " + ", ".join(f"±{int(n*1000)/10}% -> {np.median(rep[n]):.3f}" for n in NOISES) + ".", "",
          f"**Linear extrapolation** of FPR by number of old sessions (data only goes up to 4): ~{slope*100:.3f} percentage points per additional old session, so with 50 sessions about **{fpr50:.1%}** "
          "(not measured: this is a guess, the history in the data is only ~4 entries, a very long extrapolation, so for reference only).", "",
          f"Real-human distance: 1st percentile = **{thr1:.3f}**, 5th percentile = {thr5:.3f}, median = {np.median(allg):.3f}.", "",
          "## How many replayed sessions are caught (adaptive attacker: timing noise ±n, coordinates ±max(0.02, 0.4n) key widths)", "",
          "| Noise ±n | " + " | ".join(f"{int(n*1000)/10}%" for n in NOISES) + " |", "|---|" + "---|" * len(NOISES),
          f"| Current threshold ({CUR_THR}) | " + " | ".join(f"{(np.array(rep[n]) < CUR_THR).mean():.2f}" for n in NOISES) + " |",
          f"| FPR 1% threshold ({thr1:.3f}) | " + " | ".join(f"{(np.array(rep[n]) < thr1).mean():.2f}" for n in NOISES) + " |",
          f"| FPR 5% threshold ({thr5:.3f}) | " + " | ".join(f"{(np.array(rep[n]) < thr5).mean():.2f}" for n in NOISES) + " |", ""]
lines += ["## Trade-off by threshold (FPR measured at 2/3/4 old sessions; linear extrapolation to 50; catch rate by noise)", "",
          "| Threshold | FPR @2 | FPR @4 | FPR @50 (extrapolated) | " + " | ".join(f"catch ±{int(n*1000)/10}%" for n in NOISES) + " |",
          "|---|---|---|---|" + "---|" * len(NOISES)]
for th in (0.05, 0.06, 0.07, 0.085, 0.094):
    f2, f4 = float((np.array(gen[2]) < th).mean()), float((np.array(gen[4]) < th).mean())
    lines.append(f"| {th} | {f2:.4f} | {f4:.4f} | {f4 + (f4 - f2) / 2 * 46:.1%} | " + " | ".join(f"{(np.array(rep[n]) < th).mean():.2f}" for n in NOISES) + " |")
lines.append("")
(ROOT / "research/results/e5b_replay_real.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
