"""E20: MÔ PHỎNG (không phải đo người thật) — cần bao nhiêu âm tiết có chỗ chọn dấu thanh để `vi_tone_late` phân biệt hai người?

GIẢ ĐỊNH (chưa kiểm chứng): mỗi người có xác suất cố định p gõ dấu thanh muộn (cuối âm tiết) ở mỗi âm tiết có >= 2 chỗ đặt, độc lập giữa các âm tiết.
Kết quả chỉ cho biết ĐỘ DÀI/CHỌN CÂU nên thế nào, KHÔNG cho biết người Việt thật có phân tán thói quen như vậy. Dùng `vi_ime.tone_choices` để đếm âm tiết có chỗ chọn.
Chạy: python research/experiments/e20_vi_style_sim.py
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
    """k_* = số âm tiết có chỗ chọn mỗi phiên. Điểm lạ = |trung bình thử - trung bình đăng ký|."""
    own = rng.binomial(k_enroll, p_owner, trials) / k_enroll
    s_own = np.abs(rng.binomial(k_test, p_owner, trials) / k_test - own)
    s_imp = np.abs(rng.binomial(k_test, p_imp, trials) / k_test - own)
    return float(np.mean(s_imp > s_own) + 0.5 * np.mean(s_imp == s_own))


print("số âm tiết có chỗ chọn dấu thanh của từng câu:")
for p in challenge.PHRASES:
    print(f"  {choice_syllables(p):>2}  {p}")
print("\nAUC phân biệt chủ (p=0.8 muộn) và người khác (p=0.4), đăng ký 3 phiên cùng câu số âm tiết k:")
print("   k  | " + " | ".join(f"{k:>4}" for k in (1, 2, 3, 4, 5, 6, 8)))
print("  AUC | " + " | ".join(f"{auc(k, 3 * k, 0.8, 0.4):.2f}" for k in (1, 2, 3, 4, 5, 6, 8)))
print("\nkhoảng cách thói quen nhỏ hơn (0.8 vs 0.6), k=5:", f"{auc(5, 15, 0.8, 0.6):.2f}", "| lớn hơn (0.9 vs 0.2):", f"{auc(5, 15, 0.9, 0.2):.2f}")
