"""innate_dl.dl_adapter with a RANDOM-weight bundle: shapes, wiring and fallbacks. Numerical parity with PyTorch: test_pipeline.py."""
import json

import numpy as np

from innate_dl import dl_adapter as A
from data import synth


def _bundle(path):
    rng = np.random.default_rng(0)
    nf = len(A.F_NAMES)
    sh = {"att_c": (2,), "att_t": (1,), "f_mean": (nf,), "f_std": (nf,)}
    for k in (1, 3, 5):
        sh[f"conv{k}.weight"], sh[f"conv{k}.bias"] = (32, A.N_CONT * A.G, k), (32,)
    for n, s in {"proj": (64, 96), "wq": (96, 96), "wk": (96, 96), "wv": (96, 96), "wo": (96, 96), "att1": (48, 96), "att2": (1, 48), "e_head": (64, 192),
                 "u_head": (32, 192), "own1": (16, 10), "own2": (1, 16), "hum1": (32, 32 + nf + A.N_BURST), "hum2": (1, 32)}.items():
        sh[n + ".weight"], sh[n + ".bias"] = s, s[:1]
    for n, d in (("ln1", 64), ("ln2", 96)):
        sh[n + ".weight"], sh[n + ".bias"] = (d,), (d,)
    for g in ("gru_f", "gru_b"):
        sh[g + ".weight_ih"], sh[g + ".weight_hh"], sh[g + ".bias_ih"], sh[g + ".bias_hh"] = (144, 64), (144, 48), (144,), (144,)
    np.savez(path / "weights.npz", **{k: (np.ones(s) if k == "f_std" else rng.normal(0, .1, s)).astype(np.float32) for k, s in sh.items()})
    tau = {k: {"le1h": .5, "gt1h": .5, "all": .5} for k in ("2", "3", "4", "5")}
    (path / "manifest.json").write_text(json.dumps({"version": "t", "f_names": A.F_NAMES, "human": {"threshold": .5}, "owner": {"tau": tau}}))


def test_preprocessing_has_no_forbidden_channels():
    r = synth.make(n_people=1, n_per=2, n_bots=0)[0]
    x = A.seq_tensor(r.raw)
    assert x.shape == (A.L_MAX, 10) and x[:, 9].sum() == 4 and not {"w", "h", "pressure"} & set(A.CHANNELS)
    assert A.ctx_vector(None).shape == (A.N_CTX,) and A.ctx_vector({"same_device_as_enroll": None})[12] == 0.5


def test_predict_and_fallbacks(tmp_path, monkeypatch):
    recs = [r for r in synth.make(n_people=1, n_per=8, n_bots=0)]
    gal = [(r.raw, r.t) for r in recs[:4]]
    monkeypatch.setenv("NHIP_DL_BUNDLE", str(tmp_path / "nope"))
    A.reset()
    assert A.predict(recs[5].raw, recs[5].hist, gal, recs[5].t) is None  # no bundle -> None (caller keeps its own path)
    _bundle(tmp_path)
    monkeypatch.setenv("NHIP_DL_BUNDLE", str(tmp_path))
    A.reset()
    out = A.predict(recs[5].raw, recs[5].hist, gal, recs[5].t)
    assert out["k"] == 4 and 0 <= out["human"] <= 1 and 0 <= out["owner"] <= 1
    assert A.predict(recs[5].raw, recs[5].hist, gal[:1], recs[5].t)["owner"] is None  # k < 2: no owner score
    (tmp_path / "manifest.json").write_text("{broken")
    A.reset()
    assert A.predict(recs[5].raw, recs[5].hist, gal, recs[5].t) is None
