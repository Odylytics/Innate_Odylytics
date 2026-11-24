# Kịch bản thuyết trình chung kết và bộ câu hỏi giám khảo

> Dùng với [`slides/innate-slides.pdf`](slides/innate-slides.pdf) (10 trang). Slide **không được sửa sau khi nộp**: chỉnh lời nói, không chỉnh slide. Thời lượng thuyết trình `[TODO: xác nhận với BTC]`; kịch bản dưới đây ~5 phút (~30 giây/slide, slide 5–7 lâu hơn).

## Lời thuyết trình theo slide

| # | Slide | Ý chính cần nói | Thời gian |
|---|---|---|---|
| 1 | Tiêu đề | "Innate: lớp kiểm chứng con người cho ví điện tử. Một câu: PIN có thể bị đánh cắp, thói quen chạm bẩm sinh thì rất khó." | 0:20 |
| 2 | Vấn đề | Hai kịch bản: mã độc Trợ năng tự bấm, và người biết PIN. "Mọi lớp bảo mật đều nói đúng chủ. Câu hỏi còn thiếu: ai hoặc cái gì đang chạm vào màn hình?" | 0:35 |
| 3 | Khoảng trống | Chồng bảo mật 5 lớp, Innate ở lớp 3. "Bổ sung, không thay thế; chạy ngầm; điểm thấp thì hỏi thêm, không chặn cứng." | 0:30 |
| 4 | Giải pháp | Đăng ký 3–5 lần → ba phép so khớp (người/máy, chủ, phát lại) → allow/step_up/hold + lý do. "Giống Face ID ở quy trình, nhưng là tín hiệu rủi ro." | 0:40 |
| 5 | Innate Challenge | Khi chưa chắc, gõ một câu. Đọc số: 81% → 49%. **Nhấn:** "cải thiện rõ nhưng chưa phải cổng chặn". | 0:45 |
| 6 | AI | Bảng thành phần. "Học máy cổ điển có kiểm chứng; với ~100 người, thống kê và cây quyết định thắng. Không có LLM trên đường quyết định." | 0:45 |
| 7 | Bằng chứng | "Đo trên người thật, chia theo người. Bot ngây thơ bị bắt hết; nhận chủ tốt hơn nhưng vẫn là tín hiệu." Nêu rõ: bot do bộ sinh tạo, chưa phải dữ liệu của đội. | 0:50 |
| 8 | Sản phẩm | API + SDK + demo + dashboard. Mời giám khảo tự thử (link ở PDF hướng dẫn). Kịch bản 4 bước. | 0:30 |
| 9 | Hạn chế | **Nói trước khi bị hỏi:** bot giống người, nhận chủ yếu, đổi tư thế, web SDK, chưa có bot thật. "Đó là lý do thiết kế `step_up`." | 0:40 |
| 10 | Tác động | Người dùng, đối tác, vận hành; lộ trình; câu chốt "PIN is what you know. Innate is how you are." | 0:30 |

## Câu hỏi giám khảo có thể hỏi và câu trả lời trung thực

**1. Dữ liệu lấy từ đâu, bao nhiêu người, có đồng ý không?**
Số liệu hiện có từ hai bộ công khai: StrokePIN (97 người, PIN 6 số trên điện thoại, CC BY-NC-SA 4.0) và Aalto (2.260 người gõ câu). `[TODO: dữ liệu của đội: số người, số phiên, phiếu đồng ý]`. Chúng tôi chỉ lưu thời gian, toạ độ, loại sự kiện, không lưu nội dung.

**2. EER/FAR bao nhiêu, đánh giá thế nào?**
Nhận chủ với 3 lần đăng ký, kẻ gian biết PIN: kẻ gian lọt 38% ở điểm 5% chủ bị nhầm (không dùng kích thước chạm, đo trên người chưa thấy). Chia theo người, tách thời điểm, báo khoảng tin cậy và so ghép cặp. Đây là tín hiệu rủi ro, không phải cổng.

