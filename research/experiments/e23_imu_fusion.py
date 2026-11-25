"""E23 (từ E9): thêm CHUYỂN ĐỘNG điện thoại (cảm biến StrokePIN) vào nhận chủ. Cùng giao thức E9; đặc trưng imu_* = trọng lực trung bình/độ lệch (cách cầm), độ rung gia tốc và con quay (độ vững tay). StrokePIN lấy mẫu gia tốc/con quay chỉ ~5 Hz, trọng lực ~50 Hz: KHÔNG đủ để đo cú giật tại thời điểm chạm.

E9: xác minh chủ trên PIN điện thoại THẬT (StrokePIN), dùng chính features.py / owner.py của backend.

Mỗi cặp (người, PIN): đăng ký bằng k lượt NGỒI ngẫu nhiên. Kiểm thử:
  - chủ, cùng tư thế (các lượt ngồi còn lại) hoặc đổi tư thế (các lượt ĐI)
  - kẻ gian BIẾT PIN: lượt của người khác nhập cùng PIN, cùng tư thế với phiên kiểm thử (kịch bản B)
Điểm = khoảng cách chuẩn hoá (thấp = giống chủ). Gộp điểm mọi cặp rồi tính EER và FAR@FRR 5%; CI bootstrap theo người.
Ba bộ đặc trưng (thời gian / + lệch tâm / + kích thước chạm) x ba bộ phát hiện:
  backend (owner.py hiện tại: sd có sàn), Manhattan scaled (Killourhy & Maxion), E2 (co rút phương sai về dân số).
Không có bot ở đây: đây là bài "có phải chủ", dữ liệu người thật nhưng một máy mỗi người (thiết bị khác nhau giữa người).
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

KS, SEED, N_DRAW, N_IMP, BOOT, NU = (3, 5), 0, 5, 20, 100, 5
PIN_SET = lambda k: k.startswith(("pin_hold_", "pin_flight_", "pin_dx_", "pin_dy_")) or k == "pin_total"  # noqa: E731
SETS = {"PIN (thời gian + lệch tâm)": PIN_SET, "chỉ chuyển động (IMU)": lambda k: k.startswith("imu_"),
        "PIN + chuyển động (IMU)": lambda k: PIN_SET(k) or k.startswith("imu_")}
rng = random.Random(SEED)
S = strokepin_loader.load()
import pandas as pd  # noqa: E402


def imu_features(user):
    d = pd.read_csv(ROOT / f"research/data/StrokePIN/{user}_sensor.csv", usecols=["SensorType", "X", "Y", "Z", "Sample ID"])
    out = {}
    for sid, g in d.groupby("Sample ID"):
        f = {}
        gr = g[g.SensorType == "Gravity"][["X", "Y", "Z"]].to_numpy()
        for name, arr in (("accelerometer", g[g.SensorType == "Accelerometer"]), ("gyroscope", g[g.SensorType == "Gyroscope"])):
            m = np.linalg.norm(arr[["X", "Y", "Z"]].to_numpy(), axis=1)
            if len(m) >= 3:
                f[f"imu_{name}_std"] = float(m.std()); f[f"imu_{name}_mean"] = float(m.mean())
        if len(gr) >= 5:
            for i, ax in enumerate("xyz"):
                f[f"imu_grav_{ax}_mean"] = float(gr[:, i].mean()); f[f"imu_grav_{ax}_std"] = float(gr[:, i].std())
        out[sid] = f
    return out


_imu = {u: imu_features(u) for u in sorted({e["user"] for e in S})}
for e in S:
    e["f"] = features.extract(e["session"])
    e["f"].update(_imu[e["user"]].get(e["sample"], {}))
S = [e for e in S if all(k in e["f"] for k in ("imu_grav_x_mean", "imu_accelerometer_std", "imu_gyroscope_std"))]
KEYS = {n: sorted(k for k in S[0]["f"] if sel(k)) for n, sel in SETS.items()}
print({n: len(v) for n, v in KEYS.items()})
for e in S:
    e["v"] = {n: np.array([e["f"][k] for k in ks]) for n, ks in KEYS.items()}

grp = defaultdict(list)  # (user, pin, posture) -> entries
for e in S:
    grp[(e["user"], e["pin"], e["posture"])].append(e)
by_pin_post = defaultdict(lambda: defaultdict(list))  # (pin, posture) -> user -> entries
for (u, p, po), es in grp.items():
    by_pin_post[(p, po)][u] += es
users = sorted({e["user"] for e in S})
print(f"{len(S)} lượt, {len(users)} người; lượt ngồi/PIN/người trung vị:",
      int(np.median([len(v) for (u, p, po), v in grp.items() if po == "sit"])), "; đi:",
      int(np.median([len(v) for (u, p, po), v in grp.items() if po == "walk"])))


def within_var(pin, posture, exclude, name):
    """Phương sai trong-người trung bình của người KHÁC (leave-user-out), theo (PIN, tư thế)."""
    vs = [np.var(np.array([e["v"][name] for e in es]), axis=0, ddof=1)
          for u, es in by_pin_post[(pin, posture)].items() if u != exclude and len(es) >= 2]
    return np.mean(vs, axis=0)


def detectors(name, X, prior_var):
    keys, mu = KEYS[name], X.mean(0)
    floor = np.array([owner._floor(k, m) for k, m in zip(keys, mu)])
    sd_backend = np.maximum(X.std(0, ddof=1), floor)
    mad = np.abs(X - mu).mean(0) + 1e-9
    var_eb = ((len(X) - 1) * X.var(0, ddof=1) + NU * prior_var) / (len(X) - 1 + NU)
    return {"backend (owner.py: sd có sàn)": lambda x: (np.abs(x - mu) / sd_backend).mean(-1),
            "Manhattan scaled": lambda x: (np.abs(x - mu) / mad).mean(-1),
            f"E2 co rút về dân số (nu={NU})": lambda x: (np.abs(x - mu) / np.sqrt(var_eb)).mean(-1)}


# scores[(k, test_posture, set, detector)][user] = (gen[], imp[])
scores = defaultdict(lambda: defaultdict(lambda: ([], [])))
for (u, p, po), es in grp.items():
    if po != "sit":
        continue
    for k in KS:
        if len(es) < k:
            continue
        for _ in range(N_DRAW):
            enr = rng.sample(es, k)
            rest_sit = [e for e in es if e not in enr]
            walk = grp.get((u, p, "walk"), [])
            for tpost, gen_es in (("cùng tư thế (ngồi)", rest_sit), ("đổi tư thế (đi)", walk)):
                if not gen_es:
                    continue
                imp_pool = [e for v, ves in by_pin_post[(p, "sit" if tpost.startswith("cùng") else "walk")].items() if v != u for e in ves]
                imp = rng.sample(imp_pool, min(N_IMP, len(imp_pool)))
                for name in SETS:
                    X = np.array([e["v"][name] for e in enr])
                    pv = within_var(p, "sit", u, name)
                    for dn, f in detectors(name, X, pv).items():
                        g, i = scores[(k, tpost, name, dn)][u]
                        g += list(f(np.array([e["v"][name] for e in gen_es])))
                        i += list(f(np.array([e["v"][name] for e in imp])))


def metrics(gen, imp):
    gen, imp = np.asarray(gen), np.asarray(imp)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 400)))
    frr = np.array([(gen > t).mean() for t in ths])
    far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return (frr[i] + far[i]) / 2, float((imp <= np.quantile(gen, 0.95)).mean())


def pooled(per_user, us):
    return np.concatenate([per_user[u][0] for u in us]), np.concatenate([per_user[u][1] for u in us])


def ci(per_user):
    us = sorted(per_user)
    est = metrics(*pooled(per_user, us))
    bs = np.array([metrics(*pooled(per_user, rng.choices(us, k=len(us)))) for _ in range(BOOT)])
    lo, hi = np.quantile(bs, 0.025, axis=0), np.quantile(bs, 0.975, axis=0)
    return est, lo, hi


lines = ["# E23 — PIN + chuyển động. Xác minh chủ trên PIN điện thoại thật (StrokePIN, 97 người, PIN 6 số)", "",
         f"Dùng `features.py` + `owner.py` của backend. Kẻ gian **biết PIN** (người khác nhập cùng PIN). Đăng ký k lượt ngồi; "
         f"điểm gộp mọi cặp (người, PIN), CI 95% bootstrap theo người ({BOOT} lần). Thấp hơn là tốt hơn. "
         "Dữ liệu người thật; mỗi người một điện thoại, nên khác thiết bị giữa người cũng góp vào độ tách.", ""]
for k in KS:
    for tpost in ("cùng tư thế (ngồi)", "đổi tư thế (đi)"):
        lines += [f"## k = {k} lượt đăng ký, kiểm thử {tpost}", "", "| Bộ đặc trưng | Bộ phát hiện | EER | FAR @ FRR 5% |", "|---|---|---|---|"]
        for (k2, t2, name, dn), per_user in scores.items():
            if (k2, t2) != (k, tpost):
                continue
            (e, f), lo, hi = ci(per_user)
            lines.append(f"| {name} | {dn} | {e:.3f} [{lo[0]:.3f}, {hi[0]:.3f}] | {f:.3f} [{lo[1]:.3f}, {hi[1]:.3f}] |")
        lines.append("")
# so sánh GHÉP CẶP (cùng mẫu bootstrap theo người): E2 trừ backend, âm = E2 tốt hơn
lines += ["## So sánh ghép cặp: E2 (co rút về dân số) trừ backend hiện tại, âm = E2 tốt hơn", "",
          "| k | Kiểm thử | Bộ đặc trưng | dEER | dFAR @ FRR 5% |", "|---|---|---|---|---|"]
for k in KS:
    for tpost in ("cùng tư thế (ngồi)", "đổi tư thế (đi)"):
        for name in SETS:
            a = scores.get((k, tpost, name, "backend (owner.py: sd có sàn)"))
            b = scores.get((k, tpost, name, f"E2 co rút về dân số (nu={NU})"))
            if not a or not b:
                continue
            us = sorted(a)
            d = np.array([np.subtract(metrics(*pooled(b, r)), metrics(*pooled(a, r)))
                          for r in (rng.choices(us, k=len(us)) for _ in range(BOOT))])
            m = np.subtract(metrics(*pooled(b, us)), metrics(*pooled(a, us)))
            lo, hi = np.quantile(d, 0.025, axis=0), np.quantile(d, 0.975, axis=0)
            lines.append(f"| {k} | {tpost} | {name} | {m[0]:+.3f} [{lo[0]:+.3f}, {hi[0]:+.3f}] | {m[1]:+.3f} [{lo[1]:+.3f}, {hi[1]:+.3f}] |")
lines.append("")
out = ROOT / "research/results/e23_imu_fusion.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
