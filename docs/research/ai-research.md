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
| E2 | Co rút về dân số tốt hơn sàn σ cố định (**đã chạy trên DSL và StrokePIN; bản triển khai được = chỉ thời gian, đã vào `owner.py`: FAR@FRR 5% 0,66 → 0,50, E10b**) | Ước lượng prior từ Aalto/dữ liệu đội; so với sàn hiện tại | Như E1 | Có (Aalto để lấy prior) |
| E3 | Hiệu chỉnh (Platt/isotonic) giảm FAR ở cùng FRR | Fit trên lần ngồi 1, kiểm thử lần ngồi 2 | FAR@FRR 5%, đường DET | Có |
| E4 | RF/LightGBM vượt luật ở bài A và **vẫn bắt bot lạ** (**đã chạy: E4 người giả quá lạc quan; E4b người thật: bắt 100% bot ngây thơ, CT3 26%, CT4 20–73%, bot lạ yếu**) | Leave-one-tactic-out trên 4 chiến thuật + `adb` làm tập kiểm thử riêng | Tỷ lệ bắt theo chiến thuật | Cần phiên người thật |
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

### E5b — hiệu chỉnh kiểm tra phát lại trên người thật (24/11)

Mã: `research/experiments/e5b_replay_real.py`; bảng: `research/results/e5b_replay_real.md`. Người thật StrokePIN (1.842 cặp người–PIN, 4–10 lượt cùng PIN, cả ngồi và đi), dùng chính `replay.distance` của backend; phát lại thích nghi với nhiễu thời gian ±n và toạ độ ±max(0,02; 0,4n) bề rộng phím.

- **Ngưỡng 0,085 (chọn trên người giả ở E5) cho FPR người thật 0,28% → 0,40% → 0,64% khi so với 3 → 5 → 8 phiên cũ**: tăng gần tuyến tính theo số phiên. Ngoại suy tuyến tính tới 50 phiên (backend đang so tới 50) cho **~3,7%**: không đo được vì dữ liệu chỉ có ~9 lượt mỗi cặp, đây là suy đoán. Vì phát lại bị `hold` thẳng nên mức này quá đắt.
- Phân vị khoảng cách người thật: 0,1% = 0,071; 1% = 0,094; trung vị 0,189. Khoảng cách trung vị của phiên phát lại: ±5% → 0,025; ±10% → 0,050; ±15% → 0,075; ±20% → 0,101.
- **Đã đổi ngưỡng mặc định sang 0,07** (FPR ~0,1% tại 8 phiên, ~0,7% ngoại suy tại 50). Cái giá: bắt 100% phát lại có nhiễu tới ±10% nhưng chỉ **29% ở ±15%** (ngưỡng cũ: 86%) và 0% từ ±20%. Kẻ tấn công thích nghi thêm nhiễu ≥15% vẫn qua mặt kiểm tra này; lúc đó phiên trông như một người khác và chỉ còn điểm "chủ" (yếu) cản lại.
- **Giới hạn:** lịch sử trong dữ liệu ngắn (~9 lượt, một đợt thu), nên hiệu ứng nhiều phiên cũ phải đo lại bằng dữ liệu của đội (lịch sử dài, nhiều ngày). Người thật ở đây gõ PIN do người nghiên cứu giao, không phải PIN riêng đã thuộc, nên có thể ít đều hơn hoặc nhiều hơn người dùng thật.

### E11 — người/máy trên ô văn bản tự do, người thật Aalto (24/11)

Mã: `research/experiments/aalto_note_extract.py` (trích nhịp gõ từ mysqldump, **chỉ giữ thời gian, loại sự kiện, lớp ký tự, không giữ nội dung**), `e11_text_field_bots.py`; bot: `attacker/nhip_attacker/fields.py` (`generate(..., with_fields=True)`); bảng: `research/results/e11_text_field_bots.md`. Người: **33.522 câu gõ thật của 2.260 người**, chia theo người. Bot chỉ ở ô `note` (Aalto không có ô số tiền/người nhận), 4 chiến thuật: (1) đặt thẳng văn bản kiểu `ACTION_SET_TEXT`, (2) gõ đều qua công cụ tự động, (3) phát lại nhịp một người thật, (4) lấy mẫu khoảng cách từ dân số.

