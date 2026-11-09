from pathlib import Path

import scan_codebase

ROOT = Path(__file__).resolve().parents[1]


def test_scanner_finds_signals():
    report = scan_codebase.scan(ROOT / "examples/demo-service")
    ids = {s["id"] for s in report["signals"]}
    assert "set-interval" in ids
    assert "sql-select-star" in ids
    assert "img-no-alt" in ids
    assert report["summary"]["images"] == 1
    assert report["summary"]["total_bytes"] > 1_000_000
