"""Phân tích dữ liệu CỦA ĐỘI (T1–T5 trong kế hoạch thực nghiệm), chạy một lệnh sau khi export.

  python research/experiments/team_analysis.py export.jsonl [--out report.md] [--boot 300]

export.jsonl = GET /v1/export (JSON list hoặc mỗi dòng một bản ghi), có `meta` {participant_id, sitting, role, tactic}.
  T1 nhận chủ cùng máy, theo thời gian (đăng ký 3 lượt đầu buổi 1; thử: các lượt còn lại, tách "cùng buổi" và "buổi sau")
  T2 bot: tỉ lệ bắt theo chiến thuật (luật + mô hình trong backend) và tỉ lệ chặn nhầm người
  T3 phát lại: tỉ lệ chặn nhầm chủ theo độ dài lịch sử
  T4 gộp PIN + câu thử thách so với riêng PIN (cần phiên có ô challenge)
  T5 ổn định kiểu gõ tiếng Việt giữa các buổi (vi_tone_late, vi_ime_coverage)
Cỡ mẫu nhỏ: mọi số kèm khoảng tin cậy bootstrap THEO NGƯỜI và số người; đừng so với bài báo trên hàng nghìn người.
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend")]
from app.scoring import human, human_model, owner, replay  # noqa: E402

ARGS = sys.argv[1:]
SRC = next((a for a in ARGS if not a.startswith("--") and a != (ARGS[ARGS.index("--out") + 1] if "--out" in ARGS else None)
            and a != (ARGS[ARGS.index("--boot") + 1] if "--boot" in ARGS else None)), None)
OUT = Path(ARGS[ARGS.index("--out") + 1]) if "--out" in ARGS else ROOT / "research/results/team_analysis.md"
BOOT = int(ARGS[ARGS.index("--boot") + 1]) if "--boot" in ARGS else 300
ENROL = 3
rng = random.Random(0)


def load(path):
    txt = Path(path).read_text(encoding="utf-8").strip()
    recs = json.loads(txt) if txt.startswith("[") else [json.loads(x) for x in txt.splitlines() if x.strip()]
    return [r for r in recs if r.get("meta")]


def metrics(gen, imp):
    """gen, imp: điểm KHOẢNG CÁCH (thấp = giống chủ). -> (EER, FAR@FRR5%)"""
    gen, imp = np.asarray(gen, float), np.asarray(imp, float)
    ths = np.unique(np.concatenate([gen, imp]))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return (frr[i] + far[i]) / 2, float((imp <= np.quantile(gen, 0.95)).mean())


def boot_ci(per, n=BOOT):
    ps = sorted(per)
    est = metrics(np.concatenate([per[p][0] for p in ps]), np.concatenate([per[p][1] for p in ps]))
    bs = []
    for _ in range(n):
        r = [rng.choice(ps) for _ in ps]
        bs.append(metrics(np.concatenate([per[p][0] for p in r]), np.concatenate([per[p][1] for p in r])))
    lo, hi = np.quantile(bs, 0.025, axis=0), np.quantile(bs, 0.975, axis=0)
    return est, lo, hi


recs = load(SRC) if SRC else sys.exit(__doc__)
recs.sort(key=lambda r: r["created_at"])
gen_by = defaultdict(list)   # chủ -> phiên người thật của chính họ (theo thời gian)
imp_by = defaultdict(list)   # chủ -> phiên kẻ gian được chỉ định nhắm vào ví của họ
bots = []
for r in recs:
    m = r["meta"]
    if m["role"] == "genuine":
        gen_by[m["participant_id"]].append(r)
    elif m["role"] == "impostor":
        imp_by[r["user_id"]].append(r)
    elif m["role"] == "bot":
        bots.append(r)
L = ["# Phân tích dữ liệu của đội", "",
     f"{len(recs)} phiên có `meta`: {sum(len(v) for v in gen_by.values())} phiên chủ ({len(gen_by)} người), "
     f"{sum(len(v) for v in imp_by.values())} phiên kẻ gian được chỉ định, {len(bots)} phiên bot. Khoảng tin cậy 95% bootstrap theo người ({BOOT} lần).", ""]


def split_owner(rs):
    s1 = [r for r in rs if r["meta"]["sitting"] == 1]
    return s1[:ENROL], s1[ENROL:], [r for r in rs if r["meta"]["sitting"] >= 2]


def keyset(f, pref):
    return {k: v for k, v in f.items() if k.startswith(pref)}


# ---- T1 ----
def t1(feature_filter=lambda f: f, label="PIN", identity=None):
    out = {"cùng buổi": {}, "buổi sau": {}}
    for p, rs in gen_by.items():
        enr, same, later = split_owner(rs)
        if len(enr) < ENROL:
            continue
        tpl = owner.build_template([feature_filter(r["features"]) for r in enr])
        d = lambda r: -owner.score(feature_filter(r["features"]), tpl)[0]  # noqa: E731  điểm chủ cao = giống chủ
        others = [r for q, v in gen_by.items() if q != p for r in v]
        for name, tests in (("cùng buổi", same), ("buổi sau", later)):
            if len(tests) < 3:
                continue
            out[name][p] = ([d(r) for r in tests], [d(r) for r in imp_by.get(p, [])] or None, [d(r) for r in rng.sample(others, min(30, len(others)))] or None)
    return out


L += ["## T1 — Nhận chủ cùng máy, đăng ký 3 lượt đầu buổi 1", ""]
t1res = t1()
for name, per in t1res.items():
    L.append(f"### Thử {name}")
    for kind, idx in (("kẻ gian được chỉ định (cùng ví, biết PIN)", 1), ("người khác nhập cùng PIN (KHÁC MÁY, lẫn nhiễu thiết bị)", 2)):
        sel = {p: (v[0], v[idx]) for p, v in per.items() if v[idx]}
        if len(sel) < 3:
            L.append(f"- {kind}: không đủ dữ liệu ({len(sel)} người)"); continue
        (e, f), lo, hi = boot_ci(sel)
        L.append(f"- {kind}, {len(sel)} người: EER {e:.3f} [{lo[0]:.3f}, {hi[0]:.3f}]; FAR@FRR5% {f:.3f} [{lo[1]:.3f}, {hi[1]:.3f}]")
    L.append("")

# ---- T2 ----
L += ["## T2 — Bot (luật + mô hình trong backend; ngưỡng điểm người/máy 0,5)", ""]
def h_score(r):
    h = human.score(r["features"])[0]
    p = human_model.predict(r["raw"])
    return h if p is None else min(h, p)
humans = [r for v in gen_by.values() for r in v]
if humans and bots:
    fp = np.mean([h_score(r) < 0.5 for r in humans])
    L.append(f"Chặn nhầm người thật: {fp:.3f} ({len(humans)} phiên)")
    by_t = defaultdict(list)
    for r in bots:
        by_t[r["meta"].get("tactic")].append(h_score(r) < 0.5)
    for t, v in sorted(by_t.items(), key=lambda kv: str(kv[0])):
        L.append(f"- chiến thuật {t}: bắt {np.mean(v):.3f} ({len(v)} phiên bot)")
else:
    L.append("Không đủ dữ liệu (cần phiên người và phiên bot).")
L.append("")

# ---- T3 ----
L += ["## T3 — Phát lại: chặn nhầm chủ theo độ dài lịch sử (ngưỡng backend)", ""]
bins = {"1-3 phiên cũ": [], "4-8": [], "9+": []}
for rs in gen_by.values():
    fs = [r["features"] for r in rs]
    for i in range(1, len(fs)):
        flag = replay.is_replay(fs[i], fs[max(0, i - 50):i])
        bins["1-3 phiên cũ" if i <= 3 else "4-8" if i <= 8 else "9+"].append(flag)
for k, v in bins.items():
    L.append(f"- {k}: {np.mean(v):.4f} ({len(v)} lượt)" if v else f"- {k}: không có dữ liệu")
L.append("")

# ---- T4 ----
L += ["## T4 — Gộp PIN + câu thử thách so với riêng PIN", ""]
has_ch = {p: [r for r in rs if "fld_challenge_gap_mean" in r["features"]] for p, rs in gen_by.items()}
if sum(len(v) >= 8 for v in has_ch.values()) >= 3:
    saved = owner.is_identity_feature
    owner.is_identity_feature = lambda k: k.startswith(("pin_", "fld_challenge_gap", "vi_tone_late", "vi_delete_rate"))
    try:
        g_old = {p: [r for r in rs] for p, rs in has_ch.items()}
        gen_by_backup = dict(gen_by)
        gen_by.clear(); gen_by.update({p: v for p, v in g_old.items() if len(v) >= 8})
        for label, flt in (("riêng PIN", lambda f: keyset(f, "pin_")),
                           ("PIN + câu", lambda f: {k: v for k, v in f.items() if k.startswith(("pin_", "fld_challenge_gap", "vi_tone_late", "vi_delete_rate"))})):
            per = {p: (v[0], v[2]) for p, v in t1(flt).get("buổi sau", {}).items() if v[2]}
            if len(per) >= 3:
                (e, f), lo, hi = boot_ci(per)
                L.append(f"- {label}, {len(per)} người (kẻ gian = người khác): EER {e:.3f} [{lo[0]:.3f}, {hi[0]:.3f}]; FAR@FRR5% {f:.3f} [{lo[1]:.3f}, {hi[1]:.3f}]")
            else:
                L.append(f"- {label}: không đủ dữ liệu")
        gen_by.clear(); gen_by.update(gen_by_backup)
    finally:
        owner.is_identity_feature = saved
else:
    L.append("Chưa đủ phiên có ô `challenge` (cần ≥ 3 người, mỗi người ≥ 8 phiên có câu). Trang thu `#/collect` chưa có bước gõ câu.")
L.append("")

# ---- T5 ----
L += ["## T5 — Ổn định kiểu gõ tiếng Việt giữa các buổi", ""]
tl = {p: {s: np.mean([r["features"]["vi_tone_late"] for r in rs if r["meta"]["sitting"] == s and "vi_tone_late" in r["features"]] or [np.nan])
          for s in (1, 2)} for p, rs in gen_by.items()}
pairs = [(v[1], v[2]) for v in tl.values() if not (np.isnan(v[1]) or np.isnan(v[2]))]
if len(pairs) >= 6:
    a, b = np.array(pairs).T
    L.append(f"- `vi_tone_late` buổi 1 và 2: tương quan {np.corrcoef(a, b)[0, 1]:+.2f} trên {len(pairs)} người (cao và dương = ổn định; cần ≥ 0,5 mới đáng dùng)")
else:
    L.append(f"- Chưa đủ dữ liệu `vi_tone_late` ở cả 2 buổi ({len(pairs)} người; cần ≥ 6).")
cov = [r["features"]["vi_ime_coverage"] for rs in gen_by.values() for r in rs if "vi_ime_coverage" in r["features"]]
if cov:
    L.append(f"- `vi_ime_coverage` của người thật: trung bình {np.mean(cov):.2f}, {np.mean(np.array(cov) == 0):.1%} phiên bằng 0 (sẽ bị cờ `challenge_no_ime`) trên {len(cov)} phiên")
L.append("")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
