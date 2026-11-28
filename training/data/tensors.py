"""Model inputs. The preprocessing lives in backend/app/scoring/dl_adapter.py (single source, shared with the live API)."""

import numpy as np

from app.scoring.dl_adapter import F_NAMES, K_MAX, L_MAX, N_CTX, ctx_vector, seq_tensor, tab_vector  # noqa: F401
from app.scoring import bot_features

from .ingest import Record


def fit_norm(records: list[Record]) -> tuple[np.ndarray, np.ndarray]:
    """Mean/std of f_tab over TRAIN records (NaN ignored)."""
    f = np.array([[bot_features.extract(r.raw)[n] for n in F_NAMES] for r in records], dtype=np.float64)
    return np.nan_to_num(np.nanmean(f, 0)), np.maximum(np.nan_to_num(np.nanstd(f, 0)), 1e-6)


class Table:
    """Pre-computed tensors of a record list: x (N,L,10), c (N,14), f (N,F)."""

    def __init__(self, records: list[Record], mean: np.ndarray, std: np.ndarray):
        self.records = records
        self.x = np.stack([seq_tensor(r.raw) for r in records]).astype(np.float32)
        self.c = np.stack([ctx_vector(r.hist) for r in records]).astype(np.float32)
        self.f = np.stack([tab_vector(r.raw, mean, std) for r in records]).astype(np.float32)
        self.t = np.array([r.t for r in records])
