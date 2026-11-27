# Thu những dữ liệu gì từ người tham gia (trang `#/collect`)

> 25/11/2026. Trả lời câu "nên thu những loại dữ liệu gì". Căn cứ: các thí nghiệm E9–E27 trong [`../research/ai-research.md`](../research/ai-research.md), giới hạn của trình duyệt, và Luật Bảo vệ dữ liệu cá nhân 2025 (thu tối thiểu, có đồng ý). Kế hoạch thu tổng thể: [`thu-du-lieu-doi.md`](thu-du-lieu-doi.md).

## 1. Nguyên tắc chọn

1. **Chỉ thu thứ trả lời được một câu hỏi đã có thí nghiệm chờ sẵn.** Mỗi dòng dưới đây ghi nó phục vụ thí nghiệm nào.
2. **Câu hỏi lớn nhất còn mở là "nhận ra chủ"**, không phải "người hay máy" (bot ngây thơ đã bắt ~100%). Nhận chủ yếu vì: nhiễu do khác máy (E12b, E23) và mẫu đăng ký ít (E22). Dữ liệu đội phải sửa đúng hai chỗ này: **cùng máy, nhiều buổi**.
3. **Trình duyệt chỉ thấy được một phần.** Thứ chỉ app native thấy (`set_text`, chọn không có chạm, cảm biến ≥ 100 Hz) thì không hứa trên web.
4. **Dữ liệu cá nhân thu càng ít càng tốt.** Họ tên + email + mã PIN thử đã được lưu cùng dữ liệu chạm (quyết định của đội, 25/11); không thêm định danh nào khác.

## 2. Đang thu (bản hiện tại)

Trang chỉ hỏi họ tên + email (kèm một ô đồng ý), rồi cho nhập PIN 5 lần trên bàn phím 10 số. Không hỏi lần thu (đội quyết định 25/11, để trang thật gọn); `sitting` luôn gửi 1. Thời điểm thu vẫn có trong `created_at`.

| Dữ liệu | Trường | Dùng cho |
|---|---|---|
| Họ tên, email | `meta.full_name`, `meta.email` | Liên hệ, xoá theo yêu cầu, gom phiên một người (`participant_id` băm từ email) |
| Mã PIN thử tự đặt (6 số) | `pin_taps[].key` | Nghiên cứu theo phím và cặp phím (khoảng cách hình học giữa hai phím, E14/E21b); kiểm "gõ PIN mới" so với PIN quen |
| Thời điểm nhấn/nhả từng phím | `pin_taps[].t_down`, `t_up` | Thời gian giữ phím, khoảng cách giữa hai phím: lõi của nhận chủ (E9, E12b) và người/máy (E4b) |
| Vị trí chạm so với tâm phím | `x, y, key_cx, key_cy, key_w, key_h` | Độ lệch tâm (E12b); bot chạm đúng tâm |
| Kích thước vùng chạm | `w, h` | Chỉ để kiểm nhiễu thiết bị (E12b bỏ khỏi mô hình chủ). Giữ vì rẻ, đừng dựa vào |
| Màn hình và lúc chạm đầu tiên | `screens[]` | Thời gian do dự trước khi gõ |
| Mã máy | `device_id` | Tách "nhận người" với "nhận máy" |

## 3. Nên thu thêm, theo giá trị

