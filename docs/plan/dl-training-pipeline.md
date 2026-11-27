# 4-Layer Deep Learning Training Pipeline & Phone Account Integration Plan

> Design and implementation plan (27/11/2026). **Plan only — not implemented yet; no code has been modified.**
> Connects the offline research/training layer (`research/`) with the scoring core (`backend/app/scoring/`) and the phone account creation & enrollment flow (`web/src/Collect.tsx`, route `#/collect`).

---

## 1. Motivation & Gap Analysis

### What exists today
- **Scoring & API (`backend/`):**
  - `app/db.py` stores `User` (`template`), `Account` (scrypt auth for `#/collect`), and `TouchSession` (`created_at`, `user_id`, `device_id`, `raw`, `features`, `is_enrollment`, `context`, `result`, `risk`, `action`, `label`).
  - `app/scoring/` evaluates each session independently (`features.py`, `bot_features.py`, `human.py`, `human_model.py`, `owner.py`, `owner_model.py`, `fusion.py`), plus a recent-session similarity check in `replay.py` (`REPLAY_HISTORY = 50`).
  - Learned models (`human_lgbm.txt`, `owner_lgbm.txt`) run through a zero-dependency pure-Python parser (`lgbm_text.py`) because Vercel serverless deployment has no `torch` or `libgomp`.
- **Research & DL (`research/`):**
  - Tabular training scripts (`research/experiments/train_human_model.py`, `train_owner_model.py`) and benchmark scripts (`e29_cv_end_to_end.py`, `e30_enroll_curve.py`, `team_data_dryrun.py`) live separately from PyTorch experiments (`research/finetune/common.py`, `finetune.py` for TypeFormer E32).
- **Phone account creation & collection (`web/src/Collect.tsx`, `web/src/api.ts`, `web/src/enrollCurve.ts`):**
  - `Start`: email/password sign-up (`POST /v1/accounts/signup`, `POST /v1/participants`) or login (`POST /v1/accounts/login`).
  - `EnrollRounds`: 5–10 PIN entries (`POST /v1/sessions` + `POST /v1/users/{id}/enroll` with `keep_open=true`, locked via `POST /v1/users/{id}/enroll/finish`).
  - `Transfer`: live-scored transactions (`POST /v1/sessions` + `POST /v1/sessions/{id}/score`).

### Key gaps addressed by this design
1. **No inter-session history parameters:** Current models look at one session at a time and ignore **how many times the user has entered their PIN/sessions** (`n_enroll`, `n_sessions_total`, `retries`, `n_attempts_10m/1h/24h`) and **the intervals between attempts/sessions** (`dt_prev_session_sec`, `dt_last_enroll_sec`, `dt_cv_recent`, `client_dt_prev_ms`).
2. **No unified DL experimentation layer:** Switching between architectures (1D-CNN, GRU, Transformer/TypeFormer, Prototypical/Set-to-Session networks) currently requires copying dataset, splitting, and metric scripts.
3. **No production plug-in path for DL:** E32 TypeFormer improved StrokePIN EER (`0.292 -> 0.203`) and FAR@FRR5% (`0.706 -> 0.418`), yet remains research-only with no calibration, manifest, or lightweight runtime adapter into `backend/app/scoring/`.
4. **Lost client-side attempt signals during phone enrollment:** `EnrollRounds` in `Collect.tsx` discards mismatched/aborted PIN attempts (`pin_retries`) and exact client-side inter-attempt gaps (`client_dt_prev_ms`), and only renders an extrapolated `k`-curve (`enrollCurve.ts`) rather than live history telemetry.

---

## 2. 4-Layer Pipeline Architecture