Nhịp gõ thật (để hiệu chỉnh): khoảng cách giữa phím trung vị 223 ms (phân vị 5–95%: 84–1394 ms), độ biến thiên trong một câu trung vị **0,92** (rất không đều), tỷ lệ xoá trung vị 3,4%, 63% câu không có sự kiện dự đoán/dán.

Tỷ lệ bot bị bắt ở FRR 5% (LightGBM, đặc trưng `fld_*` hiện có trong backend; trong ngoặc: thêm đặc trưng mở rộng):

| | CT1 đặt thẳng văn bản | CT2 gõ đều | CT3 phát lại | CT4 lấy mẫu dân số |
|---|---|---|---|---|
| Đã thấy loại bot đó | **1,00** | **0,99** | 0,06 | 0,31 (0,58) |
| **Chưa từng thấy** | 1,00 | **0,00** (AUC 0,20) | 0,05 | 0,04 |
| IsolationForest (chỉ người) | 0,00 | 0,00 | 0,05 | 0,01 |
| Luật hiện tại của backend | 0,00 | 0,00 | 0,00 | 0,00 |

Đọc kết quả:
- **Hai bot ngây thơ (đặt thẳng văn bản, gõ đều) bị bắt ~100% khi mô hình đã thấy chúng**, vì nhịp người thật rất bất đều (CV 0,92 so với 0,35 của bot gõ đều).
- **Bot lạ là điểm yếu:** bỏ chiến thuật 2 khỏi huấn luyện thì bắt **0%** (AUC 0,20: tệ hơn đoán ngẫu nhiên, bot gõ đều trông "người hơn người" với mô hình học trên các bot khác). Đây là cùng bài học như E4/E4b: mô hình giám sát chỉ giỏi với họ bot đã thấy. IsolationForest (chỉ học từ người) **không cứu được** ở ngưỡng FRR 5% (bắt 0% hai bot ngây thơ, dù AUC 0,71–0,85).
- **Bot giống người không bắt được bằng nhịp:** phát lại (CT3) 6%, đúng như dự đoán (nhịp đó là của một người thật). Lấy mẫu dân số (CT4) 31%; **đặc trưng mở rộng (phân vị khoảng cách, độ lệch liên tiếp, độ lệch chuẩn) nâng lên 58% (AUC 0,85 → 0,93)**: bộ `fld_*` hiện có thiếu thống kê nhịp. Chưa thêm vào `bot_features.py` vì mô hình đang triển khai chưa huấn luyện trên dữ liệu có ô nhập.
- **Luật backend hiện tại bắt 0% ở ô ghi chú là có chủ ý:** ô ghi chú đặt văn bản không qua phím chỉ bị trừ nhẹ (autofill, gõ giọng nói và dán đều hợp lệ). E11 không đánh giá ô số tiền (không có dữ liệu người thật), nên luật "`set_text` ở ô số tiền = máy" **vẫn chưa kiểm chứng**.

**Giới hạn, số liệu lạc quan ở các điểm sau:**
1. Tôi chỉ giữ câu người thật có ≥ 15 phím, nên **loại sẵn** người nhập bằng giọng nói, dán hay autofill. Vì vậy việc tách "đặt thẳng văn bản" khỏi người thật (CT1) dễ hơn thực tế. Ngoài đời, nhiều người nhập ô ghi chú mà không có phím nào.
2. Dữ liệu Aalto là **chép lại câu mẫu tiếng Anh** trên điện thoại (bài kiểm tra tốc độ gõ), khác với **soạn** nội dung chuyển khoản tiếng Việt; nhịp soạn có nhiều ngừng suy nghĩ hơn.
3. Bot vẫn do bộ sinh tạo, một ô duy nhất, chưa có bot thật.

### E12 / E12b — mô hình xác minh chủ HỌC ĐƯỢC (việc A, 24/11)

Mã: `research/experiments/e12_learned_owner.py` (`--no-contact` cho E12b), `train_owner_model.py`; bảng: `research/results/e12_learned_owner.md`, `e12b_learned_owner_no_contact.md`. StrokePIN, chia theo **người** (58 huấn luyện / 39 kiểm thử, 3 cách chia), đăng ký 3 lượt ngồi, kẻ gian biết PIN, prior chỉ từ người huấn luyện. Thay `mean(|z|)` (mọi đặc trưng ngang nhau) bằng bộ phân loại học trên vector |z|.

