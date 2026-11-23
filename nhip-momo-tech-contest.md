# Nhịp — Lớp chấm điểm rủi ro hành vi cho ví điện tử

> Kế hoạch dự thi **MoMo Tech Contest 2026** · Chủ đề: An ninh mạng + Chống lừa đảo
> Đội 3 người · Cập nhật: 23/11/2026

---

## 1. Tóm tắt cuộc thi

| Mục | Chi tiết |
|---|---|
| Tên | MoMo Tech Contest 2026 (thuộc MoMo Tech Series · *Imagine The Future Workspace — Human Centered. AI Powered*) |
| Đối tượng | Sinh viên ĐH/CĐ tại Việt Nam, quốc tịch VN, 18–23 tuổi; đội 2–3 người; không thi cá nhân; người đang làm/thực tập tại MoMo không được thi |
| Đăng ký | 10:00 13/11 → **23:59:59 27/11/2026** (trưởng nhóm đăng ký tại techday.momo.vn) |
| Hạn gửi câu hỏi làm rõ | **23:59:59 27/11/2026** |
| Hạn nộp bài | **23:59:59 03/12/2026** — sau hạn không được sửa bài, kể cả sản phẩm tại link đã nộp |
| Công bố top 5 | 08/12/2026 |
| Chung kết | 11/12/2026, trực tiếp tại TP.HCM (The Adora Premium, Tân Mỹ) — 5 đội thuyết trình + trả lời giám khảo; đủ thành viên có mặt; tự túc chi phí |
| Giải thưởng | Nhất 50tr · Nhì 30tr · Ba 20tr (đã gồm thuế) · Top 3 vào thẳng vòng Leadership Interview của MoMo Talent 2027 |
| Tiêu chí chấm | Sáng tạo · Chất lượng & mức độ hoàn thiện (sản phẩm chạy ổn định tại thời điểm nộp) · Tiềm năng tác động. Không công bố trọng số. Mỗi bài ≥ 3 giám khảo chấm độc lập |
| Giám khảo | CTO, Head of AI & Data và các lead AI/Software Engineering của MoMo → thiên về kỹ thuật |
| Duy trì sản phẩm | Online liên tục đến hết 11/12/2026 |
| Liên hệ BTC | techday@mservice.com.vn |

### Thành phần bài nộp

| Thành phần | Yêu cầu |
|---|---|
| Sản phẩm | PDF hướng dẫn ≤ 1 trang A4, có link dùng thử online + tài khoản demo |
| Mã nguồn | .zip toàn bộ code + README (cách chạy, công nghệ, **tài sản có sẵn, thư viện mã nguồn mở, công cụ AI đã dùng**, nguồn dữ liệu) |
| Slide | ≤ 10 trang PDF, nêu vấn đề & giải pháp — **dùng luôn cho chung kết, không được sửa** |
| Video | ≤ 3 phút MP4, quay sản phẩm chạy thật |

### Điều kiện bị loại cần tránh

- Nộp sản phẩm đã có từ trước cho chính bài toán này / sao chép
- Người ngoài đội tham gia xây dựng
- Chia sẻ code giữa các đội
- Sửa sản phẩm sau hạn
- Che giấu việc dùng tài sản có sẵn (phải liệt kê trong README)
- Dữ liệu cá nhân/doanh nghiệp không ghi nguồn và căn cứ sử dụng

---

## 2. Vấn đề

**Điện thoại bị chiếm quyền → tiền bị chuyển đi bằng chính app và mã PIN của nạn nhân.**

Hai kịch bản:

