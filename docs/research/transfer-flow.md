# Luồng chuyển tiền: số tài khoản → ngân hàng → PIN

> Ghi chú nghiên cứu, 25/11/2026. Mục tiêu demo: chấm không chỉ lúc nhập PIN mà cả lúc **nhập số tài khoản** và **chọn ngân hàng**. Không có bước gõ tên: sau khi có số tài khoản và ngân hàng, ví tự tra tên người nhận.
> Chưa có số đo nào trong ghi chú này. Các con số trích là của nghiên cứu khác hoặc của thí nghiệm E1–E13 trong repo.

## 1. Luồng và kẻ tấn công

| Bước | Người dùng làm gì | Cách vào khác (không gõ) |
|---|---|---|
| 1. Số tài khoản | Gõ 8–19 chữ số | Dán từ tin nhắn, quét VietQR, chọn người nhận đã lưu |
| 2. Ngân hàng | Cuộn danh sách và chạm, hoặc gõ vài chữ để tìm (`VCB`, `MB`) | Tự điền khi quét VietQR |
| 3. Số tiền | Gõ số | Tự điền khi quét VietQR có số tiền |
| 4. PIN | Gõ 6 số trên bàn phím PIN tự vẽ | Không có |
| 5. Xác nhận | Vuốt hoặc chạm | Không có |

Ba kiểu kẻ tấn công, mỗi kiểu để lại dấu vết khác nhau:

| Kẻ tấn công | Số tài khoản | Ngân hàng | PIN | Lớp kiểm tra bắt được |
|---|---|---|---|---|
| **A. Mã độc Trợ năng** (RedHook, Gigabud nhắm Việt Nam; xem [`notes/bot_detection.md`](notes/bot_detection.md)) | Đặt thẳng chữ vào ô (`ACTION_SET_TEXT`), không có phím nào | Bấm phần tử danh sách bằng `ACTION_CLICK`, không có chạm thật; hoặc `dispatchGesture` | `dispatchGesture` hoặc bấm phần tử | Người hay máy |
| **B. Người biết PIN** (cầm máy nạn nhân) | Gõ tay số tài khoản của họ | Chạm tay | Gõ tay | Có phải chủ |
| **C. Nạn nhân bị lừa tự chuyển** (giả công an, giả nhân viên ngân hàng) | Thường **dán** số do kẻ lừa gửi | Chạm tay | Chính chủ gõ | Khó nhất: đúng người, đúng máy |

