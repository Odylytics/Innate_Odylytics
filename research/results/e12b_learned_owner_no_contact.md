# E12 — mô hình xác minh chủ học được (StrokePIN, người thật)

Chia theo NGƯỜI (58 người huấn luyện / 39 người kiểm thử), 3 cách chia, trung bình. Đăng ký k=3 lượt ngồi, kẻ gian biết PIN. Đặc trưng = |z| của 24 đặc trưng backend (ĐÃ BỎ kích thước chạm: đối chứng thiết bị). Cột chênh lệch = so với baseline trên cùng hàng kiểm thử (âm = tốt hơn); CI bootstrap theo người, trung bình giữa các lần chia.

| Tư thế kiểm thử | Mô hình | EER | FAR @ FRR 5% | dEER vs baseline | dFAR vs baseline |
|---|---|---|---|---|---|
| cùng (ngồi) | baseline (mean |z|, backend) | 0.161 | 0.573 | — | — |
| cùng (ngồi) | LR học trọng số | 0.206 | 0.510 | +0.045 [+0.030, +0.058] | -0.063 [-0.229, +0.057] |
| cùng (ngồi) | LightGBM học | 0.158 | 0.375 | -0.003 [-0.013, +0.007] | -0.198 [-0.363, -0.085] |
| đổi (đi) | baseline (mean |z|, backend) | 0.363 | 0.944 | — | — |
| đổi (đi) | LR học trọng số | 0.319 | 0.737 | -0.043 [-0.070, -0.022] | -0.206 [-0.254, -0.149] |
| đổi (đi) | LightGBM học | 0.309 | 0.708 | -0.053 [-0.078, -0.033] | -0.236 [-0.294, -0.184] |

Trọng số lớn nhất mà LR học được (lần chia đầu; dương = |z| lớn hơn làm tăng khả năng là kẻ gian; đơn vị chưa chuẩn hoá giữa đặc trưng):

- `pin_hold_0`: +0.288
- `pin_flight_2`: +0.281
- `pin_hold_3`: +0.276
- `pin_hold_5`: +0.273
- `pin_hold_1`: +0.269
- `pin_hold_2`: +0.268
- `pin_hold_4`: +0.259
- `pin_flight_3`: +0.184
