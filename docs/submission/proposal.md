# Innate — Đề xuất ý tưởng

> MoMo Tech Contest 2026 · Chủ đề: **An ninh mạng + Chống lừa đảo** · Đề bài: *Imagine the Future Workspace — Human Centered. AI Powered.*
> Bản nháp 24/11/2026. Mục `[TODO]` cần đội điền. Mọi con số lấy từ [`../research/ai-research.md`](../research/ai-research.md) và chạy lại được bằng mã trong `research/`.

## 1. Tóm tắt

Khi điện thoại bị chiếm quyền, tiền rời đi bằng chính app, PIN và thiết bị của nạn nhân, nên mọi lớp xác thực đều báo "đúng chủ". **Innate** là một **lớp kiểm chứng con người** chạy ngầm ở bước xác nhận giao dịch: AI so khớp cách người dùng chạm và gõ với thói quen đã đăng ký và với hình mẫu người thật, để trả lời hai câu hỏi trước khi tiền rời đi: **thao tác này do người hay máy? Nếu là người, có phải chủ tài khoản không?** Kết quả là `allow`, `step_up` (xác thực thêm) hoặc `hold`, kèm lý do tiếng Việt. Innate không thay PIN, OTP hay khuôn mặt, và không bao giờ tự khoá tài khoản: nó là tín hiệu rủi ro làm cho các lớp sẵn có thông minh hơn.

## 2. Phù hợp với đề bài

| Yêu cầu của cuộc thi | Innate |
|---|---|
| **Human Centered** | Chạy ngầm, không thêm bước; chỉ hỏi thêm khi không chắc; luôn có đường thay thế; giải thích bằng tiếng Việt vì sao bị hỏi; không lưu nội dung riêng tư |
| **AI Powered** | AI là lõi: mô hình học (LightGBM) cho người/máy và nhận chủ, co rút thống kê về dân số, phát hiện phát lại. Không phải tính năng phụ |
| **Future Workspace** | Đội vận hành nhận danh sách phiên đáng ngờ kèm lý do dễ hiểu và đánh dấu đúng/sai làm nhãn học tiếp: AI giải thích, người quyết định |
| **Chủ đề** | An ninh mạng (phát hiện thao tác tự động, truy vết điều khiển từ xa) + Chống lừa đảo (chặn giao dịch do kẻ khác thực hiện trước khi mất tiền) |
| **Dùng được online** | API (Swagger) + SDK + trang demo; `[TODO: URL, online đến hết 11/12]` |

## 3. Vấn đề

- **Kịch bản A, mã độc điều khiển từ xa:** nạn nhân cài APK giả, cấp quyền Trợ năng; mã độc đọc màn hình và OTP, tự bấm chuyển tiền (các họ như RemControl, ToxicPanda 2.0 được báo cáo trong 2025–2026).
- **Kịch bản B, người cầm máy biết PIN:** người quen hoặc kẻ trộm nhìn lén.
- Xác thực truyền thống kiểm tra thứ **có thể bị lấy đi** (PIN, OTP, thiết bị). Câu hỏi không lớp nào trả lời: **ai hoặc cái gì đang chạm vào màn hình?**

**Người dùng:** người dùng ví điện tử (được bảo vệ) và đội vận hành chống gian lận (được hỗ trợ bằng bằng chứng có giải thích).

## 4. Giải pháp và điểm sáng tạo

1. **Lớp kiểm chứng con người ở bước xác nhận giao dịch**, bổ sung cho các lớp có sẵn (thiết bị, xác thực, rủi ro giao dịch). Vị trí trong chồng bảo mật: [`../plan/positioning.md`](../plan/positioning.md).
2. **Ba phép so khớp 1:1 từ cùng một phiên thao tác:** người hay máy (không cần đăng ký), có phải chủ (cần 3–5 lần đăng ký), phát lại phiên cũ. Hợp nhất thành quyết định `allow / step_up / hold` + lý do.
3. **Innate Challenge:** khi không chắc, thay vì OTP hay quét mặt, hệ thống hiện một câu ngắn gồm chữ và số ngẫu nhiên và người dùng gõ lại (~10 giây). Nhiều phím hơn cho nhiều tín hiệu hơn (đo: EER nhận chủ 0,364 → 0,245 khi từ 6 lên 30 phím; xem [`../plan/innate-challenge.md`](../plan/innate-challenge.md)). Nội dung câu do hệ thống sinh nên không phải dữ liệu riêng tư.
4. **Trung thực về năng lực:** điểm "chủ" là tín hiệu rủi ro, không phải cổng. Thiết kế quanh điều đó (step_up, đăng ký nhiều tư thế, đường thay thế).

## 5. AI bên dưới

