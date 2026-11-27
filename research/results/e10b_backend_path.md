# E10b — chính `owner.py` của backend trên StrokePIN (prior bỏ-một-người)

k=3 lượt đăng ký, kẻ gian biết PIN, mọi đặc trưng nhận dạng như backend thật. CI 95% bootstrap theo người (100 lần). Hàng cuối mỗi bảng là chênh lệch ghép cặp (bật trừ tắt; âm = tốt hơn).

| Co rút | EER | FAR @ FRR 5% |
|---|---|---|
| tắt (hành vi cũ) | 0.157 | 0.704 |
| bật (co rút thời gian) | 0.148 | 0.541 |
| **chênh lệch ghép cặp** | -0.008 [-0.011, -0.005] | -0.163 [-0.196, -0.121] |
