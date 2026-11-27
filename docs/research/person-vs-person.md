# Xác minh người với người (1:1) và thanh "Accuracy check" lúc đăng ký (27/11/2026)

## 1. Đã có ai làm "phân biệt người với người" bằng sinh trắc hành vi chưa?

**Có, rất nhiều.** Xác minh 1:1 (phiên này có phải của chủ tài khoản, hay của người khác dù biết PIN) là bài toán gốc của sinh trắc nhịp gõ/chạm. Các công trình đã có trong `papers/` (tóm tắt chi tiết: `notes/owner_verification.md`, `paper-report.md`):

| Công trình | Làm gì | Số liệu |
|---|---|---|
| Zheng et al. 2014, *You Are How You Touch* | Nhịp + vị trí chạm khi gõ PIN trên điện thoại, >80 người | EER 3,65–7% (85 mẫu huấn luyện/người, PIN chung) |
| Buschek et al. 2015 (CHI) | Thêm lệch tâm chạm vào nhịp | EER giảm 26–37% so với chỉ nhịp; khác buổi thì EER gấp đôi |
| Killourhy & Maxion 2009 | So 14 bộ dò, cùng mật khẩu, 51 người | Scaled Manhattan tốt nhất, EER 9,6% (dùng trong `owner.py`) |
| Acien et al. 2021, TypeNet | Mạng học chung, xác minh người chưa thấy | EER di động 10,7% (1 mẫu) → 6,3% (10 mẫu) |
| Stragapede et al. 2022/2023 (Transformer, KVC) | Benchmark 5 lượt đăng ký | EER 6,99% (1) → 3,84% (5) → 3,15% (10) |
| Khan et al. 2018 | Kẻ gian tập bắt chước có AR hướng dẫn | Vượt được 87% sau ~4 phút luyện |

Kết luận: phân biệt người với người **không phải ý tưởng mới**. Điểm khác của Innate là đặt nó vào bước xác nhận chuyển tiền của ví, gộp với tín hiệu người/máy và ngữ cảnh, và đo trung thực trên PIN điện thoại thật (E9, E30).

**Thanh tiến độ/chất lượng mẫu khi đăng ký** hiếm thấy hơn trong tài liệu học thuật. Một lượt tìm (27/11) chỉ thấy bằng sáng chế hiển thị số mẫu còn thiếu dạng "nhiệt kế" ([US 7809170](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7809170)), thước đo chất lượng mẫu tương quan với lỗi (Morales et al. 2015, [repositorio.uam.es](https://repositorio.uam.es/bitstream/handle/10486/665359/towards_morales_LNCS_2015_ps.pdf?sequence=1)), và một chỉ số chất lượng mẫu dự báo FAR ([PLoS ONE 2022](https://doaj.org/article/0df83e8ac87840bfa9022a584586514c)). Chưa đọc toàn văn; **chưa thấy** công trình làm thanh này cho nhịp PIN.

## 2. Thanh "Accuracy check" trong demo đo gì

Hai con số, cả hai đều có nguồn:

1. **Thanh chính = % kẻ biết PIN bị chặn** = 1 − FAR@FRR5% theo số lượt đăng ký k (`web/src/enrollCurve.ts`).
   - k = 2, 3, 4: **đo thật** trên StrokePIN, khoảng cách của backend (E30): 14%, 50%, 57%.
   - k ≥ 5: **ngoại suy** bằng luật luỹ thừa qua k = 3 và 4 (StrokePIN có tối đa 5 lượt mỗi người–PIN nên không còn lượt thử). Giao diện ghi rõ "ngoại suy, chưa đo". k = 5 → ~62%, k = 10 → ~74%.
2. **Độ ổn định nhịp của chính người đăng ký** (`owner.consistency`): mỗi lượt chấm với mẫu dựng từ các lượt còn lại (leave-one-out), lấy trung bình. Cao = gõ đều tay. Đây **không** phải độ chính xác nhận người.

Không đưa số ngoại suy lên slide như số đo. Cách nói an toàn: "càng nhập nhiều lần càng chặn được nhiều kẻ biết PIN; 3→4 lượt đo thật, trên 4 là ước lượng".

## 3. Luồng demo cho ban giám khảo

1. `#/demo` → nhập tên → tài khoản `judge_<tên không dấu>` (cùng tên = cùng tài khoản, không phân biệt hoa thường/dấu).
2. Gõ PIN `159357` từ 5 đến 10 lần; thanh tăng sau mỗi lần. Bấm **Xong** (mở sau 5 lần) hoặc tự khoá ở lần 10.
3. Mở ví, chuyển tiền: Innate chấm điểm ở bước xác nhận.
4. Giám khảo khác đăng nhập **bằng tên người kia** và chuyển tiền: kỳ vọng `step_up`/`hold`. Hoặc bấm "Kẻ trộm biết PIN".

## 4. Thay đổi backend và giới hạn

- `POST /v1/users/{id}/enroll` nhận `keep_open` (mặc định false: hành vi cũ, khoá ở lượt 3). Với `keep_open=true`, mỗi lượt dựng lại mẫu chuẩn; khoá khi gọi `POST /v1/users/{id}/enroll/finish` hoặc đủ 10 lượt. Mẫu chuẩn cũ không có cờ `open` vẫn coi là đã khoá.
- **Giới hạn bảo mật:** trong lúc đăng ký còn mở, ai có SDK key và biết user_id đều thêm được lượt (tối đa 10). Đăng nhập bằng tên **không có mật khẩu**: chỉ dùng cho demo.
