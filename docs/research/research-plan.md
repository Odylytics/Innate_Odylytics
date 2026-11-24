# Kế hoạch nghiên cứu công nghệ

> Lập 24/11/2026. Mục tiêu: trả lời các câu hỏi kỹ thuật có thể làm sản phẩm hỏng hoặc bị giám khảo bắt bẻ, theo thứ tự rủi ro. Kết quả ghi vào [`tech-notes.md`](tech-notes.md).

## Phạm vi (cập nhật 24/11)

Nhóm làm web/demo riêng sau. Phần ví demo (`backend/app/static/wallet.html`) và việc deploy API (`nhip-api`) **ngừng phát triển**, không xoá code. R6 (hạ tầng) và R8 (dashboard) tạm hoãn. Trọng tâm là lõi AI: xem [`ai-research.md`](ai-research.md) (bài A người/máy, bài B chủ tài khoản, bài C hợp nhất và giải thích; thí nghiệm E1–E7).

## Nguyên tắc

- Câu hỏi nào mà **câu trả lời đổi thiết kế** thì làm trước.
- Ưu tiên thí nghiệm trên điện thoại demo hơn đọc thêm. Nguồn bên ngoài chỉ để định hướng.
- Mỗi câu hỏi có đầu ra kiểm chứng được và hạn.

## Câu hỏi nghiên cứu

| # | Câu hỏi | Vì sao quan trọng | Cách làm | Đầu ra | Hạn |
|---|---|---|---|---|---|
| R1 | SDK có **nhìn thấy khác biệt** giữa chạm thật và chạm bơm bởi `adb input` / `dispatchGesture` không? (w/h, pointerType, độ phân giải thời gian, `getCoalescedEvents`, số điểm giữa down và up) | Nếu khác biệt rõ thì "người hay máy" có tín hiệu cứng ngoài thống kê. Nếu không thì chỉ còn thống kê | Ghi sự kiện trên ví demo với 3 nguồn: ngón tay, `adb input tap/swipe`, app `dispatchGesture` tự viết. So sánh từng trường | Bảng trường nào khác, kèm số liệu | 28/11 |
| R2 | Trường hình học chạm (`width`/`height`) có dùng được trên máy demo không? Trả về 1 hay 0 hay giá trị thật? | Đặc trưng kích thước chạm là một trong những tín hiệu "chủ" mạnh (Zheng 2014). Máy không đo thì trả 1 | Đo trên Android Chrome và iOS Safari thật | Quyết định giữ hay bỏ `tap_w/h_*` | 26/11 |
| R3 | Với ~25 người, mô hình học (LightGBM/RF) có hơn luật + Manhattan không? Cần mấy lượt đăng ký? | "AI là lõi" phải đúng ở bản nộp, nhưng dữ liệu ít | Thu dữ liệu, đánh giá theo FETA: tách theo thời gian, một máy, leave-users-out | Bảng FAR@FRR 5%, EER, DET, phân bố theo người | 01/12 |
| R4 | Cách phát hiện phát lại (chiến thuật 3) rẻ và đủ chắc? | Baseline hiện bắt 0% chiến thuật 3 | Khoảng cách tới phiên cũ của cùng user trong không gian đặc trưng; ngưỡng từ dữ liệu người thật | Kiểm tra trong `/score` + test | 29/11 |
| R5 | Kẻ tấn công thích nghi (ActReal 2026) làm gì và Innate còn lại gì? Thêm `devicemotion`/IMU có đáng không? | Paper báo 71–77% thành công trước bộ phát hiện chạm + IMU | Đọc kỹ ActReal; thử `devicemotion` trên web demo; dựng chiến thuật 5 nếu kịp | Mục "hạn chế" trong slide + quyết định IMU | 30/11 |
| R6 | Hạ tầng: Vercel Python + Neon có đủ ổn định, độ trễ < 200 ms, không "ngủ đông" gây lỗi lúc chấm? Giới hạn gói free? | Sản phẩm phải online đến 11/12 | Đo cold start, 100 yêu cầu liên tiếp, kiểm tra giới hạn gói, bật giám sát `/health` | Số liệu độ trễ + kế hoạch dự phòng | 02/12 |
| R7 | Pháp lý thu dữ liệu: Luật BVDLCN 2025 + NĐ 356/2025 xếp sinh trắc là nhạy cảm | Điều kiện loại: dữ liệu cá nhân không nguồn và căn cứ | Soạn phiếu đồng ý, chỉ lưu thời gian + toạ độ, ghi README | Phiếu đồng ý + đoạn README | 27/11 |
| R8 | (Tuỳ chọn) Dashboard + tóm tắt LLM | Góc "Future Workspace" | Chỉ làm sau khi R1–R4 xong | Dashboard | sau 01/12 |

## Thứ tự làm

1. R2 và R7 (rẻ, chặn thu dữ liệu) → R1 (đổi thiết kế) → R4 (sửa rẻ, lấy lại điểm) → R3 (cần dữ liệu) → R5 → R6.
2. Mốc quyết định: 17:00 ngày thu dữ liệu đầu tiên. Nếu mô hình "chủ tài khoản" không tách nổi 3 người trong đội thì pitch tập trung vào "người hay máy".

## Đã làm (24/11)

- Đối chiếu số liệu kế hoạch với 7 paper gốc và đọc phần tóm tắt các paper còn lại: [`../plan/mo-ta-du-an-va-kiem-chung.md`](../plan/mo-ta-du-an-va-kiem-chung.md).
- Tìm kiếm ban đầu cho R1, R2: xem [`tech-notes.md`](tech-notes.md). **Chưa có kết luận** vì tài liệu công khai không nói về phía phòng thủ, cần thí nghiệm.
