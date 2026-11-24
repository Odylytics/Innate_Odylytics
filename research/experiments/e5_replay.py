"""E5: phát hiện phát lại (chiến thuật 3) — bắt bao nhiêu, và từ chối nhầm chủ thật bao nhiêu?

Dữ liệu GIẢ (persona của attacker/tactics.py): chỉ kiểm chứng PHƯƠNG PHÁP và tìm ngưỡng sơ bộ,
không phải số liệu cho slide. Cần lặp lại trên phiên người thật.

Mỗi lượt thử: một tài khoản có 10 phiên cũ cùng một persona; 1 phiên thật mới (đo FPR);
một phiên phát lại từ một phiên cũ với nhiễu n ở cả thời gian lẫn toạ độ (đo tỷ lệ bắt).
Ba cách tính khoảng cách:
  rel   : sai khác tương đối trên thời gian giữ/cách phím (bản đang dùng trong replay.py)
  rel+  : rel + lệch tâm dx/dy (đổi sang thang tương đối)
  z     : |a-b| / sd của chủ (sd từ 5 phiên đăng ký, có sàn như owner.py) trên mọi đặc trưng nhận dạng
"""

import copy
import random
import sys
from pathlib import Path
from statistics import fmean

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker")]
from app.scoring import features, owner  # noqa: E402
from nhip_attacker import tactics  # noqa: E402

N_USERS, N_HIST, N_ENROLL, SEED = 300, 10, 5, 0
NOISES = [0.025, 0.05, 0.10, 0.15, 0.20, 0.30]
FPR_TARGET = 0.01


def replay_of(src: dict, noise: float, rng: random.Random) -> dict:
    """Như tactic3 nhưng tham số hoá. Kẻ tấn công thích nghi tăng nhiễu CẢ HAI: thời gian ±noise,
    toạ độ ±max(2, 40*noise) px (5% -> 2 px như tactic3, 20% -> 8 px ~ độ lệch giữa hai phiên người thật)."""
    s = copy.deepcopy(src)
    jit = max(2.0, 40 * noise)
    taps, t = sorted(s["pin_taps"], key=lambda x: x["t_down"]), 0.0
    for i, tap in enumerate(taps):
        hold = (tap["t_up"] - tap["t_down"]) * rng.uniform(1 - noise, 1 + noise)
        gap = (taps[i + 1]["t_down"] - tap["t_up"]) * rng.uniform(1 - noise, 1 + noise) if i < len(taps) - 1 else 0
        tap["x"] += rng.uniform(-jit, jit)
        tap["y"] += rng.uniform(-jit, jit)
        tap["t_down"], tap["t_up"] = t, t + hold
        t += hold + max(gap, 0)
    s["pin_taps"] = taps
    return s


def timing(f):
    return [k for k in f if k.startswith(("pin_hold_", "pin_flight_"))]


def d_rel(a, b, tpl=None):
    ks = [k for k in timing(a) if k in b]
    return fmean(abs(a[k] - b[k]) / max((abs(a[k]) + abs(b[k])) / 2, 1e-6) for k in ks)


def d_relplus(a, b, tpl=None):
    ks = [k for k in timing(a) if k in b]
    parts = [abs(a[k] - b[k]) / max((abs(a[k]) + abs(b[k])) / 2, 1e-6) for k in ks]
    # lệch tâm (đơn vị bề rộng phím): người thật khác nhau ~0.07; đổi sang thang tương đối bằng cách chia 0.4
    parts += [abs(a[k] - b[k]) / 0.4 for k in a if k.startswith(("pin_dx_", "pin_dy_")) and k in b]
    return fmean(parts)


def d_z(a, b, tpl):
    ks = [k for k in tpl["sd"] if k in a and k in b]
    return fmean(abs(a[k] - b[k]) / tpl["sd"][k] for k in ks)


