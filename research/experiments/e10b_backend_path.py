"""E10b: kiểm tra CHÍNH owner.build_template/owner.score của backend (có co rút) trên StrokePIN, prior bỏ-một-người.

So `owner._PRIOR` = prior bỏ-một-người (bật) với `{}` (tắt, hành vi cũ), CÙNG các lượt đăng ký và kiểm thử.
Dùng mọi đặc trưng nhận dạng như backend thật (thời gian + lệch tâm + kích thước chạm). k=3, kẻ gian biết PIN.
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
rng = random.Random(SEED)
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
TK = sorted(k for k in S[0]["f"] if k.startswith(("pin_hold_", "pin_flight_")) or k == "pin_total")
grp, bpp = defaultdict(list), defaultdict(lambda: defaultdict(list))
for e in S:
    grp[(e["user"], e["pin"])].append(e)
    bpp[e["pin"]][e["user"]].append(e)
wv = {g: np.var(np.array([[e["f"][k] for k in TK] for e in es]), axis=0, ddof=1) for g, es in grp.items() if len(es) >= 2}
tot, cnt = sum(wv.values()), len(wv)
us_sum, us_cnt = defaultdict(lambda: 0), defaultdict(int)
for (u, _p), v in wv.items():
    us_sum[u] = us_sum[u] + v
    us_cnt[u] += 1
ON = lambda u: {"within_var": dict(zip(TK, ((tot - us_sum[u]) / (cnt - us_cnt[u])).tolist())), "n_taps": 6, "nu": 5}  # noqa: E731


def dist(f, tpl):
    return float(np.mean([abs(v) for v in owner.score(f, tpl)[1].values()]))


res = defaultdict(lambda: defaultdict(lambda: ([], [])))  # chế độ[user] = (gen, imp)
for (u, p), es in grp.items():
    if len(es) < K:
        continue
    for _ in range(N_DRAW):
        enr = rng.sample(es, K)
        gen = [e for e in es if e not in enr]
        if not gen:
            continue
        pool = [e for v, ves in bpp[p].items() if v != u for e in ves]
        imp = rng.sample(pool, min(N_IMP, len(pool)))
        for mode, prior in (("tắt (hành vi cũ)", {}), ("bật (co rút thời gian)", ON(u))):
            owner._PRIOR = prior
            tpl = owner.build_template([e["f"] for e in enr])
            g, i = res[mode][u]
            g += [dist(e["f"], tpl) for e in gen]
            i += [dist(e["f"], tpl) for e in imp]


def metrics(gen, imp):
    gen, imp = np.asarray(gen), np.asarray(imp)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 400)))
    frr = np.array([(gen > t).mean() for t in ths])
    far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return np.array([(frr[i] + far[i]) / 2, (imp <= np.quantile(gen, 0.95)).mean()])


def pooled(pu, us):
    return np.concatenate([pu[u][0] for u in us]), np.concatenate([pu[u][1] for u in us])


lines = ["# E10b — chính `owner.py` của backend trên StrokePIN (prior bỏ-một-người)", "",
         f"k={K} lượt đăng ký, kẻ gian biết PIN, mọi đặc trưng nhận dạng như backend thật. CI 95% bootstrap theo người ({BOOT} lần). "
         "Hàng cuối mỗi bảng là chênh lệch ghép cặp (bật trừ tắt; âm = tốt hơn).", ""]
off, on = res["tắt (hành vi cũ)"], res["bật (co rút thời gian)"]
us = sorted(off)
rs = [rng.choices(us, k=len(us)) for _ in range(BOOT)]
mo, mn = [metrics(*pooled(off, r)) for r in rs], [metrics(*pooled(on, r)) for r in rs]
d = np.array([b - a for a, b in zip(mo, mn)])
e_off, e_on = metrics(*pooled(off, us)), metrics(*pooled(on, us))
lo, hi = np.quantile(d, 0.025, axis=0), np.quantile(d, 0.975, axis=0)
lines += ["| Co rút | EER | FAR @ FRR 5% |", "|---|---|---|",
          f"| tắt (hành vi cũ) | {e_off[0]:.3f} | {e_off[1]:.3f} |", f"| bật (co rút thời gian) | {e_on[0]:.3f} | {e_on[1]:.3f} |",
          f"| **chênh lệch ghép cặp** | {e_on[0]-e_off[0]:+.3f} [{lo[0]:+.3f}, {hi[0]:+.3f}] | {e_on[1]-e_off[1]:+.3f} [{lo[1]:+.3f}, {hi[1]:+.3f}] |", ""]
(ROOT / "research/results/e10b_backend_path.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
