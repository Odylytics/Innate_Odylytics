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
| E1 | Mahalanobis co rút ≥ scaled Manhattan khi chỉ có 3–5 mẫu (**proxy đã chạy: không, kém hơn**) | Cùng chia dữ liệu; so theo số lượt đăng ký 1/3/5 | EER, FAR@FRR 5% + khoảng tin cậy | Có |
| E2 | Co rút về dân số tốt hơn sàn σ cố định (**proxy đã chạy: giảm FAR@FRR 5% ~7–11 điểm, EER không đổi**) | Ước lượng prior từ Aalto/dữ liệu đội; so với sàn hiện tại | Như E1 | Có (Aalto để lấy prior) |
| E3 | Hiệu chỉnh (Platt/isotonic) giảm FAR ở cùng FRR | Fit trên lần ngồi 1, kiểm thử lần ngồi 2 | FAR@FRR 5%, đường DET | Có |
| E4 | RF/LightGBM vượt luật ở bài A và **vẫn bắt bot lạ** | Leave-one-tactic-out trên 4 chiến thuật + `adb` làm tập kiểm thử riêng | Tỷ lệ bắt theo chiến thuật | Cần phiên người thật |
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
