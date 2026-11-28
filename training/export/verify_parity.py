"""PyTorch vs the backend NumPy runtime: max absolute difference on every layer output must be <= 1e-5.
Usage: python -m export.verify_parity <bundle_dir> <checkpoint.pt>   (the dry run calls `verify` directly)."""

import sys
from pathlib import Path

import numpy as np
import torch

from app.scoring import dl_adapter as A

TOL = 1e-5


@torch.no_grad()
def verify(model32, bundle_dir: str | Path, table, n: int = 64, tol: float = TOL) -> dict:
    """The NumPy runtime is float64, so it is compared with the model run in float64 (checks the maths, ~1e-12). `float32_dev`
    reports how far PyTorch's own float32 forward is from the runtime (rounding noise; informational)."""
    import copy
    model = copy.deepcopy(model32).double().eval()
    model32.eval()
    b = A.Bundle(Path(bundle_dir))
    W = b.W
    x = table.x[:n]
    xt = torch.from_numpy(x).double()
    e_t, u_t = model.encode(xt)
    e_n, u_n = A.encode(W, x)
    e32, u32 = model32.encode(torch.from_numpy(x))
    errs = {"e": np.abs(e_t.numpy() - e_n).max(), "u": np.abs(u_t.numpy() - u_n).max()}
    # layer 3 on a random gallery of varying size
    rng = np.random.default_rng(0)
    K = A.K_MAX
    gal_e = e_n[rng.integers(0, len(e_n), (len(e_n), K))]  # float64
    mask = (np.arange(K)[None] < rng.integers(2, K + 1, (len(e_n), 1))).astype(np.float64)
    dt = rng.uniform(0, 300, (len(e_n), K))
    v_t = model.match(e_t, torch.from_numpy(gal_e), torch.from_numpy(dt), torch.from_numpy(mask))
    v_n = A.match(W, e_n, gal_e, dt, mask)
    errs["v_match"] = np.abs(v_t.numpy() - v_n).max()
    k = mask.sum(1)
    dl = np.where(mask > 0, dt, 1e9).min(1)
    errs["owner_logit"] = np.abs(model.owner_logit(v_t, torch.from_numpy(k), torch.from_numpy(dl)).numpy() - A.owner_logit(W, v_n, k, dl)).max()
    f, c = table.f[:n].astype(np.float64), table.c[:n].astype(np.float64)
    errs["human_logit"] = np.abs(model.human_logit(u_t, torch.from_numpy(f), torch.from_numpy(c)).numpy() - A.human_logit(W, u_n, f, c)).max()
    errs["float32_dev"] = max(np.abs(e32.numpy() - e_n).max(), np.abs(u32.numpy() - u_n).max(),
                              np.abs(model32.human_logit(u32, torch.from_numpy(table.f[:n]), torch.from_numpy(table.c[:n])).numpy() - A.human_logit(W, u_n, f, c)).max())
    errs = {k_: float(v) for k_, v in errs.items()}
    errs["max"] = max(v for k_, v in errs.items() if k_ != "float32_dev")
    errs["ok"] = errs["max"] <= tol
    return errs


if __name__ == "__main__":
    sys.exit("run `python dryrun.py` (it builds the model, table and bundle, then calls verify)")
