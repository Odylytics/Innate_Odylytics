"""PyTorch model -> bundle for the backend NumPy runtime: manifest.json + weights.npz (float32)."""

import datetime as dt
import json
from pathlib import Path

import numpy as np

from app.scoring.dl_adapter import F_NAMES


def export(model, out_dir: str | Path, f_mean: np.ndarray, f_std: np.ndarray, tau: dict, human_threshold: float,
           synthetic: bool = False, note: str = "") -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    w = {k: v.detach().cpu().numpy().astype(np.float32) for k, v in model.state_dict().items() if k not in ("lo", "hi")}
    w["f_mean"], w["f_std"] = f_mean.astype(np.float32), f_std.astype(np.float32)
    np.savez(out / "weights.npz", **w)
    (out / "manifest.json").write_text(json.dumps({
        "version": "innate4-" + dt.date.today().isoformat(), "created": dt.datetime.now(dt.timezone.utc).isoformat(),
        "synthetic": synthetic, "note": note, "f_names": F_NAMES, "human": {"threshold": human_threshold}, "owner": {"tau": tau},
        "n_params": int(sum(p.numel() for p in model.parameters())),
    }, indent=1), encoding="utf-8")
    return out
