# Innate Challenge bằng tiếng Việt (Telex/VNI)

> 25/11/2026. Mở rộng [`innate-challenge.md`](innate-challenge.md). Đây là **giả thuyết + đếm lý thuyết + mã trích đặc trưng**. **Chưa có dữ liệu người Việt gõ thật**: mọi lợi ích bên dưới chưa được đo.

## Tình huống

Nhập PIN xong mà Innate không chắc (điểm chủ thấp, người nhận mới, số tiền lớn) thì hiện một câu tiếng Việt có dấu, ví dụ "Hôm nay trời đẹp quá", yêu cầu gõ lại. Nội dung câu do máy chủ sinh nên không phải dữ liệu riêng tư. Bước này gộp với điểm PIN, chưa thay nó.

## Vì sao tiếng Việt có thêm tín hiệu mà tiếng Anh không có

Gõ dấu bằng Telex/VNI tạo ra **phím biến đổi**: phím không thêm ký tự mà đổi chữ đã gõ (`o` `w` → ơ, `f` → dấu huyền). Có 4 nguồn khác biệt cá nhân:

1. **Telex hay VNI** (phím chữ hay phím số).
2. **Vị trí phím dấu thanh**: ngay sau nguyên âm ("trowfi") hay để cuối âm tiết ("trowif"). Đây là đúng ý "có người gõ cái này trước, có người gõ cái kia trước".
3. **Cách sửa lỗi**: gõ nhầm dấu thì xoá lùi hay gõ `z`, và tỉ lệ sửa.
4. **Độ khựng ở phím biến đổi**: dừng nghĩ trước khi bấm dấu thanh.

Hai điểm khác đáng giá cho bảo mật:
- **Thói quen 1 và 2 không phụ thuộc câu cụ thể**, nên không vướng điểm yếu của E13 (câu thử khác câu đăng ký làm nhịp theo cặp phím không còn so được).
- **Bot phải giả lập cả bộ gõ.** Câu có dấu mà không có phím biến đổi nào (`vi_ime_coverage` = 0) nghĩa là đặt thẳng văn bản, dán, `adb input text` (bỏ qua bộ gõ) hoặc bàn phím không có tiếng Việt. Máy chủ biết số phím biến đổi tối thiểu của câu nên kiểm được mà không cần nội dung.

## Đếm biến thể (E18, lý thuyết)

`research/experiments/e18_vi_variation.py`, kết quả `research/results/e18_vi_variation.txt`. Chỉ đếm vị trí dấu thanh × 2 bộ gõ:

| Câu | Phím biến đổi | Số cách gõ | Trần thông tin |
|---|---|---|---|
| Hôm nay trời đẹp quá | 6 | 8 | 3,0 bit |
| Chuyển tiền cho mẹ ở quê | 8 | 8 | 3,0 bit |
| Hôm nay trời đẹp quá mình đi uống cà phê nhé | 13 | 72 | 6,2 bit |
| Tuần này trời nắng đẹp quá | 10 | 96 | 6,6 bit |
| mua 4 ca phe 27 (không dấu, đối chứng) | 0 | 1 | 0 |

**Nói thẳng:** câu ví dụ "Hôm nay trời đẹp quá" chỉ có 8 cách gõ, tức tối đa 3 bit, vì chỉ "trời" và "đẹp" cho chọn vị trí dấu thanh. Muốn nhiều biến thể hơn thì chọn câu có **nhiều âm tiết có dấu thanh và có chữ đứng sau nguyên âm** (nắng, tuần, uống, nhé). Đây là **trần**: người thật dồn vào vài thói quen, nên thông tin thật thấp hơn. Tiếng Việt cho thêm một kênh, không phải kênh mạnh như "bảo mật hơn hẳn".

## Thiết kế ưu tiên điện thoại (25/11)

