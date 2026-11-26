# Báo cáo tổng hợp Innate: flow đề tài và số liệu thực nghiệm

> Lập 26/11/2026 từ mã và kết quả có trong repo (`research/results/`, `research/EXPERIMENTS.md`, `backend/`). Mọi con số dẫn tới file kết quả. **Dữ liệu người thật đều là bộ công khai (StrokePIN, Aalto, Touchalytics, CMU), chưa có dữ liệu của đội. Mọi bot là bộ sinh của đội, chưa có bot thật.** Đọc kèm [`../plan/how-it-works.md`](../plan/how-it-works.md) và [`../plan/positioning.md`](../plan/positioning.md).

## 1. Đề tài một đoạn

Mã độc dùng quyền Trợ năng bấm thay người dùng, hoặc kẻ gian biết PIN, khiến PIN và OTP không còn bảo vệ được giao dịch. Innate là lớp xác minh "người thật" thụ động ở bước xác nhận giao dịch: đo nhịp và cách chạm khi nhập PIN (và, ở bước xác thực thêm, một câu tiếng Việt gõ ngẫu nhiên), rồi đề xuất `allow`, `step_up` hoặc `hold`. Hệ thống không bao giờ tự khoá tài khoản; ML và luật quyết định, LLM chỉ được giải thích.

**Hai câu hỏi tách biệt**

| Câu hỏi | Cần đăng ký | Bắt ai | Độ chắc hiện đo được |
|---|---|---|---|
| Người hay máy? | Không | Mã độc, script, `adb` | Bot ngây thơ và phát lại nhiễu ≤±10%: giữ lệnh 100% (E24). Bot thích nghi: lọt 48–82%. |
| Có phải chủ? | Có (3 lượt) | Người quen, kẻ trộm biết PIN | EER 16–20% cùng tư thế, 32–36% khi đổi tư thế (E9). Không đủ làm cổng chặn. |

**Định vị trung thực:** phần mạnh là phát hiện điều khiển tự động và phát lại. Nhận chủ là tín hiệu rủi ro bổ sung, hợp nhất bằng trọng số, không phải cổng AND.

## 2. Flow hệ thống

```
App ví + SDK Innate (ghi sự kiện, không ghi nội dung)
  │  touch: toạ độ, thời điểm xuống/lên từng phím, kích thước vùng chạm, vuốt
  │  ô văn bản: chỉ thời điểm, loại (key/paste/delete/set_text), số ký tự
  ▼
POST /v1/sessions           → features.extract (≈24 đặc trưng định danh + bot_features)
POST /v1/users/{id}/enroll  → đủ 3 lượt: owner.build_template (mu, sd co rút về dân số), khoá đăng ký (409 sau đó)
  ▼
POST /v1/sessions/{id}/score   (chuỗi chấm điểm, chạy trong tiến trình, p50 3,7 ms local)
  1. human.score (luật) + human_model (LightGBM)   → điểm người/máy; luật bot lấy min với mô hình
  2. replay.is_replay (khoảng cách ≤0,07 tới phiên cũ) → ép hold, lý do replayed_session
  3. owner.score (scaled Manhattan, sd có sàn, co rút nu=5) → owner_model (LightGBM) thay điểm khi PIN đủ 6 phím
  4. fusion.fuse: rủi ro = 0,40·(1−human) + 0,35·(1−owner) + 0,15·người nhận mới + 0,10·bất thường số tiền
        hold nếu human < 0,3 hoặc rủi ro > B(0,55); step_up nếu rủi ro ≥ A(0,25); còn lại allow
  5. explain: lý do tiếng Việt từ luật và độ lệch từng đặc trưng
  ▼
Mẫu chuẩn chỉ cập nhật khi: không phải phiên đăng ký, action = allow, owner ≥ 0,8, human ≥ 0,8
  - trần trôi 1 sd mỗi đặc trưng; trôi trung bình > 0,5 sd thì đóng băng (E7, cờ frozen)
```

**Innate Challenge (bước xác thực thêm):** `GET /v1/challenge` cấp câu tiếng Việt ngẫu nhiên có ≥4 âm tiết có chỗ chọn dấu thanh, kèm token ký, dùng một lần. App gửi `fields[challenge]` (token, độ dài, sự kiện). `features.extract` thêm đặc trưng `vi_*` qua `vi_ime.py`. Hiện chỉ có tín hiệu mềm `challenge_no_ime` (≤0,3); `vi_*` chưa vào nhận chủ vì chưa có dữ liệu tiếng Việt thật.

