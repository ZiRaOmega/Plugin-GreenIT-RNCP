import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(os.environ.get("RUN_E2E") != "1", reason="RUN_E2E=1 pour exécuter la démo complète")
def test_end_to_end():
    p = subprocess.run([sys.executable, str(ROOT / "scripts/run_demo.py")], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert (ROOT / "dist/rapport-audit-greenit-demo.pdf").exists()
    assert (ROOT / "dist/soutenance-greenit-demo.pptx").exists()
    assert (ROOT / "dist/teaser-greenit-demo.mp4").exists()
    q = subprocess.run([sys.executable, str(ROOT / "scripts/check_outputs.py")], capture_output=True, text=True)
    assert q.returncode == 0, q.stderr