> For the concrete 4-layer neural model architecture (`Innate4LayerNet`) grounded in all 52 PDFs (43 unique papers) in `papers/` — mapping Layer 1 (`GRE + Multi-Scale Conv1D`), Layer 2 (`BiGRU + Self-Attention`), Layer 3 (`Time- & Attempt-Aware Set Matching + Drift Guard`), and Layer 4 (`Dual-Stream Operating-Point Calibration Head`) — see [`../research/four-layer-dl-architecture.md`](../research/four-layer-dl-architecture.md).

```
+-----------------------------------------------------------------------------+
| LAYER 1: Data Ingestion & Inter-Session History Builder                     |
| - Sources: /v1/export JSONL (team data) + StrokePIN / Aalto + attacker/     |
| - Computes HistoryContext (attempt counts, Δt intervals, retry bursts)      |
| - Builds SessionTensor (raw tap sequence + tabular + history) & FETA splits |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| LAYER 2: Pluggable Deep Learning Model Zoo & Trainers                       |
| - Owner Verification: PIN1DCNN, PINGRU, TinyTransformer, TypeFormer,        |
|   TimeAwareProtoMatcher (attention weighted by Δt and enrollment count k)   |
| - Human vs. Bot: DualStreamHumanNet (tap/field sequence + interval bursts)  |
| - Losses: Triplet (same-PIN hard negatives), SupCon, CosFace / BCE          |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| LAYER 3: Evaluation & Calibration Engine                                    |
| - FETA benchmarks: EER, FAR@FRR=5%, bootstrap CIs by person                 |
| - Stratified breakdowns: by enrollment count (k = 2..10) & Δt buckets       |
| - End-to-end simulation (allow / step_up / hold) with attacker/ tactics 1-4 |
| - k-aware calibration (Platt / Temperature / quantile) -> [0, 1] @ thr=0.5  |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| LAYER 4: Export Bridge & Backend Plug-in Adapter                            |
| - Outputs bundle: manifest.json + weights (.npz / .onnx / optional .pt)     |
| - Runtime backends: NumPy (Vercel serverless), ONNX Runtime, or HTTP worker |
| - Plugs into backend/app/scoring/ with shadow mode & automatic fallback     |
+-----------------------------------------------------------------------------+
```

Proposed directory layout (under a dedicated package, e.g. `training/`, keeping `backend/` free of PyTorch training dependencies):

```
training/
  config/                  # YAML/JSON experiment configs (model, loss, split, features)
  data/
    ingest.py              # Loaders for /v1/export JSONL, StrokePIN, Aalto, attacker/
    history_features.py    # Shared/mirrored HistoryContext extraction from timestamps
    tensors.py             # SessionTensor builder (pin_seq, swipe_seq, tab_feats, mask)
    splits.py              # Person-disjoint & time-split FETA dataset builder
  models/
    base.py                # Unified interfaces: OwnerEncoder, OwnerMatcher, HumanDetector
    encoders.py            # PIN1DCNN, PINGRU, TinyTransformer, TypeFormer wrapper
    proto_matcher.py       # TimeAwareProtoMatcher (k- & Δt-conditioned set attention)
    human_dual.py          # DualStreamHumanNet (sequence + HistoryContext burst features)
  trainers/
    train_owner.py         # Metric-learning / set-to-session training loop
    train_human.py         # Human vs. bot (generated + real adb) training loop
  eval/
    metrics.py             # EER, FAR@FRR5%, bootstrap CI, stratified k and Δt reports
    e2e_sim.py             # End-to-end fusion simulation (E29 protocol)
    calibrate.py           # k-bucketed Platt / temperature / quantile calibrator
  export/
    to_numpy.py            # Export small NN weights to .npz + manifest.json
    to_onnx.py             # Export to quantized/float32 .onnx + manifest.json
    verify_parity.py       # Numerical parity check (PyTorch vs. exported runtime <= 1e-5)
```

---

## 3. Detailed Specification of Each Layer

### Layer 1 — Data Ingestion & Inter-Session Parameters (`HistoryContext`)

Every session $s_t$ for `user_id` is paired with its ordered prior history $\{s_1, \dots, s_{t-1}\}$ sorted by `created_at`.

