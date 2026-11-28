"""END-TO-END DRY RUN on SYNTHETIC data (no scientific meaning): synth sessions with time gaps -> train Innate4LayerNet ->
eval by k and dt -> export .npz -> parity <= 1e-5 -> load the bundle with the NumPy runtime and score sessions.
Writes only to a temp dir; touches nothing in backend/ or the product.

    cd dl && uv run python dryrun.py [--people 24] [--epochs 20]
"""

import argparse
import json
import os
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path[:0] = [str(Path(__file__).parent), str(ROOT / "backend"), str(ROOT / "attacker")]

import numpy as np  # noqa: E402
import torch  # noqa: E402

from data import episodes, splits, synth, tensors  # noqa: E402
from eval import calibrate, e2e_sim, metrics  # noqa: E402
from export import to_numpy, to_onnx, verify_parity  # noqa: E402
from models.innate4 import Innate4LayerNet  # noqa: E402
from trainers import common, train_human, train_owner  # noqa: E402


def run(people=24, epochs=20, seed=0, out: Path | None = None, runtime_check=True, log=print) -> dict:
    out = out or Path(tempfile.mkdtemp(prefix="innate_dl_dryrun_"))
    torch.manual_seed(seed)
    recs = synth.make(n_people=people, n_per=12, n_bots=40 * 4, seed=seed)
    persons = sorted({r.person for r in recs if r.role == "genuine"})
    tr, va, te = splits.person_split(persons, seed=seed)
    train_recs = [r for r in recs if r.person in tr]
    mean, std = tensors.fit_norm(train_recs)
    table = tensors.Table(recs, mean, std)
    rng = random.Random(seed)
    bot_idx = [i for i, r in enumerate(recs) if r.role == "bot"]
    rng.shuffle(bot_idx)
    bot_split = {i: ("tr", "va", "te")[j % 3] for j, i in enumerate(bot_idx)}  # bots split 1/3 each
    is_h = lambda part: np.array([r.role == "genuine" and r.person in {"tr": tr, "va": va, "te": te}[part] for r in recs])  # noqa: E731
    is_b = lambda part: np.array([bot_split.get(i) == part for i in range(len(recs))])  # noqa: E731

    model = Innate4LayerNet()
    log(f"params: {sum(p.numel() for p in model.parameters()):,}")
    train_owner.train_embedding(model, table, tr, epochs=epochs, seed=seed, log=log)
    train_owner.train_matcher(model, table, tr, epochs=15, seed=seed, log=log)
    train_human.train_human(model, table, is_h("tr"), is_b("tr"), epochs=40, seed=seed, log=log)

    # ---- calibrate on validation people, evaluate on test people ----
    E, _ = common.embed_all(model, table)
    ep_va = episodes.make(table, va, ks=range(2, 7), n_imp=2, seed=1)
    ep_te = episodes.make(table, te, ks=range(2, 7), n_imp=2, seed=2)
    tau = calibrate.owner_tau(common.owner_probs(model, E, ep_va), ep_va.y, ep_va.k, ep_va.dt_last_h)
    p_h = common.human_probs(model, table)
    h_thr = calibrate.human_threshold(p_h[is_h("va")])
    p_te = common.owner_probs(model, E, ep_te)
    score = calibrate.apply_tau(p_te, ep_te.k, ep_te.dt_last_h, tau)
    rep = metrics.report(score, ep_te.y, ep_te.person, ep_te.k, ep_te.dt_last_h, n_boot=100)
    log("\nOWNER (test people, synthetic):\n" + metrics.fmt(rep))
    hb = np.concatenate([p_h[is_h("te")], p_h[is_b("te")]])
    hy = np.concatenate([np.ones(is_h("te").sum()), np.zeros(is_b("te").sum())])
    human_rep = metrics.stats(hb, hy)
    log(f"\nHUMAN vs BOT (test): EER {human_rep['eer']:.3f}  FAR@FRR5 {human_rep['far@frr5']:.3f}  Gini {human_rep['gini']:.3f}")

    # whole-system simulation with fusion.py
    cal = lambda p: np.where(p < h_thr, 0.5 * p / h_thr, 0.5 + 0.5 * (p - h_thr) / (1 - h_thr))  # noqa: E731
    g, im = ep_te.y == 1, ep_te.y == 0
    h_q = cal(p_h[ep_te.q])
    sim = e2e_sim.simulate(h_q[g], score[g], h_q[im], score[im], cal(p_h[is_b("te")]), np.full(is_b("te").sum(), 0.5))
    log("\nFUSION actions (synthetic): " + json.dumps(sim))

    # ---- export + parity ----
    bundle = to_numpy.export(model, out / "bundle", mean, std, tau, h_thr, synthetic=True, note="dry run on synthetic data")
    par = verify_parity.verify(model, bundle, table)
    log(f"\nPARITY torch vs numpy: max abs err {par['max']:.2e} (<= 1e-5: {par['ok']})  {json.dumps({k: float(f'{v:.2e}') for k, v in par.items() if k not in ('ok',)})}")
    try:
        onnx = to_onnx.export(model, out / "onnx", table)
        log(f"ONNX encoder vs onnxruntime: {onnx}")
    except Exception as e:  # ONNX is optional
        onnx = {"error": repr(e)[:200]}
        log(f"ONNX export skipped: {onnx}")

    res = {"owner": rep, "human": human_rep, "fusion": sim, "parity": par, "onnx": onnx, "bundle": str(bundle)}
    if runtime_check:
        res["runtime"] = adapter_check(bundle, recs, te, log)
    return res


def adapter_check(bundle: Path, recs, te, log=print) -> dict:
    """Load the bundle with the NumPy runtime (innate_dl/dl_adapter.py, what a backend would run) and score real-format sessions:
    gallery = first 5 entries of a test person, queries = a later genuine entry and a bot entry. The product /score is NOT involved."""
    os.environ["NHIP_DL_BUNDLE"] = str(bundle)
    from innate_dl import dl_adapter

    dl_adapter.reset()
    person = sorted(te)[0]
    mine = sorted((r for r in recs if r.person == person), key=lambda r: r.t)
    gal, q = mine[:5], mine[5]
    bot = next(r for r in recs if r.role == "bot")
    out = {}
    for name, r in (("genuine", q), ("bot", bot)):
        out[name] = dl_adapter.predict(r.raw, r.hist, [(g.raw, g.t) for g in gal], r.t)
    log("\nNUMPY RUNTIME scores: " + json.dumps(out))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--people", type=int, default=24)
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    r = run(a.people, a.epochs, a.seed)
    sys.exit(0 if r["parity"]["ok"] and r["runtime"]["genuine"] else 1)