**Ràng buộc thiết kế:** chỉ lưu thời gian, toạ độ, nhãn phím; không lưu PIN tài khoản thật; `pressure` và `isTrusted` không được dựa vào; mẫu chuẩn không dạy dần; hệ thống không khoá tài khoản. Ngoại lệ có chủ đích: trang `#/collect` lưu chữ số PIN thử do tình nguyện viên tự đặt, kèm họ tên và email (có đồng ý).

## 3. Flow thu dữ liệu của đội

1. Tình nguyện viên mở `#/collect` trên điện thoại: nhập họ tên, email, đọc phiếu đồng ý.
2. Tự đặt PIN 6 số (nhập hai lần), rồi nhập lại 5 lần qua màn hình chuyển tiền giả.
3. Sau mỗi lần nhập PIN, gõ một câu tiếng Việt ngẫu nhiên (token ký, chặn dán, có nút bỏ qua nếu bàn phím không gõ được dấu).
4. Cả 5 phiên gửi cùng nhau kèm `meta` (mã băm từ email, họ tên, email, ghi chú).
5. Phân tích: `team_analysis.py export.jsonl` (T1–T5, bootstrap theo người), `train_human_model.py --export ... --out DIR`.

**Trạng thái:** đường ống đã thử bằng dữ liệu giả (`team_data_dryrun.py`); chưa có dữ liệu thật. File export chứa dữ liệu cá nhân, không đưa vào repo hay zip nộp.

## 4. Giao thức đánh giá

- Theo FETA: tách thời gian đăng ký/kiểm thử, một thiết bị, không dùng dữ liệu kẻ gian khi huấn luyện mô hình chủ, chia theo người cho mô hình cặp.
- Chỉ số chính: **FAR@FRR 5%**, kèm EER; khoảng tin cậy bootstrap 95% theo người.
- "Kẻ biết PIN" là người khác nhập cùng PIN trên máy khác, nên số đo lẫn nhiễu thiết bị và lạc quan.
- Bot: 4 chiến thuật do đội sinh. CT1 đều, CT2 nhiễu thời gian, CT3 phát lại (có nhiễu ±n%), CT4 lấy mẫu từ phân bố dân số; thêm bot "biết mẫu chuẩn" ở E27.

## 5. Số liệu thực nghiệm

### 5.1 Người hay máy (không cần đăng ký)

**E4b, người thật StrokePIN + bot sinh, ngưỡng FRR 5%, tỷ lệ bot bị bắt** (chỉ phần PIN):

| Mô hình | CT1 | CT2 | CT3 | CT4 |
|---|---|---|---|---|
| LightGBM, thấy cả 4 chiến thuật | 1,00 | 1,00 | 0,26 | 0,73 |
| Luật baseline (`human.py`) | 1,00 | 1,00 | 0,05 | 0,01 |
| LightGBM, **bỏ đúng chiến thuật đó** khỏi huấn luyện (bot lạ) | 1,00 | 0,56 | 0,09 | 0,20 |

Bot ngây thơ bắt 100%; bot giống người thì mô hình dễ học tắt. Bài học: bot lạ là điểm yếu chính.

**E11, ô văn bản tự do (Aalto, 33.522 câu của 2.260 người):** LightGBM bắt bot đặt thẳng văn bản 100% và gõ đều 99% khi đã thấy loại bot; khi bỏ đúng chiến thuật: gõ đều 0%, phát lại 5%, lấy mẫu dân số 4–5%. Luật hiện tại của backend ở ô note bắt 0%. Luật `text_set_without_keys` cho ô số tiền chưa kiểm chứng (không có dữ liệu người).

**E19, vuốt (Touchalytics, 41 người, 20.896 nét):** luật cũ `straight>0,999` gắn cờ nhầm 13,4% phiên người; thay bằng `swipe_robotic` (CV vận tốc <0,3): 0/20.896 nét người bị chặn nhầm. Bot vuốt thẳng bị bắt 100%; thêm nhiễu ngang 2 px còn 43%, 5 px còn 4%. Đặc trưng vuốt cho AUC ~0,5 khi nhận chủ nên bị loại khỏi danh tính.

**E13, số phím trên câu gõ (Aalto), AUC bot:** CT2 0,915 (6 phím) → 0,995 (30 phím); CT4 0,719 → 0,891.

### 5.2 Phát lại

**E5b, hiệu chỉnh trên người thật (1.842 cặp người–PIN):** ngưỡng backend 0,085 (dữ liệu giả) được hạ về **0,07**. Tỷ lệ phiên người bị coi là phát lại tăng theo số phiên cũ (0,28% ở 3 phiên, 0,64% ở 8, ngoại suy ~3,7% ở 50). Tỷ lệ bắt theo nhiễu của kẻ phát lại:

| Ngưỡng | ±5% | ±10% | ±15% | ±20% | ±30% |
|---|---|---|---|---|---|
| 0,085 | 1,00 | 1,00 | 0,86 | 0,09 | 0,00 |
| 0,094 (FPR 1%) | 1,00 | 1,00 | 0,98 | 0,30 | 0,00 |
| 0,117 (FPR 5%) | 1,00 | 1,00 | 1,00 | 0,92 | 0,03 |

Ngưỡng cao hơn bắt thêm nhưng chặn nhầm chủ: ở E27b, ngưỡng 0,12 làm chủ ngồi bị hold 17%.

### 5.3 Nhận chủ

**E9, StrokePIN (97 người, PIN 6 số), đăng ký 3 lượt, kẻ biết PIN:**

| Điều kiện | EER | FAR@FRR5% |
|---|---|---|
| Cùng tư thế (ngồi), thời gian, backend | 0,201 | 0,710 |
| Cùng tư thế, thời gian, **co rút về dân số (E2)** | 0,200 | 0,570 |
| Cùng tư thế, thời gian + lệch tâm + kích thước chạm | 0,157 | 0,740 |
| Đổi tư thế (đi), thời gian | 0,323 | 0,839 |

Đổi tư thế làm mất gần hết tín hiệu. Kích thước chạm có thể mang tín hiệu thiết bị (một máy mỗi người).

**E12b, mô hình học, không dùng kích thước chạm:**

| Tư thế | Mô hình | EER | FAR@FRR5% |
|---|---|---|---|
| Ngồi | baseline mean |z| | 0,161 | 0,573 |
| Ngồi | LightGBM | 0,158 | 0,375 |
| Đi | baseline | 0,363 | 0,944 |
| Đi | LightGBM | 0,309 | 0,708 |

**E1/E2 (CMU, bàn phím máy tính) và E10:** co rút phương sai về dân số giảm FAR@FRR5% 7–11 điểm, EER không đổi; đã đưa vào `owner.py` (`population_prior.json`, nu=5).

**E13, số phím (Aalto, chỉ thời gian):** EER 0,364 → 0,245 và FAR 0,807 → 0,489 khi tăng từ 6 lên 30 phím. Cơ sở cho Innate Challenge. **E14:** chủ khi gõ 6 số mới EER 0,33. **E22:** mô hình học giảm thêm FAR ~7 điểm trên câu gõ; đặc trưng tư thế lạc quan nên bỏ.

**E23, chuyển động (IMU):** chỉ IMU đạt EER 0,038–0,070 khi cùng tư thế (FAR@FRR5% 0,03–0,10) nhưng là **nhiễu thiết bị** (mỗi người một máy) và vô dụng khi đổi tư thế (EER 0,44–0,48). **Không được tuyên bố nhận chủ bằng IMU.**

**E21/E21b:** chuẩn hoá theo cặp phím gần như không đổi; hồ sơ từng cặp phím làm tệ hơn.

**E18, E20 (tiếng Việt, mô phỏng):** một câu có 3–6,6 bit biến thể gõ Telex/VNI (trần lý thuyết). AUC kiểu gõ 0,66 (1 âm tiết) → 0,89 (8 âm tiết); chọn câu ≥4. Chưa có người thật gõ tiếng Việt. Telex hay VNI không quan sát được trên web điện thoại (keyCode 229).

### 5.4 Toàn hệ thống (E24, E25, E27, E28)

10 người chưa từng thấy bởi cả hai mô hình học, đăng ký 3 lượt ngồi, ngưỡng A=0,25 B=0,55, người nhận quen:

| Nhóm | giữ lệnh | xác thực thêm | cho qua |
|---|---|---|---|
| Chủ, ngồi | 1% | 19% | 80% |
| Chủ, đi | 0% | 37% | 63% |
| Kẻ biết PIN (máy khác) | 2% | 70% | 28% |
| Bot đều / nhiễu thời gian / phát lại ±5% / ±10% | 100% | 0% | 0% |
| Bot lấy mẫu dân số (CT4) | 26% | 67% | 7% |
| Phát lại ±15% | 30% | 13% | 58% |
| Phát lại ±20% | 1% | 26% | 72% |
| Phát lại ±30% | 4% | 48% | 48% |
| Bot biết mẫu chuẩn (scale 1,0) | 8% | 17% | 75% |
| Bot biết mẫu chuẩn (scale 0,5) | 12% | 6% | 82% |

Người nhận mới: chủ ngồi chỉ allow 17% (step_up 79%).