#### A. Inter-session & attempt parameters
1. **Number of input attempts / turns ("số lượt nhập"):**
   - `n_enroll` ($k$): count of prior `is_enrollment = true` sessions for this user.
   - `n_sessions_total`: total prior sessions for this user (enrollment + transfer/scoring).
   - `attempt_index_in_sitting`: 1-based attempt index within the current continuous sitting (sessions separated by `< 300s`, or matching `meta.sitting` during collection).
   - `n_attempts_10m`, `n_attempts_1h`, `n_attempts_24h`: session counts in sliding windows prior to $s_t$.
   - `n_recent_flagged`: count of prior sessions in the last 24h whose `action` was `step_up` or `hold`.
   - `client_retries`: number of mismatched or aborted PIN attempts on the phone keypad before the accepted submission (sent by the phone client).
2. **Intervals between attempts ("khoảng cách giữa các lần"):**
   - `dt_prev_session_sec`: seconds elapsed since $s_{t-1}$ (`null` on first session; encoded as `log1p(dt)` + presence indicator `has_prev`).
   - `dt_last_enroll_sec`: seconds elapsed since the most recent enrollment session (captures cross-session / cross-day behavioral drift).
   - `dt_mean_recent_sec`, `dt_cv_recent`: mean and coefficient of variation (`std / mean`) of inter-session gaps over the last $N=10$ sessions (scripted bots running on fixed timers exhibit abnormally low `dt_cv_recent`).
   - `enroll_span_sec`: total elapsed seconds between the 1st and $k$-th enrollment attempt.
   - `client_dt_prev_ms`: high-resolution client-side gap (ms) since the previous PIN entry/attempt on the phone, removing network/DB latency jitter for rapid retries.
3. **Device continuity:**
   - `same_device_as_enroll`: boolean / fraction of enrolled sessions sharing `device_id` with $s_t$.
   - `n_distinct_devices`: number of unique `device_id`s seen for `user_id`.

#### B. Input tensor construction (`SessionTensor`)
- **`pin_seq`** shape `(L_pin, 8)` (`L_pin = 12`, matching `SessionIn.pin_taps` `max_length=12`, or `50` when pretrained TypeFormer compatibility is needed):
  - `[hold_s, press_press_s, release_release_s, release_prev_press_s, dx_norm, dy_norm, key_code_norm, valid_mask]`
  - Explicitly excludes touch contact size (`w`, `h`) to avoid device confounding (per E12b).
- **`tab_feats`**: fixed-length vector combining `bot_features.extract(raw)` (without `CONTACT_FEATURES`) + normalized `HistoryContext` scalars.
- **Episode construction for Owner Verification:** each training/eval item forms `(support_set[1..k], support_dt_sec[1..k], query_session, query_history_ctx, label_is_impostor)` where `k` is sampled across `{2, 3, 4, ..., 10}` so models learn to adapt to variable enrollment counts.

#### C. Splitting discipline (FETA)
- Strict **person-disjoint** split (`participant_id` / `user_id` never crosses train/val/test).
- **Time-split** within each person: earlier sittings/timestamps populate enrollment (`support_set`) and earlier history; later sittings/timestamps serve as queries.
- Zero impostor data ever enters a user's enrollment template or `support_set`.

---

### Layer 2 — Pluggable Deep Learning Research Core

All candidate models implement a minimal Python contract so trainers, evaluators, and exporters treat architectures uniformly:

- **`OwnerMatcher` contract:**
  - `encode(pin_seq, mask, tab_feats) -> embedding (D,)`
  - `match(support_embs, support_dt, query_emb, history_ctx) -> logit_impostor`
- **`HumanDetector` contract:**
  - `predict_logit(pin_seq, mask, tab_feats, history_ctx) -> logit_human`

