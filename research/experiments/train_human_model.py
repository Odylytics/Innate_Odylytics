"""Train the human/bot model for the backend: LightGBM, REAL PEOPLE (StrokePIN) + bots made by the generator.

This is a TEMPORARY model: public real people (not the team's users) and synthetic bots (no real bots yet).
Replace with the team's data when available. Split by person: train 50 / val 12 / test 20 / attacker pool 15.
Touch-size features are not used (the web may only return 1; a bot can set any value).
Output: backend/app/models/human_lgbm.txt + human_lgbm.json (features, FRR 5% threshold, training description).

TEAM DATA (task B): `python experiments/train_human_model.py --export export.jsonl --out <directory> [--no-strokepin] [--no-generated]` (with --export, --out or --overwrite is REQUIRED)
  export.jsonl = output of GET /v1/export (a JSON list or one record per line {raw, meta:{participant_id, role, tactic}}).
  role genuine/impostor -> human (impostor is a person who knows the PIN); role bot -> REAL bot (adb, dispatchGesture...). People are split by participant_id.
  By default StrokePIN and generated bots are still added; drop them with --no-strokepin / --no-generated. The FRR 5% threshold is chosen on the validation people.
"""

import json
import random
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker"), str(Path(__file__).parent)]
from app.scoring import bot_features  # noqa: E402
from nhip_attacker import tactics  # noqa: E402

SEED, FRR, TACTICS = 7, 0.05, (1, 2, 3, 4)
ARGS = sys.argv[1:]
EXPORT = ARGS[ARGS.index("--export") + 1] if "--export" in ARGS else None
OUT_DIR = Path(ARGS[ARGS.index("--out") + 1]) if "--out" in ARGS else None
if EXPORT and not OUT_DIR and "--overwrite" not in ARGS:
    sys.exit("--export will OVERWRITE the model in backend/app/models. Add --out <directory> to try it, or --overwrite when sure.")
USE_STROKEPIN, USE_GENERATED = "--no-strokepin" not in ARGS, "--no-generated" not in ARGS
N_H, N_BOT = {"train": 4000, "val": 1500, "test": 3000, "pool": 500}, {"train": 800, "test": 400}
NAMES = [n for n in bot_features.FEATURE_NAMES if n not in bot_features.CONTACT_FEATURES]

rng = random.Random(SEED)
H = {k: [] for k in ("train", "val", "test", "pool")}
PINS = []
if USE_STROKEPIN:  # split as in the original version
    import strokepin_loader  # late import: running with team data only (--no-strokepin) needs no pandas/StrokePIN (results unchanged when run without flags)
    S = strokepin_loader.load()
    USERS, PINS = sorted({e["user"] for e in S}), sorted({e["pin"] for e in S})
    us = USERS[:]
    rng.shuffle(us)
    split = {"train": us[:50], "val": us[50:62], "test": us[62:82], "pool": us[82:]}
    for k, v in split.items():
        ses = [e["session"] for e in S if e["user"] in set(v)]
        H[k] = rng.sample(ses, N_H[k]) if len(ses) >= N_H[k] else ses
real_bots = {"train": [], "test": []}
if EXPORT:  # team data: GET /v1/export
    txt = Path(EXPORT).read_text(encoding="utf-8").strip()
    recs = json.loads(txt) if txt.startswith("[") else [json.loads(l) for l in txt.splitlines() if l.strip()]
    team: dict[str, list[dict]] = {}
    rbots = []
    for r in recs:
        meta, raw = r.get("meta") or {}, r.get("raw") or r
        raw = {**raw, "swipes": raw.get("swipes", []), "screens": raw.get("screens", [])}
        if meta.get("role") in ("genuine", "impostor") and raw.get("pin_taps"):
            team.setdefault(str(meta.get("participant_id")), []).append(raw)  # impostor = a person who knows the PIN: still a human
        elif meta.get("role") == "bot":
            rbots.append(raw)
    ppl = sorted(team)
    rng.shuffle(ppl)
    n = len(ppl)
    cut = {"train": ppl[: int(0.6 * n)], "val": ppl[int(0.6 * n): int(0.75 * n)], "test": ppl[int(0.75 * n):]}
    for k, who in cut.items():
        H[k] += [x for p in who for x in team[p]]
    H["pool"] += [x for p in cut["train"] for x in team[p]][:N_H["pool"]]  # attacker pool for generated bots
    rng.shuffle(rbots)
    real_bots = {"train": rbots[: int(0.7 * len(rbots))], "test": rbots[int(0.7 * len(rbots)):]}
    PINS = PINS or sorted({"".join(t["key"] for t in x["pin_taps"]) for x in H["pool"]})
    print(f"export: {n} people, {sum(len(v) for v in team.values())} human sessions, {len(rbots)} real bot sessions")
if not H["train"] or not H["val"]:
    sys.exit("missing human data for the train/val sets: need StrokePIN or an --export with role genuine")


def bots(t, n):
    return [{**tactics.generate(t, "victim", rng.choice(PINS), H["pool"], rng), "swipes": [], "screens": []} for _ in range(n)]


def vec(sessions):
    return np.array([[bot_features.extract(s)[k] for k in NAMES] for s in sessions], dtype=float).reshape(len(sessions), len(NAMES))


Xh = vec(H["train"])
Xb = np.vstack([vec(bots(t, N_BOT["train"])) for t in TACTICS] if USE_GENERATED else [np.empty((0, len(NAMES)))] + [vec(real_bots["train"])])
if USE_GENERATED and real_bots["train"]:
    Xb = np.vstack([Xb, vec(real_bots["train"])])
if len(Xb) == 0:
    sys.exit("no bots to train on: enable generated bots (drop --no-generated) or put real bots in the export")
model = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=20, subsample=0.8,
                           subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, random_state=SEED, verbose=-1)
model.fit(np.vstack([Xh, Xb]), np.r_[np.ones(len(Xh)), np.zeros(len(Xb))])
p = lambda X: model.predict_proba(X)[:, 1]  # noqa: E731
thr = float(np.quantile(p(vec(H["val"])), FRR))

rep = {"threshold": thr, "n_human_train": len(Xh), "n_bot_train": len(Xb)}
if H["test"]:
    rep["FRR_test_humans"] = float((p(vec(H["test"])) < thr).mean())
if USE_GENERATED and PINS:
    for t in TACTICS:
        rep[f"catch_tactic{t}"] = float((p(vec(bots(t, N_BOT["test"]))) < thr).mean())
if real_bots["test"]:
    rep["catch_real_bots_test"] = float((p(vec(real_bots["test"])) < thr).mean())

out = OUT_DIR or ROOT / "backend/app/models"
out.mkdir(parents=True, exist_ok=True)
model.booster_.save_model(str(out / "human_lgbm.txt"))
src = ["StrokePIN (real people, CC BY-NC-SA 4.0, split by person)"] * USE_STROKEPIN + ["team data (export)"] * bool(EXPORT)
meta = {"features": NAMES, "threshold": thr, "target_frr": FRR, "seed": SEED,
        "trained_on": " + ".join(src) + (" + bots generated by attacker/tactics.py" if USE_GENERATED else "") + (" + real bots" if real_bots["train"] else ""),
        "status": "includes team data" if EXPORT else "TEMPORARY: not the team's data, no real bots yet", "heldout_report": rep}
(out / "human_lgbm.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(rep, indent=2))