| | Cùng tư thế: EER | Cùng tư thế: FAR@FRR5% | Đổi tư thế: EER | Đổi tư thế: FAR@FRR5% |
|---|---|---|---|---|
| E12 (có kích thước chạm) baseline | 0,149 | 0,558 | 0,354 | 0,943 |
| E12 LightGBM | 0,108 | 0,200 | 0,264 | 0,675 |
| **E12b (bỏ kích thước chạm)** baseline | 0,161 | 0,573 | 0,363 | 0,944 |
| E12b hồi quy logistic | 0,206 (**+0,045, tệ hơn**) | 0,510 (khoảng tin cậy chứa 0) | 0,319 | 0,737 |
| **E12b LightGBM** | 0,158 (−0,003, không có ý nghĩa) | **0,375 (−0,198 [−0,363, −0,085])** | **0,309 (−0,053 [−0,078, −0,033])** | **0,708 (−0,236)** |

Đọc kết quả:
- **E12 đẹp vì nhiễu thiết bị:** trọng số lớn nhất hồi quy học được là `tap_w_mean` và `tap_h_mean` (kích thước vùng chạm = khác máy giữa các người). Kẻ gian trong StrokePIN dùng máy *của họ*; kịch bản B thật thì kẻ gian cầm đúng máy nạn nhân nên hiệu ứng này mất. **Số đáng tin là E12b** (đã bỏ kích thước chạm), không phải E12.
- **E12b: LightGBM học vẫn có lợi thật**, chủ yếu ở điểm vận hành FRR 5% (kẻ gian lọt 0,573 → 0,375) và khi đổi tư thế; **EER cùng tư thế không cải thiện**. Hồi quy logistic (trọng số tuyến tính) **không** tốt hơn khoảng cách cũ về EER.
- **Đã nối vào backend** (`app/scoring/owner_model.py`, `app/models/owner_lgbm.*`, tuỳ chọn; thiếu thư viện, thiếu file hoặc PIN không đủ 6 phím thì dùng điểm khoảng cách cũ; `NHIP_OWNER_MODEL=off` để tắt). Điểm được ánh xạ để ngưỡng FRR 5% = 0,5. Trên 29 người giữ lại: FRR 5,0% cùng tư thế, kẻ gian lọt 0,359; **đổi tư thế chủ bị từ chối 22,1%**.
- **Giới hạn:** huấn luyện trên 97 người công khai, mỗi người một máy (nhiễu thiết bị còn lại trong lệch tâm do chuẩn hoá theo cỡ phím ước lượng), PIN 6 số do người nghiên cứu giao, một đợt thu. Mô hình **tạm thời**; phải huấn luyện lại bằng dữ liệu của đội.

### E13 — "Innate Challenge": nhiều phím hơn thì tốt hơn? (24/11)

Mã: `research/experiments/e13_length_effect.py`; bảng: `research/results/e13_length_effect.md`; thiết kế: [`../plan/innate-challenge.md`](../plan/innate-challenge.md). Người thật gõ câu trên điện thoại (Aalto, chỉ thời gian), cắt ở n phím đầu, **câu kiểm thử khác nội dung câu đăng ký**.

| Số phím n | Nhận chủ: EER | FAR@FRR5% | Bắt bot gõ đều (AUC) | Bắt bot lấy mẫu dân số (AUC) |
|---|---|---|---|---|
| 6 | 0,364 | 0,807 | 0,915 | 0,719 |
| 10 | 0,337 | 0,733 | 0,969 | 0,764 |
| 20 | 0,279 | 0,591 | 0,996 | 0,848 |
| 30 | 0,245 | 0,489 | 0,995 | 0,891 |

Nhiều phím hơn cải thiện rõ rệt cả nhận chủ lẫn bắt bot, khoảng tin cậy không chồng. **Nhưng số tuyệt đối vẫn yếu** (EER 24,5% ở 30 phím với 6 đặc trưng nhịp và 3 câu đăng ký); **không so được với PIN** (Aalto không có thời gian giữ phím, toạ độ); người **chép câu mẫu tiếng Anh**, không gõ chuỗi chữ-số ngẫu nhiên lúc căng thẳng; bot là giả; chưa đo gộp PIN + câu và chưa đo ma sát.

### Việc B — huấn luyện lại bằng dữ liệu của đội (quy trình sẵn sàng, 24/11)

