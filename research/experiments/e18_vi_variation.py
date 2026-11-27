"""E18: how many valid ways are there to type one Vietnamese sentence with Telex/VNI? (theoretical count, NOT measured on real people)

Counts only CERTAIN variants: the position of the tone key (right after the vowel or after each remaining letter up to the end of the syllable, which Unikey/Gboard allow)
times 2 input methods (Telex/VNI). Not counted: the order of the circumflex/horn marks and the tone mark, late w (ươ), corrections, toggling the old/new tone-placement style (needs testing on a real IME).
Log2 of the number of variants is a CEILING on the information: real people concentrate on a few common habits, so the real entropy is lower (not measured).
Usage: python research/experiments/e18_vi_variation.py
"""
import math
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).parents[2] / "backend")]
from app.scoring.vi_ime import expected_transforms, tone_choices  # noqa: E402

PHRASES = [
    "Hôm nay trời đẹp quá",
    "Tuần này trời nắng đẹp quá",
    "Chuyển tiền cho mẹ ở quê",
    "Hôm nay trời đẹp quá mình đi uống cà phê nhé",
    "mua 4 ca phe 27",  # sentence without diacritics (old design): control
]


def variants(phrase: str) -> int:
    n = 1
    for w in phrase.split():
        n *= max(1, tone_choices(w))
    return n


if __name__ == "__main__":
    print(f"{'phrase':48} {'transforms':>13} {'tone options':>14} {'x2 IMEs':>9} {'log2':>5}")
    for p in PHRASES:
        v = variants(p)
        print(f"{p:48} {expected_transforms(p):>13} {v:>14} {2 * v:>9} {math.log2(2 * v):>5.1f}")
