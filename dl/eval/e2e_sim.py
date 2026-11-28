"""Whole-system simulation with backend/app/scoring/fusion.py: calibrated human + owner scores -> action rates."""

import numpy as np

from app.scoring import fusion


def actions(human: np.ndarray, owner: np.ndarray | None, new_recipient: bool = False) -> np.ndarray:
    return np.array([fusion.fuse(float(h), None if owner is None else float(o), new_recipient, 0.0)[1]
                     for h, o in zip(human, owner if owner is not None else human)])


def rates(a: np.ndarray) -> dict:
    return {k: round(float((a == k).mean()), 3) if len(a) else None for k in ("allow", "step_up", "hold")}


def simulate(h_gen, o_gen, h_imp, o_imp, h_bot, o_bot) -> dict:
    """genuine owner / PIN-knowing human impostor / bot, each as {allow, step_up, hold} shares."""
    return {"owner": rates(actions(h_gen, o_gen)), "impostor": rates(actions(h_imp, o_imp)), "bot": rates(actions(h_bot, o_bot))}