#### Candidate architectures to benchmark
1. **Lightweight PIN Encoders (primary candidates for serverless deployment):**
   - `PIN1DCNN`: multi-scale 1D convolutions (`kernel=2, 3, 5` capturing unigrams, digraphs, trigraphs) + attentive statistics pooling. Very fast on 4–12 tap inputs (< 2 ms CPU).
   - `PINGRU`: 1–2 layer bidirectional GRU over tap sequences + attention pooling + LayerNorm.
   - `TinyTransformer`: 2-layer, 4-head Transformer encoder (`d_model=64`) with relative positional encoding.
2. **Pretrained / Large Reference Encoder:**
   - `TypeFormerWrapper`: wraps `research/finetune/common.py` (`HARTrans`, E32), optionally extending input dimension from 5 to 7 (`+ dx, dy`) or projecting `HistoryContext` into a post-embedding head.
3. **`TimeAwareProtoMatcher` (Owner Head):**
   - Instead of unweighted mean Euclidean distance (E32), computes attention weights $\alpha_i$ over the $k$ enrollment embeddings $e_i$ conditioned on $\log(1 + \Delta t_i)$ and `n_enroll`, producing a weighted prototype $\mu_{\text{proto}}$ plus spread-aware comparison features $[|q - \mu_{\text{proto}}|, (q - \mu_{\text{proto}})^2, \cos(q, \mu_{\text{proto}}), \log(1 + k), \log(1 + \Delta t_{\text{last\_enroll}})]$.
4. **`DualStreamHumanNet` (Human vs. Bot Head):**
   - Branch A encodes `pin_seq`; Branch B encodes `bot_features` + `HistoryContext` (`n_attempts_10m`, `client_retries`, `dt_cv_recent`, `dt_prev_session_sec`) through a residual MLP; fused with a gated linear head.
5. **Training objectives:**
   - `TripletLoss` / `SupCon` with same-PIN hard-negative mining (impostor typing the identical 6-digit PIN).
   - Binary cross-entropy with focal weighting for `DualStreamHumanNet` against generator tactics 1–4 + real `adb` bots.

---

### Layer 3 — Evaluation & Calibration Engine

Every trained model runs the same evaluation suite before it can be exported:

1. **Core metrics:** `EER`, `FAR@FRR=5%`, `AUC`, with 1,000x person-level bootstrap 95% confidence intervals.
2. **Required stratified slices:**
   - **By enrollment count `k`:** `k = 2, 3, 4, 5, ..., 10` (replaces power-law extrapolation in `web/src/enrollCurve.ts` once real team data is collected).
   - **By inter-session gap `Δt`:** short gap (`< 10 min`, same sitting), medium (`10 min – 24 h`), long (`>= 24 h`, cross-day drift).
   - **By device condition:** same device (stolen phone) vs. different device (confound check).
   - **End-to-end simulation (`e2e_sim.py`):** plug candidate model into `fusion.py` (`allow | step_up | hold`) against genuine owners, PIN-knowing impostors, tactics 1–4, and adaptive replay (±10% to ±30%), mirroring E29.
3. **`k`-aware calibration:**
   - Fit calibration mapping on the **validation** split so output score $\in [0, 1]$ aligns with `backend/app/scoring/`:
     - `owner_match >= 0.5` corresponds to `FRR <= 5%` for each `k` bucket (`k=2`, `k=3`, `k=4`, `k>=5`).
     - `human_score >= 0.5` corresponds to `FRR <= 5%` on validation humans.
   - Save calibration parameters `(slope, intercept, threshold_by_k)` inside `manifest.json`.

---

### Layer 4 — Export Bridge & Backend Plug-in Adapter

To respect Vercel's serverless constraints (no PyTorch, minimal cold-start and bundle size, `backend/pyproject.toml`), models cross into `backend/` strictly through an exported bundle + plug-in adapter:

