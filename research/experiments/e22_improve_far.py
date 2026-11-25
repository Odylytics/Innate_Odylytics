"""E22: những cách giảm FAR (kẻ lạ lọt) cho Innate Challenge, đo trên Aalto (1.000 người đánh giá, 30 phím, câu thử khác câu đăng ký, giao thức E13).

(a) số câu đăng ký K = 1, 3, 5, 8;  (b) thêm tín hiệu tư thế cầm máy (góc nghiêng beta/gamma: trung bình, độ lệch) — LẠC QUAN vì mọi câu của một người
nằm trong MỘT buổi nên tư thế trùng giữa đăng ký và thử (không tách theo thời gian được); trên điện thoại thật là cảm biến cần xin quyền, iOS Safari cần cấp quyền, và là dữ liệu nhạy cảm;
(c) thay "trung bình |z|" bằng mô hình học (LightGBM trên vector lệch, huấn luyện ở nhóm người riêng, không trùng nhóm đánh giá).
Dữ liệu: research/data/aalto_note_orient.jsonl (aalto_note_orient.py; gitignored). Chạy: python experiments/e22_improve_far.py
"""
import json
import random
from collections import defaultdict
from pathlib import Path

import lightgbm as lgb
import numpy as np

ROOT = Path(__file__).parents[2]
N, SEED, NU, BOOT, MINC = 30, 0, 5, 60, 30
rng = random.Random(SEED)


def kc(ch):
    return "_" if ch.isspace() else "a" if ch.isalpha() else "o"


by_p = defaultdict(list)
for line in open(ROOT / "research/data/aalto_note_orient.jsonl"):
    r = json.loads(line)
    ks = [(e[0], e[3], e[4], e[5]) for e in r["events"] if e[1] == "key"]
    if len(ks) >= N + 1 and all(k[2] is not None and k[3] is not None for k in ks[:N]):
        by_p[r["participant"]].append(sorted(ks))
people = [p for p, v in by_p.items() if len(v) >= 10]
rng.shuffle(people)
prior_p, train_p, eval_p = people[:250], people[250:650], people[650:1650]
print(f"{len(people)} người đủ điều kiện (>= 10 câu); prior {len(prior_p)}, huấn luyện {len(train_p)}, đánh giá {len(eval_p)}")

pair, cls_pair = defaultdict(list), defaultdict(list)
for p in prior_p:
    for s in by_p[p]:
        for (t0, a, *_), (t1, b, *_) in zip(s, s[1:]):
            g = t1 - t0
            if 20 <= g <= 2000:
                pair[(a, b)].append(np.log(g)); cls_pair[(kc(a), kc(b))].append(np.log(g))
stat = {k: (np.mean(v), np.std(v) + 1e-6) for k, v in pair.items() if len(v) >= MINC}
cstat = {k: (np.mean(v), np.std(v) + 1e-6) for k, v in cls_pair.items()}


def six(x):
    return [x.mean(), x.std(), np.median(x), np.percentile(x, 10), np.percentile(x, 90), np.abs(np.diff(x)).mean()]


def f_time(s):
    return np.array(six(np.log(np.maximum(np.diff([k[0] for k in s[:N]]), 1.0))))


def f_time_z(s):
    z = []
    for (t0, a, *_), (t1, b, *_) in zip(s[:N], s[1:N]):
        mu, sd = stat.get((a, b)) or cstat[(kc(a), kc(b))]
        z.append((np.log(max(t1 - t0, 1.0)) - mu) / sd)
    return np.concatenate([f_time(s), six(np.array(z))])


def f_orient(s):
    b = np.array([k[2] for k in s[:N]]); g = np.array([k[3] for k in s[:N]])
    return np.array([b.mean(), b.std(), g.mean(), g.std()])


FE = {"thô (6, như E13)": f_time, "thô + chuẩn hoá cặp phím (12)": f_time_z,
      "12 + tư thế cầm máy (16)": lambda s: np.concatenate([f_time_z(s), f_orient(s)])}