| Thành phần | Phương pháp |
|---|---|
| Đặc trưng | Thời gian giữ/nhả phím, độ lệch chạm so với tâm phím (chuẩn hoá theo cỡ phím), vuốt, nhịp gõ ô nhập |
| Người hay máy | Luật "độ tự nhiên" + **LightGBM** huấn luyện trên người thật + bot sinh |
| Có phải chủ | Mẫu đăng ký (trung bình, độ dao động; độ dao động thời gian **co rút về dân số** để bù ít mẫu) + **LightGBM** học trọng số trên độ lệch chuẩn hoá |
| Phát lại | Khoảng cách tới 50 phiên gần nhất của chính tài khoản |
| An toàn của mẫu | Cập nhật chậm có trần độ trôi (chống "dạy dần") |
| Hợp nhất, giải thích | Tổng có trọng số; mẫu câu tiếng Việt; **không có LLM trên đường quyết định** (độ trễ, nhất quán, kiểm toán) |

**Vì sao học máy cổ điển, không học sâu:** với ~100 người, thống kê và cây quyết định thắng (co rút về dân số một mình giảm kẻ gian lọt 17 điểm); mô hình sâu như TypeNet được huấn luyện trên >100.000 người.

## 6. Bằng chứng (dữ liệu người thật công khai, chưa phải dữ liệu của đội)

| Việc | Kết quả |
|---|---|
| Nhận chủ (StrokePIN, 97 người, PIN 6 số, kẻ gian biết PIN, 3 lần đăng ký) | Học máy cắt kẻ gian lọt ở FRR 5% từ **57% xuống 38%**; không cải thiện EER (0,16). Đổi tư thế (ngồi→đi): EER ~0,31, kẻ gian lọt 71% |
| Người/máy (người thật chưa từng thấy; bot sinh) | Bot ngây thơ (nhịp đều, nhiễu thời gian): **bắt 100%**; lấy mẫu từ dân số: 61%; phân loại một mình chỉ bắt 12–26% phát lại |
| Kiểm tra phát lại (hiệu chỉnh trên người thật) | Bắt **100%** phát lại có nhiễu ≤ 10%, 29% ở ±15%, 0% từ ±20%; nhầm chủ ~0,1% |
| Innate Challenge (2.260 người gõ câu) | Kẻ gian lọt ở FRR 5% từ **81% xuống 49%** khi từ 6 lên 30 phím; bắt bot gõ đều AUC 0,92 → 0,996 |

## 7. Tác động

- **Người dùng:** được bảo vệ mà không thêm bước; chỉ bị hỏi thêm khi có dấu hiệu, kèm lý do.
- **Đối tác (ví, ngân hàng):** SDK + một API; ngưỡng cấu hình được; bổ sung cho lớp xác thực sẵn có.
- **Đội vận hành:** ít báo động mơ hồ, nhiều bằng chứng; nhãn đúng/sai nuôi mô hình.

## 8. Rủi ro và giới hạn

- Bot giống người (lấy mẫu dân số 20–73%, phát lại nhiễu ≥ 15%) và kẻ tấn công thích nghi cấp hệ thống (ActReal 2026) có thể qua mặt: Innate là **một lớp** trong nhiều lớp.
- Điểm "chủ" yếu (~38% kẻ biết PIN lọt ở FRR 5%); đổi tư thế gần như mất tín hiệu → đăng ký nhiều tư thế, `step_up` thay vì chặn.
- Web SDK không thấy văn bản đặt thẳng không qua phím → cần SDK native.
- **Chưa có dữ liệu của đội và bot thật**; mô hình hiện tạm thời. Kế hoạch ở mục 9.
- Quyền riêng tư: chỉ lưu thời gian, toạ độ, loại sự kiện, số ký tự; dữ liệu nhạy cảm theo Luật BVDLCN 2025, thu có đồng ý.

## 9. Kế hoạch đến chung kết

| Mốc | Việc |
|---|---|
| 27/11 | Đăng ký thi, gửi câu hỏi BTC |
| 28–30/11 | Thu dữ liệu người thật có đồng ý (≥ 2 lần ngồi, một điện thoại) và bot thật (`adb`, `dispatchGesture`) |
| 30/11–01/12 | Huấn luyện lại (`train_human_model.py --export …`), hiệu chỉnh ngưỡng, số liệu cuối |
| 02/12 | Đóng băng tính năng, kiểm tra tải, README khai tài sản |
| 03/12 | Nộp bài |
| 11/12 | Chung kết (sản phẩm online liên tục) |

## 10. Tuân thủ thể lệ

Tài sản có sẵn, thư viện mã nguồn mở, công cụ AI và nguồn dữ liệu được khai trong README: [`README.submission.md`](README.submission.md). Dữ liệu StrokePIN (CC BY-NC-SA 4.0) và các sản phẩm phái sinh (mô hình, prior) phát hành cùng giấy phép. Không dùng logo hay tên thương hiệu của bên thứ ba trong sản phẩm.
