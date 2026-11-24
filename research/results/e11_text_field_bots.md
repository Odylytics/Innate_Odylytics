# E11 — bài người/máy trên ô văn bản tự do (người thật Aalto + bot sinh)

3 cách chia người. Người: 33522 câu gõ thật của 2260 người, chia theo người (kho kẻ tấn công 200 / train 1200 / val 300 / test còn lại). Ngưỡng FRR 5% trên người ở tập validation. Mỗi ô: **tỷ lệ bot bị bắt** (AUC). Chỉ ô `note`. Bot vẫn là giả.

## Huấn luyện thấy cả 4 chiến thuật

| Mô hình | FRR thật | CT1 đặt thẳng văn bản | CT2 gõ đều | CT3 phát lại | CT4 lấy mẫu dân số |
|---|---|---|---|---|---|
| LightGBM, backend (fld_*) | 0.048 | 1.00 (1.00) | 0.99 (1.00) | 0.06 (0.60) | 0.31 (0.85) |
| IsolationForest, backend (fld_*) | 0.064 | 0.00 (0.85) | 0.00 (0.71) | 0.05 (0.49) | 0.01 (0.42) |
| LightGBM, mở rộng | 0.047 | 1.00 (1.00) | 0.99 (1.00) | 0.08 (0.64) | 0.58 (0.93) |
| IsolationForest, mở rộng | 0.061 | 0.67 (0.95) | 0.00 (0.77) | 0.06 (0.48) | 0.01 (0.34) |
| Luật hiện tại của backend (cờ khi điểm < 0,5) | 0.000 | 0.00 | 0.00 | 0.00 | 0.00 |

## Bỏ đúng một chiến thuật khỏi huấn luyện (bot lạ)

| Mô hình | FRR thật | Bỏ CT1 | Bỏ CT2 | Bỏ CT3 | Bỏ CT4 |
|---|---|---|---|---|---|
| LightGBM, backend (fld_*) | 0.049 | 1.00 (0.99) | 0.00 (0.20) | 0.05 (0.52) | 0.04 (0.56) |
| IsolationForest, backend (fld_*) | 0.064 | 0.00 (0.85) | 0.00 (0.71) | 0.05 (0.49) | 0.01 (0.42) |
| LightGBM, mở rộng | 0.047 | 1.00 (0.99) | 0.01 (0.31) | 0.05 (0.52) | 0.05 (0.58) |
| IsolationForest, mở rộng | 0.061 | 0.67 (0.95) | 0.00 (0.77) | 0.06 (0.48) | 0.01 (0.34) |