| | Kịch bản A — Mã độc điều khiển từ xa | Kịch bản B — Người khác cầm máy và biết PIN |
|---|---|---|
| Cách xảy ra | Nạn nhân bị lừa cài APK giả, cấp quyền Trợ năng (Accessibility). Mã độc xem màn hình, đọc OTP, tự mở app, tự bấm chuyển tiền (vd. RedHook, Gigabud, Hirudo, SpyNote — đã được Công an và các hãng bảo mật cảnh báo năm 2026) | Người quen, kẻ trộm nhìn lén PIN |
| Vì sao lọt | PIN/OTP/thiết bị đều "đúng" — hệ thống xác thực truyền thống coi là chính chủ | Như trên |
| Tín hiệu để phát hiện | Thao tác **không phải ngón tay người**: nhịp quá đều, vuốt quá thẳng, chạm đúng tâm nút | Thao tác là của người, nhưng **không khớp thói quen chủ tài khoản** |

**Câu hỏi sản phẩm trả lời:** *"Người đang thao tác có phải là người thật — và có phải chủ tài khoản không?"*

---

## 3. Sản phẩm

**Nhịp** là lớp chấm điểm rủi ro hành vi dạng **B2B (SDK + API)** cho ví điện tử và ngân hàng. Đối tác nhúng SDK vào app, gọi API ở bước xác nhận giao dịch để nhận điểm rủi ro, hành động đề xuất và lý do.

### Thành phần bài nộp

| # | Thành phần | Mô tả | Giám khảo dùng thế nào |
|---|---|---|---|
| 1 | **SDK JavaScript** | Ghi chạm, vuốt, cuộn, nhịp PIN (chỉ thời gian + toạ độ, **không lưu nội dung**) | Chạy ngầm trong ví demo |
| 2 | **API chấm điểm** (lõi) | `POST /v1/sessions/{id}/score` | Gọi thử qua Swagger với API key demo |
| 3 | **Ví demo** | App ví **thương hiệu riêng** (không sao chép giao diện/logo MoMo), luồng: Trang chủ → Chuyển tiền → Nhập STK → Nhập PIN | Đăng ký nhịp, sau đó cho người khác thử |
| 4 | **Dashboard vận hành** | Danh sách phiên đáng ngờ + giải thích + nút đánh dấu đúng/sai | Đúng tinh thần "Future Workspace" |

### Ví dụ phản hồi API

```json
{
  "session_id": "s_8f21",
  "human_score": 0.97,
  "owner_match": 0.31,
  "risk": "high",
  "action": "step_up",
  "reasons": ["pin_rhythm_slower_40pct", "tap_offset_right", "new_recipient"],
  "explanation_vi": "Thao tác giống người thật nhưng không khớp thói quen của chủ tài khoản. Đề nghị xác thực khuôn mặt trước khi chuyển."
}
```

`action`: `allow` (cho qua) · `step_up` (yêu cầu xác thực thêm, vd. khuôn mặt) · `hold` (giữ lệnh, báo người dùng). **Hệ thống chỉ đề xuất, không tự khóa tài khoản** — điểm "Human Centered".

### Khác gì so với những gì MoMo đã có

MoMo công bố có PIN, OTP, sinh trắc khuôn mặt (iProov, Flashmask), AI phân tích giao dịch và "AI phân tích hành vi" (không nêu rõ có dùng sinh trắc chạm/vuốt). Nhịp khác ở:

1. **Minh bạch**: cho người dùng và vận hành thấy *vì sao* phiên bị nghi ngờ.
2. **Xác thực thêm thay vì chặn cứng**.
3. **Phát hiện riêng thao tác do máy giả lập** (mã độc Trợ năng).
4. Dạng **API dùng được cho bất kỳ ví/ngân hàng nào**.

---

## 4. Kiến trúc

```
┌────────────────────────────────────────────┐
│ App ví + SDK thu tín hiệu                  │  chạm · vuốt · cuộn · nhịp PIN
└───────────────────┬────────────────────────┘
                    ▼
┌──────────── API chấm điểm phiên (< 200 ms) ─────────────┐
│  [ML] Người hay máy?   [ML] Có phải chủ?   [ML] Hợp nhất │
└──────────┬─────────────────────────────────────┬────────┘
           ▼                                     ▼
  Quyết định tức thì                     [LLM] Giải thích
  allow / step_up / hold                 cho người dùng & vận hành
                                                 ▼
                                      Dashboard đội vận hành
                                      (đánh dấu đúng/sai → cập nhật mô hình)
```

