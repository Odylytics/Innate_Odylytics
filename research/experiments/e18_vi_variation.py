"""E18: một câu tiếng Việt có bao nhiêu cách gõ hợp lệ bằng Telex/VNI? (đếm lý thuyết, KHÔNG phải đo người thật)

Chỉ đếm biến thể CHẮC CHẮN: vị trí phím dấu thanh (ngay sau nguyên âm hoặc sau mỗi chữ còn lại tới cuối âm tiết, Unikey/Gboard cho phép)
nhân với 2 bộ gõ (Telex/VNI). Chưa đếm: thứ tự dấu mũ/móc và dấu thanh, gõ w trễ (ươ), sửa lỗi, tắt/bật kiểu đặt dấu cũ/mới (cần thử trên bộ gõ thật).
Log2 của số biến thể là TRẦN của thông tin: người thật dồn vào vài thói quen phổ biến nên entropy thật thấp hơn, chưa đo.
Dùng: python research/experiments/e18_vi_variation.py
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
    "mua 4 ca phe 27",  # câu không dấu (thiết kế cũ): đối chứng
]


def variants(phrase: str) -> int:
    n = 1
    for w in phrase.split():
        n *= max(1, tone_choices(w))
    return n


if __name__ == "__main__":
    print(f"{'câu':48} {'phím biến đổi':>13} {'cách đặt thanh':>14} {'x2 bộ gõ':>9} {'log2':>5}")
    for p in PHRASES:
        v = variants(p)
        print(f"{p:48} {expected_transforms(p):>13} {v:>14} {2 * v:>9} {math.log2(2 * v):>5.1f}")
