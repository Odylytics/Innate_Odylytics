# Innate — Nghiên cứu phần AI

> 24/11/2026. Phạm vi: lõi AI phía sau Innate. Web/demo do nhóm làm sau, không nằm trong tài liệu này.
> Nền: [`paper-report.md`](paper-report.md), [`notes/`](notes/), [`tech-notes.md`](tech-notes.md). Độ tin cậy ghi theo từng ý: **[paper]** đã đọc trong PDF của đội, **[search]** chỉ thấy tóm tắt kết quả tìm kiếm, **[suy luận]** ý của tôi, chưa ai kiểm chứng.

## 1. Bài toán AI

Từ một phiên thao tác (chạm PIN, vuốt, nhịp màn hình), cộng ngữ cảnh giao dịch, trả về một quyết định `allow | step_up | hold` kèm lý do. Ba bài con:

| Bài | Đầu vào | Đầu ra | Dữ liệu huấn luyện có sẵn |
|---|---|---|---|
| **A. Người hay máy** | Một phiên | P(người) | Phiên người + phiên bot sinh ra |
| **B. Có phải chủ** | Một phiên + 3–5 phiên đăng ký của chủ | Điểm khớp | Chỉ phiên chủ (few-shot), có thể thêm dân số |
| **C. Hợp nhất + giải thích** | A, B, người nhận mới, số tiền | Rủi ro + lý do | Ít hoặc không có nhãn gian lận |

## 2. Hiện trạng mã (backend/app/scoring)

| Bài | Đang làm | Điểm yếu đã thấy khi đọc mã |
|---|---|---|
| A | Luật: CV thời gian, chạm đúng tâm, vuốt thẳng; lấy **max** tín hiệu nghi ngờ | Không học; mỗi bot qua một ngưỡng là lọt; chiến thuật 3 bắt 0%, chiến thuật 4 bắt 5–30% (người giả) |
| B | Mẫu chuẩn + scaled Manhattan; sàn σ cố định; ánh xạ `1/(1+e^{2(d−2)})` | σ ước lượng từ 3–5 mẫu rất nhiễu; ánh xạ chưa hiệu chỉnh nên quá dễ dãi |
| C | Tổng có trọng số 0,40/0,35/0,15/0,10; ngưỡng 0,25/0,55 | Trọng số chọn tay, chưa có dữ liệu để kiểm |

## 3. Kết quả nghiên cứu theo thành phần

### A. Người hay máy

- **Tiền lệ:** BeCAPTCHA dùng chạm + gia tốc kế cho một thao tác kéo thả; hệ đa phương thức gấp đôi hiệu quả ở chế độ "agnostic" (bot chưa thấy) và giữ tỷ lệ bắt bot trên 90% khi huấn luyện đa dạng [paper]. Huấn luyện chỉ trên một kiểu bot rồi gặp kiểu khác thì tụt mạnh [paper].
- **Hệ quả thiết kế:** đánh giá bằng **leave-one-tactic-out** (huấn luyện trên 3 chiến thuật, kiểm thử trên chiến thuật còn lại), không kiểm thử trên cùng bộ sinh với tập huấn luyện [suy luận, dựa trên kết quả agnostic của BeCAPTCHA].
- **Tín hiệu đề xuất bổ sung** (đều [suy luận], cần đo): độ lượng tử hoá thời gian (sự kiện bơm thường tròn mili-giây, đều), số điểm giữa down và up, dao động toạ độ trong lúc giữ, biến thiên `w`/`h`, entropy nhiễu. Một bài blog ngành cũng cho rằng bot thiếu "tính ngẫu nhiên và trôi chảy" của chạm thật [search, Radware].
- **Mô hình:** bắt đầu bằng Random Forest hoặc LightGBM trên ~40 đặc trưng (có tiền lệ trong BeCAPTCHA-Type [paper]). Dữ liệu ít nên **ưu tiên mô hình đơn giản, ít tham số**: một nghiên cứu nhỏ báo thuật toán thống kê vượt học sâu khi dữ liệu nhỏ [search]. Thêm **one-class** (huấn luyện chỉ trên người) để bắt bot lạ [suy luận].
- **Giới hạn đã biết:** ActReal (2026, preprint) cho thấy tác nhân cấp hệ thống sinh chạm + IMU khớp thời gian thành công 71–77% [paper]. Lớp A mạnh nhất với bot ngây thơ; phải nói rõ.
- **Phát hiện phát lại (chiến thuật 3):** không cần học. Đo khoảng cách tới các phiên cũ **của cùng chủ**; người thật không lặp lại nhịp sát ±5% [suy luận]. Ngưỡng lấy từ phân bố khoảng cách giữa các phiên thật của cùng người.

### B. Có phải chủ (few-shot)