**Nguyên tắc:** ML ra quyết định; **LLM chỉ giải thích, không nằm trên đường ra quyết định** (vì độ trễ, tính nhất quán, khả năng kiểm toán).

### Công nghệ

| Phần | Công nghệ |
|---|---|
| API & ML | Python, FastAPI, scikit-learn, LightGBM (mô hình nạp sẵn trong bộ nhớ) |
| Lưu trữ | Postgres (vd. Supabase): phiên, mẫu chuẩn, nhãn |
| Frontend | Next.js (ví demo + dashboard), SDK bằng TypeScript |
| Deploy | API trên nền tảng chạy liên tục (không ngủ đông); frontend trên Vercel |
| LLM | Claude/OpenAI API, gọi bất đồng bộ, có giới hạn chi phí |

---

## 5. Lớp AI chi tiết

### 5.0 Trích xuất đặc trưng (~40 đặc trưng mỗi phiên)

| Nhóm | Đặc trưng | Vai trò |
|---|---|---|
| Nhịp PIN | Thời gian giữ mỗi phím (4), khoảng cách giữa phím (3), tổng thời gian | **Mạnh nhất khi đi cùng vị trí chạm** — thêm vị trí chạm vào nhịp giảm EER 26–37% (Buschek 2015) |
| Vị trí chạm | Độ lệch so với tâm nút (dx, dy), kích thước vùng chạm | Thói quen bấm lệch riêng; cũng là tín hiệu người/máy |
| Vuốt & cuộn | Thời gian, độ dài, vận tốc TB/đỉnh, gia tốc, độ cong, điểm bắt đầu | Tín hiệu **phụ**: 1 lần vuốt ~13% EER, cần 11–12 lần mới xuống 2–3% (Touchalytics) |
| Cảm biến chuyển động *(mới, tuỳ chọn)* | Gia tốc kế quanh thời điểm chạm (`devicemotion`) | Người vs máy: thêm gia tốc kế nâng tỷ lệ bắt bot từ ~60% lên 80–90% (BeCAPTCHA 2021). iOS cần xin quyền |
| Nhịp phiên | Thời gian đứng im giữa màn hình, thời gian tới thao tác đầu | Bị dẫn dắt / bị điều khiển — **giả thuyết của đội**, chưa có nghiên cứu học thuật |

Ghi chú kỹ thuật:
- Bàn phím PIN **tự vẽ trong app** + Pointer Events → lấy được toạ độ, thời điểm nhấn/nhả, kích thước chạm (tránh vấn đề bàn phím ảo trên web di động).
- Không dựa vào `pressure`: chuẩn W3C Pointer Events quy định máy không đo được áp lực thì trả 0.5 cố định; FETA ghi nhận đa số Android ước lượng áp lực từ kích thước chạm.
- Không dựa vào cờ `isTrusted` để bắt bot (script tạo được sự kiện giả; mã độc Trợ năng bấm ở tầng hệ thống) — phát hiện dựa trên nhịp và hình dạng thao tác.

### 5.1 Mô hình 1 — Người hay máy?

- **Dữ liệu "người"**: phiên thật do đội thu.
- **Dữ liệu "máy"**: bộ giả lập hacker sinh phiên theo 4 chiến thuật (dễ → khó):
  1. Bấm cách đều, đúng tâm nút
  2. Thêm nhiễu ngẫu nhiên vào thời gian
  3. Phát lại phiên người thật có thêm nhiễu
  4. Lấy mẫu thời gian từ phân bố của người thật
