#!/usr/bin/env python3
"""Valide un fichier audit.yml contre le schéma et les facteurs disponibles."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import jsonschema
import yaml

HERE = Path(__file__).resolve().parent
DEFAULT_SCHEMA = HERE.parent / "assets" / "audit.schema.json"
DEFAULT_FACTORS = HERE.parent / "references" / "factors.open.csv"
DEFAULT_SOURCES = HERE.parent / "references" / "sources.yml"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} ne contient pas un objet YAML")
    return data


def load_factors(paths: list[Path]) -> dict[str, dict]:
    factors: dict[str, dict] = {}
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                factors[row["factor_id"]] = row
    return factors


def as_float(row: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key) or default)
    except (TypeError, ValueError):
        return default


def validate(audit_path: Path, schema_path: Path, factor_paths: list[Path],
             sources_path: Path, strict: bool) -> int:
    audit = load_yaml(audit_path)
    schema = load_yaml(schema_path)
    jsonschema.Draft202012Validator(schema).validate(audit)
    factors = load_factors(factor_paths)
    sources_doc = load_yaml(sources_path)
    source_ids = {s["id"] for s in sources_doc.get("sources", [])}
    warnings: list[str] = []
    errors: list[str] = []

    if not audit["scope"].get("include_embodied", True):
        warnings.append("include_embodied=false : la fabrication des équipements est exclue.")
    if audit["scope"].get("include_end_of_life") and not any(
        i["category"] == "decommissioning" for i in audit["inventory"]["items"]
    ):
        warnings.append("include_end_of_life=true mais aucun item decommissioning.")

    for item in audit["inventory"]["items"]:
        fid = item["factor_id"]
        if fid not in factors:
            errors.append(f"{item['id']}: facteur inconnu {fid!r}")
            continue
        factor = factors[fid]
        if item["category"] == "network":
            if as_float(factor, "use_gwp_per_gb") <= 0 and as_float(factor, "use_gwp_per_h") <= 0:
                errors.append(f"{item['id']}: facteur réseau sans impact par Go ou par heure")
        elif item["category"] != "decommissioning":
            if as_float(factor, "embedded_gwp") <= 0 and as_float(factor, "use_gwp_per_h") <= 0:
                errors.append(f"{item['id']}: facteur sans impact embarqué ni usage")
        if item["category"] == "server" and item["data_quality"] == "assumption":
            warnings.append(f"{item['id']}: caractéristiques serveur supposées.")
        if item["source_id"] not in source_ids:
            errors.append(f"{item['id']}: source_id inconnu {item['source_id']!r}")
        if item["allocation_share"] < 0 or item["allocation_share"] > 1:
            errors.append(f"{item['id']}: allocation_share hors [0,1]")
        if item["pue"] < 1:
            errors.append(f"{item['id']}: pue < 1")
        if any(item[k] < 0 for k in ("quantity", "hours", "gb")):
            errors.append(f"{item['id']}: quantité négative")

    for assumption in audit.get("assumptions", []):
        if assumption["source_id"] not in source_ids:
            errors.append(f"{assumption['id']}: source_id inconnu {assumption['source_id']!r}")

    print(f"Audit : {audit_path}")
    print(f"Items : {len(audit['inventory']['items'])} | facteurs : {len(factors)} | sources : {len(source_ids)}")
    for w in warnings:
        print(f"AVERTISSEMENT : {w}")
    for e in errors:
        print(f"ERREUR : {e}", file=sys.stderr)
    if errors or (strict and warnings):
        return 1
    print("OK audit valide")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    ap.add_argument("--factors", type=Path, action="append")
    ap.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    return validate(args.input, args.schema, args.factors or [DEFAULT_FACTORS], args.sources, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
