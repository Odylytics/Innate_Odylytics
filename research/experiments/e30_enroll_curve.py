"""E30: số lượt đăng ký k (2, 3, 4) và phân bố lỗi theo nạn nhân, nhận chủ bằng khoảng cách của backend (owner.py), StrokePIN.

StrokePIN chỉ có tối đa 5 lượt mỗi (người, PIN): k=4 để lại 1 lượt kiểm thử; k=1 không có độ lệch chuẩn (bỏ); k=5 không còn lượt kiểm thử.
Prior dân số: file population_prior.json của backend (tính từ một phần người, không loại riêng từng nạn nhân: có thể lạc quan nhẹ).
Kẻ gian = người khác nhập cùng PIN trên máy của họ (lẫn nhiễu thiết bị). Điểm = trung bình |z|; ngưỡng chung chọn để FRR 5%.
Gini theo nạn nhân: FAR của từng nạn nhân tại ngưỡng chung (Eberz 2017: trung bình che người "lọt mãi mãi").
Chạy (từ backend/): uv run --with pandas --with numpy --with scikit-learn --with lightgbm python ../research/experiments/e30_enroll_curve.py
"""
import random, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, owner  # noqa: E402
import strokepin_loader  # noqa: E402

rng = random.Random(30)
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
grp = defaultdict(list); by_pin = defaultdict(list)
for e in S:
    grp[(e["user"], e["pin"])].append(e); by_pin[e["pin"]].append(e)
USERS = sorted({u for u, _ in grp})


def dist(e, tpl):
    return float(np.mean([abs(v) for v in owner.score(e["f"], tpl)[1].values()]))


def eer_far(gen, imp):
    thr = np.quantile(gen, 0.95)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 400)))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths]); i = np.argmin(abs(frr - far))
    return (frr[i] + far[i]) / 2, thr


def gini(x):
    x = np.sort(np.asarray(x)); n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum())) if x.sum() else 0.0


L = ["# E30 — số lượt đăng ký và phân bố lỗi theo nạn nhân (StrokePIN, khoảng cách của backend)", "",
     "k=1 không tính được độ lệch chuẩn; k=5 không còn lượt kiểm thử (tối đa 5 lượt mỗi người–PIN). CI 95% bootstrap theo người. "
     "FAR@FRR5% dùng ngưỡng chung; cột Gini và 'nạn nhân FAR>90%' là theo từng nạn nhân (người chủ tài khoản).", "",
     "| k | EER | FAR@FRR5% | Gini FAR theo nạn nhân | nạn nhân FAR > 90% | trung vị FAR nạn nhân |", "|---|---|---|---|---|---|"]
for k in (2, 3, 4):
    G, I = defaultdict(list), defaultdict(list)
    for (u, p), es in grp.items():
        if len(es) < 5: continue
        for _ in range(5):
            enr = rng.sample(es, k); tpl = owner.build_template([e["f"] for e in enr])
            G[u] += [dist(e, tpl) for e in es if e not in enr]
            others = [e for e in by_pin[p] if e["user"] != u]
            I[u] += [dist(e, tpl) for e in rng.sample(others, min(15, len(others)))]
    def pooled(us): return np.concatenate([G[u] for u in us]), np.concatenate([I[u] for u in us])
    def metr(us):
        g, i = pooled(us); eer, thr = eer_far(g, i); return eer, float((i <= thr).mean())
    est = metr(USERS); bs = np.array([metr([USERS[rng.randrange(len(USERS))] for _ in USERS]) for _ in range(100)])
    g, i = pooled(USERS); thr = np.quantile(g, 0.95)
    far_u = np.array([(np.array(I[u]) <= thr).mean() for u in USERS])
    ci = lambda j: f"{est[j]:.3f} [{np.quantile(bs[:, j], .025):.3f}, {np.quantile(bs[:, j], .975):.3f}]"  # noqa: E731
    L.append(f"| {k} | {ci(0)} | {ci(1)} | {gini(far_u):.2f} | {(far_u > 0.9).sum()}/{len(USERS)} | {np.median(far_u):.2f} |")
    print(L[-1], flush=True)
Path(ROOT / "research/results/e30_enroll_curve.md").write_text("\n".join(L) + "\n", encoding="utf-8")
