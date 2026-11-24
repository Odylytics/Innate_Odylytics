# Innate

**Innate** (bẩm sinh): *PIN có thể bị đánh cắp, thói quen chạm bẩm sinh thì rất khó.* Chấm điểm hành vi chạm để trả lời hai câu hỏi — thao tác này do *bot* hay người, và người đó có phải *chủ* tài khoản không.

**Lớp kiểm chứng con người** (human verification layer) chạy ngầm ở bước xác nhận giao dịch: AI so khớp thao tác chạm/gõ với thói quen đã đăng ký và với hình mẫu người thật. Định vị: [`docs/plan/positioning.md`](docs/plan/positioning.md). Dự thi MoMo Tech Contest 2026. Đang trong giai đoạn phát triển; bản README nộp bài sẽ thay file này.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `backend/` | API FastAPI + ví demo/SDK (`app/static/wallet.html`, phục vụ ở `/`) |
| `attacker/` | Bộ giả lập hacker (4 chiến thuật, `adb`) |
| `docs/contest/` | Thể lệ và [danh sách output phải nộp](docs/contest/submission-checklist.md) |
| `docs/plan/` | **[Định vị: Innate là lớp gì](docs/plan/positioning.md)**, [cách hoạt động](docs/plan/how-it-works.md), kế hoạch dự án và [mô tả + kiểm chứng bằng paper](docs/plan/mo-ta-du-an-va-kiem-chung.md) |
| `docs/research/` | [Kế hoạch nghiên cứu](docs/research/research-plan.md), [ghi chú công nghệ](docs/research/tech-notes.md), tổng hợp và ghi chú paper |
| `research/` | Thí nghiệm AI chạy cục bộ ([README](research/README.md)); dữ liệu ở `research/data/` không commit |
| `papers/` | PDF paper, chia theo nhóm (không đưa vào bản nộp) |

## Chạy nhanh

```bash
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000
# mở http://localhost:8000  (ví demo, PIN 159357) và /docs (Swagger, key demo-key)
uv run pytest -q
```

Chi tiết: [`backend/README.md`](backend/README.md), [`attacker/README.md`](attacker/README.md).
