import csv
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "plugins/greenit-audit/references"


def test_rgesn_csv():
    rows = list(csv.DictReader((REF / "rgesn-2024.csv").open(encoding="utf-8-sig")))
    assert len(rows) == 78
    counts = Counter(r["chapter"] for r in rows)
    assert counts["1 — Stratégie"] == 10
    assert counts["4 — Expérience et interface utilisateur"] == 15
    assert counts["7 — Backend"] == 4
    assert sum(counts.values()) == 78


def test_assessment_has_78(tmp_path):
    import yaml
    assessment = yaml.safe_load((ROOT / "examples/demo-service/rgesn-assessment.yml").read_text(encoding="utf-8"))
    assert len(assessment["assessment"]) == 78
    out = tmp_path / "score.csv"
    md = tmp_path / "score.md"
    p = subprocess.run([sys.executable, str(ROOT / "plugins/greenit-audit/scripts/score_rgesn.py"),
                        "--assessment", str(ROOT / "examples/demo-service/rgesn-assessment.yml"),
                        "--out", str(out), "--markdown", str(md)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    rows = list(csv.DictReader(out.open(encoding="utf-8-sig")))
    assert len(rows) == 78
    assert "Statuts évalués" in md.read_text(encoding="utf-8")
    assert "Preuves disponibles" in md.read_text(encoding="utf-8")


def test_parse_blocks():
    import sys
    sys.path.insert(0, str(ROOT / "plugins/greenit-audit/scripts"))
    from build_audit_pack import parse_blocks
    assert parse_blocks("BC01,BC04") == ("BC01", "BC04")
    assert parse_blocks("bloc 2, bloc 3") == ("BC02", "BC03")
    try:
        parse_blocks("BC05")
    except ValueError:
        pass
    else:
        raise AssertionError("BC05 doit être refusé")


def test_exam_bc01_bc04():
    import csv
    p = ROOT / "plugins/greenit-audit/references/rncp39388-bc01-bc04-exam.csv"
    rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
    assert len(rows) == 16
    assert {r["part"] for r in rows} == {str(i) for i in range(1, 10)}
    assert {r["exam_code"] for r in rows} == {f"C1.{i}" for i in range(1, 9)} | {f"C4.{i}" for i in range(1, 9)}
