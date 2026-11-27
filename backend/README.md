# Innate — Backend API

API chấm điểm rủi ro hành vi (Người 2). FastAPI + SQLAlchemy, SQLite khi chạy local, Postgres (Neon) khi deploy.

## Bản đang chạy

| | |
|---|---|
| URL | https://nhip-api-taupe.vercel.app |
| Swagger | https://nhip-api-taupe.vercel.app/docs → **Authorize** → nhập API key |
| API key | 3 key theo vai trò (SDK / ops / ML), lưu ở `backend/.env.deploy-key` trên máy Người 2 (không commit). Hỏi Người 2 khi cần |
| Hạ tầng | Vercel project `nhip-api`, vùng Singapore (`sin1`); DB Neon `nhip-db` (gói free, Singapore), gắn qua Vercel Marketplace |
| Độ trễ đo 23/11 | Xử lý phía server 16–21 ms/lần chấm; khứ hồi từ Việt Nam ~125–150 ms |

Deploy lại: `cd backend; vercel deploy --prod`. Xem trạng thái: `/vercel:status` trong Claude Code, hoặc `vercel ls nhip-api`.

## Chạy

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

- Swagger: http://localhost:8000/docs (`/` cũng chuyển về đây) → bấm **Authorize**, nhập `demo-key` (key SDK). Muốn thử dashboard/export ở local thì đặt thêm `NHIP_OPS_KEYS` / `NHIP_ML_KEYS`.
- Kiểm thử: `uv run pytest -q` (7 bài, ~2 giây). SQLite trong test bật kiểm tra khoá ngoại để giống Postgres.

### Biến môi trường

| Biến | Mặc định | Ghi chú |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./nhip.db` | Trên Vercel do Neon tự đặt; `postgres://` được tự đổi sang driver psycopg |
| `NHIP_API_KEYS` | `demo-key` *(chỉ khi DB là SQLite local; nối DB thật mà không đặt thì đóng hết)* | Key **SDK** (nằm trong app web): gửi phiên, đăng ký nhịp, chấm điểm. Nhiều key cách nhau dấu phẩy |
| `NHIP_OPS_KEYS` | *(trống = đóng)* | Key **dashboard**: xem danh sách phiên, gắn nhãn |
| `NHIP_ML_KEYS` | *(trống = đóng)* | Key **Người 1**: `/v1/export` |
| `NHIP_CORS_ORIGINS` | `*` | Bản deploy đang để `*`. **Đặt đúng domain ví demo + dashboard khi Người 3 deploy frontend** |
| `NHIP_THRESHOLD_A` | `0.25` | rủi ro < A → `allow` |
| `NHIP_THRESHOLD_B` | `0.55` | rủi ro > B → `hold`; giữa A và B → `step_up` |

Mọi phản hồi có header `X-Process-Time-Ms` (độ trễ xử lý, dùng cho số liệu slide). Đo local: ~6 ms/lần chấm điểm.

## Endpoint

Tất cả `/v1/*` cần header `X-API-Key` đúng vai trò ở cột *Quyền*. Sai key → 401; key hợp lệ nhưng sai vai trò → 403. Key SDK nằm trong app web nên **không** mở được dashboard hay export.

| Method | Đường dẫn | Quyền | Việc |
|---|---|---|---|
| GET | `/health` | deploy | Kiểm tra sống |
| POST | `/v1/sessions` | App | Gửi phiên thao tác → `{session_id, n_features}` |
| POST | `/v1/users/{user_id}/enroll` | SDK | Body `{session_id}`. Đánh dấu lượt đăng ký; đủ 3 lượt thì có mẫu chuẩn và **khoá đăng ký** (thêm lượt → 409) |
| GET | `/v1/users/{user_id}` | App | Số lượt đã đăng ký, mẫu chuẩn sẵn sàng chưa, số lần cập nhật |
| POST | `/v1/sessions/{id}/score` | App | Body `{recipient_is_new, amount}` → điểm + hành động + lý do |
| GET | `/v1/export?participant_id=&limit=500&offset=0` | ML | Xuất phiên có `meta` (dữ liệu thô + đặc trưng + nhãn thu dữ liệu), cũ nhất trước, **theo trang**: mỗi trang tối đa `limit` (≤ 2000) phiên và ~3 MB; còn dữ liệu thì header `X-Next-Offset` cho offset trang sau |
| GET | `/v1/sessions?flagged=true&limit=50` | ops | Phiên `step_up`/`hold` mới nhất (bỏ `flagged` = tất cả phiên đã chấm) |
| POST | `/v1/sessions/{id}/label` | ops | Body `{label: "fraud" \| "legit"}` |

### Luồng của app (Người 3)

```
Đăng ký nhịp (3–5 lần):  POST /v1/sessions  →  POST /v1/users/{uid}/enroll
Chuyển tiền:             POST /v1/sessions  →  POST /v1/sessions/{sid}/score  →  hiện action + explanation_vi
```

