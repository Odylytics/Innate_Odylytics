"""Owner training. Stage A: embedding (layers 1-2) with batch-hard Triplet loss, negatives preferring the SAME PIN.
Stage B: set matching + owner head (layers 3-4) on episodes, embeddings frozen. Only genuine entries of train people are used
(no impostor data enters the owner model of a person, FETA)."""

import random

import numpy as np
import torch
import torch.nn.functional as F

from data import episodes
from . import common


def triplet_loss(e, person, pin, margin: float = 0.3):
    d = torch.cdist(e, e)
    same = person[:, None] == person[None, :]
    eye = torch.eye(len(e), dtype=torch.bool)
    pos = (d * (same & ~eye)).max(1).values
    neg_ok = ~same
    same_pin = neg_ok & (pin[:, None] == pin[None, :])
    cand = torch.where(same_pin.any(1, keepdim=True), same_pin, neg_ok)  # hard negatives from the same PIN when the batch has them
    neg = torch.where(cand, d, torch.full_like(d, 9.0)).min(1).values
    ok = (same & ~eye).any(1) & neg_ok.any(1)
    return F.relu(pos - neg + margin)[ok].mean() if ok.any() else d.sum() * 0


def train_embedding(model, table, people: set[str], epochs: int = 30, P: int = 8, M: int = 4, lr: float = 2e-3, seed: int = 0, log=print):
    rng = random.Random(seed)
    torch.manual_seed(seed)
    idx = {p: v for p, v in episodes.person_index(table, people).items() if len(v) >= 2}
    pid = {p: i for i, p in enumerate(sorted(idx))}
    pin_id = torch.tensor([hash(r.pin) % 10_000 for r in table.records])
    x = torch.from_numpy(table.x)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    steps = max(8, sum(len(v) for v in idx.values()) // (P * M))
    for ep in range(epochs):
        model.train()
        tot = 0.0
        for _ in range(steps):
            ps = rng.sample(sorted(idx), min(P, len(idx)))
            sel = [i for p in ps for i in rng.sample(idx[p], min(M, len(idx[p])))]
            e, _ = model.encode(x[sel])
            loss = triplet_loss(e, torch.tensor([pid[table.records[i].person] for i in sel]), pin_id[sel])
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += float(loss)
        if ep % 5 == 0 or ep == epochs - 1:
            log(f"[embed] epoch {ep:3d} triplet {tot / steps:.4f}")


def train_matcher(model, table, people: set[str], epochs: int = 15, lr: float = 3e-3, seed: int = 0, log=print):
    E, _ = common.embed_all(model, table)
    params = [*model.own1.parameters(), *model.own2.parameters(), model.att_c, model.att_t]
    opt = torch.optim.Adam(params, lr=lr)
    for ep in range(epochs):
        ep_set = episodes.make(table, people, ks=range(2, 9), n_imp=1, max_q=3, seed=seed + ep)
        y = torch.from_numpy(ep_set.y).float()
        perm = np.random.default_rng(seed + ep).permutation(len(ep_set))
        model.eval()  # layers 1-2 are frozen: no dropout/jitter
        tot = 0.0
        for i in range(0, len(perm), 128):
            sel = perm[i:i + 128]
            loss = F.binary_cross_entropy_with_logits(common.owner_logits(model, E, ep_set, sel), y[sel])
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += float(loss) * len(sel)
        if ep % 5 == 0 or ep == epochs - 1:
            log(f"[match] epoch {ep:3d} bce {tot / len(perm):.4f}")
