# E12 — mô hình xác minh chủ học được (StrokePIN, người thật)

Chia theo NGƯỜI (58 người huấn luyện / 39 người kiểm thử), 3 cách chia, trung bình. Đăng ký k=3 lượt, kẻ gian biết PIN. Đặc trưng = |z| của 26 đặc trưng backend. Cột chênh lệch = so với baseline trên cùng hàng kiểm thử (âm = tốt hơn); CI bootstrap theo người, trung bình giữa các lần chia.

| Mô hình | EER | FAR @ FRR 5% | dEER vs baseline | dFAR vs baseline |
|---|---|---|---|---|
| baseline (mean |z|, backend) | 0.149 | 0.528 | — | — |
| LR học trọng số | 0.129 | 0.300 | -0.020 [-0.031, -0.006] | -0.228 [-0.409, -0.121] |
| LightGBM học | 0.097 | 0.171 | -0.052 [-0.061, -0.043] | -0.357 [-0.540, -0.245] |

Trọng số lớn nhất mà LR học được (lần chia đầu; dương = |z| lớn hơn làm tăng khả năng là kẻ gian; đơn vị chưa chuẩn hoá giữa đặc trưng):

- `tap_w_mean`: +2.753
- `tap_h_mean`: +2.649
- `pin_hold_3`: +0.497
- `pin_hold_2`: +0.471
- `pin_hold_0`: +0.456
- `pin_hold_4`: +0.437
- `pin_hold_1`: +0.436
- `pin_hold_5`: +0.419
