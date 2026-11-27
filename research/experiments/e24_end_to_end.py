"""E24 + E25 + E27: decision matrix for the WHOLE SYSTEM, threshold sweep, and adaptive bots.

Runs exactly the backend `/score` chain (human.score + human_model, replay, owner.score + owner_model, fusion.fuse) in process, without HTTP/DB.
Data: StrokePIN (real people, 6-digit PINs). Uses ONLY people who are NOT in the training set of the human/machine model (train_human_model.py: seed 7,
us[62:]) AND of the owner model (train_owner_model.py: seed 21, us[68:]), so we do not measure on trained data.
The "PIN-knowing" impostor = another person entering the same PIN on THEIR OWN DEVICE (confounded with device noise; treat the results gently); bots come from the team's generator; adaptive bots come from this script.
Run: python research/experiments/e24_end_to_end.py   (needs numpy, pandas, lightgbm; fastapi not needed)
"""
import copy
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker"), str(Path(__file__).parent)]
from app.scoring import features, fusion, human, human_model, owner, owner_model, replay  # noqa: E402
from nhip_attacker import tactics  # noqa: E402
import strokepin_loader  # noqa: E402

SEED = 0
rng = random.Random(SEED)
S = strokepin_loader.load()
USERS = sorted({e["user"] for e in S})
a = USERS[:]; random.Random(7).shuffle(a); not_in_human_train = set(a[62:])
b = USERS[:]; random.Random(21).shuffle(b); not_in_owner_train = set(b[68:])
EVAL = sorted(not_in_human_train & not_in_owner_train)
print(f"people never seen by both learned models: {len(EVAL)}/{len(USERS)}; human/machine model: {human_model.loaded()}, owner model: {owner_model.loaded()}")
for e in S:
    e["f"] = features.extract(e["session"])
by = defaultdict(list)  # (user, pin) -> entries
for e in S:
    by[(e["user"], e["pin"])].append(e)
by_pin = defaultdict(list)
for e in S:
    by_pin[e["pin"]].append(e)


def decide(raw, f, tpl, history, new_recipient, use_models=True):
    """Copy of `score_session`. -> (risk, action, human, owner)."""
    h, br = human.score(f)
    p = human_model.predict(raw) if use_models else None
    if p is not None:
        h = p if br == ["insufficient_data"] else min(h, p)
    if replay.is_replay(f, history[-50:]):
        h = min(h, 0.1)
    o, z = owner.score(f, tpl) if tpl else (None, {})
    if o and use_models:
        m = owner_model.predict(z)
        o = o if m is None else m
    risk, action, _ = fusion.fuse(h, o, new_recipient, 0.0)
    return risk, action, h, o


def strip(s):
    return {**s, "swipes": [], "screens": []}


def noisy_replay(src, n):
    """Replays the victim's session, with timing noise ±n and coordinate noise ±max(0.02, 0.4n) of the key width (as in E5b)."""
    s = copy.deepcopy(src); taps = sorted(s["pin_taps"], key=lambda t: t["t_down"]); t = 0.0
    for i, tap in enumerate(taps):
        hold = (tap["t_up"] - tap["t_down"]) * rng.uniform(1 - n, 1 + n)
        gap = (taps[i + 1]["t_down"] - tap["t_up"]) * rng.uniform(1 - n, 1 + n) if i < len(taps) - 1 else 0
        r = max(0.02, 0.4 * n)
        tap["x"] += rng.uniform(-r, r) * tap["key_w"]; tap["y"] += rng.uniform(-r, r) * tap["key_h"]
        tap["t_down"], tap["t_up"] = t, t + hold
        t += hold + max(gap, 0)
    s["pin_taps"] = taps
    return s


