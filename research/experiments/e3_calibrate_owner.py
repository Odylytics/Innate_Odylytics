"""E3: hiệu chỉnh ánh xạ khoảng cách -> điểm chủ của owner.py trên PIN thật (StrokePIN).

Dùng đúng owner.build_template/score. Đăng ký 3 lượt; chủ = các lượt còn lại; kẻ gian biết PIN = người khác, cùng PIN.
Chia người làm hai nửa: fit Platt (a,b) trên nửa A, kiểm trên nửa B (không rò người). So ánh xạ hiện tại (d=2 -> 0,5).
"""
import math, random, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, owner  # noqa: E402
import strokepin_loader  # noqa: E402

rng = random.Random(0)
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
grp = defaultdict(list)
for e in S:
    grp[(e["user"], e["pin"])].append(e)
by_pin = defaultdict(list)
for (u, p), es in grp.items():
    by_pin[p] += [(u, e) for e in es]
users = sorted({u for u, _ in grp})
rng.shuffle(users)
half = {u: i % 2 for i, u in enumerate(users)}
rows = []  # (half, label, d)
for (u, p), es in grp.items():
    if len(es) < 5:
        continue
    enr = rng.sample(es, 3)
    tpl = owner.build_template([e["f"] for e in enr])
    def d(e):
        _, z = owner.score(e["f"], tpl)
        return float(np.mean([abs(v) for v in z.values()]))
    for e in es:
        if e not in enr:
            rows.append((half[u], 1, d(e)))
    imps = [e for v, e in by_pin[p] if v != u]
    for e in rng.sample(imps, min(20, len(imps))):
        rows.append((half[u], 0, d(e)))
R = np.array(rows)
def fit(x, y):  # Platt bằng gradient, không phụ thuộc sklearn
    a, b = -1.0, 2.0
    for _ in range(4000):
        p = 1 / (1 + np.exp(-(a * x + b)))
        w = np.where(y == 1, 0.5 / y.mean(), 0.5 / (1 - y.mean()))  # cân bằng lớp: chủ và kẻ gian nặng ngang nhau
        a -= 0.05 * (w * (p - y) * x).mean(); b -= 0.05 * (w * (p - y)).mean()
    return a, b
A, B = R[R[:, 0] == 0], R[R[:, 0] == 1]
a, b = fit(A[:, 2], A[:, 1])
sig = lambda x, a, b: 1 / (1 + np.exp(-(a * x + b)))
old = lambda x: 1 / (1 + np.exp(np.minimum(2 * (x - 2), 700)))
out = [f"# E3 — hiệu chỉnh điểm chủ (StrokePIN, PIN 6 số, đăng ký 3 lượt)", "",
       f"Fit Platt trên nửa A ({len(A)} phiên): score = sigmoid({a:.3f}·d + {b:.3f}). Kiểm trên nửa B ({len(B)} phiên, người khác hẳn).", "",
       "| Ánh xạ | Chủ có score ≥ 0,5 | Kẻ gian biết PIN có score ≥ 0,5 |", "|---|---|---|"]
for name, f in (("hiện tại (d=2→0,5)", old), (f"Platt đã fit (cân bằng lớp)", lambda x: sig(x, a, b))):
    s = f(B[:, 2]); g, i = s[B[:, 1] == 1], s[B[:, 1] == 0]
    out.append(f"| {name} | {(g >= .5).mean():.2f} | {(i >= .5).mean():.2f} |")
g = B[B[:, 1] == 1, 2]; i = B[B[:, 1] == 0, 2]
t = np.quantile(g, 0.95)
out += ["", f"Ngưỡng d cho FRR 5% (nửa B): d={t:.2f}; FAR tại đó = {(i <= t).mean():.2f}. Trung vị d: chủ {np.median(g):.2f}, kẻ gian {np.median(i):.2f}.",
        "", "Kết luận: xem số trên. Platt chỉ dời ngưỡng, không tạo thêm độ tách; FAR@FRR5% vẫn quyết bởi đặc trưng (E9/E12b)."]
Path(ROOT / "research/results/e3_calibrate_owner.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
