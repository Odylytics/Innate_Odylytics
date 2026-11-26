# E30 — số lượt đăng ký và phân bố lỗi theo nạn nhân (StrokePIN, ngồi, khoảng cách của backend)

k=1 không tính được độ lệch chuẩn; k=5 không còn lượt kiểm thử (tối đa 5 lượt ngồi mỗi người–PIN). CI 95% bootstrap theo người. FAR@FRR5% dùng ngưỡng chung; cột Gini và 'nạn nhân FAR>90%' là theo từng nạn nhân (người chủ tài khoản).

| k | EER | FAR@FRR5% | Gini FAR theo nạn nhân | nạn nhân FAR > 90% | trung vị FAR nạn nhân |
|---|---|---|---|---|---|
| 2 | 0.167 [0.156, 0.178] | 0.857 [0.661, 0.923] | 0.02 | 7/97 | 0.86 |
| 3 | 0.146 [0.138, 0.155] | 0.503 [0.421, 0.627] | 0.10 | 0/97 | 0.52 |
| 4 | 0.138 [0.128, 0.150] | 0.429 [0.360, 0.534] | 0.13 | 0/97 | 0.44 |
