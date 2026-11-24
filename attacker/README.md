# TIBOM — Bộ giả lập hacker

Người 2. Sinh phiên bot theo 4 chiến thuật (mục 5.1 kế hoạch), đo tỷ lệ bắt theo từng chiến thuật, và tấn công thật lên điện thoại demo qua `adb`.

## Cài đặt

```powershell
cd attacker
uv sync
```

API key: đặt `NHIP_API_KEY` (key của bản deploy nằm ở `backend/.env.deploy-key` trên máy Người 2). URL mặc định `http://localhost:8000`; bản online dùng `--api https://nhip-api-taupe.vercel.app`.

```powershell
$env:NHIP_API_KEY = "<key>"
```

## 4 chiến thuật

| # | Chiến thuật | Cách sinh | Mô phỏng |
|---|---|---|---|
| 1 | Bấm cách đều, đúng tâm nút | Giữ phím 60 ms, cách 140 ms, toạ độ = tâm phím, kích thước chạm cố định, vuốt thẳng | Mã độc ngây thơ / `adb input tap` |
| 2 | Thêm nhiễu thời gian | Giữ 40–140 ms, cách 80–350 ms ngẫu nhiên; vẫn đúng tâm nút | Mã độc có né cơ bản |
| 3 | Phát lại phiên người thật + nhiễu | Lấy một phiên thật, thời gian ±5%, toạ độ ±2 px | Mã độc đã ghi lại phiên của nạn nhân |
| 4 | Lấy mẫu từ phân bố người thật | Mỗi giá trị (giữ phím, khoảng cách, lệch tâm, kích thước chạm, đường vuốt) lấy độc lập từ toàn bộ phiên người | Kẻ tấn công có dữ liệu nhiều người (Serwadda & Phoha 2013) |

Nguồn phiên người cho chiến thuật 3–4 (`--human-source`):
- `api` (mặc định): phiên `meta.role = genuine` lấy qua `/v1/export` — **dùng khi đã thu dữ liệu thật**.
- `synth`: phiên người giả do tool tự sinh — chỉ để thử khi chưa có dữ liệu.
- `file:<đường dẫn.jsonl>`: mỗi dòng một phiên định dạng `SessionIn`.

## Lệnh

### Sinh dữ liệu "máy" cho Người 1

```powershell
uv run python -m nhip_attacker generate --api https://nhip-api-taupe.vercel.app --user acc_p01 --n 50
```

Gửi phiên với `meta = {participant_id: "sim", role: "bot", tactic: 1..4}`. Người 1 lấy qua `GET /v1/export` (lọc `meta.role == "bot"`). Phiên chỉ được lưu, không chấm điểm, nên không ảnh hưởng mẫu chuẩn.

### Đo tỷ lệ bắt theo chiến thuật (số liệu slide)

```powershell
uv run python -m nhip_attacker report --api https://nhip-api-taupe.vercel.app --enroll-synth --n 40
```

- `--enroll-synth`: tự tạo tài khoản mục tiêu `sim_target_*` đã đăng ký 3 lượt. Chiến thuật 3 phát lại một phiên khác của chính chủ tài khoản đó.
- `--target <user_id>`: dùng tài khoản đã đăng ký thật. **Cẩn thận**: phiên bot được chấm `allow` với điểm khớp cao sẽ cập nhật mẫu chuẩn của tài khoản đó — đừng chạy lên tài khoản của người tham gia thật.
- `--new-recipient`: chấm như chuyển cho người nhận mới.

### Tấn công thật qua adb (demo "bảng điều khiển hacker")

Cần: Android platform-tools (`adb` trong PATH), điện thoại bật **USB debugging**, ví demo đang mở ở màn hình nhập PIN.

1. Lấy toạ độ phím: trên điện thoại bật Tuỳ chọn nhà phát triển → **Vị trí con trỏ (Pointer location)**, chạm vào từng phím PIN, ghi lại X/Y ở thanh trên cùng (pixel thiết bị).
2. Ghi vào `layout.json`:

   ```json
   {"1": [180, 1450], "2": [540, 1450], "3": [900, 1450],
    "4": [180, 1650], "5": [540, 1650], "6": [900, 1650],
    "7": [180, 1850], "8": [540, 1850], "9": [900, 1850], "0": [540, 2050]}
   ```

3. Thử in lệnh trước, rồi chạy thật:

```powershell
uv run python -m nhip_attacker adb --layout layout.json --pin 1593 --tactic 1 --dry-run
```

```powershell
uv run python -m nhip_attacker adb --layout layout.json --pin 1593 --tactic 2 --swipe 540 1800 540 900
```

Chỉ hỗ trợ chiến thuật 1–2 (adb bấm đúng toạ độ). Mỗi lệnh adb mất ~50–300 ms nên nhịp không đều tuyệt đối — đó chính là "mã độc thật" để demo. Hướng mở rộng: app Android dùng `AccessibilityService.dispatchGesture` (đúng cơ chế mã độc).

## Kết quả đo (23/11, baseline luật của backend, dữ liệu người GIẢ)

`report --enroll-synth --human-source synth`, 40 phiên/chiến thuật, 3 seed, API local; chạy lại 20 phiên trên bản online cho kết quả tương tự:

| Chiến thuật | Bị gắn cờ (step_up + hold) | Ghi chú |
|---|---|---|
| 1 | 100% (toàn bộ `hold`) | Nhịp đều + đúng tâm |
| 2 | 100% (toàn bộ `hold`) | Đúng tâm nút vẫn lộ |
| 3 | 0% | Phát lại phiên của chính chủ: qua cả kiểm tra người/máy lẫn chủ tài khoản |
| 4 | 5–30% | Lấy mẫu từ phân bố người: qua kiểm tra người/máy; kiểm tra chủ tài khoản quá dễ dãi |

**Không đưa lên slide** — người là dữ liệu giả. Đo lại khi có dữ liệu thật và mô hình của Người 1.

Rút ra cho đội:
- Luật baseline chỉ chặn được 1–2, đúng như kế hoạch dự đoán. Mô hình 1 của Người 1 (học trên phiên bot sinh bằng `generate`) là thứ phải nâng 3–4.
- Chiến thuật 4 cho thấy ánh xạ điểm khớp chủ (`owner.py`, d = 2 → 0,5) đang quá dễ dãi: lấy mẫu từ người khác vẫn được coi là chủ. Cần hiệu chỉnh trên dữ liệu thật (mục 5.5).
- Chiến thuật 3: phát lại gần như y hệt một phiên cũ là dấu hiệu mạnh — người thật không bao giờ lặp lại nhịp trong ±5%. Có thể thêm kiểm tra "trùng phiên cũ" ở backend.

## Kiểm thử

```powershell
uv run pytest -q
```

7 bài: tính chất từng chiến thuật (đúng tâm / nhiễu / bám phiên gốc / nằm trong phân bố người), lỗi khi thiếu dữ liệu người, lệnh adb ở chế độ `--dry-run`.
