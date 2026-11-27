# Bản đồ tài liệu và mã (đọc file này trước)

> Cập nhật 27/11/2026. Thư mục gốc của dự án: `Innate_Odylytics/` (repo `Odylytics/Innate_Odylytics`; trước đây `momo_contest-main/`). Ngôn ngữ tài liệu: tiếng Việt; `README.md` gốc là cổng vào bằng tiếng Anh.

## Muốn biết... thì đọc...
| Câu hỏi | Đọc |
|---|---|
| Innate là gì, nằm ở đâu trong chồng bảo mật | [`plan/positioning.md`](plan/positioning.md), [`plan/how-it-works.md`](plan/how-it-works.md) |
| Số đo hiện tại, giới hạn | [`research/ai-research.md`](research/ai-research.md) (mục 6b: mọi thí nghiệm), bảng chỉ mục [`../research/EXPERIMENTS.md`](../research/EXPERIMENTS.md) |
| Báo cáo tổng hợp: flow hệ thống, flow thu dữ liệu, mọi số liệu thực nghiệm, hạn chế | [`research/bao-cao-tong-hop.md`](research/bao-cao-tong-hop.md) |
| Sơ đồ luồng và cách từng mô hình chạy (mở bằng trình duyệt) | [`research/so-do-luong.html`](research/so-do-luong.html) |
| Nộp bài thiếu gì, hạn, thể lệ | [`contest/submission-checklist.md`](contest/submission-checklist.md), [`contest/the-le-cuoc-thi.md`](contest/the-le-cuoc-thi.md), [`contest/dang-ky-va-cau-hoi-btc.md`](contest/dang-ky-va-cau-hoi-btc.md) |
| Giấy phép, tài sản có sẵn, dữ liệu | [`../LICENSE`](../LICENSE), [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md), [`research/datasets.md`](research/datasets.md) |
| Thu dữ liệu của đội ra sao | [`plan/thu-du-lieu-doi.md`](plan/thu-du-lieu-doi.md) (kế hoạch + phiếu đồng ý + lệnh phân tích) |
| Câu thử thách (Innate Challenge) | [`plan/innate-challenge.md`](plan/innate-challenge.md), tiếng Việt Telex/VNI: [`plan/innate-challenge-vi.md`](plan/innate-challenge-vi.md) |
| 4 kênh bằng chứng (chuyển động, PIN, câu, vuốt) | [`plan/bon-cong-pipeline.md`](plan/bon-cong-pipeline.md) |
| Bài báo liên quan, ta học được gì | [`research/related-work.md`](research/related-work.md), [`research/paper-report.md`](research/paper-report.md) |
| Web demo cho giám khảo | [`plan/web-demo.md`](plan/web-demo.md), [`research/transfer-flow.md`](research/transfer-flow.md), `../web/README.md` |
| Hồ sơ nộp (PDF 1 trang, slide PPTX + PDF, README, zip) | thư mục gốc `submission/` (sinh bằng `tools/build_submission.sh`); kịch bản video và thuyết trình: [`submission/`](submission/) trong `docs/` |
| Fine-tune TypeFormer | [`../research/finetune/README.md`](../research/finetune/README.md), kết quả [`../research/results/e32_typeformer_finetune.md`](../research/results/e32_typeformer_finetune.md) |

## Cây thư mục (đường dẫn tính từ gốc repo)
```
LICENSE, THIRD_PARTY_NOTICES.md   giấy phép (CC BY-NC-SA 4.0) và thành phần bên thứ ba
README.md                         cổng vào (English); CLAUDE.md = quy ước + khoảng trống đã biết
backend/                          API FastAPI + lõi chấm điểm
  app/main.py, schemas.py, db.py  API (/v1/...), schema dữ liệu, bảng
  app/scoring/                    lõi AI: features, human, human_model, owner, owner_model, replay, fusion, explain,
                                  challenge (câu + token dùng một lần), vi_ime (kiểu gõ tiếng Việt), bot_features
  app/models/                     mô hình LightGBM (TẠM: StrokePIN + bot sinh), CC BY-NC-SA
  tests/                          43 test (+ synth.py, synth_vi.py: dữ liệu giả)
attacker/                         bộ giả lập hacker 4 chiến thuật + tấn công adb thật (8 test)
sdk/                              SDK nhập liệu điện thoại (innate-compose.js), probe.html thử bàn phím, test Node
web/                              landing + web demo + trang thu dữ liệu (#/collect) + vận hành (#/ops) (React/Vite)
research/                         thí nghiệm
  experiments/                    mã (E1–E27, huấn luyện, phân tích dữ liệu đội, dry-run)
  results/                        bảng kết quả sinh ra (.md/.txt)
  models/                         mô hình dữ liệu giả, chỉ tham khảo
  finetune/                       E32: fine-tune TypeFormer lên StrokePIN (chỉ nghiên cứu, chưa vào API)
  data/, external/                dữ liệu và mã bên thứ ba: GIT-IGNORED, không nộp
tools/                            dựng hồ sơ nộp: build_submission.sh, build_pptx.js (slide sửa được), product-guide.html, assets, fonts
submission/                       hồ sơ nộp SINH RA (Product, Slide, Document); zip mã nguồn không đưa vào git
docs/                             tài liệu (xem bảng trên)
  contest/  plan/  research/  submission/  brand/  (research/notes/ = ghi chú đọc paper theo nhóm; brand/ = brand kit + asset-pack Innate)
papers/                           52 PDF bài báo (bản quyền nhà xuất bản: không nộp; danh mục ở docs/research/paper-report.md)
```
Dữ liệu tải về (git-ignored): `research/data/` (đã giải nén) và bản zip gốc ở `research/data/_archives/` (Touchalytics, Aalto).

## Quy ước
- Số hiệu thí nghiệm: E1–E14 như trong `ai-research.md` (E14 = chuỗi số mới, do đội web làm); E18–E28 bổ sung 25–26/11. **E15–E17 không dùng** (đổi thành E19–E21 để khỏi trùng E14).
- Mọi con số trong tài liệu do mã trong `research/experiments/` sinh ra; không có số nào chỉnh tay. Số trên dữ liệu giả chỉ để thử đường ống, không đưa lên slide.
- Dữ liệu người dùng: chỉ thời gian, toạ độ, loại sự kiện, số ký tự; không lưu nội dung PIN, số tiền, nội dung gõ.