1. **Bundle layout (`backend/app/models/dl/<bundle_name>/`):**
   - `manifest.json`: schema version, `task` (`owner | human`), `architecture`, `pin_seq_len`, `tab_features`, `history_features`, normalization `mean/std`, `k`-aware calibration params, `heldout_report`, data provenance/license note.
   - `weights.npz` (for pure-NumPy inference of compact CNN/GRU/MLP/TinyTransformer models) or `model.onnx` (optional `onnxruntime` path).
2. **Backend scoring adapter (`backend/app/scoring/dl_adapter.py`):**
   - Controlled via environment variables (safe fallback by default):
     - `NHIP_OWNER_BACKEND=lgbm|dl_numpy|dl_onnx|dl_remote|rules` (default remains existing `lgbm` until validated).
     - `NHIP_HUMAN_BACKEND=lgbm|dl_numpy|dl_onnx|dl_remote|rules`.
     - `NHIP_DL_SHADOW=on|off` and `NHIP_DL_BUNDLE=<name>`.
   - **Pure-NumPy runner (preferred for Vercel):** implements Conv1D, GRU, LayerNorm, MultiHeadAttention, and Linear layers in pure NumPy/Python (same philosophy as `lgbm_text.py`), verified by `verify_parity.py` to match PyTorch within `1e-5`.
   - **Optional remote HTTP runner (`dl_remote`):** for heavy models like full `TypeFormer`, calls an external GPU/CPU inference endpoint with a tight timeout (e.g. `150 ms`) and automatically falls back to `owner_lgbm` / `owner.py` on timeout or error.
   - **Shadow mode:** evaluates the DL bundle asynchronously/inline during `POST /v1/sessions/{id}/score` and writes `{bundle, human_score, owner_match, latency_ms}` into `TouchSession.result["shadow"]` without altering live `action` (`allow | step_up | hold`).

---

## 4. Integration Plan with Phone Account Creation (`#/collect`)

The phone user entry lives in `web/src/Collect.tsx` (`#/collect`), backed by `/v1/accounts/*`, `/v1/users/{id}/enroll*`, `/v1/sessions`, `/v1/sessions/{id}/score`, and `/v1/export` in `backend/app/main.py`.

### End-to-End Flow After Integration

```
[Phone: #/collect]
  1. Start (Sign up / Login)
     -> POST /v1/accounts/signup (+ /v1/participants)
     -> Creates User + Account; initializes device_id & flow clock
           |
           v
  2. EnrollRounds (5–10 PIN entries, keep_open=true)
     -> Tracks client_retries (mismatches/clears) & client_dt_prev_ms
     -> POST /v1/sessions (raw + attempt_meta {flow_stage: "signup_enroll", retries, client_dt_prev_ms})
        -> Backend history.py queries prior TouchSessions for user_id -> computes HistoryContext
        -> Stores HistoryContext snapshot safely (no breaking DB column migration)
     -> POST /v1/users/{id}/enroll (keep_open=true)
        -> Returns EnrollOut + history_summary (n_enroll, mean_gap_sec, dt_last_enroll_sec, consistency)
        -> UI renders Accuracy check bar + live attempt/interval telemetry
     -> POST /v1/users/{id}/enroll/finish (locks enrollment)
           |
           v
  3. Transfer (Live-scored transaction)
     -> Tracks retries & client_dt_prev_ms (meta stays omitted unless collection mode)
     -> POST /v1/sessions (raw + attempt_meta {flow_stage: "transfer", ...})
     -> POST /v1/sessions/{id}/score
        -> history.py builds HistoryContext -> passed to dl_adapter (active or shadow) + existing scoring
        -> Returns ScoreOut (allow | step_up | hold)
           |
           v
  4. Offline Training Loop
     -> GET /v1/export returns sessions WITH persisted HistoryContext & attempt_meta
     -> Layer 1 ingests export -> Layer 2 trains DL models -> Layer 3 calibrates by k & Δt -> Layer 4 deploys bundle
```

### Concrete File-by-File Integration Plan

