"""Generate backend/app/scoring/population_prior.json from StrokePIN: WITHIN-person variance of the timing features.

For each (person, PIN, posture) with >= 2 sessions: the variance of each feature; prior = mean over all groups.
Used for shrinkage in owner.build_template (E2/E10): timing ONLY; for off-center offsets, keep the sd with a floor because the variability
of off-center offsets differs too much between people/devices (E10: shrinkage for off-center offsets made it worse).
The prior is an aggregate statistic from CC BY-NC-SA 4.0 data (source credited in the file).
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features  # noqa: E402
import strokepin_loader  # noqa: E402

S = strokepin_loader.load()
grp = defaultdict(list)
for e in S:
    grp[(e["user"], e["pin"], e["posture"])].append(features.extract(e["session"]))
keys = sorted(k for k in S and features.extract(S[0]["session"]) if k.startswith(("pin_hold_", "pin_flight_")) or k == "pin_total")
vs = [np.var(np.array([[f[k] for k in keys] for f in fs]), axis=0, ddof=1) for fs in grp.values() if len(fs) >= 2]
prior = dict(zip(keys, np.mean(vs, axis=0).round(2).tolist()))
out = {"within_var": prior, "n_taps": 6, "nu": 5,
       "source": "StrokePIN (Yao & Wang 2026, CC BY-NC-SA 4.0), 97 people, 6-digit PINs, sitting+walking; aggregate statistics over all PINs",
       "n_groups": len(vs), "note": "pin_total is only used when the PIN has exactly 6 keys"}
(ROOT / "backend/app/scoring/population_prior.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: round(v ** 0.5, 1) for k, v in prior.items()}, indent=1), len(vs), "groups")
