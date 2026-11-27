"""Non-PIN input fields (amount, recipient, note) for bots, per tactic. Matches the backend `SessionIn.fields`.

Only timing (integer ms), event kind, character count, character class: NO content.

1. Accessibility malware sets the text directly (`ACTION_SET_TEXT`): one `set_text` event, no keys.
2. Automated typing (like `adb input text` with a delay): evenly random gaps between keys, no delete, no paste.
3. Replay: copy the event sequence of a real human session, ±5% noise on the gaps.
4. Sampling from the real human population: gaps drawn independently from the pool, delete/paste rates matching the pool.

`humans` is the list of sessions that have `fields` (real people). If there are none, tactics 3 and 4 return empty (nothing to copy).
"""

import copy
import random

FIELD_PLAN = (("amount", "digit", (4, 8)), ("recipient", "digit", (10, 10)), ("note", "letter", (12, 40)))


def _start(rng: random.Random) -> float:
    return rng.uniform(300, 1500)


def set_text(rng: random.Random) -> list[dict]:
    t, out = _start(rng), []
    for name, _cls, (lo, hi) in FIELD_PLAN:
        out.append({"name": name, "events": [{"t": round(t), "kind": "set_text", "n": rng.randint(lo, hi)}]})
        t += rng.uniform(200, 600)
    return out


def even_typing(rng: random.Random) -> list[dict]:
    t, out = _start(rng), []
    for name, cls, (lo, hi) in FIELD_PLAN:
        ev = []
        for _ in range(rng.randint(lo, hi)):
            t += rng.uniform(60, 250)
            ev.append({"t": round(t), "kind": "key", "n": 1, "cls": cls})
        out.append({"name": name, "events": ev})
        t += rng.uniform(200, 600)
    return out


def replay(fields: list[dict], rng: random.Random) -> list[dict]:
    """Copy the event sequence of a real human session, ±5% noise on the gaps between events."""
    out = copy.deepcopy(fields)
    for fld in out:
        t, prev = 0.0, None
        for e in sorted(fld["events"], key=lambda e: e["t"]):
            gap = 0.0 if prev is None else (e["t"] - prev) * rng.uniform(0.95, 1.05)
            prev, t = e["t"], t + gap
            e["t"] = round(t)
    return out


def sampled(humans: list[dict], rng: random.Random, names: tuple[str, ...] | None = None) -> list[dict]:
    """Gaps between events drawn independently from the real-human pool (same field name); delete/paste rates match the pool."""
    out = []
    for name in names or [n for n, _c, _r in FIELD_PLAN]:
        pool = [f for h in humans for f in h.get("fields", []) if f["name"] == name]
        if not pool:
            continue
        gaps, cls_pool, lens, dels, pastes, keys = [], [], [], 0, [], 0
        for f in pool:
            ev = sorted(f["events"], key=lambda e: e["t"])
            gaps += [b["t"] - a["t"] for a, b in zip(ev, ev[1:])]
            lens.append(sum(e["kind"] == "key" for e in ev))
            cls_pool += [e.get("cls") for e in ev if e["kind"] == "key" and e.get("cls")]
            keys += sum(e["kind"] == "key" for e in ev)
            dels += sum(e["n"] for e in ev if e["kind"] == "delete")
            pastes += [e["n"] for e in ev if e["kind"] == "paste"]
        if not gaps or not cls_pool:
            continue
        p_del, p_paste = dels / max(keys, 1), len(pastes) / max(keys, 1)
        t, ev = _start(rng), []
        for _ in range(max(rng.choice(lens), 1)):
            t += rng.choice(gaps)
            ev.append({"t": round(t), "kind": "key", "n": 1, "cls": rng.choice(cls_pool)})
            r = rng.random()
            if r < p_del and ev:
                t += rng.choice(gaps)
                ev.append({"t": round(t), "kind": "delete", "n": 1})
            elif r < p_del + p_paste and pastes:
                t += rng.choice(gaps)
                ev.append({"t": round(t), "kind": "paste", "n": rng.choice(pastes)})
        out.append({"name": name, "events": ev})
    return out


def for_tactic(tactic: int, rng: random.Random, humans: list[dict], source: dict | None = None) -> list[dict]:
    if tactic == 1:
        return set_text(rng)
    if tactic == 2:
        return even_typing(rng)
    if tactic == 3:
        return replay(source["fields"], rng) if source and source.get("fields") else []
    if tactic == 4:
        return sampled(humans, rng)
    raise ValueError(f"No such tactic {tactic}")
