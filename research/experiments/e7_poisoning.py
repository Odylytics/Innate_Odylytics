"""E7: tấn công đầu độc mẫu chuẩn ("dạy dần") và các cách phòng thủ.

Kẻ tấn công (kiểu Lovisotto 2020, mạnh: tạo được vector đặc trưng tuỳ ý) mỗi bước gửi một phiên nằm
SÁT RANH GIỚI cập nhật (owner >= 0.8): x = mu + d*(x_kẻ_gian - mu) với d lớn nhất vẫn được chấp nhận,
nên mẫu chuẩn bị kéo dần về phía kẻ gian. Sau n lần tiêm, đo:
  - impostor_accept: tỷ lệ phiên THẬT của kẻ gian (persona khác) có owner >= 0.5
  - genuine_accept : tỷ lệ phiên mới của chủ có owner >= 0.5
Thêm kịch bản "chủ trôi chậm": thói quen chủ đổi +15% thời gian trong 100 phiên, kiểm cái giá của việc chặn cập nhật.

Phòng thủ (đều dùng cùng quy tắc chấp nhận, khác quy tắc cập nhật):
  none      : không trần
  cap1.0sd  : bản hiện tại của owner.py (mỗi đặc trưng trôi tối đa 1 sd so với lúc đăng ký)
  cap0.5sd, cap0.25sd : trần chặt hơn
  freeze    : dừng cập nhật khi trôi trung bình > 0.5 sd (trôi có hướng), đồng thời cờ cảnh báo
Persona GIẢ (attacker/tactics.py): kiểm chứng phương pháp, không phải số liệu cho slide.
"""

import random
import sys
from pathlib import Path
from statistics import fmean

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker")]
from app.scoring import features, owner  # noqa: E402
from nhip_attacker import tactics  # noqa: E402

PIN, N_PAIRS, SEED = "159357", 100, 0
CHECKPOINTS = [0, 10, 25, 50, 100, 200]
ACCEPT, UPDATE_MIN = 0.5, 0.8  # UPDATE_MIN = ngưỡng cập nhật trong main.py


def mean_drift_sd(tpl):
    return fmean(abs(tpl["mu"][k] - tpl["mu0"][k]) / tpl["sd"][k] for k in tpl["mu"])


def make_update(name):
    def upd(tpl, f):
        if name == "freeze":
            new = _raw_update(tpl, f, 1e9)
            return new if mean_drift_sd(new) <= 0.5 else tpl
        cap = {"none": 1e9, "cap1.0sd": 1.0, "cap0.5sd": 0.5, "cap0.25sd": 0.25}[name]
        return _raw_update(tpl, f, cap)
    return upd


def _raw_update(tpl, f, cap):
    old = owner.DRIFT_CAP
    owner.DRIFT_CAP = cap
    try:
        return owner.update(tpl, f)
    finally:
        owner.DRIFT_CAP = old


def craft(tpl, target):
    """Điểm gần kẻ gian nhất trên đoạn mu -> target mà owner vẫn >= UPDATE_MIN (chia đôi)."""
    mu = tpl["mu"]
    lo, hi = 0.0, 1.0
    for _ in range(25):
        d = (lo + hi) / 2
        x = {k: mu[k] + d * (target[k] - mu[k]) for k in mu}
        s, _z = owner.score(x, tpl)
        lo, hi = (d, hi) if s >= UPDATE_MIN else (lo, d)
    return {k: mu[k] + lo * (target[k] - mu[k]) for k in mu}


def feats(sessions):
    return [features.extract(s) for s in sessions]


def rate(tpl, fs, thr=ACCEPT):
    return float(np.mean([owner.score(f, tpl)[0] >= thr for f in fs]))


DEFS = ["none", "cap1.0sd", "cap0.5sd", "cap0.25sd", "freeze"]
poison = {d: {c: {"imp": [], "gen": [], "drift": []} for c in CHECKPOINTS} for d in DEFS}
DRIFTS = [0.15, 0.30, 0.50]
drift_gen = {(d, g): [] for d in DEFS for g in DRIFTS}
drift_gen80 = {(d, g): [] for d in DEFS for g in DRIFTS}

