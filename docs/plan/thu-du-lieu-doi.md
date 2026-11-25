# Kế hoạch thu dữ liệu của đội (nhóm nhỏ, 25/11/2026)

Mục tiêu: thay các số "tạm" (mô hình huấn luyện trên dữ liệu công khai và bot sinh) bằng số đo trên **đúng điều kiện của đội**: cùng máy, cùng tư thế, PIN và câu thử thách của cùng một người. Đây là việc đáng giá nhất còn lại (xem `ai-research.md`, E22).

## Quy mô và lịch
- **10–20 người tự nguyện** (bạn bè, người quen), mỗi người **2 buổi cách nhau ≥ 1 ngày** (buổi 1 đăng ký, buổi 2 kiểm thử theo thời gian đúng FETA). Thu xong trước 01/12 để kịp số liệu vào slide; **sau 03/12 không sửa được slide**.
- Mỗi người dùng **điện thoại của chính họ** (bàn phím quen), ngồi cầm máy như bình thường. Ghi tư thế (`note`: ngồi/đi/nằm).
- Mỗi buổi: 3 lần nhập PIN `1593` (đăng ký), 5 lần nhập PIN kiểm thử, 5 câu thử thách ngẫu nhiên (`GET /v1/challenge`), vài lượt người thứ hai (kẻ gian biết PIN) bấm thử tài khoản của người đó.
- Bot: dùng `attacker/` (4 chiến thuật) và `adb` trên 1–2 máy thật để có tập bot độc lập với bộ sinh.

## Dùng sẵn hạ tầng hiện có
Backend đã có nhãn thu dữ liệu `meta` (`participant_id`, `sitting`, `role` genuine/impostor/bot, `tactic`, `note`) trong `POST /v1/sessions` và `GET /v1/export` (key ML). Huấn luyện lại: `research/experiments/train_human_model.py --export export.jsonl` (chưa thử trên dữ liệu thật). Web demo cần gắn `meta` khi thu: `TODO` đội web xác nhận cách bật chế độ thu.

## Dữ liệu được lưu
Chỉ **thời gian, toạ độ, kích thước chạm, loại sự kiện, số ký tự, lớp ký tự**. **Không lưu** nội dung PIN, tên, số điện thoại, nội dung chuyển khoản. `participant_id` là mã ngẫu nhiên (vd. `p07`), bảng ghép mã với tên người (nếu cần) giữ riêng, không đưa vào repo hay zip nộp.

## Phiếu đồng ý (mẫu, đội chỉnh và **nhờ người am hiểu pháp lý xem lại**)

> **PHIẾU ĐỒNG Ý THAM GIA THU THẬP DỮ LIỆU THAO TÁC**
> Đội <TÊN ĐỘI> thu dữ liệu cách chạm và gõ để nghiên cứu cho sản phẩm tham dự MoMo Tech Contest 2026.
> 1. **Dữ liệu thu:** thời điểm và vị trí các lần chạm, kích thước vùng chạm, thời điểm và loại phím gõ (không ghi nội dung PIN hay nội dung câu), kiểu thao tác. Không thu ảnh, giọng nói, danh bạ, vị trí, tin nhắn.
> 2. **Mục đích:** huấn luyện và đánh giá mô hình phát hiện bot và nhận diện chủ tài khoản của đội; trình bày số liệu tổng hợp trong bài dự thi.
> 3. **Lưu trữ và chia sẻ:** dữ liệu gắn mã ẩn danh, lưu trong nhóm nghiên cứu, **không** bán hay chia cho bên thứ ba; số liệu công bố chỉ ở dạng tổng hợp. Dữ liệu thô <có/không> nằm trong gói nộp (TODO: quyết định).
> 4. **Thời hạn:** xoá dữ liệu thô sau <ngày> (đề xuất: sau chung kết 11/12/2026) nếu bạn yêu cầu hoặc khi hết mục đích.
> 5. **Quyền của bạn:** có thể từ chối hoặc rút lui bất cứ lúc nào, yêu cầu xem hoặc xoá dữ liệu của mình, liên hệ <email đội>.
> 6. Dữ liệu thao tác có thể là **dữ liệu nhạy cảm** theo Luật Bảo vệ dữ liệu cá nhân 2025 và các văn bản hướng dẫn; việc thu dựa trên sự đồng ý của bạn tại phiếu này.
>
> Họ tên: ____ · Ngày: ____ · Chữ ký / xác nhận: ____ · Mã tham gia (đội điền): ____

## Phân tích sau khi thu (đã có sẵn mã)
- Nhận chủ theo thời gian (buổi 1 vs 2): `research/experiments/e9_strokepin_owner.py` làm mẫu, thay nguồn dữ liệu.
- Người/máy trên bot thật: `train_human_model.py`, giữ bot `adb` làm tập kiểm độc lập.
- Hiệu chỉnh ngưỡng phát lại (E5b), ngưỡng `fusion.py`, ánh xạ điểm `owner.py` (d=2 → 0,5 đang lỏng).
- Câu tiếng Việt: kiểm `vi_tone_late` và `vi_ime_coverage` ổn định giữa 2 buổi không (xem `innate-challenge-vi.md`).
- Báo cáo: FAR@FRR 5% kèm khoảng tin cậy bootstrap theo người; **ghi rõ cỡ mẫu nhỏ**, không so với số công bố trên hàng nghìn người.
