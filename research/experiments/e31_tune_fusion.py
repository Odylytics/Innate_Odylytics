"""E31: chỉnh trọng số fusion và ngưỡng A trên kết quả E29, tune trên 3 phần, KIỂM trên 2 phần còn lại (người khác hẳn).

Đầu vào: pickle do e29 xuất (E29_DUMP): mỗi hàng (người, rủi ro quen, rủi ro mới, human, owner, phần). Tính lại rủi ro = wb·(1−human) + wo·(1−owner) (+ wn nếu người nhận mới).
Mục tiêu: trong số cấu hình để chủ vẫn được allow >= mức hiện tại (76% trên phần tune), chọn cấu hình tối đa hoá tỉ lệ KHÔNG allow trung bình của nhóm "kẻ tấn công thích nghi"
(kẻ biết PIN, CT4, bot biết mẫu chuẩn 1,0 và 0,5, phát lại ±15/20/30%). B giữ 0,55, HUMAN_HOLD 0,3, số tiền 0.
Chạy: python research/experiments/e31_tune_fusion.py <đường dẫn pickle>
"""
import pickle, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parents[2]
R = pickle.load(open(sys.argv[1], "rb"))
G = list(R)
OWN, ADV = G[0], [G[1], G[5], G[10], G[11], G[7], G[8], G[9]]  # thứ tự nhóm của e29 (không còn nhóm thứ hai cũ)
TUNE, TEST = {0, 1, 2}, {3, 4}
B, HH = 0.55, 0.3


def arr(g, folds):
    rows = [r for r in R[g] if r[5] in folds]
    return np.array([r[3] for r in rows]), np.array([r[4] if r[4] is not None else 0.5 for r in rows])


def allow_rate(g, folds, wb, wo, A, new=False):
    h, o = arr(g, folds)
    risk = wb * (1 - h) + wo * (1 - o) + (0.15 if new else 0)
    hold = (h < HH) | (risk > B)
    return float(((~hold) & (risk < A)).mean())


def adv_block(folds, wb, wo, A):
    return float(np.mean([1 - allow_rate(g, folds, wb, wo, A) for g in ADV]))


cur = (0.40, 0.35, 0.25)
base_own = allow_rate(OWN, TUNE, *cur)
best = None
for wo in np.arange(0.20, 0.71, 0.05):
    for wb in np.arange(0.20, 0.51, 0.05):
        for A in np.arange(0.05, 0.50, 0.01):
            if allow_rate(OWN, TUNE, wb, wo, A) < base_own:
                continue
            s = adv_block(TUNE, wb, wo, A)
            if best is None or s > best[0]:
                best = (s, wb, wo, A)
_, wb, wo, A = best
L = ["# E31 — chỉnh trọng số fusion và ngưỡng A (tune 3 phần, kiểm 2 phần của E29)", "",
     f"Ràng buộc: chủ allow trên phần tune >= hiện tại ({100 * base_own:.0f}%). Mục tiêu: trung bình tỉ lệ không-allow của 7 nhóm tấn công thích nghi. "
     "Lưới: wo 0,20–0,70, wb 0,20–0,50, A 0,05–0,49; B=0,55; số tiền = 0; trọng số người nhận mới 0,15. Bot ngây thơ và phát lại ≤±10% đã 100% ở mọi cấu hình nên không đưa vào mục tiêu.", "",
     f"Chọn được: wb={wb:.2f}, wo={wo:.2f}, A={A:.2f} (hiện tại: wb=0,40, wo=0,35, A=0,25).", "",
     "| Nhóm | hiện tại (kiểm) | đã chỉnh (kiểm) | hiện tại (tune) | đã chỉnh (tune) |", "|---|---|---|---|---|"]
for g in [OWN] + ADV:
    L.append(f"| {g}{' (allow)' if g == OWN else ' (không allow)'} | "
             + " | ".join(f"{100 * (allow_rate(g, f, *p) if g == OWN else 1 - allow_rate(g, f, *p)):.0f}%" for f, p in
                          ((TEST, cur), (TEST, (wb, wo, A)), (TUNE, cur), (TUNE, (wb, wo, A)))) + " |")
L.append(f"| **trung bình nhóm tấn công** | {100 * adv_block(TEST, *cur):.0f}% | {100 * adv_block(TEST, wb, wo, A):.0f}% | {100 * adv_block(TUNE, *cur):.0f}% | {100 * adv_block(TUNE, wb, wo, A):.0f}% |")
L += ["", f"Người nhận MỚI, chủ allow (kiểm): hiện tại {100 * allow_rate(OWN, TEST, *cur, new=True):.0f}%, đã chỉnh {100 * allow_rate(OWN, TEST, wb, wo, A, new=True):.0f}%.", "",
      "Giới hạn: một lần chia tune/kiểm, 97 người; mục tiêu là lựa chọn của đội (7 nhóm ngang nhau); bot do đội sinh; chưa dữ liệu đội. Không nên áp dụng nếu mức cải thiện trên phần kiểm nhỏ hơn dao động giữa hai phần."]
Path(ROOT / "research/results/e31_tune_fusion.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
