# E24 / E25 / E27 — quyết định toàn hệ thống trên StrokePIN (người thật) + bot

10 người chưa từng thấy bởi cả hai mô hình học; đăng ký 3 lượt ngồi mỗi (người, PIN); lịch sử phát lại = các lượt trước. Ngưỡng hiện tại A=0.25, B=0.55. Kẻ biết PIN dùng MÁY KHÁC (lẫn nhiễu thiết bị). Bot là bộ sinh/script của đội, không phải bot thật.

## E24 — người nhận quen, số tiền bình thường

| Nhóm | n | allow | step_up | hold | (không mô hình học) allow |
|---|---|---|---|---|---|
| chủ, cùng tư thế (ngồi) | 356 | 80% | 19% | 1% | 96% |
| chủ, đổi tư thế (đi) | 709 | 63% | 37% | 0% | 91% |
| kẻ biết PIN (người khác, máy khác) | 712 | 28% | 70% | 2% | 90% |
| bot CT1 đều | 356 | 0% | 0% | 100% | 0% |
| bot CT2 nhiễu thời gian | 356 | 0% | 0% | 100% | 0% |
| bot CT3 phát lại ±5% | 356 | 0% | 0% | 100% | 0% |
| bot CT4 lấy mẫu dân số | 356 | 7% | 67% | 26% | 80% |
| phát lại ±10% | 356 | 0% | 0% | 100% | 0% |
| phát lại ±15% | 356 | 58% | 13% | 30% | 71% |
| phát lại ±20% | 356 | 72% | 26% | 1% | 99% |
| phát lại ±30% | 356 | 48% | 48% | 4% | 99% |
| bot biết mẫu chuẩn (scale 1.0) | 356 | 75% | 17% | 8% | 96% |
| bot biết mẫu chuẩn (scale 0.5) | 356 | 82% | 6% | 12% | 94% |

## E24 — người nhận MỚI

| Nhóm | n | allow | step_up | hold | (không mô hình học) allow |
|---|---|---|---|---|---|
| chủ, cùng tư thế (ngồi) | 356 | 17% | 79% | 4% | 92% |
| chủ, đổi tư thế (đi) | 709 | 2% | 95% | 3% | 77% |
| kẻ biết PIN (người khác, máy khác) | 712 | 1% | 86% | 14% | 62% |
| bot CT1 đều | 356 | 0% | 0% | 100% | 0% |
| bot CT2 nhiễu thời gian | 356 | 0% | 0% | 100% | 0% |
| bot CT3 phát lại ±5% | 356 | 0% | 0% | 100% | 0% |
| bot CT4 lấy mẫu dân số | 356 | 0% | 46% | 54% | 50% |
| phát lại ±10% | 356 | 0% | 0% | 100% | 0% |
| phát lại ±15% | 356 | 8% | 61% | 31% | 70% |
| phát lại ±20% | 356 | 6% | 90% | 4% | 98% |
| phát lại ±30% | 356 | 1% | 88% | 11% | 99% |
| bot biết mẫu chuẩn (scale 1.0) | 356 | 20% | 71% | 9% | 89% |
| bot biết mẫu chuẩn (scale 0.5) | 356 | 43% | 46% | 12% | 86% |

## E25 — quét ngưỡng A (allow < A) và B (hold > B), người nhận quen, có mô hình học

Mục tiêu: chủ cùng tư thế hầu như luôn `allow` (hold ≤ 1%), kẻ biết PIN và bot bị chặn (không `allow`) càng nhiều càng tốt.

| A | B | chủ ngồi: allow / hold | chủ đi: allow | chủ ngồi, người nhận MỚI: allow | kẻ biết PIN: không allow | CT4: không allow | biết mẫu chuẩn 1.0: không allow | phát lại ±15%: không allow |
|---|---|---|---|---|---|---|---|---|
| 0.25 | 0.55 | 80% / 1% | 63% | 17% | 72% | 93% | 25% | 42% | ← hiện tại
| 0.10 | 0.55 | 17% / 1% | 2% | 0% | 99% | 100% | 80% | 92% |
| 0.15 | 0.55 | 42% / 1% | 11% | 0% | 98% | 100% | 54% | 73% |
| 0.20 | 0.55 | 65% / 1% | 34% | 0% | 90% | 98% | 36% | 58% |
| 0.30 | 0.55 | 91% / 1% | 83% | 42% | 50% | 80% | 17% | 38% |
| 0.35 | 0.55 | 95% / 1% | 92% | 65% | 31% | 67% | 12% | 33% |
| 0.40 | 0.60 | 96% / 1% | 97% | 80% | 14% | 54% | 9% | 31% |
| 0.45 | 0.65 | 98% / 1% | 99% | 91% | 6% | 42% | 8% | 30% |
| 0.25 | 0.40 | 80% / 4% | 63% | 17% | 72% | 93% | 25% | 42% |
| 0.25 | 0.70 | 80% / 1% | 63% | 17% | 72% | 93% | 25% | 42% |

## E27b — quét ngưỡng phát lại (backend hiện dùng 0,07), có mô hình học, người nhận quen

Phiên bị coi là phát lại thì `hold`. Đánh đổi: ngưỡng cao bắt thêm bot phát lại có nhiễu nhưng chặn nhầm chủ.

| Ngưỡng | chủ ngồi: hold | chủ đi: hold | phát lại ±10% | ±15% | ±20% | ±30% | bot biết mẫu chuẩn (1.0): hold |
|---|---|---|---|---|---|---|---|
| 0.050 | 1% | 0% | 100% | 30% | 1% | 4% | 8% |
| 0.070 | 1% | 0% | 100% | 30% | 1% | 4% | 8% |
| 0.085 | 3% | 0% | 100% | 86% | 11% | 4% | 11% |
| 0.100 | 6% | 0% | 100% | 99% | 47% | 4% | 17% |
| 0.120 | 17% | 1% | 100% | 100% | 95% | 8% | 33% |
| 0.150 | 38% | 6% | 100% | 100% | 100% | 51% | 58% |

