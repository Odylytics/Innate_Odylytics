# Innate — Lớp chấm điểm rủi ro hành vi chạm cho ví điện tử

> **KHUNG README NỘP BÀI — chưa hoàn chỉnh (mục giấy phép và tài sản có sẵn đã kiểm 25/11).** Mục có `TODO` cần đội điền/quyết trước 03/12. Khi nộp, đổi tên file này thành `README.md` ở gốc gói `.zip` và xoá dòng này. Danh sách kiểm: [`../contest/submission-checklist.md`](../contest/submission-checklist.md).

**Đội:** `TODO: tên đội` · **Thành viên:** `TODO` · **Chủ đề:** An ninh mạng + Chống lừa đảo · **MoMo Tech Contest 2026**

## 1. Sản phẩm là gì

Innate (bẩm sinh) là **lớp kiểm chứng con người** chạy ngầm ở bước xác nhận giao dịch, bổ sung cho PIN/OTP/khuôn mặt (không thay thế). Nó chấm điểm rủi ro của giao dịch dựa trên **cách người dùng chạm và gõ** khi nhập PIN và các ô giao dịch, để trả lời hai câu hỏi: thao tác do **người hay máy** làm (mã độc Trợ năng, `adb`, script), và nếu là người thì có **khớp thói quen chủ tài khoản** không. Kết quả: `allow` / `step_up` (xác thực thêm) / `hold` (giữ lệnh), kèm lý do tiếng Việt. Khi chưa chắc, **Innate Challenge** yêu cầu gõ lại một câu tiếng Việt ngẫu nhiên (máy chủ cấp, ký token) để có thêm tín hiệu: nhịp gõ và kiểu gõ dấu Telex/VNI. Phần kiểu gõ tiếng Việt mới là giả thuyết, chưa đo trên người thật (`../plan/innate-challenge-vi.md`). Hệ thống chỉ đề xuất, không tự khoá tài khoản. Giải thích đầy đủ: [`../plan/how-it-works.md`](../plan/how-it-works.md); định vị: [`../plan/positioning.md`](../plan/positioning.md).

**Giới hạn (nói thẳng):** điểm "chủ" là một tín hiệu rủi ro, **không phải cổng xác thực**. Số đo hiện có (dữ liệu người thật công khai): EER ~16%; ở FRR 5% còn 38–57% kẻ gian biết PIN lọt (57% khoảng cách cơ bản, 38% mô hình học); đổi tư thế gần như mất tín hiệu. Bot ngây thơ bị bắt 100%; bot giống người thì yếu (xem mục 6).

## 2. Dùng thử trực tuyến

| | |
|---|---|
| Trang demo (web) | `TODO: URL deploy của thư mục web/` (đội web chốt) |
| API | https://nhip-api-taupe.vercel.app (`/health` 200 ngày 25/11/2026) |
| Swagger | https://nhip-api-taupe.vercel.app/docs (bấm Authorize, nhập key SDK) |
| Tài khoản / API key demo | `TODO`: key SDK của bản deploy (đã nằm trong bản build web, xem `web/README.md`); web demo không cần đăng nhập |
| PIN demo | `159357` (web demo, 6 số, theo `web/README.md`) |

Kịch bản 4 bước: (1) đăng ký nhịp 3–5 lần; (2) chuyển tiền bằng chính chủ; (3) người thứ hai biết PIN thử → bị yêu cầu xác thực thêm; (4) bảng điều khiển bot → bị giữ lệnh. Sản phẩm phải online đến hết 11/12/2026: `TODO: xác nhận URL web cuối và theo dõi Vercel đến hết ngày đó`.

## 3. Cách chạy local

```bash
cd backend
uv sync --extra ml          # hoặc: pip install fastapi uvicorn sqlalchemy "psycopg[binary]" lightgbm numpy
uv run uvicorn app.main:app --reload --port 8000     # /docs = Swagger, key mặc định demo-key
uv run pytest -q            # 40 bài
cd ../attacker && uv sync && uv run pytest -q         # 8 bài
cd .. && node --test sdk/innate-compose.test.js        # 4 bài (SDK nhập liệu điện thoại)
cd web && npm install && npm test && npm run dev       # trang web demo (Vite)
```

Biến môi trường: `DATABASE_URL`, `NHIP_API_KEYS` (SDK), `NHIP_OPS_KEYS` (dashboard), `NHIP_ML_KEYS` (xuất dữ liệu cho ML; ops/ml đóng khi chưa đặt), `NHIP_CORS_ORIGINS`, `NHIP_THRESHOLD_A/B`, `NHIP_HUMAN_MODEL=off` / `NHIP_OWNER_MODEL=off` (tắt mô hình học người/máy, nhận chủ), `NHIP_POP_PRIOR=off` (tắt prior dân số), `NHIP_REPLAY_THRESHOLD`. Tên `NHIP_*` là định danh kỹ thuật cũ, giữ để không làm hỏng bản đã deploy.

## 4. Công nghệ