| # | Dữ liệu | Trên web? | Vì sao (bằng chứng) | Chi phí |
|---|---|---|---|---|
| 1 | **Buổi 2 cách ≥ 1 ngày** cùng người, cùng máy, cùng PIN | Có (email + `created_at`) | Không có buổi 2 thì mọi số nhận chủ chỉ là "cùng buổi", lạc quan. FETA bắt buộc chia theo thời gian | Nhắc người tham gia quay lại. **Cần ghi rõ trên trang: lần sau nhập lại đúng mã PIN cũ** |
| 2 | **Kẻ gian biết PIN, trên chính máy của chủ** | Có (cần thêm lại vai "người biết PIN" và cho nhập mã của chủ) | E24: kẻ biết PIN vẫn `allow` 28%. Dữ liệu công khai (StrokePIN) cho kẻ gian dùng máy khác, lẫn nhiễu thiết bị; chỉ dữ liệu đội có "cùng máy" | Người thứ hai, 5 lần nhập |
| 3 | **Câu thử thách tiếng Việt** (`GET /v1/challenge`, gõ lại câu) | Có thời gian gõ; kiểu gõ dấu Telex/VNI **chưa chắc** (cần thử `beforeinput`/composition trên Gboard và iOS) | E13/E22: 30 phím cho EER 0,25 so với 0,36 khi chỉ 6 phím; tiếng Việt thêm `vi_tone_late` (chưa đo trên người thật) | 5 câu mỗi buổi, ~2 phút. Chỉ lưu `t, kind, n, cls`, **không lưu nội dung câu** |
| 4 | **Cảm biến chuyển động** (gia tốc, con quay, hướng máy) trong lúc gõ PIN | Có hạn chế: cần HTTPS, iOS Safari phải bấm cho phép, ~60 Hz | E23: chỉ chuyển động cho EER 0,04 (nghi do nhận máy). Cần dữ liệu **cùng máy, hai người** mới biết là nhận người hay nhận máy; và có phân biệt "máy nằm trên bàn (bot)" với "tay cầm" không | Phải thêm trường `imu` vào API (chưa có) và xin quyền riêng. **Là dữ liệu nhạy cảm hơn**: hỏi riêng, cho từ chối mà vẫn tham gia được |
| 5 | **Vuốt xác nhận** | Có (SDK đã có `swipes`) | E19: luật vận tốc đều bắt 100% bot vuốt đều, 0/20.896 nét người bị chặn nhầm, nhưng đo trên Touchalytics, chưa trên vuốt xác nhận của app | Thêm một bước vuốt sau mỗi lần PIN |
| 6 | **Thông tin máy tối thiểu**: hãng/đời máy (tự khai hoặc `userAgent`), kích thước màn hình, `devicePixelRatio`, ngón/tay dùng (cái/trỏ, trái/phải) | Có | Giải thích phương sai giữa người; kiểm toạ độ có cần chuẩn hoá theo màn hình không | Rất thấp |

## 4. Không nên thu

| Dữ liệu | Lý do |
|---|---|
| Lực nhấn (`pressure`) | Trình duyệt thường trả hằng số; quy tắc thiết kế: không dựa vào |
| `isTrusted`, ảnh, giọng nói, vị trí GPS, danh bạ | Không phục vụ thí nghiệm nào; tăng rủi ro pháp lý |
| Nội dung câu thử thách, số tài khoản thật | Không cần cho đặc trưng; máy chủ đã biết câu qua token |
| Mật khẩu/PIN thật của người tham gia | Đã cảnh báo hai lần; nếu ai báo nhập nhầm PIN thật thì xoá ngay phiên của họ |
| Tuổi, giới tính, nghề nghiệp | Cỡ mẫu 10–20 người không đủ để phân tích theo nhóm; chỉ thêm định danh |

## 5. Đề xuất thứ tự cho trang thu

1. Trang hiện chỉ hỏi tên + email theo quyết định của đội; các mục ở phần 3 (buổi 2, kẻ gian) **chưa làm**. Nếu muốn số nhận chủ đáng tin hơn, mục 3.1 (quay lại buổi 2, nhận ra qua email + `created_at`) là việc rẻ nhất.
2. **Trước 30/11:** thêm lại vai kẻ gian biết PIN, nhập trên máy của chủ (mục 3.2).
3. **Nếu kịp:** câu thử thách (mục 3.3) sau khi thử bộ gõ trên điện thoại thật; vuốt xác nhận (mục 3.5).
4. **Để sau nộp bài:** cảm biến chuyển động (mục 3.4): cần sửa API, quyền iOS, và phiếu đồng ý riêng.

Mỗi người tham gia, tối thiểu: 2 buổi × 5 lần PIN + 5 lần kẻ gian trên máy của họ. Với 10–20 người là đủ để **chạy được** `team_analysis.py` (T1–T5), nhưng khoảng tin cậy sẽ rộng; ghi rõ cỡ mẫu khi đưa số lên slide.

## 6. Lưu ý pháp lý và vận hành

- Họ tên, email và mã PIN thử nằm cùng dữ liệu chạm trong mỗi phiên, nên file `/v1/export` là dữ liệu cá nhân: chỉ người giữ key ML được xuất, không đưa vào repo hay zip nộp.
- Phiếu đồng ý phải liệt kê đúng những gì thu. Khi thêm mục nào ở phần 3 thì sửa phiếu trong `web/src/Collect.tsx` cùng lúc.
- Nêu thời hạn xoá (đề xuất: sau chung kết 11/12/2026) và cách yêu cầu xoá (đặt `VITE_COLLECT_CONTACT`).
- Nhờ người am hiểu pháp lý xem lại phiếu (Luật BVDLCN 2025), như đã ghi trong `thu-du-lieu-doi.md`.
