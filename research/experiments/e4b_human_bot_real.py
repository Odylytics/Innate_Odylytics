"""E4b: bài "người hay máy" với NGƯỜI THẬT (StrokePIN) và bot do bộ sinh tạo, đánh giá bỏ-một-chiến-thuật.

Khác E4 (người giả): người là phiên PIN thật. Bot vẫn là 4 chiến thuật của nhóm (attacker/tactics.py) nhưng dựng
trên PIN thật và phân bố của người thật (chiến thuật 3 phát lại một phiên người thật, 4 lấy mẫu từ dân số thật).
Chia theo NGƯỜI (không người nào xuất hiện ở hai tập): train / val / test / kho của kẻ tấn công.
Chỉ so phần PIN: StrokePIN không có vuốt/màn hình, nên bot cũng bị bỏ vuốt/màn hình (nếu không, bot khác người ở chỗ không liên quan).
FRR thật trên người ở tập test có thể lệch 5% vì người test dùng thiết bị khác người validation: đó là kết quả, không phải lỗi.
Hạn chế: bot vẫn là giả. Chưa có bot thật (adb, dispatchGesture).
"""

import random
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker"), str(Path(__file__).parent)]
from app.scoring import bot_features, features, human  # noqa: E402
from nhip_attacker import tactics  # noqa: E402
import strokepin_loader  # noqa: E402

SEEDS, FRR, TACTICS = (1, 2, 3), 0.05, (1, 2, 3, 4)
N_H = {"train": 3000, "val": 1000, "test": 3000, "pool": 400}
N_BOT = {"train": 500, "val": 150, "test": 400}
ALL = bot_features.FEATURE_NAMES
NO_CONTACT = [n for n in ALL if n not in bot_features.CONTACT_FEATURES]

S = strokepin_loader.load()
USERS = sorted({e["user"] for e in S})
PINS = sorted({e["pin"] for e in S})


def clean(sess):
    return {**sess, "swipes": [], "screens": []}


def build(seed):
    rng = random.Random(seed)
    us = USERS[:]
    rng.shuffle(us)
    split = {"train": us[:40], "val": us[40:52], "test": us[52:82], "pool": us[82:]}
    H = {}
    for k, v in split.items():
        pool = [e["session"] for e in S if e["user"] in set(v)]
        H[k] = rng.sample(pool, min(N_H[k], len(pool)))
    d = {"H": H, "B": {t: {} for t in TACTICS}}
    for t in TACTICS:
        for k in ("train", "val", "test"):
            d["B"][t][k] = [clean(tactics.generate(t, "victim", rng.choice(PINS), H["pool"], rng)) for _ in range(N_BOT[k])]
    return d


def vec(sessions, names):
    return np.array([[bot_features.extract(s)[k] for k in names] for s in sessions], dtype=float)


def rule_score(sessions):
    return np.array([human.score(features.extract(s))[0] for s in sessions])


def fit_lgb(Xh, Xb, seed):
    X, y = np.vstack([Xh, Xb]), np.r_[np.ones(len(Xh)), np.zeros(len(Xb))]
    return lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=20, subsample=0.8,
                              subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, random_state=seed, verbose=-1).fit(X, y)


def metrics(sc, thr, hum, bots):
    out = {"FRR": float((sc(hum) < thr).mean())}
    for t, X in bots.items():
        sb = sc(X)
        out[t] = (float((sb < thr).mean()), float(roc_auc_score(np.r_[np.ones(len(hum)), np.zeros(len(sb))], np.r_[sc(hum), sb])))
    return out


