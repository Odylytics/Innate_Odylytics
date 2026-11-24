# E12 — mô hình xác minh chủ học được (StrokePIN, người thật)

Chia theo NGƯỜI (58 người huấn luyện / 39 người kiểm thử), 3 cách chia, trung bình. Đăng ký k=3 lượt ngồi, kẻ gian biết PIN. Đặc trưng = |z| của 31 đặc trưng backend. Cột chênh lệch = so với baseline trên cùng hàng kiểm thử (âm = tốt hơn); CI bootstrap theo người, trung bình giữa các lần chia.

| Tư thế kiểm thử | Mô hình | EER | FAR @ FRR 5% | dEER vs baseline | dFAR vs baseline |
|---|---|---|---|---|---|
| cùng (ngồi) | baseline (mean |z|, backend) | 0.149 | 0.558 | — | — |
| cùng (ngồi) | LR học trọng số | 0.135 | 0.296 | -0.014 [-0.027, -0.001] | -0.261 [-0.440, -0.138] |
| cùng (ngồi) | LightGBM học | 0.108 | 0.200 | -0.041 [-0.055, -0.030] | -0.358 [-0.540, -0.240] |
| đổi (đi) | baseline (mean |z|, backend) | 0.354 | 0.943 | — | — |
| đổi (đi) | LR học trọng số | 0.273 | 0.738 | -0.081 [-0.108, -0.052] | -0.205 [-0.352, -0.121] |
| đổi (đi) | LightGBM học | 0.264 | 0.675 | -0.090 [-0.120, -0.059] | -0.268 [-0.370, -0.195] |

Trọng số lớn nhất mà LR học được (lần chia đầu; dương = |z| lớn hơn làm tăng khả năng là kẻ gian; đơn vị chưa chuẩn hoá giữa đặc trưng):

- `tap_w_mean`: +1.382
- `tap_h_mean`: +1.016
- `pin_hold_0`: +0.288
- `pin_hold_2`: +0.256
- `pin_hold_3`: +0.254
- `pin_flight_2`: +0.250
- `pin_hold_1`: +0.246
- `pin_hold_4`: +0.245
