# E4b — người/máy với NGƯỜI THẬT (StrokePIN) và bot do bộ sinh tạo

3 cách chia người khác nhau (train 40 / val 12 / test 30 / kho kẻ tấn công 15 người, không trùng người). Ngưỡng chọn để FRR = 5% trên người ở tập validation. Mỗi ô: **tỷ lệ bot bị bắt** (AUC). Chỉ so phần PIN. Bot vẫn là giả.

## Huấn luyện thấy cả 4 chiến thuật

| Mô hình | FRR thật (người test) | CT1 | CT2 | CT3 | CT4 |
|---|---|---|---|---|---|
| LightGBM | 0.059 | 1.00 (1.00) | 1.00 (1.00) | 0.26 (0.74) | 0.73 (0.93) |
| IsolationForest (chỉ người) | 0.046 | 1.00 (0.97) | 0.86 (0.97) | 0.07 (0.54) | 0.03 (0.59) |
| Bộ kết hợp | 0.053 | 1.00 (0.97) | 1.00 (0.97) | 0.20 (0.57) | 0.62 (0.78) |
| LightGBM (không kích thước chạm) | 0.059 | 1.00 (1.00) | 1.00 (1.00) | 0.23 (0.72) | 0.69 (0.91) |
| IsolationForest (chỉ người) (không kích thước chạm) | 0.056 | 0.33 (0.94) | 0.31 (0.93) | 0.07 (0.52) | 0.03 (0.59) |
| Bộ kết hợp (không kích thước chạm) | 0.061 | 1.00 (0.97) | 1.00 (0.97) | 0.18 (0.56) | 0.61 (0.77) |
| Luật baseline (human.py) | 0.058 | 1.00 (1.00) | 1.00 (1.00) | 0.05 (0.49) | 0.01 (0.46) |

## Bỏ đúng một chiến thuật khỏi huấn luyện, kiểm thử trên chiến thuật đó (bot lạ)

| Mô hình | FRR thật | Bỏ CT1 | Bỏ CT2 | Bỏ CT3 | Bỏ CT4 |
|---|---|---|---|---|---|
| LightGBM | 0.059 | 1.00 (1.00) | 0.56 (0.86) | 0.09 (0.57) | 0.20 (0.66) |
| IsolationForest (chỉ người) | 0.046 | 1.00 (0.97) | 0.86 (0.97) | 0.07 (0.54) | 0.03 (0.59) |
| Bộ kết hợp | 0.057 | 1.00 (0.97) | 0.76 (0.85) | 0.09 (0.52) | 0.15 (0.54) |
| LightGBM (không kích thước chạm) | 0.058 | 1.00 (1.00) | 0.47 (0.80) | 0.08 (0.57) | 0.20 (0.70) |
| IsolationForest (chỉ người) (không kích thước chạm) | 0.056 | 0.33 (0.94) | 0.31 (0.93) | 0.07 (0.52) | 0.03 (0.59) |
| Bộ kết hợp (không kích thước chạm) | 0.064 | 1.00 (0.97) | 0.39 (0.66) | 0.09 (0.52) | 0.16 (0.54) |
