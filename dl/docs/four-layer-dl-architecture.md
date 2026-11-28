# Innate4LayerNet: 4-layer deep-learning architecture

Status 28/11/2026: implemented in `dl/` (`models/innate4.py`, NumPy twin in `innate_dl/dl_adapter.py`), research only, trained only on SYNTHETIC data, not part of the product or the submission. The design below was written down from the architecture sketch of 28/11; the paper-to-layer mapping cites the papers in `papers/` and `docs/research/related-work.md` and was NOT re-verified paper by paper here.

## Inputs
- `x_seq` (L<=12 taps x 10 channels): hold_s, pp_s (press-press), rr_s (release-release), rp_s (release-press), pp2_s, rp2_s (lag 2), dx_norm, dy_norm (offset in key units), jump_dist (distance between consecutive key centres, key units), mask. Time in seconds. Contact size `w,h` and pressure are dropped (device confound, CLAUDE.md).
- `h_ctx` (14): log1p of n_enroll, n_sessions_total, attempt_index_in_sitting, n_attempts_10m/1h/24h, n_recent_flagged, client_retries, dt_prev_session, dt_last_enroll, dt_mean_recent; dt_cv_recent; same_device_as_enroll (0/0.5/1); log1p n_distinct_devices. `enroll_span_sec` and `client_dt_prev_ms` are computed but not fed to the net (client-measured / redundant).
- `f_tab`: `bot_features.extract` minus the contact-size group, standardised with train statistics.

## Layers
1. **Spatio-temporal tokenisation.** Gaussian Range Encoding (G=20 per continuous channel, TypeFormer) -> masked Conv1D k=1,3,5 (TypeNet: conv before the RNN) -> Linear -> LayerNorm, H1 in R^{L x 64}. Train-time timing jitter U[0.98, 1.02] (BehavePassDB).
2. **Sequential motor encoder.** BiGRU (2x48) -> masked 4-head self-attention (+residual, LayerNorm) -> attentive statistics pooling (mean+std) -> `e_q` in R^64 (L2-normalised, identity) and `u_q` in R^32 (naturalness). 154k parameters in total.
3. **Time- and attempt-aware set matching + drift guard.** Gallery = the user's k enrolment embeddings with their age dt_i. Hybrid prototype: anchor mu_0 (first 3 entries) and mu_decay = sum alpha_i e_i, alpha = softmax(temp(k) * cos(e_q, e_i) + w_t * log(1+dt_i)) (Giot 2012, Lovisotto 2020). `v_match` (8) = cos to mu_0, cos to mu_decay, max/mean/min/std of cos over the set (ActReal Eq. 5 style), `drift_cos` = cos(mu_decay - mu_0, e_q - mu_0), `drift_mag`.
4. **Dual-stream operating-point head.** `s_human` = MLP(u_q, f_tab, h_burst) (h_burst = attempt index, 10m/1h counts, flagged, retries, dt_prev). `s_owner` = MLP(v_match, log1p k, log1p dt_last). Both are probabilities; `eval/calibrate.py` fits the threshold at FRR=5%: `tau(k, dt)` for k in {2,3,4,5+} x dt in {<=1h, >1h} (human: one threshold) and maps it to 0.5, the convention of `human_model.py` / `owner_model.py` and `fusion.py`.

## Training
Stage A: batch-hard Triplet on `e_q`, negatives preferably the same PIN. Stage B: layers 3-4 on episodes (gallery = first k entries, query = later entry or another person), embeddings frozen. Human head: trunk and `e_head` frozen, `u_head` + human head trained (tactics 1-4 / adb bots vs people). Owner models never see impostor data of the same person (FETA).

## Limits (honest)
- Dry run on synthetic data only (`dl/dryrun.py`); the numbers have no scientific meaning. StrokePIN has no timestamps between entries: `from_strokepin` assumes 1 h per entry.
- Not wired into the product: the `/score` shadow-mode patch is parked in `dl/integration/`.
- Bot and owner tests share generators with training (CLAUDE.md known gap): keep real/adb bots as the independent test.
