# research/

AI experiments (run locally, not part of the submission). **Full index E1–E32: [`EXPERIMENTS.md`](EXPERIMENTS.md).** Map of the whole project: [`../docs/INDEX.md`](../docs/INDEX.md).

- `experiments/e1_fewshot_owner.py`: E1/E2 proxy on CMU DSL-StrongPassword. Needs `numpy`, `pandas`.
- `experiments/e5_replay.py`: E5, replay detection (synthetic data). Needs `numpy`; imports `backend/` and `attacker/` directly.
- `experiments/e7_poisoning.py`: E7, template poisoning (synthetic data).
- `experiments/e4_human_bot_lgbm.py`: E4, LightGBM + IsolationForest for the human/bot task, leave-one-tactic-out evaluation (synthetic data). Needs `lightgbm`, `scikit-learn`.
- `experiments/e4b_human_bot_real.py`: E4b, human/bot with real people from StrokePIN (bots are still synthetic).
- `experiments/strokepin_loader.py` + `e9_strokepin_owner.py`: E9, owner verification on a real phone PIN (StrokePIN, needs `git clone` into `data/StrokePIN`).
- `experiments/aalto_note_extract.py` + `e11_text_field_bots.py`: real free-text typing rhythm from Aalto (timing only, no content) and E11 human/bot on the note field; run with `python -I` because it reads externally downloaded data.
- `experiments/e12_learned_owner.py` (+ `--no-contact`), `train_owner_model.py`: learned owner verification (E12/E12b) and training the model for the backend.
- `experiments/e13_length_effect.py`: do more keys help (Innate Challenge).
- `experiments/e5b_replay_real.py`: E5b, calibrating the replay check on real people (StrokePIN).
- `experiments/e10_deployable_prior.py`, `e10b_backend_path.py`, `make_population_prior.py`: shrinkage toward the population usable in deployment; checks `owner.py` itself; generates `backend/app/scoring/population_prior.json`.
- `experiments/train_human_model.py`: trains the human/bot model (StrokePIN + generated bots) into `backend/app/models/` (temporary).
- `external/`: downloaded third-party code/weights (gitignored), currently TypeFormer (MIT).
- `models/`: models trained on synthetic data, for reference only.
- `data/`: downloaded data (gitignored). Links and status: [`../docs/research/datasets.md`](../docs/research/datasets.md).
- `results/`: generated result tables.

```bash
mkdir -p data && curl -L -o data/DSL-StrongPasswordData.csv https://www.cs.cmu.edu/~keystroke/DSL-StrongPasswordData.csv
python experiments/e1_fewshot_owner.py     # writes results/e1_dsl.md
```
