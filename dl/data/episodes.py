"""Verification episodes: gallery = the person's first k entries by time, query = a later entry (genuine) or another person's
entry (impostor, same PIN is typical). The impostor query inherits the time of the genuine query it is paired with and
is never part of any gallery (FETA)."""

import random
from dataclasses import dataclass

import numpy as np

from innate_dl.dl_adapter import K_MAX

from .splits import by_person


@dataclass
class Episodes:
    gal: np.ndarray  # (n, K_MAX) table indices (padded with 0)
    mask: np.ndarray  # (n, K_MAX)
    q: np.ndarray  # (n,) table index of the query
    dt_h: np.ndarray  # (n, K_MAX) hours from each gallery entry to the query time
    y: np.ndarray  # (n,) 1 = genuine
    person: np.ndarray  # (n,) the account owner
    k: np.ndarray  # (n,)

    def __len__(self):
        return len(self.y)

    @property
    def dt_last_h(self):
        return np.where(self.mask > 0, self.dt_h, 1e9).min(1)


def person_index(table, people: set[str]) -> dict[str, list[int]]:
    """person -> table indices of their genuine entries in time order."""
    ids = {id(r): i for i, r in enumerate(table.records)}
    return {p: [ids[id(r)] for r in v] for p, v in by_person(table.records).items() if p in people}


def make(table, people: set[str], ks, n_imp: int = 1, max_q: int | None = None, seed: int = 0, min_q: int = 1) -> Episodes:
    rng = random.Random(seed)
    idx = person_index(table, people)
    pool = [i for v in idx.values() for i in v]
    own = {i: p for p, v in idx.items() for i in v}
    rows = []
    for p, v in idx.items():
        for k in ks:
            if len(v) < k + min_q:
                continue
            qs = v[k:]
            if max_q and len(qs) > max_q:
                qs = rng.sample(qs, max_q)
            for q in qs:
                rows.append((p, k, v[:k], q, 1, q))
                others = [i for i in rng.sample(pool, min(len(pool), 8 * n_imp)) if own[i] != p][:n_imp]
                rows += [(p, k, v[:k], i, 0, q) for i in others]  # the impostor query takes the genuine query's time
    n = len(rows)
    gal, mask, dt, q, tq = np.zeros((n, K_MAX), int), np.zeros((n, K_MAX), np.float32), np.zeros((n, K_MAX), np.float32), np.zeros(n, int), np.zeros(n)
    for r, (p, k, g, qi, y, qt) in enumerate(rows):
        g = g[-K_MAX:]
        gal[r, :len(g)], mask[r, :len(g)], q[r], tq[r] = g, 1, qi, table.t[qt]
        dt[r, :len(g)] = np.maximum(tq[r] - table.t[g], 0) / 3600
    return Episodes(gal, mask, q, dt, np.array([x[4] for x in rows]), np.array([x[0] for x in rows]), np.array([min(x[1], K_MAX) for x in rows]))
