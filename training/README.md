# training/: the 4-layer deep model (Innate4LayerNet)

Research code, kept apart from the backend: it needs PyTorch, the API does not. The API runs the exported weights with NumPy (`backend/app/scoring/dl_adapter.py`).
Design: [`docs/research/four-layer-dl-architecture.md`](../docs/research/four-layer-dl-architecture.md), pipeline: [`docs/plan/dl-training-pipeline.md`](../docs/plan/dl-training-pipeline.md).

**Status 28/11/2026: tried on SYNTHETIC data only. No number printed here is a result.** Real data comes from `#/collect` (`GET /v1/export`).

## Run
```
cd training
uv sync
uv run python dryrun.py              # ~20 s: synth data -> train -> eval by k and dt -> export -> parity -> backend shadow score
uv run python -m pytest -q
```
`dryrun.py` writes to a temp directory and never touches `backend/app/models/`.

## What is where
| Folder | Content |
|---|---|
| `data/` | `ingest.py` (export JSON/JSONL, StrokePIN, attacker bots), `history_features.py` (uses the backend formulas), `tensors.py`, `splits.py` (person-disjoint + time split), `episodes.py` (gallery of k entries + query), `synth.py` (dry run only) |
| `models/innate4.py` | the 4 layers |
| `trainers/` | `train_owner.py` (triplet with same-PIN hard negatives, then matcher), `train_human.py` (human vs bots) |
| `eval/` | `metrics.py` (EER, FAR@FRR=5%, Gini, bootstrap CI by person, per k and dt), `calibrate.py` (tau(k, dt) at FRR 5%), `e2e_sim.py` (runs `fusion.py`) |
| `export/` | `to_numpy.py` (bundle), `verify_parity.py` (<= 1e-5), `to_onnx.py` (optional) |

## From a trained model to the API
1. `to_numpy.export(model, dir, f_mean, f_std, tau, human_threshold)` writes `manifest.json` + `weights.npz`.
2. `verify_parity.verify(...)` must report `ok` (float64 PyTorch vs the NumPy runtime).
3. Point the backend at it: `NHIP_DL_BUNDLE=<dir>` and `NHIP_DL_SHADOW=1`. Each `/score` then logs `result["shadow"]` (visible in `/v1/export`) while the decision still comes from lgbm/rules.
4. Only after comparing shadow against lgbm on real data per k and dt: `NHIP_OWNER_BACKEND=dl` and/or `NHIP_HUMAN_BACKEND=dl`.
Missing or broken bundle, or no numpy: the backend silently keeps the lgbm/rule path.

## Known limits
- Synthetic data; StrokePIN has no timestamps between entries (`from_strokepin` assumes 1 h per entry).
- `train_human` trains only `u_head` and the human head (trunk frozen so the owner embedding stays intact).
- Bots in training and test come from the same generators (CLAUDE.md known gap): keep `adb` sessions as the independent test.
- Data derived from StrokePIN is CC BY-NC-SA 4.0: a bundle trained on it inherits that licence.