| Hướng | Dữ liệu cần | Bằng chứng | Quyết định |
|---|---|---|---|
| Scaled Manhattan (đang dùng) | 3–5 mẫu | Tốt nhất trong 14 bộ phát hiện, EER ~9,6% trên keystroke máy tính [paper] | **Giữ làm baseline** |
| Mahalanobis + **co rút hiệp phương sai** | 3–5 mẫu | Với ít mẫu so với số chiều, ước lượng MLE kém; co về đường chéo là cách phổ biến, chọn tham số bằng cross-validation [search, nghiên cứu vuốt] | **Thử**; đối chiếu với Manhattan |
| Co rút về **trung bình/phương sai dân số** (empirical Bayes) | 3–5 mẫu + tập dân số | Không tìm thấy nguồn áp dụng đúng cho keystroke few-shot [search, khoảng trống] | **Ý chính của đội để thử** [suy luận]; có thể là đóng góp mới nhỏ |
| Siamese/triplet (TypeNet) | Hàng chục nghìn người | EER 9,2% trên bàn phím cảm ứng, văn bản tự do, >100k người [paper]; kế hoạch gốc ghi 10,7% (1 lượt) → 7,3% (5 lượt), số này tôi chưa đối chiếu lại với PDF | **Không khả thi** với ~25 người; chỉ pairwise nhỏ nếu còn thời gian |
| Transformer (Stragapede) | Dữ liệu Aalto lớn | EER 3,84% với 5 phiên đăng ký trên Aalto [paper] | Không áp dụng; ghi làm trần tham chiếu |
| Dữ liệu tổng hợp theo người (UserBoost) | Vài mẫu thật | Giảm số mẫu thật cần để đăng ký; nhưng nghiên cứu trên cử chỉ đồng hồ đeo tay, không phải màn hình chạm [search] | Ý tưởng sau cùng; không ưu tiên |

**Kỳ vọng thực tế** (từ Buschek và FETA [paper]): đăng ký cùng một phiên cho số lạc quan gấp đôi; đánh giá nghiêm làm EER từ 4,9% lên 13,8%. Với ~25 người và 3–5 lượt, mục tiêu hợp lý là **EER 10–15%**, báo kèm khoảng tin cậy.

**Hiệu chỉnh điểm:** thay ánh xạ logistic cố định bằng ánh xạ học từ dữ liệu (Platt hoặc isotonic trên phân bố khoảng cách của chủ so với người lạ) [suy luận]. Báo cáo ở điểm vận hành FAR@FRR 5% theo ISO/IEC 19795-1 [paper, qua ghi chú].

**An toàn của chính mẫu chuẩn:** cập nhật tự động có thể bị đầu độc (Biggio 2012; Lovisotto 2020: >70% thành công với <10 lần tiêm, phát hiện bắt >99% sau 2 lần) [paper]. Giữ trần độ trôi và thêm kiểm tra hướng trôi.

### C. Hợp nhất và giải thích

- Tổng có trọng số sau chuẩn hoá (z-score/tanh) là phương pháp chuẩn; tanh chịu ngoại lai tốt nhất [paper, Jain 2005 qua ghi chú]. Freeman 2016 (LinkedIn): kết hợp tín hiệu có trọng số học được nâng AUC 0,913 → 0,955 [paper].
- Khi **chưa có nhãn gian lận**, giữ trọng số tay nhưng chọn ngưỡng theo FRR 5%. Khi có nhãn từ dashboard, thay bằng hồi quy logistic có ràng buộc đơn điệu [suy luận].
- Giải thích: mỗi số hạng `w·x` đã là phần đóng góp chính xác nên không cần SHAP. Với LightGBM ở bài A dùng TreeSHAP (tính chính xác, đa thức) để lấy 2–3 đặc trưng lệch nhiều nhất [paper].

## 3b. Tín hiệu ngoài PIN: số tiền, người nhận, nội dung chuyển khoản

Một giao dịch có nhiều chỗ nhập hơn PIN. Mỗi chỗ là một nguồn tín hiệu, và mỗi chỗ có ràng buộc kỹ thuật khác nhau. **Khung mã đã có (24/11):** `SessionIn.fields`, đặc trưng ở `features.py`/`bot_features.py`, luật `text_set_without_keys` ở `human.py`, SDK thu ở `wallet.html`, 3 test. **Chưa có thí nghiệm nào trên dữ liệu ô nhập** và chưa có phiên thật nào; cần R9 trong [`research-plan.md`](research-plan.md). Hợp đồng dữ liệu: [`backend/README.md`](../../backend/README.md).

| Ô nhập | Tín hiệu | Ai nhập bằng gì | Ràng buộc đã biết | Dữ liệu/mô hình để thử |
|---|---|---|---|---|
| **Số tiền** | Nhịp gõ từng chữ số; nếu app tự vẽ bàn phím số thì có cả toạ độ chạm như PIN | Người: gõ từng phím. Bot: gõ phím, hoặc đặt thẳng văn bản | Ô số tiền thường dùng bàn phím số tự vẽ: khi đó đủ thông tin như PIN | Cùng phương pháp E1/E2/E9 |
| **Số tài khoản/số điện thoại người nhận** | Như trên; **dán** (paste) vs gõ; sửa lỗi | Người: gõ hoặc dán từ danh bạ/tin nhắn. Bot: điền thẳng | Bàn phím hệ thống: chỉ có thời gian giữa các lần gõ, **không có toạ độ** | StrokePIN không có; cần thu |
| **Tên/nội dung chuyển khoản (văn bản tự do tiếng Việt)** | Nhịp gõ văn bản tự do: độ dài chuỗi lớn nên nhiều tín hiệu hơn PIN rất nhiều | Người: gõ; bot: thường đặt thẳng văn bản hoặc gõ rất đều | Bàn phím hệ thống trên web: `keydown` thường trả `keyCode` 229, không đủ để biết phím và không có thời gian nhả đáng tin; native có `TextWatcher` (thời gian thay đổi văn bản) | **Đúng miền của dữ liệu Aalto (gõ tự do trên điện thoại) và mô hình TypeFormer (MIT, có trọng số)**; xem bên dưới |