**3. Sao không dùng học sâu?**
Dữ liệu nhỏ. Co rút thống kê về dân số một mình giảm kẻ gian lọt 17 điểm; mô hình sâu như TypeNet cần >100.000 người. Chúng tôi chọn thứ chạy được, kiểm chứng được và giải thích được.

**4. Bot phát lại thao tác thật thì sao?**
Có kiểm tra phát lại riêng: bắt 100% khi nhiễu thêm vào ≤ 10%, nhưng chỉ 29% ở ±15% và 0% từ ±20%. Kẻ tấn công thích nghi thêm nhiễu đủ lớn sẽ qua mặt; khi đó phiên trông như người khác và chỉ còn điểm "chủ" (yếu) cản lại. Đây là cuộc đua, chúng tôi nói thẳng.

**5. Bot lấy mẫu từ phân bố người thật thì sao?**
Bắt 20–73% tuỳ có thấy loại bot đó khi huấn luyện hay chưa. Chưa có bot thật để đo; đó là việc đang làm.

**6. Mã độc ngày nay có hành xử như vậy không? (tính thực tế)**
Mã độc Trợ năng điều khiển từ xa đã được báo cáo nhiều. Việc nhịp chạm của chúng đều hay lộ hay không **chưa có nghiên cứu công bố đo trực tiếp**; đó là giả thuyết của chúng tôi, kiểm chứng bằng bộ giả lập và `adb`. Chúng tôi không khẳng định đã bắt được mã độc thật.

**7. Vì sao không để LLM quyết định?**
Độ trễ, tính nhất quán, khả năng kiểm toán. LLM (nếu có) chỉ tóm tắt vụ việc cho đội vận hành, không nằm trên đường ra quyết định.

**8. Khác gì hệ thống nội bộ của ví, hay giải pháp thương mại (BioCatch…)?**
Chúng tôi không biết chi tiết hệ thống nội bộ của ai. Điểm khác chúng tôi nhắm tới: lý do giải thích được, `step_up` thay vì chặn cứng, tách bạch người/máy và chủ, và dạng API mở cho mọi ví. Hướng đã có tiền lệ trong ngành (behavioral biometrics, risk-based authentication); chúng tôi không tuyên bố là phát minh ra hướng này.

**9. Độ trễ và chi phí mỗi lần chấm?**
Xử lý phía máy chủ ~16–21 ms (đo trên bản triển khai trước đây), mô hình là cây quyết định nhỏ (~180 KB). `[TODO: đo lại trên bản nộp]`. Không có lời gọi LLM trên đường chấm điểm.

**10. Đổi điện thoại, đổi tư thế thì sao?**
Đổi tư thế gần như mất tín hiệu (đo: EER 0,31, kẻ gian lọt 71%). Vì vậy: đăng ký nhiều tư thế, và điểm thấp chỉ dẫn tới `step_up`. Đổi điện thoại cần đăng ký lại có kiểm soát (chưa thiết kế xong).

**11. Xử lý dữ liệu nhạy cảm theo luật mới thế nào?**
Coi nhịp chạm/gõ là dữ liệu nhạy cảm (Luật BVDLCN 2025, NĐ 356/2025): chỉ thu khi đồng ý, không lưu nội dung PIN/số tiền/ghi chú, ghi rõ trong README. Mẫu nằm trên máy chủ nên phải bảo vệ như dữ liệu sinh trắc.

**12. Innate Challenge có phiền người dùng không?**
Chỉ hiện khi hệ thống không chắc, ~10 giây, luôn có đường thay thế (OTP/khuôn mặt). **Chưa đo ma sát thực tế** và dữ liệu đo là chép câu tiếng Anh, không phải gõ chuỗi ngẫu nhiên lúc căng thẳng.

**13. Sản phẩm đã chạy trên điện thoại thật chưa?**
Ví demo và SDK web chạy trên trình duyệt điện thoại; SDK native chưa có. `[TODO: cập nhật theo thực tế lúc nộp]`.

## Nguyên tắc khi trả lời
Nêu giới hạn **trước** khi bị hỏi; dùng "tín hiệu rủi ro", "rất khó", không dùng "không thể", "bắt mọi mã độc"; số liệu nào chưa phải dữ liệu của đội thì nói rõ.
