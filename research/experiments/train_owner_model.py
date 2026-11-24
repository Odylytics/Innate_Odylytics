"""Huấn luyện mô hình xác minh chủ (LightGBM trên |z|) cho backend, từ StrokePIN (người thật), KHÔNG dùng kích thước chạm.

Chia theo người: 70 huấn luyện / còn lại validation (chọn ngưỡng FRR 5% trên lượt chủ cùng tư thế). Prior dân số chỉ từ người huấn luyện.
Mô hình TẠM THỜI: dữ liệu công khai, PIN 6 số do người nghiên cứu giao, một đợt thu; thay bằng dữ liệu của đội.
Ra: backend/app/models/owner_lgbm.txt + owner_lgbm.json.
"""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import lightgbm as lgb
import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, owner  # noqa: E402
import strokepin_loader  # noqa: E402

K, N_DRAW, N_IMP, SEED, FRR = 3, 5, 15, 21, 0.05
EXCL = {"tap_w_mean", "tap_h_mean"}  # mang thông tin thiết bị
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
TK = sorted(k for k in S[0]["f"] if k.startswith(("pin_hold_", "pin_flight_")) or k == "pin_total")
grp, bpp = defaultdict(list), defaultdict(lambda: defaultdict(list))
for e in S:
    grp[(e["user"], e["pin"], e["posture"])].append(e)
    bpp[(e["pin"], e["posture"])][e["user"]].append(e)
USERS = sorted({e["user"] for e in S})
rng = random.Random(SEED)
us = USERS[:]
rng.shuffle(us)
tr, va = set(us[:68]), set(us[68:])
WV = {g: np.var(np.array([[e["f"][k] for k in TK] for e in es]), axis=0, ddof=1) for g, es in grp.items() if len(es) >= 2}
pv = np.mean([v for (u, _p, _po), v in WV.items() if u in tr], axis=0)
owner._PRIOR = {"within_var": dict(zip(TK, pv.tolist())), "n_taps": 6, "nu": 5}


def rows(users):
    X, y, post = [], [], []
    keys = None
    for (u, p, po), es in grp.items():
        if u not in users or po != "sit" or len(es) < K:
            continue
        for _ in range(N_DRAW):
            enr = rng.sample(es, K)
            tpl = owner.build_template([e["f"] for e in enr])
            keys = keys or sorted(k for k in tpl["mu"] if k not in EXCL)
            for tpost, gen in (("sit", [e for e in es if e not in enr]), ("walk", grp.get((u, p, "walk"), []))):
                if not gen:
                    continue
                pool = [e for v, ves in bpp[(p, tpost)].items() if v != u for e in ves]
                for lab, ents in ((0, gen), (1, rng.sample(pool, min(N_IMP, len(pool))))):
                    for e in ents:
                        z = owner.score(e["f"], tpl)[1]
                        X.append([abs(z[k]) for k in keys]); y.append(lab); post.append(tpost)
    return np.array(X), np.array(y), np.array(post), keys


Xtr, ytr, _, keys = rows(tr)
Xva, yva, pva, _ = rows(va)
m = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=30, subsample=0.8,
                       subsample_freq=1, colsample_bytree=0.8, random_state=SEED, verbose=-1).fit(Xtr, ytr)
p = m.predict_proba(Xva)[:, 1]
sit_gen = p[(yva == 0) & (pva == "sit")]
thr = float(np.quantile(sit_gen, 1 - FRR))  # p_kẻ_gian cao hơn ngưỡng này => nghi; 5% lượt chủ cùng tư thế bị nghi
rep = {"threshold": thr}
for post in ("sit", "walk"):
    mk = pva == post
    rep[f"FRR_{post}"] = float((p[mk & (yva == 0)] > thr).mean())
    rep[f"FAR_{post}"] = float((p[mk & (yva == 1)] <= thr).mean())
out = ROOT / "backend/app/models"
out.mkdir(exist_ok=True)
m.booster_.save_model(str(out / "owner_lgbm.txt"))
meta = {"features": keys, "threshold": thr, "target_frr": FRR, "seed": SEED,
        "trained_on": "StrokePIN (người thật, CC BY-NC-SA 4.0), PIN 6 số, KHÔNG dùng kích thước chạm; chia theo người",
        "status": "TẠM THỜI: dữ liệu công khai, chưa phải dữ liệu của đội; thiết bị khác nhau giữa người", "heldout_report": rep}
(out / "owner_lgbm.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(rep, indent=2), "| số đặc trưng:", len(keys))
