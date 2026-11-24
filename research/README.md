# research/

Thí nghiệm AI (chạy cục bộ, không thuộc bản nộp).

- `experiments/e1_fewshot_owner.py`: E1/E2 proxy trên CMU DSL-StrongPassword. Cần `numpy`, `pandas`.
- `experiments/e5_replay.py`: E5, phát hiện phát lại (dữ liệu giả). Cần `numpy`; import trực tiếp `backend/` và `attacker/`.
- `experiments/e7_poisoning.py`: E7, đầu độc mẫu chuẩn (dữ liệu giả).
- `experiments/e4_human_bot_lgbm.py`: E4, LightGBM + IsolationForest cho bài người/máy, đánh giá bỏ-một-chiến-thuật (dữ liệu giả). Cần `lightgbm`, `scikit-learn`.
- `experiments/e4b_human_bot_real.py`: E4b, người/máy với người thật từ StrokePIN (bot vẫn giả).
- `experiments/strokepin_loader.py` + `e9_strokepin_owner.py`: E9, xác minh chủ trên PIN điện thoại thật (StrokePIN, cần `git clone` vào `data/StrokePIN`).
- `experiments/e5b_replay_real.py`: E5b, hiệu chỉnh kiểm tra phát lại trên người thật (StrokePIN).
- `experiments/e10_deployable_prior.py`, `e10b_backend_path.py`, `make_population_prior.py`: co rút về dân số dùng được khi triển khai; kiểm tra chính `owner.py`; sinh `backend/app/scoring/population_prior.json`.
- `experiments/train_human_model.py`: huấn luyện mô hình người/máy (StrokePIN + bot sinh) ra `backend/app/models/` (tạm thời).
- `external/`: mã/trọng số của bên thứ ba tải về (gitignored), hiện có TypeFormer (MIT).
- `models/`: mô hình huấn luyện trên dữ liệu giả, chỉ để tham khảo.
- `data/`: dữ liệu tải về (gitignored). Link và trạng thái: [`../docs/research/datasets.md`](../docs/research/datasets.md).
- `results/`: bảng kết quả sinh ra.

```bash
mkdir -p data && curl -L -o data/DSL-StrongPasswordData.csv https://www.cs.cmu.edu/~keystroke/DSL-StrongPasswordData.csv
python experiments/e1_fewshot_owner.py     # ghi results/e1_dsl.md
```