**Hệ quả cho chọn mô hình:**
- **TypeFormer hợp với ô văn bản tự do** (nội dung chuyển khoản, tên), không hợp với PIN. Nó học chuỗi gõ dài trên bàn phím điện thoại và cho embedding để xác minh chủ. Với PIN 6 phím thì thống kê (E2/E9) vẫn hợp hơn. Đề xuất E8 chuyển sang ô văn bản tự do: so TypeFormer với baseline thống kê trên dữ liệu Aalto (đã có link, xem `datasets.md`) rồi trên dữ liệu thu của đội.
- **Tín hiệu người/máy mạnh nhất có thể nằm ở đây:** dịch vụ Trợ năng có API đặt thẳng văn bản vào ô (`ACTION_SET_TEXT`) mà **không phát sự kiện phím**, nên văn bản "xuất hiện" không kèm nhịp gõ. Tôi chưa kiểm chứng việc mã độc cụ thể (RedHook, Gigabud...) dùng cách nào, và cần đo trên máy thật (R9).
- **Một phiên nhiều ô cho nhiều tín hiệu hơn một PIN,** nên có thể cải thiện điểm "chủ" (điểm yếu lớn nhất ở E9) bằng cách gộp nhiều nguồn: kỳ vọng nhưng **chưa được đo**.

**Quyền riêng tư (quan trọng hơn với ô văn bản):** nội dung chuyển khoản và tên là dữ liệu cá nhân. Giữ nguyên tắc của PIN: **chỉ lưu thời gian và loại ký tự thô** (chữ, số, khoảng trắng, dấu), không lưu nội dung. Nếu dùng mô hình cần mã phím, chỉ dùng mã đã băm thô hoặc lớp ký tự. Ghi rõ trong phiếu đồng ý (R7) vì Luật BVDLCN 2025 coi sinh trắc là nhạy cảm.

**Ràng buộc nền tảng cần nói thật:** trên web di động, bàn phím hệ thống nằm ngoài trang nên SDK không thấy toạ độ chạm trên đó; chỉ có bàn phím tự vẽ (như PIN) cho toạ độ. SDK native cũng không đọc được toạ độ chạm trên bàn phím hệ thống. Đây là lý do nên để app tự vẽ bàn phím số cho số tiền nếu có thể.

## 4. Kiến trúc AI đề xuất (v1)

```
phiên ──► features (~40) ──┬─► A1: RF/LightGBM  (người vs bot, huấn luyện đa chiến thuật)
                           ├─► A2: one-class    (chỉ người; bắt bot lạ)
                           ├─► A3: phát lại     (khoảng cách tới phiên cũ của chủ)
                           └─► B : Mahalanobis co rút + Manhattan, hiệu chỉnh theo dân số
A1,A2,A3 ─► human_score   B ─► owner_match
human_score, owner_match, người nhận mới, số tiền ─► fusion (chuẩn hoá + trọng số) ─► allow / step_up / hold
                                                    └─► lý do (z-score / TreeSHAP) → câu tiếng Việt
```

## 5. Dữ liệu

| Nguồn | Dùng cho | Truy cập | Việc cần làm |
|---|---|---|---|
| **Dữ liệu đội tự thu** (~25 người × ≥2 lần ngồi, một máy) | Bài B và đánh giá cuối | Tự thu, có phiếu đồng ý | Soạn phiếu (R7); đây là nguồn chính |
| **HuMIdb** (600 người, 14 cảm biến, benchmark bot BeCAPTCHA) | Bài A | Cần ký thỏa thuận cấp phép và gửi email cho nhóm tác giả, rồi nhận tài khoản tải về; ~5 GB [search, một bản mirror trên GitHub, cần xác nhận ở trang gốc BiDAlab] | **Gửi yêu cầu sớm** vì có thời gian chờ |
| **Aalto typing37k** (37.370 người) | Ước lượng phương sai dân số cho co rút; kiểm tra sơ bộ đặc trưng thời gian | Dữ liệu tải được từ trang dự án [paper, ghi chú] | Kiểm tra giấy phép và kích thước |
| BB-MAS, BehavePassDB, MobileTouchDB, FETA | So sánh phụ | Giấy phép **chưa kiểm** | Kiểm trước khi dùng, ghi vào README |

Lưu ý: dữ liệu công khai không phải PIN trên bàn phím tự vẽ của đội, nên chỉ dùng để ước lượng phân bố dân số và kiểm tra sơ bộ, không thay cho dữ liệu của đội.

