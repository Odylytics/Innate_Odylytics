"""E11: bài người/máy trên Ô VĂN BẢN TỰ DO (ghi chú chuyển khoản) với NGƯỜI THẬT (Aalto) và bot sinh.

Người = nhịp gõ thật của 2.263 người (Aalto typing37k; chỉ thời gian, loại sự kiện, lớp ký tự; KHÔNG nội dung), chia theo người.
Bot = 4 chiến thuật trong attacker/nhip_attacker/fields.py, CHỈ ô `note` (Aalto không có ô số tiền/người nhận):
  1 đặt thẳng văn bản (ACTION_SET_TEXT)   2 gõ đều qua công cụ tự động   3 phát lại nhịp một người thật (±5%)   4 lấy mẫu từ dân số
Đặc trưng: (a) các `fld_*` hiện có trong backend/bot_features.py; (b) "mở rộng" = (a) + vài thống kê nhịp tính ngay trong thí nghiệm,
để biết bộ đặc trưng của backend thiếu gì. Đánh giá: ngưỡng FRR 5% trên người ở tập validation; tất cả chiến thuật / bỏ một chiến thuật.
Hạn chế: bot vẫn là giả; một ô duy nhất; người gõ câu mẫu tiếng Anh trên điện thoại, không phải nội dung chuyển khoản tiếng Việt.
"""

import json
import random
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker")]
from app.scoring import bot_features, features, human  # noqa: E402
from nhip_attacker import fields  # noqa: E402

SEEDS, FRR, TACTICS = (1, 2, 3), 0.05, (1, 2, 3, 4)
N_H = {"train": 4000, "val": 1000, "test": 3000, "pool": 500}
N_BOT = {"train": 600, "val": 150, "test": 500}
BASE = [n for n in bot_features.FEATURE_NAMES if n.startswith("fld_")]
EXTRA = ["gap_std", "gap_p10", "gap_p50", "gap_p90", "succ_diff_rel", "n_keys"]


def to_session(rec):
    ev = []
    for t, kind, n, cls in rec["events"]:
        e = {"t": t, "kind": kind, "n": n}
        if cls:
            e["cls"] = cls
        ev.append(e)
    return {"user_id": rec["participant"], "pin_taps": [], "swipes": [], "screens": [], "fields": [{"name": "note", "events": ev}]}


H_ALL = [(r["participant"], to_session(r)) for r in map(json.loads, open(ROOT / "research/data/aalto_note_events.jsonl"))]
PEOPLE = sorted({p for p, _ in H_ALL})


def extra(sess):
    ev = sorted(sess["fields"][0]["events"], key=lambda e: e["t"]) if sess.get("fields") else []
    ts = [e["t"] for e in ev if e["kind"] == "key"]
    g = np.diff(ts) if len(ts) > 3 else np.array([np.nan])
    sd = np.abs(np.diff(g)).mean() / g.mean() if len(g) > 2 and g.mean() > 0 else np.nan
    return [np.std(g), *np.nanpercentile(g, [10, 50, 90]), sd, float(len(ts))] if len(ts) > 3 else [np.nan] * 6


def vec(sessions, ext):
    rows = []
    for s in sessions:
        f = bot_features.extract(s)
        rows.append([f[k] for k in BASE] + (extra(s) if ext else []))
    return np.array(rows, dtype=float)


def build(seed):
    rng = random.Random(seed)
    ps = PEOPLE[:]
    rng.shuffle(ps)
    cut = {"pool": ps[:200], "train": ps[200:1400], "val": ps[1400:1700], "test": ps[1700:]}
    H = {}
    for k, who in cut.items():
        ses = [s for p, s in H_ALL if p in set(who)]
        H[k] = rng.sample(ses, min(N_H[k], len(ses)))
    pool = H["pool"]
    B = {t: {} for t in TACTICS}
    for t in TACTICS:
        for k in ("train", "val", "test"):
            out = []
            for _ in range(N_BOT[k]):
                src = rng.choice(pool)
                fl = [f for f in fields.for_tactic(t, rng, pool, src) if f["name"] == "note"]
                out.append({"user_id": "victim", "pin_taps": [], "swipes": [], "screens": [], "fields": fl})
            B[t][k] = out
    return H, B


def metrics(sc, thr, hum, bots):
    out = {"FRR": float((sc(hum) < thr).mean())}
    sh = sc(hum)
    for t, X in bots.items():
        sb = sc(X)
        out[t] = (float((sb < thr).mean()), float(roc_auc_score(np.r_[np.ones(len(sh)), np.zeros(len(sb))], np.r_[sh, sb])))
    return out


