"""E29: E24 lặp trên CẢ 97 người bằng cross-validation 5 phần CHIA THEO NGƯỜI, kèm khoảng tin cậy và phân bố theo nạn nhân.

Mỗi phần: huấn luyện LẠI mô hình người/máy (train_human_model.py) và mô hình chủ (train_owner_model.py) chỉ trên người ngoài phần đó
(prior dân số cũng chỉ từ họ; kho kẻ gian khi huấn luyện chỉ gồm họ), rồi chấm người của phần đó bằng đúng chuỗi /score (như E24).
Mỗi người dùng tối đa N_PINS PIN ngẫu nhiên. CI 95% bootstrap theo người. Bot vẫn là bộ sinh của đội (bot thích nghi do E24).
Chạy (từ backend/): uv run --with pandas --with numpy --with scikit-learn --with lightgbm python ../research/experiments/e29_cv_end_to_end.py
"""
import copy, random, sys, time
from collections import defaultdict
from pathlib import Path
import lightgbm as lgb
import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker"), str(Path(__file__).parent)]
from app.scoring import bot_features, features, fusion, human, human_model, owner, owner_model, replay  # noqa: E402
from nhip_attacker import tactics  # noqa: E402
import strokepin_loader  # noqa: E402

SEED, FOLDS, N_PINS, FRR = 29, 5, 6, 0.05
rng = random.Random(SEED)
S = strokepin_loader.load()
for e in S:
    e["f"] = features.extract(e["session"])
USERS = sorted({e["user"] for e in S}); PINS = sorted({e["pin"] for e in S})
by = defaultdict(lambda: defaultdict(list)); by_pin = defaultdict(list); by_user = defaultdict(list)
for e in S:
    by[(e["user"], e["pin"])][e["posture"]].append(e); by_pin[e["pin"]].append(e); by_user[e["user"]].append(e)
grp, bpp = defaultdict(list), defaultdict(lambda: defaultdict(list))
for e in S:
    grp[(e["user"], e["pin"], e["posture"])].append(e); bpp[(e["pin"], e["posture"])][e["user"]].append(e)
TK = sorted(k for k in S[0]["f"] if k.startswith(("pin_hold_", "pin_flight_")) or k == "pin_total")
NAMES = [n for n in bot_features.FEATURE_NAMES if n not in bot_features.CONTACT_FEATURES]
EXCL = {"tap_w_mean", "tap_h_mean"}


def strip(s): return {**s, "swipes": [], "screens": []}


def noisy_replay(src, n):
    s = copy.deepcopy(src); taps = sorted(s["pin_taps"], key=lambda t: t["t_down"]); t = 0.0
    for i, tap in enumerate(taps):
        hold = (tap["t_up"] - tap["t_down"]) * rng.uniform(1 - n, 1 + n)
        gap = (taps[i + 1]["t_down"] - tap["t_up"]) * rng.uniform(1 - n, 1 + n) if i < len(taps) - 1 else 0
        r = max(0.02, 0.4 * n)
        tap["x"] += rng.uniform(-r, r) * tap["key_w"]; tap["y"] += rng.uniform(-r, r) * tap["key_h"]
        tap["t_down"], tap["t_up"] = t, t + hold
        t += hold + max(gap, 0)
    s["pin_taps"] = taps
    return s