## 6. Kế hoạch thí nghiệm

| # | Giả thuyết | Quy trình | Chỉ số | Cần dữ liệu thật? |
|---|---|---|---|---|
| E1 | Mahalanobis co rút ≥ scaled Manhattan khi chỉ có 3–5 mẫu (**proxy đã chạy: không, kém hơn**; chưa lặp lại trên StrokePIN) | Cùng chia dữ liệu; so theo số lượt đăng ký 1/3/5 | EER, FAR@FRR 5% + khoảng tin cậy | Có |
| E2 | Co rút về dân số tốt hơn sàn σ cố định (**đã chạy trên DSL và StrokePIN (E9): giảm FAR@FRR 5% 7–16 điểm, EER không đổi**) | Ước lượng prior từ Aalto/dữ liệu đội; so với sàn hiện tại | Như E1 | Có (Aalto để lấy prior) |
| E3 | Hiệu chỉnh (Platt/isotonic) giảm FAR ở cùng FRR | Fit trên lần ngồi 1, kiểm thử lần ngồi 2 | FAR@FRR 5%, đường DET | Có |
| E4 | RF/LightGBM vượt luật ở bài A và **vẫn bắt bot lạ** (**proxy đã chạy: vượt luật với bot đã thấy; sập 0–23% với bot lạ do học tắt; IsolationForest tổng quát hoá tốt hơn**) | Leave-one-tactic-out trên 4 chiến thuật + `adb` làm tập kiểm thử riêng | Tỷ lệ bắt theo chiến thuật | Cần phiên người thật |
| E5 | Kiểm tra phát lại bắt chiến thuật 3 mà không từ chối chủ thật (**đã chạy: bắt 100% ở ±5–10% nhiễu, thua từ ±20%**) | Ngưỡng từ phân bố khoảng cách giữa các phiên thật của cùng người | Tỷ lệ bắt chiến thuật 3, FRR tăng thêm | Có |
| E6 | Tín hiệu mới (lượng tử hoá thời gian, dao động toạ độ) tách bot khỏi người | Thêm từng nhóm đặc trưng, đo cải thiện | Độ quan trọng, ΔAUC/ΔFAR | Có, cùng với dữ liệu `adb` |
| E7 | Chống đầu độc: drift cap + kiểm tra hướng trôi chặn được chuỗi "dạy dần" (**đã chạy: trần giới hạn chứ không loại bỏ; khuyến nghị đóng băng + cờ**) | Mô phỏng chuỗi phiên bot nằm trên ngưỡng cập nhật | Độ trôi mẫu sau n lần | Không (mô phỏng) |

**Quy tắc đánh giá** (FETA [paper]): tách theo thời gian, một điện thoại, không đưa dữ liệu kẻ gian vào huấn luyện bài B, leave-users-out nếu có mô hình so cặp, báo phân bố lỗi theo từng người (Eberz 2017).

## 6b. Kết quả thí nghiệm đã chạy (24/11)

**E1/E2 phiên bản proxy** trên CMU DSL-StrongPassword (bàn phím máy tính, mật khẩu cố định, 51 người, 31 đặc trưng thời gian): đăng ký bằng k mẫu ngẫu nhiên của phiên 1, kiểm thử trên phiên 5–8, 10 lần bốc mẫu mỗi người, khoảng tin cậy bootstrap theo người, prior dân số chỉ lấy từ **các người khác**. Mã: `research/experiments/e1_fewshot_owner.py`, bảng đầy đủ: `research/results/e1_dsl.md`.

| k mẫu đăng ký | EER baseline (Manhattan scaled) | Thay đổi EER của E2 (ν=5) | Thay đổi FAR@FRR 5% của E2 (ν=5) |
|---|---|---|---|
| 3 | 0,211 | −0,011 [−0,022, +0,001] | **−0,112 [−0,153, −0,071]** |
| 5 | 0,198 | +0,000 [−0,010, +0,011] | **−0,087 [−0,122, −0,051]** |
| 10 | 0,194 | +0,001 [−0,006, +0,010] | **−0,066 [−0,097, −0,036]** |

Đọc kết quả:
- **Co rút phương sai về dân số (E2) giảm FAR ở điểm vận hành FRR 5%** (khoảng 7–11 điểm phần trăm, khoảng tin cậy ghép cặp không chứa 0), mạnh nhất khi chỉ có 3 mẫu. **EER gần như không đổi**. Nghĩa là cải thiện nằm ở phần đuôi (chấp nhận ít chủ bị từ chối), đúng điểm vận hành mà Innate chọn.
- **Mahalanobis co rút về đường chéo (E1) kém hơn** baseline ở cả ba mức k (EER 0,21–0,25 so với 0,19–0,21).
- **Sàn σ hiện tại của `owner.py` gần như không khác baseline**, nên nó không đang giúp gì ở few-shot.
- EER ~0,20 cao hơn 9,6% của Killourhy & Maxion vì họ huấn luyện với 200 mẫu còn ở đây chỉ 3–10 mẫu và kiểm thử ở các phiên sau. Số này không so sánh trực tiếp được.

