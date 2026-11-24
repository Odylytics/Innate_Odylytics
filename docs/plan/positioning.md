# Innate là gì trong bức tranh an ninh mạng

> Chốt ngày 24/11/2026. Đây là tài liệu **định vị** (Innate nằm ở đâu, làm gì, không làm gì). Giải thích cơ chế: [`how-it-works.md`](how-it-works.md). Câu chuyện pitch: [`pitch-story.md`](pitch-story.md).

## Một câu

> **Innate là lớp kiểm chứng con người (human verification layer) chạy ngầm ở bước xác nhận giao dịch: AI so khớp thao tác hiện tại với thói quen đã đăng ký và với hình mẫu của người thật, để trả lời "đây là người hay máy, và có phải chủ không", trước khi tiền rời đi.**

Nó là một lớp **bảo mật hành vi thụ động** (passive behavioral security), không thay thế bất kỳ lớp nào có sẵn, mà bổ sung lớp mà các lớp kia không có: **bằng chứng rằng người đang thao tác là con người, và là đúng chủ**.

## Vì sao cần lớp này

Mọi lớp xác thực truyền thống kiểm tra thứ **có thể bị lấy đi**: PIN (nhìn lén), OTP (đọc được), thiết bị (chiếm được). Mã độc Trợ năng (kỹ thuật được MITRE ATT&CK for Mobile xếp vào **Input Injection, T1516**) khiến mọi thứ trông đúng: đúng app, đúng PIN, đúng thiết bị, đúng phiên đang mở. Câu hỏi còn lại mà không lớp nào trả lời: **ai hoặc cái gì đang chạm vào màn hình?**

## Innate nằm ở đâu trong chồng bảo mật

```
┌─ 1. Toàn vẹn thiết bị/ứng dụng  (attestation, chống root/hook, quét mã độc)   "máy này có sạch không?"
├─ 2. Xác thực                     (PIN, OTP, khuôn mặt, vân tay)                 "người này biết/có/là gì?"
├─ 3. ★ INNATE: kiểm chứng con người (hành vi chạm/gõ, chạy ngầm)               "thao tác này do NGƯỜI hay MÁY?
│        AI so khớp với thói quen đã đăng ký + hình mẫu người thật                   Có phải CHỦ không?"
├─ 4. Rủi ro giao dịch             (số tiền, người nhận, lịch sử, mạng lưới)       "giao dịch này có bất thường không?"
└─ 5. Vận hành & phản hồi          (dashboard, xác thực thêm, giữ lệnh, điều tra)
```

- **Bổ sung, không thay thế.** Lớp 1 (attestation) trả lời "máy có bị can thiệp không"; Innate trả lời "người trên máy có phải người thật và đúng chủ không". Mã độc đủ tinh vi có thể qua lớp 1; thao tác của nó vẫn để lại dấu vết hành vi. Ngược lại, kẻ đứng cạnh biết PIN thì qua mọi lớp thiết bị, nhưng không có thói quen của chủ.
- **Phía API:** đối tác (ví, ngân hàng) nhúng SDK thu tín hiệu và gọi một API chấm điểm. Đầu ra là điểm và hành động đề xuất, không phải quyết định cuối: đối tác giữ quyền quyết định.

## Tên gọi trong ngành (để giám khảo định vị nhanh)

Innate thuộc nhóm mà tài liệu chuyên ngành gọi là **behavioral biometrics / continuous authentication / risk-based authentication (RBA)**, kết hợp **human-vs-bot detection** (phát hiện tự động hoá). Nói theo ngôn ngữ sản phẩm: *kiểm chứng con người ở bước xác nhận*. Lưu ý: "HUMAN Security" là tên một công ty; **đừng dùng cụm đó làm tên hay khẩu hiệu**, chỉ dùng "kiểm chứng con người" / "human verification".

## AI bên dưới làm gì: so khớp (matching)