### Phiên SDK gửi lên (hợp đồng dữ liệu)

Chỉ thời gian (ms, tính từ lúc vào màn hình) và toạ độ (px), **không có nội dung PIN** ngoài nhãn phím để biết tâm phím. Ví dụ đầy đủ có sẵn trong Swagger.

```json
{
  "user_id": "demo_user",            // chữ, số, _ . -  (≤ 64 ký tự)
  "device_id": "demo_phone",
  "pin_taps": [                       // ≤ 12; lấy từ Pointer Events trên bàn phím PIN tự vẽ
    {"key": "1", "t_down": 0, "t_up": 95, "x": 66, "y": 395, "w": 40, "h": 40,
     "key_cx": 60, "key_cy": 400, "key_w": 100, "key_h": 70}
  ],
  "swipes": [ {"points": [{"t": 0, "x": 200, "y": 600}, {"t": 40, "x": 230, "y": 470}]} ],
  "screens": [ {"name": "transfer", "t_enter": 0, "t_first_touch": 1200} ]
}
```

- `w`, `h` = `PointerEvent.width/height`; `key_cx/cy/w/h` = tâm và kích thước phím (`getBoundingClientRect`).
- Không gửi `pressure`. Không dựa vào `isTrusted`.
- Giới hạn: ≤ 30 lần vuốt mỗi phiên, ≤ 200 điểm mỗi lần vuốt (~3 giây ở 60 Hz); dài hơn thì SDK cắt bớt.
- **Khi thu dữ liệu** thêm `"meta": {"participant_id": "p07", "sitting": 1, "role": "genuine", "note": "..."}`. `sitting` = lần thu thứ mấy (1 đăng ký, 2+ kiểm thử); `role` = `genuine`, `impostor` (biết PIN, cố bấm giống chủ) hoặc `bot` (kèm `tactic` 1–4, do [bộ giả lập](../attacker/README.md) gửi). Lượt đóng giả: `user_id` là tài khoản của chủ, `participant_id` là người đang bấm.
- Server từ chối (422): `t_up < t_down`, số NaN/âm, `user_id` có ký tự lạ, quá nhiều sự kiện.

**Ô nhập ngoài PIN (`fields`, tuỳ chọn):** số tiền, người nhận, ghi chú. Chỉ gửi **thời gian, loại sự kiện và số ký tự**, không gửi nội dung.

```json
"fields": [
  {"name": "amount",    "events": [{"t": 4100, "kind": "key", "n": 1, "cls": "digit"}, {"t": 4290, "kind": "key", "n": 1, "cls": "digit"}]},
  {"name": "recipient", "events": [{"t": 2200, "kind": "paste", "n": 10}]},
  {"name": "note",      "events": [{"t": 6100, "kind": "key", "n": 1, "cls": "letter"}, {"t": 6350, "kind": "delete", "n": 1}]}
]
```

- `name`: `amount | recipient | note | name`. `kind`: `key` (gõ ký tự), `paste` (dán), `delete`, `set_text` (văn bản đổi mà **không có sự kiện phím**, vd. Trợ năng `ACTION_SET_TEXT`; chỉ SDK native phát hiện được).
- Web SDK cũ (`wallet.html`, đã bỏ) chỉ phát `key`, `paste`, `delete` từ sự kiện `input`; không phát `set_text`.
- Luật baseline: `set_text` ở ô **số tiền** bị coi là máy (`text_set_without_keys`, giữ lệnh); ở ô khác chỉ trừ điểm nhẹ vì autofill/danh bạ cũng có thể đặt văn bản không qua phím. Ngưỡng **chưa kiểm chứng trên máy thật** (R9).
- Nhịp gõ trong ô (≥ 4 phím) thành đặc trưng nhận dạng chủ `fld_<ô>_gap_mean/std`; muốn có trong mẫu chuẩn thì lượt đăng ký phải gõ cả các ô đó.

### Phản hồi chấm điểm

```json
{
  "session_id": "s_8f21a0c3d4e5",
  "human_score": 0.97,
  "owner_match": 0.12,
  "risk": "medium",
  "risk_score": 0.47,
  "action": "step_up",
  "reasons": ["pin_rhythm_slower_40pct", "tap_offset_left", "new_recipient"],
  "explanation_vi": "Thao tác giống người thật nhưng không khớp thói quen của chủ tài khoản (nhịp PIN chậm hơn 40%, chạm lệch trái). Giao dịch: người nhận mới. Đề nghị xác thực khuôn mặt trước khi chuyển."
}
```

`owner_match = null` khi người dùng chưa đăng ký đủ 3 lượt (lý do `not_enrolled`). Đã đăng ký mà phiên thiếu nhịp PIN (không bấm PIN, hoặc PIN ngắn hơn lúc đăng ký) → `owner_match = 0`, lý do `missing_pin_evidence`, không bao giờ `allow`.