cache = {}


def feats(name, s):
    k = (name, id(s))
    if k not in cache:
        cache[k] = FE[name](s)
    return cache[k]


def metrics(gen, imp):
    gen, imp = np.asarray(gen), np.asarray(imp)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 300)))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return np.array([(frr[i] + far[i]) / 2, (imp <= np.quantile(gen, 0.95)).mean()])


def prior_var(name):
    return np.mean([np.var(np.array([feats(name, s) for s in by_p[p]]), axis=0, ddof=1) for p in prior_p], axis=0)


def deviations(name, K, pv, people_, n_imp, learned_rows=False):
    """-> {người: (vector lệch của câu thật [m, d], của câu kẻ gian [n, d])}"""
    out = {}
    for p in people_:
        ss = by_p[p]; idx = list(range(len(ss))); rng.shuffle(idx)
        enr = np.array([feats(name, ss[i]) for i in idx[:K]]); mu = enr.mean(0)
        sd = np.sqrt((max(K - 1, 0) * (enr.var(0, ddof=1) if K > 1 else 0) + NU * pv) / (max(K - 1, 0) + NU))
        dev = lambda s: np.abs(feats(name, s) - mu) / sd  # noqa: E731
        gen = np.array([dev(ss[i]) for i in idx[K:K + 5]])
        imp = np.array([dev(rng.choice(by_p[q])) for q in rng.sample(people_, n_imp + 1) if q != p][:n_imp])
        out[p] = (gen, imp)
    return out


def report(label, scores):
    ps = sorted(scores)
    est = metrics(np.concatenate([scores[p][0] for p in ps]), np.concatenate([scores[p][1] for p in ps]))
    bs = []
    for _ in range(BOOT):
        r = [rng.choice(ps) for _ in ps]
        bs.append(metrics(np.concatenate([scores[p][0] for p in r]), np.concatenate([scores[p][1] for p in r])))
    lo, hi = np.quantile(bs, 0.025, axis=0), np.quantile(bs, 0.975, axis=0)
    line = f"| {label} | {est[0]:.3f} [{lo[0]:.3f}, {hi[0]:.3f}] | {est[1]:.3f} [{lo[1]:.3f}, {hi[1]:.3f}] |"
    print(line, flush=True)
    return line


L = ["# E22 — các cách giảm FAR ở 30 phím (Aalto, người thật; câu thử khác câu đăng ký)", "",
     "| Cấu hình | EER | FAR @ FRR 5% |", "|---|---|---|"]
for name in FE:
    pv = prior_var(name)
    for K in (3,) if "tư thế" not in name and "chuẩn" in name else (1, 3, 5, 8) if name.startswith("thô (6") else (3,):
        d = deviations(name, K, pv, eval_p, 12)
        L.append(report(f"{name}, K={K} câu đăng ký", {p: (g.mean(1), i.mean(1)) for p, (g, i) in d.items()}))

# (c) mô hình học trên vector lệch, bộ 12 đặc trưng, K=3
name = "thô + chuẩn hoá cặp phím (12)"; pv = prior_var(name)
tr = deviations(name, 3, pv, train_p, 20)
X = np.vstack([np.vstack([g, i]) for g, i in tr.values()]); y = np.concatenate([np.r_[np.ones(len(g)), np.zeros(len(i))] for g, i in tr.values()])
m = lgb.train({"objective": "binary", "learning_rate": 0.05, "num_leaves": 7, "min_data_in_leaf": 30, "seed": SEED, "verbose": -1}, lgb.Dataset(X, y), 200)
d = deviations(name, 3, pv, eval_p, 12)
L.append(report(f"{name}, K=3, mô hình học (LightGBM)", {p: (-m.predict(g), -m.predict(i)) for p, (g, i) in d.items()}))
(ROOT / "research/results/e22_improve_far.md").write_text("\n".join(L) + "\n", encoding="utf-8")
