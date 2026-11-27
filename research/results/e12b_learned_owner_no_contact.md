# E12 — mô hình xác minh chủ học được (StrokePIN, người thật)

Chia theo NGƯỜI (58 người huấn luyện / 39 người kiểm thử), 3 cách chia, trung bình. Đăng ký k=3 lượt, kẻ gian biết PIN. Đặc trưng = |z| của 24 đặc trưng backend (ĐÃ BỎ kích thước chạm: đối chứng thiết bị). Cột chênh lệch = so với baseline trên cùng hàng kiểm thử (âm = tốt hơn); CI bootstrap theo người, trung bình giữa các lần chia.

| Mô hình | EER | FAR @ FRR 5% | dEER vs baseline | dFAR vs baseline |
|---|---|---|---|---|
| baseline (mean |z|, backend) | 0.160 | 0.549 | — | — |
| LR học trọng số | 0.188 | 0.546 | +0.028 [+0.018, +0.040] | -0.004 [-0.166, +0.083] |
| LightGBM học | 0.140 | 0.316 | -0.020 [-0.026, -0.014] | -0.233 [-0.410, -0.134] |

Trọng số lớn nhất mà LR học được (lần chia đầu; dương = |z| lớn hơn làm tăng khả năng là kẻ gian; đơn vị chưa chuẩn hoá giữa đặc trưng):

- `pin_hold_3`: +0.497
- `pin_hold_2`: +0.468
- `pin_hold_1`: +0.458
- `pin_hold_5`: +0.456
- `pin_hold_0`: +0.451
- `pin_hold_4`: +0.443
- `pin_flight_2`: +0.398
- `pin_total`: +0.344
