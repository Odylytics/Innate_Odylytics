import numpy as np
import torch

from data.episodes import Episodes


@torch.no_grad()
def embed_all(model, table, bs: int = 256) -> tuple[torch.Tensor, torch.Tensor]:
    """Frozen-encoder embeddings (e, u) of every table row."""
    model.eval()
    x = torch.from_numpy(table.x)
    es, us = zip(*(model.encode(x[i:i + bs]) for i in range(0, len(x), bs)))
    return torch.cat(es), torch.cat(us)


def owner_logits(model, E: torch.Tensor, ep: Episodes, sel=None) -> torch.Tensor:
    """Layers 3+4 on pre-computed embeddings."""
    sel = np.arange(len(ep)) if sel is None else sel
    gal, mask = torch.from_numpy(ep.gal[sel]), torch.from_numpy(ep.mask[sel])
    dt = torch.from_numpy(ep.dt_h[sel])
    v = model.match(E[torch.from_numpy(ep.q[sel])], E[gal], dt, mask)
    return model.owner_logit(v, mask.sum(1), torch.where(mask > 0, dt, torch.full_like(dt, 1e9)).min(1).values)


@torch.no_grad()
def owner_probs(model, E, ep: Episodes, bs: int = 2048) -> np.ndarray:
    model.eval()
    return np.concatenate([torch.sigmoid(owner_logits(model, E, ep, np.arange(i, min(i + bs, len(ep))))).numpy() for i in range(0, len(ep), bs)])


@torch.no_grad()
def human_probs(model, table, bs: int = 512) -> np.ndarray:
    model.eval()
    out = []
    for i in range(0, len(table.x), bs):
        s = slice(i, i + bs)
        _, u = model.encode(torch.from_numpy(table.x[s]))
        out.append(torch.sigmoid(model.human_logit(u, torch.from_numpy(table.f[s]), torch.from_numpy(table.c[s]))).numpy())
    return np.concatenate(out)