def mimic(victim_sessions, scale):
    """Impostor who knows the victim's TEMPLATE: samples each value from a Gaussian with the victim's (mean, std) at each key position."""
    ts = [sorted(s["pin_taps"], key=lambda t: t["t_down"]) for s in victim_sessions]
    k = len(ts[0]); out = copy.deepcopy(victim_sessions[0]); taps = out["pin_taps"] = sorted(out["pin_taps"], key=lambda t: t["t_down"])
    t = 0.0
    for i in range(k):
        col = lambda f: np.array([f(x[i], x, i) for x in ts])  # noqa: E731
        hold = col(lambda tp, x, j: tp["t_up"] - tp["t_down"])
        dx = col(lambda tp, x, j: (tp["x"] - tp["key_cx"]) / tp["key_w"]); dy = col(lambda tp, x, j: (tp["y"] - tp["key_cy"]) / tp["key_h"])
        g = lambda v: rng.gauss(v.mean(), max(v.std() * scale, 1e-3))  # noqa: E731
        h_ = max(g(hold), 20.0)
        taps[i]["x"] = taps[i]["key_cx"] + g(dx) * taps[i]["key_w"]; taps[i]["y"] = taps[i]["key_cy"] + g(dy) * taps[i]["key_h"]
        taps[i]["t_down"], taps[i]["t_up"] = t, t + h_
        fl = np.array([x[i + 1]["t_down"] - x[i]["t_up"] for x in ts]) if i < k - 1 else None
        t += h_ + (max(g(fl), 20.0) if fl is not None else 0)
    return out


GROUPS = ["owner", "PIN-knowing impostor (other person, other device)", "T1 uniform bot", "T2 timing-noise bot",
          "T3 replay ±5% bot", "T4 population-sampling bot", "replay ±10%", "replay ±15%", "replay ±20%", "replay ±30%",
          "template-aware bot (scale 1.0)", "template-aware bot (scale 0.5)"]
rows = {g: [] for g in GROUPS}  # g -> [(risk_known, risk_new, human, owner, action_known, action_new, models_off: (..))]


def record(g, raw, tpl, hist):
    f = features.extract(raw)
    r = []
    for use_models in (True, False):
        rk, ak, h, o = decide(raw, f, tpl, hist, False, use_models)
        rn, an, _, _ = decide(raw, f, tpl, hist, True, use_models)
        r.append((rk, rn, h, o, ak, an))
    r.append(replay.nearest(f, hist[-50:]))  # distance to the nearest earlier session, for the replay-threshold sweep
    rows[g].append(tuple(r))


for (u, pin), ents in by.items():
    if u not in EVAL or len(ents) < 5:
        continue
    es = ents[:]; rng.shuffle(es)
    enr, tests = es[:3], es[3:]
    tpl = owner.build_template([e["f"] for e in enr])
    hist = [e["f"] for e in enr]
    for e in tests:
        record(GROUPS[0], e["session"], tpl, hist); hist = hist + [e["f"]]
    others = [e for e in by_pin[pin] if e["user"] != u]
    for e in rng.sample(others, min(4, len(others))):
        record(GROUPS[1], {**e["session"], "user_id": u}, tpl, hist)
    victim = [e["session"] for e in es]
    pop = [e["session"] for e in rng.sample(by_pin[pin], min(150, len(by_pin[pin])))]
    for _ in range(2):
        for gi, t in ((2, 1), (3, 2), (4, 3), (5, 4)):
            raw = strip(tactics.generate(t, u, pin, victim if t == 3 else pop if t == 4 else victim, rng))
            record(GROUPS[gi], raw, tpl, hist)
        src = rng.choice(victim)
        for gi, n in ((6, 0.10), (7, 0.15), (8, 0.20), (9, 0.30)):
            record(GROUPS[gi], strip(noisy_replay(src, n)), tpl, hist)
        for gi, sc in ((10, 1.0), (11, 0.5)):
            record(GROUPS[gi], strip(mimic(victim[:6], sc)), tpl, hist)


def pct(v):
    return f"{100 * np.mean(v):.0f}%"