Python 3.11+, FastAPI, SQLAlchemy (SQLite khi chạy local, Postgres khi deploy), LightGBM (mô hình người/máy, tuỳ chọn), web demo React 18 + TypeScript + Vite trong `web/` (có SDK thu sự kiện chạm), SDK nhập liệu cho điện thoại `sdk/innate-compose.js`. Hạ tầng: Vercel (API và web, hai project) + Neon Postgres (theo `CLAUDE.md`; `TODO: xác nhận`).

Các lớp AI (không có LLM trên đường ra quyết định): đặc trưng thời gian/toạ độ → (A) người hay máy: luật + LightGBM + kiểm tra phát lại → (B) có phải chủ: so với mẫu chuẩn bằng khoảng cách chuẩn hoá (co rút phương sai về dân số cho đặc trưng thời gian) rồi **LightGBM học trọng số** trên độ lệch → (C) hợp nhất có trọng số + giải thích bằng mẫu câu.

## 5. Tài sản có sẵn, thư viện mã nguồn mở, công cụ AI, dữ liệu — KHAI ĐẦY ĐỦ (giấu = bị loại)

### Thư viện mã nguồn mở
| Thư viện | Dùng cho |
|---|---|
| FastAPI, Uvicorn, SQLAlchemy, psycopg | Backend API và lưu trữ |
| LightGBM, NumPy | Mô hình người/máy (tuỳ chọn) |
| scikit-learn, pandas, NumPy, LightGBM | Chỉ trong `research/` (thí nghiệm, không chạy trong sản phẩm) |
| React, React DOM, Vite, TypeScript (Apache-2.0), Vitest, Lenis (MIT); DiceBear (MIT) để dựng sẵn ảnh đại diện | Trang web demo trong `web/`. Ảnh đại diện "Notionists" của Zoish theo **CC0 1.0** (kiểm 25/11 trên trang DiceBear) |
| psycopg (**LGPL-3.0**) | Kết nối Postgres, dùng nguyên bản như thư viện phụ thuộc, không sao chép vào mã |
| pytest, httpx | Kiểm thử |

### Dữ liệu và giấy phép
| Nguồn | Dùng cho | Giấy phép / điều kiện | Ghi chú |
|---|---|---|---|
| **StrokePIN** (Yao & Wang, IEEE TDSC 2026; DOI 10.21227/thft-4721; chủ sở hữu: Đại học Nam Khai) | Đánh giá bài "chủ"; huấn luyện mô hình người/máy; sinh `population_prior.json` | **CC BY-NC-SA 4.0**: phi thương mại, ghi nguồn, **chia sẻ phái sinh cùng giấy phép** | **Mô hình trong `backend/app/models/` và `population_prior.json` là sản phẩm phái sinh: phát hành theo CC BY-NC-SA 4.0.** Đội chốt (25/11): **toàn bộ gói theo CC BY-NC-SA 4.0** (`LICENSE`); thư viện bên thứ ba giữ giấy phép riêng (`THIRD_PARTY_NOTICES.md`). Dùng thương mại cần chủ sở hữu StrokePIN cho phép bằng văn bản |
| CMU DSL-StrongPassword (Killourhy & Maxion 2009) | Thí nghiệm few-shot (`research/`) | Kiểm 25/11: trang gốc không nêu giấy phép, yêu cầu trích dẫn bài DSN-2009 | Không có trong sản phẩm |
| Touchalytics (Frank et al. 2013) | Chỉ trong `research/` (E19: kiểm luật vuốt và nhận chủ bằng vuốt); ngưỡng vận tốc vuốt 0,3 chọn khi quan sát dữ liệu này. Không có dữ liệu hay mô hình phái sinh trong sản phẩm | Kiểm 25/11: trang gốc và `readme_data.txt` **không nêu giấy phép**; dữ liệu đưa tải công khai kèm bài báo | Trích dẫn Frank et al., IEEE TIFS 8(1), 2013 |
| Aalto typing37k (Palin et al. 2019) | Chỉ trong `research/` (E11, E12, E13, E21, E22: nhịp gõ người thật). Không có dữ liệu hay mô hình phái sinh trong sản phẩm | Kiểm 25/11: trang và bài báo nói "openly available" nhưng **không nêu giấy phép dữ liệu** (chỉ phần mềm thu dữ liệu là MIT) | Dữ liệu chứa nội dung gõ: **không đưa vào gói**; `research/data/` bị loại; chỉ công bố bảng tổng hợp. Trích dẫn MobileHCI 2019 |
| Dữ liệu tự thu của đội | `TODO` | Phiếu đồng ý của người tham gia; chỉ lưu thời gian, toạ độ, loại sự kiện, **không lưu nội dung** | `TODO: số người, số phiên, ngày thu` |

Bot trong `attacker/` là **dữ liệu tự sinh** (4 chiến thuật), không phải mã độc thật.

