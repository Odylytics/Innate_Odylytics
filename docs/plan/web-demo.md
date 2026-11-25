# Demo trên website cho ban giám khảo

> Ghi chú 25/11/2026. Nhóm dùng Mac + iPhone, app native chưa có. Mục tiêu: một link giám khảo mở được ngay (yêu cầu "dùng thử online" của thể lệ), đến hết 11/12.
> Code web nằm ở thư mục `web/` của repo này (landing `#/` + demo `#/demo` + kịch bản `#/demo?story=1` + vận hành `#/ops`). API ở `backend/`. (Repo `Innate_website` cũ đã được gộp vào đây ngày 26/11.)

## 1. Giám khảo sẽ trải nghiệm gì

1. Mở link → landing (`#/`): vấn đề, cách Innate trả lời, nút **Xem demo 2 phút** và **Tự thử ví demo**.
2. **Xem demo 2 phút** (`#/demo?story=1`): kịch bản 8 bước tự chạy, có tiếng. Hà đăng ký nhịp → Hà chuyển cho mẹ (`allow`) → mã độc bấm PIN lúc 2 giờ sáng (`hold`) → Bảo biết PIN (`step_up`) → Khoa xem dashboard → chính sách. Phiên dựng sẵn nhưng **chấm thật trên API**.
3. **Tự thử ví** (`#/demo`): giám khảo tự gõ PIN `1593` ba lần để đăng ký, chuyển tiền bằng nhịp của chính mình, rồi bấm "mã độc" hoặc "người khác" trong bảng điều khiển kẻ tấn công để thấy kết quả khác.

Phần chạy thật: thu chạm (Pointer Events trên bàn phím PIN tự vẽ và thanh vuốt xác nhận), chấm điểm, khoá đăng ký, lý do tiếng Việt. Phần giả lập: phiên của mã độc, Bảo và các nhân vật (sinh trong trình duyệt, gửi lên API chấm như phiên thật).

## 2. Kiểm tra trên máy (25/11)

API chạy local, chấm đúng các phiên mà web demo tạo ra (`synth.ts`, cùng hạt giống với kịch bản). "25 người" = 25 nhân vật giả ngẫu nhiên, mỗi người đăng ký 3 lần rồi chuyển tiền; Bảo và mã độc thử trên tài khoản của từng người. **Toàn bộ là phiên giả: chỉ kiểm tra đường đi của dữ liệu, không phải độ chính xác.**

| PIN demo | AI (LightGBM) | Kịch bản: Hà / Bảo / mã độc | 25 chủ ví | 25 lần Bảo | 25 lần mã độc |
|---|---|---|---|---|---|
| 4 số `1593` (hiện tại) | tắt | allow / step_up / hold | 24 allow | 23 step_up, 2 hold | 25 hold |
| 4 số `1593` (hiện tại) | bật | allow / **hold** / hold | 24 allow | 21 step_up, 4 hold | 25 hold |
| 6 số `159357` | tắt | allow / step_up / hold | 25 allow | 22 step_up, 3 hold | 25 hold |
| 6 số `159357` | bật | allow / **hold** / hold | **16 allow, 9 step_up** | 11 step_up, 14 hold | 25 hold |

Phát hiện:
- **Mô hình "có phải chủ" không chạy với PIN 4 số.** Nó học trên PIN 6 số (StrokePIN), nên với `1593` API lặng lẽ dùng phép so khoảng cách. Mô hình "người hay máy" thì có chạy.
- **Đổi sang PIN 6 số thì mô hình chủ chạy, nhưng làm phiền chủ thật 9/25 lần.** Giám khảo tự thử rất có thể bị yêu cầu xác thực thêm với chính nhịp của mình. Trên phiên giả, chưa biết với người thật ra sao.
- **Bật AI thì kịch bản lệch lời thoại.** Bước Bảo nói "Innate yêu cầu xác thực khuôn mặt" (`step_up`), nhưng khi bật AI thì Bảo bị `hold`. Kịch bản được hiệu chỉnh khi API online chỉ chạy luật.
- **Chuột hay ngón tay không đổi kết quả** trên phiên giả (kích thước chạm không nằm trong đặc trưng người/máy). Nhịp bấm chuột thật của giám khảo chưa đo.
- **API online hiện chỉ chạy luật**: Vercel không cài `lightgbm`. Bản online hiện cho đúng cột "tắt AI" ở trên.