`research/experiments/train_human_model.py --export export.jsonl [--no-strokepin] [--no-generated]` nhận đầu ra của `GET /v1/export` (role `genuine`/`impostor` = người, role `bot` = bot **thật**), chia người theo `participant_id`, ngưỡng FRR 5% trên người validation, báo bắt bot thật ở tập test. Mặc định (không cờ) cho **mô hình giống hệt từng byte** bản đang triển khai. Đã thử nhánh `--export` bằng dữ liệu đội **giả lập**: chạy đúng (kết quả trên dữ liệu giả không có ý nghĩa). **Việc huấn luyện thật chưa làm được vì đội chưa có dữ liệu.**

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

### E4b — người/máy với NGƯỜI THẬT (đã chạy; người thật, bot vẫn giả)

Mã: `research/experiments/e4b_human_bot_real.py`; bảng: `research/results/e4b_human_bot_real.md`. Người = phiên PIN thật từ StrokePIN, **chia theo người** (train 40 / val 12 / test 30 / kho kẻ tấn công 15, không trùng người, 3 cách chia). Bot = 4 chiến thuật của nhóm, dựng trên PIN thật và phân bố người thật; chỉ so phần PIN (bot bị bỏ vuốt/màn hình vì StrokePIN không có). Ngưỡng FRR 5% chọn trên người ở tập validation.

| Tỷ lệ bot bị bắt | CT1 | CT2 | CT3 | CT4 | FRR thật |
|---|---|---|---|---|---|
| Luật baseline (`human.py`) | 1,00 | 1,00 | 0,05 | 0,01 | 0,058 |
| LightGBM, đã thấy cả 4 chiến thuật | 1,00 | 1,00 | **0,26** | **0,73** | 0,059 |
| LightGBM, **bỏ đúng chiến thuật đó** | 1,00 | 0,56 | 0,09 | 0,20 | 0,059 |
| IsolationForest (chỉ người), có kích thước chạm | 1,00 | 0,86 | 0,07 | 0,03 | 0,046 |
| IsolationForest, **không** kích thước chạm | **0,33** | **0,31** | 0,07 | 0,03 | 0,056 |

So với E4 (người giả):
- **E4 giả đã quá lạc quan.** Chiến thuật 3: 0,85 → **0,26**; chiến thuật 4: 0,97 → **0,73**. Với người thật thì bot giống người khó bắt hơn nhiều.
- **Hiện tượng "sập 0%" của E4 biến mất** (bỏ CT1 vẫn bắt 100%): nó là học tắt do chi tiết vuốt của bộ sinh người giả, đúng như đã chẩn đoán. Nhưng **bot lạ vẫn khó**: bỏ CT2 còn 0,56, bỏ CT3 còn 0,09, bỏ CT4 còn 0,20.
- **IsolationForest chỉ tách được bot ngây thơ nhờ kích thước chạm:** bỏ nhóm này thì chiến thuật 1, 2 chỉ còn 0,31–0,33. Bot dùng `w=h=1` quá dễ lộ ở dữ liệu giả; bot thật có thể đặt giá trị bất kỳ, và trình duyệt cũng trả 1 cho người thật khi máy không đo được (R2). Không được dựa vào nhóm này.
- **LightGBM giám sát vẫn bắt chiến thuật 1, 2 ở 100% kể cả không có kích thước chạm** (nhờ nhịp đều và đúng tâm), nên đây là phần chắc nhất.
- **FRR thật 5,8–6,4% so với mục tiêu 5%:** người test dùng thiết bị khác người validation. Ngưỡng cần hiệu chỉnh theo thiết bị.

**Hệ quả:**
1. Bài người/máy chắc chắn bắt được **bot ngây thơ** (chiến thuật 1, 2; `adb`, script). Đây là con số có thể nói.
2. **Chiến thuật 3 (phát lại) phải giao cho kiểm tra phát lại (E5)**, không phải cho phân loại: phân loại chỉ bắt 9–26%.
3. **Chiến thuật 4 (lấy mẫu từ dân số) chỉ bắt 20–73%** tuỳ có thấy hay chưa. Nói thẳng là giới hạn.
4. Vẫn là **bot giả**: chưa có bot thật. Kết quả trên bot thật có thể khác theo cả hai hướng.

### E10 / E10b — co rút về dân số, bản triển khai được, đã vào `owner.py` (24/11)

