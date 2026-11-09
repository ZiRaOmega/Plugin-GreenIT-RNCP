import csv
import json
from pathlib import Path

import yaml

import calc

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "plugins/greenit-audit/references"


def test_demo_metrics():
    audit = yaml.safe_load((ROOT / "examples/demo-service/audit.yml").read_text(encoding="utf-8"))
    factors = calc.load_factors([REF / "factors.open.csv", REF / "factors.local.example.csv"])
    metrics = calc.calculate(audit, factors)
    for key in ("gwp", "adpe", "adpf"):
        assert metrics["totals"][key] > 0
    assert abs(sum(x["share_gwp"] for x in metrics["shares"]["by_tier"]) - 100) < 0.1
    assert metrics["hotspots"][0]["id"] == "server"
    assert all(i["factor_id"] and i["source_id"] for i in metrics["items"])


def test_server_formula_positive():
    audit = yaml.safe_load((ROOT / "examples/demo-service/audit.yml").read_text(encoding="utf-8"))
    factors = calc.load_factors([REF / "factors.open.csv", REF / "factors.local.example.csv"])
    metrics = calc.calculate(audit, factors)
    server = next(i for i in metrics["items"] if i["id"] == "server")
    assert 1.0 < server["gwp"] < 1.3
    assert server["adpe"] > 0
    assert server["adpf"] > 0


def test_share_sum_by_stage():
    audit = yaml.safe_load((ROOT / "examples/demo-service/audit.yml").read_text(encoding="utf-8"))
    factors = calc.load_factors([REF / "factors.open.csv", REF / "factors.local.example.csv"])
    metrics = calc.calculate(audit, factors)
    assert abs(sum(x["share_gwp"] for x in metrics["shares"]["by_stage"]) - 100) < 0.1
