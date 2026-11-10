import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SANITIZER = ROOT / "plugins/greenit-reviewer/scripts/sanitize_ai_text.py"
REVIEWER = ROOT / "plugins/greenit-reviewer/scripts/review_deliverables.py"


def test_sanitizer_removes_ai_characters(tmp_path):
    p = tmp_path / "sample.md"
    p.write_text("Un texte — avec “guillemets” et … un emoji 🚀.\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SANITIZER), str(p), "--apply"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "—" not in p.read_text(encoding="utf-8")
    assert "“" not in p.read_text(encoding="utf-8")
    assert "🚀" not in p.read_text(encoding="utf-8")


def test_reviewer_runs_on_dist():
    if not (ROOT / "dist").exists():
        return
    out = ROOT / "dist/review-report.json"
    r = subprocess.run([sys.executable, str(REVIEWER), "--root", str(ROOT / "dist"), "--out", str(out)],
                       capture_output=True, text=True)
    assert out.exists()
