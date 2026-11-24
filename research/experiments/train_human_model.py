"""Huấn luyện mô hình người/máy cho backend: LightGBM, NGƯỜI THẬT (StrokePIN) + bot do bộ sinh tạo.

Đây là mô hình TẠM THỜI: người thật công khai (chưa phải người dùng của đội) và bot giả (chưa có bot thật).
Thay bằng dữ liệu của đội khi có. Chia theo người: train 50 / val 12 / test 20 / kho kẻ tấn công 15.
Không dùng đặc trưng kích thước chạm (web có thể chỉ trả 1; bot đặt được giá trị bất kỳ).
Ra: backend/app/models/human_lgbm.txt + human_lgbm.json (đặc trưng, ngưỡng FRR 5%, mô tả huấn luyện).

DỮ LIỆU CỦA ĐỘI (việc B): `python experiments/train_human_model.py --export export.jsonl [--no-strokepin] [--no-generated]`
  export.jsonl = đầu ra của GET /v1/export (JSON list hoặc mỗi dòng một bản ghi {raw, meta:{participant_id, role, tactic}}).
  role genuine/impostor -> người (impostor là người biết PIN); role bot -> bot THẬT (adb, dispatchGesture...). Người chia theo participant_id.
  Mặc định vẫn thêm StrokePIN và bot sinh; bỏ bằng --no-strokepin / --no-generated. Ngưỡng FRR 5% chọn trên người validation.
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
import strokepin_loader  # noqa: E402

SEED, FRR, TACTICS = 7, 0.05, (1, 2, 3, 4)
ARGS = sys.argv[1:]
EXPORT = ARGS[ARGS.index("--export") + 1] if "--export" in ARGS else None
USE_STROKEPIN, USE_GENERATED = "--no-strokepin" not in ARGS, "--no-generated" not in ARGS
N_H, N_BOT = {"train": 4000, "val": 1500, "test": 3000, "pool": 500}, {"train": 800, "test": 400}
NAMES = [n for n in bot_features.FEATURE_NAMES if n not in bot_features.CONTACT_FEATURES]

rng = random.Random(SEED)
H = {k: [] for k in ("train", "val", "test", "pool")}
PINS = []
if USE_STROKEPIN:  # chia như bản gốc (giữ nguyên kết quả khi chạy không cờ)
    S = strokepin_loader.load()
    USERS, PINS = sorted({e["user"] for e in S}), sorted({e["pin"] for e in S})
    us = USERS[:]
    rng.shuffle(us)
    split = {"train": us[:50], "val": us[50:62], "test": us[62:82], "pool": us[82:]}
    for k, v in split.items():
        ses = [e["session"] for e in S if e["user"] in set(v)]
        H[k] = rng.sample(ses, N_H[k]) if len(ses) >= N_H[k] else ses
real_bots = {"train": [], "test": []}
if EXPORT:  # dữ liệu của đội: GET /v1/export
    txt = Path(EXPORT).read_text(encoding="utf-8").strip()
    recs = json.loads(txt) if txt.startswith("[") else [json.loads(l) for l in txt.splitlines() if l.strip()]
    team: dict[str, list[dict]] = {}
    rbots = []
    for r in recs:
        meta, raw = r.get("meta") or {}, r.get("raw") or r
        raw = {**raw, "swipes": raw.get("swipes", []), "screens": raw.get("screens", [])}
        if meta.get("role") in ("genuine", "impostor") and raw.get("pin_taps"):
            team.setdefault(str(meta.get("participant_id")), []).append(raw)  # impostor = người biết PIN: vẫn là người
        elif meta.get("role") == "bot":
            rbots.append(raw)
    ppl = sorted(team)
    rng.shuffle(ppl)
    n = len(ppl)
    cut = {"train": ppl[: int(0.6 * n)], "val": ppl[int(0.6 * n): int(0.75 * n)], "test": ppl[int(0.75 * n):]}
    for k, who in cut.items():
        H[k] += [x for p in who for x in team[p]]
    H["pool"] += [x for p in cut["train"] for x in team[p]][:N_H["pool"]]  # kho kẻ tấn công cho bot sinh
    rng.shuffle(rbots)
    real_bots = {"train": rbots[: int(0.7 * len(rbots))], "test": rbots[int(0.7 * len(rbots)):]}
    PINS = PINS or sorted({"".join(t["key"] for t in x["pin_taps"]) for x in H["pool"]})
    print(f"export: {n} người, {sum(len(v) for v in team.values())} phiên người, {len(rbots)} phiên bot thật")
if not H["train"] or not H["val"]:
    sys.exit("thiếu dữ liệu người cho tập train/val: cần StrokePIN hoặc --export có role genuine")


def bots(t, n):
    return [{**tactics.generate(t, "victim", rng.choice(PINS), H["pool"], rng), "swipes": [], "screens": []} for _ in range(n)]


def vec(sessions):
    return np.array([[bot_features.extract(s)[k] for k in NAMES] for s in sessions], dtype=float).reshape(len(sessions), len(NAMES))


Xh = vec(H["train"])
Xb = np.vstack([vec(bots(t, N_BOT["train"])) for t in TACTICS] if USE_GENERATED else [np.empty((0, len(NAMES)))] + [vec(real_bots["train"])])
if USE_GENERATED and real_bots["train"]:
    Xb = np.vstack([Xb, vec(real_bots["train"])])
if len(Xb) == 0:
    sys.exit("không có bot nào để huấn luyện: bật bot sinh (bỏ --no-generated) hoặc đưa bot thật vào export")
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

out = ROOT / "backend/app/models"
out.mkdir(exist_ok=True)
model.booster_.save_model(str(out / "human_lgbm.txt"))
src = ["StrokePIN (người thật, CC BY-NC-SA 4.0, chia theo người)"] * USE_STROKEPIN + ["dữ liệu của đội (export)"] * bool(EXPORT)
meta = {"features": NAMES, "threshold": thr, "target_frr": FRR, "seed": SEED,
        "trained_on": " + ".join(src) + (" + bot sinh bởi attacker/tactics.py" if USE_GENERATED else "") + (" + bot thật" if real_bots["train"] else ""),
        "status": "có dữ liệu của đội" if EXPORT else "TẠM THỜI: chưa phải dữ liệu của đội, chưa có bot thật", "heldout_report": rep}
(out / "human_lgbm.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(rep, indent=2))
