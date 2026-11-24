# Dữ liệu để thử nghiệm

> Kiểm tra link ngày 24/11/2026 (HTTP status thật khi gọi từ máy làm việc). **Giấy phép chưa được xác nhận cho bộ nào**: đọc điều khoản trên trang gốc và ghi vào README trước khi dùng cho bài nộp.

| Bộ dữ liệu | Dùng cho | Link | Trạng thái link | Ghi chú |
|---|---|---|---|---|
| **CMU DSL-StrongPassword** (51 người × 400 lần gõ một mật khẩu, 31 đặc trưng thời gian) | Thí nghiệm few-shot bài B (đã chạy, E1/E2 proxy) | Trang: https://www.cs.cmu.edu/~keystroke/ · CSV: https://www.cs.cmu.edu/~keystroke/DSL-StrongPasswordData.csv | 200, tải trực tiếp 4,6 MB | Trang không nêu chữ "license"; trích dẫn Killourhy & Maxion 2009. Bàn phím máy tính, không phải PIN điện thoại |
| **HuMIdb** (600 người, 14 cảm biến, benchmark bot BeCAPTCHA) | Bài A người/máy | https://github.com/BiDAlab/HuMIdb | 200 | Truy cập cần ký thỏa thuận cấp phép rồi gửi email cho nhóm tác giả, nhận tài khoản tải (~5 GB). Quy trình này tôi chỉ thấy qua bản mirror, xác nhận ở trang gốc. **Cần gửi sớm** |
| **Aalto typing37k** (37.370 người gõ trên điện thoại) | Ước lượng phương sai dân số; kiểm tra sơ bộ | https://userinterfaces.aalto.fi/typing37k/ | 200 | Dữ liệu SQL **4,7 GB nén, 43,4 GB giải nén** (theo trang). Nặng; cân nhắc có cần không |
| **Touchalytics** (41 người, vuốt/cuộn) | Đặc trưng vuốt | https://www.mariofrank.net/touchalytics/ | 200 (chỉ xác nhận trang, chưa xem link dữ liệu) | |
| **BB-MAS** (117 người, gõ/vuốt/dáng đi trên nhiều thiết bị) | So sánh phụ | DOI https://doi.org/10.21227/rpaz-0h66 (IEEE DataPort) | 403 khi gọi bằng curl; cần mở bằng trình duyệt, có thể cần tài khoản | |
| HMOG, KVC, BehavePassDB, MobileTouchDB, FETA | So sánh phụ | Chưa có link xác nhận | Các địa chỉ tôi đoán đều 404 hoặc không truy cập được, nên **không liệt kê** | Tìm trên trang arXiv/bài báo gốc trong `papers/` |

Dữ liệu tải về đặt ở `research/data/` (đã `.gitignore`, không commit).
