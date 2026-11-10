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


def test_block_guard(tmp_path):
    import csv, sys
    from pathlib import Path
    sys.path.insert(0, str(ROOT / "plugins/greenit-reviewer/scripts"))
    from review_deliverables import review_rncp
    src = ROOT / "plugins/greenit-audit/references/rncp39388-matrix.csv"
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig")))
    for r in rows:
        r["status"] = "validé" if r["block"] in {"BC02", "BC03"} else "hors périmètre"
    base = tmp_path / "rncp39388"
    base.mkdir()
    with (base / "01-matrice-competences.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["block", "block_title", "competency_id", "competency", "evidence", "location", "status"])
        w.writeheader(); w.writerows(rows)
    findings = []
    review_rncp(tmp_path, findings, "BC01,BC04")
    block_findings = [x for x in findings if x["code"] == "rncp-block-status"]
    assert sum(1 for x in block_findings if x["severity"] == "blocker") == 9
    assert sum(1 for x in block_findings if x["severity"] == "major") == 10
