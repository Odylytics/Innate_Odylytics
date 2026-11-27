# E24 / E25 / E27 — quyết định toàn hệ thống trên StrokePIN (người thật) + bot

10 người chưa từng thấy bởi cả hai mô hình học; đăng ký 3 lượt mỗi (người, PIN); lịch sử phát lại = các lượt trước. Ngưỡng hiện tại A=0.25, B=0.55. Kẻ biết PIN dùng MÁY KHÁC (lẫn nhiễu thiết bị). Bot là bộ sinh/script của đội, không phải bot thật.

## E24 — người nhận quen, số tiền bình thường

| Nhóm | n | allow | step_up | hold | (không mô hình học) allow |
|---|---|---|---|---|---|
| chủ | 356 | 81% | 18% | 1% | 96% |
| kẻ biết PIN (người khác, máy khác) | 712 | 28% | 71% | 1% | 89% |
| bot CT1 đều | 356 | 0% | 0% | 100% | 0% |
| bot CT2 nhiễu thời gian | 356 | 0% | 0% | 100% | 0% |
| bot CT3 phát lại ±5% | 356 | 0% | 0% | 100% | 0% |
| bot CT4 lấy mẫu dân số | 356 | 5% | 72% | 23% | 81% |
| phát lại ±10% | 356 | 0% | 0% | 100% | 0% |
| phát lại ±15% | 356 | 60% | 13% | 28% | 71% |
| phát lại ±20% | 356 | 72% | 26% | 1% | 98% |
| phát lại ±30% | 356 | 44% | 53% | 3% | 98% |
| bot biết mẫu chuẩn (scale 1.0) | 356 | 79% | 15% | 6% | 97% |
| bot biết mẫu chuẩn (scale 0.5) | 356 | 86% | 5% | 9% | 95% |

## E24 — người nhận MỚI

| Nhóm | n | allow | step_up | hold | (không mô hình học) allow |
|---|---|---|---|---|---|
| chủ | 356 | 18% | 79% | 3% | 91% |
| kẻ biết PIN (người khác, máy khác) | 712 | 0% | 87% | 13% | 61% |
| bot CT1 đều | 356 | 0% | 0% | 100% | 0% |
| bot CT2 nhiễu thời gian | 356 | 0% | 0% | 100% | 0% |
| bot CT3 phát lại ±5% | 356 | 0% | 0% | 100% | 0% |
| bot CT4 lấy mẫu dân số | 356 | 0% | 45% | 55% | 46% |
| phát lại ±10% | 356 | 0% | 0% | 100% | 0% |
| phát lại ±15% | 356 | 8% | 64% | 28% | 69% |
| phát lại ±20% | 356 | 7% | 89% | 4% | 96% |
| phát lại ±30% | 356 | 1% | 91% | 8% | 97% |
| bot biết mẫu chuẩn (scale 1.0) | 356 | 21% | 72% | 7% | 92% |
| bot biết mẫu chuẩn (scale 0.5) | 356 | 39% | 52% | 9% | 85% |

## E25 — quét ngưỡng A (allow < A) và B (hold > B), người nhận quen, có mô hình học

Mục tiêu: chủ hầu như luôn `allow` (hold ≤ 1%), kẻ biết PIN và bot bị chặn (không `allow`) càng nhiều càng tốt.

| A | B | chủ: allow / hold | chủ, người nhận MỚI: allow | kẻ biết PIN: không allow | CT4: không allow | biết mẫu chuẩn 1.0: không allow | phát lại ±15%: không allow |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.55 | 81% / 1% | 18% | 72% | 95% | 21% | 40% | ← hiện tại
| 0.10 | 0.55 | 18% / 1% | 0% | 100% | 100% | 79% | 92% |
| 0.15 | 0.55 | 43% / 1% | 0% | 98% | 100% | 51% | 72% |
| 0.20 | 0.55 | 64% / 1% | 0% | 90% | 99% | 33% | 52% |
| 0.30 | 0.55 | 90% / 1% | 43% | 54% | 82% | 13% | 34% |
| 0.35 | 0.55 | 95% / 1% | 64% | 34% | 70% | 8% | 30% |
| 0.40 | 0.60 | 97% / 1% | 81% | 13% | 55% | 7% | 28% |
| 0.45 | 0.65 | 99% / 1% | 90% | 6% | 39% | 6% | 28% |
| 0.25 | 0.40 | 81% / 3% | 18% | 72% | 95% | 21% | 40% |
| 0.25 | 0.70 | 81% / 1% | 18% | 72% | 95% | 21% | 40% |

## E27b — quét ngưỡng phát lại (backend hiện dùng 0,07), có mô hình học, người nhận quen

Phiên bị coi là phát lại thì `hold`. Đánh đổi: ngưỡng cao bắt thêm bot phát lại có nhiễu nhưng chặn nhầm chủ.

| Ngưỡng | chủ: hold | phát lại ±10% | ±15% | ±20% | ±30% | bot biết mẫu chuẩn (1.0): hold |
|---|---|---|---|---|---|---|
| 0.050 | 1% | 100% | 28% | 1% | 3% | 6% |
| 0.070 | 1% | 100% | 28% | 1% | 3% | 6% |
| 0.085 | 3% | 100% | 85% | 10% | 3% | 10% |
| 0.100 | 6% | 100% | 99% | 50% | 3% | 16% |
| 0.120 | 15% | 100% | 100% | 96% | 7% | 33% |
| 0.150 | 37% | 100% | 100% | 100% | 50% | 55% |