Hai phép so khớp, đều là **xác minh 1:1** (so với một mẫu cụ thể), không phải nhận diện 1:N:

| Phép so khớp | So cái gì với cái gì | Cần đăng ký? | Kết quả |
|---|---|---|---|
| **Người hay máy** | Thao tác hiện tại ↔ hình mẫu "người thật" học từ dữ liệu nhiều người (và bot) | Không | Điểm "là người" |
| **Có phải chủ** | Thao tác hiện tại ↔ **mẫu thói quen của chính chủ** (3–5 lần đăng ký) | Có | Điểm khớp chủ |
| **Phát lại** | Thao tác hiện tại ↔ **các phiên cũ của chính tài khoản** (trùng bất thường) | Không | Cờ "phát lại" |

Hợp nhất: điểm người/máy + điểm khớp chủ + ngữ cảnh (người nhận mới, số tiền bất thường) → `allow` / `step_up` / `hold` + lý do tiếng Việt. Chi tiết kỹ thuật và số đo: [`../research/ai-research.md`](../research/ai-research.md).

## Hai kịch bản bị chặn

| | A. Mã độc điều khiển từ xa | B. Người cầm máy biết PIN |
|---|---|---|
| Vì sao lọt các lớp khác | PIN/OTP/thiết bị đều đúng | Như trên |
| Innate thấy gì | Thao tác **không phải ngón tay người**: nhịp quá đều, đúng tâm nút, văn bản đặt thẳng không qua phím, phát lại | Thao tác của người nhưng **không khớp thói quen chủ** |
| Mức tin cậy hiện có | Bot ngây thơ: bắt 100%. Bot giống người: yếu (xem giới hạn) | Yếu hơn: EER 16–20% |

## Innate KHÔNG làm gì

- **Không phát hiện mã độc** (không quét app, không đọc nhật ký hệ thống); chỉ thấy **hệ quả** của nó lên cách chạm.
- **Không thay PIN, OTP, khuôn mặt**: điểm thấp thì **hỏi thêm**, không chặn cứng, không tự khoá tài khoản.
- **Không đọc nội dung**: chỉ thời gian, toạ độ, loại sự kiện, số ký tự; không lưu PIN, số tiền, nội dung chuyển khoản.
- **Không phát hiện lừa đảo bằng nội dung** (tin nhắn, cuộc gọi); đó là việc của lớp khác.

## Giới hạn phải nói thẳng (dữ liệu người thật công khai; chưa phải dữ liệu của đội)

- Điểm "chủ": **EER 16–20%; ở FRR 5% còn ~50% kẻ gian biết PIN lọt** (E9, E10b); đổi tư thế gần như mất tín hiệu. Đây là **tín hiệu rủi ro, không phải cổng xác thực**.
- Bot giống người (chiến thuật phát lại, lấy mẫu dân số) bị bắt yếu; kẻ tấn công thích nghi cấp hệ thống có thể qua mặt cả chạm lẫn cảm biến (Wang 2026, ActReal: 71–77%).
- Web SDK không thấy được văn bản đặt thẳng không qua phím; cần SDK native.
- Chưa có bot thật (`adb`, `dispatchGesture`) và chưa có dữ liệu của đội trong bất kỳ số đo nào.

## Cách nói với giám khảo

| Nói | Không nói |
|---|---|
| "Một **lớp kiểm chứng con người** chạy ngầm, bổ sung cho PIN/OTP/khuôn mặt" | "Thay thế xác thực", "chống được mọi mã độc" |
| "AI **so khớp** thao tác với thói quen chủ và với hình mẫu người thật" | "AI nhận ra bạn là ai" (nhận diện 1:N) |
| "Bắt chắc bot ngây thơ; phần nhận chủ là tín hiệu rủi ro, điểm thấp thì hỏi thêm" | "Chính xác như vân tay" |
| Nêu số đo thật và giới hạn trước khi bị hỏi | Hứa EER vài phần trăm như trong paper |