**Giới hạn cần nói thật:** dữ liệu là bàn phím máy tính, một mật khẩu cố định, không có vị trí chạm. Đây là bằng chứng cho **phương pháp** (co rút về dân số giúp khi ít mẫu), chưa phải cho số liệu của Innate. Cần lặp lại trên dữ liệu PIN của đội. E5 và E7 chạy sau, xem bên dưới.

### E5 — phát hiện phát lại (đã chạy, dữ liệu GIẢ)

Mã: `research/experiments/e5_replay.py`; bảng: `research/results/e5_replay.md`. Đã cài vào backend: `app/scoring/replay.py` (nối trong `/score`, phiên bị coi là phát lại thì `human_score` ≤ 0,1, lý do `replayed_session`, hành động `hold`), 1 test mới.

- Kẻ tấn công **thích nghi**: tăng nhiễu cả thời gian (±n) lẫn toạ độ (±max(2, 40n) px). Ngưỡng chọn để chỉ ~1% phiên người thật mới bị nhầm là phát lại.
- Khoảng cách hiện đang dùng: thời gian giữ/cách phím (tương đối) **cộng lệch tâm dx/dy**. Bản chỉ dùng thời gian yếu hơn rõ khi nhiễu cao.

| Mức nhiễu của kẻ tấn công | ±5% (như chiến thuật 3) | ±10% | ±15% | ±20% | ±30% |
|---|---|---|---|---|---|
| Bắt được, PIN 4 số | 1,00 | 1,00 | 0,59 | 0,07 | 0,00 |
| Bắt được, PIN 6 số | 1,00 | 1,00 | 0,99 | 0,36 | 0,00 |

- **Chiến thuật 3 gốc (±5%) bị bắt hoàn toàn**; kiểm tra phát lại bắt tốt đến nhiễu ±10–15%. Từ ±20–30% trở lên kẻ tấn công thắng, vì lúc đó phiên phát lại đã dao động ngang người thật. Đây là cuộc đua, không phải lời giải cuối.
- **Lỗi phát hiện nhờ thí nghiệm:** với PIN 4 số chỉ có 7 đặc trưng thời gian nên hai phiên thật có thể gần nhau tình cờ; khi so với 200 phiên cũ, tỷ lệ từ chối nhầm chủ lên **7,5%** (PIN 6 số: 0%). Backend đã giảm số phiên so xuống **50** (PIN 4 số còn 3,3%). Ví demo dùng PIN 6 số. Nếu đối tác dùng PIN 4 số, nên tăng ngưỡng hoặc giảm số phiên so thêm.
- **Giới hạn:** persona giả (độ dao động giữa các phiên do tôi/đội đặt ra), nên ngưỡng 0,085 **phải hiệu chỉnh lại trên dữ liệu người thật**. Chỉ so với phiên cũ **của cùng tài khoản**; phát lại một phiên chưa từng gửi lên máy chủ thì không bị bắt bởi kiểm tra này.

### E7 — đầu độc mẫu chuẩn (đã chạy, dữ liệu GIẢ)

Mã: `research/experiments/e7_poisoning.py`; bảng: `research/results/e7_poisoning.md`. **Chưa thay đổi `owner.py`**; đây là khuyến nghị để đội quyết.

Kẻ tấn công mạnh (tạo được vector đặc trưng tuỳ ý) mỗi bước gửi phiên sát ngưỡng cập nhật (owner ≥ 0,8). 100 cặp chủ/kẻ gian.

| Phòng thủ | Kẻ gian được chấp nhận sau tiêm (n=0 là 0,56) | Chủ được chấp nhận sau tiêm | Chủ trôi +50% (đếm ≥ 0,8) |
|---|---|---|---|
| Không trần | **1,00** (từ n=25) | **0,58** (chủ bị khoá ngoài) | 1,00 |
| Trần 1 sd/đặc trưng (**hiện tại**) | 0,85 | 1,00 | 0,67 |
| Trần 0,5 sd | 0,75 | 1,00 | 0,41 |
| Trần 0,25 sd | 0,67 | 1,00 | 0,28 |
| Đóng băng khi trôi trung bình > 0,5 sd (kèm cờ) | 0,77 | 1,00 | 0,68 |

