# TypeFormer fine-tune (E32)

Research only; nothing here ships in the API. Result: [`../results/e32_typeformer_finetune.md`](../results/e32_typeformer_finetune.md).

```bash
cd research/finetune
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python torch numpy pandas scikit-learn einops "x_transformers==0.27.0" torchtyping typeguard
.venv/bin/python zero_shot.py                      # pretrained TypeFormer on StrokePIN (needs research/data/StrokePIN)
.venv/bin/python finetune.py --epochs 25 --out runs/ft_a
```

`common.py` builds a patched copy of `research/external/TypeFormer` in `_tf/` (the original hard-codes CUDA and float64; MPS needs float32). The pretrained weights and code are MIT (Stragapede et al.); `external/` and `_tf/` are git-ignored. Checkpoints (`runs/**/*.pt`) are git-ignored.
