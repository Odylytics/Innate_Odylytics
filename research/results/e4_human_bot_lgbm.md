# E4 — LightGBM cho bài người/máy (dữ liệu giả)

3 lần sinh dữ liệu độc lập, trung bình. Ngưỡng chọn trên người ở tập validation để FRR = 5%. Mỗi ô là **tỷ lệ bot bị bắt** (AUC trong ngoặc). Dữ liệu giả: chỉ kiểm chứng đường ống.

## Huấn luyện thấy cả 4 chiến thuật (lạc quan)

| Mô hình | FRR thật | Chiến thuật 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| LightGBM | 0.047 | 1.00 (1.00) | 1.00 (1.00) | 0.85 (0.97) | 0.97 (0.99) |
| IsolationForest (chỉ người) | 0.051 | 1.00 (1.00) | 1.00 (1.00) | 0.12 (0.65) | 0.47 (0.87) |
| Bộ kết hợp (LightGBM hoặc IsolationForest) | 0.049 | 1.00 (nan) | 1.00 (nan) | 0.80 (nan) | 0.97 (nan) |
| LightGBM (không kích thước chạm) | 0.052 | 1.00 (1.00) | 1.00 (1.00) | 0.85 (0.96) | 0.98 (1.00) |
| IsolationForest (chỉ người) (không kích thước chạm) | 0.050 | 1.00 (1.00) | 1.00 (1.00) | 0.13 (0.67) | 0.38 (0.85) |
| Bộ kết hợp (LightGBM hoặc IsolationForest) (không kích thước chạm) | 0.047 | 1.00 (nan) | 1.00 (nan) | 0.82 (nan) | 0.97 (nan) |
| Luật baseline (human.py) | 0.049 | 1.00 (1.00) | 1.00 (1.00) | 0.04 (0.49) | 0.01 (0.41) |

## Bỏ một chiến thuật khỏi huấn luyện, kiểm thử trên đúng chiến thuật đó (thực tế hơn với bot lạ)

| Mô hình | FRR thật | Bỏ chiến thuật 1 | Bỏ 2 | Bỏ 3 | Bỏ 4 |
|---|---|---|---|---|---|
| LightGBM | 0.047 | 0.00 (0.50) | 1.00 (1.00) | 0.07 (0.56) | 0.23 (0.68) |
| IsolationForest (chỉ người) | 0.051 | 1.00 (1.00) | 1.00 (1.00) | 0.12 (0.65) | 0.47 (0.87) |
| Bộ kết hợp (LightGBM hoặc IsolationForest) | 0.049 | 1.00 (nan) | 1.00 (nan) | 0.11 (nan) | 0.41 (nan) |
| LightGBM (không kích thước chạm) | 0.050 | 0.00 (0.41) | 1.00 (1.00) | 0.08 (0.57) | 0.24 (0.69) |
| IsolationForest (chỉ người) (không kích thước chạm) | 0.050 | 1.00 (1.00) | 1.00 (1.00) | 0.13 (0.67) | 0.38 (0.85) |
| Bộ kết hợp (LightGBM hoặc IsolationForest) (không kích thước chạm) | 0.049 | 1.00 (nan) | 1.00 (nan) | 0.13 (nan) | 0.37 (nan) |

## Mô hình dựa vào đặc trưng nào (gain, mô hình đầy đủ)

| Đặc trưng | Tỷ trọng gain |
|---|---|
| swipe_v_peak_ratio | 0.18 |
| swipe_lateral_dev | 0.16 |
| dy_std | 0.14 |
| tap_w_std | 0.13 |
| dx_std | 0.10 |
| off_mean | 0.09 |
| swipe_straight | 0.03 |
| tap_h_std | 0.03 |

Mô hình đầy đủ lưu ở `research/models/human_lgbm_synthetic.txt` (huấn luyện trên dữ liệu GIẢ, **không dùng cho bản nộp**).
