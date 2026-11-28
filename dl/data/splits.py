"""FETA-style splits: person-disjoint (train/val/test people never overlap) + time-split inside each person
(the first k entries by time are the gallery, later ones are queries). Impostor queries are other people's sessions and
are NEVER part of a gallery or of owner-head training for the same person."""

import random
from collections import defaultdict

from .ingest import Record


def person_split(persons: list[str], frac=(0.6, 0.2, 0.2), seed: int = 0) -> tuple[set, set, set]:
    ps = sorted(set(persons))
    random.Random(seed).shuffle(ps)
    a, b = round(len(ps) * frac[0]), round(len(ps) * (frac[0] + frac[1]))
    return set(ps[:a]), set(ps[a:b]), set(ps[b:])


def by_person(records: list[Record], role: str = "genuine") -> dict[str, list[Record]]:
    d = defaultdict(list)
    for r in records:
        if r.role == role:
            d[r.person].append(r)
    return {p: sorted(v, key=lambda r: r.t) for p, v in d.items()}


def time_split(sessions: list[Record], k: int) -> tuple[list[Record], list[Record]]:
    """(gallery, queries): the first k sessions by time vs everything later."""
    s = sorted(sessions, key=lambda r: r.t)
    return s[:k], s[k:]