Mã: `research/experiments/e10_deployable_prior.py` (so các biến thể), `e10b_backend_path.py` (kiểm tra chính mã backend), `make_population_prior.py` (sinh prior); bảng: `research/results/e10_deployable_prior.md`, `e10b_backend_path.md`. Dữ liệu: StrokePIN, người thật, prior **bỏ-một-người**.

E9 dùng prior riêng theo (PIN, tư thế), mà khi chạy thật không biết trước PIN. E10 thử prior **dùng chung mọi PIN và cả hai tư thế**:
- **Chỉ thời gian:** prior chung giảm FAR@FRR 5% ~8–11 điểm, gần bằng bản cận trên theo PIN (−0,11).
- **Thêm lệch tâm: co rút cho lệch tâm làm TỆ HƠN** (EER +0,04, FAR +0,06; kể cả prior theo PIN cũng làm EER tệ +0,03). Độ dao động lệch tâm khác nhau quá nhiều giữa người và thiết bị. **Đây là điều chỉnh so với kết luận E9** (khi đó tôi nói E2 nên áp dụng cho mọi đặc trưng).
- **Biến thể lai thắng:** co rút **chỉ cho thời gian**, giữ sd có sàn cho lệch tâm.

**Đã áp dụng vào `owner.py`** (hàm `_sd`, `population_prior.json`, ν=5): chỉ `pin_hold_i`, `pin_flight_i`, và `pin_total` (chỉ khi PIN đúng 6 phím); có thể tắt bằng `NHIP_POP_PRIOR=off`.

E10b chạy **chính `owner.build_template`/`owner.score`** với mọi đặc trưng nhận dạng như backend thật, k=3:

| Tư thế kiểm thử | Co rút | EER | FAR @ FRR 5% |
|---|---|---|---|
| Cùng (ngồi) | tắt (cũ) | 0,153 | 0,663 |
| Cùng (ngồi) | **bật** | 0,146 | **0,495** |
| | chênh lệch ghép cặp | −0,007 [−0,011, −0,004] | **−0,167 [−0,190, −0,114]** |
| Đổi (đi) | tắt / bật | 0,352 / 0,355 | 0,943 / 0,943 |

Đọc kết quả:
- Cải thiện thật và **không đánh đổi EER** ở cùng tư thế: kẻ gian lọt giảm từ 66% xuống 50% ở FRR 5%.
- **Không cứu được trường hợp đổi tư thế** (0,943 không đổi). Vấn đề đó cần đăng ký nhiều tư thế, không phải co rút.
- FAR 50% vẫn rất cao: điểm "chủ" vẫn không thể làm cổng chặn.
- **Tương tác với sửa bảo mật mới (24/11):** `/enroll` giờ trả 409 khi đã có mẫu chuẩn (chặn người khác tiêm nhịp của mình vào tài khoản đã đăng ký). Điều này **xung đột với khuyến nghị đăng ký nhiều tư thế** của E9: cần một đường đăng ký lại có kiểm soát (vd. sau khi xác thực mạnh), chưa thiết kế.

**Giới hạn:** prior trong `population_prior.json` tính trên **cả 97 người** (bản chạy thật), nên khi chấm lại trên chính StrokePIN sẽ rò rỉ; E10b dùng bỏ-một-người để tránh. Prior là thống kê từ dữ liệu CC BY-NC-SA 4.0: ghi trong README. Chỉ kiểm trên PIN 6 số trên điện thoại ở một đợt thu.

### Mô hình người/máy đã nối vào backend (24/11, TẠM THỜI)

