# Innate hoạt động thế nào (giải thích cho giám khảo và cho đội)

> Chốt ngày 24/11/2026. Dùng làm nền cho slide, video và phần trả lời giám khảo. Số liệu lấy từ E9/E4b (dữ liệu người thật công khai, chưa phải dữ liệu của đội); xem [`../research/ai-research.md`](../research/ai-research.md).

## Câu chốt

> **Giống Face ID ở quy trình đăng ký và đối chiếu, nhưng là tín hiệu rủi ro, không phải chìa khoá.**
> PIN có thể bị đánh cắp, thói quen chạm bẩm sinh thì rất khó. *(Nói "rất khó", không nói "không thể": xem [`pitch-story.md`](pitch-story.md).)*

## Luồng

```
Lần đầu (setup)      nhập PIN / chuyển tiền thử 3–5 lần  →  lưu "mẫu thói quen" của bạn
Mỗi lần dùng sau     nhập như bình thường  →  so với mẫu  →  điểm khớp
                                              + kiểm tra "người hay máy"
                     →  cho qua / yêu cầu xác thực thêm (khuôn mặt, OTP) / giữ lệnh
```

## Hai việc "huấn luyện" khác nhau (hay bị nhầm)

| | Huấn luyện chung | Đăng ký của từng người dùng |
|---|---|---|
| Khi nào | Một lần, trước khi ra sản phẩm | Mỗi người, lần đầu dùng |
| Dữ liệu | Nhiều người (StrokePIN, rồi dữ liệu của đội) | 3–5 lần nhập của chính người đó |
| Học gì | "Người nhập thường thế nào", "bot trông thế nào", phân bố dân số (prior) | **Không huấn luyện mô hình riêng**: chỉ lưu trung bình và độ dao động từng đặc trưng |

Vì người dùng cuối chỉ có 3–5 mẫu, đây là bài toán **ít mẫu (few-shot)**. Kiến thức dân số (prior) giúp bù cho việc ít mẫu: E2 giảm tỷ lệ kẻ gian lọt ở điểm vận hành FRR 5% khoảng 7–16 điểm phần trăm.

## Hai câu hỏi, không phải một

| Câu hỏi | Cần đăng ký? | Bắt được ai | Độ chắc (số đo hiện có) |
|---|---|---|---|
| **Người hay máy?** | **Không**: có tác dụng từ lần dùng đầu | Mã độc, script, `adb` (kịch bản A) | Bot ngây thơ: bắt 100% (E4b). Bot giống người: 5–73% |
| **Có phải chủ?** | **Có**: cần mẫu | Người quen, kẻ trộm biết PIN (kịch bản B) | EER 16–20% (E9) |

## Không giống vân tay hay khuôn mặt

| | Vân tay, khuôn mặt | Thói quen nhập PIN |
|---|---|---|
| Bản chất | Đặc điểm cơ thể, gần như cố định | Hành vi: đổi theo tư thế, tâm trạng, thời gian |
| Độ chính xác | Rất cao | **EER 16–20%**; ở FRR 5% thì 57–73% kẻ gian biết PIN vẫn lọt (E9) |
| Đổi điều kiện | Ổn định | **Ngồi → đi: gần như mất tín hiệu** (EER 32–40%) |
| Mẫu lưu ở đâu | Trong chip bảo mật trên máy | **Trên máy chủ** → phải bảo vệ như dữ liệu sinh trắc nhạy cảm |

Hệ quả: Innate **không thay** mật khẩu hay Face ID. Điểm khớp thấp thì **không chặn cứng**, mà yêu cầu xác thực mạnh hơn. Đó là lý do có `step_up`.

## Cách đăng ký nên làm (khác Face ID một chút)

- **Nhiều tư thế** (ngồi, đứng, đi) và **nhiều lần ngồi khác nhau**. E9 cho thấy chỉ đăng ký khi ngồi là không đủ; Buschek 2015 cho thấy đăng ký trong một phiên cho số lạc quan gấp đôi.
- Mẫu **tự cập nhật chậm** theo thời gian, có **trần độ trôi** để kẻ gian không "dạy dần" được (E7: không có trần thì kẻ gian được chấp nhận 100% và chủ bị khoá ngoài).
- Chỉ lưu **thời gian, toạ độ, loại sự kiện**, không lưu nội dung PIN, số tiền, nội dung chuyển khoản.
- Đăng ký cả các **ô nhập ngoài PIN** (số tiền, người nhận, ghi chú) nếu muốn dùng nhịp gõ của chúng làm tín hiệu chủ.

## Cách nói với giám khảo (an toàn)

| Nói | Không nói |
|---|---|
| "Giống Face ID ở cách đăng ký và đối chiếu, nhưng là **một tín hiệu rủi ro**" | "Thay thế Face ID / PIN", "chính xác như vân tay" |
| "Bắt chắc bot ngây thơ ngay từ lần đầu; phần nhận chủ cần vài lần đăng ký" | "Bắt mọi mã độc" |
| "Điểm thấp thì hỏi thêm, không chặn cứng" | "Tự khoá tài khoản" |
| Số đo thật: EER 16–20%, nói trước khi bị hỏi | Hứa EER vài phần trăm như trong paper |
