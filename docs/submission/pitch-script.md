# Kịch bản thuyết trình chung kết và bộ câu hỏi giám khảo

> Dùng với `submission/Slide/Innate-slides.pdf` (10 trang). Slide **không được sửa sau khi nộp**: chỉnh lời nói, không chỉnh slide. Thời lượng thuyết trình `[TODO: xác nhận với BTC]`; kịch bản dưới đây ~5 phút (~30 giây/slide, slide 5–7 lâu hơn).

## Lời thuyết trình theo slide

| # | Slide | Ý chính cần nói | Thời gian |
|---|---|---|---|
| 1 | Tiêu đề | "Innate: lớp kiểm chứng con người cho ví điện tử. Một câu: PIN có thể bị đánh cắp, thói quen chạm bẩm sinh thì rất khó." | 0:20 |
| 2 | Vấn đề | Hai kịch bản: mã độc Trợ năng tự bấm, và người biết PIN. "Mọi lớp bảo mật đều nói đúng chủ. Câu hỏi còn thiếu: ai hoặc cái gì đang chạm vào màn hình?" | 0:35 |
| 3 | Khoảng trống | Chồng bảo mật 5 lớp, Innate ở lớp 3. "Bổ sung, không thay thế; chạy ngầm; điểm thấp thì hỏi thêm, không chặn cứng." | 0:30 |
| 4 | Giải pháp | Đăng ký 3–5 lần → ba phép so khớp (người/máy, chủ, phát lại) → allow/step_up/hold + lý do. "Giống Face ID ở quy trình, nhưng là tín hiệu rủi ro." | 0:40 |
| 5 | Innate Challenge | Khi chưa chắc, gõ một câu tiếng Việt ngẫu nhiên. Đọc số: 81% → 49% (đo trên câu tiếng Anh). **Nhấn:** "cải thiện rõ nhưng chưa phải cổng chặn; kiểu gõ dấu tiếng Việt là giả thuyết, chưa đo". | 0:45 |
| 6 | AI | Bảng thành phần. "Học máy cổ điển có kiểm chứng; với ~100 người, thống kê và cây quyết định thắng. Không có LLM trên đường quyết định." | 0:45 |
| 7 | Bằng chứng | "Đo trên người thật, chia theo người. Bot ngây thơ bị bắt hết; nhận chủ tốt hơn nhưng vẫn là tín hiệu." Nêu rõ: bot do bộ sinh tạo, chưa phải dữ liệu của đội. | 0:50 |
| 8 | Sản phẩm | API + SDK + demo + dashboard. Mời giám khảo tự thử (link ở PDF hướng dẫn). Kịch bản 4 bước. | 0:30 |
| 9 | Hạn chế | **Nói trước khi bị hỏi:** bot giống người, nhận chủ yếu, web SDK, chưa có bot thật. "Đó là lý do thiết kế `step_up`." | 0:40 |
| 10 | Tác động | Người dùng, đối tác, vận hành; lộ trình; câu chốt "PIN is what you know. Innate is how you are." | 0:30 |

## Câu hỏi giám khảo có thể hỏi và câu trả lời trung thực

**1. Dữ liệu lấy từ đâu, bao nhiêu người, có đồng ý không?**
Số liệu hiện có từ hai bộ công khai: StrokePIN (97 người, PIN 6 số trên điện thoại, CC BY-NC-SA 4.0) và Aalto (2.260 người gõ câu). `[TODO: dữ liệu của đội: số người, số phiên, phiếu đồng ý]`. Chúng tôi chỉ lưu thời gian, toạ độ, loại sự kiện, không lưu nội dung.

**2. EER/FAR bao nhiêu, đánh giá thế nào?**
Nhận chủ với 3 lần đăng ký, kẻ gian biết PIN: kẻ gian lọt 38% ở điểm 5% chủ bị nhầm (không dùng kích thước chạm, đo trên người chưa thấy). Chia theo người, tách thời điểm, báo khoảng tin cậy và so ghép cặp. Đây là tín hiệu rủi ro, không phải cổng.

**3. Sao không dùng học sâu?**
Dữ liệu nhỏ. Co rút thống kê về dân số một mình giảm kẻ gian lọt 17 điểm; mô hình sâu như TypeNet cần >100.000 người. Chúng tôi chọn thứ chạy được, kiểm chứng được và giải thích được.

**4. Bot phát lại thao tác thật thì sao?**
Có kiểm tra phát lại riêng: bắt 100% khi nhiễu thêm vào ≤ 10%, nhưng chỉ 29% ở ±15% và 0% từ ±20%. Đo cả hệ thống (E24, E27): phát lại nhiễu ±15–30% được cho qua 48–72%. Có thể nâng ngưỡng phát lại (0,085 bắt 86% ở ±15%) nhưng chặn nhầm chủ tăng; sẽ chốt khi có lịch sử dài của đội. Kẻ tấn công thích nghi thêm nhiễu đủ lớn sẽ qua mặt; khi đó phiên trông như người khác và chỉ còn điểm "chủ" (yếu) cản lại. Đây là cuộc đua, chúng tôi nói thẳng.

**5. Bot lấy mẫu từ phân bố người thật thì sao?**
Bắt 20–73% tuỳ có thấy loại bot đó khi huấn luyện hay chưa. Bot **biết mẫu chuẩn** của nạn nhân thì qua 75–82% (E27). Chưa có bot thật để đo; đó là việc đang làm.

