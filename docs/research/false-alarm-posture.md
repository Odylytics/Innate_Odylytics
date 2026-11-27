# Báo động nhầm (chủ thật bị chặn/hỏi thêm), nguy hiểm của nó, và tư thế ngồi/đi (27/11/2026)

"Báo động nhầm" ở đây = **chủ tài khoản thật không được `allow`** (bị `step_up` hoặc `hold`). Ngược lại "lọt" = kẻ biết PIN được `allow`.
Số liệu: E33 (`research/experiments/e33_posture_false_alarm.py`, bảng đầy đủ `research/results/e33_posture_false_alarm.md`), chạy đúng chuỗi `/score` của backend trên StrokePIN (PIN 6 số thật, mỗi người 5 lượt ngồi + 5 lượt đi). Tập kiểm thử cố định cho mọi cách đăng ký.

## 1. Kết quả chính (đủ mô hình học, 10 người chưa từng thấy, người nhận quen; CI 95% theo người)

| Cách đăng ký | Chủ **ngồi**: báo nhầm | Chủ **đi**: báo nhầm | Chủ bị **giữ lệnh** | Kẻ biết PIN lọt (ngồi / đi) |
|---|---|---|---|---|
| 3 lượt ngồi (giống người dùng ngồi đăng ký trong app) | 17% [11, 23] | **41% [31, 50]** | 0–1% | 24% / 31% |
| 3 lượt đi | 36% [28, 44] | 16% [11, 21] | 0–1% | 30% / 37% |
| 2 ngồi + 2 đi | 20% [13, 27] | **18% [12, 24]** | 0–1% | 34% / 39% |
| 3 ngồi + 3 đi | 18% [12, 25] | 19% [12, 25] | 0–1% | 33% / 40% |

Đọc bảng:
1. **Đổi tư thế làm báo nhầm tăng hơn gấp đôi.** Đăng ký khi ngồi rồi chuyển tiền khi đang đi: 41% lần chủ thật bị hỏi thêm (ngồi: 17%). Ngược lại cũng vậy (đăng ký khi đi, dùng khi ngồi: 36%).
2. **Đăng ký trộn tư thế gần như san bằng hai bên** (~18–20% cả ngồi lẫn đi): báo nhầm khi đi giảm từ 41% xuống 18%.
3. **Cái giá:** mẫu "rộng" hơn nên kẻ biết PIN lọt nhiều hơn khoảng 10 điểm (ngồi 24% → 34%, CI không chồng nhau). Đây là đánh đổi thật, không phải miễn phí.
4. **Chủ gần như không bao giờ bị giữ lệnh** (0–1%; phần lớn ca hiếm đó là do luật "giống bot" khi đi). Nguy cơ chính là **phiền**, không phải mất tiền hay khoá tài khoản.
5. **Người nhận mới:** gần như mọi giao dịch của chủ đều bị hỏi thêm (84–98%) và kẻ gian hầu như không lọt (0–1%). Trọng số "người nhận mới" đang lấn át nhịp; demo nên chọn người nhận quen để thấy khác biệt.

Bảng phụ (tắt mô hình học, 96 người, chỉ luật + khoảng cách): báo nhầm thấp (ngồi 4%, đi 11%; trộn tư thế: 3% / 5%) nhưng **kẻ biết PIN lọt 85–94%**. Nghĩa là công thức khoảng cách một mình gần như không chặn ai; mô hình học (dù TẠM THỜI) đang gánh phần nhận chủ.

## 2. Vì sao báo nhầm nguy hiểm

| Nguy cơ | Cơ chế | Mức độ ở Innate hiện tại |
|---|---|---|
| **Phiền, bỏ giao dịch** | Chủ thật bị hỏi thêm ~1/5 lần khi ngồi, ~2/5 lần khi đi | Cao nếu người dùng hay chuyển tiền khi di chuyển. Paper RBA (Wiefling 2020) cho thấy người dùng chấp nhận step-up vì nó *hiếm*; Freeman 2016 chọn ngưỡng theo ngân sách báo nhầm nhỏ |
| **"Mệt cảnh báo"** | Hỏi thêm quá thường thì người dùng coi đó là thủ tục, gõ cho xong; kẻ gian ngồi cạnh cũng quen | Làm giảm giá trị của chính bước step-up |
| **Giữ nhầm tiền của chủ** | `hold` do luật "giống bot" hoặc rủi ro > 0,55 | 0–1% với người nhận quen; cao hơn với người nhận mới (E24: 3–4%). Tiền gấp (viện phí, học phí) bị trễ |
| **Vòng lặp không học được** | Mẫu chỉ cập nhật sau `allow` tự tin (chống đầu độc). Lần chuyển khi đi thường bị hỏi thêm → không bao giờ dạy mẫu về tư thế đi | Người hay đi lại bị phạt mãi; báo nhầm không tự giảm theo thời gian |
| **Không công bằng** | Người lớn tuổi, run tay, khuyết tật vận động, người dùng một tay khi đi xe buýt: nhịp dao động lớn hơn → báo nhầm nhiều hơn một cách hệ thống | Chưa đo theo nhóm người; Eberz 2017 khuyên báo phân bố lỗi theo từng người (Gini), không chỉ trung bình |
| **Hạ ngưỡng để bớt phiền thì kẻ gian lọt** | Bảng E25: nới A, B thì chủ ít bị hỏi nhưng kẻ biết PIN lọt nhiều hơn | Phải chọn điểm vận hành có chủ đích, theo dịch vụ (Wiefling 2021) |
| **Thanh Accuracy check lạc quan** | Đường cong E30 đo khi *ngồi*, cùng tư thế | Ngoài đời (đi, đứng) độ chặn kẻ gian thật và tỷ lệ báo nhầm đều khác số trên thanh |

## 3. Có cần đưa ngồi và đi vào không? Có.

1. **Đăng ký nên có cả hai tư thế.** Đề xuất cho app: trong 5–10 lần nhập, nhắc "lần 1–3: ngồi; lần 4–5: vừa đi vừa nhập" (≈ "2–3 ngồi + 2 đi" ở bảng trên). Giảm báo nhầm khi đi ~41% → ~18%, đổi lại kẻ biết PIN lọt thêm ~10 điểm.
2. **Cho mẫu học tư thế mới một cách có kiểm soát:** sau khi chủ vượt qua `step_up` (gõ câu đúng), cho phép thêm phiên đó vào mẫu ("supervised update", như Windows Hello đòi PIN trước khi cập nhật; Lovisotto 2020). Cần bước step-up thật trong app trước (hiện chỉ báo).
3. **Thu dữ liệu đội có nhãn tư thế và nhãn người cầm máy** để đo lại trên người Việt, PIN tự đặt, cùng điện thoại (kẻ gian cầm đúng máy nạn nhân chưa được mô phỏng: số "lọt" thật có thể cao hơn).
4. **Báo cáo theo từng người** (ai bị báo nhầm nhiều), không chỉ trung bình.

## 4. Giới hạn của E33

- Chỉ 10 người cho bảng đủ mô hình (CI rộng); bảng 96 người tắt mô hình học.
- StrokePIN: PIN do người nghiên cứu giao (20 PIN chung), ngồi và đi trong cùng đợt thu (không có khoảng cách nhiều ngày), kẻ gian dùng máy khác.
- Không có cảm biến chuyển động trong pipeline; không biết phiên đang ở tư thế nào lúc chạy thật.
- Mô hình học là bản tạm, huấn luyện trên StrokePIN (người khác) + bot tự sinh.
