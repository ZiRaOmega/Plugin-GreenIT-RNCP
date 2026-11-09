import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in [
    ROOT / "plugins/greenit-audit/scripts",
    ROOT / "plugins/greenit-studio/scripts",
    ROOT / "plugins/greenit-engineering/scripts",
    ROOT / "scripts",
]:
    sys.path.insert(0, str(p))
