# E7 — tấn công đầu độc mẫu chuẩn (dữ liệu giả)

100 cặp (chủ, kẻ gian), kẻ tấn công tiêm phiên sát ngưỡng cập nhật (owner >= 0.8). 'Chấp nhận' = owner >= 0.5. Persona giả, chỉ kiểm chứng phương pháp.

## Tỷ lệ phiên THẬT của kẻ gian được chấp nhận sau n lần tiêm (càng thấp càng tốt)

| Phòng thủ | n=0 | n=10 | n=25 | n=50 | n=100 | n=200 |
|---|---|---|---|---|---|---|
| none | 0.56 | 0.96 | 1.00 | 1.00 | 1.00 | 1.00 |
| cap1.0sd | 0.56 | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 |
| cap0.5sd | 0.56 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 |
| cap0.25sd | 0.56 | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 |
| freeze | 0.56 | 0.77 | 0.77 | 0.77 | 0.77 | 0.77 |

## Tỷ lệ phiên mới của chủ được chấp nhận sau n lần tiêm (càng cao càng tốt)

| Phòng thủ | n=0 | n=10 | n=25 | n=50 | n=100 | n=200 |
|---|---|---|---|---|---|---|
| none | 1.00 | 1.00 | 0.68 | 0.59 | 0.58 | 0.58 |
| cap1.0sd | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| cap0.5sd | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| cap0.25sd | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| freeze | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

## Trôi trung bình của mẫu chuẩn (đơn vị sd) sau n lần tiêm

| Phòng thủ | n=0 | n=10 | n=25 | n=50 | n=100 | n=200 |
|---|---|---|---|---|---|---|
| none | 0.00 | 1.05 | 1.66 | 1.82 | 1.83 | 1.83 |
| cap1.0sd | 0.00 | 0.64 | 0.72 | 0.73 | 0.73 | 0.73 |
| cap0.5sd | 0.00 | 0.38 | 0.40 | 0.41 | 0.41 | 0.41 |
| cap0.25sd | 0.00 | 0.21 | 0.21 | 0.22 | 0.22 | 0.22 |
| freeze | 0.00 | 0.42 | 0.42 | 0.42 | 0.42 | 0.42 |

## Cái giá: chủ thật trôi chậm (thời gian giữ/cách phím tăng dần trong 100 phiên) — tỷ lệ phiên mới của chủ được chấp nhận

| Phòng thủ | +15% | +30% | +50% |
|---|---|---|---|
| none | 1.00 | 1.00 | 1.00 |
| cap1.0sd | 1.00 | 1.00 | 1.00 |
| cap0.5sd | 1.00 | 1.00 | 0.99 |
| cap0.25sd | 1.00 | 1.00 | 0.98 |
| freeze | 1.00 | 1.00 | 1.00 |

Cùng kịch bản, nhưng đếm là chấp nhận khi owner >= 0.8 (ngưỡng cập nhật; nhạy hơn với việc mẫu không theo kịp chủ):

| Phòng thủ | +15% | +30% | +50% |
|---|---|---|---|
| none | 1.00 | 1.00 | 1.00 |
| cap1.0sd | 1.00 | 0.98 | 0.67 |
| cap0.5sd | 1.00 | 0.95 | 0.41 |
| cap0.25sd | 1.00 | 0.90 | 0.28 |
| freeze | 1.00 | 0.99 | 0.68 |