def evaluate(d, seed):
    res = {}
    for names, tag in ((ALL, ""), (NO_CONTACT, " (không kích thước chạm)")):
        F = {("H", k): vec(d["H"][k], names) for k in ("train", "val", "test")}
        F.update({(t, k): vec(d["B"][t][k], names) for t in TACTICS for k in ("train", "val", "test")})
        for scen, held in [("tất cả chiến thuật", None)] + [(f"bỏ chiến thuật {t}", t) for t in TACTICS]:
            tr = [t for t in TACTICS if t != held]
            m = fit_lgb(F[("H", "train")], np.vstack([F[(t, "train")] for t in tr]), seed)
            iso = IsolationForest(n_estimators=200, random_state=seed).fit(F[("H", "train")])
            sl, si = (lambda X, m=m: m.predict_proba(X)[:, 1]), (lambda X, iso=iso: iso.score_samples(X))
            test_b = {t: F[(t, "test")] for t in (TACTICS if held is None else [held])}
            for name, sc in (("LightGBM" + tag, sl), ("IsolationForest (chỉ người)" + tag, si)):
                res[(name, scen)] = metrics(sc, np.quantile(sc(F[("H", "val")]), FRR), F[("H", "test")], test_b)
            tl, ti = (np.quantile(f(F[("H", "val")]), 0.0267) for f in (sl, si))
            ens = lambda X: np.where((sl(X) < tl) | (si(X) < ti), 0.0, 1.0)  # noqa: E731
            res[("Bộ kết hợp" + tag, scen)] = metrics(ens, 0.5, F[("H", "test")], test_b)
    sv = rule_score(d["H"]["val"])
    thr = np.quantile(sv, FRR)
    sh = rule_score(d["H"]["test"])
    flag = (lambda s: s <= thr) if thr >= 1 else (lambda s: s < thr)
    row = {"FRR": float(flag(sh).mean())}
    for t in TACTICS:
        sb = rule_score(d["B"][t]["test"])
        row[t] = (float(flag(sb).mean()), float(roc_auc_score(np.r_[np.ones(len(sh)), np.zeros(len(sb))], np.r_[sh, sb])))
    res[("Luật baseline (human.py)", "không huấn luyện")] = row
    return res


all_res = [evaluate(build(s), s) for s in SEEDS]
keys = list(all_res[0])


def cell(r, t):
    return f"{np.mean([x[t][0] for x in r]):.2f}" + ("" if np.isnan(np.mean([x[t][1] for x in r])) else f" ({np.mean([x[t][1] for x in r]):.2f})")


lines = ["# E4b — người/máy với NGƯỜI THẬT (StrokePIN) và bot do bộ sinh tạo", "",
         f"{len(SEEDS)} cách chia người khác nhau (train 40 / val 12 / test 30 / kho kẻ tấn công 15 người, không trùng người). "
         f"Ngưỡng chọn để FRR = {FRR:.0%} trên người ở tập validation. Mỗi ô: **tỷ lệ bot bị bắt** (AUC). "
         "Chỉ so phần PIN. Bot vẫn là giả.", "",
         "## Huấn luyện thấy cả 4 chiến thuật", "", "| Mô hình | FRR thật (người test) | CT1 | CT2 | CT3 | CT4 |", "|---|---|---|---|---|---|"]
for k in keys:
    if k[1] not in ("tất cả chiến thuật", "không huấn luyện"):
        continue
    r = [x[k] for x in all_res]
    lines.append(f"| {k[0]} | {np.mean([x['FRR'] for x in r]):.3f} | " + " | ".join(cell(r, t) for t in TACTICS) + " |")
lines += ["", "## Bỏ đúng một chiến thuật khỏi huấn luyện, kiểm thử trên chiến thuật đó (bot lạ)", "",
          "| Mô hình | FRR thật | Bỏ CT1 | Bỏ CT2 | Bỏ CT3 | Bỏ CT4 |", "|---|---|---|---|---|---|"]
for name in dict.fromkeys(k[0] for k in keys if k[1].startswith("bỏ")):
    cells, frr = [], []
    for t in TACTICS:
        r = [x[(name, f"bỏ chiến thuật {t}")] for x in all_res]
        cells.append(cell(r, t))
        frr += [x["FRR"] for x in r]
    lines.append(f"| {name} | {np.mean(frr):.3f} | " + " | ".join(cells) + " |")
(ROOT / "research/results/e4b_human_bot_real.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
