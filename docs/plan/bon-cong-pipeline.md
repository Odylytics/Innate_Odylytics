# Innate với 4 kênh bằng chứng: chuyển động, PIN, câu gõ, vùng chạm/vuốt

> 25/11/2026. Trả lời ý "tổng hợp 4 cổng thì AI có bắt được bot không". Số liệu: [`../research/ai-research.md`](../research/ai-research.md) (E19, E22, E23).

## Trả lời ngắn
**Có, nên làm, nhưng là hợp nhất 4 kênh bằng chứng, không phải 4 cổng nối tiếp phải qua hết.** Nếu mỗi cổng chặn nhầm chủ 5% mà bắt buộc qua cả 4, chủ bị chặn nhầm ~18,5% (1 − 0,95⁴). Cách đúng: cả 4 kênh cho điểm vào `fusion.py`; chỉ khi chưa chắc mới yêu cầu gõ câu (kênh 3); kết quả vẫn là `allow | step_up | hold`.

```
Chạy ngầm:   (1) chuyển động  +  (2) nhập PIN  +  (4) chạm/vuốt   ->  hợp nhất rủi ro
                                          chắc chắn là chủ/người ──► allow
                                          rõ ràng là máy ─────────► hold
                                          chưa chắc ─► (3) gõ câu ─► hợp nhất lại ─► allow | step_up | hold
```
Điểm mạnh của ý tưởng: kẻ tấn công phải giả **đồng thời** chạm, rung lắc, nhịp PIN, nhịp gõ, kiểu gõ dấu và các tín hiệu đó phải **khớp thời điểm với nhau**. Mỗi kênh riêng lẻ giả được (bài báo ActReal giả cả cảm biến chuyển động); khớp chéo giữa các kênh khó hơn. Chưa có thí nghiệm nào của đội đo sự khó đó.

## Từng kênh: đã có gì, bằng chứng, hạn chế
| Kênh | Dùng để | Bằng chứng của đội | Hạn chế nói thẳng |
|---|---|---|---|
| **1. Chuyển động** (gia tốc, con quay, trọng lực) | Bot: máy nằm yên trên bàn, không có tay cầm; nhận chủ: cách cầm | **E23 (StrokePIN):** chỉ chuyển động cho EER 0,04–0,07 và FAR 3–10% khi cùng tư thế (PIN thời gian + lệch tâm: EER 0,17–0,20, FAR 69–75%). **Đổi tư thế (ngồi → đi): EER 0,44–0,48, ngang đoán mò.** | **Số E23 lạc quan do thiết bị:** mỗi người một điện thoại, cảm biến lệch khác nhau, nên một phần là nhận máy chứ không nhận người. Kẻ cầm chính điện thoại của nạn nhân sẽ không bị bắt như vậy. StrokePIN chỉ lấy gia tốc/con quay ~5 Hz nên **không đo được cú giật khi chạm**. Tài liệu: HMOG 25,7–34,2% (chỉ chạm) → 7–10% (thêm chuyển động); BeCAPTCHA ~60% → 80–90%; **ActReal: tác tử cấp hệ thống giả được cả cảm biến, thành công 71,1% trước bộ dò chạm + chuyển động.** Web: `DeviceMotion` cần HTTPS và hỏi quyền trên iOS Safari, tối đa ~60 Hz. |
| **2. Nhập PIN** | Nhận chủ, người/máy, phát lại | Đã có: EER 0,16, FAR 37,5% (học máy), bot ngây thơ 100%, phát lại ≤ ±10% 100% | Đổi tư thế mất tín hiệu; kẻ biết PIN lọt nhiều. |
| **3. Gõ câu** | Thêm tín hiệu khi chưa chắc; kiểu gõ dấu tiếng Việt | **E22:** FAR 43–52% ở 30 phím (mô hình học 43%); bot gõ đều AUC 0,996 | Kiểu gõ tiếng Việt chưa đo trên người thật (chờ thử trên điện thoại). |
| **4. Vùng chạm / vuốt** | Bot (vuốt vận tốc đều) | **E19:** luật vận tốc đều bắt 100% bot vuốt đều, 0/20.896 nét người thật bị chặn nhầm | Vuốt **không** nhận chủ được (AUC ~0,5); kích thước vùng chạm là nhiễu thiết bị (E12b). Kênh 4 là cổng chống bot, không phải cổng nhận chủ. |

## Câu "tôi tên là nguyễn minh quân" hay câu ngẫu nhiên?
| | Câu cố định của người dùng | Câu ngẫu nhiên do máy chủ cấp (đang làm) |
|---|---|---|
| Ưu | Đăng ký và thử cùng câu: so cùng nội dung, tín hiệu tốt hơn; nhiều dấu (ô, ê, ễ, â) cho kênh kiểu gõ tiếng Việt | Chống phát lại **nội dung**; máy chủ biết câu mà không lưu nội dung; không phải dữ liệu cá nhân |
| Nhược | **Là tên người dùng: dữ liệu cá nhân**; kẻ nhìn trộm biết câu; kẻ ghi lại nhịp gõ phát lại nguyên văn; máy chủ không biết câu để kiểm "gõ đúng" (chỉ so băm có muối) | Câu đổi mỗi lần nên nhịp theo cặp phím khó so (E21b) |
Gợi ý: giữ câu ngẫu nhiên làm cổng chống bot/phát lại; câu cố định chỉ là phương án bổ sung về sau (người dùng tự chọn, có đồng ý riêng), chưa làm.

## Bot có bị bắt không?
- **Bot ngây thơ** (script, `adb`, mã độc cơ bản): có, kênh chạm/vuốt và PIN đã bắt ~100%; kênh chuyển động thêm "không có tay cầm".
- **Bot khôn** (lấy mẫu từ dân số, giả cảm biến): **không đảm bảo**. Đây là giới hạn đã biết (E4b: 20–73%; ActReal). E24/E27 (chạy đúng chuỗi `/score`, StrokePIN, chưa có kênh chuyển động và câu gõ) đo cụ thể: bot **biết mẫu chuẩn** của nạn nhân được `allow` 75–82%, phát lại có nhiễu ±15–30% được `allow` 48–72%; bot lấy mẫu dân số (CT4) chỉ `allow` 7% ([`../../research/results/e24_end_to_end.md`](../../research/results/e24_end_to_end.md)). Lợi thế duy nhất của hợp nhất là buộc kẻ tấn công giả nhất quán nhiều kênh; chưa đo kênh chuyển động và câu gõ có kéo các con số này xuống không.
- **Độc lập thì nhân, tương quan thì không:** nếu 4 kênh độc lập, FAR có thể nhân (vd. 37,5% × 43% ≈ 16%), nhưng cùng một tư thế, cùng một máy, cùng một phiên thì chúng **tương quan**, đừng nhân khi chưa đo.

## Việc nên làm tiếp (theo giá trị)
1. **Thử bot `adb` trên điện thoại nằm yên trên bàn vs người cầm máy:** đo độ rung chuyển động. Rẻ, quyết định xem kênh 1 có thật sự là cổng chống bot. Cần ≥ 100 Hz (gốc Android) hoặc ≥ 50 Hz (web, nếu máy cho).
2. **Thu dữ liệu đội có chuyển động**, mỗi người nhập PIN + gõ câu, cùng máy cho cả chủ và "kẻ gian" (người thứ hai cầm máy của chủ) để tách nhiễu thiết bị.
3. **Kiểm tra khớp thời điểm chạm và cú giật IMU** (cần tốc độ lấy mẫu cao).
4. Đặc trưng `imu_*` trong `features.py`: **chưa viết**; viết khi có dữ liệu cùng máy.
