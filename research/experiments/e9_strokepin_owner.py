"""E9: owner verification on REAL phone PINs (StrokePIN), using the backend's own features.py / owner.py.

Each (person, PIN) pair: enroll with k random sessions. Test:
  - owner: the remaining sessions
  - PIN-knowing impostor: another person's entry of the same PIN (scenario B)
Score = normalized distance (low = similar to the owner). Pool the scores of all pairs, then compute EER and FAR@FRR 5%; CI by bootstrap over people.
Three feature sets (timing / + center offset / + touch size) x three detectors:
  backend (current owner.py: sd with floor), Manhattan scaled (Killourhy & Maxion), E2 (variance shrinkage toward the population).
No bots here: this is the "is it the owner" task, real-human data but one device per person (devices differ between people).
"""

import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, owner  # noqa: E402
import strokepin_loader  # noqa: E402

KS, SEED, N_DRAW, N_IMP, BOOT, NU = (3, 5), 0, 5, 20, 100, 5
SETS = {
    "timing": lambda k: k.startswith(("pin_hold_", "pin_flight_")) or k == "pin_total",
    "timing + center offset": lambda k: k.startswith(("pin_hold_", "pin_flight_", "pin_dx_", "pin_dy_")) or k == "pin_total",
    "timing + center offset + touch size": lambda k: (k.startswith(("pin_hold_", "pin_flight_", "pin_dx_", "pin_dy_"))
                                                         or k in ("pin_total", "tap_w_mean", "tap_h_mean")),
}
rng = random.Random(SEED)
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
KEYS = {n: sorted(k for k in S[0]["f"] if sel(k)) for n, sel in SETS.items()}
for e in S:
    e["v"] = {n: np.array([e["f"][k] for k in ks]) for n, ks in KEYS.items()}

grp = defaultdict(list)  # (user, pin) -> entries
for e in S:
    grp[(e["user"], e["pin"])].append(e)
by_pin = defaultdict(lambda: defaultdict(list))  # pin -> user -> entries
for (u, p), es in grp.items():
    by_pin[p][u] += es
users = sorted({e["user"] for e in S})
print(f"{len(S)} entries, {len(users)} people; median entries/PIN/person:", int(np.median([len(v) for v in grp.values()])))


def within_var(pin, exclude, name):
    """Mean within-person variance of OTHER people (leave-user-out), by PIN."""
    vs = [np.var(np.array([e["v"][name] for e in es]), axis=0, ddof=1)
          for u, es in by_pin[pin].items() if u != exclude and len(es) >= 2]
    return np.mean(vs, axis=0)


def detectors(name, X, prior_var):
    keys, mu = KEYS[name], X.mean(0)
    floor = np.array([owner._floor(k, m) for k, m in zip(keys, mu)])
    sd_backend = np.maximum(X.std(0, ddof=1), floor)
    mad = np.abs(X - mu).mean(0) + 1e-9
    var_eb = ((len(X) - 1) * X.var(0, ddof=1) + NU * prior_var) / (len(X) - 1 + NU)
    return {"backend (owner.py: sd with floor)": lambda x: (np.abs(x - mu) / sd_backend).mean(-1),
            "Manhattan scaled": lambda x: (np.abs(x - mu) / mad).mean(-1),
            f"E2 shrinkage toward population (nu={NU})": lambda x: (np.abs(x - mu) / np.sqrt(var_eb)).mean(-1)}


# scores[(k, set, detector)][user] = (gen[], imp[])
scores = defaultdict(lambda: defaultdict(lambda: ([], [])))
for (u, p), es in grp.items():
    for k in KS:
        if len(es) < k:
            continue
        for _ in range(N_DRAW):
            enr = rng.sample(es, k)
            gen_es = [e for e in es if e not in enr]
            if not gen_es:
                continue
            imp_pool = [e for v, ves in by_pin[p].items() if v != u for e in ves]
            imp = rng.sample(imp_pool, min(N_IMP, len(imp_pool)))
            for name in SETS:
                X = np.array([e["v"][name] for e in enr])
                pv = within_var(p, u, name)
                for dn, f in detectors(name, X, pv).items():
                    g, i = scores[(k, name, dn)][u]
                    g += list(f(np.array([e["v"][name] for e in gen_es])))
                    i += list(f(np.array([e["v"][name] for e in imp])))


def metrics(gen, imp):
    gen, imp = np.asarray(gen), np.asarray(imp)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 400)))
    frr = np.array([(gen > t).mean() for t in ths])
    far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return (frr[i] + far[i]) / 2, float((imp <= np.quantile(gen, 0.95)).mean())


def pooled(per_user, us):
    return np.concatenate([per_user[u][0] for u in us]), np.concatenate([per_user[u][1] for u in us])


def ci(per_user):
    us = sorted(per_user)
    est = metrics(*pooled(per_user, us))
    bs = np.array([metrics(*pooled(per_user, rng.choices(us, k=len(us)))) for _ in range(BOOT)])
    lo, hi = np.quantile(bs, 0.025, axis=0), np.quantile(bs, 0.975, axis=0)
    return est, lo, hi


lines = ["# E9 — owner verification on real phone PINs (StrokePIN, 97 people, 6-digit PIN)", "",
         f"Uses the backend's `features.py` + `owner.py`. The impostor **knows the PIN** (another person enters the same PIN). Enrollment on k sessions; "
         f"scores pooled over all (person, PIN) pairs, 95% CI by bootstrap over people ({BOOT} resamples). Lower is better. "
         "Real-human data; each person has one phone, so device differences between people also contribute to the separation.", ""]
for k in KS:
    lines += [f"## k = {k} enrollment sessions", "", "| Feature set | Detector | EER | FAR @ FRR 5% |", "|---|---|---|---|"]
    for (k2, name, dn), per_user in scores.items():
        if k2 != k:
            continue
        (e, f), lo, hi = ci(per_user)
        lines.append(f"| {name} | {dn} | {e:.3f} [{lo[0]:.3f}, {hi[0]:.3f}] | {f:.3f} [{lo[1]:.3f}, {hi[1]:.3f}] |")
    lines.append("")
# PAIRED comparison (same bootstrap sample by person): E2 minus backend, negative = E2 is better
lines += ["## Paired comparison: E2 (shrinkage toward population) minus current backend, negative = E2 is better", "",
          "| k | Feature set | dEER | dFAR @ FRR 5% |", "|---|---|---|---|"]
for k in KS:
    for name in SETS:
        a = scores.get((k, name, "backend (owner.py: sd with floor)"))
        b = scores.get((k, name, f"E2 shrinkage toward population (nu={NU})"))
        if not a or not b:
            continue
        us = sorted(a)
        d = np.array([np.subtract(metrics(*pooled(b, r)), metrics(*pooled(a, r)))
                      for r in (rng.choices(us, k=len(us)) for _ in range(BOOT))])
        m = np.subtract(metrics(*pooled(b, us)), metrics(*pooled(a, us)))
        lo, hi = np.quantile(d, 0.025, axis=0), np.quantile(d, 0.975, axis=0)
        lines.append(f"| {k} | {name} | {m[0]:+.3f} [{lo[0]:+.3f}, {hi[0]:+.3f}] | {m[1]:+.3f} [{lo[1]:+.3f}, {hi[1]:+.3f}] |")
lines.append("")
out = ROOT / "research/results/e9_strokepin_owner.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
