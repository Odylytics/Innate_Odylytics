"""E10: co rút về dân số DÙNG ĐƯỢC KHI TRIỂN KHAI (StrokePIN, người thật).

E9 dùng prior riêng theo PIN: chạy thật thì không biết trước PIN của người dùng. Ở đây so:
  backend           : owner.py hiện tại (sd có sàn)
  E2 theo PIN       : prior phương sai trong-người của CÙNG PIN (cận trên, không triển khai được)
  E2 chung          : prior trung bình trên MỌI PIN của những người KHÁC (triển khai được)
  E2 chung + sàn    : như trên nhưng sd không thấp hơn sàn của owner.py
nu = trọng số của prior (số "mẫu ảo"). Chỉ dùng thời gian và lệch tâm (không kích thước chạm: đơn vị phụ thuộc thiết bị,
và web có thể chỉ trả 1). Đăng ký k=3 lượt; kiểm thử các lượt còn lại; kẻ gian biết PIN.
"""

import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, owner  # noqa: E402
import strokepin_loader  # noqa: E402

K, SEED, N_DRAW, N_IMP, BOOT = 3, 0, 5, 20, 100
SETS = {
    "thời gian": lambda k: k.startswith(("pin_hold_", "pin_flight_")) or k == "pin_total",
    "thời gian + lệch tâm": lambda k: k.startswith(("pin_hold_", "pin_flight_", "pin_dx_", "pin_dy_")) or k == "pin_total",
}
rng = random.Random(SEED)
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
KEYS = {n: sorted(k for k in S[0]["f"] if sel(k)) for n, sel in SETS.items()}
for e in S:
    e["v"] = {n: np.array([e["f"][k] for k in ks]) for n, ks in KEYS.items()}

grp = defaultdict(list)
for e in S:
    grp[(e["user"], e["pin"])].append(e)
by_pin = defaultdict(lambda: defaultdict(list))
for (u, p), es in grp.items():
    by_pin[p][u] += es

# phương sai trong-người theo (người, PIN); prior chung = trung bình trên người KHÁC
wv = {n: {g: np.var(np.array([e["v"][n] for e in es]), axis=0, ddof=1) for g, es in grp.items() if len(es) >= 2} for n in SETS}
tot = {n: sum(wv[n].values()) for n in SETS}
cnt = {n: len(wv[n]) for n in SETS}
user_sum = {n: defaultdict(lambda: 0) for n in SETS}
user_cnt = {n: defaultdict(int) for n in SETS}
for n in SETS:
    for (u, p), v in wv[n].items():
        user_sum[n][u] = user_sum[n][u] + v
        user_cnt[n][u] += 1


def prior_pooled(u, n):
    c = cnt[n] - user_cnt[n][u]
    return (tot[n] - user_sum[n][u]) / c


def prior_pin(u, p, n):
    vs = [np.var(np.array([e["v"][n] for e in es]), axis=0, ddof=1)
          for v, es in by_pin[p].items() if v != u and len(es) >= 2]
    return np.mean(vs, axis=0)


