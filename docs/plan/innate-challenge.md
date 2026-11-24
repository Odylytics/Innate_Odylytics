# Innate Challenge — gõ một câu để chứng minh "người thật, đúng chủ"

> Ý tưởng chốt ngày 24/11/2026. Bổ sung cho lớp kiểm chứng thụ động của Innate ([`positioning.md`](positioning.md)). Số liệu: [`../research/ai-research.md`](../research/ai-research.md), E13.

## Ý tưởng một đoạn

Mặc định Innate chạy **thụ động**: người dùng chỉ nhập PIN như bình thường và Innate chấm điểm nhịp chạm. Khi hệ thống **không chắc** (điểm khớp chủ thấp, người nhận mới, số tiền lớn), thay vì bắt nhập OTP hay quét mặt, nó hiện **một câu ngắn gồm chữ và số do hệ thống sinh ngẫu nhiên** ("mua 4 ca phe 27") và người dùng **gõ lại đúng câu đó**, mất chừng 10 giây. Một câu 15–20 ký tự cho nhiều tín hiệu hơn nhiều so với 6 lần chạm PIN, và nội dung câu do hệ thống tạo nên **không phải dữ liệu riêng tư của người dùng**.

```
Giao dịch ─► Innate thụ động chấm điểm (PIN)
              ├─ chắc là chủ, là người ─────────────► allow
              ├─ rõ ràng là máy ────────────────────► hold
              └─ KHÔNG CHẮC ─► Innate Challenge: "gõ lại câu này"
                                 └─ gộp thêm tín hiệu ─► allow / step_up (OTP, khuôn mặt) / hold
```

## Vì sao có khả năng tốt hơn

1. **Nhiều tín hiệu hơn.** Nhịp gõ, độ biến thiên, thói quen sửa lỗi trên 20–30 phím.
2. **Khó điền sẵn.** Câu mới mỗi lần: không có văn bản nào để mã độc đặt sẵn; đặt thẳng cả câu (`ACTION_SET_TEXT`) hay dán nguyên câu là dấu hiệu máy, vì người thật gõ từng phím.
3. **Ít ma sát hơn OTP/khuôn mặt** *(chưa đo)*: một thao tác quen thuộc, không đổi app, không chờ SMS.
4. **Hợp tinh thần "Human Centered":** hỏi thêm **khi cần**, không phiền người dùng mỗi giao dịch, và người dùng thấy rõ vì sao bị hỏi.

## Bằng chứng (E13, người thật gõ câu trên điện thoại, dữ liệu Aalto)

Mỗi câu cắt ở n phím đầu (n = 6 ≈ độ dài PIN 6 số). Chỉ dùng thời gian giữa các phím; đăng ký 3 câu, **câu kiểm thử khác nội dung câu đăng ký** (đúng tình huống câu ngẫu nhiên).

| Số phím n | Nhận chủ: EER | Nhận chủ: FAR ở FRR 5% | Bắt bot gõ đều (AUC) | Bắt bot lấy mẫu dân số (AUC) |
|---|---|---|---|---|
| 6 | 0,364 | 0,807 | 0,915 | 0,719 |
| 10 | 0,337 | 0,733 | 0,969 | 0,764 |
| 20 | 0,279 | 0,591 | 0,996 | 0,848 |
| 30 | **0,245** | **0,489** | 0,995 | 0,891 |

**Giả thuyết được ủng hộ về hướng:** nhiều phím hơn thì nhận chủ tốt hơn rõ rệt (EER 0,364 → 0,245; kẻ gian lọt ở FRR 5% từ 81% xuống 49%, khoảng tin cậy không chồng nhau) và bắt bot gõ đều gần như hoàn hảo từ 20 phím.

## Điều KHÔNG được chứng minh (nói thẳng)

- **Số tuyệt đối vẫn yếu:** ở 30 phím, EER 24,5% và ~49% kẻ gian lọt ở FRR 5% (chỉ 6 đặc trưng nhịp, 3 câu đăng ký). Câu thử thách **không phải phép màu**; nó cải thiện, không biến điểm "chủ" thành cổng chặn.
- **Không so được với PIN:** dữ liệu Aalto không có thời gian giữ phím và toạ độ, khác bộ StrokePIN. Cũng **chưa đo** việc gộp PIN + câu thử thách.
- **Dữ liệu là chép câu mẫu tiếng Anh** trên điện thoại (một bài kiểm tra tốc độ gõ), không phải gõ chuỗi chữ-số ngẫu nhiên khi sắp mất tiền: người dùng đang căng thẳng, gõ chuỗi lạ thì chậm và khác thói quen.
- **Bot trong E13 là bot giả** và chỉ hai họ; kẻ tấn công biết hệ thống có thể gõ phím giả nhịp người (xem dưới).
- **Chưa đo ma sát** (thời gian, tỷ lệ bỏ giữa chừng, người khuyết tật, bàn phím giọng nói).

