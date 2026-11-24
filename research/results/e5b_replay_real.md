# E5b — hiệu chỉnh kiểm tra phát lại trên người thật (StrokePIN)

1842 cặp (người, PIN), mỗi cặp 4–10 lượt cùng PIN (cả ngồi và đi). Ngưỡng hiện tại trong backend: **0.085** (chọn trên dữ liệu giả ở E5). Khoảng cách = `replay.distance` của backend.

## Người thật mới có bị coi là phát lại không? (khoảng cách gần nhất tới lịch sử của chính họ)

| Số phiên cũ đem so | Số lượt thử | Trung vị khoảng cách | FPR tại ngưỡng hiện tại | FPR tại 0.5x ngưỡng |
|---|---|---|---|---|
| 3 | 17892 | 0.206 | 0.0028 | 0.0001 |
| 5 | 17777 | 0.189 | 0.0040 | 0.0001 |
| 8 | 17071 | 0.176 | 0.0064 | 0.0001 |

Phân vị khoảng cách người thật: 0,1% = 0.071; 0,5% = 0.087; 1% = 0.094; 5% = 0.117. Khoảng cách trung vị của phiên phát lại theo nhiễu: ±2.5% -> 0.019, ±5.0% -> 0.025, ±10.0% -> 0.050, ±15.0% -> 0.075, ±20.0% -> 0.101, ±30.0% -> 0.150.

**Ngoại suy tuyến tính** FPR theo số phiên cũ (chỉ có dữ liệu tới 8): ~0.073 điểm phần trăm mỗi phiên cũ thêm, nên với 50 phiên khoảng **3.7%** (không đo được: đây là suy đoán, lịch sử trong dữ liệu chỉ ~9 lượt).

Khoảng cách người thật: phân vị 1% = **0.094**, 5% = 0.117, trung vị = 0.189.

## Bắt được bao nhiêu phiên phát lại (kẻ tấn công thích nghi: nhiễu thời gian ±n, toạ độ ±max(0.02, 0.4n) bề rộng phím)

| Nhiễu ±n | 2.5% | 5.0% | 10.0% | 15.0% | 20.0% | 30.0% |
|---|---|---|---|---|---|---|
| Ngưỡng hiện tại (0.085) | 1.00 | 1.00 | 1.00 | 0.86 | 0.09 | 0.00 |
| Ngưỡng FPR 1% (0.094) | 1.00 | 1.00 | 1.00 | 0.98 | 0.30 | 0.00 |
| Ngưỡng FPR 5% (0.117) | 1.00 | 1.00 | 1.00 | 1.00 | 0.92 | 0.03 |

## Đánh đổi theo ngưỡng (FPR đo ở 3/5/8 phiên cũ; ngoại suy tuyến tính tới 50; tỷ lệ bắt theo nhiễu)

| Ngưỡng | FPR @3 | FPR @8 | FPR @50 (ngoại suy) | bắt ±2.5% | bắt ±5.0% | bắt ±10.0% | bắt ±15.0% | bắt ±20.0% | bắt ±30.0% |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.0001 | 0.0001 | 0.1% | 1.00 | 1.00 | 0.50 | 0.00 | 0.00 | 0.00 |
| 0.06 | 0.0003 | 0.0005 | 0.3% | 1.00 | 1.00 | 0.95 | 0.05 | 0.00 | 0.00 |
| 0.07 | 0.0007 | 0.0013 | 0.7% | 1.00 | 1.00 | 1.00 | 0.29 | 0.00 | 0.00 |
| 0.085 | 0.0028 | 0.0064 | 3.7% | 1.00 | 1.00 | 1.00 | 0.86 | 0.09 | 0.00 |
| 0.094 | 0.0061 | 0.0138 | 7.8% | 1.00 | 1.00 | 1.00 | 0.98 | 0.29 | 0.00 |
