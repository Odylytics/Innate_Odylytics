"""E5b: hiệu chỉnh kiểm tra phát lại trên NGƯỜI THẬT (StrokePIN), dùng chính replay.distance của backend.

Lịch sử của tài khoản = các lượt nhập CÙNG PIN của CÙNG người (~5 lượt; người dùng thật nhập một PIN).
 - Người thật: mỗi lượt đối chiếu với các lượt còn lại cùng nhóm -> khoảng cách gần nhất. Ngưỡng nào thì bị coi nhầm là phát lại?
 - Phát lại: lấy một lượt trong lịch sử, thêm nhiễu thời gian ±n và toạ độ ±max(0.02, 0.4n) bề rộng phím (như E5, đổi sang đơn vị
   bề rộng phím để không phụ thuộc thiết bị), đối chiếu với toàn bộ lịch sử (có cả bản gốc). Bắt được bao nhiêu?
Lịch sử chỉ ~4 lượt nên KHÔNG đo được hiệu ứng "nhiều phiên cũ làm tăng FPR" của E5 (mất ở PIN 4 số, lịch sử 200): xem giới hạn.
"""

import copy
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, replay  # noqa: E402
import strokepin_loader  # noqa: E402

SEED, NOISES, CUR_THR = 0, (0.025, 0.05, 0.10, 0.15, 0.20, 0.30), replay.REPLAY_THRESHOLD
rng = random.Random(SEED)
S = strokepin_loader.load()
grp = defaultdict(list)
for e in S:
    grp[(e["user"], e["pin"])].append(e)
grp = {k: v for k, v in grp.items() if len(v) >= 4}


def replay_of(sess, noise):
    s = copy.deepcopy(sess)
    taps, t = sorted(s["pin_taps"], key=lambda x: x["t_down"]), 0.0
    jit = max(0.02, 0.4 * noise)
    for i, tap in enumerate(taps):
        hold = (tap["t_up"] - tap["t_down"]) * rng.uniform(1 - noise, 1 + noise)
        gap = (taps[i + 1]["t_down"] - tap["t_up"]) * rng.uniform(1 - noise, 1 + noise) if i < len(taps) - 1 else 0
        tap["x"] += rng.uniform(-jit, jit) * tap["key_w"]
        tap["y"] += rng.uniform(-jit, jit) * tap["key_h"]
        tap["t_down"], tap["t_up"] = t, t + hold
        t += hold + max(gap, 0)
    s["pin_taps"] = taps
    return s


def nearest(f, hist):
    ds = [d for h in hist if (d := replay.distance(f, h)) is not None]
    return min(ds) if ds else np.inf


# 1) người thật mới vs lịch sử, theo kích thước lịch sử
gen = {h: [] for h in (2, 3, 4)}  # mỗi cặp ~5 lượt nên lịch sử tối đa 4
for (u, p), es in grp.items():
    for i, e in enumerate(es):
        others = [x["f"] if "f" in x else features.extract(x["session"]) for j, x in enumerate(es) if j != i]
        f = features.extract(e["session"])
        for h in gen:
            if len(others) >= h:
                gen[h].append(nearest(f, rng.sample(others, h)))
allg = np.concatenate([np.array(v) for v in gen.values()])
thr1 = float(np.quantile(allg, 0.01))
thr5 = float(np.quantile(allg, 0.05))

# 2) phát lại vs toàn bộ lịch sử (có bản gốc)
rep = {n: [] for n in NOISES}
for (u, p), es in grp.items():
    hist = [features.extract(x["session"]) for x in es]
    src = rng.choice(es)
    for n in NOISES:
        rep[n].append(nearest(features.extract(replay_of(src["session"], n)), hist))