## Kẻ tấn công làm gì, và Innate Challenge chặn được gì

| Kẻ tấn công | Chặn được? | Ghi chú |
|---|---|---|
| Đặt thẳng cả câu (`ACTION_SET_TEXT`) | **Có**, nếu SDK **native** thấy văn bản đổi mà không có sự kiện phím | Web SDK **không** thấy được: cần native (R1/R9) |
| Dán nguyên câu | Có, bằng cờ `challenge_pasted` | Cần tắt chọn/sao chép văn bản câu thử thách (vẽ bằng ảnh/canvas) |
| Gõ phím tự động nhịp đều | Có (AUC ~0,99 ở ≥ 20 phím, bot đã thấy) | Bot **lạ** vẫn yếu (E4b, E11) |
| Gõ phím tự động **nhịp lấy mẫu từ người thật** | **Yếu** (AUC 0,72–0,89) | Kẻ tấn công thích nghi (ActReal 2026) vẫn qua mặt được |
| Phát lại nhịp đã ghi của nạn nhân | **Chưa chặn** | Câu mới mỗi lần không tự chặn phát lại *thời gian*: kẻ tấn công gõ câu đúng với nhịp đã ghi. Cần mở rộng kiểm tra phát lại (E5) sang chuỗi khoảng cách phím |
| Kẻ đứng cạnh biết PIN | Một phần | Cải thiện nhận chủ nhưng yếu (xem trên) |

**Kiểm tra "đã gõ đúng câu" mà không lưu nội dung:** app so văn bản gõ với câu hiển thị ngay trên máy và gửi lên **mã băm có muối** (hoặc chỉ cờ khớp/không khớp) cùng thời gian các phím; máy chủ biết câu đúng nên kiểm tra được mà không lưu văn bản. Điều này **giả định app không bị can thiệp** (lớp 1 trong [`positioning.md`](positioning.md)).

## Thiết kế câu thử thách

- **Ngắn, 12–20 ký tự, chữ + số, không dấu.** Dài hơn cho nhiều tín hiệu hơn (E13) nhưng tăng ma sát: cần đo.
- **Ngẫu nhiên mỗi lần**, phát từ máy chủ kèm mã dùng một lần (nonce), hết hạn sau vài chục giây.
- **Tắt tự sửa, dự đoán, gợi ý** ở ô nhập (`autocorrect=off`, `autocomplete=off`, `spellcheck=false`) để nhịp gõ không bị nhiễu.
- **Luôn có đường thay thế** (OTP/khuôn mặt) cho người không gõ được (khuyết tật, giọng nói): Innate không bao giờ là cách duy nhất để hoàn tất giao dịch.

## Quyền riêng tư

Nội dung câu do hệ thống sinh nên **không phải dữ liệu cá nhân của người dùng** (tốt hơn việc đọc ô ghi chú tự do). Vẫn chỉ lưu thời gian, loại sự kiện, số ký tự, lớp ký tự. Nhịp gõ là dữ liệu sinh trắc nhạy cảm: cần đồng ý rõ ràng (Luật BVDLCN 2025, NĐ 356/2025).

## Trạng thái hiện thực

| Đã có (24/11) | Chưa có |
|---|---|
| `SessionIn.fields` nhận ô `challenge` kèm `expected_len`; đặc trưng nhịp gõ; luật `set_text` hoặc dán nguyên câu = máy; 1 test | Giao diện hiển thị câu; bộ sinh câu và nonce; kiểm tra băm; SDK native; kiểm tra phát lại chuỗi phím; **bất kỳ dữ liệu thật nào trong ô thử thách** |

**Việc cần làm để biến thành sản phẩm:** (1) thu dữ liệu người thật gõ câu ngẫu nhiên chữ-số (đội), (2) đo gộp PIN + câu, (3) đo ma sát, (4) kiểm tra phát lại cho chuỗi phím, (5) SDK native cho `set_text`.