## Lớp chấm điểm (`app/scoring/`) — Người 1 thay từng file, giữ chữ ký hàm

| File | Hàm | Bản baseline hiện tại |
|---|---|---|
| `features.py` | `extract(raw) -> dict` | Giữ phím, khoảng cách phím, tổng thời gian, lệch tâm (dx, dy theo kích thước phím), kích thước chạm; vuốt: thời gian, độ dài, độ thẳng, vận tốc TB/đỉnh; thời gian tới chạm đầu |
| `owner.py` | `build_template`, `score`, `update` | Scaled Manhattan (Killourhy & Maxion 2009) có sàn độ lệch chuẩn. Ánh xạ khoảng cách → [0,1] **chưa hiệu chỉnh** (d = 2 → 0,5) |
| `human.py` | `score(features) -> (human_score, reasons)` | Luật: nhịp quá đều (CV < 0,08), chạm đúng tâm (< 0,06 bề rộng phím), vuốt thẳng tuyệt đối (tín hiệu yếu, tối đa trừ 0,5) |
| `fusion.py` | `fuse`, `amount_anomaly` | `0,40·(1−người) + 0,35·(1−chủ) + 0,15·người_nhận_mới + 0,10·số_tiền_bất_thường`; `human < 0,3` → luôn `hold` |
| `explain.py` | `explain(...)` | Nhóm đặc trưng lệch ≥ 1,5 sd → tối đa 3 lý do + câu tiếng Việt theo mẫu. Không dùng LLM |

**Cập nhật mẫu chuẩn** (mục 5.2 kế hoạch): chỉ sau phiên đầu tiên được chấm là `allow`, không phải lượt đăng ký, `owner_match ≥ 0,8` và `human_score ≥ 0,8`. Trung bình trượt α = 0,1, và mẫu không được trôi quá 1 sd so với lúc đăng ký. Chưa làm: kiểm tra hướng trôi.

## Kiểm thử đã chạy

`tests/test_api.py` (dữ liệu giả từ `tests/synth.py`):

- Không có/sai API key → 401 (kể cả header ngoài ASCII); key sai vai trò → 403; dữ liệu sai → 422; đăng ký phiên của người khác → 400; đăng ký thêm khi đã có mẫu chuẩn → 409.
- Phiên chỉ có vuốt hoặc PIN thiếu phím cho tài khoản đã đăng ký → không `allow`, lý do `missing_pin_evidence`.
- Luồng đầy đủ: chưa đăng ký → `not_enrolled`; đăng ký 3 lượt → có mẫu chuẩn; chủ thật → `allow`; người khác biết PIN → `step_up` với lý do nhịp/vị trí; bot chiến thuật 1 → `hold` với `tap_exact_center`; số tiền gấp 50 lần → `amount_unusual`; mẫu chuẩn được cập nhật; dashboard thấy phiên bị gắn cờ; gắn nhãn được.
- Chặn trôi: 200 lần "dạy dần" bằng phiên lệch xa, mẫu chuẩn vẫn trong ±1 sd.

Chạy 200 seed với dữ liệu giả: chủ thật được cho qua 95%, người khác bị gắn cờ 100%, bot chiến thuật 1 bị giữ 100%. **Đây là dữ liệu tự sinh, không phải số liệu để lên slide** — số thật phải đo trên dữ liệu thu từ người theo mục 5.5.

## Giới hạn đã biết

- Ngưỡng và trọng số là giá trị khởi đầu, chưa fit trên dữ liệu thật.
- Luật người/máy bắt được chiến thuật 1–2; chiến thuật 3 (phát lại phiên người thật) và 4 sẽ qua — cần mô hình của Người 1.
- Key SDK nằm trong app web nên ai cũng xem được: người dùng app vẫn gửi được phiên và chấm điểm cho **bất kỳ** `user_id` nào, và có thể đăng ký nhịp trước cho tài khoản **chưa** đăng ký. Sản phẩm thật cần gắn `user_id` với phiên đăng nhập của ví (backend của đối tác gọi API bằng key bí mật).
- Chưa có luồng đặt lại mẫu chuẩn (đăng ký lại) — hiện phải xoá `users.template` trong DB.
- Mẫu chuẩn dùng chung mọi thiết bị của một người dùng (kế hoạch dùng một điện thoại demo).
- Chưa có: bộ giả lập hacker, tóm tắt LLM cho dashboard, migration DB (bảng được tạo tự động lúc khởi động).

## Việc tiếp theo của Người 2

1. ~~Bộ giả lập hacker~~ — xong 23/11, xem [attacker/README.md](../attacker/README.md).
2. ~~Deploy~~ — xong 23/11. Còn: đặt `NHIP_CORS_ORIGINS` khi có domain frontend.
3. Tài khoản demo cho giám khảo.