- **Mô hình**: LightGBM / Random Forest + đặc trưng "độ tự nhiên" (biến thiên nhịp, độ thẳng vuốt, độ phân tán vị trí chạm).
- **Báo cáo** tỷ lệ bắt được **theo từng chiến thuật**; thừa nhận chiến thuật 4 khó.
- **Thêm một nguồn tấn công thật** ngoài bộ giả lập: `adb shell input tap` từ laptop (và nếu kịp, một app dùng `dispatchGesture` của AccessibilityService — đúng cơ chế mã độc dùng). Đây cũng là "bảng điều khiển hacker" trong demo.
- **Cơ sở**: 4 chiến thuật khớp với tài liệu — (1)(2) bot thủ công trong BeCAPTCHA/Iliou 2021; (3) phát lại có điều chỉnh (ActReal 2026, preprint); (4) lấy mẫu từ phân bố người (Serwadda & Phoha CCS 2013, BeCAPTCHA-Type "Universal"). Bot sinh bằng GAN qua mặt được bộ phát hiện chỉ dùng chạm (~60%) → lý do thêm cảm biến chuyển động.
- **Nói đúng mức trong pitch**: chưa có bài báo nào đo nhịp/vị trí chạm của mã độc Trợ năng thật. Câu "nhịp quá đều, chạm đúng tâm nút" là **giả thuyết của đội**, kiểm chứng bằng bộ giả lập, không phải kết quả đã công bố.

### 5.2 Mô hình 2 — Có phải chủ tài khoản? (few-shot)

**Bản 1 — So với mẫu chuẩn (làm trước)**
- Đăng ký 3–5 lượt → trung bình + độ dao động từng đặc trưng.
- Điểm = **scaled Manhattan** (|x − trung bình| / độ lệch chuẩn, cộng lại) — tốt nhất trong 14 bộ phát hiện của Killourhy & Maxion 2009 (EER 9,6%); Zheng 2014 cũng dùng.
- Dễ giải thích ("PIN chậm hơn 40%").
- **Kỳ vọng thực tế**: các bài báo đạt EER 3–7% với hàng chục lượt đăng ký; 3–5 lượt trong **một lần ngồi** sẽ kém hơn, và kết quả cùng phiên lạc quan gấp đôi so với khác phiên (Buschek 2015). → Đăng ký chia **≥ 2 lần ngồi** khi có thể; đo và báo đúng số.

**Bản 2 — Mô hình so cặp (pairwise verifier)**
- Học một mô hình chung: *"hai phiên này có cùng một người không?"*
- Đầu vào: chênh lệch đặc trưng giữa hai phiên; nhãn: cùng người / khác người.
- ~25 người × 5 phiên → hàng nghìn cặp.
- Người dùng mới chỉ cần vài lượt đăng ký (TypeNet: EER 10,7% với 1 lượt → 7,3% với 5 lượt trên điện thoại).
- **Bắt buộc đánh giá kiểu leave-users-out**: người trong tập kiểm thử không có cặp nào trong tập huấn luyện. 25 người là rất nhỏ (TypeNet học từ >100k người) → chỉ làm nếu bản 1 chạy ổn; nếu không kịp, bỏ khỏi bản nộp.

**Cập nhật theo thời gian:** chỉ cập nhật mẫu chuẩn sau phiên được cho qua với điểm khớp cao **và** PIN đúng trên thiết bị đã biết. Như vậy chưa đủ chống "dạy dần" (Biggio 2012; Lovisotto 2020: tấn công thành công >70% với <10 lần tiêm) → thêm:
- **Giới hạn độ trôi**: mỗi lần cập nhật chỉ dịch mẫu chuẩn một lượng nhỏ (vd. trung bình trượt với hệ số 0,1), và tổng độ lệch so với mẫu đăng ký gốc có trần.
- **Kiểm tra hướng trôi**: nếu nhiều lần cập nhật liên tiếp kéo về cùng một hướng → dừng cập nhật, đánh dấu cho vận hành (Lovisotto 2020: bắt >99% sau 2 lần tiêm).

### 5.3 Mô hình 3 — Hợp nhất rủi ro

Chưa có dữ liệu gian lận thật → dùng hàm điểm có trọng số, giải thích được:

```
rủi ro = w1·(1 − người_hay_máy) + w2·(1 − khớp_chủ)
       + w3·(người nhận mới) + w4·(số tiền bất thường so với lịch sử)
```

