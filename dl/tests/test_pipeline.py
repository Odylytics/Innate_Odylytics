import numpy as np
import torch

from innate_dl.history import KEYS
from data import episodes, splits, synth, tensors
from eval import calibrate, metrics
from export import to_numpy, verify_parity
from models.innate4 import Innate4LayerNet


def _table(seed=0, people=10):
    recs = synth.make(n_people=people, n_per=10, n_bots=20, seed=seed)
    m, s = tensors.fit_norm(recs)
    return tensors.Table(recs, m, s), m, s


def test_synth_history_has_every_key_and_gaps():
    t, *_ = _table()
    h = [r.hist for r in t.records if r.role == "genuine" and r.person == "p00"]
    assert all(set(x) == set(KEYS) for x in h)
    assert sorted(x["n_sessions_total"] for x in h) == list(range(10))  # counted by time order
    assert any(x["dt_prev_session_sec"] and x["dt_prev_session_sec"] > 3600 for x in h)


def test_splits_are_person_disjoint_and_gallery_is_genuine_and_earlier():
    t, *_ = _table()
    tr, va, te = splits.person_split([r.person for r in t.records if r.role == "genuine"])
    assert not (tr & va or tr & te or va & te)
    ep = episodes.make(t, te, ks=[3], n_imp=1)
    for i in range(len(ep)):
        gal = [t.records[j] for j in ep.gal[i][: int(ep.mask[i].sum())]]
        assert all(g.person == ep.person[i] and g.role == "genuine" for g in gal)  # no impostor/bot in a gallery
        if ep.y[i]:
            assert t.t[ep.q[i]] > max(t.t[ep.gal[i][: int(ep.mask[i].sum())]])  # time split: genuine query is later than the gallery
        else:
            assert t.records[ep.q[i]].person != ep.person[i]


def test_metrics():
    pos, neg = np.linspace(0.6, 1, 50), np.linspace(0, 0.4, 50)
    assert metrics.eer(pos, neg) == 0 and metrics.far_at_frr(pos, neg) == 0 and metrics.gini(pos, neg) == 1
    rng = np.random.default_rng(0)
    p, n = rng.normal(1, 1, 400), rng.normal(0, 1, 400)
    assert 0.2 < metrics.eer(p, n) < 0.4
    tau = calibrate.owner_tau(np.concatenate([p, n]) / 10 + 0.5, np.r_[np.ones(400), np.zeros(400)], np.full(800, 3), np.full(800, 5.0))
    assert tau["3"]["gt1h"] > 0 and tau["2"]["all"] == 0.5  # an empty bucket falls back to 0.5


def test_numpy_runtime_matches_torch_within_1e5(tmp_path):
    t, m, s = _table()
    torch.manual_seed(1)
    model = Innate4LayerNet()
    tau = {k: {"le1h": 0.5, "gt1h": 0.5, "all": 0.5} for k in ("2", "3", "4", "5")}
    b = to_numpy.export(model, tmp_path, m, s, tau, 0.5, synthetic=True)
    r = verify_parity.verify(model, b, t)
    assert r["ok"], r


def test_dry_run_end_to_end(tmp_path):
    import dryrun
    res = dryrun.run(people=12, epochs=2, out=tmp_path, log=lambda *_: None)
    assert res["parity"]["ok"] and res["runtime"]["genuine"]["k"] == 5 and res["runtime"]["bot"]["human"] < res["runtime"]["genuine"]["human"]
    assert (tmp_path / "bundle" / "weights.npz").exists()
