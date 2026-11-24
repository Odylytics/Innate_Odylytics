# Nhịp — Mô tả dự án và kiểm chứng bằng paper

> Cập nhật 24/11/2026. Tài liệu này tóm tắt ý tưởng, hiện trạng mã nguồn, và kết quả đối chiếu các con số trong kế hoạch với paper gốc trong `papers/`.
> Kế hoạch đầy đủ: [`../nhip-momo-tech-contest.md`](../nhip-momo-tech-contest.md). Tổng hợp paper: [`../reports/Paper nền tảng cho Nhịp.md`](../reports/Paper%20nền%20tảng%20cho%20Nhịp.md).

## 1. Ý tưởng

**Nhịp** là lớp chấm điểm rủi ro hành vi (B2B SDK + API) cho ví điện tử và ngân hàng. Khi điện thoại bị chiếm quyền, tiền vẫn đi ra bằng đúng app, đúng PIN, đúng thiết bị của nạn nhân, nên xác thực truyền thống coi đó là chính chủ. Nhịp trả lời hai câu hỏi tại bước xác nhận giao dịch:

1. Thao tác này do **ngón tay người** hay do **máy** (mã độc Trợ năng, `adb`, script)?
2. Nếu là người, có **khớp thói quen chủ tài khoản** không?

Hai kịch bản: **A** mã độc điều khiển từ xa (RedHook, Gigabud, SpyNote…), **B** người quen/kẻ trộm biết PIN.

Đầu vào chỉ gồm thời gian và toạ độ chạm (giữ phím, khoảng cách giữa phím, lệch tâm phím, kích thước chạm, vuốt), không lưu nội dung PIN. Đầu ra: điểm người/máy, điểm khớp chủ, rủi ro, hành động `allow | step_up | hold`, lý do và câu giải thích tiếng Việt. Hệ thống **chỉ đề xuất**, không tự khoá tài khoản. LLM không nằm trên đường ra quyết định.

### Ba tầng chấm điểm

| Tầng | Cách làm | Nền tảng |
|---|---|---|
| Người hay máy | Luật "độ tự nhiên" (baseline) → LightGBM/RF | BeCAPTCHA, Iliou 2021, Serwadda & Phoha 2013 |
| Có phải chủ | Mẫu chuẩn 3–5 lượt, scaled Manhattan, cập nhật có trần độ trôi | Killourhy & Maxion 2009, Zheng 2014, Buschek 2015 |
| Hợp nhất | Tổng có trọng số sau chuẩn hoá, 3 vùng theo ngưỡng A/B | Freeman 2016, Wiefling 2020–2022 |

## 2. Hiện trạng (24/11/2026)

| Có | Chưa có |
|---|---|
| Backend FastAPI + SQLAlchemy, đã deploy Vercel + Neon; endpoint `/v1/sessions`, `/enroll`, `/score`, `/export`, `/label` | SDK JavaScript, bàn phím PIN tự vẽ |
| Chấm điểm baseline: `human.py` (luật), `owner.py` (Manhattan + drift cap), `fusion.py`, `explain.py` | Ví demo, dashboard vận hành |
| Bộ giả lập hacker 4 chiến thuật + `adb` | Dữ liệu người thật, mô hình LightGBM/RF |
| 7 + 7 bài test | Số liệu đánh giá thật (FAR@FRR 5%, EER, DET) |
| 52 PDF paper + báo cáo tổng hợp | Slide, video, PDF 1 trang, README nộp bài |

Số liệu baseline hiện có (bắt 100% chiến thuật 1–2, 0% chiến thuật 3, 5–30% chiến thuật 4) đo trên người **giả**, không dùng cho slide.

## 3. Kiểm chứng con số bằng paper gốc

Đã trích text PDF và đối chiếu.

| Khẳng định trong kế hoạch | Kết quả đối chiếu |
|---|---|
| Zheng 2014: EER 3,65–7,34% khi nhập PIN | **Đúng.** PIN `3-2-4-4` 3,65%, `1-1-1-1` 6,96%, `5-5-5-5` 7,34%, PIN 8 số ~4,5%. 80+ người, một tư thế, 85 lượt huấn luyện/người, và **dùng cả gia tốc, áp lực, kích thước chạm, thời gian**. |
| Buschek 2015: thêm vị trí chạm giảm EER 26,4–36,8% | **Đúng.** 28 người, 2 tuần. Đánh giá một phiên cho EER thấp hơn nửa so với khác phiên. |
| FETA 2022: EER 4,9% → 13,8% | **Đúng.** Rà 30 bài, tất cả mắc ít nhất một lỗi. Đưa dữ liệu kẻ gian vào huấn luyện làm đẹp 2,55 điểm, trộn đời máy 3,2–5,8 điểm. |
| BioTouchPass2: EER 2,38% | **Đúng.** 217 người, PIN 4 số, mô hình RNN. Với tấn công bắt chước (imitation), EER 10,4–15%. |
| Lovisotto 2020: đầu độc mẫu >70% với <10 lần tiêm | **Đúng.** Phát hiện bắt >99% sau 2 lần tiêm. |
| Touchalytics 2012 | Median EER 0% cùng phiên, 2–3% khác phiên, <4% sau một tuần. Chính tác giả kết luận **không đủ làm xác thực độc lập**, chỉ hợp làm một phần của hệ đa tín hiệu. |
| TypeNet 2021 | EER 9,2% trên bàn phím cảm ứng (văn bản tự do, >100k người). Stragapede 2022 (Transformer): 3,84% trên Aalto với 5 phiên đăng ký. |
| Freeman 2016 (LinkedIn) | Kết hợp tín hiệu có trọng số, AUC 0,913 → 0,955. Dùng ngữ cảnh đăng nhập, không dùng sinh trắc chạm. |
| BeCAPTCHA 2021 | Thêm gia tốc kế cải thiện rõ, giữ tỷ lệ bắt bot >90% khi huấn luyện đa dạng. Chế độ "agnostic" (bot chưa thấy) kém hơn hẳn. Con số "~60% → 80–90%" trong kế hoạch **không tìm thấy nguyên văn**. |
| Killourhy 2009: Manhattan scaled tốt nhất | Abstract ghi hai bộ tốt nhất EER 9,6% và 10,2%. Chưa xác nhận bộ nào đạt 9,6%. |
| Kịch bản A: mã độc Trợ năng có quyền cao | **Đúng.** Cloak & Dagger (2017): Trợ năng + overlay điều khiển trọn vòng phản hồi UI, lấy PIN, cài app. Diao 2019: lỗi thiết kế khung Trợ năng. AccessiLeaks 2019: 72% app tài chính top lộ thông tin. |