- **Chuẩn hoá trước khi cộng**: đưa mỗi điểm về [0,1] bằng z-score/tanh rồi mới nhân trọng số — tanh chịu ngoại lệ tốt nhất (Jain, Nandakumar & Ross 2005).
- 3 vùng: < A → `allow` · A–B → `step_up` · > B → `hold`.
- Chọn ngưỡng ưu tiên ít làm phiền chủ thật (vd. FRR ≈ 5%), báo FAR tại ngưỡng đó.
- **A, B là cấu hình chỉnh được** theo đối tác: thay đổi ngưỡng nhỏ ảnh hưởng mạnh tới cả bảo mật lẫn trải nghiệm (Wiefling 2021, 780 người).
- **Cơ sở**: đây là mô hình *xác thực dựa trên rủi ro* (risk-based authentication) — LinkedIn: kết hợp tín hiệu có trọng số nâng AUC 0,913 → 0,955 (Freeman 2016); người dùng thấy step-up khi rủi ro dễ chịu hơn 2FA luôn bật (Wiefling 2020).
- **Phần tự mở rộng (nói rõ trong pitch)**: vùng `hold` và tín hiệu "người nhận mới / số tiền bất thường" chưa có nghiên cứu học thuật kiểm chứng (các nghiên cứu RBA dùng IP, trình duyệt; chỉ có tài liệu của hãng như BioCatch).
- Lộ trình: thay bằng mô hình có giám sát khi có dữ liệu thật từ đối tác (Wiefling 2022, 3,3 triệu người dùng).

### 5.4 Lớp giải thích

- Lấy 2–3 đặc trưng lệch nhiều nhất (z-score cho mô hình 2, TreeSHAP cho LightGBM ở mô hình 1) → câu tiếng Việt theo mẫu.
- Với hàm hợp nhất ở 5.3, mỗi số hạng `w·giá_trị` **chính là** phần đóng góp → không cần SHAP.
- LLM chỉ dùng ở dashboard để viết tóm tắt vụ việc cho chuyên viên.

### 5.5 Đánh giá (làm đúng cách)

Căn cứ: FETA (Georgiev 2022) rà 30 bài về chạm — **tất cả** mắc ít nhất một lỗi đánh giá; gộp các lỗi biến EER thật 13,8% thành 4,9%.

- **Tách theo thời gian**: đăng ký bằng phiên trước, kiểm thử bằng phiên sau. Không tách ngẫu nhiên (tách ngẫu nhiên làm EER đẹp hơn ~3,8 điểm).
- **Một điện thoại duy nhất** cho mọi người tham gia (trộn đời máy làm đẹp số 3,2–5,8 điểm).
- **Không đưa dữ liệu kẻ gian vào huấn luyện mô hình 2** (làm đẹp số ~2,55 điểm; 80% bài báo mắc lỗi này).
- **Leave-users-out** cho mô hình so cặp.
- Báo cáo cả mức phiên đơn lẻ và mức gộp tín hiệu.
- **Số liệu lên slide:**
  - FAR khi FRR = 5% (**số chính** — ISO/IEC 19795-1 ưu tiên sai số tại một điểm vận hành; EER chỉ để so sánh với bài báo)
  - EER + đường DET, kèm khoảng tin cậy (25 người là ít)
  - Phân bố lỗi theo từng người (trung bình che giấu người "khó" — Eberz 2017)
  - Tỷ lệ bắt bot theo từng chiến thuật
  - Độ chính xác theo số lượt đăng ký (1 / 3 / 5)
  - Độ trễ API
- **Bộ dữ liệu công khai để đối chiếu** (kiểm tra giấy phép trước khi dùng, ghi vào README): MobileTouchDB/BioTouchPass2 (217 người, PIN 4 số, EER 2,38%), BB-MAS (117 người), BehavePassDB (81 người, 4 phiên), HuMIdb (600 người, có cảm biến — dùng cho người/máy).