- `backend/app/scoring/human_model.py` nạp LightGBM (`backend/app/models/human_lgbm.txt` + `.json`); **tuỳ chọn**: thiếu `lightgbm`, thiếu file hoặc đặt `NHIP_HUMAN_MODEL=off` thì dùng luật baseline. Nối trong `/score`: lấy điểm bi quan hơn giữa luật và mô hình (nếu luật không đủ dữ liệu thì dùng điểm mô hình); mô hình cờ mà luật không giải thích được thì thêm lý do `ml_bot_pattern`.
- Điểm mô hình được ánh xạ để ngưỡng FRR 5% (trên người validation) = 0,5.
- Huấn luyện: `research/experiments/train_human_model.py` trên **người thật StrokePIN + bot sinh bởi `tactics.py`**, chia theo người, **không dùng kích thước chạm**. Mô hình này là **tạm thời**: chưa phải dữ liệu của đội, chưa có bot thật.
- Kết quả trên 20 người **chưa từng thấy**: FRR 3,3%; bắt chiến thuật 1: 100%, 2: 100%, 3: 12%, 4: 61% (nhất quán với E4b). Người giả của `tests/synth.py` không bị coi là máy (0/200), bot chiến thuật 1 điểm 0,0.
- **Giấy phép:** mô hình huấn luyện trên StrokePIN (CC BY-NC-SA 4.0, chia sẻ phái sinh cùng giấy phép). Ghi trong README nộp bài.
- Cài đặt: `pip install lightgbm` (nhóm `ml` tuỳ chọn trong `pyproject.toml`); chưa cập nhật `uv.lock`.

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

### E18–E20 — câu thử thách tiếng Việt và vuốt trên người thật (25/11)

- **E18** (`research/experiments/e18_vi_variation.py`): đếm lý thuyết số cách gõ một câu bằng Telex/VNI; trần 3,0 bit cho "Hôm nay trời đẹp quá" và 6,6 bit cho câu nhiều dấu thanh. Không phải đo người.
- **E19 — Touchalytics, 41 người thật, 20.896 nét vuốt** (`e19_touchalytics.py`, `results/e19_touchalytics.txt`):
  - Luật cũ `swipe_straight_max > 0.999` **gắn cờ nhầm 13,4% phiên 3 nét của người thật** (nét ít điểm gần như tự thẳng: 30% nét 3–5 điểm).
  - **Vận tốc đều** (CV vận tốc < 0,3) gặp **0/20.896 lần ở người thật**, bắt 100% bot vuốt đều và bot nhiễu thời gian ±6 ms (kể cả bot có nhiễu ngang 5–10 px mà luật cũ bỏ lọt). Đã thay luật (`swipe_robotic`, cue `swipe_uniform_speed`, tối đa 0,7). Cận trên 95% của FPR theo từng nét ≈ 3/20.896 = 0,014%; **bot vẫn là bộ sinh của đội**, bot thật có thể giả vận tốc người.
  - **Nhận chủ bằng 5 đặc trưng vuốt: AUC 0,48–0,60 (ngang đoán mò)**, kể cả cùng ngày cùng tác vụ (FAR@FRR5% 0,88–0,97). Đã **loại `swipe_*` khỏi nhận chủ** (`owner.is_identity_feature`). Giới hạn: chỉ 5 đặc trưng, pixel khác theo máy nên so trong cùng máy, 11 người đủ dữ liệu cho phép thử ngày 1 vs 7–14 ngày sau.
- **E20 — mô phỏng** (`e20_vi_style_sim.py`): với giả định mỗi người có xác suất cố định gõ dấu thanh muộn, AUC tăng từ 0,66 (1 âm tiết có chỗ chọn) lên 0,78 (4) và 0,89 (8) cho cặp p = 0,8 vs 0,4; còn 0,64 ở cặp 0,8 vs 0,6. Dùng để chọn câu (≥ 4 âm tiết có chỗ chọn), **không** là bằng chứng về người Việt thật.

### E21 / E21b — chuẩn hoá theo cặp phím (học theo TypeNet, Gunetti–Picardi), Aalto 1.000 người (25/11)

Mã: `research/experiments/aalto_note_chars.py` (giữ chữ cái, gitignored, chỉ nghiên cứu), `e21_digraph_norm.py`, `e21b_digraph_profile.py`; bảng: `research/results/e21_digraph_norm.md`, `e21b_digraph_profile.md`. Giao thức E13, câu thử khác câu đăng ký.

| Đặc trưng (30 phím) | EER | FAR@FRR5% |
|---|---|---|
| E13 thô (6) | 0,249 [0,243, 0,259] | 0,498 [0,473, 0,524] |
| chuẩn hoá theo cặp phím (6) | 0,245 [0,236, 0,253] | 0,479 [0,456, 0,501] |
| thô + chuẩn hoá (12) | **0,238** [0,228, 0,245] | **0,467** [0,446, 0,489] |
| chỉ hồ sơ cặp phổ biến (E21b) | 0,326 | 0,772 |

