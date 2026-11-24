# Innate — câu chuyện pitch

> **PIN có thể bị đánh cắp. Thói quen chạm bẩm sinh thì rất khó.**
> Cập nhật 24/11/2026. Dùng cho slide (≤ 10 trang), video (≤ 3 phút) và phần thuyết trình chung kết.

> Định vị sản phẩm (Innate là lớp gì, nằm ở đâu trong chồng bảo mật): [`positioning.md`](positioning.md).

## Ý chính

Mọi thứ xác thực truyền thống đều là thứ có thể **lấy đi**: PIN nhìn lén được, OTP đọc được, thiết bị chiếm được. Mã độc như RemControl và ToxicPanda 2.0 (2026) lạm dụng quyền Trợ năng để tự bấm chuyển tiền bằng chính app, PIN và thiết bị của nạn nhân. Còn **cách một người chạm**: giữ phím bao lâu, lệch tâm nút về phía nào, vuốt nhanh hay chậm, là thói quen vận động hình thành từ nhỏ, không có file nào để sao chép.

Innate đo đúng điều đó, và chỉ trả lời hai câu hỏi tại bước xác nhận giao dịch:

| Câu hỏi | Bắt được ai |
|---|---|
| Thao tác này do **người** hay **máy**? | Mã độc, script, `adb` (kịch bản A) |
| Nếu là người, có phải **chủ** tài khoản không? | Người quen, kẻ trộm biết PIN (kịch bản B) |

Kết quả là `allow`, `step_up` (xác thực thêm) hoặc `hold` (giữ lệnh), kèm lý do tiếng Việt. Hệ thống đề xuất, không tự khoá tài khoản.

## Mạch kể (7 nhịp)

1. **Mở bằng một câu chuyện.** Nạn nhân cài APK giả, cấp quyền Trợ năng. Vài phút sau tiền đi ra bằng đúng PIN của họ. Mọi lớp bảo mật đều nói "đúng chủ".
2. **Chỉ ra lỗ hổng.** Mọi thứ ta kiểm tra đều là thứ kẻ gian có thể lấy được.
3. **Đổi góc nhìn.** Có một thứ họ không lấy được dễ dàng: cách bạn chạm.
4. **Cho xem bằng chứng học thuật.** Nhập PIN bằng nhịp và vị trí chạm phân biệt được người với người (Zheng 2014: EER 3,65–7%; Buschek 2015: thêm vị trí chạm giảm lỗi 26–37%).
5. **Demo sống (mục 6 của kế hoạch).** Giám khảo A đăng ký. Giám khảo B biết PIN nhưng bị yêu cầu xác thực thêm. Bảng điều khiển hacker bấm tự động và bị gắn "không phải người thật".
6. **Minh bạch.** Màn hình hiện lý do: "nhịp PIN chậm hơn 40%, chạm lệch phải". Đây là điểm khác với hộp đen.
7. **Nói thật về giới hạn, rồi chốt.** Innate là một tín hiệu trong nhiều lớp, đã đo bằng quy trình đánh giá chặt, mở bằng API cho bất kỳ ví nào.

## Câu khẩu hiệu

- EN: *PIN is what you know. Innate is how you are.*
- VI: *Mật khẩu có thể bị lộ. Cách bạn chạm thì không dễ bị đánh cắp.*

## Giữ cho câu chuyện đứng vững (quan trọng)

Giám khảo là CTO và Head of AI. "Bẩm sinh" là cách kể hay, nhưng bằng chứng cho thấy thói quen chạm **khó** chứ không **không thể** đánh cắp. Nói quá sẽ bị bắt bẻ ngay.

| Nói | Không nói |
|---|---|
| "**Rất khó** đánh cắp", "không có file nào để sao chép" | "Không thể giả mạo", "chính xác tuyệt đối" |
| "Một **tín hiệu** trong nhiều lớp, dùng để kích hoạt xác thực thêm" | "Thay thế OTP / PIN" |
| "Bắt tốt bot ngây thơ; bot thích nghi là hướng nghiên cứu" | "Bắt mọi mã độc" |

**Bằng chứng nên chuẩn bị sẵn khi bị hỏi:**
- Tấn công bắt chước (người cố tình nhái) làm EER tăng lên 10–15% (BioTouchPass2, 2020). Tức là có thể nhái được một phần.
- Luyện tập làm kẻ tấn công tốt lên: FAR từ 0,24 lên 0,63 sau khi luyện (Tey 2013, nguồn thứ cấp trong báo cáo paper, chưa tải được bản gốc).
- Mã độc thích nghi cấp hệ thống qua mặt bộ phát hiện chạm + IMU 71–77% (ActReal 2026, preprint).
- Chính tác giả Touchalytics kết luận chạm không đủ làm xác thực độc lập.
- Số liệu của đội sẽ chênh với paper vì 3 lựa chọn đánh giá nghiêm hơn (tách theo thời gian, một máy, không dùng dữ liệu kẻ gian khi huấn luyện), theo FETA 2022. Nói điều này **trước** khi bị hỏi.

**Cách biến điểm yếu thành điểm mạnh:** "Chúng tôi không hứa kẻ gian không bao giờ nhái được. Chúng tôi làm cho việc đó **đắt hơn nhiều**, và khi nghi ngờ thì hỏi thêm thay vì chặn cứng."

## Gắn với tiêu chí chấm

| Tiêu chí | Innate trả lời |
|---|---|
| Sáng tạo | Đổi trục xác thực từ "thứ bạn có/biết" sang "cách bạn hành động"; tách bạch bot và chủ |
| Chất lượng, hoàn thiện | Online, ví demo + API + Swagger; đo bằng quy trình FETA, báo FAR@FRR kèm khoảng tin cậy |
| Tiềm năng tác động | API mở cho ví/ngân hàng, đối phó đúng mối đe doạ Trợ năng đang tăng |

## Gợi ý khung 10 slide

1. Câu chuyện nạn nhân + khẩu hiệu
2. Vấn đề: hai kịch bản A (mã độc) và B (biết PIN)
3. Vì sao xác thực hiện tại hụt (mọi thứ đều có thể bị lấy)
4. Ý tưởng: cách bạn chạm
5. Innate làm gì: hai câu hỏi, ba hành động
6. Kiến trúc và AI (người/máy, chủ, hợp nhất, giải thích)
7. Demo (ảnh chụp + QR sản phẩm)
8. Kết quả đo thật và cách đo
9. Giới hạn trung thực và hướng mở rộng
10. Tác động và lộ trình (API cho đối tác)
