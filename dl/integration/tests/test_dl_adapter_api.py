"""dl_adapter: NumPy runtime of the 4-layer model. Uses a RANDOM-weight bundle (shape check, wiring, fallbacks); numerical
parity with PyTorch is checked in training/ (export/verify_parity.py)."""

import json
import random

import numpy as np
import pytest

from app.db import SessionLocal, TouchSession
from app.scoring import dl_adapter as A
from tests.synth import IMPOSTOR, OWNER, human_session
from tests.test_api import H, _post_session, _score, client  # noqa: F401


def _shapes(nf=len(A.F_NAMES)):
    s = {"att_c": (2,), "att_t": (1,), "f_mean": (nf,), "f_std": (nf,)}
    for k in (1, 3, 5):
        s[f"conv{k}.weight"], s[f"conv{k}.bias"] = (32, A.N_CONT * A.G, k), (32,)
    lin = {"proj": (64, 96), "wq": (96, 96), "wk": (96, 96), "wv": (96, 96), "wo": (96, 96), "att1": (48, 96), "att2": (1, 48),
           "e_head": (64, 192), "u_head": (32, 192), "own1": (16, 10), "own2": (1, 16), "hum1": (32, 32 + nf + A.N_BURST), "hum2": (1, 32)}
    for n, sh in lin.items():
        s[n + ".weight"], s[n + ".bias"] = sh, sh[:1]
    for n, d in (("ln1", 64), ("ln2", 96)):
        s[n + ".weight"], s[n + ".bias"] = (d,), (d,)
    for g in ("gru_f", "gru_b"):
        s[g + ".weight_ih"], s[g + ".weight_hh"], s[g + ".bias_ih"], s[g + ".bias_hh"] = (144, 64), (144, 48), (144,), (144,)
    return s


@pytest.fixture
def bundle(tmp_path):
    rng = np.random.default_rng(0)
    w = {k: (rng.normal(0, 0.1, sh) if k != "f_std" else np.ones(sh)).astype(np.float32) for k, sh in _shapes().items()}
    np.savez(tmp_path / "weights.npz", **w)
    tau = {k: {"le1h": 0.5, "gt1h": 0.5, "all": 0.5} for k in ("2", "3", "4", "5")}
    (tmp_path / "manifest.json").write_text(json.dumps({"version": "test", "f_names": A.F_NAMES, "human": {"threshold": 0.5}, "owner": {"tau": tau}}))
    return tmp_path


def _env(monkeypatch, bundle, owner="lgbm", human="lgbm", shadow="0"):
    monkeypatch.setenv("NHIP_DL_BUNDLE", str(bundle))
    monkeypatch.setenv("NHIP_OWNER_BACKEND", owner)
    monkeypatch.setenv("NHIP_HUMAN_BACKEND", human)
    monkeypatch.setenv("NHIP_DL_SHADOW", shadow)
    A.reset()


def _enrolled_user(client, name, rng):  # noqa: F811
    for _ in range(4):
        sid = _post_session(client, human_session(name, IMPOSTOR, rng))
        assert client.post(f"/v1/users/{name}/enroll", json={"session_id": sid, "keep_open": True}, headers=H).status_code == 200
    client.post(f"/v1/users/{name}/enroll/finish", headers=H)


def _result(sid):
    with SessionLocal() as db:
        return db.get(TouchSession, sid).result


def test_preprocessing_shapes_and_no_forbidden_channels():
    raw = human_session("u", OWNER, random.Random(1))
    x = A.seq_tensor(raw)
    assert x.shape == (A.L_MAX, 10) and x[:, 9].sum() == 4 and A.CHANNELS[9] == "mask"
    assert not {"w", "h", "pressure"} & set(A.CHANNELS)
    assert A.ctx_vector(None).shape == (A.N_CTX,) and A.ctx_vector({"same_device_as_enroll": None})[12] == 0.5


def test_default_is_off_and_health_shape_kept(client, monkeypatch):  # noqa: F811
    for v in ("NHIP_DL_SHADOW", "NHIP_OWNER_BACKEND", "NHIP_HUMAN_BACKEND"):
        monkeypatch.delenv(v, raising=False)
    h = client.get("/health").json()
    assert set(h["models"]) == {"human", "owner"} and h["dl_pipeline"]["shadow"] is False


def test_shadow_logs_without_changing_the_decision(client, bundle, monkeypatch):  # noqa: F811
    rng = random.Random(11)
    _enrolled_user(client, "dl_shadow", rng)
    sid = _post_session(client, human_session("dl_shadow", IMPOSTOR, rng))  # not allowed => the template is not updated between the two scores
    _env(monkeypatch, bundle, shadow="0")
    base = _score(client, sid, amount=1000)
    assert "shadow" not in (_result(sid) or {})
    _env(monkeypatch, bundle, shadow="1")
    shadowed = _score(client, sid, amount=1000)
    assert shadowed == base and "shadow" not in shadowed  # response schema is unchanged
    sh = _result(sid)["shadow"]["dl"]
    assert sh["k"] == 4 and 0 <= sh["human"] <= 1 and 0 <= sh["owner"] <= 1 and _result(sid)["shadow"]["bundle"] == "test"


def test_dl_backend_replaces_owner_score(client, bundle, monkeypatch):  # noqa: F811
    rng = random.Random(12)
    _enrolled_user(client, "dl_live", rng)
    sid = _post_session(client, human_session("dl_live", IMPOSTOR, rng))
    _env(monkeypatch, bundle, owner="dl", human="dl", shadow="1")
    out = _score(client, sid, amount=1000)
    dl = _result(sid)["shadow"]["dl"]
    assert out["owner_match"] == round(dl["owner"], 3)


@pytest.mark.parametrize("case", ["missing_dir", "corrupt"])
def test_fallback_when_bundle_missing_or_broken(client, tmp_path, monkeypatch, case):  # noqa: F811
    rng = random.Random(13)
    name = f"dl_fb_{case}"
    _enrolled_user(client, name, rng)
    sid = _post_session(client, human_session(name, IMPOSTOR, rng))
    _env(monkeypatch, tmp_path / "nope", shadow="0")
    base = _score(client, sid, amount=1000)  # lgbm/rule path
    if case == "corrupt":
        (tmp_path / "manifest.json").write_text("{not json")
        _env(monkeypatch, tmp_path, owner="dl", human="dl", shadow="1")
    else:
        _env(monkeypatch, tmp_path / "nope", owner="dl", human="dl", shadow="1")
    assert _score(client, sid, amount=1000) == base
    assert "shadow" not in _result(sid) and client.get("/health").json()["dl_pipeline"]["bundle"] is False
