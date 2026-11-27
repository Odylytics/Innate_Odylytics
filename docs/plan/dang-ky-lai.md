# Đăng ký lại có kiểm soát (sau 409 ở `/enroll`)

> Thiết kế 26/11/2026, **chưa cài đặt**. Giải quyết khoảng trống ghi ở `CLAUDE.md`: `/enroll` trả 409 khi đã có mẫu chuẩn (chống chèn nhịp kẻ gian), nhưng chủ vẫn cần một đường hợp lệ để thêm lượt đăng ký (vd. đổi máy, nhịp thay đổi theo thời gian).

## Nguyên tắc
- Chỉ **chủ đã xác thực bằng kênh ngoài Innate** (OTP/sinh trắc của app ví) mới được mở cửa sổ đăng ký lại. Innate không tự xác thực.
- Không bao giờ đăng ký lại chỉ vì điểm thấp: điểm thấp có thể là kẻ gian hoặc chủ gõ khác thường ngày, Innate không phân biệt được (E9).
- Mẫu cũ giữ nguyên cho đến khi mẫu mới đủ lượt; lượt mới **thêm**, không thay.

## Luồng
1. App ví xác thực chủ bằng kênh mạnh, rồi gọi `POST /v1/users/{id}/enroll/window` (key SDK + token một lần do backend ví ký, hết hạn 10 phút). Backend đặt `user.enroll_until`.
2. Trong cửa sổ, `/enroll` nhận thêm lượt (thay vì 409), tối đa 5 lượt mỗi cửa sổ, 1 cửa sổ/ngày.
3. Đủ lượt: dựng lại mẫu từ **tất cả** lượt đăng ký (cũ + mới); xoá cờ `frozen` (xem E7: mẫu đóng băng chỉ mở lại bằng đường này); `mu0` đặt lại.
4. Ghi nhật ký (ai mở, lúc nào, bao nhiêu lượt) để dashboard hiện.

## Rủi ro còn lại
- Kẻ chiếm được phiên đã xác thực vẫn tiêm được nhịp của mình: giới hạn bằng 5 lượt/cửa sổ, 1 cửa sổ/ngày và cảnh báo khi mẫu mới lệch > 1 sd so với mẫu cũ.
- Không có dữ liệu thật về mức nhịp của cùng người thay đổi qua nhiều ngày; ngưỡng 1 sd là giả định.
