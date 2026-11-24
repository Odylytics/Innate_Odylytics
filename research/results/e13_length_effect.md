# E13 — giả thuyết "Innate Challenge": nhiều ký tự hơn thì nhận chủ và bắt bot tốt hơn?

Người thật gõ câu trên điện thoại (Aalto), chỉ thời gian. Mỗi câu cắt ở n phím đầu (n = 6 tương đương độ dài PIN 6 số). Mọi n dùng cùng các câu. **Không so được số tuyệt đối với StrokePIN** (khác dữ liệu, khác phép đo: ở đây không có thời gian giữ phím và toạ độ).

## (1) Xác minh chủ theo số phím

| Số phím n | EER | FAR @ FRR 5% |
|---|---|---|
| 6 | 0.364 [0.355, 0.371] | 0.807 [0.787, 0.822] |
| 10 | 0.337 [0.330, 0.345] | 0.733 [0.714, 0.761] |
| 20 | 0.279 [0.272, 0.289] | 0.591 [0.566, 0.616] |
| 30 | 0.245 [0.238, 0.254] | 0.489 [0.472, 0.511] |

## (2) Phát hiện bot trên câu gõ theo số phím (AUC; LightGBM đã thấy loại bot, chia theo người)

| Số phím n | CT2 gõ đều | CT4 lấy mẫu dân số |
|---|---|---|
| 6 | 0.915 | 0.719 |
| 10 | 0.969 | 0.764 |
| 20 | 0.996 | 0.848 |
| 30 | 0.995 | 0.891 |
