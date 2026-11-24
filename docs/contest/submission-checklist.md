# Output phải nộp cho BTC

> Nguồn: thể lệ chính thức ([tóm tắt](the-le-cuoc-thi.md)). Hạn nộp **23:59:59 03/12/2026**. Sau hạn **không được sửa**, kể cả sản phẩm tại link đã nộp. Gửi câu hỏi làm rõ trước **23:59:59 27/11**: techday@mservice.com.vn.

## 4 thành phần

| # | Thành phần | Định dạng và giới hạn | Nội dung cho TIBOM | Người phụ trách | Trạng thái |
|---|---|---|---|---|---|
| 1 | **Sản phẩm** | PDF ≤ 1 trang A4. Có link dùng thử online ngay, kèm tài khoản dùng thử nếu cần đăng nhập | Link ví demo (`/`) + Swagger (`/docs`). Ghi user demo, API key demo, PIN demo `159357`, 4 bước dùng | Người 3 | Chưa |
| 2 | **Mã nguồn** | `.zip` toàn bộ code + `README` | README khai: cách chạy, công nghệ, **tài sản có sẵn, thư viện mã nguồn mở, công cụ AI đã dùng**, nguồn dữ liệu | Người 2 | Chưa |
| 3 | **Tài liệu mô tả** | Slide PDF ≤ 10 trang. Dùng luôn cho chung kết, **không được sửa** | Vấn đề, giải pháp, kiến trúc, số liệu đánh giá, demo, hạn chế | Người 3 + Người 1 (số liệu) | Chưa |
| 4 | **Video** | MP4 ≤ 3 phút (phần quá 3 phút không được xem) | Quay sản phẩm chạy thật: đăng ký nhịp → chuyển tiền chủ thật → người lạ → bot bị chặn | Người 3 | Chưa |

## Điều kiện sản phẩm

- Dùng thử được **online**, không phụ thuộc máy local của đội.
- **AI là lõi** tạo ra giá trị, không phải tính năng phụ.
- Chạy ổn định lúc nộp và **online liên tục đến hết 11/12/2026**.
- Thuộc ít nhất 1 chủ đề: Trợ lý AI · An ninh mạng · Chống lừa đảo (TIBOM: An ninh mạng + Chống lừa đảo).

## Lưu ý khi đóng `.zip`

- **Loại bỏ**: `backend/.env.deploy-key` và mọi `.env*`, `*.db`, `.venv`, `__pycache__`, `.vercel`.
- `papers/` là PDF có bản quyền của người khác: không đưa vào zip, chỉ liệt kê trong README (DOI nằm ở [`../research/paper-report.md`](../research/paper-report.md)).
- Thương hiệu: không dùng logo hay tên MoMo trong sản phẩm, slide, video.
- Dữ liệu cá nhân phải ghi nguồn và căn cứ sử dụng (phiếu đồng ý của người tham gia thu dữ liệu).

## Bị loại nếu

Nộp sản phẩm có từ trước · người ngoài đội tham gia · chia sẻ code giữa các đội · sửa sau hạn · giấu tài sản có sẵn · dữ liệu cá nhân không nguồn.

## Mốc

| Ngày | Việc |
|---|---|
| 27/11 | Đăng ký thi (trưởng nhóm, techday.momo.vn) + gửi câu hỏi BTC |
| 03/12 | Nộp đủ 4 thành phần |
| 08/12 | Công bố top 5 |
| 11/12 | Chung kết tại TP.HCM; sản phẩm phải còn online |