def detectors(n, X, pv_pin, pv_pool):
    keys, mu, k = KEYS[n], X.mean(0), len(X)
    floor = np.array([owner._floor(a, m) for a, m in zip(keys, mu)])
    s2 = X.var(0, ddof=1)

    def eb(pv, nu, use_floor):
        sd = np.sqrt(((k - 1) * s2 + nu * pv) / (k - 1 + nu))
        sd = np.maximum(sd, floor) if use_floor else sd
        return lambda x: (np.abs(x - mu) / sd).mean(-1)
    sd_backend = np.maximum(X.std(0, ddof=1), floor)
    is_off = np.array([a.startswith(("pin_dx_", "pin_dy_")) for a in keys])
    return {"backend (sd có sàn)": lambda x: (np.abs(x - mu) / sd_backend).mean(-1),
            "E2 theo PIN, nu=5 (cận trên)": eb(pv_pin, 5, False),
            "E2 chung, nu=5": eb(pv_pool, 5, False),
            "E2 chung, nu=10": eb(pv_pool, 10, False),
            "E2 chung + sàn, nu=5": eb(pv_pool, 5, True),
            "E2 chung + sàn, nu=10": eb(pv_pool, 10, True),
            # lai: co rút CHỈ cho thời gian, giữ sd có sàn cho lệch tâm (độ dao động lệch tâm khác nhau quá nhiều giữa người/thiết bị)
            **{f"LAI nu={nu}: E2 chung cho thời gian + sd có sàn cho lệch tâm": (lambda x, sd=np.where(is_off, sd_backend, np.sqrt(((k - 1) * s2 + nu * pv_pool) / (k - 1 + nu))): (np.abs(x - mu) / sd).mean(-1)) for nu in (3, 5, 10)}}


scores = defaultdict(lambda: defaultdict(lambda: ([], [])))
for (u, p), es in grp.items():
    if len(es) < K:
        continue
    for _ in range(N_DRAW):
        enr = rng.sample(es, K)
        gen_es = [e for e in es if e not in enr]
        if not gen_es:
            continue
        pool = [e for v, ves in by_pin[p].items() if v != u for e in ves]
        imp = rng.sample(pool, min(N_IMP, len(pool)))
        for n in SETS:
            X = np.array([e["v"][n] for e in enr])
            for dn, f in detectors(n, X, prior_pin(u, p, n), prior_pooled(u, n)).items():
                g, i = scores[(n, dn)][u]
                g += list(f(np.array([e["v"][n] for e in gen_es])))
                i += list(f(np.array([e["v"][n] for e in imp])))


def metrics(gen, imp):
    gen, imp = np.asarray(gen), np.asarray(imp)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 400)))
    frr = np.array([(gen > t).mean() for t in ths])
    far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return np.array([(frr[i] + far[i]) / 2, (imp <= np.quantile(gen, 0.95)).mean()])


def pooled(pu, us):
    return np.concatenate([pu[u][0] for u in us]), np.concatenate([pu[u][1] for u in us])


lines = ["# E10 — co rút về dân số dùng được khi triển khai (StrokePIN, người thật)", "",
         f"Đăng ký k={K} lượt; kẻ gian biết PIN; điểm gộp mọi cặp (người, PIN); CI 95% bootstrap theo người ({BOOT} lần). "
         "Cột dEER, dFAR là **chênh lệch ghép cặp so với backend hiện tại** (âm = tốt hơn). Không dùng kích thước chạm.", ""]
for n in SETS:
    lines += [f"## Bộ đặc trưng: {n}", "", "| Bộ phát hiện | EER | FAR @ FRR 5% | dEER so với backend | dFAR so với backend |", "|---|---|---|---|---|"]
    base = scores[(n, "backend (sd có sàn)")]
    us = sorted(base)
    resamples = [rng.choices(us, k=len(us)) for _ in range(BOOT)]
    mb = [metrics(*pooled(base, r)) for r in resamples]
    for (n2, dn), pu in scores.items():
        if n2 != n:
            continue
        est = metrics(*pooled(pu, us))
        mc = [metrics(*pooled(pu, r)) for r in resamples]
        d = np.array([a - b for a, b in zip(mc, mb)])
        dest = est - metrics(*pooled(base, us))
        lo, hi = np.quantile(d, 0.025, axis=0), np.quantile(d, 0.975, axis=0)
        lines.append(f"| {dn} | {est[0]:.3f} | {est[1]:.3f} | {dest[0]:+.3f} [{lo[0]:+.3f}, {hi[0]:+.3f}] | {dest[1]:+.3f} [{lo[1]:+.3f}, {hi[1]:+.3f}] |")
    lines.append("")
out = ROOT / "research/results/e10_deployable_prior.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