1. **Client API & Schema Contract (`web/src/api.ts`, `backend/app/schemas.py`):**
   - Add optional `attempt_meta` to `SessionIn`:
     - `flow_stage: Literal["signup_enroll", "login_enroll", "transfer", "step_up"] | None`
     - `retries: int = Field(default=0, ge=0, le=100)`
     - `client_dt_prev_ms: float | None = Field(default=None, ge=0)`
   - Keep `SessionIn.meta` (`CollectionMeta`) unchanged so transfer sessions that intentionally omit `meta` do not pollute `/v1/export?collected_only=true`.
   - Extend `EnrollOut` / `AccountOut` / `UserOut` with an optional `history_summary` object (`n_enroll`, `n_sessions_total`, `mean_enroll_gap_sec`, `dt_last_enroll_sec`, `enroll_span_sec`, `dl_bundle_active`).

2. **Phone Account & Enrollment UI (`web/src/Collect.tsx`, `web/src/enrollCurve.ts`):**
   - **`Start`:** on successful `signup` or `login`, record `lastEntryAt` timestamp in memory/state and pass `AccountStatus` (including `history_summary` if resuming enrollment on a later day/sitting).
   - **`EnrollRounds`:**
     - Increment a `retriesRef` counter whenever the user submits a mismatched PIN (`digits !== pin.current`), clears/aborts mid-entry, or encounters an incomplete tap error.
     - Compute `client_dt_prev_ms = performance.now() - lastRoundTs` before calling `api.createSession(...)`, and reset `retriesRef = 0` after successful enrollment.
     - Update the **Accuracy check** section under the keypad to surface the user's real attempt telemetry alongside the existing curve (e.g., entries completed `k/10`, average interval between rounds, rhythm steadiness `consistency`, and whether the active curve is `measured` vs. `DL-calibrated`).
   - **`Transfer`:**
     - Track `retries` and `client_dt_prev_ms` between confirmation attempts and attach `attempt_meta: { flow_stage: "transfer", retries, client_dt_prev_ms }`.
     - If `score.action === "step_up"` and the user re-enters or proceeds to a challenge phrase, carry the retry/interval context cleanly without altering `demoSim.ts` (the static `#/demo` wallet must remain completely offline per `CLAUDE.md`).

3. **Backend History Extraction & Persistence (`backend/app/db.py`, `backend/app/main.py`, `backend/app/scoring/history.py`):**
   - **Database schema safety (`Base.metadata.create_all` constraint):** Because existing SQLite (`nhip.db`) and Neon Postgres tables are not auto-migrated by `create_all`, **do not add required columns to existing `sessions` or `users` tables**. Instead:
     - Either create a dedicated table `SessionHistory` (via `Base.metadata.create_all`) keyed by `session_id` (`ForeignKey("sessions.id")`), **or** persist the computed `HistoryContext` snapshot inside `TouchSession.raw["_history"]` (and return it in `/v1/export`).
     - **Important isolation guard:** keep `hist_*` keys **out** of `TouchSession.features` (or add `"hist_"` to `owner.is_identity_feature` exclusions) so existing scaled-Manhattan templates in `owner.py` and `replay.py` remain 100% unaffected.
   - **Endpoint wiring in `main.py`:**
     - `POST /v1/sessions`: extract `HistoryContext` from prior `TouchSession` rows of `body.user_id` + `body.attempt_meta`, persist snapshot.
     - `POST /v1/users/{id}/enroll`, `/enroll/finish`, `GET /v1/users/{id}`, `/v1/accounts/signup`, `/v1/accounts/login`: include `history_summary` in `_enroll_status()`.
     - `POST /v1/sessions/{id}/score`: pass `(s.raw, feats, tpl, history_ctx)` to `dl_adapter` (in active or shadow mode); if `dl_adapter` returns `None` or is disabled, keep current `human_model` / `owner_model` / `owner.py` / `fusion.py` behavior.
     - Keep `GET /health` `"models": {"human": bool, "owner": bool}` keys intact so existing tests (`test_learned_models_load_by_default`) do not break; expose DL bundle status under an additive key such as `"dl_pipeline": {...}`.
   - **Controlled re-enrollment compatibility (`docs/plan/dang-ky-lai.md`):** when a user later re-enrolls across days via an authenticated re-enrollment window, `n_enroll` and `dt_last_enroll_sec` naturally reflect multi-day enrollment rounds for `TimeAwareProtoMatcher`.

