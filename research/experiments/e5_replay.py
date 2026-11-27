"""E5: replay detection (tactic 3) — how many are caught, and how many real owners are wrongly rejected?

SYNTHETIC data (personas from attacker/tactics.py): this only checks the METHOD and finds a rough threshold,
it is not a number for slides. It must be repeated on real human sessions.

Each trial: one account with 10 old sessions of the same persona; 1 new real session (measures FPR);
one session replayed from an old session with noise n in both timing and coordinates (measures the catch rate).
Three ways to compute the distance:
  rel   : relative difference on hold/flight times (the version used in replay.py)
  rel+  : rel + center offset dx/dy (converted to a relative scale)
  z     : |a-b| / owner sd (sd from the 5 enrollment sessions, with a floor as in owner.py) over all identity features
"""

import copy
import random
import sys
from pathlib import Path
from statistics import fmean

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker")]
from app.scoring import features, owner  # noqa: E402
from nhip_attacker import tactics  # noqa: E402

N_USERS, N_HIST, N_ENROLL, SEED = 300, 10, 5, 0
NOISES = [0.025, 0.05, 0.10, 0.15, 0.20, 0.30]
FPR_TARGET = 0.01


def replay_of(src: dict, noise: float, rng: random.Random) -> dict:
    """Like tactic3 but parameterized. An adaptive attacker raises noise in BOTH: timing ±noise,
    coordinates ±max(2, 40*noise) px (5% -> 2 px as in tactic3, 20% -> 8 px ~ the deviation between two real human sessions)."""
    s = copy.deepcopy(src)
    jit = max(2.0, 40 * noise)
    taps, t = sorted(s["pin_taps"], key=lambda x: x["t_down"]), 0.0
    for i, tap in enumerate(taps):
        hold = (tap["t_up"] - tap["t_down"]) * rng.uniform(1 - noise, 1 + noise)
        gap = (taps[i + 1]["t_down"] - tap["t_up"]) * rng.uniform(1 - noise, 1 + noise) if i < len(taps) - 1 else 0
        tap["x"] += rng.uniform(-jit, jit)
        tap["y"] += rng.uniform(-jit, jit)
        tap["t_down"], tap["t_up"] = t, t + hold
        t += hold + max(gap, 0)
    s["pin_taps"] = taps
    return s


def timing(f):
    return [k for k in f if k.startswith(("pin_hold_", "pin_flight_"))]


def d_rel(a, b, tpl=None):
    ks = [k for k in timing(a) if k in b]
    return fmean(abs(a[k] - b[k]) / max((abs(a[k]) + abs(b[k])) / 2, 1e-6) for k in ks)


def d_relplus(a, b, tpl=None):
    ks = [k for k in timing(a) if k in b]
    parts = [abs(a[k] - b[k]) / max((abs(a[k]) + abs(b[k])) / 2, 1e-6) for k in ks]
    # center offset (in key-width units): real humans differ by ~0.07; converted to a relative scale by dividing by 0.4
    parts += [abs(a[k] - b[k]) / 0.4 for k in a if k.startswith(("pin_dx_", "pin_dy_")) and k in b]
    return fmean(parts)


def d_z(a, b, tpl):
    ks = [k for k in tpl["sd"] if k in a and k in b]
    return fmean(abs(a[k] - b[k]) / tpl["sd"][k] for k in ks)


DISTS = {"rel (current)": d_rel, "rel+ (adds center offset)": d_relplus, "z (by owner sd)": d_z}


def run(pin_len: int):
    pin = "159357"[:pin_len] if pin_len <= 6 else "1593571593"[:pin_len]
    rng = random.Random(SEED)
    layout = tactics.DEFAULT_LAYOUT
    gen_d = {n: [] for n in DISTS}                      # nearest distance from the new real session to the history
    rep_d = {n: {z: [] for z in NOISES} for n in DISTS}  # of the replayed session
    for u in range(N_USERS):
        sess = tactics.synth_owner(f"u{u}", N_HIST + 1, pin, layout, seed=SEED * 100000 + u)
        feats = [features.extract(s) for s in sess]
        hist, fresh = feats[:N_HIST], feats[N_HIST]
        tpl = owner.build_template(hist[:N_ENROLL])
        for n, d in DISTS.items():
            gen_d[n].append(min(d(fresh, h, tpl) for h in hist))
        src_i = rng.randrange(N_HIST)
        for z in NOISES:
            rep = features.extract(replay_of(sess[src_i], z, rng))
            for n, d in DISTS.items():
                rep_d[n][z].append(min(d(rep, h, tpl) for h in hist))
    out = []
    for n in DISTS:
        g = np.array(gen_d[n])
        thr = float(np.quantile(g, FPR_TARGET))  # threshold so that only ~1% of new real sessions are treated as replays
        row = {z: float((np.array(rep_d[n][z]) < thr).mean()) for z in NOISES}
        out.append((n, thr, float((g < thr).mean()), row, float(np.median(g))))
    return out


lines = ["# E5 — replay detection (synthetic data)", "",
         f"{N_USERS} synthetic accounts, {N_HIST} old sessions per account. The threshold is chosen so that **only ~{FPR_TARGET:.0%} of new real-human sessions are treated as replays**; "
         "the table reports the catch rate of replayed sessions by the attacker's noise level (time ±n, coordinates ±max(2, 40n) px). Synthetic personas, this only checks the method.", ""]
for pin_len in (4, 6):
    lines += [f"## {pin_len}-digit PIN", "", "| Distance | Threshold | FPR | Median distance of real humans | " + " | ".join(f"noise ±{int(z*1000)/10}%" for z in NOISES) + " |",
              "|---|---|---|---|" + "---|" * len(NOISES)]
    for n, thr, fpr, row, med in run(pin_len):
        lines.append(f"| {n} | {thr:.3f} | {fpr:.3f} | {med:.3f} | " + " | ".join(f"{row[z]:.2f}" for z in NOISES) + " |")
    lines.append("")
# backend FPR (rel+, default threshold) by number of old sessions compared
THR = 0.085
lines += [f"## FPR of the version used in the backend (rel+, threshold {THR}) by number of old sessions compared", "",
          "| PIN | 10 old sessions | 50 old sessions | 200 old sessions |", "|---|---|---|---|"]
for pin_len in (4, 6):
    pin, rows = "159357"[:pin_len], {10: [], 50: [], 200: []}
    for u in range(120):
        f = [features.extract(x) for x in tactics.synth_owner(f"v{u}", 201, pin, tactics.DEFAULT_LAYOUT, seed=5000 + u)]
        for h in rows:
            rows[h].append(min(d_relplus(f[200], x) for x in f[:h]))
    lines.append(f"| {pin_len} digits | " + " | ".join(f"{float((np.array(v) < THR).mean()):.3f}" for v in rows.values()) + " |")
lines.append("")
out = ROOT / "research/results/e5_replay.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
