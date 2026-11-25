"""E21b (tiếp E21): thêm HỒ SƠ THEO CẶP PHÍM — so z trung bình của các cặp phím phổ biến có mặt ở cả câu đăng ký và câu thử (cùng ý tưởng phép đo tuyệt đối A của Gunetti & Picardi).

E21: chuẩn hoá nhịp theo CẶP PHÍM (digraph) có giúp nhận chủ khi câu thử khác câu đăng ký không?

Lý do: Innate Challenge đổi câu mỗi lần, mà thời gian giữa hai phím phụ thuộc cặp phím ("th" nhanh, "qx" chậm). E13 dùng log khoảng cách thô nên một phần
khác biệt là do NỘI DUNG câu. Ở đây trừ trung bình dân số của từng cặp phím (prior từ nhóm người riêng, không trùng nhóm đánh giá) rồi chia độ lệch chuẩn
(z = (log gap - mu_ab) / sd_ab), dự phòng theo lớp ký tự khi cặp hiếm. Cùng giao thức E13: đăng ký 3 câu, thử câu khác, cắt ở n phím đầu, co rút phương sai về dân số.
Ý tưởng cùng họ với phép đo tương đối của Gunetti & Picardi (TISSEC 2005) và việc TypeNet/TypeFormer học theo cặp phím.
Chỉ người thật, không có bot (dữ liệu bot của đội không có ký tự). Dữ liệu cần: research/data/aalto_note_keys.jsonl (aalto_note_chars.py; gitignored, có chữ cái câu mẫu).
Chạy: python experiments/e21_digraph_norm.py
"""
import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
NS, SEED, K, NU, BOOT, MINC = (10, 20, 30), 0, 3, 5, 80, 30
rng = random.Random(SEED)


def kc(ch):  # lớp ký tự dự phòng
    return "_" if ch.isspace() else "a" if ch.isalpha() else "o"


by_p = defaultdict(list)  # người -> [list (t, ch)]
for line in open(ROOT / "research/data/aalto_note_keys.jsonl"):
    r = json.loads(line)
    ks = [(e[0], e[3]) for e in r["events"] if e[1] == "key"]
    if len(ks) >= max(NS) + 1:
        by_p[r["participant"]].append(sorted(ks))
people = [p for p, v in by_p.items() if len(v) >= 8]
rng.shuffle(people)
prior_p, eval_p = people[:300], people[300:1300]
print(f"{len(people)} người; prior {len(prior_p)}, đánh giá {len(eval_p)}")

# thống kê cặp phím từ nhóm prior (khoảng cách tính trên các phím kề nhau, 20 ms .. 2 s)
pair, cls_pair = defaultdict(list), defaultdict(list)
for p in prior_p:
    for s in by_p[p]:
        for (t0, a), (t1, b) in zip(s, s[1:]):
            g = t1 - t0
            if 20 <= g <= 2000:
                pair[(a, b)].append(np.log(g)); cls_pair[(kc(a), kc(b))].append(np.log(g))
stat = {k: (np.mean(v), np.std(v) + 1e-6) for k, v in pair.items() if len(v) >= MINC}
cstat = {k: (np.mean(v), np.std(v) + 1e-6) for k, v in cls_pair.items()}
print(f"{len(stat)} cặp phím đủ mẫu (>= {MINC}); phủ {np.mean([ (a,b) in stat for s in by_p[prior_p[0]] for (_,a),(_,b) in zip(s,s[1:])]):.0%} cặp của một người prior")


def logs(s, n):
    return np.log(np.maximum(np.diff([t for t, _ in s[:n]]), 1.0))


def zs(s, n):
    out = []
    for (t0, a), (t1, b) in zip(s[:n], s[1:n]):
        mu, sd = stat.get((a, b)) or cstat[(kc(a), kc(b))]
        out.append((np.log(max(t1 - t0, 1.0)) - mu) / sd)
    return np.array(out)


def six(x):
    return [x.mean(), x.std(), np.median(x), np.percentile(x, 10), np.percentile(x, 90), np.abs(np.diff(x)).mean()]



from collections import Counter
TOPD = [d for d, _ in Counter((a, b) for p in prior_p for s in by_p[p] for (_, a), (_, b) in zip(s, s[1:])).most_common(40) if d in stat][:30]
print("cặp phổ biến:", "".join(a + b + " " for a, b in TOPD[:15]).replace("  ", "_ "))