**E25, quét ngưỡng A (B=0,55):**

| A | Chủ ngồi allow | Kẻ biết PIN không allow |
|---|---|---|
| 0,10 | 17% | 99% |
| 0,20 | 65% | 90% |
| **0,25 (hiện tại)** | **80%** | **72%** |
| 0,30 | 91% | 50% |
| 0,40 | 96% | 14% |

Không có điểm tối ưu cho cả hai phía.

**E28, độ dài PIN (mô phỏng bằng cắt 4 lần chạm đầu):** PIN 4 số làm mô hình chủ học không chạy, kẻ biết PIN được allow 68% (6 số: 28%). **Kết luận đã áp dụng: demo web chuyển sang PIN 6 số `159357`.** Với 6 số và AI bật, chủ ngồi mới allow 16/25 lần trong kịch bản demo (`docs/plan/web-demo.md`).

**E3, hiệu chỉnh điểm chủ:** ánh xạ cũ (d=2→0,5) cho 84% kẻ biết PIN vượt 0,5 (chủ 96%); Platt cân bằng lớp còn 27% (chủ 90%). Ở FRR 5% FAR vẫn ~50%. Nối vào backend (`NHIP_OWNER_MAP=platt`) chỉ đổi đường dự phòng, làm chủ ngồi ở người nhận mới tụt từ 92% xuống 2% allow và chặn cập nhật mẫu chuẩn, nên **để tắt mặc định** (`e24_platt_map.md`).

**E7, đầu độc mẫu chuẩn (dữ liệu giả):** không có trần trôi thì kẻ gian được chấp nhận 100% và chủ bị khoá ngoài (0,58). Đóng băng khi trôi >0,5 sd cho 0,77 (so 0,85 của trần 1 sd), kèm cờ cảnh báo. Đã cài trong `owner.update`; chưa lộ cờ ra API.

### 5.5 Hiệu năng và hạ tầng

- **E26:** `/score` p50 3,7 ms, p95 5,2 ms, max 36,5 ms (local, sau khi nạp sẵn mô hình; trước đó lần đầu ~1 s). Không gồm mạng và cold start.
- **R6:** 100 lần `GET /health` tới `nhip-api-taupe.vercel.app`: min 0,16 s, p50 0,22 s, p95 0,48 s, max 1,27 s. Chưa đo `/score`, cold start sau thời gian rảnh, giới hạn gói free.
- Kiểm thử: backend 50, attacker 8, web 7 test đều qua; `vite build` thành công.

## 6. Hạn chế đã biết (nên ghi nguyên văn trên slide)

1. Chưa có dữ liệu của đội và bot thật; train và test bot dùng chung 4 bộ sinh.
2. Nhận chủ bằng nhịp chạm yếu (FAR ~50% ở FRR 5%), đổi tư thế mất tín hiệu; kẻ biết PIN trong đo lường dùng máy khác nên số lạc quan.
3. Bot biết mẫu chuẩn hoặc phát lại ±15% trở lên qua mặt 48–82%; chưa có biện pháp đối phó (ActReal báo tấn công thích nghi thành công 71–77%).
4. Mô hình học dùng dữ liệu StrokePIN (CC BY-NC-SA 4.0) nên cả repo theo giấy phép đó; mô hình là tạm thời cho đến khi có dữ liệu đội.
5. Chưa có đường đăng ký lại có kiểm soát (thiết kế ở `../plan/dang-ky-lai.md`); mẫu bị đóng băng chưa có cách mở.
6. Kiểu gõ tiếng Việt chưa kiểm chứng trên bàn phím thật; chưa nối `vi_*` vào nhận chủ.

## 7. Việc còn lại (đến 03/12)

| Việc | Cần |
|---|---|
| Thu dữ liệu đội, chạy `team_analysis`, huấn luyện lại | Người tham gia |
| Bot thật qua `adb` làm tập test độc lập | Điện thoại Android |
| Đo kích thước chạm (R2) trên Android Chrome và iOS Safari | Điện thoại thật |
| Deploy lại web với PIN 6 số, quay video | Quyết định deploy |
| Điền hồ sơ nộp (tên đội, URL, key demo, README, slide) | Đội |
| Nếu muốn bật Platt: dời A/B và `UPDATE_MIN_OWNER`, đo lại E24/E25 | Dữ liệu đội |
| Lộ cờ `frozen` ra API, cài đăng ký lại | Một vòng code backend |

Hạn: 27/11 23:59 đăng ký và câu hỏi BTC; 03/12 23:59 nộp bài; 11/12 chung kết, sản phẩm phải còn online.
