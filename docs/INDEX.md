# Bản đồ tài liệu và mã (đọc file này trước)

> Cập nhật 25/11/2026. Thư mục gốc của dự án: `momo_contest-main/` (repo `Odylytics/Innate_Odylytics`). Ngôn ngữ tài liệu: tiếng Việt; `README.md` gốc là cổng vào bằng tiếng Anh.

## Muốn biết... thì đọc...
| Câu hỏi | Đọc |
|---|---|
| Innate là gì, nằm ở đâu trong chồng bảo mật | [`plan/positioning.md`](plan/positioning.md), [`plan/how-it-works.md`](plan/how-it-works.md) |
| Số đo hiện tại, giới hạn | [`research/ai-research.md`](research/ai-research.md) (mục 6b: mọi thí nghiệm), bảng chỉ mục [`../research/EXPERIMENTS.md`](../research/EXPERIMENTS.md) |
| Nộp bài thiếu gì, hạn, thể lệ | [`contest/submission-checklist.md`](contest/submission-checklist.md), [`contest/the-le-cuoc-thi.md`](contest/the-le-cuoc-thi.md), [`contest/dang-ky-va-cau-hoi-btc.md`](contest/dang-ky-va-cau-hoi-btc.md) |
| Giấy phép, tài sản có sẵn, dữ liệu | [`../LICENSE`](../LICENSE), [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md), [`research/datasets.md`](research/datasets.md) |
| Thu dữ liệu của đội ra sao | [`plan/thu-du-lieu-doi.md`](plan/thu-du-lieu-doi.md) (kế hoạch + phiếu đồng ý + lệnh phân tích) |
| Câu thử thách (Innate Challenge) | [`plan/innate-challenge.md`](plan/innate-challenge.md), tiếng Việt Telex/VNI: [`plan/innate-challenge-vi.md`](plan/innate-challenge-vi.md) |
| 4 kênh bằng chứng (chuyển động, PIN, câu, vuốt) | [`plan/bon-cong-pipeline.md`](plan/bon-cong-pipeline.md) |
| Bài báo liên quan, ta học được gì | [`research/related-work.md`](research/related-work.md), [`research/paper-report.md`](research/paper-report.md) |
| Web demo cho giám khảo | [`plan/web-demo.md`](plan/web-demo.md), [`research/transfer-flow.md`](research/transfer-flow.md), `../web/README.md` |
| Slide, video, PDF 1 trang, README nộp | [`submission/`](submission/) |

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
  data/, external/                dữ liệu và mã bên thứ ba: GIT-IGNORED, không nộp
docs/                             tài liệu (xem bảng trên)
  contest/  plan/  research/  submission/  (research/notes/ = ghi chú đọc paper theo nhóm)
papers/                           52 PDF bài báo (bản quyền nhà xuất bản: không nộp; danh mục ở docs/research/paper-report.md)
```
Ngoài repo (máy người thu dữ liệu): `/Users/nguyenminhquan/Desktop/Projects/Innate/data.zip` (Touchalytics), `processed_typing_data.zip` (Aalto), đã giải nén vào `research/data/`.

## Quy ước
- Số hiệu thí nghiệm: E1–E14 như trong `ai-research.md` (E14 = chuỗi số mới, do đội web làm); E18–E27 bổ sung 25/11. **E15–E17 không dùng** (đổi thành E19–E21 để khỏi trùng E14).
- Mọi con số trong tài liệu do mã trong `research/experiments/` sinh ra; không có số nào chỉnh tay. Số trên dữ liệu giả chỉ để thử đường ống, không đưa lên slide.
- Dữ liệu người dùng: chỉ thời gian, toạ độ, loại sự kiện, số ký tự; không lưu nội dung PIN, số tiền, nội dung gõ.
