"""E14: nhận ra chủ khi gõ CHUỖI SỐ MỚI (mô phỏng gõ số tài khoản), người thật StrokePIN.

Câu hỏi: số tài khoản đổi theo từng giao dịch, nên không so được theo vị trí chữ số như mẫu PIN (pin_hold_0..5).
Với đặc trưng KHÔNG phụ thuộc nội dung, còn nhận ra chủ được bao nhiêu khi chuỗi số chưa từng thấy lúc đăng ký?

StrokePIN: 97 người, 20 PIN 6 số dùng chung, ngồi/đi. Mỗi người: đăng ký bằng 3 lượt x 3 PIN (9 "giao dịch") khi ngồi.
Kiểm thử (kẻ gian = người khác gõ CÙNG chuỗi số, cùng tư thế):
  A. cùng chuỗi số đã đăng ký (lượt chưa dùng)      B. chuỗi số mới
  C. chuỗi số mới, 12 số (gộp 2 lượt của 2 PIN mới) D. chuỗi số mới, khi đi
Đặc trưng: thời gian giữ/khoảng cách (gộp, và theo khoảng cách hình học giữa hai phím), lệch tâm theo cột/hàng phím.
BỎ kích thước chạm (mang thông tin thiết bị, như E12b). Bộ phát hiện: khoảng cách mean|z| (như backend) và LightGBM học
trên |z| từ người huấn luyện (chia theo NGƯỜI, 3 cách chia). CI 95% bootstrap theo người, trung bình giữa các lần chia.
Giới hạn: 6-12 số ngắn hơn hoặc bằng số tài khoản; bàn phím StrokePIN có thể khác app; mỗi người một máy.
"""

import random
import sys
from collections import defaultdict
from pathlib import Path

import lightgbm as lgb
import numpy as np

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import strokepin_loader  # noqa: E402

N_PIN_ENR, K_PER_PIN, N_GEN, N_IMP, BOOT, SPLITS = 3, 3, 30, 3, 100, (21, 22, 23)
COL = {k: i for i, ks in enumerate(("147", "2580", "369")) for k in ks}
ROW = {k: i for i, ks in enumerate(("123", "456", "789", "0")) for k in ks}
FEATS = (["hold_mean", "hold_std", "hold_med", "flight_mean", "flight_std", "flight_med", "flight_same", "flight_near", "flight_far",
          "dx_mean", "dy_mean", "dx_std", "dy_std"] + [f"dx_c{i}" for i in range(3)] + [f"dy_r{i}" for i in range(4)])


def feats(entries: list[dict]) -> np.ndarray:
    """Đặc trưng không phụ thuộc nội dung trên một hoặc nhiều lượt gõ (gộp). Thiếu = NaN."""
    hold, fl, fl_cls, dx, dy = [], [], defaultdict(list), [], []
    by_c, by_r = defaultdict(list), defaultdict(list)
    for e in entries:
        t = e["session"]["pin_taps"]
        for a in t:
            hold.append(a["t_up"] - a["t_down"])
            ox, oy = (a["x"] - a["key_cx"]) / a["key_w"], (a["y"] - a["key_cy"]) / a["key_h"]
            dx.append(ox); dy.append(oy); by_c[COL[a["key"]]].append(ox); by_r[ROW[a["key"]]].append(oy)
        for a, b in zip(t, t[1:]):
            f = b["t_down"] - a["t_up"]
            d = np.hypot((b["key_cx"] - a["key_cx"]) / a["key_w"], (b["key_cy"] - a["key_cy"]) / a["key_h"])
            fl.append(f); fl_cls["same" if d < 0.5 else "near" if d < 1.6 else "far"].append(f)
    m = lambda v: float(np.mean(v)) if v else np.nan  # noqa: E731
    v = [np.mean(hold), np.std(hold), np.median(hold), np.mean(fl), np.std(fl), np.median(fl),
         m(fl_cls["same"]), m(fl_cls["near"]), m(fl_cls["far"]), np.mean(dx), np.mean(dy), np.std(dx), np.std(dy)]
    v += [m(by_c[i]) for i in range(3)] + [m(by_r[i]) for i in range(4)]
    return np.array(v, dtype=float)