def mimic(victim_sessions, scale):
    ts = [sorted(s["pin_taps"], key=lambda t: t["t_down"]) for s in victim_sessions]
    k = len(ts[0]); out = copy.deepcopy(victim_sessions[0]); taps = out["pin_taps"] = sorted(out["pin_taps"], key=lambda t: t["t_down"]); t = 0.0
    for i in range(k):
        col = lambda f: np.array([f(x[i]) for x in ts])  # noqa: E731
        hold = col(lambda tp: tp["t_up"] - tp["t_down"])
        dx = col(lambda tp: (tp["x"] - tp["key_cx"]) / tp["key_w"]); dy = col(lambda tp: (tp["y"] - tp["key_cy"]) / tp["key_h"])
        g = lambda v: rng.gauss(v.mean(), max(v.std() * scale, 1e-3))  # noqa: E731
        h_ = max(g(hold), 20.0)
        taps[i]["x"] = taps[i]["key_cx"] + g(dx) * taps[i]["key_w"]; taps[i]["y"] = taps[i]["key_cy"] + g(dy) * taps[i]["key_h"]
        taps[i]["t_down"], taps[i]["t_up"] = t, t + h_
        fl = np.array([x[i + 1]["t_down"] - x[i]["t_up"] for x in ts]) if i < k - 1 else None
        t += h_ + (max(g(fl), 20.0) if fl is not None else 0)
    return out


def train_human(fit, val):
    sf = [e["session"] for u in fit for e in by_user[u]]; sv = [e["session"] for u in val for e in by_user[u]]
    Hf = rng.sample(sf, min(4000, len(sf))); Hv = rng.sample(sv, min(1500, len(sv))); pool = rng.sample(sf, 500)
    vec = lambda ss: np.array([[bot_features.extract(s)[k] for k in NAMES] for s in ss], dtype=float)  # noqa: E731
    bots = lambda t, n: [{**tactics.generate(t, "victim", rng.choice(PINS), pool, rng), "swipes": [], "screens": []} for _ in range(n)]  # noqa: E731
    Xh = vec(Hf); Xb = np.vstack([vec(bots(t, 800)) for t in (1, 2, 3, 4)])
    m = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=20, subsample=0.8, subsample_freq=1,
                           colsample_bytree=0.8, reg_lambda=1.0, random_state=SEED, verbose=-1).fit(np.vstack([Xh, Xb]), np.r_[np.ones(len(Xh)), np.zeros(len(Xb))])
    thr = float(np.quantile(m.predict_proba(vec(Hv))[:, 1], FRR))
    human_model._state["m"] = (m.booster_, {"features": NAMES, "threshold": thr})


def train_owner(fit, val):
    fs = set(fit)
    WV = {g: np.var(np.array([[e["f"][k] for k in TK] for e in es]), axis=0, ddof=1) for g, es in grp.items() if len(es) >= 2 and g[0] in fs}
    owner._PRIOR = {"within_var": dict(zip(TK, np.mean(list(WV.values()), axis=0).tolist())), "n_taps": 6, "nu": 5}

    def rows(users, allowed):
        X, y, post, keys = [], [], [], None
        for (u, p, po), es in grp.items():
            if u not in users or po != "sit" or len(es) < 3: continue
            for _ in range(3):
                enr = rng.sample(es, 3); tpl = owner.build_template([e["f"] for e in enr])
                keys = keys or sorted(k for k in tpl["mu"] if k not in EXCL)
                for tp, gen in (("sit", [e for e in es if e not in enr]), ("walk", grp.get((u, p, "walk"), []))):
                    if not gen: continue
                    pool = [e for v, ves in bpp[(p, tp)].items() if v != u and v in allowed for e in ves]
                    for lab, ents in ((0, gen), (1, rng.sample(pool, min(15, len(pool))))):
                        for e in ents:
                            z = owner.score(e["f"], tpl)[1]; X.append([abs(z[k]) for k in keys]); y.append(lab); post.append(tp)
        return np.array(X), np.array(y), np.array(post), keys
    Xt, yt, _, keys = rows(fs, fs); Xv, yv, pv, _ = rows(set(val), fs | set(val))
    m = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=30, subsample=0.8, subsample_freq=1,
                           colsample_bytree=0.8, random_state=SEED, verbose=-1).fit(Xt, yt)
    p = m.predict_proba(Xv)[:, 1]
    thr = float(np.quantile(p[(yv == 0) & (pv == "sit")], 1 - FRR))
    owner_model._state["m"] = (m.booster_, {"features": keys, "threshold": thr})