Không tải được (paywalled hoặc nguồn chặn tải tự động): Tey 2013 (NDSS), Serwadda & Phoha 2013, Biggio 2013, Pisani 2016, Jain 2005, ISO 19795-1, Patel 2016, Stylios 2021, Vijayanand 2025. DOI có trong `reports/`.

## 4. Phát hiện quan trọng nhất

**ActReal (Wang 2026, preprint)**: tác nhân cấp hệ thống có đặc quyền có thể sinh đồng thời chạm và cảm biến IMU khớp thời gian. Tỷ lệ tấn công thành công trung bình 77,5% trên các bộ phát hiện dựa vào quỹ đạo chạm/thời gian, và **vẫn 71,1% khi bộ phát hiện dùng cả chạm lẫn IMU**. Nghĩa là mã độc đủ tinh vi sẽ qua mặt được lớp "người hay máy". Đây là rào cản lớn hơn mọi con số EER.

Các điểm khác:
- Các con số tốt nhất đến từ điều kiện thuận lợi (Zheng: 85 lượt đăng ký, nhiều cảm biến; BioTouchPass2: 217 người, RNN). Nhịp có ~25 người, một điện thoại, 3–5 lượt, **không có áp lực** (Pointer Events trả 0.5). Kỳ vọng thực tế **10–15% EER**.
- Tấn công bắt chước (kịch bản B) có số liệu cụ thể (10–15% EER) và nên nằm trong slide.
- Với bot chưa từng thấy, bộ phân loại học trên bot sinh sẵn giảm mạnh (BeCAPTCHA, BeCAPTCHA-Type: few-shot là thách thức). Huấn luyện và kiểm thử cùng 4 bộ sinh bot của đội sẽ cho số quá đẹp.
- Eberz 2017: EER trung bình che lỗi có hệ thống, cần báo phân bố theo từng người.
- Ahmed 2026: báo cáo sai số tại điểm vận hành (FAR@FRR) kèm khoảng tin cậy, không báo ROC-AUC đơn lẻ.

## 5. Kết luận

1. **Hướng đi có nền học thuật thật.** Nhịp gõ, vị trí chạm khi nhập PIN và vuốt phân biệt được người với người (EER vài % đến ~10%) và người với bot ngây thơ. Các con số trong kế hoạch phần lớn khớp paper.
2. **Chỉ nên là một tín hiệu rủi ro, không phải cổng xác thực.** Chính Touchalytics, Zheng và FETA đều nói vậy. Thiết kế `step_up` thay vì chặn cứng là đúng.
3. **Phần chắc nhất khi demo là bắt bot ngây thơ** (chiến thuật 1–2, `adb`, mã độc cơ bản). Đây là thao tác thực tế nhất của mã độc Trợ năng hiện nay.
4. **Phần yếu nhất là bot thích nghi** (chiến thuật 3–4, ActReal). Cần nói thẳng trong pitch, thêm kiểm tra phát lại, và đo bằng nguồn bot độc lập, không phải bộ sinh dùng để huấn luyện.
5. **Giá trị khác biệt**: minh bạch lý do, `step_up`, API mở dùng cho bất kỳ ví nào, và đánh giá trung thực theo FETA. Pitch theo hướng đó, không hứa hẹn con số.

## 6. Việc cần làm

| Ưu tiên | Việc |
|---|---|
| 1 | Đăng ký thi và gửi câu hỏi cho BTC **trước 23:59 27/11** |
| 2 | Ví demo web + SDK Pointer Events + bàn phím PIN tự vẽ (đang chặn mọi thứ khác) |
| 3 | Thu dữ liệu thật: ≥ 2 lần ngồi, một điện thoại, có phiếu đồng ý |
| 4 | Backend: kiểm tra "trùng phiên cũ" để bắt chiến thuật 3 |
| 5 | Mô hình 1 (LightGBM/RF), giữ riêng nguồn bot `adb` làm tập kiểm thử độc lập |
| 6 | Hiệu chỉnh `owner.py` (ánh xạ d=2 → 0,5 đang quá dễ dãi) trên dữ liệu thật |
| 7 | Đánh giá: FAR@FRR 5%, DET, khoảng tin cậy, phân bố lỗi theo người, bắt bot theo chiến thuật |
| 8 | Slide ≤10 trang, video ≤3 phút, PDF 1 trang, README khai báo tài sản/OSS/công cụ AI. Nộp trước **23:59 03/12** |
