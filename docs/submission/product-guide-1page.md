# Innate — Hướng dẫn dùng thử (≤ 1 trang A4, bản NHÁP)

> **Chưa dùng được để nộp:** cần điền URL web demo và key (nếu cần). Khi xong, xuất PDF 1 trang A4 (thể lệ: chứa **link sản phẩm** và **tài khoản dùng thử**). Không đưa khoá bí mật vào file này: key SDK nằm sẵn trong bản build web, giám khảo không cần nhập.

**Innate** — lớp kiểm chứng con người cho ví điện tử. *PIN có thể bị đánh cắp, thói quen chạm bẩm sinh thì rất khó.*

| | |
|---|---|
| **Trang demo** | `[TODO: URL web, mở được ngay, không cần đăng nhập]` (landing `#/`, ví demo `#/demo`, kịch bản `#/demo?story=1`) |
| **API + Swagger** | https://nhip-api-taupe.vercel.app/docs (xem được ngay; thử gọi cần key SDK `[TODO]`) |
| **PIN demo** | `159357` (6 số) |

## 3 cách xem (khoảng 3 phút)
1. **Xem kịch bản:** mở `#/demo?story=1`. Tám bước tự chạy: chủ ví đăng ký nhịp, chuyển tiền được qua (`allow`); người biết PIN bị yêu cầu xác thực thêm (`step_up`) kèm lý do; mã độc tự bấm bị giữ lệnh (`hold`).
2. **Tự thử ví:** mở `#/demo`, nhập PIN `1593` ba lần để đăng ký nhịp, rồi chuyển tiền (chọn người nhận đã lưu hoặc nhập số tài khoản và chọn ngân hàng). Đưa máy cho người khác nhập cùng PIN để xem kết quả khác đi.
3. **Mã độc giả lập:** trong bảng điều khiển kẻ tấn công, bấm "mã độc" (điền thẳng số tài khoản rồi bấm PIN) hoặc "người khác" để xem Innate chấm điểm ngay trên API thật.

## Đọc kết quả
`allow` cho qua · `step_up` cần xác thực thêm (khuôn mặt, OTP) · `hold` giữ lệnh và báo người dùng, kèm lý do bằng tiếng Việt. Innate chỉ **đề xuất**, không tự khoá tài khoản.

## Lưu ý
Giao diện ví và các nhân vật là hư cấu, không phải ứng dụng của bất kỳ ví nào. Phiên của mã độc và nhân vật được sinh trong trình duyệt rồi gửi lên API chấm như phiên thật. Innate là **tín hiệu rủi ro**, không thay PIN/OTP/khuôn mặt. Chỉ lưu thời gian, toạ độ, loại sự kiện; không lưu PIN hay nội dung. Mã nguồn và số liệu: xem gói `.zip`. Giấy phép: CC BY-NC-SA 4.0.
