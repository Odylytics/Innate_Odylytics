"""Operating-point calibration on VALIDATION people: tau(k, dt) (owner) and one threshold (human), each at FRR = 5%."""

import numpy as np

from .metrics import dt_bucket, k_bucket

MIN_GENUINE = 20  # below this a bucket falls back to the pooled threshold of its k bucket


def _thr(p_genuine: np.ndarray, frr: float) -> float:
    return float(np.quantile(p_genuine, frr))


def owner_tau(p, y, k, dt_h, frr: float = 0.05) -> dict:
    """{"2": {"le1h": t, "gt1h": t, "all": t}, ... "5+": ...} thresholds on P(owner); a score below tau is a rejection."""
    kb, small = k_bucket(k), dt_h <= 1
    out = {}
    for b in ("2", "3", "4", "5+"):
        m = (kb == b) & (y == 1)
        pooled = _thr(p[m], frr) if m.sum() >= 2 else 0.5
        cell = lambda mm: _thr(p[mm], frr) if mm.sum() >= MIN_GENUINE else pooled  # noqa: E731
        out["5" if b == "5+" else b] = {"le1h": cell(m & small), "gt1h": cell(m & ~small), "all": pooled}
    return out


def human_threshold(p_human: np.ndarray, frr: float = 0.05) -> float:
    return _thr(p_human, frr)


def apply_tau(p, k, dt_h, tau: dict) -> np.ndarray:
    """P(owner) -> score where the tau(k, dt) threshold maps to 0.5 (identical to dl_adapter._calibrate)."""
    out = np.empty(len(p))
    for i, (pi, ki, di) in enumerate(zip(p, k, dt_h)):
        t = tau[str(min(max(int(ki), 2), 5))]["le1h" if di <= 1 else "gt1h"]
        t = min(max(t, 1e-6), 1 - 1e-6)
        out[i] = 0.5 * pi / t if pi < t else 0.5 + 0.5 * (pi - t) / (1 - t)
    return out
