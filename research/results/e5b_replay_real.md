# E5b — hiệu chỉnh kiểm tra phát lại trên người thật (StrokePIN)

1817 cặp (người, PIN), mỗi cặp ~5 lượt cùng PIN. Ngưỡng hiện tại trong backend: **0.07** (chọn trên dữ liệu giả ở E5). Khoảng cách = `replay.distance` của backend.

## Người thật mới có bị coi là phát lại không? (khoảng cách gần nhất tới lịch sử của chính họ)

| Số phiên cũ đem so | Số lượt thử | Trung vị khoảng cách | FPR tại ngưỡng hiện tại | FPR tại 0.5x ngưỡng |
|---|---|---|---|---|
| 2 | 8969 | 0.185 | 0.0008 | 0.0001 |
| 3 | 8969 | 0.174 | 0.0014 | 0.0001 |
| 4 | 8505 | 0.167 | 0.0020 | 0.0002 |

Phân vị khoảng cách người thật: 0,1% = 0.064; 0,5% = 0.082; 1% = 0.088; 5% = 0.107. Khoảng cách trung vị của phiên phát lại theo nhiễu: ±2.5% -> 0.019, ±5.0% -> 0.025, ±10.0% -> 0.050, ±15.0% -> 0.075, ±20.0% -> 0.100, ±30.0% -> 0.150.

**Ngoại suy tuyến tính** FPR theo số phiên cũ (chỉ có dữ liệu tới 4): ~0.061 điểm phần trăm mỗi phiên cũ thêm, nên với 50 phiên khoảng **3.0%** (không đo được: đây là suy đoán, lịch sử trong dữ liệu chỉ ~4 lượt, ngoại suy rất xa nên chỉ để tham khảo).

Khoảng cách người thật: phân vị 1% = **0.088**, 5% = 0.107, trung vị = 0.176.

## Bắt được bao nhiêu phiên phát lại (kẻ tấn công thích nghi: nhiễu thời gian ±n, toạ độ ±max(0.02, 0.4n) bề rộng phím)

| Nhiễu ±n | 2.5% | 5.0% | 10.0% | 15.0% | 20.0% | 30.0% |
|---|---|---|---|---|---|---|
| Ngưỡng hiện tại (0.07) | 1.00 | 1.00 | 1.00 | 0.28 | 0.00 | 0.00 |
| Ngưỡng FPR 1% (0.088) | 1.00 | 1.00 | 1.00 | 0.92 | 0.16 | 0.00 |
| Ngưỡng FPR 5% (0.107) | 1.00 | 1.00 | 1.00 | 1.00 | 0.73 | 0.01 |

## Đánh đổi theo ngưỡng (FPR đo ở 2/3/4 phiên cũ; ngoại suy tuyến tính tới 50; tỷ lệ bắt theo nhiễu)

| Ngưỡng | FPR @2 | FPR @4 | FPR @50 (ngoại suy) | bắt ±2.5% | bắt ±5.0% | bắt ±10.0% | bắt ±15.0% | bắt ±20.0% | bắt ±30.0% |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.0001 | 0.0002 | 0.3% | 1.00 | 1.00 | 0.51 | 0.00 | 0.00 | 0.00 |
| 0.06 | 0.0003 | 0.0006 | 0.6% | 1.00 | 1.00 | 0.95 | 0.05 | 0.00 | 0.00 |
| 0.07 | 0.0008 | 0.0020 | 3.0% | 1.00 | 1.00 | 1.00 | 0.28 | 0.00 | 0.00 |
| 0.085 | 0.0050 | 0.0111 | 15.0% | 1.00 | 1.00 | 1.00 | 0.85 | 0.10 | 0.00 |
| 0.094 | 0.0126 | 0.0226 | 25.2% | 1.00 | 1.00 | 1.00 | 0.98 | 0.31 | 0.00 |