---

## 5. Phased Implementation Roadmap

| Phase | Deliverables | Exit Criteria / Verification |
|---|---|---|
| **Phase 1: History Contract & Phone Telemetry** | `backend/app/scoring/history.py`, optional `attempt_meta` in `schemas.py`, `main.py` wiring + `/v1/export` snapshot, `web/src/api.ts` + `Collect.tsx` telemetry & enrollment summary UI. | All existing `backend/tests/` (60 tests) and `web` Vitest suites pass; new unit tests verify `n_enroll`, `retries`, `dt_prev_session_sec`, `dt_last_enroll_sec`, and zero template leakage in `owner.py`. |
| **Phase 2: Layer 1 Dataset & FETA Splitter** | `training/data/{ingest,history_features,tensors,splits}.py` supporting `/v1/export` JSONL, StrokePIN, and `attacker/` dry-run data. | Reproducible dry-run exports `(pin_seq, tab_feats, history_ctx)` with zero person/time leakage and parity checks against `backend/app/scoring/history.py`. |
| **Phase 3: Layer 2–3 DL Zoo, Eval & Calibration** | `training/models/{base,encoders,proto_matcher,human_dual}.py`, `training/trainers/*`, `training/eval/{metrics,e2e_sim,calibrate}.py`. | Benchmark table comparing `owner.py`, `owner_lgbm`, `PIN1DCNN`, `PINGRU`, `TimeAwareProtoMatcher`, and `TypeFormer` across `k=2..5+` and same-sitting vs. cross-day `Δt`. |
| **Phase 4: Layer 4 Export, Adapter & Shadow Rollout** | `training/export/*`, `backend/app/scoring/dl_adapter.py`, `manifest.json` + `.npz`/`.onnx` bundle, shadow-mode logging on `/v1/sessions/{id}/score`. | `verify_parity.py` max diff `<= 1e-5`; `/score` latency p50 `< 15 ms` local; shadow scores logged on `#/collect` sessions without changing `allow \| step_up \| hold` until threshold calibration is approved. |
| **Phase 5: Promotion & Measured `k`-Curve** | Flip `NHIP_OWNER_BACKEND` / `NHIP_HUMAN_BACKEND` to exported DL bundle after real team data validation; replace extrapolated values in `web/src/enrollCurve.ts` with measured DL curve. | Real-data `FAR@FRR=5%` with bootstrap CIs outperforms interim LightGBM baseline across unseen people and cross-day sittings. |

---

## 6. Guardrails & Constraints (Do Not Break)
- **Privacy (PDPL 2025 / Luật BVDLCN 2025):** `HistoryContext` stores only aggregate counts and time intervals ($\Delta t$), never raw PINs/passwords/message content. Keep `#/collect` consent disclosures accurate if new client retry counters are persisted.
- **Static demo isolation:** `#/demo` (`web/src/demoSim.ts`) remains strictly offline with zero backend calls.
- **Rule-first safety:** ML/DL models remain a risk signal inside `fusion.py` (`allow | step_up | hold`); never turn `owner_match` into a hard account lock, and never place an LLM on the decision path.
- **Backward compatibility:** Existing Neon Postgres / local SQLite databases, `NHIP_API_KEYS` / `NHIP_OPS_KEYS` / `NHIP_ML_KEYS` scopes, and `NHIP_*` env defaults must continue running with zero manual migration steps.