DISTS = {"rel (hiện tại)": d_rel, "rel+ (thêm lệch tâm)": d_relplus, "z (theo sd của chủ)": d_z}


def run(pin_len: int):
    pin = "159357"[:pin_len] if pin_len <= 6 else "1593571593"[:pin_len]
    rng = random.Random(SEED)
    layout = tactics.DEFAULT_LAYOUT
    gen_d = {n: [] for n in DISTS}                      # khoảng cách gần nhất của phiên thật mới tới lịch sử
    rep_d = {n: {z: [] for z in NOISES} for n in DISTS}  # của phiên phát lại
    for u in range(N_USERS):
        sess = tactics.synth_owner(f"u{u}", N_HIST + 1, pin, layout, seed=SEED * 100000 + u)
        feats = [features.extract(s) for s in sess]
        hist, fresh = feats[:N_HIST], feats[N_HIST]
        tpl = owner.build_template(hist[:N_ENROLL])
        for n, d in DISTS.items():
            gen_d[n].append(min(d(fresh, h, tpl) for h in hist))
        src_i = rng.randrange(N_HIST)
        for z in NOISES:
            rep = features.extract(replay_of(sess[src_i], z, rng))
            for n, d in DISTS.items():
                rep_d[n][z].append(min(d(rep, h, tpl) for h in hist))
    out = []
    for n in DISTS:
        g = np.array(gen_d[n])
        thr = float(np.quantile(g, FPR_TARGET))  # ngưỡng để chỉ ~1% phiên thật mới bị coi là phát lại
        row = {z: float((np.array(rep_d[n][z]) < thr).mean()) for z in NOISES}
        out.append((n, thr, float((g < thr).mean()), row, float(np.median(g))))
    return out


lines = ["# E5 — phát hiện phát lại (dữ liệu giả)", "",
         f"{N_USERS} tài khoản giả, {N_HIST} phiên cũ mỗi tài khoản. Ngưỡng chọn để **chỉ ~{FPR_TARGET:.0%} phiên người thật mới bị coi là phát lại**; "
         "bảng báo tỷ lệ bắt phiên phát lại theo mức nhiễu của kẻ tấn công (thời gian ±n, toạ độ ±max(2, 40n) px). Persona giả, chỉ kiểm chứng phương pháp.", ""]
for pin_len in (4, 6):
    lines += [f"## PIN {pin_len} số", "", "| Khoảng cách | Ngưỡng | FPR | Trung vị khoảng cách người thật | " + " | ".join(f"nhiễu ±{int(z*1000)/10}%" for z in NOISES) + " |",
              "|---|---|---|---|" + "---|" * len(NOISES)]
    for n, thr, fpr, row, med in run(pin_len):
        lines.append(f"| {n} | {thr:.3f} | {fpr:.3f} | {med:.3f} | " + " | ".join(f"{row[z]:.2f}" for z in NOISES) + " |")
    lines.append("")
# FPR của backend (rel+, ngưỡng mặc định) theo số phiên cũ được đem so
THR = 0.085
lines += [f"## FPR của bản đang dùng trong backend (rel+, ngưỡng {THR}) theo số phiên cũ đem so", "",
          "| PIN | 10 phiên cũ | 50 phiên cũ | 200 phiên cũ |", "|---|---|---|---|"]
for pin_len in (4, 6):
    pin, rows = "159357"[:pin_len], {10: [], 50: [], 200: []}
    for u in range(120):
        f = [features.extract(x) for x in tactics.synth_owner(f"v{u}", 201, pin, tactics.DEFAULT_LAYOUT, seed=5000 + u)]
        for h in rows:
            rows[h].append(min(d_relplus(f[200], x) for x in f[:h]))
    lines.append(f"| {pin_len} số | " + " | ".join(f"{float((np.array(v) < THR).mean()):.3f}" for v in rows.values()) + " |")
lines.append("")
out = ROOT / "research/results/e5_replay.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