### Tài sản có sẵn khác (đã khai ở `web/README.md`)
| Tài sản | Nguồn | Ghi chú |
|---|---|---|
| Hệ thiết kế và khung giao diện web | **Movago**, trang demo web trước đây của một thành viên (team Odylytics), dùng lại: `styles.css`, `ui.tsx`, `smooth.ts`, `sound.ts`, `Intro.tsx`, `StoryBar.tsx`... | Nội dung Innate, ví, SDK, client API, các trang và hình vẽ là mới |
| Tham chiếu bố cục | Mẫu Movora (Framer Marketplace) qua `DESIGN.md` của Movago | Chỉ lưới, khoảng cách, hình khối; không dùng ảnh, logo, chữ của Movora |
| Phông chữ | Sora, Manrope, JetBrains Mono (SIL OFL, Google Fonts) | Sora không có glyph tiếng Việt: tiêu đề tiếng Việt dùng Manrope |

Danh sách đầy đủ kèm cách kiểm: `THIRD_PARTY_NOTICES.md`.

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
| Xác minh chủ (StrokePIN, 97 người, kẻ gian biết PIN, 3 lần đăng ký, chia theo người, **không dùng kích thước chạm**) | Khoảng cách cơ bản: EER 0,161, kẻ gian lọt 0,573 ở FRR 5%. **Học máy: EER 0,158, kẻ gian lọt 0,375** (−0,198, CI không chứa 0). Đổi tư thế (ngồi→đi): EER 0,309, kẻ gian lọt 0,708 | Khoảng tin cậy ghép cặp, bootstrap theo người. Bản có kích thước chạm cho số đẹp hơn nhưng là nhiễu **thiết bị** (kẻ gian trong dữ liệu dùng máy khác), nên không dùng |
| Người/máy (người thật, bot sinh) | Bot ngây thơ (CT1, CT2): 100%; CT3 (phát lại): 12–26%; CT4 (lấy mẫu dân số): 20–73% | Bot **do bộ sinh tạo**, chưa có bot thật |
| Kiểm tra phát lại (người thật, ngưỡng 0,07) | Bắt 100% phát lại có nhiễu tới ±10%; 29% ở ±15%; 0% từ ±20% | FPR người thật ~0,1% (8 phiên cũ), ngoại suy ~0,7% (50 phiên). Hiệu chỉnh lại trên dữ liệu của đội |
| **Innate Challenge** (2.260 người gõ câu, chỉ thời gian) | Kẻ gian lọt ở FRR 5%: 81% (6 phím) → 49% (30 phím); bắt bot gõ đều AUC 0,92 → 0,996 | Chép câu mẫu tiếng Anh; chưa đo gộp PIN + câu, chưa đo ma sát |
| Luật vuốt (Touchalytics, 41 người, 20.896 nét) | Luật "vận tốc đều" (CV < 0,3): 0 nét người thật bị gắn cờ, bắt 100% bot vuốt đều/nhiễu thời gian ±6 ms. Luật cũ "thẳng > 0.999" gắn cờ nhầm 13,4% phiên người thật (đã thay). Nhận chủ bằng vuốt: AUC 0,48–0,60 (đã bỏ khỏi nhận chủ) | Bot là bộ sinh của đội; bot thật có thể giả vận tốc |
| Innate Challenge tiếng Việt | **Chưa đo trên người Việt.** Có số mô phỏng và đếm lý thuyết (3–6,6 bit biến thể gõ Telex/VNI) | `../plan/innate-challenge-vi.md`; cần thu dữ liệu và thử Gboard/iOS thật |
| Chuẩn hoá nhịp theo cặp phím (Aalto, 1.000 người) | Gần như không đổi (EER 0,249 → 0,238 ở 30 phím); không đưa vào sản phẩm | Kết quả âm tính, ghi để minh bạch |
| Số liệu trên dữ liệu của đội | `TODO` | |

Chi tiết, giả thuyết, giới hạn và cách chạy lại: [`../research/ai-research.md`](../research/ai-research.md), thư mục `research/`.

## 7. Cấu trúc gói nộp

```
backend/    API, SDK, mô hình, test           attacker/   bộ giả lập bot (4 chiến thuật, adb)
research/   mã thí nghiệm + kết quả            docs/       kế hoạch, giải thích, nghiên cứu
```
**Hồ sơ nộp (không nằm trong zip mã nguồn nếu BTC tách riêng):** `docs/submission/` gồm slide PDF, đề xuất, kịch bản video/thuyết trình, bản nháp hướng dẫn 1 trang.

**Không đưa vào gói:** `papers/` (PDF có bản quyền), `research/data/` và `research/external/` (dữ liệu và mã bên thứ ba), `.env*`, `backend/.env.deploy-key`, `*.db`, `.venv`, `__pycache__`.

## 8. Quyền riêng tư và pháp lý

Chỉ lưu thời gian, toạ độ, loại sự kiện và số ký tự; **không lưu nội dung PIN, số tiền, nội dung chuyển khoản**. Dữ liệu chạm/gõ coi là dữ liệu nhạy cảm (Luật Bảo vệ dữ liệu cá nhân 2025 và NĐ 356/2025, hiệu lực 01/01/2026): người tham gia thu dữ liệu đã đồng ý bằng phiếu (mẫu phiếu: `docs/plan/thu-du-lieu-doi.md` (mục "Phiếu đồng ý"), đính kèm vào zip). Không dùng logo hay tên thương hiệu của bên thứ ba; giao diện demo là minh hoạ.
