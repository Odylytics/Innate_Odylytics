import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "dl"), str(ROOT / "backend"), str(ROOT / "attacker")]