L = ["# E24 / E25 / E27 — whole-system decisions on StrokePIN (real people) + bots", "",
     f"{len(EVAL)} people never seen by either learned model; enrollment 3 sessions per (person, PIN); replay history = the previous sessions. Current thresholds A={fusion.THRESHOLD_A}, B={fusion.THRESHOLD_B}. "
     "The PIN-knowing impostor uses a DIFFERENT DEVICE (confounded with device noise). Bots are the team's generator/scripts, not real bots.", ""]
for ctx, ia in (("known recipient, normal amount", 4), ("NEW recipient", 5)):
    L += [f"## E24 — {ctx}", "", "| Group | n | allow | step_up | hold | (no learned model) allow |", "|---|---|---|---|---|---|"]
    for g in GROUPS:
        rs = rows[g]
        if not rs:
            continue
        a_on = [r[0][ia] for r in rs]; a_off = [r[1][ia] for r in rs]
        L.append(f"| {g} | {len(rs)} | {pct([x == 'allow' for x in a_on])} | {pct([x == 'step_up' for x in a_on])} | {pct([x == 'hold' for x in a_on])} | {pct([x == 'allow' for x in a_off])} |")
    L.append("")

# E25: threshold sweep
def act(risk, h, A, B):
    return "hold" if h < fusion.HUMAN_HOLD or risk > B else "step_up" if risk >= A else "allow"


L += ["## E25 — sweep of threshold A (allow < A) and B (hold > B), known recipient, with learned models", "",
      "Goal: the owner almost always gets `allow` (hold ≤ 1%), and PIN-knowing impostors and bots are blocked (not `allow`) as often as possible.", "",
      "| A | B | owner: allow / hold | owner, NEW recipient: allow | PIN-knowing impostor: not allow | T4: not allow | template-aware 1.0: not allow | replay ±15%: not allow |", "|---|---|---|---|---|---|---|---|"]
def line(A, B):
    d = lambda g: [act(r[0][0], r[0][2], A, B) for r in rows[g]]  # noqa: E731
    na = lambda g: np.mean([x != "allow" for x in d(g)])  # noqa: E731
    s = d(GROUPS[0])
    new = [act(r[0][1], r[0][2], A, B) for r in rows[GROUPS[0]]]
    return (f"| {A:.2f} | {B:.2f} | {pct([x == 'allow' for x in s])} / {pct([x == 'hold' for x in s])} | {pct([x == 'allow' for x in new])} | "
            f"{100 * na(GROUPS[1]):.0f}% | {100 * na(GROUPS[5]):.0f}% | {100 * na(GROUPS[10]):.0f}% | {100 * na(GROUPS[7]):.0f}% |")
for A, B in [(fusion.THRESHOLD_A, fusion.THRESHOLD_B), (0.10, 0.55), (0.15, 0.55), (0.20, 0.55), (0.30, 0.55), (0.35, 0.55), (0.40, 0.60), (0.45, 0.65), (0.25, 0.40), (0.25, 0.70)]:
    L.append(line(A, B) + (" ← current" if (A, B) == (fusion.THRESHOLD_A, fusion.THRESHOLD_B) else ""))
L.append("")
L += ["## E27b — sweep of the replay threshold (the backend currently uses 0.07), with learned models, known recipient", "",
      "A session judged to be a replay gets `hold`. Trade-off: a higher threshold catches more noisy replay bots but wrongly blocks the owner.", "",
      "| Threshold | owner: hold | replay ±10% | ±15% | ±20% | ±30% | template-aware bot (1.0): hold |", "|---|---|---|---|---|---|---|"]
for thr in (0.05, 0.07, 0.085, 0.10, 0.12, 0.15):
    h = lambda g: pct([(r[2] < thr) or r[0][4] == "hold" for r in rows[g]])  # noqa: E731
    L.append(f"| {thr:.3f} | {h(GROUPS[0])} | {h(GROUPS[6])} | {h(GROUPS[7])} | {h(GROUPS[8])} | {h(GROUPS[9])} | {h(GROUPS[10])} |")
L.append("")
out = ROOT / "research/results/e24_end_to_end.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
