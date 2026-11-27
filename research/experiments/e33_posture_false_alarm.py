"""E33: false alarms (owner asked for extra verification / held) by sitting/walking posture, and whether mixed-posture enrollment reduces them.

Runs the exact `/score` chain of the backend (same as E24): human.score + human_model, replay, owner.score + owner_model, fusion.fuse.
StrokePIN data: each (person, PIN) has 5 sitting + 5 walking sessions, a shared 6-digit PIN. The test set is FIXED for every enrollment scheme:
the owner's last 2 sitting + last 2 walking sessions; PIN-knowing impostor = 3 sitting + 3 walking sessions of another person with the same PIN (their device).
Enrollment uses only the first 3 sitting and first 3 walking sessions, so no test session is in the template.

Two tables:
 - "full": all learned models, only on people never seen by either model (as in E24) -> few people, wide CI.
 - "rules": learned models off (human/bot rules + owner distance), on everyone -> more people, no data leakage.
95% CI by bootstrap over people. Known recipient, normal amount (and one column for a new recipient).
Run: cd backend; uv run --with pandas python ../research/experiments/e33_posture_false_alarm.py
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
a = USERS[:]; random.Random(7).shuffle(a); not_h = set(a[62:])
b = USERS[:]; random.Random(21).shuffle(b); not_o = set(b[68:])
EVAL = sorted(not_h & not_o)
for e in S:
    e["f"] = features.extract(e["session"])
by = defaultdict(lambda: defaultdict(list))
for e in S:
    by[(e["user"], e["pin"])][e["posture"]].append(e)
by_pin = defaultdict(list)
for e in S:
    by_pin[e["pin"]].append(e)

CONFIGS = {  # name -> (number of sitting sessions, number of walking sessions) used for enrollment
    "sitting 3 (current ~ app)": (3, 0),
    "walking 3": (0, 3),
    "sitting 2 + walking 1 (k=3)": (2, 1),
    "sitting 2 + walking 2 (k=4)": (2, 2),
    "sitting 3 + walking 1 (k=4)": (3, 1),
    "sitting 3 + walking 3 (k=6)": (3, 3),
}


def decide(raw, f, tpl, hist, new_recipient, use_models):
    h, br = human.score(f)
    p = human_model.predict(raw) if use_models else None
    if p is not None:
        h = p if br == ["insufficient_data"] else min(h, p)
    if replay.is_replay(f, hist[-50:]):
        h = min(h, 0.1)
    o, z = owner.score(f, tpl) if tpl else (None, {})
    if o and use_models:
        m = owner_model.predict(z)
        o = o if m is None else m
    _, action, _ = fusion.fuse(h, o, new_recipient, 0.0)
    return action, h < fusion.HUMAN_HOLD


def run(users, use_models):
    # res[config][group] -> list of (user, action_known, action_new, bot_hold)
    res = defaultdict(lambda: defaultdict(list))
    for (u, pin), post in by.items():
        if u not in users or len(post["sit"]) < 5 or len(post["walk"]) < 5:
            continue
        sit, walk = post["sit"][:], post["walk"][:]
        rng.shuffle(sit); rng.shuffle(walk)
        tests = {"owner sitting": sit[3:5], "owner walking": walk[3:5]}
        others = [e for e in by_pin[pin] if e["user"] != u]
        osit = [e for e in others if e["posture"] == "sit"]; owalk = [e for e in others if e["posture"] == "walk"]
        tests["PIN-knowing impostor (sitting)"] = rng.sample(osit, min(3, len(osit)))
        tests["PIN-knowing impostor (walking)"] = rng.sample(owalk, min(3, len(owalk)))
        for name, (ns, nw) in CONFIGS.items():
            enr = sit[:ns] + walk[:nw]
            tpl = owner.build_template([e["f"] for e in enr])
            hist = [e["f"] for e in enr]
            for g, es in tests.items():
                for e in es:
                    raw = e["session"] if g.startswith("owner") else {**e["session"], "user_id": u}
                    ak, bh = decide(raw, e["f"], tpl, hist, False, use_models)
                    an, _ = decide(raw, e["f"], tpl, hist, True, use_models)
                    res[name][g].append((u, ak, an, bh))
    return res


def boot(rows, stat, n=1000):
    us = sorted({r[0] for r in rows})
    byu = defaultdict(list)
    for r in rows:
        byu[r[0]].append(r)
    point = stat(rows)
    if len(us) < 2:
        return point, point, point
    rs = np.random.default_rng(1)
    vals = []
    for _ in range(n):
        pick = rs.choice(len(us), len(us))
        vals.append(stat([r for i in pick for r in byu[us[i]]]))
    return point, np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def fmt(t):
    p, lo, hi = t
    return f"{100 * p:.0f}% [{100 * lo:.0f}, {100 * hi:.0f}]"


not_allow = lambda rows: np.mean([r[1] != "allow" for r in rows])  # noqa: E731
hold = lambda rows: np.mean([r[1] == "hold" for r in rows])  # noqa: E731
bot_hold = lambda rows: np.mean([r[3] for r in rows])  # noqa: E731
allow = lambda rows: np.mean([r[1] == "allow" for r in rows])  # noqa: E731
not_allow_new = lambda rows: np.mean([r[2] != "allow" for r in rows])  # noqa: E731
allow_new = lambda rows: np.mean([r[2] == "allow" for r in rows])  # noqa: E731

L = ["# E33 — false alarms by posture (sitting/walking) and mixed-posture enrollment (StrokePIN)", "",
     "False alarm = the real owner is NOT `allow`ed (gets `step_up` or `hold`). Leak = the PIN-knowing impostor is `allow`ed. "
     "Fixed test set for every enrollment scheme (owner: 2 sitting + 2 walking; PIN-knowing impostor: 3 sitting + 3 walking, other device). "
     f"Thresholds A={fusion.THRESHOLD_A}, B={fusion.THRESHOLD_B}. 95% CI by bootstrap over people.", ""]
for label, users, models in (("full: all learned models, people never seen", set(EVAL), True), ("rules: learned models off, everyone", set(USERS), False)):
    res = run(users, models)
    nu = len({r[0] for r in next(iter(res.values()))["owner sitting"]})
    L += [f"## {label} ({nu} people)", "",
          "### Known recipient", "",
          "| Enrollment | Sitting owner: false alarm | Sitting owner: held | Walking owner: false alarm | Walking owner: held | of which held as 'bot-like' (walking) | Sitting PIN-knowing impostor: leak | Walking PIN-knowing impostor: leak |",
          "|---|---|---|---|---|---|---|---|"]
    for name in CONFIGS:
        g = res[name]
        L.append(f"| {name} | {fmt(boot(g['owner sitting'], not_allow))} | {fmt(boot(g['owner sitting'], hold))} | {fmt(boot(g['owner walking'], not_allow))} | "
                 f"{fmt(boot(g['owner walking'], hold))} | {fmt(boot(g['owner walking'], bot_hold))} | {fmt(boot(g['PIN-knowing impostor (sitting)'], allow))} | {fmt(boot(g['PIN-knowing impostor (walking)'], allow))} |")
    L += ["", "### NEW recipient", "", "| Enrollment | Sitting owner: false alarm | Walking owner: false alarm | PIN-knowing impostor (sitting+walking): leak |", "|---|---|---|---|"]
    for name in CONFIGS:
        g = res[name]
        L.append(f"| {name} | {fmt(boot(g['owner sitting'], not_allow_new))} | {fmt(boot(g['owner walking'], not_allow_new))} | "
                 f"{fmt(boot(g['PIN-knowing impostor (sitting)'] + g['PIN-knowing impostor (walking)'], allow_new))} |")
    L.append("")
out = ROOT / "research/results/e33_posture_false_alarm.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