lines = ["# E5b — hiệu chỉnh kiểm tra phát lại trên người thật (StrokePIN)", "",
         f"{len(grp)} cặp (người, PIN), mỗi cặp ~5 lượt cùng PIN. Ngưỡng hiện tại trong backend: **{CUR_THR}** "
         "(chọn trên dữ liệu giả ở E5). Khoảng cách = `replay.distance` của backend.", "",
         "## Người thật mới có bị coi là phát lại không? (khoảng cách gần nhất tới lịch sử của chính họ)", "",
         "| Số phiên cũ đem so | Số lượt thử | Trung vị khoảng cách | FPR tại ngưỡng hiện tại | FPR tại 0.5x ngưỡng |", "|---|---|---|---|---|"]
for h, v in gen.items():
    a = np.array(v)
    lines.append(f"| {h} | {len(a)} | {np.median(a):.3f} | {(a < CUR_THR).mean():.4f} | {(a < CUR_THR / 2).mean():.4f} |")
q = {x: float(np.quantile(allg, x)) for x in (0.001, 0.005, 0.01, 0.05)}
slope = float((np.array(gen[4]) < CUR_THR).mean() - (np.array(gen[2]) < CUR_THR).mean()) / 2
fpr50 = float((np.array(gen[4]) < CUR_THR).mean()) + slope * (50 - 4)
lines += ["", f"Phân vị khoảng cách người thật: 0,1% = {q[0.001]:.3f}; 0,5% = {q[0.005]:.3f}; 1% = {q[0.01]:.3f}; 5% = {q[0.05]:.3f}. "
          f"Khoảng cách trung vị của phiên phát lại theo nhiễu: " + ", ".join(f"±{int(n*1000)/10}% -> {np.median(rep[n]):.3f}" for n in NOISES) + ".", "",
          f"**Ngoại suy tuyến tính** FPR theo số phiên cũ (chỉ có dữ liệu tới 4): ~{slope*100:.3f} điểm phần trăm mỗi phiên cũ thêm, nên với 50 phiên khoảng **{fpr50:.1%}** "
          "(không đo được: đây là suy đoán, lịch sử trong dữ liệu chỉ ~4 lượt, ngoại suy rất xa nên chỉ để tham khảo).", "",
          f"Khoảng cách người thật: phân vị 1% = **{thr1:.3f}**, 5% = {thr5:.3f}, trung vị = {np.median(allg):.3f}.", "",
          "## Bắt được bao nhiêu phiên phát lại (kẻ tấn công thích nghi: nhiễu thời gian ±n, toạ độ ±max(0.02, 0.4n) bề rộng phím)", "",
          "| Nhiễu ±n | " + " | ".join(f"{int(n*1000)/10}%" for n in NOISES) + " |", "|---|" + "---|" * len(NOISES),
          f"| Ngưỡng hiện tại ({CUR_THR}) | " + " | ".join(f"{(np.array(rep[n]) < CUR_THR).mean():.2f}" for n in NOISES) + " |",
          f"| Ngưỡng FPR 1% ({thr1:.3f}) | " + " | ".join(f"{(np.array(rep[n]) < thr1).mean():.2f}" for n in NOISES) + " |",
          f"| Ngưỡng FPR 5% ({thr5:.3f}) | " + " | ".join(f"{(np.array(rep[n]) < thr5).mean():.2f}" for n in NOISES) + " |", ""]
lines += ["## Đánh đổi theo ngưỡng (FPR đo ở 2/3/4 phiên cũ; ngoại suy tuyến tính tới 50; tỷ lệ bắt theo nhiễu)", "",
          "| Ngưỡng | FPR @2 | FPR @4 | FPR @50 (ngoại suy) | " + " | ".join(f"bắt ±{int(n*1000)/10}%" for n in NOISES) + " |",
          "|---|---|---|---|" + "---|" * len(NOISES)]
for th in (0.05, 0.06, 0.07, 0.085, 0.094):
    f2, f4 = float((np.array(gen[2]) < th).mean()), float((np.array(gen[4]) < th).mean())
    lines.append(f"| {th} | {f2:.4f} | {f4:.4f} | {f4 + (f4 - f2) / 2 * 46:.1%} | " + " | ".join(f"{(np.array(rep[n]) < th).mean():.2f}" for n in NOISES) + " |")
lines.append("")
(ROOT / "research/results/e5b_replay_real.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
