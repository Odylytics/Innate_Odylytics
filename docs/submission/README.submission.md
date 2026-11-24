# Innate — Lớp chấm điểm rủi ro hành vi chạm cho ví điện tử

> **KHUNG README NỘP BÀI — chưa hoàn chỉnh.** Mục có `TODO` cần đội điền/quyết trước 03/12. Khi nộp, đổi tên file này thành `README.md` ở gốc gói `.zip` và xoá dòng này. Danh sách kiểm: [`../contest/submission-checklist.md`](../contest/submission-checklist.md).

**Đội:** `TODO: tên đội` · **Thành viên:** `TODO` · **Chủ đề:** An ninh mạng + Chống lừa đảo · **MoMo Tech Contest 2026**

## 1. Sản phẩm là gì

Innate (bẩm sinh) là **lớp kiểm chứng con người** chạy ngầm ở bước xác nhận giao dịch, bổ sung cho PIN/OTP/khuôn mặt (không thay thế). Nó chấm điểm rủi ro của giao dịch dựa trên **cách người dùng chạm và gõ** khi nhập PIN và các ô giao dịch, để trả lời hai câu hỏi: thao tác do **người hay máy** làm (mã độc Trợ năng, `adb`, script), và nếu là người thì có **khớp thói quen chủ tài khoản** không. Kết quả: `allow` / `step_up` (xác thực thêm) / `hold` (giữ lệnh), kèm lý do tiếng Việt. Hệ thống chỉ đề xuất, không tự khoá tài khoản. Giải thích đầy đủ: [`../plan/how-it-works.md`](../plan/how-it-works.md); định vị: [`../plan/positioning.md`](../plan/positioning.md).

**Giới hạn (nói thẳng):** điểm "chủ" là một tín hiệu rủi ro, **không phải cổng xác thực**. Số đo hiện có (dữ liệu người thật công khai): EER 16–20%; ở FRR 5% còn ~50% kẻ gian biết PIN lọt; đổi tư thế gần như mất tín hiệu. Bot ngây thơ bị bắt 100%; bot giống người thì yếu (xem mục 6).

## 2. Dùng thử trực tuyến

| | |
|---|---|
| Trang demo | `TODO: URL` |
| API + Swagger | `TODO: URL/docs` |
| Tài khoản / API key demo | `TODO` |
| PIN demo | `159357` (ví demo) |

Kịch bản 4 bước: (1) đăng ký nhịp 3–5 lần; (2) chuyển tiền bằng chính chủ; (3) người thứ hai biết PIN thử → bị yêu cầu xác thực thêm; (4) bảng điều khiển bot → bị giữ lệnh. `TODO: xác nhận URL cuối; sản phẩm phải online đến hết 11/12/2026.`

## 3. Cách chạy local

```bash
cd backend
uv sync --extra ml          # hoặc: pip install fastapi uvicorn sqlalchemy "psycopg[binary]" lightgbm numpy
uv run uvicorn app.main:app --reload --port 8000     # /docs = Swagger, key mặc định demo-key
uv run pytest -q            # 18 bài
cd ../attacker && uv sync && uv run pytest -q         # 7 bài
```

Biến môi trường: `DATABASE_URL`, `NHIP_API_KEYS`, `NHIP_CORS_ORIGINS`, `NHIP_THRESHOLD_A/B`, `NHIP_HUMAN_MODEL=off` (tắt mô hình học), `NHIP_POP_PRIOR=off` (tắt prior dân số), `NHIP_REPLAY_THRESHOLD`. Tên `NHIP_*` là định danh kỹ thuật cũ, giữ để không làm hỏng bản đã deploy.

## 4. Công nghệ

Python 3.11+, FastAPI, SQLAlchemy (SQLite khi chạy local, Postgres khi deploy), LightGBM (mô hình người/máy, tuỳ chọn), SDK JavaScript thuần (Pointer Events) trong `backend/app/static/wallet.html`. Hạ tầng triển khai: `TODO: xác nhận (Vercel + Neon theo bản đã deploy)`.

Các lớp AI (không có LLM trên đường ra quyết định): đặc trưng thời gian/toạ độ → (A) người hay máy: luật + LightGBM + kiểm tra phát lại → (B) có phải chủ: so với mẫu chuẩn bằng khoảng cách chuẩn hoá, co rút phương sai về dân số cho đặc trưng thời gian → (C) hợp nhất có trọng số + giải thích bằng mẫu câu.

## 5. Tài sản có sẵn, thư viện mã nguồn mở, công cụ AI, dữ liệu — KHAI ĐẦY ĐỦ (giấu = bị loại)

### Thư viện mã nguồn mở
| Thư viện | Dùng cho |
|---|---|
| FastAPI, Uvicorn, SQLAlchemy, psycopg | Backend API và lưu trữ |
| LightGBM, NumPy | Mô hình người/máy (tuỳ chọn) |
| scikit-learn, pandas, NumPy, LightGBM | Chỉ trong `research/` (thí nghiệm, không chạy trong sản phẩm) |
| pytest, httpx | Kiểm thử |

