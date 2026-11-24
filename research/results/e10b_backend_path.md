# E10b — chính `owner.py` của backend trên StrokePIN (prior bỏ-một-người)

k=3 lượt đăng ký ngồi, kẻ gian biết PIN, mọi đặc trưng nhận dạng như backend thật. CI 95% bootstrap theo người (100 lần). Hàng cuối mỗi bảng là chênh lệch ghép cặp (bật trừ tắt; âm = tốt hơn).

## cùng tư thế (ngồi)

| Co rút | EER | FAR @ FRR 5% |
|---|---|---|
| tắt (hành vi cũ) | 0.153 | 0.663 |
| bật (co rút thời gian) | 0.146 | 0.495 |
| **chênh lệch ghép cặp** | -0.007 [-0.011, -0.004] | -0.167 [-0.190, -0.114] |

## đổi tư thế (đi)

| Co rút | EER | FAR @ FRR 5% |
|---|---|---|
| tắt (hành vi cũ) | 0.352 | 0.943 |
| bật (co rút thời gian) | 0.355 | 0.943 |
| **chênh lệch ghép cặp** | +0.003 [-0.000, +0.007] | -0.000 [-0.001, +0.001] |