Đọc kết quả:
- **Không có trần là thảm hoạ:** kẻ gian được chấp nhận 100% và chủ thật bị khoá ngoài (0,58). Việc `owner.py` có trần là cần thiết và đúng.
- **Trần giới hạn thiệt hại chứ không loại bỏ:** mẫu bị kéo tới trần rất nhanh (~10 lần tiêm) rồi dừng. Với trần hiện tại, kẻ gian được chấp nhận 0,85 so với 0,56 lúc đầu.
- **Đóng băng khi trôi có hướng** thắng trần 1 sd: kẻ gian 0,77 (thấp hơn 0,85) với cái giá ngang nhau cho chủ trôi mạnh (0,68 so với 0,67), và còn phát ra **cờ cảnh báo** cho vận hành. Trần chặt hơn (0,5; 0,25 sd) giảm kẻ gian nhưng làm chủ trôi mạnh bị từ chối nhiều (0,41; 0,28). **Khuyến nghị:** chuyển sang "đóng băng + cờ", khi đóng băng thì yêu cầu đăng ký lại.
- **Phát hiện quan trọng hơn cả E7:** ngay trước khi bị đầu độc (n=0), **56% phiên thật của kẻ gian đã được chấp nhận** (owner ≥ 0,5) trên persona giả. Đây là hậu quả của ánh xạ điểm `d=2 → 0,5` quá dễ dãi trong `owner.py`, đã ghi ở mục 2. Ưu tiên hiệu chỉnh (E3) cao hơn việc chọn cách chống đầu độc.
- **Giới hạn:** một chiến lược tấn công, persona giả, 100 cặp, chưa có khoảng tin cậy; kịch bản "chủ trôi" chỉ đổi thời gian. Cái giá của trần chỉ lộ ra ở ngưỡng 0,8; ở ngưỡng 0,5 mọi phòng thủ đều ~1,00 vì ngưỡng 0,5 quá dễ dãi.

### E4 — LightGBM cho bài người/máy (đã chạy, dữ liệu GIẢ)

Mã: `research/experiments/e4_human_bot_lgbm.py`; đặc trưng: `backend/app/scoring/bot_features.py` (vector độ dài cố định, ~30 đặc trưng, thiếu thì NaN); bảng: `research/results/e4_human_bot_lgbm.md`; mô hình huấn luyện trên dữ liệu giả lưu ở `research/models/` (**không dùng cho bản nộp**, và chưa nối vào backend). Ngưỡng chọn trên người ở tập validation để FRR = 5%, 3 lần sinh dữ liệu độc lập.

Tỷ lệ bot bị bắt (FRR thật ~5%):

| Mô hình | CT1 | CT2 | CT3 | CT4 |
|---|---|---|---|---|
| Luật baseline (`human.py`) | 1,00 | 1,00 | 0,04 | 0,01 |
| LightGBM, **thấy cả 4 chiến thuật** khi huấn luyện | 1,00 | 1,00 | 0,85 | 0,97 |
| LightGBM, **bỏ đúng chiến thuật đó** khỏi huấn luyện | **0,00** | 1,00 | 0,07 | 0,23 |
| IsolationForest (chỉ huấn luyện trên người), chiến thuật lạ | 1,00 | 1,00 | 0,12 | 0,47 |
| Bộ kết hợp (LightGBM hoặc IsolationForest), chiến thuật lạ | 1,00 | 1,00 | 0,11 | 0,41 |

Đọc kết quả:
- **Khi mô hình đã thấy loại bot**, LightGBM hơn hẳn luật baseline (chiến thuật 3: 0,85 so với 0,04; chiến thuật 4: 0,97 so với 0,01). Con số đẹp này chủ yếu phản ánh việc nó học được **dấu vết của bộ sinh dữ liệu**, nên không dùng cho slide.
- **Khi gặp bot lạ, LightGBM sập**: bỏ chiến thuật 1 khỏi huấn luyện thì bắt **0%** (AUC 0,50) dù đó là bot ngây thơ nhất. Tôi đã kiểm tra: đó là **học tắt**. Trên dữ liệu giả, người luôn có bước thời gian vuốt đều (`swipe_dt_cv = 0`), còn chiến thuật 2 có nhiễu nên `swipe_dt_cv > 0`; cây chọn đúng điều kiện đó để tách hoàn toàn chiến thuật 2. Chiến thuật 1 cũng có `swipe_dt_cv = 0` nên bị xếp là người (P(người) = 0,971 cố định). Đây là rủi ro thật với dữ liệu thật: bot do script sinh ra khác người ở những chi tiết tầm thường, mô hình học chi tiết đó và không tổng quát hoá.
- **IsolationForest (chỉ học từ người) tổng quát hoá tốt hơn với bot lạ** (chiến thuật 1, 2: 100% dù chưa từng thấy; chiến thuật 4: 38–47%, dao động giữa các lần chạy vì IsolationForest ngẫu nhiên; lần chạy lại sau khi thêm đặc trưng ô nhập cho 0,47 thay vì 0,38). Vì vậy giữ nó trong bộ kết hợp. Bộ kết hợp về cơ bản bằng mô hình tốt hơn trong hai mô hình ở từng trường hợp.
- **Chiến thuật 3, 4 (bot giống người) vẫn khó với bot lạ**: bắt 11–41%. Chiến thuật 3 nên giao cho kiểm tra phát lại (E5), không phải cho phân loại.
- Bỏ nhóm kích thước chạm (`tap_w/h`) gần như không đổi kết quả trên dữ liệu giả; nhóm này vẫn cần kiểm chứng trên thiết bị thật (R2).
- Đặc trưng quan trọng nhất: `swipe_v_peak_ratio`, `swipe_lateral_dev`, `dy_std`, `tap_w_std`, `dx_std`. Hầu hết là đặc trưng vuốt/lệch tâm do bộ sinh quyết định, nên cần soi lại với dữ liệu thật.

