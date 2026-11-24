"""E13: kiểm tra giả thuyết "Innate Challenge": gõ một câu (chữ + số) cho nhiều tín hiệu hơn nhập PIN 6 số.

Dữ liệu: nhịp gõ THẬT của người gõ câu trên điện thoại (Aalto; chỉ thời gian). Mỗi câu cắt ở n phím đầu, n = 6 (như PIN 6 số), 10, 20, 30;
mọi n dùng CÙNG các câu (>= 30 phím) để so công bằng. Đặc trưng nhịp: trung bình/độ lệch/trung vị/phân vị 10 và 90 của log khoảng cách giữa phím,
và độ lệch liên tiếp. Chỉ thời gian: không có thời gian giữ phím hay toạ độ (Aalto không có), nên KHÔNG so được số tuyệt đối với PIN StrokePIN.

(1) Xác minh chủ: đăng ký 3 câu, kiểm thử các câu còn lại, kẻ gian = câu của người khác; prior dân số từ nhóm người riêng; EER, FAR@FRR 5%, CI bootstrap theo người.
(2) Phát hiện bot gõ đều (CT2) và lấy mẫu dân số (CT4): AUC của LightGBM theo n (đã thấy loại bot), chia theo người.
Hạn chế: người CHÉP câu mẫu tiếng Anh, không phải soạn; bot giả; một dòng thời gian không có mã phím.
"""

import json
import random
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "attacker")]
from nhip_attacker import fields  # noqa: E402

NS, SEED, K, NU, BOOT = (6, 10, 20, 30), 0, 3, 5, 80
rng = random.Random(SEED)
recs = [json.loads(l) for l in open(ROOT / "research/data/aalto_note_events.jsonl")]


def keys_t(ev):
    return sorted(e[0] for e in ev if e[1] == "key")


def feats(ts, n):
    g = np.maximum(np.diff(ts[:n]), 1.0)
    lg = np.log(g)
    return np.array([lg.mean(), lg.std(), np.median(lg), np.percentile(lg, 10), np.percentile(lg, 90), np.abs(np.diff(lg)).mean()])


by_p = {}
for r in recs:
    ts = keys_t(r["events"])
    if len(ts) >= max(NS) + 1:
        by_p.setdefault(r["participant"], []).append(ts)
people = [p for p, v in by_p.items() if len(v) >= 8]
rng.shuffle(people)
prior_p, eval_p = people[:300], people[300:1300]
print(f"{len(people)} người có >= 8 câu (>= {max(NS)+1} phím); prior {len(prior_p)}, đánh giá {len(eval_p)}")


def metrics(gen, imp):
    gen, imp = np.asarray(gen), np.asarray(imp)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 300)))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return np.array([(frr[i] + far[i]) / 2, (imp <= np.quantile(gen, 0.95)).mean()])


L = ["# E13 — giả thuyết \"Innate Challenge\": nhiều ký tự hơn thì nhận chủ và bắt bot tốt hơn?", "",
     "Người thật gõ câu trên điện thoại (Aalto), chỉ thời gian. Mỗi câu cắt ở n phím đầu (n = 6 tương đương độ dài PIN 6 số). Mọi n dùng cùng các câu. "
     "**Không so được số tuyệt đối với StrokePIN** (khác dữ liệu, khác phép đo: ở đây không có thời gian giữ phím và toạ độ).", "",
     "## (1) Xác minh chủ theo số phím", "", "| Số phím n | EER | FAR @ FRR 5% |", "|---|---|---|"]
verify = {}
for n in NS:
    pv = np.mean([np.var(np.array([feats(t, n) for t in by_p[p]]), axis=0, ddof=1) for p in prior_p], axis=0)
    per = {}
    for p in eval_p:
        ss = by_p[p]
        idx = list(range(len(ss))); rng.shuffle(idx)
        enr = np.array([feats(ss[i], n) for i in idx[:K]])
        mu = enr.mean(0)
        sd = np.sqrt(((K - 1) * enr.var(0, ddof=1) + NU * pv) / (K - 1 + NU))
        score = lambda f: float(np.mean(np.abs(f - mu) / sd))  # noqa: E731
        gen = [score(feats(ss[i], n)) for i in idx[K:K + 5]]
        imp = []
        for q in rng.sample(eval_p, 12):
            if q != p:
                imp.append(score(feats(rng.choice(by_p[q]), n)))
        per[p] = (gen, imp)
    ps = sorted(per)
    est = metrics(sum((per[p][0] for p in ps), []), sum((per[p][1] for p in ps), []))
    bs = []
    for _ in range(BOOT):
        r = [rng.choice(ps) for _ in ps]
        bs.append(metrics(sum((per[p][0] for p in r), []), sum((per[p][1] for p in r), [])))
    lo, hi = np.quantile(bs, 0.025, axis=0), np.quantile(bs, 0.975, axis=0)
    verify[n] = est
    L.append(f"| {n} | {est[0]:.3f} [{lo[0]:.3f}, {hi[0]:.3f}] | {est[1]:.3f} [{lo[1]:.3f}, {hi[1]:.3f}] |")

# (2) bot gõ đều (CT2) và lấy mẫu dân số (CT4), AUC theo n (LightGBM đã thấy loại bot đó)
pool_sessions = [{"fields": [{"name": "note", "events": [{"t": t, "kind": "key", "n": 1, "cls": "letter"} for t in by_p[p][0]]}]} for p in prior_p]
L += ["", "## (2) Phát hiện bot trên câu gõ theo số phím (AUC; LightGBM đã thấy loại bot, chia theo người)", "", "| Số phím n | CT2 gõ đều | CT4 lấy mẫu dân số |", "|---|---|---|"]
train_p, test_p = eval_p[:600], eval_p[600:]
for n in NS:
    res = {}
    for t in (2, 4):
        def bots(m):
            out = []
            while len(out) < m:
                ev = [f for f in fields.for_tactic(t, rng, pool_sessions, None) if f["name"] == "note"]
                ts = sorted(e["t"] for f in ev for e in f["events"] if e["kind"] == "key")
                if len(ts) >= n + 1:
                    out.append(ts)
            return out
        Xh = lambda ps: np.array([feats(rng.choice(by_p[p]), n) for p in ps for _ in range(3)])  # noqa: E731
        Xtr = np.vstack([Xh(train_p), np.array([feats(b, n) for b in bots(1500)])])
        ytr = np.r_[np.ones(len(train_p) * 3), np.zeros(1500)]
        Xte = np.vstack([Xh(test_p), np.array([feats(b, n) for b in bots(1000)])])
        yte = np.r_[np.ones(len(test_p) * 3), np.zeros(1000)]
        m = lgb.LGBMClassifier(n_estimators=150, learning_rate=0.05, num_leaves=7, min_child_samples=20, random_state=SEED, verbose=-1).fit(Xtr, ytr)
        res[t] = roc_auc_score(yte, m.predict_proba(Xte)[:, 1])
    L.append(f"| {n} | {res[2]:.3f} | {res[4]:.3f} |")
(ROOT / "research/results/e13_length_effect.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