S = strokepin_loader.load()
for e in S:
    e["v"] = feats([e])
grp = defaultdict(list)  # (user, pin, posture) -> lượt
for e in S:
    grp[(e["user"], e["pin"], e["posture"])].append(e)
USERS = sorted({e["user"] for e in S})


def floor_from(train_users) -> np.ndarray:
    """Sàn độ lệch chuẩn = nửa trung vị độ lệch chuẩn trong-người (chỉ từ người huấn luyện, không rò rỉ)."""
    sds = []
    for u in train_users:
        X = np.array([e["v"] for (uu, _p, po), es in grp.items() if uu == u and po == "sit" for e in es])
        sds.append(np.nanstd(X, axis=0))
    return 0.5 * np.nanmedian(np.array(sds), axis=0)


def rows(users, floor, seed):
    """-> {điều kiện: (Z, nhãn 0=chủ/1=kẻ gian, người)}; Z = |z| so với mẫu của chủ."""
    rng = random.Random(seed)
    out = defaultdict(lambda: ([], [], []))

    def add(cond, v, lab, u, mu, sd):
        Z, y, w = out[cond]
        Z.append(np.abs((v - mu) / sd)); y.append(lab); w.append(u)

    for u in users:
        pins = sorted(p for (uu, p, po), es in grp.items() if uu == u and po == "sit" and len(es) >= K_PER_PIN + 1)
        if len(pins) < N_PIN_ENR + 2:
            continue
        rng.shuffle(pins)
        enr_pins, new_pins = pins[:N_PIN_ENR], pins[N_PIN_ENR:]
        enr, seen_rest = [], []
        for p in enr_pins:
            es = rng.sample(grp[(u, p, "sit")], len(grp[(u, p, "sit")]))
            enr += es[:K_PER_PIN]; seen_rest += es[K_PER_PIN:]
        X = np.array([e["v"] for e in enr])
        mu, sd = np.nanmean(X, axis=0), np.fmax(np.nanstd(X, axis=0), floor)

        def others(p, po):
            return [e for (v, pp, ppo), es in grp.items() if pp == p and ppo == po and v != u for e in es]

        tests = {"A": [(e, "sit") for e in seen_rest],
                 "B": [(e, "sit") for p in new_pins for e in grp[(u, p, "sit")]],
                 "D": [(e, "walk") for p in new_pins for e in grp.get((u, p, "walk"), [])]}
        for cond, items in tests.items():
            for e, po in rng.sample(items, min(N_GEN, len(items))):
                add(cond, e["v"], 0, u, mu, sd)
                for imp in rng.sample(others(e["pin"], po), min(N_IMP, len(others(e["pin"], po)))):
                    add(cond, imp["v"], 1, u, mu, sd)
        # C: 12 số = 2 lượt của 2 PIN mới khác nhau; kẻ gian = MỘT người khác gõ đúng 2 PIN đó
        for _ in range(N_GEN):
            p1, p2 = rng.sample(new_pins, 2)
            add("C", feats([rng.choice(grp[(u, p1, "sit")]), rng.choice(grp[(u, p2, "sit")])]), 0, u, mu, sd)
            cand = [v for v in USERS if v != u and grp.get((v, p1, "sit")) and grp.get((v, p2, "sit"))]
            for v in rng.sample(cand, min(N_IMP, len(cand))):
                add("C", feats([rng.choice(grp[(v, p1, "sit")]), rng.choice(grp[(v, p2, "sit")])]), 1, u, mu, sd)
    return {c: tuple(np.array(a) for a in t) for c, t in out.items()}


