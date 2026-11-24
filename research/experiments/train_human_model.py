"""Huấn luyện mô hình người/máy cho backend: LightGBM, NGƯỜI THẬT (StrokePIN) + bot do bộ sinh tạo.

Đây là mô hình TẠM THỜI: người thật công khai (chưa phải người dùng của đội) và bot giả (chưa có bot thật).
Thay bằng dữ liệu của đội khi có. Chia theo người: train 50 / val 12 / test 20 / kho kẻ tấn công 15.
Không dùng đặc trưng kích thước chạm (web có thể chỉ trả 1; bot đặt được giá trị bất kỳ).
Ra: backend/app/models/human_lgbm.txt + human_lgbm.json (đặc trưng, ngưỡng FRR 5%, mô tả huấn luyện).
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
N_H, N_BOT = {"train": 4000, "val": 1500, "test": 3000, "pool": 500}, {"train": 800, "test": 400}
NAMES = [n for n in bot_features.FEATURE_NAMES if n not in bot_features.CONTACT_FEATURES]

S = strokepin_loader.load()
USERS, PINS = sorted({e["user"] for e in S}), sorted({e["pin"] for e in S})
rng = random.Random(SEED)
us = USERS[:]
rng.shuffle(us)
split = {"train": us[:50], "val": us[50:62], "test": us[62:82], "pool": us[82:]}
H = {k: rng.sample([e["session"] for e in S if e["user"] in set(v)], N_H[k]) if len([e for e in S if e["user"] in set(v)]) >= N_H[k]
     else [e["session"] for e in S if e["user"] in set(v)] for k, v in split.items()}


def bots(t, n):
    return [{**tactics.generate(t, "victim", rng.choice(PINS), H["pool"], rng), "swipes": [], "screens": []} for _ in range(n)]


def vec(sessions):
    return np.array([[bot_features.extract(s)[k] for k in NAMES] for s in sessions], dtype=float)


Xh = vec(H["train"])
Xb = np.vstack([vec(bots(t, N_BOT["train"])) for t in TACTICS])
model = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=20, subsample=0.8,
                           subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, random_state=SEED, verbose=-1)
model.fit(np.vstack([Xh, Xb]), np.r_[np.ones(len(Xh)), np.zeros(len(Xb))])
p = lambda X: model.predict_proba(X)[:, 1]  # noqa: E731
thr = float(np.quantile(p(vec(H["val"])), FRR))

Xt = vec(H["test"])
rep = {"threshold": thr, "FRR_test_humans": float((p(Xt) < thr).mean())}
for t in TACTICS:
    rep[f"catch_tactic{t}"] = float((p(vec(bots(t, N_BOT["test"]))) < thr).mean())

out = ROOT / "backend/app/models"
out.mkdir(exist_ok=True)
model.booster_.save_model(str(out / "human_lgbm.txt"))
meta = {"features": NAMES, "threshold": thr, "target_frr": FRR, "seed": SEED,
        "trained_on": "StrokePIN (người thật, CC BY-NC-SA 4.0, chia theo người) + bot sinh bởi attacker/tactics.py",
        "status": "TẠM THỜI: chưa phải dữ liệu của đội, chưa có bot thật", "heldout_report": rep}
(out / "human_lgbm.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(rep, indent=2))