### Dữ liệu và giấy phép
| Nguồn | Dùng cho | Giấy phép / điều kiện | Ghi chú |
|---|---|---|---|
| **StrokePIN** (Yao & Wang, IEEE TDSC 2026; DOI 10.21227/thft-4721) | Đánh giá bài "chủ"; huấn luyện mô hình người/máy; sinh `population_prior.json` | **CC BY-NC-SA 4.0**: phi thương mại, ghi nguồn, **chia sẻ phái sinh cùng giấy phép** | **Mô hình trong `backend/app/models/` và `population_prior.json` là sản phẩm phái sinh: phát hành theo CC BY-NC-SA 4.0.** `TODO: đội quyết định giấy phép cho phần mã còn lại và kiểm tra tương thích` |
| CMU DSL-StrongPassword (Killourhy & Maxion 2009) | Thí nghiệm few-shot (`research/`) | Trang gốc không nêu giấy phép | Không có trong sản phẩm |
| Touchalytics (Frank et al. 2013) | `TODO: nếu dùng cho đặc trưng vuốt` | `TODO: kiểm` | |
| Aalto typing37k (Palin et al. 2019) | `TODO: nếu dùng` | `TODO: kiểm` | Dữ liệu chứa nội dung gõ: không đưa vào sản phẩm |
| Dữ liệu tự thu của đội | `TODO` | Phiếu đồng ý của người tham gia; chỉ lưu thời gian, toạ độ, loại sự kiện, **không lưu nội dung** | `TODO: số người, số phiên, ngày thu` |

Bot trong `attacker/` là **dữ liệu tự sinh** (4 chiến thuật), không phải mã độc thật.

### Công cụ AI đã dùng
| Công cụ | Dùng cho |
|---|---|
| Claude Code (Anthropic; mô hình Claude Sonnet 5.5) | Hỗ trợ viết mã, thí nghiệm, tài liệu và rà soát paper. Mọi số liệu thí nghiệm do mã trong `research/` sinh ra và có thể chạy lại |
| `TODO: công cụ AI khác (nếu có) / mô hình mã nguồn mở khác` | |

### Bài báo tham khảo (không kèm trong gói; danh mục ở `docs/research/paper-report.md`)
Zheng 2014, Buschek 2015, Killourhy & Maxion 2009, Georgiev 2022 (FETA), Acien 2021 (BeCAPTCHA), Fratantonio 2017, Lovisotto 2020, Wang 2026 (ActReal), v.v.

## 6. Kết quả đo (dữ liệu người thật công khai; CHƯA phải dữ liệu của đội)

| Việc | Kết quả | Ghi chú |
|---|---|---|
| Xác minh chủ (StrokePIN, 97 người, kẻ gian biết PIN, 3 lượt đăng ký) | EER 0,146; FAR 0,495 ở FRR 5% | Co rút về dân số cho thời gian: FAR 0,663 → 0,495 (ghép cặp, CI không chứa 0). Đổi tư thế: EER ~0,35, không cải thiện |
| Người/máy (người thật, bot sinh) | Bot ngây thơ (CT1, CT2): 100%; CT3 (phát lại): 12–26%; CT4 (lấy mẫu dân số): 20–73% | Bot **do bộ sinh tạo**, chưa có bot thật |
| Kiểm tra phát lại (người thật, ngưỡng 0,07) | Bắt 100% phát lại có nhiễu tới ±10%; 29% ở ±15%; 0% từ ±20% | FPR người thật ~0,1% (8 phiên cũ), ngoại suy ~0,7% (50 phiên). Hiệu chỉnh lại trên dữ liệu của đội |
| Số liệu trên dữ liệu của đội | `TODO` | |

Chi tiết, giả thuyết, giới hạn và cách chạy lại: [`../research/ai-research.md`](../research/ai-research.md), thư mục `research/`.

## 7. Cấu trúc gói nộp

```
backend/    API, SDK, mô hình, test           attacker/   bộ giả lập bot (4 chiến thuật, adb)
research/   mã thí nghiệm + kết quả            docs/       kế hoạch, giải thích, nghiên cứu
```
**Không đưa vào gói:** `papers/` (PDF có bản quyền), `research/data/` và `research/external/` (dữ liệu và mã bên thứ ba), `.env*`, `backend/.env.deploy-key`, `*.db`, `.venv`, `__pycache__`.

## 8. Quyền riêng tư và pháp lý

Chỉ lưu thời gian, toạ độ, loại sự kiện và số ký tự; **không lưu nội dung PIN, số tiền, nội dung chuyển khoản**. Dữ liệu chạm/gõ coi là dữ liệu nhạy cảm (Luật Bảo vệ dữ liệu cá nhân 2025 và NĐ 356/2025, hiệu lực 01/01/2026): người tham gia thu dữ liệu đã đồng ý bằng phiếu (`TODO: đính kèm mẫu phiếu`). Không dùng logo hay tên thương hiệu của bên thứ ba; giao diện demo là minh hoạ.
