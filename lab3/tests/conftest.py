import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in ("part1", "part2", "part3"):
    sys.path.insert(0, str(ROOT / folder))
