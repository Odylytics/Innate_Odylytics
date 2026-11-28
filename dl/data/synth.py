"""SYNTHETIC multi-sitting sessions for the dry run and the tests (NO scientific value): personas from the attacker simulator
whose rhythm drifts slowly with time, entered at spread-out timestamps, plus bots of tactics 1-4. Never use these numbers as results."""

import random

from nhip_attacker import tactics

from .history_features import build
from .ingest import Record

DAY = 86400.0
T0 = 1_790_000_000.0  # fixed epoch so runs are reproducible
SITTINGS = (0, 40, 180, 3600, DAY, 3 * DAY, 7 * DAY)  # seconds after the first entry: enrolment burst, then sittings over a week


def make(n_people: int = 24, n_per: int = 12, n_bots: int = 150, seed: int = 0, pin: str = "1593") -> list[Record]:
    rng = random.Random(seed)
    out: list[Record] = []
    for i in range(n_people):
        pid, persona = f"p{i:02d}", tactics._persona(rng)
        base = T0 + rng.uniform(0, DAY)
        recs = []
        for j in range(n_per):
            t = base + SITTINGS[min(j // 2, len(SITTINGS) - 1)] + 25 * (j % 2) + rng.uniform(0, 20)
            drift = 1 + 0.015 * (t - base) / DAY  # slow rhythm drift: ~+10% after a week
            p = {**persona, "hold": persona["hold"] * drift, "flight": persona["flight"] * drift}
            raw = tactics._persona_session(pid, p, pin, tactics.DEFAULT_LAYOUT, rng)
            raw["attempt_meta"] = {"flow_stage": "signup_enroll" if j < 5 else "transfer", "retries": int(rng.random() < 0.15)}
            recs.append(Record(person=pid, account=pid, t=t, raw=raw, device=f"dev{i}", is_enrollment=j < 5, attempt_meta=raw["attempt_meta"]))
        build(recs)
        out += recs
    humans = [r.raw for r in out]
    for b in range(n_bots):
        tac = 1 + b % 4
        victim = out[rng.randrange(len(out))]
        raw = tactics.generate(tac, victim.account, pin, humans, rng)
        raw["attempt_meta"] = {"flow_stage": "transfer", "retries": 0}
        r = Record(person="bot", account=victim.account, t=victim.t + rng.uniform(0, 7 * DAY), raw=raw, role="bot", tactic=tac, device="bot",
                   attempt_meta=raw["attempt_meta"])
        # a bot's history is computed against the victim account's earlier sessions
        from innate_dl import history
        import datetime as dt
        prior = [history.Prior(dt.datetime.fromtimestamp(x.t, dt.timezone.utc), x.device, x.is_enrollment, x.action) for x in out if x.account == r.account]
        r.hist = history.compute([p for p in prior if p.created_at.timestamp() < r.t], "bot", dt.datetime.fromtimestamp(r.t, dt.timezone.utc), r.attempt_meta)
        out.append(r)
    return out