Danh mục paper đầy đủ: [reports/Paper nền tảng cho Nhịp.md](reports/Paper%20nền%20tảng%20cho%20Nhịp.md) · PDF trong `papers/`.

---

## 6. Kịch bản demo chung kết

| Bước | Ai làm | Mục đích |
|---|---|---|
| 1. Đăng ký | Giám khảo A làm 3–5 lượt chuyển tiền thử (~20 giây/lượt) trên điện thoại của đội | Học nhịp riêng |
| 2. Công bố PIN | Cả 3 giám khảo biết PIN (vd. 1593) | Đúng kịch bản "kẻ gian biết PIN" |
| 3. Thử | Giám khảo B, C → rồi **A làm lại** | Phải thấy chủ thật được chấp nhận, người khác bị yêu cầu xác thực thêm |
| 4. Giải thích | Màn hình hiện điểm + lý do ("nhịp PIN chậm hơn 40%, chạm lệch phải, cuộn thẳng hơn") | AI là lõi + minh bạch |
| 5. Tấn công bằng máy | "Bảng điều khiển hacker" tự bấm vào app từ máy khác | Mô phỏng mã độc Trợ năng → báo "không phải người thật" |
| 6. Dashboard | Mở dashboard vận hành, xem tóm tắt vụ việc, đánh dấu đúng/sai | Góc "Future Workspace" |

Chuẩn bị: đăng ký và thử cùng tư thế; đặt ngưỡng nghiêng về `step_up` thay vì chặn; có video dự phòng nếu mạng hội trường kém.

---

## 7. Phân vai & kế hoạch — build trong 1 ngày

### Vai trò (mỗi người sở hữu một phần, chịu trách nhiệm đến lúc nộp)

| | **Người 1 — Data & ML** | **Người 2 — Backend & tấn công** | **Người 3 — App & pitch** (trưởng nhóm) |
|---|---|---|---|
| Sở hữu | Trích xuất đặc trưng, mô hình 1 & 2, hàm hợp nhất, lớp giải thích (lý do), số liệu đánh giá | API chấm điểm, DB, deploy, độ trễ, cập nhật mẫu chuẩn, **bộ giả lập hacker + bảng điều khiển hacker** | SDK thu tín hiệu, bàn phím PIN, ví demo, màn hình đăng ký/kết quả, dashboard; slide, video, PDF 1 trang |
| Đầu ra cuối ngày | `features.py`, `model1.pkl`, `score()` trả về điểm + 2–3 lý do; bảng số liệu sơ bộ | API online có `/enroll`, `/score`, Swagger, API key demo; bot chạy được cả 4 chiến thuật + 1 nguồn tấn công thật | Ví demo chạy trên điện thoại demo, end-to-end; khung slide 10 trang |
| Trả lời giám khảo (mục 9) | Câu 1, 2, 3, 4 | Câu 5, 6, 8 | Câu 7 + dẫn dắt toàn bộ demo |

**Làm chung, không giao riêng:** thu dữ liệu; đăng ký thi + gửi câu hỏi cho BTC **trước 23:59 27/11** (Người 3).

### Ngày build (D-day)

