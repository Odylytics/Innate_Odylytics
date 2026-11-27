"""The pure-Python LightGBM reader must give the same probability as lightgbm on the repo's real model."""
import math
import random
from pathlib import Path

import pytest

from app.scoring.lgbm_text import TextBooster

MODELS = Path(__file__).parents[1] / "app" / "models"


@pytest.mark.parametrize("name,nan", [("human_lgbm.txt", True), ("owner_lgbm.txt", False)])
def test_matches_lightgbm(name, nan):
    lgb = pytest.importorskip("lightgbm")
    ref = lgb.Booster(model_file=str(MODELS / name))
    mine = TextBooster.from_file(MODELS / name)
    rng = random.Random(0)
    n = ref.num_feature()
    rows = [[rng.uniform(-2, 120) if rng.random() > 0.1 else (math.nan if nan else 0.0) for _ in range(n)] for _ in range(300)]
    for a, b in zip(ref.predict(rows), mine.predict(rows)):
        assert abs(a - b) < 1e-9
