# E3 — hiệu chỉnh điểm chủ (StrokePIN, PIN 6 số, đăng ký 3 lượt ngồi)

Fit Platt trên nửa A (18634 phiên): score = sigmoid(-1.216·d + 1.390). Kiểm trên nửa B (18788 phiên, người khác hẳn).

| Ánh xạ | Chủ có score ≥ 0,5 | Kẻ gian biết PIN có score ≥ 0,5 |
|---|---|---|
| hiện tại (d=2→0,5) | 0.96 | 0.84 |
| Platt đã fit (cân bằng lớp) | 0.90 | 0.27 |

Ngưỡng d cho FRR 5% (nửa B): d=1.37; FAR tại đó = 0.50. Trung vị d: chủ 0.73, kẻ gian 1.37.

Kết luận: xem số trên. Platt chỉ dời ngưỡng, không tạo thêm độ tách; FAR@FRR5% vẫn quyết bởi đặc trưng (E9/E12b).