| Giờ | Người 1 — Data & ML | Người 2 — Backend & tấn công | Người 3 — App & pitch |
|---|---|---|---|
| **08:00–09:00** | **Cả đội**: chốt 2 hợp đồng dữ liệu — JSON phiên SDK gửi lên (sự kiện chạm: `t_down`, `t_up`, `x`, `y`, `w`, `h`, `key`) và schema phản hồi API (mục 3). Tạo repo, deploy "hello world" cho API và frontend ngay từ đầu | | |
| **09:00–12:00** | Hàm trích xuất ~40 đặc trưng từ JSON mẫu; mô hình 2 bản 1 (scaled Manhattan) | FastAPI: nhận phiên, lưu DB, `/enroll`, `/score` (trả số giả trước); deploy | SDK Pointer Events + bàn phím PIN tự vẽ; luồng Trang chủ → Chuyển tiền → Nhập STK → PIN |
| **12:00–13:00** | **Ghép lần 1 + thu dữ liệu lần ngồi 1**: 3 người × 5 phiên trên **một điện thoại demo** | | |
| **13:00–17:00** | Mô hình 1 (Random Forest/LightGBM) trên phiên người + phiên bot; hàm hợp nhất (chuẩn hoá tanh, trọng số); câu lý do tiếng Việt từ z-score | Bộ giả lập 4 chiến thuật → sinh phiên bot cho Người 1; **nguồn tấn công thật**: `adb shell input tap` từ laptop vào ví demo; nạp mô hình vào API | Màn hình đăng ký nhịp, màn hình kết quả có lý do; dashboard dạng bảng (phiên đáng ngờ + lý do + nút đúng/sai) |
| **17:00** | ⚑ **Mốc quyết định**: nếu mô hình 2 không tách nổi 3 người trong đội → pitch tập trung vào **"người hay máy"**, "có phải chủ" thành tín hiệu phụ | | |
| **17:00–19:00** | **Ghép lần 2 end-to-end + thu dữ liệu lần ngồi 2**: đội làm lại 5 phiên mỗi người + 3–5 bạn bè (có phiếu đồng ý) + lượt "biết PIN, đóng giả chủ" | | |
| **19:00–21:00** | Đánh giá: tách theo thời gian (lần ngồi 1 đăng ký → lần ngồi 2 kiểm thử), FAR@FRR 5%, EER, tỷ lệ bắt bot từng chiến thuật | Cập nhật mẫu chuẩn có trần độ trôi; đo độ trễ; tài khoản demo; giới hạn chi phí | Chạy thử toàn luồng trên điện thoại demo, sửa lỗi giao diện; chạy thử kịch bản demo mục 6 |
| **21:00–23:00** | Đưa số liệu sơ bộ vào slide | README nháp (thư viện, công cụ AI, nguồn dữ liệu, tài sản có sẵn) | Khung slide 10 trang + kịch bản video 3 phút |

**Cắt khỏi ngày build** (làm sau nếu kịp, không ảnh hưởng demo): mô hình so cặp (bản 2), tóm tắt LLM ở dashboard, cảm biến gia tốc, kiểm tra hướng trôi.

### Sau ngày build (đến 3/12)

| Mốc | Việc |
|---|---|
| Đến 27/11 | Thu đủ ~25 người × ≥ 2 lần ngồi × 5 phiên; **đăng ký thi + câu hỏi cho BTC trước 23:59 27/11** |
| 28/11–1/12 | Đánh giá lại trên dữ liệu đủ (DET, khoảng tin cậy, phân bố lỗi theo người); phần cắt ở trên nếu kịp |
| 2/12 | Đóng băng tính năng; kiểm thử tải, sao lưu, hosting chạy liên tục |
| 3/12 | Slide cuối, video, PDF 1 trang, zip mã nguồn. **Nộp trước 23:59** |

## 8. Rủi ro & cách xử lý

| Rủi ro | Xử lý |
|---|---|
| 3–5 lượt đăng ký không đủ để phân biệt người | Đo sớm (1/3/5 lượt), đăng ký chia ≥ 2 lần ngồi, báo đúng số; mốc quyết định 17:00 ngày build → chuyển trọng tâm sang "người hay máy" (không dựa vào "bị dẫn dắt" — chưa có nghiên cứu) |
| Tín hiệu "bị dẫn dắt" / nạn nhân bị lừa qua điện thoại | Chỉ có tài liệu của hãng (BioCatch…) → trình bày là hướng mở rộng, không đưa vào số liệu chính |
| Giám khảo căng thẳng trên sân khấu → từ chối nhầm chủ thật | Đăng ký & thử cùng tư thế; ngưỡng nghiêng về `step_up` |
| Bot tinh vi (chiến thuật 4) qua mặt | Thừa nhận trong pitch; kết hợp nhiều tín hiệu; native SDK có thêm tín hiệu thiết bị |
| Số liệu đẹp giả do đánh giá sai | Tách theo thời gian, một thiết bị, báo mức phiên đơn lẻ |
| Pháp lý dữ liệu | Luật BVDLCN 2025 + NĐ 356/2025 (hiệu lực 1/1/2026) xếp sinh trắc học vào dữ liệu nhạy cảm → coi dữ liệu chạm/vuốt là nhạy cảm: xin đồng ý rõ ràng, chỉ lưu đặc trưng thời gian/toạ độ, không lưu nội dung, ghi rõ trong README |
| Thương hiệu | Không sao chép giao diện/logo MoMo; dùng thương hiệu riêng |
| Sản phẩm sập / hết credit trước 11/12 | Hosting chạy liên tục, giới hạn chi phí LLM, cache, giám sát |
| Câu hỏi "MoMo có rồi mà?" | Nhấn vào minh bạch, step-up, phát hiện thao tác máy, dạng API mở |