rng = random.Random(SEED)
for i in range(N_PAIRS):
    own = tactics.synth_owner(f"o{i}", 5 + 20, PIN, tactics.DEFAULT_LAYOUT, seed=2 * i)
    imp = tactics.synth_owner(f"i{i}", 40, PIN, tactics.DEFAULT_LAYOUT, seed=2 * i + 1)
    f_enr, f_gen = feats(own[:5]), feats(own[5:])
    f_imp = feats(imp)
    base = owner.build_template(f_enr)
    target = {k: fmean(f[k] for f in f_imp if k in f) for k in base["mu"]}
    for d in DEFS:
        upd, tpl = make_update(d), base
        for n in range(max(CHECKPOINTS) + 1):
            if n in CHECKPOINTS:
                poison[d][n]["imp"].append(rate(tpl, f_imp))
                poison[d][n]["gen"].append(rate(tpl, f_gen))
                poison[d][n]["drift"].append(mean_drift_sd(tpl))
            tpl = upd(tpl, craft(tpl, target))
    # chủ trôi chậm: persona đổi thói quen +g thời gian trong 100 phiên, mỗi phiên đủ điểm thì cập nhật
    p0 = tactics._persona(random.Random(2 * i))
    for g in DRIFTS:
        for d in DEFS:
            upd, tpl, r = make_update(d), base, random.Random(i)
            for t in range(100):
                p = {**p0, "hold": p0["hold"] * (1 + g * t / 99), "flight": p0["flight"] * (1 + g * t / 99)}
                f = features.extract(tactics._persona_session(f"o{i}", p, PIN, tactics.DEFAULT_LAYOUT, r))
                if owner.score(f, tpl)[0] >= UPDATE_MIN:
                    tpl = upd(tpl, f)
            p = {**p0, "hold": p0["hold"] * (1 + g), "flight": p0["flight"] * (1 + g)}
            fresh = feats([tactics._persona_session(f"o{i}", p, PIN, tactics.DEFAULT_LAYOUT, r) for _ in range(20)])
            drift_gen[(d, g)].append(rate(tpl, fresh))
            drift_gen80[(d, g)].append(rate(tpl, fresh, UPDATE_MIN))

lines = ["# E7 — tấn công đầu độc mẫu chuẩn (dữ liệu giả)", "",
         f"{N_PAIRS} cặp (chủ, kẻ gian), kẻ tấn công tiêm phiên sát ngưỡng cập nhật (owner >= {UPDATE_MIN}). "
         f"'Chấp nhận' = owner >= {ACCEPT}. Persona giả, chỉ kiểm chứng phương pháp.", "",
         "## Tỷ lệ phiên THẬT của kẻ gian được chấp nhận sau n lần tiêm (càng thấp càng tốt)", "",
         "| Phòng thủ | " + " | ".join(f"n={c}" for c in CHECKPOINTS) + " |", "|---|" + "---|" * len(CHECKPOINTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(poison[d][c]['imp']):.2f}" for c in CHECKPOINTS) + " |")
lines += ["", "## Tỷ lệ phiên mới của chủ được chấp nhận sau n lần tiêm (càng cao càng tốt)", "",
          "| Phòng thủ | " + " | ".join(f"n={c}" for c in CHECKPOINTS) + " |", "|---|" + "---|" * len(CHECKPOINTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(poison[d][c]['gen']):.2f}" for c in CHECKPOINTS) + " |")
lines += ["", "## Trôi trung bình của mẫu chuẩn (đơn vị sd) sau n lần tiêm", "",
          "| Phòng thủ | " + " | ".join(f"n={c}" for c in CHECKPOINTS) + " |", "|---|" + "---|" * len(CHECKPOINTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(poison[d][c]['drift']):.2f}" for c in CHECKPOINTS) + " |")
lines += ["", "## Cái giá: chủ thật trôi chậm (thời gian giữ/cách phím tăng dần trong 100 phiên) — tỷ lệ phiên mới của chủ được chấp nhận", "",
          "| Phòng thủ | " + " | ".join(f"+{int(g*100)}%" for g in DRIFTS) + " |", "|---|" + "---|" * len(DRIFTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(drift_gen[(d, g)]):.2f}" for g in DRIFTS) + " |")
lines += ["", f"Cùng kịch bản, nhưng đếm là chấp nhận khi owner >= {UPDATE_MIN} (ngưỡng cập nhật; nhạy hơn với việc mẫu không theo kịp chủ):", "",
          "| Phòng thủ | " + " | ".join(f"+{int(g*100)}%" for g in DRIFTS) + " |", "|---|" + "---|" * len(DRIFTS)]
for d in DEFS:
    lines.append(f"| {d} | " + " | ".join(f"{np.mean(drift_gen80[(d, g)]):.2f}" for g in DRIFTS) + " |")
lines.append("")
out = ROOT / "research/results/e7_poisoning.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
