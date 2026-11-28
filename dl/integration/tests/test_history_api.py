import datetime as dt
import random

from innate_dl import history, owner
from innate_dl.history import Prior
from tests.synth import OWNER, human_session
from tests.test_api import H, _post_session, client  # noqa: F401  (client fixture)

T0 = dt.datetime(2026, 11, 27, 10, 0, tzinfo=dt.timezone.utc)
at = lambda sec, dev="d1", enr=False, act=None: Prior(T0 + dt.timedelta(seconds=sec), dev, enr, act)  # noqa: E731


def test_compute_counts_and_gaps():
    prior = [at(0, enr=True), at(60, enr=True), at(150, enr=True), at(4000, "d2", act="hold")]
    now = T0 + dt.timedelta(seconds=4100)
    h = history.compute(prior, "d1", now, {"retries": 2, "client_dt_prev_ms": 1500.0})
    assert h["n_enroll"] == 3 and h["n_sessions_total"] == 4
    assert h["n_attempts_10m"] == 1 and h["n_attempts_1h"] == 1 and h["n_attempts_24h"] == 4
    assert h["dt_prev_session_sec"] == 100 and h["dt_last_enroll_sec"] == 3950 and h["enroll_span_sec"] == 150
    assert h["attempt_index_in_sitting"] == 2  # a 3850 s pause split the sittings
    assert h["n_recent_flagged"] == 1 and h["n_distinct_devices"] == 2 and h["same_device_as_enroll"] is True
    assert h["client_retries"] == 2 and h["client_dt_prev_ms"] == 1500.0
    assert set(h) == set(history.KEYS)


def test_compute_first_session_has_no_gaps_and_handles_naive_datetimes():
    h = history.compute([], "d1", T0)
    assert h["n_sessions_total"] == 0 and h["dt_prev_session_sec"] is None and h["same_device_as_enroll"] is None
    naive = Prior(T0.replace(tzinfo=None), "d1", True, None)
    assert history.compute([naive], "d1", T0 + dt.timedelta(seconds=5))["dt_prev_session_sec"] == 5


def test_history_stored_in_raw_not_in_features(client):  # noqa: F811
    rng = random.Random(3)
    body = {**human_session("hist1", OWNER, rng), "attempt_meta": {"flow_stage": "signup_enroll", "retries": 1, "client_dt_prev_ms": 900}}
    _post_session(client, body)
    sid = _post_session(client, human_session("hist1", OWNER, rng))
    from app.db import SessionLocal, TouchSession
    with SessionLocal() as db:
        s = db.get(TouchSession, sid)
        assert s.raw["_history"]["n_sessions_total"] == 1
        assert not any(k.startswith(("hist", "_history")) for k in s.features)
        assert all(owner.is_identity_feature(k) or k.startswith(("screen_", "swipe_", "tap_w_std")) for k in s.features)
    first = [r for r in client.get("/v1/export", headers={"X-API-Key": "test-key"}, params={"collected_only": False}).json() if r["user_id"] == "hist1"][0]
    assert first["history"]["client_retries"] == 1 and first["raw"]["attempt_meta"]["flow_stage"] == "signup_enroll"


def test_attempt_meta_validation(client):  # noqa: F811
    bad = {**human_session("hist2", OWNER, random.Random(1)), "attempt_meta": {"flow_stage": "nope"}}
    assert client.post("/v1/sessions", json=bad, headers=H).status_code == 422
    bad["attempt_meta"] = {"retries": -1}
    assert client.post("/v1/sessions", json=bad, headers=H).status_code == 422


def test_history_summary_in_account_and_user(client):  # noqa: F811
    rng = random.Random(5)
    a = client.post("/v1/accounts/signup", json={"email": "hs@example.com", "password": "matkhau1"}, headers=H).json()
    uid = a["user_id"]
    for _ in range(3):
        sid = _post_session(client, {**human_session(uid, OWNER, rng), "attempt_meta": {"flow_stage": "signup_enroll", "client_dt_prev_ms": 2000}})
        out = client.post(f"/v1/users/{uid}/enroll", json={"session_id": sid, "keep_open": True}, headers=H).json()
    hs = out["history_summary"]
    assert hs["n_entries"] == 3 and hs["client_dt_mean_ms"] == 2000 and hs["dt_mean_sec"] >= 0
    assert client.get(f"/v1/users/{uid}", headers=H).json()["history_summary"]["n_entries"] == 3