---

## 9. Câu hỏi giám khảo có thể hỏi — chuẩn bị trước

1. Dữ liệu lấy từ đâu, bao nhiêu người, có đồng ý không?
2. EER / FAR / FRR là bao nhiêu, đánh giá theo cách nào?
3. Cần bao nhiêu lượt đăng ký? Người dùng đổi điện thoại thì sao?
4. Bot phát lại thao tác người thật thì sao?
5. Độ trễ và chi phí mỗi lần chấm điểm?
6. Vì sao không để LLM quyết định?
7. Khác gì hệ thống nội bộ MoMo?
8. Xử lý dữ liệu nhạy cảm theo luật mới thế nào?

---

## 10. Nguồn tham khảo chính

**Cuộc thi**
- Trang chủ MoMo TechDay 2026: https://techday.momo.vn/
- Đề bài: https://techday.momo.vn/topic.html
- Thể lệ: https://techday.momo.vn/assets/docs/the-le-cuoc-thi.pdf

**Bối cảnh MoMo & mã độc**
- MoMo và Bộ Công an hợp tác chống lừa đảo bằng AI: https://www.momo.vn/tin-tuc/thong-bao/momo-va-bo-cong-an-dong-hop-tac-day-lui-lua-dao-8893
- MoMo có an toàn không (các lớp bảo mật): https://www.momo.vn/blog/momo-co-an-toan-khong-giai-dap-tu-a-z-thong-tin-c198dt2342
- Công an Hà Nội cảnh báo mã độc RedHook: https://dantri.com.vn/phap-luat/cong-an-ha-noi-canh-bao-2-ma-doc-co-the-tu-chuyen-tien-dien-ma-otp-20260826130439761.htm
- Mã độc chiếm quyền trợ năng: https://m.tinnhanhchungkhoan.vn/cuoc-dua-ai-bao-ve-ngan-hang-so-post397114.html

**Sinh trắc hành vi**
- BioCatch — phát hiện lừa đảo qua hành vi: https://www.biocatch.com/detect-social-engineering-scam
- Touchalytics: https://arxiv.org/pdf/1207.6231
- FETA — sai lầm khi đánh giá touch biometrics: https://ar5iv.labs.arxiv.org/html/2201.10606
- Xác thực qua nhịp chạm PIN: https://www.eecis.udel.edu/~hnw/paper/tapping.pdf
- Buschek et al. 2015 (đặc trưng không gian khi nhập mật khẩu): http://www.florian-alt.org/unibw/wp-content/publications/buschek2015chi.pdf
- Tấn công bắt chước nhịp gõ bằng AR: https://cs.uwaterloo.ca/~uhengart/publications/mobisys18.pdf
- Bộ dữ liệu KVC / Aalto: https://arxiv.org/pdf/2311.06000v3

**Tham khảo mô hình sản phẩm**
- MouseCat (YC W26): https://www.ycombinator.com/companies/mousecat

**Pháp lý**
- Sinh trắc học là dữ liệu nhạy cảm theo luật mới: https://thesaigontimes.vn/dung-dua-voi-du-lieu-sinh-trac-hoc-nguoi-dung/
