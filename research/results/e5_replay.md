# E5 — phát hiện phát lại (dữ liệu giả)

300 tài khoản giả, 10 phiên cũ mỗi tài khoản. Ngưỡng chọn để **chỉ ~1% phiên người thật mới bị coi là phát lại**; bảng báo tỷ lệ bắt phiên phát lại theo mức nhiễu của kẻ tấn công (thời gian ±n, toạ độ ±max(2, 40n) px). Persona giả, chỉ kiểm chứng phương pháp.

## PIN 4 số

| Khoảng cách | Ngưỡng | FPR | Trung vị khoảng cách người thật | nhiễu ±2.5% | nhiễu ±5.0% | nhiễu ±10.0% | nhiễu ±15.0% | nhiễu ±20.0% | nhiễu ±30.0% |
|---|---|---|---|---|---|---|---|---|---|
| rel (hiện tại) | 0.065 | 0.010 | 0.141 | 1.00 | 1.00 | 0.93 | 0.28 | 0.05 | 0.00 |
| rel+ (thêm lệch tâm) | 0.088 | 0.010 | 0.143 | 1.00 | 1.00 | 1.00 | 0.59 | 0.07 | 0.00 |
| z (theo sd của chủ) | 0.388 | 0.010 | 0.625 | 1.00 | 1.00 | 1.00 | 0.66 | 0.14 | 0.00 |

## PIN 6 số

| Khoảng cách | Ngưỡng | FPR | Trung vị khoảng cách người thật | nhiễu ±2.5% | nhiễu ±5.0% | nhiễu ±10.0% | nhiễu ±15.0% | nhiễu ±20.0% | nhiễu ±30.0% |
|---|---|---|---|---|---|---|---|---|---|
| rel (hiện tại) | 0.078 | 0.010 | 0.153 | 1.00 | 1.00 | 1.00 | 0.56 | 0.12 | 0.01 |
| rel+ (thêm lệch tâm) | 0.106 | 0.010 | 0.152 | 1.00 | 1.00 | 1.00 | 0.99 | 0.36 | 0.00 |
| z (theo sd của chủ) | 0.499 | 0.010 | 0.720 | 1.00 | 1.00 | 1.00 | 0.97 | 0.35 | 0.00 |

## FPR của bản đang dùng trong backend (rel+, ngưỡng 0.085) theo số phiên cũ đem so

| PIN | 10 phiên cũ | 50 phiên cũ | 200 phiên cũ |
|---|---|---|---|
| 4 số | 0.000 | 0.033 | 0.075 |
| 6 số | 0.000 | 0.000 | 0.000 |