Kiểu C nằm ngoài phạm vi chính của Innate ([`../plan/positioning.md`](../plan/positioning.md)): nhịp chạm đúng là của chủ. Các nhà cung cấp thương mại có nêu dấu hiệu như do dự khi nhập người nhận lạ, hoặc đang có cuộc gọi lúc chuyển tiền, nhưng đó là tuyên bố tiếp thị chưa được kiểm chứng độc lập, và giới phân tích nghi ngờ hành vi có thể chặn được loại lừa này ([American Banker](https://www.americanbanker.com/payments/news/biometrics-role-in-stopping-peer-to-peer-payment-scams), [BioCatch](https://www.biocatch.com/blog/authorized-push-payment-fraud-how-digital-behavior-can-uncover-social-engineering-scams), [Outseer](https://www.outseer.com/solutions/scam-prevention)). Với demo, chỉ nên dùng "dán số tài khoản + người nhận mới" làm **ngữ cảnh** để đề nghị xác thực thêm, không coi đó là bằng chứng lừa đảo.

## 2. Tín hiệu theo từng bước

### Bước 1: số tài khoản

Nếu số tài khoản được gõ trên **bàn phím số tự vẽ** (như bàn phím PIN), mỗi lần gõ cho đúng những gì PIN đang cho: giữ phím, khoảng cách giữa hai phím, độ lệch so với tâm phím. Khác biệt lớn là **nội dung đổi theo từng giao dịch**. Mẫu nhịp PIN hiện tại so theo vị trí chữ số (`pin_hold_0..5`), nên không dùng lại được. Cần đặc trưng **không phụ thuộc nội dung**:

- phân bố thời gian giữ phím (trung bình, độ lệch, tứ phân vị);
- khoảng cách giữa hai phím theo **khoảng cách hình học giữa hai phím** (cùng phím, kề nhau, xa nhau), không theo cặp chữ số;
- độ lệch tâm theo **từng phím** (phím 1 hay bị chạm lệch trái...), gộp lại khi phím xuất hiện;
- thao tác xoá và gõ lại.

Ưu điểm: 8–19 phím mỗi lần, nhiều hơn PIN 6 số. E13 cho thấy gõ nhiều phím hơn giúp nhận ra người tốt hơn (EER 0,364 với 6 phím, 0,245 với 30 phím, trên chữ cái Aalto). Chưa có nghiên cứu nào đo việc gõ **chữ số tự do** trên điện thoại. Một bài nhận xét bàn phím số ít được nghiên cứu hơn bàn phím chữ, và một thí nghiệm PIN dùng một lần chỉ đạt EER 26% ([Springer, 2018](https://link.springer.com/content/pdf/10.1186/s42400-018-0009-4.pdf)). Vì vậy kỳ vọng nên thấp.

Tín hiệu người hay máy:
- `set_text` (văn bản đổi mà không có phím): chỉ SDK native thấy. Đây là dấu hiệu mã độc rõ nhất: mã độc dùng Trợ năng để đặt chữ hoặc bấm phần tử trong app khác ([MITRE ATT&CK T1516](https://attack.mitre.org/techniques/T1516/)); Gustuff đặt giá trị ô nhập trong app ngân hàng theo cách này (theo Group-IB, chưa đọc bản gốc).
- Gõ quá đều, đúng tâm phím: như bot chiến thuật 1–2 với PIN.
- Dán: người thật cũng hay dán, nên chỉ là ngữ cảnh.

**Quyền riêng tư:** số tài khoản người nhận là dữ liệu cá nhân. Phiên PIN hiện gửi nhãn phím (`key`). Với số tài khoản, **không được gửi nhãn phím**, vì gộp lại sẽ ra đúng số tài khoản. Chỉ gửi thời gian, độ lệch so với tâm phím đã chuẩn hoá, và khoảng cách giữa hai phím liên tiếp. Phải ghi rõ trong phiếu đồng ý.

### Bước 2: chọn ngân hàng

Đây là bước chạm và cuộn, không phải gõ. Tín hiệu:
- **Chọn mà không có chạm thật** (SDK native thấy sự kiện chọn nhưng không có `MotionEvent` trước đó): dấu hiệu `ACTION_CLICK` của mã độc. Cùng loại với `set_text`, nên dùng làm **luật**, không cần học máy.
- Cú cuộn: tốc độ, độ cong, cách dừng. Giống phần vuốt đã có (`swipe_*`), có dữ liệu công khai Touchalytics (41 người, vuốt/cuộn).
- Thời gian từ khi mở danh sách tới lúc chọn, số lần cuộn qua lại.
- Gõ ô tìm kiếm: quá ngắn để nhận ra người, chỉ dùng để bắt `set_text` hoặc dán.

Không có bộ dữ liệu công khai nào cho việc chọn ngân hàng trong danh sách. Phần nhận ra người ở bước này chỉ đo được bằng dữ liệu của nhóm.

### Bước 3–5: số tiền, PIN, xác nhận

Đã có trong API: luật `set_text` ở ô số tiền, mô hình PIN (người hay máy, có phải chủ), phát lại, vuốt xác nhận.

## 3. API hiện có gì, còn thiếu gì

| Việc | Hiện trạng | Cần làm |
|---|---|---|
| Ô số tài khoản | Dùng tạm `fields[name="recipient"]`: chỉ có thời gian, loại sự kiện, số ký tự; **không có toạ độ chạm** | Thêm danh sách chạm cho ô số tài khoản (như `pin_taps` nhưng không có nhãn phím), hoặc tính đặc trưng ngay trên máy |
| Chọn ngân hàng | Không có | Thêm sự kiện chọn: thời điểm, có chạm thật đi trước hay không, các cú cuộn |
| Luật `set_text` / chọn không có chạm | Chỉ có cho ô số tiền | Mở rộng cho số tài khoản và ngân hàng |
| Mô hình người hay máy cho ô văn bản (E11) | Chỉ trong `research/`, chưa gắn vào `/score` | Gắn vào, rồi huấn luyện lại cho chữ số |
| Nhận ra chủ qua nhịp gõ số tài khoản | Không có | Đặc trưng không phụ thuộc nội dung (mục 2), chạy E14 trước |

## 4. Thí nghiệm đề xuất

**E14. Nhận ra chủ khi gõ chữ số mới (làm được ngay, dữ liệu StrokePIN).** StrokePIN có 20 PIN 6 số dùng chung cho 97 người. Cho đăng ký trên một nhóm PIN rồi kiểm tra trên **các PIN chưa thấy**, dùng đặc trưng không phụ thuộc nội dung. Đây là mô phỏng gần nhất của việc gõ một số tài khoản mới. Câu hỏi: khi nội dung đổi, tín hiệu chủ tài khoản còn lại bao nhiêu so với E12b (FAR 0,375 tại FRR 5% khi cùng PIN)? Giới hạn: 6 số ngắn hơn số tài khoản, và bàn phím trong StrokePIN có thể khác bàn phím của app.

**Kết quả E14 (25/11, [`../../research/results/e14_unseen_digits.md`](../../research/results/e14_unseen_digits.md)).** Đăng ký 3 PIN x 3 lượt khi ngồi, 20 đặc trưng không phụ thuộc nội dung, không dùng kích thước chạm, kẻ gian gõ cùng chuỗi số:

| Kiểm thử | LightGBM: EER | LightGBM: FAR @ FRR 5% |
|---|---|---|
| cùng chuỗi số đã đăng ký | 0.250 | 0.537 |
| chuỗi số mới, 6 số | 0.325 | 0.697 |
| chuỗi số mới, 12 số | 0.268 | 0.588 |
| chuỗi số mới, khi đi | 0.367 | 0.822 |

- Khi chuỗi số mới, tín hiệu yếu đi rõ: ở mức chỉ làm phiền chủ 5% số lần, **~70% kẻ gian vẫn lọt** với 6 số, **~59%** với 12 số. Gõ dài hơn giúp, đúng hướng E13.
- LightGBM tốt hơn khoảng cách đơn giản ở mọi dòng; khoảng cách đơn giản gần như vô dụng ở FRR 5% (FAR ~0,92).
- Đổi tư thế (đi) làm mất gần hết tín hiệu, như E9.
- **Kết luận:** nhịp gõ số tài khoản **không đủ để đứng một mình**. Chỉ nên là bằng chứng cộng thêm vào điểm PIN, và chỉ có ý nghĩa khi số tài khoản đủ dài. Việc tiếp theo nên đo: gộp điểm PIN (E12b) với điểm số tài khoản có giảm được FAR không.
- Giới hạn: StrokePIN không có số tài khoản thật; 12 số là gộp 2 lượt gõ riêng, không phải một lần gõ liền; mỗi người một máy.

**E15. Bot gõ số tài khoản.** Thêm vào bộ giả lập (`attacker/`) các chiến thuật: `set_text` số tài khoản, dán, gõ đều đúng tâm phím, lấy mẫu từ phân bố người. Đo luật và mô hình trên cả luồng số tài khoản → ngân hàng → PIN. Bot vẫn là bot giả, chỉ dùng để kiểm tra đường đi của dữ liệu.

**E16. Chọn ngân hàng (cần dữ liệu của nhóm).** Khi app điện thoại có màn chọn ngân hàng: thu phiên thật có đồng ý, và chạy bot `ACTION_CLICK` / `dispatchGesture` thật trên máy Android. Đo luật "chọn không có chạm" và đặc trưng cuộn.

Thứ tự: E14 trước (không cần app, trả lời câu hỏi "gõ số tài khoản có giúp nhận chủ không"), rồi đổi schema + E15, cuối cùng E16 khi có app.

## 5. Kịch bản demo gợi ý

1. Chủ ví chuyển tiền: gõ số tài khoản, chọn ngân hàng, gõ PIN → `allow`.
2. Mã độc: số tài khoản bị đặt thẳng, ngân hàng được chọn không có chạm, PIN bấm đều → `hold`, lý do tiếng Việt cho từng bước.
3. Người biết PIN: gõ tay mọi bước → nhịp gõ số tài khoản và PIN không khớp chủ → `step_up`.
4. (Tuỳ chọn) Nạn nhân bị lừa: dán số tài khoản lạ, người nhận mới, số tiền lớn → `step_up` vì ngữ cảnh, kèm cảnh báo. Nói rõ trên sân khấu đây là ngữ cảnh, không phải nhận ra kẻ lừa.

Bước 2 và 3 của kịch bản cần **app native**: web không thấy `set_text` và chọn không có chạm.
