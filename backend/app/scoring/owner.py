"""Model 2 version 1: compare against the template with scaled Manhattan distance (Killourhy & Maxion 2009)."""

import json
import math
import os
from pathlib import Path
from statistics import fmean, stdev, variance

# Standard-deviation floor: 3–5 enrollment attempts give a very noisy sd; the floor keeps a "too stable" feature from dominating the score.
_SD_FLOOR = {"pin_hold": 15.0, "pin_flight": 25.0, "pin_total": 80.0, "pin_dx": 0.05, "pin_dy": 0.05}

ALPHA = 0.1  # template update rate
DRIFT_CAP = 1.0  # the template must not drift more than 1 sd from enrollment (against gradual "teaching")
# E3 (StrokePIN): class-balanced Platt, score = 1/(1+exp(K*(d-D0))). Default is "legacy" (d=2 -> 0.5): Platt only changes the fallback path and breaks the new-recipient flow, see research/results/e24_platt_map.md
_MAP = {"platt": (1.216, 1.143), "legacy": (2.0, 2.0)}
MAP_K, MAP_D0 = _MAP[os.environ.get("NHIP_OWNER_MAP", "legacy")]
FREEZE_DRIFT = 0.5  # E7: mean drift > 0.5 sd freezes the template + sets the "frozen" flag; authenticated re-enrollment is needed


def is_identity_feature(k: str) -> bool:
    # swipe_*: E19 (Touchalytics) gives AUC ~0.5 when identifying the owner with 5 swipe features (even same day, same task): only adds noise
    return not k.startswith(("screen_", "swipe_", "vi_")) and k not in (
        "tap_w_std", "fld_set_text_frac", "fld_amount_set_text",
        "fld_challenge_set_text", "fld_challenge_paste", "fld_challenge_token_bad")


def _floor(k: str, mu: float) -> float:
    base = next((v for p, v in _SD_FLOOR.items() if k.startswith(p)), 0.0)
    return max(base, 0.1 * abs(mu), 1e-6)


def _load_prior() -> dict:
    """Population within-person variance for TIMING features (research/experiments/make_population_prior.py)."""
    try:
        if os.environ.get("NHIP_POP_PRIOR", "on") == "off":
            return {}
        return json.loads((Path(__file__).parent / "population_prior.json").read_text(encoding="utf-8"))
    except Exception:  # file missing: use the floored sd as before
        return {}


_PRIOR = _load_prior()


def _sd(k: str, xs: list[float], mu: float, prior_var: dict[str, float]) -> float:
    """Shrinkage (E2/E10): for timing features with a prior, pull the variance estimated from a few samples toward the population variance.
    Other features (off-center...) keep the floored sd: shrinkage makes off-center worse (E10).
    """
    pv = prior_var.get(k)
    if pv is None or len(xs) < 2:
        return max(stdev(xs), _floor(k, mu))
    nu, n = _PRIOR.get("nu", 5), len(xs)
    return math.sqrt(((n - 1) * variance(xs) + nu * pv) / (n - 1 + nu))


def build_template(feature_list: list[dict[str, float]]) -> dict:
    keys = set.intersection(*({k for k in f if is_identity_feature(k)} for f in feature_list))
    mu = {k: fmean(f[k] for f in feature_list) for k in keys}
    prior_var = dict(_PRIOR.get("within_var", {}))
    # total entry time depends on PIN length: use the prior only when the PIN has exactly the number of keys of the source data
    n = _PRIOR.get("n_taps", 6)
    if f"pin_hold_{n - 1}" not in keys or f"pin_hold_{n}" in keys:
        prior_var.pop("pin_total", None)
    sd = {k: _sd(k, [f[k] for f in feature_list], mu[k], prior_var) for k in keys}
    return {"mu": mu, "sd": sd, "mu0": dict(mu), "n": len(feature_list), "updates": 0}


def missing_pin_evidence(features: dict[str, float], tpl: dict) -> bool:
    """The session lacks the PIN rhythm that the template was built from (PIN skipped, PIN of a different length)."""
    return any(k.startswith("pin_") and k not in features for k in tpl["mu"])


def score(features: dict[str, float], tpl: dict) -> tuple[float | None, dict[str, float]]:
    z = {k: (features[k] - tpl["mu"][k]) / tpl["sd"][k] for k in tpl["mu"] if k in features}
    if missing_pin_evidence(features, tpl):
        return 0.0, z  # enrolled but no PIN evidence: treated as a mismatch, not "neutral"
    if not z:
        return None, z
    d = fmean(abs(v) for v in z.values())
    # shortcut: Platt fitted on StrokePIN (E3), not team data; refit when real data is available
    return 1 / (1 + math.exp(min(MAP_K * (d - MAP_D0), 700.0))), z  # prevent overflow when the session is very far off (previously OverflowError => 500)


def drift(tpl: dict) -> float:
    """Mean drift of the template since enrollment, in sd units."""
    return fmean(abs(tpl["mu"][k] - tpl["mu0"][k]) / tpl["sd"][k] for k in tpl["mu"])


def update(tpl: dict, features: dict[str, float]) -> dict:
    if tpl.get("frozen"):
        return tpl
    mu = dict(tpl["mu"])
    for k in mu:
        if k in features:
            moved = mu[k] + ALPHA * (features[k] - mu[k])
            lo = tpl["mu0"][k] - DRIFT_CAP * tpl["sd"][k]
            hi = tpl["mu0"][k] + DRIFT_CAP * tpl["sd"][k]
            mu[k] = min(max(moved, lo), hi)
    new = {**tpl, "mu": mu, "updates": tpl["updates"] + 1}
    return {**new, "frozen": True} if drift(new) > FREEZE_DRIFT else new


def consistency(feature_list: list[dict[str, float]]) -> float | None:
    """Rhythm stability at enrollment: each attempt is scored against the template built from the other attempts (leave-one-out), then averaged.
    High = the person types consistently across attempts. Not the accuracy of recognizing a person (see E30 for FAR by number of attempts)."""
    if len(feature_list) < 3:  # the template from the remaining attempts needs >= 2 attempts to have a standard deviation
        return None
    scores = [score(f, build_template(feature_list[:i] + feature_list[i + 1:]))[0] for i, f in enumerate(feature_list)]
    scores = [s for s in scores if s is not None]
    return round(fmean(scores), 3) if scores else None
