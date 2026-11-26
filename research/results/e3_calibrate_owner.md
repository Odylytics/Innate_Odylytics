# E3 — hiệu chỉnh điểm chủ (StrokePIN, PIN 6 số, đăng ký 3 lượt ngồi)

Fit Platt trên nửa A (18634 phiên): score = sigmoid(-1.216·d + 1.390). Kiểm trên nửa B (18788 phiên, người khác hẳn).

| Ánh xạ | Chủ có score ≥ 0,5 | Kẻ gian biết PIN có score ≥ 0,5 |
|---|---|---|
| hiện tại (d=2→0,5) | 0.96 | 0.84 |
| Platt đã fit (cân bằng lớp) | 0.90 | 0.27 |

Ngưỡng d cho FRR 5% (nửa B): d=1.37; FAR tại đó = 0.50. Trung vị d: chủ 0.73, kẻ gian 1.37.

Kết luận: xem số trên. Platt chỉ dời ngưỡng, không tạo thêm độ tách; FAR@FRR5% vẫn quyết bởi đặc trưng (E9/E12b).

## Đã nối vào backend chưa? Thử (26/11): có công tắc, KHÔNG bật mặc định

`owner.py` có `NHIP_OWNER_MAP=platt` (mặc định `legacy`). Chạy lại E24 với Platt (`e24_platt_map.md`):
- Các cột **có mô hình học không đổi**: với PIN 6 số, điểm chủ lấy từ `owner_model` (LightGBM), Platt chỉ đổi đường khoảng cách dự phòng (PIN 4 số, tắt mô hình, thiếu đặc trưng).
- Đường dự phòng, người nhận quen: kẻ biết PIN qua 90% -> 79%, chủ ngồi 96% -> 94%. Có lợi nhẹ.
- Đường dự phòng, **người nhận mới**: chủ ngồi allow 92% -> 2%, kẻ biết PIN 62% -> 0%. Điểm chủ tối đa của Platt chỉ ~0,63 nên rủi ro hợp nhất của chủ luôn >= 0,13, cộng 0,15 người nhận mới vượt A=0,25: mọi người đều `step_up`.
- `UPDATE_MIN_OWNER = 0.8` cũng không bao giờ đạt dưới Platt, nên mẫu chuẩn ngừng cập nhật (test `test_full_flow` hỏng khi bật).

Muốn bật Platt cần dời A/B và `UPDATE_MIN_OWNER` cùng lúc rồi đo lại E24/E25. Việc đó chỉ đáng làm khi dùng đường dự phòng thật, và nên làm trên dữ liệu của đội thay vì StrokePIN.