**6. Mã độc ngày nay có hành xử như vậy không? (tính thực tế)**
Mã độc Trợ năng điều khiển từ xa đã được báo cáo nhiều. Việc nhịp chạm của chúng đều hay lộ hay không **chưa có nghiên cứu công bố đo trực tiếp**; đó là giả thuyết của chúng tôi, kiểm chứng bằng bộ giả lập và `adb`. Chúng tôi không khẳng định đã bắt được mã độc thật.

**7. Vì sao không để LLM quyết định?**
Độ trễ, tính nhất quán, khả năng kiểm toán. LLM (nếu có) chỉ tóm tắt vụ việc cho đội vận hành, không nằm trên đường ra quyết định.

**8. Khác gì hệ thống nội bộ của ví, hay giải pháp thương mại (BioCatch…)?**
Chúng tôi không biết chi tiết hệ thống nội bộ của ai. Điểm khác chúng tôi nhắm tới: lý do giải thích được, `step_up` thay vì chặn cứng, tách bạch người/máy và chủ, và dạng API mở cho mọi ví. Hướng đã có tiền lệ trong ngành (behavioral biometrics, risk-based authentication); chúng tôi không tuyên bố là phát minh ra hướng này.

**9. Độ trễ và chi phí mỗi lần chấm?**
Đo local (E26, không tính mạng): `/score` p50 3,7 ms, p99 14 ms; mô hình là cây quyết định nhỏ (~180 KB). Chưa đo trên Vercel/Neon: `[TODO: đo lại trên bản nộp]`. Không có lời gọi LLM trên đường chấm điểm.

**10. Đổi điện thoại thì sao?**
Điểm thấp chỉ dẫn tới `step_up`, không chặn. Đổi điện thoại cần đăng ký lại có kiểm soát (chưa thiết kế xong).

**11. Xử lý dữ liệu nhạy cảm theo luật mới thế nào?**
Coi nhịp chạm/gõ là dữ liệu nhạy cảm (Luật BVDLCN 2025, NĐ 356/2025): chỉ thu khi đồng ý, không lưu nội dung PIN/số tiền/ghi chú, ghi rõ trong README. Mẫu nằm trên máy chủ nên phải bảo vệ như dữ liệu sinh trắc.

**12. Innate Challenge có phiền người dùng không?**
Chỉ hiện khi hệ thống không chắc, ~10 giây, luôn có đường thay thế (OTP/khuôn mặt). **Chưa đo ma sát thực tế** và dữ liệu đo là chép câu tiếng Anh, không phải gõ câu tiếng Việt ngẫu nhiên lúc căng thẳng.

**13. Sản phẩm đã chạy trên điện thoại thật chưa?**
Ví demo và SDK web chạy trên trình duyệt điện thoại; SDK native chưa có. `[TODO: cập nhật theo thực tế lúc nộp]`.

**14. Sao lại gõ tiếng Việt? Có công trình nào chưa?**
Chúng tôi tìm và **không thấy công trình công bố nào** dùng kiểu gõ Telex/VNI làm sinh trắc học (không có nghĩa là chưa ai làm). Ý tưởng: phím biến đổi dấu thanh và vị trí gõ dấu là thói quen cá nhân, không phụ thuộc câu cụ thể, và bot phải giả lập cả bộ gõ. Hiện mới có thiết kế, mô phỏng và mã trích đặc trưng; **chưa đo trên người Việt thật**.

**15. Sao không dùng cảm biến chuyển động (con quay, gia tốc)?**
Thử trên StrokePIN (E23): chuyển động cho EER 0,04 nhưng đó là nhiễu thiết bị (mỗi người một máy); dữ liệu chỉ 5 Hz nên không kiểm được cú giật khi chạm. Chúng tôi coi đó là ứng viên chống bot ("có tay cầm"), chưa tuyên bố.

**16. Bản online chạy mô hình học chưa?**
Rồi: `/health` báo cả hai mô hình đã nạp, mô hình chạy bằng Python thuần nên không phụ thuộc thư viện hệ thống. Mô hình có dự phòng luật nếu lỗi. Trên người thật (E29, 97 người), có mô hình học thì kẻ biết PIN được cho qua 22%, tắt mô hình thì 89%. Số này đo trong `research/`, chưa đo trên bản online; các phiên trong demo là mô phỏng. `[TODO: chạy backend/scripts/check_online.py lúc nộp và trước 11/12]`

**17. Vì sao demo dùng PIN 6 số?**
Mô hình chủ học trên PIN 6 số (StrokePIN), và với PIN 4 số kẻ biết PIN lọt nhiều hơn rõ rệt (E28: 68% so với 28% được `allow`), nên demo dùng PIN 6 số `159357`. Mô hình học đang bật trên bản online; nếu nó tắt (lỗi hay công tắc), hệ thống tự rơi về luật và yếu hơn, và chúng tôi nói thẳng điều này.

## Nguyên tắc khi trả lời
Nêu giới hạn **trước** khi bị hỏi; dùng "tín hiệu rủi ro", "rất khó", không dùng "không thể", "bắt mọi mã độc"; số liệu nào chưa phải dữ liệu của đội thì nói rõ.
