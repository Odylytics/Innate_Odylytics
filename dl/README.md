# dl/: 4-layer deep model (research only)

**This folder is NOT part of the product and NOT part of the contest submission.** The live API (`backend/`), the website (`web/`) and the hand-in pack never import it; `tools/build_submission.sh` leaves `dl/` out of the source zip. It exists so the team can research a deep model next to the LightGBM one without touching what was reviewed.

Design: [`docs/four-layer-dl-architecture.md`](docs/four-layer-dl-architecture.md). Pipeline: [`docs/dl-training-pipeline.md`](docs/dl-training-pipeline.md).

**Status 28/11/2026: tried on SYNTHETIC data only. No number here is a result.**

## Run
```
cd dl
uv sync
uv run python dryrun.py        # ~20 s: synth data -> train -> eval by k and dt -> export -> parity -> NumPy runtime scores
uv run python -m pytest -q     # 10 tests
```
`dryrun.py` writes to a temp dir and touches nothing in `backend/` or `web/`. It reads `backend/app/scoring/{bot_features,fusion}.py` (read only) and `attacker/`.

## Layout
| Path | Content |
|---|---|
| `innate_dl/` | `dl_adapter.py` (input preprocessing + pure-NumPy forward + bundle loader; single source shared with training), `history.py` (HistoryContext, 16 parameters) |
| `data/` | `ingest.py` (`/v1/export` JSON/JSONL, StrokePIN, attacker bots; rebuilds HistoryContext offline), `tensors.py`, `splits.py` (person-disjoint + time split), `episodes.py`, `synth.py` (dry run only) |
| `models/innate4.py` | the 4 layers (PyTorch) |
| `trainers/` | `train_owner.py` (triplet, same-PIN hard negatives; then matcher), `train_human.py` |
| `eval/` | `metrics.py` (EER, FAR@FRR=5%, Gini, bootstrap CI by person per k and dt), `calibrate.py` (tau(k, dt) at FRR 5%), `e2e_sim.py` (via `fusion.py`) |
| `export/` | `to_numpy.py` (manifest.json + weights.npz), `verify_parity.py` (float64 torch vs NumPy <= 1e-5), `to_onnx.py` (optional) |
| `integration/` | **parked, not applied**: `product-hooks.patch` (the `/score` shadow mode, `attempt_meta`, `history_summary`, `#/collect` telemetry), `tests/` and `web/` that go with it |

## Data
The product stores no HistoryContext and no `attempt_meta`. For training, `ingest.from_export` rebuilds history offline from `created_at`, `device_id`, `is_enrollment` and the scoring `result`, but only over exported (collected) sessions, so counts are lower bounds and `client_retries` / `client_dt_prev_ms` are 0 / None. Real timing across sittings needs real `#/collect` data.

## Landing it in the product later (after 03/12, only if shadow evidence justifies it)
1. `git apply dl/integration/product-hooks.patch` (it also adds numpy to `backend/pyproject.toml`; regenerate `uv.lock`).
2. Copy `dl/innate_dl/{dl_adapter,history}.py` to `backend/app/scoring/` and change the imports in the patch's `main.py` hunks accordingly; copy `integration/tests/*` to `backend/tests/` and `integration/web/*` to `web/src/`.
3. `NHIP_DL_BUNDLE=<dir> NHIP_DL_SHADOW=1`, compare against lgbm per k and dt on real data; only then `NHIP_OWNER_BACKEND=dl` / `NHIP_HUMAN_BACKEND=dl`.
The patch was made against the 28/11 `main`; expect to resolve small conflicts.

## Limits
- Synthetic data; StrokePIN has no timestamps between entries (`from_strokepin` assumes 1 h per entry).
- `train_human` trains only `u_head` and the human head (trunk frozen so the owner embedding stays intact).
- Bots in training and test come from the same generators (CLAUDE.md known gap): keep `adb` sessions as the independent test.
- A bundle trained on StrokePIN inherits its CC BY-NC-SA 4.0 licence.
- PyTorch, ONNX and ONNX Runtime are used here only; the product does not depend on them.