**Hệ quả:** bài người/máy cần **nhiều họ bot khác nhau do công cụ thật sinh ra** (`adb`, app `dispatchGesture`, ít nhất vài kiểu), và người thật. Chỉ khi đó đánh giá "bỏ một họ bot" mới có nghĩa.

### Open weights có sẵn (đã kiểm chứng ngày 24/11 qua GitHub API)

| Ứng viên | Giấy phép | Có trọng số? | Dùng cho | Khớp với Innate? |
|---|---|---|---|---|
| **TypeFormer** (`gstrag/TypeFormer`) | **MIT** | **Có**: `pretrained/TypeFormer_pretrained.pt` (14,8 MB) và `preliminary_transformer_pretrained.pt` (3,7 MB) | Bài B (xác minh chủ qua embedding gõ phím di động) | Một phần: xem bên dưới |
| TypeNet, SwipeFormer, KVC, MobileTouchDB, HuMIdb (BiDAlab) | **Không có giấy phép** trên repo | **Không**: repo chỉ có README/hình, dữ liệu cấp qua thỏa thuận email | | Không thể dùng làm trọng số |
| Mô hình cho bài A (người/máy) | | **Không tìm thấy mô hình huấn luyện sẵn nào** | | Phải tự huấn luyện (LightGBM) |

Chi tiết TypeFormer: huấn luyện trên bộ gõ di động Aalto; đầu vào là chuỗi phím, mỗi phím 5 đặc trưng (thời gian giữ, giữa hai lần nhấn, giữa hai lần nhả, giữa hai phím, mã phím/255); đầu ra là embedding, xác minh bằng khoảng cách tới các embedding đăng ký. Bản sao về `research/external/TypeFormer` (commit `8bf1342`, gitignored; mã dựa trên torch 1.13 cũ).

**Khoảng cách miền cần kiểm chứng trước khi "lôi về tinh chỉnh":**
1. TypeFormer học **gõ văn bản tự do** (chuỗi dài, nhiều phím); PIN 6 số chỉ có 6 phím, rất ngắn.
2. Đầu vào của nó **không có vị trí chạm**, mà Buschek 2015 cho thấy đặc trưng không gian giảm 26–37% lỗi. Vứt thông tin này đi có thể phản tác dụng.
3. Fine-tune cần **dữ liệu PIN thật của đội** (chưa có). Với ~25 người, nguy cơ quá khớp cao; E2 đã đạt cải thiện chỉ bằng co rút thống kê.
4. Khai báo: dùng trọng số này phải ghi vào README nộp bài (tài sản có sẵn + trích dẫn bài báo) và cân nhắc việc Aalto là nguồn dữ liệu huấn luyện.

**Đề xuất E8:** nhúng phiên PIN qua TypeFormer (đệm chuỗi), so với Manhattan + co rút dân số (E2) trên **cùng dữ liệu PIN thật** theo cùng quy trình đánh giá. Chỉ chọn nếu thắng ở FAR@FRR 5%. Bản đầu có thể thử zero-shot trên DSL, nhưng đó là bàn phím máy tính nên chỉ là kiểm tra đường ống.

### E9 — xác minh chủ trên PIN điện thoại THẬT (StrokePIN)

Đây là thí nghiệm đầu tiên trên **dữ liệu người thật, PIN 6 số, có toạ độ chạm**, chạy bằng **chính `features.py` và `owner.py` của backend**. Dữ liệu: StrokePIN (97 người, 17.895 lượt hợp lệ, 20 PIN chung, ngồi/đi; CC BY-NC-SA 4.0; xem `datasets.md`). Mã: `research/experiments/strokepin_loader.py`, `e9_strokepin_owner.py`; bảng: `research/results/e9_strokepin_owner.md`.

Thiết lập: đăng ký k=3 lượt **ngồi**; kiểm thử chủ (cùng tư thế hoặc đổi sang **đi**); kẻ gian **biết PIN** (người khác nhập cùng PIN); điểm gộp mọi cặp (người, PIN); CI 95% bootstrap theo người. Mỗi cặp chỉ có ~5 lượt ngồi, nên k=5 không có lượt ngồi còn lại để kiểm thử cùng tư thế.

**Cùng tư thế (ngồi), k=3, backend hiện tại (sd có sàn):**

| Bộ đặc trưng | EER | FAR @ FRR 5% |
|---|---|---|
| Thời gian | 0,201 [0,195, 0,208] | 0,697 |
| + lệch tâm | 0,166 [0,158, 0,177] | 0,734 |
| + lệch tâm + kích thước chạm | 0,158 [0,147, 0,167] | 0,718 |

**Đổi tư thế (ngồi → đi), k=3:** EER 0,32–0,36, FAR@FRR 5% 0,84–0,94.

