# Experiment index (E1–E32)

> Updated 25/11/2026. Interpretation, hypotheses and limits of each experiment: [`../docs/research/ai-research.md`](../docs/research/ai-research.md) (section 6b). Code in `experiments/`, result tables in `results/`. Data: [`../docs/research/datasets.md`](../docs/research/datasets.md). Data licenses: [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
> Column "Data": **real** = publicly available real people; **synthetic** = self-generated (not shown on slides). Bots are always the team's generator (no real bots yet). In the bot names, T1–T4 are the four attack tactics (T = tactic).

| E | Question | Data | Code `experiments/` | Result `results/` | Short conclusion |
|---|---|---|---|---|---|
| E1/E2 | Does shrinking variance toward the population help few-shot? | real (CMU, computer keyboard) | `e1_fewshot_owner.py` | `e1_dsl.md` | Lowers FAR@FRR5% by 7–11 points, EER unchanged |
| E3 | Calibrate the owner score mapping `d → score` | real (StrokePIN) | `e3_calibrate_owner.py` | `e3_calibrate_owner.md` | The old mapping lets 84% of PIN-knowing impostors pass 0.5; class-balanced Platt reduces this to 27% (owner 90%); FAR@FRR5% is still 50%. Trial wiring into the backend (`NHIP_OWNER_MAP=platt`, `e24_platt_map.md`): it only changes the fallback path and breaks the new-recipient flow; left off by default |
| E4 | LightGBM human/bot, leave-one-tactic-out | synthetic | `e4_human_bot_lgbm.py` | `e4_human_bot_lgbm.md` | The good numbers come from shortcut learning; unseen bots collapse |
| E4b | Human/bot with real people | real (StrokePIN) | `e4b_human_bot_real.py` | `e4b_human_bot_real.md` | T1/2 100%; T3 9–26%, T4 20–73% |
| E5 | Replay detection, adaptive noise | synthetic | `e5_replay.py` | `e5_replay.md` | Catches up to ±10–15% |
| E5b | Calibrate replay detection on real people | real (StrokePIN) | `e5b_replay_real.py` | `e5b_replay_real.md` | Threshold 0.07; 29% at ±15% |
| E7 | Template poisoning | synthetic | `e7_poisoning.py` | `e7_poisoning.md` | Should "freeze + flag" (not applied yet) |
| E9 | Owner recognition on a real phone PIN | real (StrokePIN) | `strokepin_loader.py`, `e9_strokepin_owner.py` | `e9_strokepin_owner.md` | EER ~0.16; the signal is lost when posture changes |
| E10/E10b | Shrinkage toward the population usable in deployment | real | `make_population_prior.py`, `e10_deployable_prior.py`, `e10b_backend_path.py` | `e10_*.md`, `e10b_*.md` | Goes into `owner.py`, generates `population_prior.json` |
| E11 | Human/bot on a free-text field | real (Aalto) | `aalto_note_extract.py`, `e11_text_field_bots.py` | `e11_text_field_bots.md` | Naive bot ~100% once seen in training; unseen bots 0% |
| E12/E12b | Learned owner model | real (StrokePIN) | `e12_learned_owner.py`, `train_owner_model.py` | `e12_learned_owner.md`, `e12b_*.md` | FAR@FRR5% 0.573 → 0.375 |
| E13 | Do more keys help? (Innate Challenge) | real (Aalto) | `e13_length_effect.py` | `e13_length_effect.md` | FAR 81% → 49% from 6 → 30 keys |
| E14 | Owner when typing a new number string (account number) | real (StrokePIN) | `e14_unseen_digits.py` | `e14_unseen_digits.md` | EER 0.33 (6 new digits); see `docs/research/transfer-flow.md` |
| E18 | Number of Telex/VNI ways to type a sentence | theoretical | `e18_vi_variation.py` | `e18_vi_variation.txt` | 3–6.6 bits of variation (upper bound) |
| E19 | Swipe rule and owner recognition by swipe | real (Touchalytics) | `e19_touchalytics.py` | `e19_touchalytics.txt` | The old rule wrongly blocks 13.4%; the uniform-velocity rule 0/20,896; swipes do not identify the owner (AUC ~0.5) |
| E20 | How many syllables have a tone-mark choice | simulation | `e20_vi_style_sim.py` | `e20_vi_style_sim.txt` | AUC 0.66 (1) → 0.89 (8); choose sentences with ≥ 4 |
| E21/E21b | Normalization by key pair | real (Aalto) | `aalto_note_chars.py`, `e21_digraph_norm.py`, `e21b_digraph_profile.py` | `e21_digraph_norm.md`, `e21b_*.md` | Almost no change; the key-pair profile is worse |
| E22 | Ways to reduce FAR of the challenge sentence | real (Aalto) | `aalto_note_orient.py`, `e22_improve_far.py` | `e22_improve_far.md` | Learned model −7 points; posture is optimistic, dropped |
| E23 | Phone motion for owner recognition | real (StrokePIN) | `e23_imu_fusion.py` | `e23_imu_fusion.md` | EER 0.04 but it is device noise; lost when posture changes |
| E24 | Whole-system decision (allow/step_up/hold) | real + bot | `e24_end_to_end.py` | `e24_end_to_end.md` | Naive bots and replay ≤ ±10% 100% hold |
| E25 | Sweep of thresholds A, B | real + bot | `e24_end_to_end.py` | `e24_end_to_end.md` | No optimum for both sides |
| E26 | Local API latency | synthetic | `e26_latency.py` | `e26_latency.md` | `/score` p50 3.7 ms, max 36 ms after preloading the models (before: ~1 s on the first call) |
| E28 | 4-digit PIN (demo) or 6-digit: system decision | real (StrokePIN cut to 4 taps, approximation) | `e28_pin_length.py` | `e28_pin_length.md` | 4-digit PIN: the learned owner model does not run; PIN-knowing impostor allowed 68% (6 digits: 28%) |
| E29 | E24 on all 97 people (5-fold CV by person, models retrained), CI | real + bot | `e29_cv_end_to_end.py` | `e29_cv_end_to_end.md` | PIN-knowing impostor allow 22% [20,24]; sitting owner 76%, walking 49%; template-aware bot allow 72–87%; no victim is allowed >90% (Gini 0.28) |
| E29b | E29 with the learned models off (fallback mode: rules only; the online version ran in this mode until 26/11) | real + bot | `e29_cv_end_to_end.py` with `E29_MODELS=off` | `e29_rules_only.md` | PIN-knowing impostor allow **89%**, sitting owner 95%, template-aware bot 95%; naive bots and replay ≤±10% still 100% hold |
| E30 | Number of enrollment sessions k=2,3,4 and Gini by victim | real (StrokePIN) | `e30_enroll_curve.py` | `e30_enroll_curve.md` | FAR@FRR5% 0.857 (k=2) → 0.503 (k=3) → 0.429 (k=4) |
| E31 | Tune fusion weights + threshold A on E29 (tune on 3 folds, test on 2) | real + bot | `e31_tune_fusion.py` (reads the `e29` pickle written with `E29_DUMP`) | `e31_tune_fusion.md` | Best is wb 0.50 / wo 0.30 / A 0.26, only +2 points on the test folds (55% → 57%) and lowers blocking of the PIN-knowing impostor 81% → 77%: within the variation, KEEP the current configuration |
| E32 | Fine-tune TypeFormer (Aalto) on StrokePIN, 60/7/30 people split by person | real (StrokePIN) | `finetune/finetune.py`, `finetune/zero_shot.py` | `e32_typeformer_finetune.md` | k=3: EER 0.292 → 0.203, FAR@FRR5% 0.706 → 0.418 (30 unseen people); a single run, no CI, not in the API yet |
| E27/E27b | Adaptive bots; replay threshold | real + bot | `e24_end_to_end.py` | `e24_end_to_end.md` | Replay of ±15% and above and the template-aware bot get through |

**Not run / no numbers yet:** E3 on team data (it was run on StrokePIN), E6, E8 (plans in `docs/research/research-plan.md`); combining PIN + sentence; Vietnamese typing style on real people; real bots; team data. Pipeline for team data: `team_analysis.py` (T1–T5), `team_data_dryrun.py` (tests the pipeline with fake data), `train_human_model.py --export ... --out ...`.

## Re-running
- Environment: `numpy pandas scikit-learn lightgbm` (+ `fastapi httpx` for `e26`, `team_data_dryrun`). Data is downloaded separately into `research/data/` (git-ignored).
- Use `python -I` for scripts that read externally downloaded data (`aalto_note_*.py`).
- Experiment numbers E15–E17 are not used (renamed to E19–E21 to avoid clashing with E14).
