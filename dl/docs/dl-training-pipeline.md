# DL training pipeline (4 stages)

> Research only (`dl/`). The product and the submission do not include it. Parts that touch the product (`attempt_meta`, `/score` shadow mode) are parked in `dl/integration/` and are NOT applied.

```
phone #/collect --attempt_meta--> POST /v1/sessions --history.compute--> raw["_history"]  (HistoryContext, 16 keys)
        GET /v1/export (ML key) --> training/data/ingest.py --> tensors (x_seq, h_ctx, f_tab) --> splits (person-disjoint + time)
        training/trainers (owner: triplet + matcher; human: u/head) --> eval/calibrate (tau(k,dt), FRR 5%) --> export/to_numpy
        bundle (manifest.json + weights.npz) --> backend/app/scoring/dl_adapter.py (NumPy) --> /score (shadow or live)
```

## Stage 1: history parameters
- `innate_dl/history.py` computes HistoryContext from a user's earlier sessions (+ optional `attempt_meta`): counts (n_enroll, n_sessions_total, attempt_index_in_sitting, n_attempts_10m/1h/24h, n_recent_flagged, client_retries), gaps (dt_prev_session_sec, dt_last_enroll_sec, dt_mean_recent_sec, dt_cv_recent, enroll_span_sec, client_dt_prev_ms), device continuity (same_device_as_enroll, n_distinct_devices). A sitting ends after a 30 min pause.
- In the product nothing of this is stored. Training rebuilds it offline from an export (`data/ingest.py`).
- Parked design (`integration/`): store it in `TouchSession.raw["_history"]` (never in `features`, so `owner.py` templates are unchanged), send `attempt_meta` from `#/collect` (transfers without `meta`, so `collected_only` still skips them), add `history_summary` to the enrol responses. `#/demo` stays static.

## Stage 2: data + splits (`training/data/`)
`ingest.py` (export, StrokePIN, attacker bots), `history_features.py` (imports the backend formulas: one source), `tensors.py`, `splits.py`, `episodes.py`, `synth.py` (dry run only).

## Stage 3: models + trainers + eval (`training/models`, `trainers`, `eval`)
See `docs/research/four-layer-dl-architecture.md`. Metrics: EER, FAR@FRR=5%, Gini, person-clustered bootstrap CI by k and dt; `e2e_sim.py` runs `fusion.py`.

## Stage 4: export + runtime
`export/to_numpy.py` (bundle), `verify_parity.py` (float64 torch vs NumPy <= 1e-5), `to_onnx.py` (optional encoder). `innate_dl/dl_adapter.py` is pure NumPy (no torch needed to run a bundle). `dryrun.py` loads the bundle and scores sessions with it.
Parked, not applied (`integration/product-hooks.patch`): `/score` wiring behind `NHIP_DL_BUNDLE`, `NHIP_OWNER_BACKEND`, `NHIP_HUMAN_BACKEND` (`lgbm` default | `dl`) and `NHIP_DL_SHADOW=1` (log to `TouchSession.result["shadow"]`, decisions unchanged), with silent fallback to lgbm/rules.

## Phases
1. Done: model, training, eval, export, dry run (synthetic). 2. Collect real data on `#/collect` (consent), export, retrain. 3. After 03/12: land `integration/`, run shadow on the live API, compare with lgbm per k and dt. 4. Only then switch the backend env vars; a bundle trained on StrokePIN is CC BY-NC-SA.

Run: see `dl/README.md`.
