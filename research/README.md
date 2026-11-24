# research/

Thí nghiệm AI (chạy cục bộ, không thuộc bản nộp).

- `experiments/e1_fewshot_owner.py`: E1/E2 proxy trên CMU DSL-StrongPassword. Cần `numpy`, `pandas`.
- `experiments/e5_replay.py`: E5, phát hiện phát lại (dữ liệu giả). Cần `numpy`; import trực tiếp `backend/` và `attacker/`.
- `experiments/e7_poisoning.py`: E7, đầu độc mẫu chuẩn (dữ liệu giả).
- `experiments/e4_human_bot_lgbm.py`: E4, LightGBM + IsolationForest cho bài người/máy, đánh giá bỏ-một-chiến-thuật (dữ liệu giả). Cần `lightgbm`, `scikit-learn`.
- `external/`: mã/trọng số của bên thứ ba tải về (gitignored), hiện có TypeFormer (MIT).
- `models/`: mô hình huấn luyện trên dữ liệu giả, chỉ để tham khảo.
- `data/`: dữ liệu tải về (gitignored). Link và trạng thái: [`../docs/research/datasets.md`](../docs/research/datasets.md).
- `results/`: bảng kết quả sinh ra.

```bash
mkdir -p data && curl -L -o data/DSL-StrongPasswordData.csv https://www.cs.cmu.edu/~keystroke/DSL-StrongPasswordData.csv
python experiments/e1_fewshot_owner.py     # ghi results/e1_dsl.md
```