def decide(raw, f, tpl, history, new_recipient):
    h, br = human.score(f); p = human_model.predict(raw)
    if p is not None: h = p if br == ["insufficient_data"] else min(h, p)
    if replay.is_replay(f, history[-50:]): h = min(h, 0.1)
    o, z = owner.score(f, tpl) if tpl else (None, {})
    if o:
        m = owner_model.predict(z); o = o if m is None else m
    risk, action, _ = fusion.fuse(h, o, new_recipient, 0.0)
    return risk, action, h


GROUPS = ["chủ, cùng tư thế (ngồi)", "chủ, đổi tư thế (đi)", "kẻ biết PIN (người khác, máy khác)", "bot CT1 đều", "bot CT2 nhiễu thời gian",
          "bot CT3 phát lại ±5%", "bot CT4 lấy mẫu dân số", "phát lại ±10%", "phát lại ±15%", "phát lại ±20%", "phát lại ±30%",
          "bot biết mẫu chuẩn (scale 1.0)", "bot biết mẫu chuẩn (scale 0.5)"]
R = {g: [] for g in GROUPS}  # g -> [(user, risk_known, risk_new, human)]


def record(g, u, raw, tpl, hist):
    f = features.extract(raw)
    rk, _, h = decide(raw, f, tpl, hist, False); rn, _, _ = decide(raw, f, tpl, hist, True)
    R[g].append((u, rk, rn, h))


us = USERS[:]; random.Random(SEED).shuffle(us)
t0 = time.time()
for fi in range(FOLDS):
    test = set(us[fi::FOLDS]); rest = [u for u in us if u not in test]; val, fit = rest[:12], rest[12:]
    train_human(fit, val); train_owner(fit, val)
    print(f"phần {fi + 1}/{FOLDS}: {len(test)} người kiểm thử, mô hình đã huấn luyện ({time.time() - t0:.0f}s)", flush=True)
    for u in sorted(test):
        pins = [p for (uu, p), post in by.items() if uu == u and len(post["sit"]) >= 5]
        for pin in rng.sample(pins, min(N_PINS, len(pins))):
            post = by[(u, pin)]; es = post["sit"][:]; rng.shuffle(es); enr, tests = es[:3], es[3:]
            tpl = owner.build_template([e["f"] for e in enr]); hist = [e["f"] for e in enr]
            for e in tests:
                record(GROUPS[0], u, e["session"], tpl, hist); hist = hist + [e["f"]]
            for e in post["walk"][:4]: record(GROUPS[1], u, e["session"], tpl, hist)
            others = [e for e in by_pin[pin] if e["user"] != u and e["posture"] == "sit"]
            for e in rng.sample(others, min(4, len(others))): record(GROUPS[2], u, {**e["session"], "user_id": u}, tpl, hist)
            victim = [e["session"] for e in es]; pop = [e["session"] for e in rng.sample(by_pin[pin], min(150, len(by_pin[pin])))]
            for _ in range(2):
                for gi, t in ((3, 1), (4, 2), (5, 3), (6, 4)):
                    record(GROUPS[gi], u, strip(tactics.generate(t, u, pin, victim if t == 3 else pop if t == 4 else victim, rng)), tpl, hist)
                src = rng.choice(victim)
                for gi, n in ((7, 0.10), (8, 0.15), (9, 0.20), (10, 0.30)): record(GROUPS[gi], u, strip(noisy_replay(src, n)), tpl, hist)
                for gi, sc in ((11, 1.0), (12, 0.5)): record(GROUPS[gi], u, strip(mimic(victim[:6], sc)), tpl, hist)

A0, B0 = fusion.THRESHOLD_A, fusion.THRESHOLD_B


def act(risk, h, A, B): return "hold" if h < fusion.HUMAN_HOLD or risk > B else "step_up" if risk >= A else "allow"