def metrics(s, y):
    """(EER, FAR @ FRR 5%); điểm cao = giống kẻ gian."""
    gen, imp = s[y == 0], s[y == 1]
    ths = np.unique(np.quantile(s, np.linspace(0, 1, 400)))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return np.array([(frr[i] + far[i]) / 2, (imp <= np.quantile(gen, 0.95)).mean()])


def boot_ci(s, y, who):
    rng = np.random.default_rng(0)
    us = np.unique(who); idx = {u: np.where(who == u)[0] for u in us}
    m = [metrics(s[r], y[r]) for r in (np.concatenate([idx[u] for u in rng.choice(us, len(us))]) for _ in range(BOOT))]
    return np.quantile(m, 0.025, axis=0), np.quantile(m, 0.975, axis=0)


res = defaultdict(list)
n_test = {}
for sp in SPLITS:
    r = random.Random(sp); us = USERS[:]; r.shuffle(us)
    tr, te = us[:58], us[58:]
    floor = floor_from(tr)
    Rtr, Rte = rows(tr, floor, sp), rows(te, floor, sp + 100)
    Ztr = np.vstack([Rtr[c][0] for c in "BC"]); ytr = np.concatenate([Rtr[c][1] for c in "BC"])
    gb = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=30, subsample=0.8,
                            subsample_freq=1, colsample_bytree=0.8, random_state=sp, verbose=-1).fit(Ztr, ytr)
    for c, (Z, y, w) in sorted(Rte.items()):
        n_test[c] = (int((y == 0).sum()), int((y == 1).sum()), len(np.unique(w)))
        for name, s in (("khoảng cách mean|z|", np.nanmean(Z, axis=1)), ("LightGBM học", gb.predict_proba(Z)[:, 1])):
            res[(c, name)].append((metrics(s, y), *boot_ci(s, y, w)))

LABEL = {"A": "cùng chuỗi số đã đăng ký", "B": "**chuỗi số mới** (6 số)", "C": "**chuỗi số mới, 12 số** (gộp 2 lượt)",
         "D": "chuỗi số mới, khi **đi**"}
L = ["# E14 — nhận ra chủ khi gõ chuỗi số mới (mô phỏng số tài khoản; StrokePIN, người thật)", "",
     f"Đăng ký {N_PIN_ENR} PIN x {K_PER_PIN} lượt khi ngồi. Kẻ gian = người khác gõ **cùng chuỗi số**, cùng tư thế. "
     f"{len(FEATS)} đặc trưng không phụ thuộc nội dung, **không** dùng kích thước chạm. Chia theo người (58 huấn luyện / "
     f"{len(USERS) - 58} kiểm thử), {len(SPLITS)} cách chia; CI 95% bootstrap theo người, trung bình giữa các lần chia. Thấp hơn là tốt hơn.", "",
     "| Kiểm thử | Bộ phát hiện | EER | FAR @ FRR 5% | Phiên chủ / kẻ gian / người (lần chia cuối) |", "|---|---|---|---|---|"]
for (c, name), v in sorted(res.items()):
    est, lo, hi = (np.mean([x[i] for x in v], axis=0) for i in range(3))
    g, i_, n = n_test[c]
    L.append(f"| {LABEL[c]} | {name} | {est[0]:.3f} [{lo[0]:.3f}, {hi[0]:.3f}] | {est[1]:.3f} [{lo[1]:.3f}, {hi[1]:.3f}] | {g} / {i_} / {n} |")
L += ["", "Đối chiếu E12b (cùng PIN, đặc trưng theo vị trí chữ số, không kích thước chạm): khoảng cách EER 0.161 / FAR 0.573; "
      "LightGBM EER 0.158 / FAR 0.375. Khác giao thức (E12b đăng ký 3 lượt của MỘT PIN), nên chỉ so hướng, không so từng số."]
(ROOT / "research/results/e14_unseen_digits.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