**Kết quả gần như không đổi** (cải thiện ≤ 1,1 điểm EER, khoảng tin cậy chạm nhau). So hồ sơ theo từng cặp phím **làm tệ hơn** vì hai câu ngẫu nhiên chỉ chung ~6,5 cặp phổ biến ở 30 phím. Kết luận: với câu đổi mỗi lần, chuẩn hoá nội dung không phải đòn bẩy; kênh không phụ thuộc câu (kiểu gõ tiếng Việt) và nhiều phím hơn quan trọng hơn. Chưa đưa vào backend. Công trình liên quan: [`related-work.md`](related-work.md).

### E22 — cách giảm FAR của Innate Challenge (Aalto, 939 người đánh giá, 30 phím, 25/11)

Mã: `research/experiments/aalto_note_orient.py`, `e22_improve_far.py`; bảng: `research/results/e22_improve_far.md`. Giao thức E13 (câu thử khác câu đăng ký); khoảng tin cậy bootstrap theo người.

| Cấu hình | EER | FAR@FRR5% |
|---|---|---|
| 6 đặc trưng thô, K=1 câu đăng ký | 0,288 | 0,625 |
| K=3 (như E13) | 0,253 | 0,517 |
| K=5 | 0,246 | 0,471 |
| K=8 | 0,235 | 0,457 |
| thô + chuẩn hoá cặp phím (12), K=3 | 0,248 | 0,502 |
| **+ mô hình học (LightGBM trên vector lệch), K=3** | **0,227** | **0,429** |
| + tư thế cầm máy (góc nghiêng), K=3 | 0,144 | 0,277 |

- **Thêm câu đăng ký giúp nhưng giảm dần:** 1 → 3 câu cắt FAR 10 điểm, 3 → 8 câu chỉ thêm 6 điểm.
- **Mô hình học giúp ~7 điểm FAR** (0,502 → 0,429), cùng hướng với E12b.
- **Góc nghiêng thiết bị cho số đẹp nhất (FAR 0,277) nhưng KHÔNG nên tin:** mọi câu của một người nằm trong một buổi nên tư thế trùng giữa đăng ký và thử (E9: đổi tư thế gần như mất tín hiệu, EER 0,309). Trên điện thoại thật cần xin quyền cảm biến (iOS Safari), là dữ liệu nhạy cảm, và chỉ đo được "đang cầm kiểu nào". Không đưa vào sản phẩm khi chưa có dữ liệu hai buổi.
- Bảng đánh đổi FRR/FAR (E13 thô, 30 phím): FRR 5% → FAR 49%; 10% → 39%; 20% → 29%; 30% → 22%; 40% → 17%.

### E23 — thêm chuyển động điện thoại vào nhận chủ (StrokePIN, 97 người, 25/11)

Mã: `research/experiments/e23_imu_fusion.py`; bảng: `research/results/e23_imu_fusion.md`. Giao thức E9; đặc trưng IMU: trọng lực (trung bình, độ lệch theo trục), độ rung gia tốc và con quay. Bộ phát hiện E2 (co rút về dân số), k = 3 lượt đăng ký.

| Bộ đặc trưng | Cùng tư thế (ngồi): EER / FAR@FRR5% | Đổi tư thế (đi): EER / FAR@FRR5% |
|---|---|---|
| PIN (thời gian + lệch tâm) | 0,197 / 0,692 | 0,374 / 0,936 |
| Chỉ chuyển động | 0,038 / 0,030 | 0,441 / 0,913 |
| PIN + chuyển động | 0,057 / 0,075 | 0,420 / 0,910 |

**Không tin được số này:** mỗi người một điện thoại, nên gia tốc/trọng lực mang **dấu vết thiết bị** (độ lệch cảm biến, góc cầm) chứ không chỉ thói quen người; kẻ gian trong dữ liệu dùng máy khác. Cùng lỗi đã loại kích thước chạm (E12b). Kịch bản kẻ gian cầm đúng điện thoại của nạn nhân không được mô phỏng. **Đổi tư thế thì mất hết (EER 0,42–0,48).** StrokePIN lấy gia tốc/con quay ~5 Hz nên không kiểm được khớp thời điểm chạm và cú giật. Kết luận: chuyển động là ứng viên cho cổng chống bot ("có tay cầm"), chưa chứng minh được cho nhận chủ. Thiết kế 4 kênh: [`../plan/bon-cong-pipeline.md`](../plan/bon-cong-pipeline.md).

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
