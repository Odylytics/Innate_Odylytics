# E14 — nhận ra chủ khi gõ chuỗi số mới (mô phỏng số tài khoản; StrokePIN, người thật)

Đăng ký 3 PIN x 3 lượt. Kẻ gian = người khác gõ **cùng chuỗi số**. 20 đặc trưng không phụ thuộc nội dung, **không** dùng kích thước chạm. Chia theo người (58 huấn luyện / 39 kiểm thử), 3 cách chia; CI 95% bootstrap theo người, trung bình giữa các lần chia. Thấp hơn là tốt hơn.

| Kiểm thử | Bộ phát hiện | EER | FAR @ FRR 5% | Phiên chủ / kẻ gian / người (lần chia cuối) |
|---|---|---|---|---|
| cùng chuỗi số đã đăng ký | LightGBM học | 0.245 [0.204, 0.283] | 0.500 [0.392, 0.602] | 225 / 675 / 39 |
| cùng chuỗi số đã đăng ký | khoảng cách mean|z| | 0.264 [0.231, 0.301] | 0.737 [0.565, 0.909] | 225 / 675 / 39 |
| **chuỗi số mới** (6 số) | LightGBM học | 0.328 [0.303, 0.357] | 0.697 [0.640, 0.748] | 1170 / 3510 / 39 |
| **chuỗi số mới** (6 số) | khoảng cách mean|z| | 0.360 [0.336, 0.385] | 0.917 [0.863, 0.944] | 1170 / 3510 / 39 |
| **chuỗi số mới, 12 số** (gộp 2 lượt) | LightGBM học | 0.284 [0.259, 0.316] | 0.607 [0.531, 0.680] | 1170 / 3510 / 39 |
| **chuỗi số mới, 12 số** (gộp 2 lượt) | khoảng cách mean|z| | 0.335 [0.302, 0.369] | 0.909 [0.863, 0.942] | 1170 / 3510 / 39 |

Đối chiếu E12b (cùng PIN, đặc trưng theo vị trí chữ số, không kích thước chạm): khoảng cách EER 0.161 / FAR 0.573; LightGBM EER 0.158 / FAR 0.375. Khác giao thức (E12b đăng ký 3 lượt của MỘT PIN), nên chỉ so hướng, không so từng số.