## 3. Việc cần làm để demo web chạy được

| # | Việc | Ai / ở đâu | Ghi chú |
|---|---|---|---|
| 1 | Deploy `web/` (Root Directory = `web`) với `VITE_SDK_KEY` | người deploy | Thiếu key → API trả 401, demo báo lỗi |
| 2 | Chốt bật AI trên API online hay không | nhóm | Bật: bằng chứng "AI là lõi" rõ hơn, nhưng phải sửa lời kịch bản bước Bảo (hoặc chọn hạt giống khác) và chấp nhận chủ ví đôi khi bị `step_up` |
| 3 | Giữ PIN 4 số cho phần "tự thử" | web | Ổn định cho giám khảo. Nói thẳng trong slide: mô hình chủ học trên PIN 6 số, bản demo dùng so khoảng cách |
| 4 | Thử trên iPhone thật và laptop thật | nhóm | Safari iOS hỗ trợ Pointer Events; chưa kiểm `width/height` chạm trên iOS. Thử nhanh qua mạng LAN: chạy Vite với `--host` và API với `--host 0.0.0.0`, mở `http://<IP máy Mac>:5173` trên iPhone |
| 5 | Ghi "Hướng dẫn dùng thử" trên landing + PDF 1 trang | `web/` + `docs/submission/` | Link, PIN `1593`, 3 bước; tài liệu nộp hiện còn ghi ví cũ và PIN `159357` |

## 4. Đưa luồng chuyển tiền mới vào web (số tài khoản → ngân hàng → PIN)

Web làm được phần lớn, trừ hai tín hiệu mã độc chỉ app native thấy:

| Bước | Trên web | Cách demo |
|---|---|---|
| Gõ số tài khoản trên bàn phím số tự vẽ | **Thu được** nhịp và độ lệch tâm (Pointer Events, như PIN) | Chủ ví gõ thật; theo E14, chỉ là bằng chứng cộng thêm |
| Chọn ngân hàng trong danh sách | **Thu được** chạm và cuộn | Chủ ví chọn thật |
| Mã độc đặt thẳng số tài khoản (`set_text`) | **Không thu được** từ trình duyệt | Bảng điều khiển kẻ tấn công gửi phiên giả có `set_text`; API bắt bằng luật. Ghi rõ "mô phỏng" |
| Mã độc chọn ngân hàng không có chạm | **Không thu được** | Như trên |

Cần sửa API trước (xem [`../research/transfer-flow.md`](../research/transfer-flow.md) mục 3): ô số tài khoản có toạ độ chạm nhưng **không gửi nhãn phím**, sự kiện chọn ngân hàng, mở rộng luật `set_text` cho hai bước này. Sau đó mới thêm màn hình vào ví web và kịch bản.

## 5. Thứ tự đề xuất (hạn nộp 03/12)

1. Deploy web như hiện tại (PIN 4 số, API chỉ luật) để có link chạy ổn định sớm. **Đây là bản an toàn.**
2. Thử trên iPhone và laptop thật của nhóm; sửa giao diện nếu cần.
3. Quyết định bật AI trên API; nếu bật thì sửa lời kịch bản bước Bảo cho khớp và kiểm lại.
4. Thêm số tài khoản + ngân hàng vào API, rồi vào ví web và kịch bản.
5. Cập nhật PDF 1 trang và video theo đúng bản web cuối.
