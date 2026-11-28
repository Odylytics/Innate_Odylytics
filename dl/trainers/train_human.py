"""Human-vs-bot training (tactics 1-4 or real adb sessions as bots). The encoder trunk and e_head stay frozen (they carry identity);
only u_head and the human head are trained, so the owner embedding is not disturbed."""

import numpy as np
import torch
import torch.nn.functional as F


def train_human(model, table, human_mask: np.ndarray, bot_mask: np.ndarray, epochs: int = 40, lr: float = 3e-3, seed: int = 0, log=print):
    """human_mask / bot_mask: boolean (N,) over table rows used for training."""
    sel = np.flatnonzero(human_mask | bot_mask)
    y = torch.from_numpy(human_mask[sel].astype(np.float32))
    model.eval()
    x = torch.from_numpy(table.x[sel])  # u is recomputed each step from the frozen trunk through the (trainable) u_head only
    params = [*model.u_head.parameters(), *model.hum1.parameters(), *model.hum2.parameters()]
    opt = torch.optim.Adam(params, lr=lr)
    f, c = torch.from_numpy(table.f[sel]), torch.from_numpy(table.c[sel])
    w = torch.where(y > 0, 0.5 / y.mean(), 0.5 / (1 - y.mean()))  # class-balanced
    g = torch.Generator().manual_seed(seed)
    for ep in range(epochs):
        perm = torch.randperm(len(sel), generator=g)
        tot = 0.0
        for i in range(0, len(perm), 128):
            b = perm[i:i + 128]
            with torch.no_grad():
                pooled = model.pooled(x[b])
            u = model.u_head(pooled)
            loss = (F.binary_cross_entropy_with_logits(model.human_logit(u, f[b], c[b]), y[b], reduction="none") * w[b]).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += float(loss) * len(b)
        if ep % 10 == 0 or ep == epochs - 1:
            log(f"[human] epoch {ep:3d} bce {tot / len(sel):.4f}")
