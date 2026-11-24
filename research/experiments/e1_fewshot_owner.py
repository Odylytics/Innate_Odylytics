"""E1/E2 (proxy): few-shot owner verification on CMU DSL-StrongPassword.

Question: with only k = 3/5/10 enrollment samples, does shrinking the per-feature spread toward a
population prior (E2) or shrinking the covariance toward its diagonal (E1) beat scaled Manhattan?

Protocol (time split): enroll with k random reps from session 1; genuine test = sessions 5-8;
impostor test = 5 reps from each other subject's sessions 5-8. Enrollment draw repeated N_DRAWS times.
Population prior comes from OTHER subjects only (leave-subject-out). Not a mobile PIN dataset: a sanity
proxy for the method, not evidence for Innate's numbers.

Usage: python e1_fewshot_owner.py [path/to/DSL-StrongPasswordData.csv] [out.md]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[1] / "data/DSL-StrongPasswordData.csv"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parents[1] / "results/e1_dsl.md"
KS, N_DRAWS, SEED, BOOT = (3, 5, 10), 10, 0, 2000

df = pd.read_csv(CSV)
FEATS = [c for c in df.columns if c[:2] in ("H.", "DD", "UD")]
SUBJ = sorted(df.subject.unique())
sess1 = {s: df[(df.subject == s) & (df.sessionIndex == 1)][FEATS].to_numpy() for s in SUBJ}
late = {s: df[(df.subject == s) & (df.sessionIndex >= 5)][FEATS].to_numpy() for s in SUBJ}


def eer_and_far(gen: np.ndarray, imp: np.ndarray) -> tuple[float, float]:
    """Scores: lower = more genuine. -> (EER, FAR at FRR = 5%)."""
    ths = np.unique(np.concatenate([gen, imp]))
    frr = np.array([(gen > t).mean() for t in ths])
    far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    t95 = np.quantile(gen, 0.95)
    return float((frr[i] + far[i]) / 2), float((imp <= t95).mean())


# ---- detectors: fit(X_enroll, prior) -> score(x) ----
def manhattan_scaled(X, prior):  # Killourhy & Maxion 2009: divide by mean absolute deviation
    mu = X.mean(0)
    mad = np.abs(X - mu).mean(0) + 1e-9
    return lambda x: (np.abs(x - mu) / mad).sum(-1)


def manhattan_floor(X, prior):  # current owner.py idea: sd with a floor of 10% of |mean|
    mu, sd = X.mean(0), np.maximum(X.std(0, ddof=1), 0.1 * np.abs(X.mean(0)))
    return lambda x: (np.abs(x - mu) / sd).sum(-1)


def make_eb(nu):  # E2: shrink per-feature variance toward the population within-person variance
    def f(X, prior):
        k = len(X)
        mu = X.mean(0)
        var = ((k - 1) * X.var(0, ddof=1) + nu * prior["within_var"]) / (k - 1 + nu)
        return lambda x: (np.abs(x - mu) / np.sqrt(var)).sum(-1)
    return f


def make_maha(lam):  # E1: Mahalanobis, covariance shrunk toward its diagonal
    def f(X, prior):
        S = np.cov(X, rowvar=False)
        C = (1 - lam) * S + lam * np.diag(np.diag(S)) + 1e-9 * np.eye(S.shape[0])
        Ci, mu = np.linalg.inv(C), X.mean(0)
        return lambda x: np.sqrt(np.einsum("...i,ij,...j->...", x - mu, Ci, x - mu))
    return f


DETECTORS = {
    "Manhattan scaled (baseline)": manhattan_scaled,
    "Manhattan + sd floor (current owner.py)": manhattan_floor,
    "E2 variance prior nu=2": make_eb(2),
    "E2 variance prior nu=5": make_eb(5),
    "E2 variance prior nu=10": make_eb(10),
    "E1 Mahalanobis shrink lam=0.5": make_maha(0.5),
    "E1 Mahalanobis shrink lam=0.9": make_maha(0.9),
}

rng = np.random.default_rng(SEED)
imp_pool = {s: late[s][rng.choice(len(late[s]), 20, replace=False)] for s in SUBJ}  # fixed per subject
# prior (leave-subject-out): mean within-person variance of each feature over the other subjects
wv = {s: sess1[s].var(0, ddof=1) for s in SUBJ}

res = {k: {d: {"eer": [], "far": []} for d in DETECTORS} for k in KS}
for s in SUBJ:
    prior = {"within_var": np.mean([wv[o] for o in SUBJ if o != s], axis=0)}
    gen = late[s]
    imp = np.concatenate([imp_pool[o][:5] for o in SUBJ if o != s])
    for k in KS:
        acc = {d: [[], []] for d in DETECTORS}
        for _ in range(N_DRAWS):
            X = sess1[s][rng.choice(len(sess1[s]), k, replace=False)]
            for d, fit in DETECTORS.items():
                sc = fit(X, prior)
                e, f = eer_and_far(sc(gen), sc(imp))
                acc[d][0].append(e)
                acc[d][1].append(f)
        for d in DETECTORS:
            res[k][d]["eer"].append(np.mean(acc[d][0]))
            res[k][d]["far"].append(np.mean(acc[d][1]))


def ci(v):  # bootstrap over subjects
    v = np.asarray(v)
    m = [rng.choice(v, len(v)).mean() for _ in range(BOOT)]
    return v.mean(), np.quantile(m, 0.025), np.quantile(m, 0.975)


lines = ["# E1/E2 (proxy) — few-shot owner verification on DSL-StrongPassword", "",
         f"{len(SUBJ)} subjects, {len(FEATS)} timing features, enroll = k random reps of session 1, test = sessions 5-8, "
         f"{N_DRAWS} enrollment draws per subject, 95% CI by bootstrap over subjects. Lower is better.", ""]
for k in KS:
    lines += [f"## k = {k} enrollment samples", "", "| Detector | EER | FAR @ FRR=5% |", "|---|---|---|"]
    for d in DETECTORS:
        e, f = ci(res[k][d]["eer"]), ci(res[k][d]["far"])
        lines.append(f"| {d} | {e[0]:.3f} [{e[1]:.3f}, {e[2]:.3f}] | {f[0]:.3f} [{f[1]:.3f}, {f[2]:.3f}] |")
    lines.append("")
base, cand = "Manhattan scaled (baseline)", "E2 variance prior nu=5"
lines += ["## Paired difference (same subjects): E2 nu=5 minus baseline, negative = E2 better", "",
          "| k | dEER | dFAR @ FRR=5% |", "|---|---|---|"]
for k in KS:
    de = np.array(res[k][cand]["eer"]) - np.array(res[k][base]["eer"])
    df_ = np.array(res[k][cand]["far"]) - np.array(res[k][base]["far"])
    (a, al, ah), (b, bl, bh) = ci(de), ci(df_)
    lines.append(f"| {k} | {a:+.3f} [{al:+.3f}, {ah:+.3f}] | {b:+.3f} [{bl:+.3f}, {bh:+.3f}] |")
lines.append("")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