Đọc kết quả:
- **Tín hiệu "chủ" có thật nhưng yếu với 3 lượt đăng ký:** EER 16–20% khi kẻ gian biết PIN. Ở điểm vận hành FRR 5%, **FAR vẫn 57–73%**: đa số kẻ gian lọt. Nghĩa là điểm "chủ" không thể làm cổng chặn; đúng với thiết kế `step_up` và với việc gộp thêm tín hiệu bot và ngữ cảnh. Con số này là số đo thật đầu tiên, nên thay thế kỳ vọng 10–15% rút ra từ paper.
- **Đổi tư thế phá gần hết tín hiệu** (EER 0,32–0,40, FAR@5% 0,75–0,94). Đăng ký chỉ khi ngồi rồi nhập khi đi gần như vô dụng; lệch tâm còn làm tệ hơn (0,32 → 0,36). Hệ quả thiết kế: đăng ký phải bao nhiều tư thế/ngữ cảnh, hoặc giảm trọng số điểm "chủ" khi phát hiện đổi tư thế (cảm biến chuyển động).
- **Lệch tâm và kích thước chạm cải thiện EER** (0,201 → 0,166 → 0,158), khớp với Buschek 2015. **Nhưng chưa cải thiện FAR@FRR 5%** (0,70 → 0,73 → 0,72, CI rộng).
- **Sd có sàn của `owner.py` hơn hẳn Manhattan scaled thuần** trên PIN thật (EER 0,158 so với 0,227 khi dùng cả ba nhóm đặc trưng). Trên DSL thì hai cách ngang nhau (E1/E2 proxy). Sàn có ích khi chỉ có 3 mẫu và PIN ngắn.
- **E2 (co rút phương sai về dân số) lặp lại trên dữ liệu thật:** giảm FAR@FRR 5% so với backend hiện tại, ghép cặp theo người: thời gian −0,140 [−0,161, −0,107]; thời gian + lệch tâm + kích thước −0,159 [−0,198, −0,117]; EER gần như không đổi (−0,001 và +0,005). Riêng bộ "thời gian + lệch tâm" EER **tệ hơn** +0,031 [+0,026, +0,037]. Hiệu ứng nhất quán với DSL: cải thiện nằm ở phần đuôi, không phải EER.

**Giới hạn quan trọng, số liệu trên bị thổi phồng ở hai điểm:**
1. **Khác thiết bị giữa các người.** 94 cặp kích thước phím khác nhau trên 97 người, nên nhiều khả năng mỗi người dùng một điện thoại. Lệch tâm và kích thước chạm vì thế mang cả thông tin **thiết bị**. Trong kịch bản B thật, kẻ gian cầm **đúng điện thoại của nạn nhân**, nên khác biệt này biến mất. Vì vậy cải thiện nhờ lệch tâm/kích thước (0,201 → 0,158) là cận trên; con số sát thực tế hơn là hàng "thời gian" (EER ~0,20).
2. PIN do người nghiên cứu giao (20 PIN chung, nhiều PIN yếu như 111111, 123456), người dùng không gõ PIN riêng đã thuộc; mỗi cặp chỉ ~5 lượt mỗi tư thế, đăng ký và kiểm thử trong cùng một đợt thu (chưa có khoảng cách nhiều ngày).

## 7. Thứ tự làm

1. **Gửi yêu cầu HuMIdb**, kiểm giấy phép Aalto (chạy nền, có thời gian chờ).
2. **E5 và E7** (không cần dữ liệu thật, sửa rẻ, lấy lại điểm cho chiến thuật 3 và độ an toàn mẫu).
3. Dựng **khung đánh giá** (chia theo thời gian, FAR@FRR, DET, khoảng tin cậy) chạy được trên dữ liệu giả, để khi có dữ liệu thật chỉ cần thay nguồn.
4. Khi có dữ liệu: E1 → E3 → E4 → E6 → E2.

## 8. Câu hỏi còn mở

1. Số lượt đăng ký thực tế tối thiểu để B tách được người ở mức chấp nhận được?
2. Tín hiệu bơm nào lộ ra cho SDK, và có khác nhau giữa web và native? (R1)
3. Co rút về dân số có thực sự giúp không? Không có nguồn xác nhận, cần đo.
4. Một số nguồn ở đây chỉ là tóm tắt kết quả tìm kiếm; cần đọc bản gốc UserBoost (arXiv 2407.09104), Ffinger (arXiv 2504.17271) và nghiên cứu vuốt Bayesian (arXiv 2008.01013) trước khi trích dẫn.

## Nguồn mới trong lượt này

- ActReal: https://arxiv.org/pdf/2608.30038
- UserBoost: https://arxiv.org/abs/2407.09104
- Contrastive Learning for Continuous Touch-Based Authentication: https://arxiv.org/abs/2504.17271
- Few-shot continuous authentication (Applied Sciences 12(20), 10365): https://www.mdpi.com/2076-3417/12/20/10365
- Swipe dynamics, Bayesian unsupervised: https://arxiv.org/abs/2008.01013
- Review of keystroke dynamics methods: https://arxiv.org/abs/2502.16177
- Radware, attestation + behavioural anomaly detection: https://www.radware.com/blog/application-protection/complementing-attestation-with-behavioural-anomaly-detection-in-mobile-applications/
- HuMIdb (mirror, quy trình cấp phép): https://github.imc.re/BiDAlab/HuMIdb
