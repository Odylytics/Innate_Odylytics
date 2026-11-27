"""Fine-tune TypeFormer (pretrained Aalto) lên StrokePIN, triplet loss, tách theo NGƯỜI (60 train / 7 val / 30 test).
Anchor/positive: cùng người, cùng PIN (cả hai tư thế: học bất biến tư thế). Negative: người khác nhập CÙNG PIN (đúng kịch bản kẻ biết PIN).
Chọn checkpoint theo EER trên 7 người val (k=3), báo cáo cuối trên 30 người test."""
import argparse, json, random, time, warnings
from collections import defaultdict
warnings.filterwarnings("ignore")
import numpy as np, torch, common

ap = argparse.ArgumentParser()
ap.add_argument("--epochs", type=int, default=30); ap.add_argument("--lr", type=float, default=1e-4)
ap.add_argument("--steps", type=int, default=60); ap.add_argument("--bs", type=int, default=64)
ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", default="runs/ft_a")
a = ap.parse_args()
random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
d = torch.device("mps")
S = common.load_sessions()
tr, va, te = common.split_users({e["user"] for e in S})
by = defaultdict(dict)  # (pin) -> user -> [idx]
for i, e in enumerate(S):
    if e["user"] in set(tr): by[e["pin"]].setdefault(e["user"], []).append(i)
pins = [p for p, u in by.items() if len(u) >= 2]
X = torch.from_numpy(np.stack([e["x"] for e in S]))

def batch():
    A, P, N = [], [], []
    while len(A) < a.bs:
        pin = random.choice(pins); us = by[pin]; u, v = random.sample(list(us), 2)
        if len(us[u]) < 2: continue
        i, j = random.sample(us[u], 2); A.append(i); P.append(j); N.append(random.choice(us[v]))
    return [X[ix].to(d) for ix in (A, P, N)]

m = common.build_model(d)
opt = torch.optim.AdamW(m.parameters(), lr=a.lr, weight_decay=1e-4)
tl = lambda a_, p_, n_: torch.relu((a_ - p_).pow(2).sum(1) - (a_ - n_).pow(2).sum(1) + 1.0).mean()  # = TripletLoss(margin=1)
import os; os.makedirs(a.out, exist_ok=True)
best, log = 9, []
r0 = common.evaluate(m, S, va, d, ks=(3,))[3]["same_posture"][0]; print(f"epoch 0 (zero-shot) val EER {r0:.3f}")
for ep in range(1, a.epochs + 1):
    m.train(); t0 = time.time(); L = 0
    for _ in range(a.steps):
        x = batch(); opt.zero_grad(); loss = tl(*[m(t) for t in x]); loss.backward(); opt.step(); L += loss.item()
    r = common.evaluate(m, S, va, d, ks=(3,))[3]; v = (r["same_posture"][0] + r["walk"][0]) / 2
    log.append({"epoch": ep, "loss": L / a.steps, "val_eer_same": r["same_posture"][0], "val_eer_walk": r["walk"][0]})
    star = v < best
    if star: best = v; torch.save(m.state_dict(), f"{a.out}/best.pt")
    print(f"epoch {ep} loss {L/a.steps:.3f} val EER same {r['same_posture'][0]:.3f} walk {r['walk'][0]:.3f} {'*' if star else ''} ({time.time()-t0:.0f}s)", flush=True)
m.load_state_dict(torch.load(f"{a.out}/best.pt")); res = common.evaluate(m, S, te, d, ks=(2, 3, 4))
json.dump({"args": vars(a), "log": log, "test": {str(k): v for k, v in res.items()}, "split": {"train": tr, "val": va, "test": te}}, open(f"{a.out}/result.json", "w"), indent=1)
for k, r in res.items(): print("TEST k=%d same EER %.3f FAR@FRR5%% %.3f | walk EER %.3f FAR %.3f" % (k, *r["same_posture"], *r["walk"]))
