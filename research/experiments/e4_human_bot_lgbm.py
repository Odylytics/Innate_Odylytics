"""E4: LightGBM cho bài "người hay máy", so với luật baseline, bằng đánh giá BỎ MỘT CHIẾN THUẬT.

Dữ liệu hoàn toàn GIẢ (người: attacker/tactics.synth_humans, bot: 4 chiến thuật của chính nhóm).
Vì vậy: (a) kiểm chứng đường ống và quy trình đánh giá, (b) cho thấy mô hình học gì và KHÔNG học được gì,
KHÔNG phải số liệu cho slide. Cần thay nguồn bằng phiên người thật và bot thật (adb, dispatchGesture).

Cách đánh giá:
  - ngưỡng chọn trên người ở tập validation sao cho 5% người bị nhầm là máy (FRR 5%), KHÔNG dùng bot của tập kiểm thử
  - "tất cả chiến thuật": huấn luyện thấy cả 4 chiến thuật (lạc quan)
  - "bỏ một chiến thuật": huấn luyện chỉ thấy 3, kiểm thử trên chiến thuật còn lại (thực tế hơn với bot lạ)
  - "không kích thước chạm": bỏ nhóm w/h, vì máy có thể không đo và bot thật đặt giá trị bất kỳ
  - kẻ tấn công dùng một kho người RIÊNG (không trùng tập huấn luyện/kiểm thử) cho chiến thuật 3, 4
"""

import random
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker")]
from app.scoring import bot_features, features, human  # noqa: E402
from nhip_attacker import tactics  # noqa: E402

PIN, SEEDS, FRR = "159357", (1, 2, 3), 0.05
N_H = {"train": 1500, "val": 600, "test": 1000, "pool": 400}
N_BOT = {"train": 400, "val": 150, "test": 300}  # mỗi chiến thuật
TACTICS = (1, 2, 3, 4)
ALL = bot_features.FEATURE_NAMES
NO_CONTACT = [n for n in ALL if n not in bot_features.CONTACT_FEATURES]


def humans(n, seed):
    return tactics.synth_humans(n, PIN, tactics.DEFAULT_LAYOUT, seed=seed)


def bots(t, n, pool, seed):
    rng = random.Random(seed)
    return [tactics.generate(t, "victim", PIN, pool, rng) for _ in range(n)]


def vec(sessions, names):
    return np.array([[bot_features.extract(s)[k] for k in names] for s in sessions], dtype=float)


def rule_score(sessions):
    return np.array([human.score(features.extract(s))[0] for s in sessions])


def build(seed):
    pool = humans(N_H["pool"], 1000 + seed)
    d = {"H": {}, "B": {t: {} for t in TACTICS}}
    for i, split in enumerate(("train", "val", "test")):
        d["H"][split] = humans(N_H[split], 10 * seed + i)
        for t in TACTICS:
            d["B"][t][split] = bots(t, N_BOT[split], pool, 100 * seed + 10 * t + i)
    return d


def fit_lgb(Xh, Xb, seed):
    X = np.vstack([Xh, Xb])
    y = np.r_[np.ones(len(Xh)), np.zeros(len(Xb))]  # 1 = người
    m = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=20, subsample=0.8,
                           subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, random_state=seed, verbose=-1)
    return m.fit(X, y)


def evaluate(d, seed):
    """-> {(mô hình, kịch bản): {chiến thuật: (tỷ lệ bắt, AUC), 'FRR': ...}}"""
    res = {}
    H = {s: d["H"][s] for s in d["H"]}
    for names, tag in ((ALL, ""), (NO_CONTACT, " (không kích thước chạm)")):
        feats = {("H", s): vec(H[s], names) for s in H}
        feats.update({(t, s): vec(d["B"][t][s], names) for t in TACTICS for s in ("train", "val", "test")})
        for scen, held in [("tất cả chiến thuật", None)] + [(f"bỏ chiến thuật {t}", t) for t in TACTICS]:
            train_t = [t for t in TACTICS if t != held]
            Xb = np.vstack([feats[(t, "train")] for t in train_t])
            m = fit_lgb(feats[("H", "train")], Xb, seed)
            iso = IsolationForest(n_estimators=200, random_state=seed).fit(feats[("H", "train")])
            scorers = {"LightGBM" + tag: lambda X, m=m: m.predict_proba(X)[:, 1],
                       "IsolationForest (chỉ người)" + tag: lambda X, iso=iso: iso.score_samples(X)}
            for name, sc in scorers.items():
                thr = np.quantile(sc(feats[("H", "val")]), FRR)  # flag nếu điểm < thr
                row = {"FRR": float((sc(feats[("H", "test")]) < thr).mean())}
                for t in (TACTICS if held is None else [held]):
                    s_b, s_h = sc(feats[(t, "test")]), sc(feats[("H", "test")])
                    row[t] = (float((s_b < thr).mean()), float(roc_auc_score(np.r_[np.ones(len(s_h)), np.zeros(len(s_b))],
                                                                               np.r_[s_h, s_b])))
                res[(name, scen)] = row
            # bộ kết hợp: cờ nếu LightGBM HOẶC IsolationForest cờ; mỗi mô hình ở FRR ~2,7% để hợp lại ~5%
            sl, si = scorers["LightGBM" + tag], scorers["IsolationForest (chỉ người)" + tag]
            tl, ti = (np.quantile(f(feats[("H", "val")]), 0.0267) for f in (sl, si))
            flag = lambda X: (sl(X) < tl) | (si(X) < ti)  # noqa: E731
            row = {"FRR": float(flag(feats[("H", "test")]).mean())}
            for t in (TACTICS if held is None else [held]):
                row[t] = (float(flag(feats[(t, "test")]).mean()), float("nan"))
            res[("Bộ kết hợp (LightGBM hoặc IsolationForest)" + tag, scen)] = row
    # luật baseline: không huấn luyện, nên chỉ có một kịch bản
    sv = rule_score(d["H"]["val"])
    thr = np.quantile(sv, FRR)
    # nhiều người điểm 1.0 -> ngưỡng có thể trùng; lật dấu bằng "<=" nếu thr == 1
    flag = (lambda s: s <= thr) if thr >= 1 else (lambda s: s < thr)
    sh = rule_score(d["H"]["test"])
    row = {"FRR": float(flag(sh).mean())}
    for t in TACTICS:
        sb = rule_score(d["B"][t]["test"])
        row[t] = (float(flag(sb).mean()), float(roc_auc_score(np.r_[np.ones(len(sh)), np.zeros(len(sb))], np.r_[sh, sb])))
    res[("Luật baseline (human.py)", "không huấn luyện")] = row
    return res


