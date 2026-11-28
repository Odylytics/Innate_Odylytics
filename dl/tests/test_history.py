import datetime as dt
import json

from data import ingest
from innate_dl import history
from innate_dl.history import Prior

T0 = dt.datetime(2026, 11, 27, 10, 0, tzinfo=dt.timezone.utc)
at = lambda sec, dev="d1", enr=False, act=None: Prior(T0 + dt.timedelta(seconds=sec), dev, enr, act)  # noqa: E731


def test_compute_counts_and_gaps():
    prior = [at(0, enr=True), at(60, enr=True), at(150, enr=True), at(4000, "d2", act="hold")]
    h = history.compute(prior, "d1", T0 + dt.timedelta(seconds=4100), {"retries": 2, "client_dt_prev_ms": 1500.0})
    assert h["n_enroll"] == 3 and h["n_sessions_total"] == 4
    assert h["n_attempts_10m"] == 1 and h["n_attempts_1h"] == 1 and h["n_attempts_24h"] == 4
    assert h["dt_prev_session_sec"] == 100 and h["dt_last_enroll_sec"] == 3950 and h["enroll_span_sec"] == 150
    assert h["attempt_index_in_sitting"] == 2  # a 3850 s pause split the sittings
    assert h["n_recent_flagged"] == 1 and h["n_distinct_devices"] == 2 and h["same_device_as_enroll"] is True
    assert h["client_retries"] == 2 and h["client_dt_prev_ms"] == 1500.0 and set(h) == set(history.KEYS)


def test_first_session_and_naive_datetimes():
    h = history.compute([], "d1", T0)
    assert h["n_sessions_total"] == 0 and h["dt_prev_session_sec"] is None and h["same_device_as_enroll"] is None
    assert history.compute([Prior(T0.replace(tzinfo=None), "d1", True, None)], "d1", T0 + dt.timedelta(seconds=5))["dt_prev_session_sec"] == 5


def test_export_without_history_is_rebuilt_offline(tmp_path):
    """The product's /v1/export has no `history`: ingest rebuilds it from created_at/device/is_enrollment."""
    from data import synth
    recs = [r for r in synth.make(n_people=2, n_per=6, n_bots=0) if r.person == "p00"]
    rows = [{"session_id": f"s{i}", "user_id": "acct", "device_id": r.device, "created_at": dt.datetime.fromtimestamp(r.t, dt.timezone.utc).isoformat(),
             "meta": {"participant_id": "p00", "sitting": 1, "role": "genuine"}, "raw": r.raw, "is_enrollment": r.is_enrollment, "result": None}
            for i, r in enumerate(recs)]
    f = tmp_path / "export.jsonl"
    f.write_text("\n".join(json.dumps(x) for x in rows))
    out = ingest.from_export(f)
    assert [r.hist["n_sessions_total"] for r in sorted(out, key=lambda r: r.t)] == list(range(6))