def evaluate(seed):
    H, B = build(seed)
    res = {}
    for ext, tag in ((False, "backend (fld_*)"), (True, "mở rộng")):
        F = {("H", k): vec(H[k], ext) for k in ("train", "val", "test")}
        F.update({(t, k): vec(B[t][k], ext) for t in TACTICS for k in ("train", "val", "test")})
        for scen, held in [("tất cả", None)] + [(f"bỏ CT{t}", t) for t in TACTICS]:
            tr = [t for t in TACTICS if t != held]
            m = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=20, subsample=0.8,
                                   subsample_freq=1, colsample_bytree=0.8, random_state=seed, verbose=-1)
            m.fit(np.vstack([F[("H", "train")]] + [F[(t, "train")] for t in tr]),
                  np.r_[np.ones(len(F[("H", "train")])), np.zeros(sum(len(F[(t, "train")]) for t in tr))])
            iso = IsolationForest(n_estimators=200, random_state=seed).fit(np.nan_to_num(F[("H", "train")], nan=-1))
            test_b = {t: F[(t, "test")] for t in (TACTICS if held is None else [held])}
            for name, sc in ((f"LightGBM, {tag}", lambda X, m=m: m.predict_proba(X)[:, 1]),
                             (f"IsolationForest, {tag}", lambda X, iso=iso: iso.score_samples(np.nan_to_num(X, nan=-1)))):
                res[(name, scen)] = metrics(sc, np.quantile(sc(F[("H", "val")]), FRR), F[("H", "test")], test_b)
    # luật hiện tại của backend trên chính các phiên này (ô số tiền mới bị coi là máy; ô ghi chú chỉ trừ nhẹ)
    rs = lambda S: np.array([human.score(features.extract(s))[0] for s in S])  # noqa: E731
    row = {"FRR": float((rs(H["test"]) < 0.5).mean())}
    for t in TACTICS:
        row[t] = (float((rs(B[t]["test"]) < 0.5).mean()), float("nan"))
    res[("Luật hiện tại của backend (cờ khi điểm < 0,5)", "không huấn luyện")] = row
    return res


all_res = [evaluate(s) for s in SEEDS]
keys = list(all_res[0])


def cell(r, t):
    return f"{np.mean([x[t][0] for x in r]):.2f}" + ("" if np.isnan(np.mean([x[t][1] for x in r])) else f" ({np.mean([x[t][1] for x in r]):.2f})")


L = ["# E11 — bài người/máy trên ô văn bản tự do (người thật Aalto + bot sinh)", "",
     f"{len(SEEDS)} cách chia người. Người: {len(H_ALL)} câu gõ thật của {len(PEOPLE)} người, chia theo người (kho kẻ tấn công 200 / train 1200 / val 300 / test còn lại). "
     f"Ngưỡng FRR {FRR:.0%} trên người ở tập validation. Mỗi ô: **tỷ lệ bot bị bắt** (AUC). Chỉ ô `note`. Bot vẫn là giả.", "",
     "## Huấn luyện thấy cả 4 chiến thuật", "", "| Mô hình | FRR thật | CT1 đặt thẳng văn bản | CT2 gõ đều | CT3 phát lại | CT4 lấy mẫu dân số |", "|---|---|---|---|---|---|"]
for k in keys:
    if k[1] not in ("tất cả", "không huấn luyện"):
        continue
    r = [x[k] for x in all_res]
    L.append(f"| {k[0]} | {np.mean([x['FRR'] for x in r]):.3f} | " + " | ".join(cell(r, t) for t in TACTICS) + " |")
L += ["", "## Bỏ đúng một chiến thuật khỏi huấn luyện (bot lạ)", "", "| Mô hình | FRR thật | Bỏ CT1 | Bỏ CT2 | Bỏ CT3 | Bỏ CT4 |", "|---|---|---|---|---|---|"]
for name in dict.fromkeys(k[0] for k in keys if k[1].startswith("bỏ")):
    cells, frr = [], []
    for t in TACTICS:
        r = [x[(name, f"bỏ CT{t}")] for x in all_res]
        cells.append(cell(r, t))
        frr += [x["FRR"] for x in r]
    L.append(f"| {name} | {np.mean(frr):.3f} | " + " | ".join(cells) + " |")
(ROOT / "research/results/e11_text_field_bots.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