all_res = [evaluate(build(s), s) for s in SEEDS]
keys = list(all_res[0])
lines = ["# E4 — LightGBM cho bài người/máy (dữ liệu giả)", "",
         f"{len(SEEDS)} lần sinh dữ liệu độc lập, trung bình. Ngưỡng chọn trên người ở tập validation để FRR = {FRR:.0%}. "
         "Mỗi ô là **tỷ lệ bot bị bắt** (AUC trong ngoặc). Dữ liệu giả: chỉ kiểm chứng đường ống.", ""]
for scen in ("tất cả chiến thuật",):
    lines += [f"## Huấn luyện thấy cả 4 chiến thuật (lạc quan)", "", "| Mô hình | FRR thật | Chiến thuật 1 | 2 | 3 | 4 |", "|---|---|---|---|---|---|"]
    for k in keys:
        if k[1] not in (scen, "không huấn luyện"):
            continue
        r = [x[k] for x in all_res]
        cells = [f"{np.mean([x[t][0] for x in r]):.2f} ({np.mean([x[t][1] for x in r]):.2f})" for t in TACTICS]
        lines.append(f"| {k[0]} | {np.mean([x['FRR'] for x in r]):.3f} | " + " | ".join(cells) + " |")
lines += ["", "## Bỏ một chiến thuật khỏi huấn luyện, kiểm thử trên đúng chiến thuật đó (thực tế hơn với bot lạ)", "",
          "| Mô hình | FRR thật | Bỏ chiến thuật 1 | Bỏ 2 | Bỏ 3 | Bỏ 4 |", "|---|---|---|---|---|---|"]
for name in dict.fromkeys(k[0] for k in keys if k[1].startswith("bỏ")):
    cells, frr = [], []
    for t in TACTICS:
        r = [x[(name, f"bỏ chiến thuật {t}")] for x in all_res]
        cells.append(f"{np.mean([x[t][0] for x in r]):.2f} ({np.mean([x[t][1] for x in r]):.2f})")
        frr += [x["FRR"] for x in r]
    lines.append(f"| {name} | {np.mean(frr):.3f} | " + " | ".join(cells) + " |")

# độ quan trọng đặc trưng của mô hình đầy đủ (gain), để thấy mô hình dựa vào đâu
d = build(SEEDS[0])
Xh, Xb = vec(d["H"]["train"], ALL), np.vstack([vec(d["B"][t]["train"], ALL) for t in TACTICS])
m = fit_lgb(Xh, Xb, SEEDS[0])
gain = m.booster_.feature_importance("gain")
order = np.argsort(gain)[::-1][:8]
lines += ["", "## Mô hình dựa vào đặc trưng nào (gain, mô hình đầy đủ)", "", "| Đặc trưng | Tỷ trọng gain |", "|---|---|"]
lines += [f"| {ALL[i]} | {gain[i] / gain.sum():.2f} |" for i in order]
(ROOT / "research/models").mkdir(exist_ok=True)
m.booster_.save_model(str(ROOT / "research/models/human_lgbm_synthetic.txt"))
lines += ["", "Mô hình đầy đủ lưu ở `research/models/human_lgbm_synthetic.txt` (huấn luyện trên dữ liệu GIẢ, **không dùng cho bản nộp**).", ""]
(ROOT / "research/results/e4_human_bot_lgbm.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
