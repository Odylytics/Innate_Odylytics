# Innate — Hướng dẫn dùng thử (≤ 1 trang A4, bản NHÁP)

> **Chưa dùng được để nộp:** cần điền URL và tài khoản demo thật. Khi xong, xuất PDF 1 trang A4 (thể lệ: chứa **link sản phẩm** và **tài khoản dùng thử**). Không đưa API key thật vào file này trước khi quyết định cách cấp key cho giám khảo.

**Innate** — lớp kiểm chứng con người cho ví điện tử. *PIN có thể bị đánh cắp, thói quen chạm bẩm sinh thì rất khó.*

| | |
|---|---|
| **Trang demo** | `[TODO: URL]` |
| **API + Swagger** | `[TODO: URL]/docs` (bấm *Authorize*, nhập key demo) |
| **Tài khoản / key demo** | `[TODO]` |
| **PIN demo** | `159357` |

## 4 bước dùng thử (khoảng 3 phút)
1. **Đăng ký nhịp:** mở trang demo → *Đăng ký nhịp thao tác* → nhập PIN `159357` ba đến năm lần, cầm máy như bình thường.
2. **Chuyển tiền bằng chính bạn:** nhập số người nhận và số tiền → nhập PIN → kết quả **allow** (qua).
3. **Người thứ hai biết PIN:** đưa máy cho người khác nhập cùng PIN → kết quả **step_up** (yêu cầu xác thực thêm) kèm lý do ("nhịp PIN chậm hơn…, chạm lệch…").
4. **Bot:** chạy bộ giả lập `[TODO: cách chạy hoặc nút trên trang]` → kết quả **hold** (giữ lệnh), lý do "nhịp đều bất thường".

## Đọc kết quả
`allow` cho qua · `step_up` cần xác thực thêm (khuôn mặt, OTP) · `hold` giữ lệnh và báo người dùng. Innate chỉ **đề xuất**, không tự khoá tài khoản.

## Lưu ý
Giao diện ví là minh hoạ, không phải ứng dụng của bất kỳ ví nào. Innate là **tín hiệu rủi ro**, không thay PIN/OTP/khuôn mặt. Chỉ lưu thời gian, toạ độ, loại sự kiện; không lưu PIN hay nội dung. Mã nguồn và số liệu: xem gói `.zip`.