- **Câu viết thường, chỉ chữ cái và khoảng trắng** (`scoring/challenge.py`): không Shift, không đổi lớp phím số, nên nhịp gõ ít nhiễu hơn và Telex/VNI đều gõ được. Mọi câu có ≥ 4 âm tiết có chỗ chọn dấu thanh (test kiểm).
- **`GET /v1/challenge`** cấp câu + token ký HMAC (`NHIP_CHALLENGE_SECRET`). App gửi lại token trong `fields[name=challenge]`; máy chủ biết câu mà không lưu nội dung gõ. Token giả bị bỏ qua. **Chưa chống dùng lại token** (không có kho nonce).
- **Điện thoại không thấy phím nào** (Gboard báo `keyCode 229`, chỉ có sự kiện soạn chữ). Vì vậy `sdk/innate-compose.js` suy ra phím biến đổi từ **độ dài ô nhập không đổi** (n = 0), và `cls` = null. Hệ quả: **Telex hay VNI không đo được trên web điện thoại** (`vi_vni_frac` bị bỏ, không đoán); chỉ đo được ở bàn phím máy tính hoặc SDK native. Phần còn lại (vị trí dấu thanh, sửa lỗi, độ khựng, có dùng bộ gõ không) vẫn đo được.
- **Giá trị gán bằng script** (không có sự kiện `input`) bị `finish()` phát hiện thành `set_text`. `ACTION_SET_TEXT` của mã độc cũng vậy ở app native.
- **Tắt tự sửa/gợi ý** (`autocorrect`, `autocomplete`, `spellcheck` = off); chọn gợi ý từ bàn phím ghi thành `paste` (độ dài tăng > 1).
- **SDK native (Android/iOS)** mới là đường chắc: `TextWatcher.onTextChanged(count, before)` cho đúng thông tin này kèm `InputConnection`. Chưa viết.

## Mã đã có

| Phần | File | Trạng thái |
|---|---|---|
| Đặc trưng kiểu gõ | `backend/app/scoring/vi_ime.py` | Có test (người gõ giả) |
| Câu + token | `backend/app/scoring/challenge.py`, `GET /v1/challenge` | Có test |
| Nối vào chấm điểm | `features.extract` (khi có `token` hợp lệ) và `human.py`: `challenge_no_ime` tối đa 0,3 (tín hiệu mềm) | Có test |
| Nhận chủ | `owner.py` **cố ý loại** `vi_*` cho tới khi có dữ liệu | Chưa dùng |
| Thu sự kiện điện thoại | `sdk/innate-compose.js` (+ test Node) | Test bằng chuỗi sự kiện GIẢ theo đặc tả, **chưa thử máy thật** |
| Thử trên máy thật | `sdk/probe.html` | Người có điện thoại mở, gõ, sao chép log (xem dưới) |

## Việc người có điện thoại làm (đo bởi người, 15 phút)

Mở `sdk/probe.html` (host bất kỳ hoặc mở file) trên: Gboard Telex, Gboard VNI, bàn phím iOS Telex, mỗi loại gõ "trời đẹp quá" với dấu thanh ngay sau nguyên âm rồi lần nữa để cuối âm tiết. Gửi log. Cần trả lời: (1) `keyCode` có là 229 không; (2) phím dấu thanh có cho `dLen = 0` không (nếu bàn phím thay cả từ, `dLen` khác 0 và giả định sai); (3) iOS có sự kiện `compositionupdate` không. Nếu (2) sai thì `vi_ime.py` phải đổi cách nhận biến đổi.

## Rủi ro và việc chưa kiểm chứng

| Việc | Vì sao quan trọng |
|---|---|
| SDK có thấy phím biến đổi không? | Web trên Gboard thường báo `keyCode 229` và sự kiện composition, không phải phím. Phải thử để biết SDK tính được `n=0` hay chỉ thấy văn bản đổi. Cần làm ở SDK native hoặc thử `beforeinput`. |
| Quy tắc bộ gõ | Số cách đặt dấu thanh giả định bộ gõ cho phép gõ dấu sau nguyên âm. Cần thử trên Unikey, Gboard, bàn phím iOS. Chưa đếm thứ tự dấu mũ/dấu thanh, w trễ, kiểu đặt dấu cũ/mới. |
| Người không có bộ gõ tiếng Việt | Không gõ được câu có dấu. Luôn giữ đường thay thế (câu không dấu hoặc OTP). `vi_ime_coverage` = 0 không được tự dẫn tới `hold`. |
| Người đổi bàn phím | Đổi Telex↔VNI hoặc đổi thiết bị làm đặc trưng nhảy. Phải học trên nhiều lần, không dùng một lần. |
| Dữ liệu | Aalto là tiếng Anh nên **không** kiểm được gì về tiếng Việt. Cần thu người Việt gõ câu thật (đội), có phiếu đồng ý. |

## Thu dữ liệu gợi ý (để đo thật)

20+ người, 2 buổi cách nhau ít nhất một ngày, mỗi buổi 5 câu ngẫu nhiên có ≥ 8 phím biến đổi, trên máy của chính họ (giữ bộ gõ quen). Lưu `t, kind, n, cls`. Đo: (a) `vi_tone_late` và `vi_vni_frac` ổn định giữa 2 buổi không, (b) FAR@FRR 5% khi gộp với nhịp, (c) bot gõ qua `adb`/set_text bị `vi_ime_coverage` bắt bao nhiêu.
