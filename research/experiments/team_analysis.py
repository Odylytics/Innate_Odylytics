"""Analysis of the TEAM'S data (T1–T5 in the experiment plan), one command after the export.

  python research/experiments/team_analysis.py export.jsonl [--out report.md] [--boot 300]

export.jsonl = GET /v1/export (a JSON list or one record per line), with `meta` {participant_id, sitting, role, tactic}.
  T1 owner recognition on the same device, over time (enroll with the first 3 sessions of sitting 1; test: the remaining sessions, split into "same sitting" and "later sitting")
  T2 bots: catch rate by tactic (rules + model in the backend) and the rate of wrongly blocking humans
  T3 replay: rate of wrongly blocking the owner by history length
  T4 PIN + challenge sentence combined vs PIN alone (needs sessions with a challenge field)
  T5 stability of Vietnamese typing style across sittings (vi_tone_late, vi_ime_coverage)
Small sample: every number comes with a bootstrap confidence interval OVER PEOPLE and the number of people; do not compare with papers on thousands of people.
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend")]
from app.scoring import human, human_model, owner, replay  # noqa: E402

ARGS = sys.argv[1:]
SRC = next((a for a in ARGS if not a.startswith("--") and a != (ARGS[ARGS.index("--out") + 1] if "--out" in ARGS else None)
            and a != (ARGS[ARGS.index("--boot") + 1] if "--boot" in ARGS else None)), None)
OUT = Path(ARGS[ARGS.index("--out") + 1]) if "--out" in ARGS else ROOT / "research/results/team_analysis.md"
BOOT = int(ARGS[ARGS.index("--boot") + 1]) if "--boot" in ARGS else 300
ENROL = 3
rng = random.Random(0)


def load(path):
    txt = Path(path).read_text(encoding="utf-8").strip()
    recs = json.loads(txt) if txt.startswith("[") else [json.loads(x) for x in txt.splitlines() if x.strip()]
    return [r for r in recs if r.get("meta")]


def metrics(gen, imp):
    """gen, imp: DISTANCE scores (low = similar to the owner). -> (EER, FAR@FRR5%)"""
    gen, imp = np.asarray(gen, float), np.asarray(imp, float)
    ths = np.unique(np.concatenate([gen, imp]))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return (frr[i] + far[i]) / 2, float((imp <= np.quantile(gen, 0.95)).mean())


def boot_ci(per, n=BOOT):
    ps = sorted(per)
    est = metrics(np.concatenate([per[p][0] for p in ps]), np.concatenate([per[p][1] for p in ps]))
    bs = []
    for _ in range(n):
        r = [rng.choice(ps) for _ in ps]
        bs.append(metrics(np.concatenate([per[p][0] for p in r]), np.concatenate([per[p][1] for p in r])))
    lo, hi = np.quantile(bs, 0.025, axis=0), np.quantile(bs, 0.975, axis=0)
    return est, lo, hi


recs = load(SRC) if SRC else sys.exit(__doc__)
recs.sort(key=lambda r: r["created_at"])
gen_by = defaultdict(list)   # owner -> their own real-human sessions (in time order)
imp_by = defaultdict(list)   # owner -> sessions of the assigned impostor targeting their wallet
bots = []
for r in recs:
    m = r["meta"]
    if m["role"] == "genuine":
        gen_by[m["participant_id"]].append(r)
    elif m["role"] == "impostor":
        imp_by[r["user_id"]].append(r)
    elif m["role"] == "bot":
        bots.append(r)
L = ["# Team data analysis", "",
     f"{len(recs)} sessions with `meta`: {sum(len(v) for v in gen_by.values())} owner sessions ({len(gen_by)} people), "
     f"{sum(len(v) for v in imp_by.values())} assigned impostor sessions, {len(bots)} bot sessions. 95% confidence intervals by bootstrap over people ({BOOT} resamples).", ""]


def split_owner(rs):
    s1 = [r for r in rs if r["meta"]["sitting"] == 1]
    return s1[:ENROL], s1[ENROL:], [r for r in rs if r["meta"]["sitting"] >= 2]


def keyset(f, pref):
    return {k: v for k, v in f.items() if k.startswith(pref)}


# ---- T1 ----
def t1(feature_filter=lambda f: f, label="PIN", identity=None):
    out = {"same sitting": {}, "later sitting": {}}
    for p, rs in gen_by.items():
        enr, same, later = split_owner(rs)
        if len(enr) < ENROL:
            continue
        tpl = owner.build_template([feature_filter(r["features"]) for r in enr])
        d = lambda r: -owner.score(feature_filter(r["features"]), tpl)[0]  # noqa: E731  high owner score = similar to the owner
        others = [r for q, v in gen_by.items() if q != p for r in v]
        for name, tests in (("same sitting", same), ("later sitting", later)):
            if len(tests) < 3:
                continue
            out[name][p] = ([d(r) for r in tests], [d(r) for r in imp_by.get(p, [])] or None, [d(r) for r in rng.sample(others, min(30, len(others)))] or None)
    return out


L += ["## T1 — Owner recognition on the same device, enrolled with the first 3 sessions of sitting 1", ""]
t1res = t1()
for name, per in t1res.items():
    L.append(f"### Test: {name}")
    for kind, idx in (("assigned impostor (same wallet, knows the PIN)", 1), ("another person entering the same PIN (DIFFERENT DEVICE, confounded with device noise)", 2)):
        sel = {p: (v[0], v[idx]) for p, v in per.items() if v[idx]}
        if len(sel) < 3:
            L.append(f"- {kind}: not enough data ({len(sel)} people)"); continue
        (e, f), lo, hi = boot_ci(sel)
        L.append(f"- {kind}, {len(sel)} people: EER {e:.3f} [{lo[0]:.3f}, {hi[0]:.3f}]; FAR@FRR5% {f:.3f} [{lo[1]:.3f}, {hi[1]:.3f}]")
    L.append("")

# ---- T2 ----
L += ["## T2 — Bots (rules + model in the backend; human/bot score threshold 0.5)", ""]
def h_score(r):
    h = human.score(r["features"])[0]
    p = human_model.predict(r["raw"])
    return h if p is None else min(h, p)
humans = [r for v in gen_by.values() for r in v]
if humans and bots:
    fp = np.mean([h_score(r) < 0.5 for r in humans])
    L.append(f"Wrongly blocked real people: {fp:.3f} ({len(humans)} sessions)")
    by_t = defaultdict(list)
    for r in bots:
        by_t[r["meta"].get("tactic")].append(h_score(r) < 0.5)
    for t, v in sorted(by_t.items(), key=lambda kv: str(kv[0])):
        L.append(f"- tactic {t}: caught {np.mean(v):.3f} ({len(v)} bot sessions)")
else:
    L.append("Not enough data (need human sessions and bot sessions).")
L.append("")

# ---- T3 ----
L += ["## T3 — Replay: wrongly blocking the owner by history length (backend threshold)", ""]
bins = {"1-3 old sessions": [], "4-8": [], "9+": []}
for rs in gen_by.values():
    fs = [r["features"] for r in rs]
    for i in range(1, len(fs)):
        flag = replay.is_replay(fs[i], fs[max(0, i - 50):i])
        bins["1-3 old sessions" if i <= 3 else "4-8" if i <= 8 else "9+"].append(flag)
for k, v in bins.items():
    L.append(f"- {k}: {np.mean(v):.4f} ({len(v)} sessions)" if v else f"- {k}: no data")
L.append("")

# ---- T4 ----
L += ["## T4 — PIN + challenge sentence combined vs PIN alone", ""]
has_ch = {p: [r for r in rs if "fld_challenge_gap_mean" in r["features"]] for p, rs in gen_by.items()}
if sum(len(v) >= 8 for v in has_ch.values()) >= 3:
    saved = owner.is_identity_feature
    owner.is_identity_feature = lambda k: k.startswith(("pin_", "fld_challenge_gap", "vi_tone_late", "vi_delete_rate"))
    try:
        g_old = {p: [r for r in rs] for p, rs in has_ch.items()}
        gen_by_backup = dict(gen_by)
        gen_by.clear(); gen_by.update({p: v for p, v in g_old.items() if len(v) >= 8})
        for label, flt in (("PIN alone", lambda f: keyset(f, "pin_")),
                           ("PIN + sentence", lambda f: {k: v for k, v in f.items() if k.startswith(("pin_", "fld_challenge_gap", "vi_tone_late", "vi_delete_rate"))})):
            per = {p: (v[0], v[2]) for p, v in t1(flt).get("later sitting", {}).items() if v[2]}
            if len(per) >= 3:
                (e, f), lo, hi = boot_ci(per)
                L.append(f"- {label}, {len(per)} people (impostor = another person): EER {e:.3f} [{lo[0]:.3f}, {hi[0]:.3f}]; FAR@FRR5% {f:.3f} [{lo[1]:.3f}, {hi[1]:.3f}]")
            else:
                L.append(f"- {label}: not enough data")
        gen_by.clear(); gen_by.update(gen_by_backup)
    finally:
        owner.is_identity_feature = saved
else:
    L.append("Not enough sessions with a `challenge` field (need ≥ 3 people, each with ≥ 8 sessions that have the sentence). The collection page `#/collect` does not have the sentence-typing step yet.")
L.append("")

# ---- T5 ----
L += ["## T5 — Stability of Vietnamese typing style across sittings", ""]
tl = {p: {s: np.mean([r["features"]["vi_tone_late"] for r in rs if r["meta"]["sitting"] == s and "vi_tone_late" in r["features"]] or [np.nan])
          for s in (1, 2)} for p, rs in gen_by.items()}
pairs = [(v[1], v[2]) for v in tl.values() if not (np.isnan(v[1]) or np.isnan(v[2]))]
if len(pairs) >= 6:
    a, b = np.array(pairs).T
    L.append(f"- `vi_tone_late` sittings 1 and 2: correlation {np.corrcoef(a, b)[0, 1]:+.2f} over {len(pairs)} people (high and positive = stable; needs ≥ 0.5 to be worth using)")
else:
    L.append(f"- Not enough `vi_tone_late` data in both of the 2 sittings ({len(pairs)} people; need ≥ 6).")
cov = [r["features"]["vi_ime_coverage"] for rs in gen_by.values() for r in rs if "vi_ime_coverage" in r["features"]]
if cov:
    L.append(f"- `vi_ime_coverage` of real people: mean {np.mean(cov):.2f}, {np.mean(np.array(cov) == 0):.1%} of sessions equal 0 (would be flagged `challenge_no_ime`) over {len(cov)} sessions")
L.append("")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
