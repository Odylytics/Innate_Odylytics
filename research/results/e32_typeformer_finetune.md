# E32: fine-tune TypeFormer (Aalto pretrained) on StrokePIN

Setup: `research/finetune/` (`finetune.py`, `common.py`, `zero_shot.py`). 97 people split **by person**: 60 train / 7 validation / 30 test (seed 0). Input = TypeFormer's 5 features per key (hold, press-press, release-release, release-press, key code/255), PIN padded to 50 rows. Triplet loss (margin 1), anchor/positive = same person and PIN (both postures), negative = another person typing the **same** PIN. AdamW lr 1e-4, 25 epochs x 60 steps x batch 64 on Apple M4 (MPS); checkpoint chosen on validation EER. Evaluation = E9 style: enroll k sitting entries per (person, PIN), genuine = remaining sitting entries (same posture) or walking entries, impostor = other test people typing the same PIN.

| k enrol | EER same posture | FAR@FRR5% same | EER walking | FAR@FRR5% walking |
|---|---|---|---|---|
| 2 | 0.207 | 0.426 | 0.314 | 0.659 |
| 3 | 0.203 | 0.418 | 0.311 | 0.661 |
| 4 | 0.200 | 0.390 | 0.310 | 0.658 |

Zero-shot (pretrained, no fine-tune), same 30 test people: k=3 EER 0.292, FAR@FRR5% 0.706; walking EER 0.379, FAR 0.848.

Caveats (say them): one run, one split, no confidence interval; 30 test people, not the 97-person protocol of E29/E30, so not directly comparable with the LightGBM numbers; devices differ between people (device confound); **not wired into the API** (Vercel has no torch; export to numpy/ONNX would be needed). The statistical baseline on 97 people (E30, k=3) is EER 0.146, FAR 0.503, so the fine-tuned Transformer is better on FAR at FRR 5% but not on EER on a different split.
