# DL training pipeline (4 stages) and hook into `#/collect`

```
phone #/collect --attempt_meta--> POST /v1/sessions --history.compute--> raw["_history"]  (HistoryContext, 16 keys)
        GET /v1/export (ML key) --> training/data/ingest.py --> tensors (x_seq, h_ctx, f_tab) --> splits (person-disjoint + time)
        training/trainers (owner: triplet + matcher; human: u/head) --> eval/calibrate (tau(k,dt), FRR 5%) --> export/to_numpy
        bundle (manifest.json + weights.npz) --> backend/app/scoring/dl_adapter.py (NumPy) --> /score (shadow or live)
```

## Stage 1: history parameters (backend + web)
- `backend/app/scoring/history.py` computes HistoryContext from the user's earlier sessions + `attempt_meta` (`flow_stage`, `retries`, `client_dt_prev_ms`, sent by `#/collect`): counts (n_enroll, n_sessions_total, attempt_index_in_sitting, n_attempts_10m/1h/24h, n_recent_flagged, client_retries), gaps (dt_prev_session_sec, dt_last_enroll_sec, dt_mean_recent_sec, dt_cv_recent, enroll_span_sec, client_dt_prev_ms), device continuity (same_device_as_enroll, n_distinct_devices). A sitting ends after a 30 min pause.
- Stored in `TouchSession.raw["_history"]` (no new table, `create_all` needs no ALTER); returned as `history` by `/v1/export`. NEVER in `features`, so `owner.py` templates are unchanged. `EnrollOut/AccountOut/UserOut.history_summary` feeds the Accuracy check telemetry.
- Web: `web/src/attempt.ts` counts retries (wrong PIN, deleted digit, failed tap) and the gap between entries. Enrolment sends `signup_enroll` / `login_enroll`; transfers send `transfer` WITHOUT `meta`, so `/v1/export?collected_only=true` still skips them. `#/demo` (`demoSim.ts`) is untouched.

## Stage 2: data + splits (`training/data/`)
`ingest.py` (export, StrokePIN, attacker bots), `history_features.py` (imports the backend formulas: one source), `tensors.py`, `splits.py`, `episodes.py`, `synth.py` (dry run only).

## Stage 3: models + trainers + eval (`training/models`, `trainers`, `eval`)
See `docs/research/four-layer-dl-architecture.md`. Metrics: EER, FAR@FRR=5%, Gini, person-clustered bootstrap CI by k and dt; `e2e_sim.py` runs `fusion.py`.

## Stage 4: export + backend adapter
`export/to_numpy.py` (bundle), `verify_parity.py` (float64 torch vs NumPy <= 1e-5), `to_onnx.py` (optional encoder). `dl_adapter.py` is pure NumPy (no torch on Vercel). Env: `NHIP_DL_BUNDLE` (default `backend/app/models/dl/`), `NHIP_OWNER_BACKEND`, `NHIP_HUMAN_BACKEND` (`lgbm` default | `dl`), `NHIP_DL_SHADOW=1` (log to `TouchSession.result["shadow"]`, decisions unchanged). No bundle, broken bundle or numpy missing => silent fallback to `owner_model`/`human_model`/`owner.py`/`human.py`. `/health` keeps `models: {human, owner}`; DL state is under `dl_pipeline`.

## Phases
1. Done: history + web telemetry + adapter + dry run (synthetic). 2. Collect real data on `#/collect` (consent), export, retrain with `dryrun`-style script on the export. 3. Run shadow on the live API, compare with lgbm per k and dt. 4. Only then switch `NHIP_*_BACKEND=dl`; ship a bundle trained on real data (licence: CC BY-NC-SA, declare it).

Run: `cd training && uv sync && uv run python dryrun.py` (about 20 s) and `uv run python -m pytest -q`.