def dz(s, n):
    """z theo từng cặp phổ biến trong n phím đầu: {cặp: trung bình z}"""
    acc = defaultdict(list)
    for (t0, a), (t1, b) in zip(s[:n], s[1:n]):
        if (a, b) in TOPD:
            acc[(a, b)].append((np.log(max(t1 - t0, 1.0)) - stat[(a, b)][0]) / stat[(a, b)][1])
    return {k: float(np.mean(v)) for k, v in acc.items()}


# độ lệch chuẩn trong-người của z theo cặp (từ nhóm prior), dùng làm thước đo
within = {}
for d in TOPD:
    vs = [np.var([x for s in by_p[p] for x in [dz(s, 60).get(d)] if x is not None], ddof=1) for p in prior_p
          if sum(dz(s, 60).get(d) is not None for s in by_p[p]) >= 3]
    within[d] = float(np.sqrt(np.mean(vs))) if vs else 1.0


def profile_dist(enr_profiles, test_p):
    ds = []
    for d, x in test_p.items():
        m = [pr[d] for pr in enr_profiles if d in pr]
        if m:
            ds.append(abs(x - np.mean(m)) / within[d])
    return (np.mean(ds), len(ds)) if ds else (None, 0)


def metrics(gen, imp):
    gen, imp = np.asarray(gen), np.asarray(imp)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 300)))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return np.array([(frr[i] + far[i]) / 2, (imp <= np.quantile(gen, 0.95)).mean()])


fe = lambda s, n: np.concatenate([six(logs(s, n)), six(zs(s, n))])  # noqa: E731
L = ["# E21b — thêm hồ sơ theo cặp phím phổ biến", "", "| Điểm | n phím | EER | FAR @ FRR 5% | số cặp chung trung bình |", "|---|---|---|---|---|"]
for n in NS:
    pv = np.mean([np.var(np.array([fe(s, n) for s in by_p[p]]), axis=0, ddof=1) for p in prior_p], axis=0)
    res = {"12 đặc trưng (E21)": {}, "chỉ hồ sơ cặp phím": {}, "12 đặc trưng + hồ sơ": {}}
    shared = []
    for p in eval_p:
        ss = by_p[p]; idx = list(range(len(ss))); rng.shuffle(idx)
        enr = np.array([fe(ss[i], n) for i in idx[:K]]); mu = enr.mean(0)
        sd = np.sqrt(((K - 1) * enr.var(0, ddof=1) + NU * pv) / (K - 1 + NU))
        eprof = [dz(ss[i], n) for i in idx[:K]]
        def sc(s):
            a = float(np.mean(np.abs(fe(s, n) - mu) / sd)); b, k = profile_dist(eprof, dz(s, n))
            return a, b, k
        gen = [sc(ss[i]) for i in idx[K:K + 5]]
        imp = [sc(rng.choice(by_p[q])) for q in rng.sample(eval_p, 12) if q != p]
        shared += [k for _, _, k in gen]
        for name, f in (("12 đặc trưng (E21)", lambda t: t[0]), ("chỉ hồ sơ cặp phím", lambda t: t[1] if t[1] is not None else 1.5),
                        ("12 đặc trưng + hồ sơ", lambda t: t[0] + (t[1] if t[1] is not None else 1.5))):
            res[name][p] = ([f(t) for t in gen], [f(t) for t in imp])
    for name, per in res.items():
        ps = sorted(per)
        est = metrics(sum((per[p][0] for p in ps), []), sum((per[p][1] for p in ps), []))
        bs = []
        for _ in range(BOOT):
            r = [rng.choice(ps) for _ in ps]
            bs.append(metrics(sum((per[p][0] for p in r), []), sum((per[p][1] for p in r), [])))
        lo, hi = np.quantile(bs, 0.025, axis=0), np.quantile(bs, 0.975, axis=0)
        L.append(f"| {name} | {n} | {est[0]:.3f} [{lo[0]:.3f}, {hi[0]:.3f}] | {est[1]:.3f} [{lo[1]:.3f}, {hi[1]:.3f}] | {np.mean(shared):.1f} |")
        print(L[-1], flush=True)
(ROOT / "research/results/e21b_digraph_profile.md").write_text("\n".join(L) + "\n", encoding="utf-8")
