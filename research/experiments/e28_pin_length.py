"""E28: 4-digit PIN (as in the web demo, PIN 1593) or 6-digit (training data)? `allow/step_up/hold` decisions for the owner and the PIN-knowing impostor.

The learned owner-recognition model is trained on 6-digit PINs and only runs with all 6 keys (`owner_model.predict` returns None if features are missing), so with a 4-digit PIN the backend falls back to the distance score of `owner.py`.
A 4-digit PIN is simulated by CUTTING the first 4 taps of a StrokePIN session (a real 6-digit PIN): only an approximation (people typing a real 4-digit PIN may differ), but it shows the direction.
The same 10 people never seen by either learned model, and the same E24 protocol (known recipient). The PIN-knowing impostor uses a DIFFERENT DEVICE (confounded with device noise).
Run: python research/experiments/e28_pin_length.py
"""
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, fusion, human, human_model, owner, owner_model, replay  # noqa: E402
import strokepin_loader  # noqa: E402

rng = random.Random(0)
S = strokepin_loader.load()
USERS = sorted({e["user"] for e in S})
a = USERS[:]; random.Random(7).shuffle(a); b = USERS[:]; random.Random(21).shuffle(b)
EVAL = sorted(set(a[62:]) & set(b[68:]))


def trunc(sess, k):
    return {**sess, "pin_taps": sess["pin_taps"][:k]}


def decide(raw, tpl, hist):
    f = features.extract(raw)
    h, br = human.score(f)
    p = human_model.predict(raw)
    if p is not None:
        h = p if br == ["insufficient_data"] else min(h, p)
    if replay.is_replay(f, hist[-50:]):
        h = min(h, 0.1)
    o, z = owner.score(f, tpl)
    used_model = False
    if o:
        m = owner_model.predict(z)
        used_model = m is not None
        o = o if m is None else m
    return fusion.fuse(h, o, False, 0.0)[1], used_model


out = ["# E28 — 4-digit PIN (demo) and 6-digit PIN: system decisions", "",
       "10 people never seen by either learned model; the 4-digit PIN is simulated by cutting the first 4 taps of a real 6-digit PIN (approximation). Known recipient. The PIN-knowing impostor uses a different device.", "",
       "| PIN | learned owner model runs? | sitting owner: allow / step_up / hold | PIN-knowing impostor: allow / step_up / hold |", "|---|---|---|---|"]
for k in (6, 4):
    res = {"owner": [], "imp": []}; used = []
    by = defaultdict(lambda: defaultdict(list)); by_pin = defaultdict(list)
    for e in S:
        by[(e["user"], e["pin"])][e["posture"]].append(e); by_pin[e["pin"]].append(e)
    for (u, pin), post in by.items():
        if u not in EVAL or len(post["sit"]) < 5:
            continue
        es = post["sit"][:]; rng.shuffle(es)
        enr, tests = es[:3], es[3:]
        feats_ = [features.extract(trunc(e["session"], k)) for e in enr]
        tpl = owner.build_template(feats_)
        hist = list(feats_)
        for e in tests:
            act, um = decide(trunc(e["session"], k), tpl, hist); res["owner"].append(act); used.append(um)
            hist.append(features.extract(trunc(e["session"], k)))
        others = [e for e in by_pin[pin] if e["user"] != u and e["posture"] == "sit"]
        for e in rng.sample(others, min(4, len(others))):
            res["imp"].append(decide(trunc({**e["session"], "user_id": u}, k), tpl, hist)[0])
    pc = lambda L, x: f"{100 * np.mean([a == x for a in L]):.0f}%"  # noqa: E731
    row = lambda L: " / ".join(pc(L, x) for x in ("allow", "step_up", "hold"))  # noqa: E731
    out.append(f"| {k} digits | {'yes' if np.mean(used) > 0.5 else 'NO (falls back to distance)'} | {row(res['owner'])} | {row(res['imp'])} |")
    print(out[-1], flush=True)
(ROOT / "research/results/e28_pin_length.md").write_text("\n".join(out) + "\n", encoding="utf-8")
