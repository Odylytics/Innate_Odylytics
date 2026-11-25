# E14 — nhận ra chủ khi gõ chuỗi số mới (mô phỏng số tài khoản; StrokePIN, người thật)

Đăng ký 3 PIN x 3 lượt khi ngồi. Kẻ gian = người khác gõ **cùng chuỗi số**, cùng tư thế. 20 đặc trưng không phụ thuộc nội dung, **không** dùng kích thước chạm. Chia theo người (58 huấn luyện / 39 kiểm thử), 3 cách chia; CI 95% bootstrap theo người, trung bình giữa các lần chia. Thấp hơn là tốt hơn.

| Kiểm thử | Bộ phát hiện | EER | FAR @ FRR 5% | Phiên chủ / kẻ gian / người (lần chia cuối) |
|---|---|---|---|---|
| cùng chuỗi số đã đăng ký | LightGBM học | 0.250 [0.218, 0.288] | 0.537 [0.442, 0.619] | 227 / 681 / 39 |
| cùng chuỗi số đã đăng ký | khoảng cách mean|z| | 0.261 [0.225, 0.296] | 0.784 [0.597, 0.933] | 227 / 681 / 39 |
| **chuỗi số mới** (6 số) | LightGBM học | 0.325 [0.302, 0.345] | 0.697 [0.645, 0.746] | 1170 / 3510 / 39 |
| **chuỗi số mới** (6 số) | khoảng cách mean|z| | 0.356 [0.331, 0.381] | 0.918 [0.871, 0.943] | 1170 / 3510 / 39 |
| **chuỗi số mới, 12 số** (gộp 2 lượt) | LightGBM học | 0.268 [0.243, 0.296] | 0.588 [0.507, 0.661] | 1170 / 3510 / 39 |
| **chuỗi số mới, 12 số** (gộp 2 lượt) | khoảng cách mean|z| | 0.332 [0.301, 0.361] | 0.918 [0.850, 0.938] | 1170 / 3510 / 39 |
| chuỗi số mới, khi **đi** | LightGBM học | 0.367 [0.337, 0.399] | 0.822 [0.751, 0.879] | 1140 / 3420 / 38 |
| chuỗi số mới, khi **đi** | khoảng cách mean|z| | 0.414 [0.382, 0.447] | 0.933 [0.910, 0.950] | 1140 / 3420 / 38 |

Đối chiếu E12b (cùng PIN, đặc trưng theo vị trí chữ số, không kích thước chạm): khoảng cách EER 0.161 / FAR 0.573; LightGBM EER 0.158 / FAR 0.375. Khác giao thức (E12b đăng ký 3 lượt của MỘT PIN), nên chỉ so hướng, không so từng số.