def rate(rows, col, A, B, what):
    """Tỉ lệ theo NGƯỜI rồi bootstrap trên người. what: 'allow' | 'notallow' | 'hold' | 'step_up'."""
    per = defaultdict(list)
    for r in rows:
        a = act(r[col], r[3], A, B)
        per[r[0]].append((a == "allow") if what == "allow" else (a != "allow") if what == "notallow" else (a == what))
    ids = sorted(per); v = np.array([np.mean(per[u]) for u in ids]); n = np.array([len(per[u]) for u in ids])
    est = (v * n).sum() / n.sum()
    br = random.Random(1); bs = []
    for _ in range(300):
        s = [br.randrange(len(ids)) for _ in ids]; bs.append((v[s] * n[s]).sum() / n[s].sum())
    return est, np.quantile(bs, 0.025), np.quantile(bs, 0.975), v


fmt = lambda t: f"{100 * t[0]:.0f}% [{100 * t[1]:.0f}, {100 * t[2]:.0f}]"  # noqa: E731
L = ["# E29 — E24 trên cả 97 người (cross-validation 5 phần theo người)", "",
     f"Mỗi phần huấn luyện lại hai mô hình học chỉ trên người ngoài phần đó. {len(USERS)} người, tối đa {N_PINS} PIN mỗi người, ngưỡng A={A0}, B={B0}. "
     "Ô: **tỉ lệ [CI 95% bootstrap theo người]**. Kẻ biết PIN dùng MÁY KHÁC (lẫn nhiễu thiết bị); bot là bộ sinh của đội. Số phiên mỗi nhóm ở cột n.", "",
     "## Người nhận quen", "", "| Nhóm | n | hold | step_up | allow |", "|---|---|---|---|---|"]
for g in GROUPS:
    L.append(f"| {g} | {len(R[g])} | " + " | ".join(fmt(rate(R[g], 1, A0, B0, w)) for w in ("hold", "step_up", "allow")) + " |")
L += ["", "## Người nhận MỚI", "", "| Nhóm | n | hold | step_up | allow |", "|---|---|---|---|---|"]
for g in GROUPS:
    L.append(f"| {g} | {len(R[g])} | " + " | ".join(fmt(rate(R[g], 2, A0, B0, w)) for w in ("hold", "step_up", "allow")) + " |")
L += ["", "## Quét ngưỡng A (B=0,55, người nhận quen): chủ ngồi được allow / không allow với …", "",
      "| A | chủ ngồi allow | kẻ biết PIN | bot CT4 | biết mẫu chuẩn 1,0 | phát lại ±15% |", "|---|---|---|---|---|---|"]
for A in (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40):
    L.append(f"| {A:.2f}{' ←' if A == A0 else ''} | {fmt(rate(R[GROUPS[0]], 1, A, 0.55, 'allow'))} | "
             + " | ".join(fmt(rate(R[g], 1, A, 0.55, "notallow")) for g in (GROUPS[2], GROUPS[6], GROUPS[11], GROUPS[8])) + " |")
v = rate(R[GROUPS[2]], 1, A0, B0, "allow")[3]
srt = np.sort(v); n = len(srt); gini = float((2 * np.arange(1, n + 1) - n - 1).dot(srt) / (n * srt.sum())) if srt.sum() else 0.0
L += ["", "## Phân bố theo nạn nhân (kẻ biết PIN, người nhận quen, A=0,25)", "",
      f"Tỉ lệ kẻ biết PIN được allow, tính riêng từng nạn nhân ({n} người): trung vị {100 * np.median(v):.0f}%, phân vị 90% {100 * np.quantile(v, .9):.0f}%, lớn nhất {100 * v.max():.0f}%.",
      f"Hệ số Gini {gini:.2f} (0 = đều giữa các nạn nhân, 1 = dồn vào vài người). Số nạn nhân bị allow > 50%: {(v > 0.5).sum()}/{n}; > 90%: {(v > 0.9).sum()}/{n}.", ""]
Path(ROOT / "research/results/e29_cv_end_to_end.md").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L)); print(f"xong sau {time.time() - t0:.0f}s")
