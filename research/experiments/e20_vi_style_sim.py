"""E20: SIMULATION (not measured on real people) — how many syllables with a tone-placement choice are needed for `vi_tone_late` to tell two people apart?

ASSUMPTION (unverified): each person has a fixed probability p of typing the tone mark late (at the end of the syllable) on each syllable with >= 2 possible placements, independently across syllables.
The result only says how LONG the sentence should be / how to CHOOSE sentences, it does NOT show that real Vietnamese typists vary in habit like this. Uses `vi_ime.tone_choices` to count syllables with a choice.
Run: python research/experiments/e20_vi_style_sim.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path[:0] = [str(Path(__file__).parents[2] / "backend")]
from app.scoring import challenge, vi_ime  # noqa: E402

rng = np.random.default_rng(0)


def choice_syllables(p: str) -> int:
    return sum(vi_ime.tone_choices(w) >= 2 for w in p.split())


def auc(k_test: int, k_enroll: int, p_owner: float, p_imp: float, trials: int = 4000) -> float:
    """k_* = number of syllables with a choice per session. Anomaly score = |test mean - enrollment mean|."""
    own = rng.binomial(k_enroll, p_owner, trials) / k_enroll
    s_own = np.abs(rng.binomial(k_test, p_owner, trials) / k_test - own)
    s_imp = np.abs(rng.binomial(k_test, p_imp, trials) / k_test - own)
    return float(np.mean(s_imp > s_own) + 0.5 * np.mean(s_imp == s_own))


print("number of syllables with a tone-placement choice in each sentence:")
for p in challenge.PHRASES:
    print(f"  {choice_syllables(p):>2}  {p}")
print("\nAUC separating the owner (p=0.8 late) from another person (p=0.4), enrollment of 3 sessions with the same number of syllables k:")
print("   k  | " + " | ".join(f"{k:>4}" for k in (1, 2, 3, 4, 5, 6, 8)))
print("  AUC | " + " | ".join(f"{auc(k, 3 * k, 0.8, 0.4):.2f}" for k in (1, 2, 3, 4, 5, 6, 8)))
print("\nsmaller habit gap (0.8 vs 0.6), k=5:", f"{auc(5, 15, 0.8, 0.6):.2f}", "| larger (0.9 vs 0.2):", f"{auc(5, 15, 0.9, 0.2):.2f}")
