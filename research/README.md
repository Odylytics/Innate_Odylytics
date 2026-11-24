# research/

Thí nghiệm AI (chạy cục bộ, không thuộc bản nộp).

- `experiments/e1_fewshot_owner.py`: E1/E2 proxy trên CMU DSL-StrongPassword. Cần `numpy`, `pandas`.
- `data/`: dữ liệu tải về (gitignored). Link và trạng thái: [`../docs/research/datasets.md`](../docs/research/datasets.md).
- `results/`: bảng kết quả sinh ra.

```bash
mkdir -p data && curl -L -o data/DSL-StrongPasswordData.csv https://www.cs.cmu.edu/~keystroke/DSL-StrongPasswordData.csv
python experiments/e1_fewshot_owner.py     # ghi results/e1_dsl.md
```
