import random
from statistics import pstdev

import pytest

from nhip_attacker import adb, tactics

PIN = "1593"


def _holds(s):
    return [t["t_up"] - t["t_down"] for t in s["pin_taps"]]


def _offsets(s):
    return [(t["x"] - t["key_cx"], t["y"] - t["key_cy"]) for t in s["pin_taps"]]


def _valid(s):
    taps = s["pin_taps"]
    assert "".join(t["key"] for t in taps) == PIN
    assert all(t["t_up"] >= t["t_down"] >= 0 for t in taps)
    assert all(a["t_down"] <= b["t_down"] for a, b in zip(taps, taps[1:]))
    assert all(len(sw["points"]) >= 2 for sw in s["swipes"])


def test_tactic1_constant_and_centered():
    s = tactics.tactic1("u", PIN)
    _valid(s)
    assert len(set(_holds(s))) == 1
    assert all(o == (0, 0) for o in _offsets(s))


def test_tactic2_noisy_timing_but_centered():
    s = tactics.tactic2("u", PIN, rng=random.Random(1))
    _valid(s)
    assert pstdev(_holds(s)) > 5
    assert all(o == (0, 0) for o in _offsets(s))


def test_tactic3_replays_source_closely():
    src = tactics.synth_humans(1, PIN, seed=3)[0]
    s = tactics.tactic3("victim", src, random.Random(2))
    _valid(s)
    assert s["user_id"] == "victim" and "meta" not in s
    for a, b in zip(_holds(src), _holds(s)):
        assert abs(a - b) <= 0.05 * a + 1e-6
    for (ax, ay), (bx, by) in zip(_offsets(src), _offsets(s)):
        assert abs(ax - bx) <= 2 and abs(ay - by) <= 2
    assert src["user_id"] != "victim"  # không sửa phiên gốc


def test_tactic4_samples_from_population():
    pop = tactics.synth_humans(20, PIN, seed=4)
    lo = min(h for p in pop for h in _holds(p)) * 0.95
    hi = max(h for p in pop for h in _holds(p)) * 1.05
    s = tactics.tactic4("u", PIN, pop, rng=random.Random(5))
    _valid(s)
    assert all(lo <= h <= hi for h in _holds(s))
    assert any(o != (0, 0) for o in _offsets(s))


def test_generate_requires_humans_for_3_and_4():
    with pytest.raises(ValueError):
        tactics.generate(3, "u", PIN, [], random.Random())
    with pytest.raises(ValueError):
        tactics.generate(4, "u", PIN, [], random.Random())


def test_synth_owner_is_one_consistent_person():
    sessions = tactics.synth_owner("me", 5, PIN, seed=9)
    assert {s["user_id"] for s in sessions} == {"me"}
    others = tactics.synth_humans(5, PIN, seed=99)
    spread = lambda ss: pstdev([sum(_holds(s)) for s in ss])  # noqa: E731
    assert spread(sessions) < spread(others) * 2


def test_adb_dry_run_commands():
    layout = {"1": (100, 1500), "5": (540, 1700), "9": (980, 1900), "3": (980, 1500)}
    cmds = adb.attack(PIN, layout, 1, swipe=(540, 1800, 540, 900), dry_run=True)
    assert cmds[0][:3] == ["shell", "input", "swipe"]
    assert [c[3:] for c in cmds[1:]] == [["100", "1500"], ["540", "1700"], ["980", "1900"], ["980", "1500"]]
    with pytest.raises(ValueError):
        adb.attack("1234", layout, 1, dry_run=True)
