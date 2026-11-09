#!/usr/bin/env python3
"""Moteur de calcul ACV screening : GWP100, ADPe, ADPf.

Unités internes :
- GWP : kg CO2e
- ADPe : kg Sb eq
- ADPf : MJ
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
DEFAULT_FACTORS = HERE.parent / "references" / "factors.open.csv"
INDICATORS = ("gwp", "adpe", "adpf")
ENGINE_VERSION = "0.1.2"


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


def f(row: dict, key: str, default: float = 0.0) -> float:
    value = row.get(key)
    if value in (None, ""):
        return default
    return float(value)


def f_opt(row: dict, key: str) -> float | None:
    """Lit un facteur ; une cellule vide signifie « indisponible », pas zéro."""
    value = row.get(key)
    if value in (None, ""):
        return None
    return float(value)


def nfmt(value: float | None) -> str:
    return "—" if value is None else f"{value:.6g}"


def r(value: float, ndigits: int = 10) -> float:
    return round(float(value), ndigits)


def calculate(audit: dict, factors: dict[str, dict], allow_missing: bool = False) -> dict:
    scope = audit["scope"]
    grid = float(scope["grid_intensity_gco2e_per_kwh"])
    items_out: list[dict] = []
    warnings: list[str] = []
    for item in audit["inventory"]["items"]:
        fid = item["factor_id"]
        if fid not in factors:
            msg = f"{item['id']}: facteur {fid!r} absent"
            if item["category"] != "network" and not allow_missing:
                raise KeyError(msg)
            warnings.append(msg)
            items_out.append({**item, "gwp": None, "adpe": None, "adpf": None,
                              "assessed": False,
                              "assessed_indicators": {k: False for k in INDICATORS},
                              "formula": "facteur absent"})
            continue
        factor = factors[fid]
        alloc = float(item.get("allocation_share", 1.0))
        pue = float(item.get("pue", 1.0))
        qty = float(item.get("quantity", 1.0))
        hours = float(item.get("hours", 0.0))
        gb = float(item.get("gb", 0.0))
        category = item["category"]
        ref_grid = f(factor, "reference_grid_gco2e_per_kwh", 0.0)
        grid_ratio = (grid / ref_grid) if ref_grid > 0 else 1.0

        if category == "network":
            f_gwp = f_opt(factor, "use_gwp_per_gb")
            f_adpe = f_opt(factor, "use_adpe_per_gb")
            f_adpf = f_opt(factor, "use_adpf_per_gb")
            gwp = None if f_gwp is None else gb * f_gwp * grid_ratio * alloc
            adpe = None if f_adpe is None else gb * f_adpe * grid_ratio * alloc
            adpf = None if f_adpf is None else gb * f_adpf * grid_ratio * alloc
            parts = [f"{gb:g} Go × facteur/Go × ({grid:g}/{ref_grid:g}) × S_alloc({alloc:g})"]
            if adpe is None or adpf is None:
                parts.append("ADPe/ADPf indisponibles")
            formula = " ; ".join(parts)
        elif category == "decommissioning":
            eol_gwp = f_opt(factor, "eol_gwp_per_unit")
            if eol_gwp is None and not allow_missing:
                raise KeyError(f"{item['id']}: facteur de fin de vie absent (eol_gwp_per_unit)")
            gwp = None if eol_gwp is None else qty * eol_gwp * alloc
            f_adpe = f_opt(factor, "eol_adpe_per_unit")
            f_adpf = f_opt(factor, "eol_adpf_per_unit")
            adpe = None if f_adpe is None else qty * f_adpe * alloc
            adpf = None if f_adpf is None else qty * f_adpf * alloc
            formula = f"{qty:g} × facteur fin de vie × S_alloc({alloc:g})"
        else:
            lifetime = f(factor, "lifetime_h")
            if lifetime <= 0:
                raise ValueError(f"{fid}: lifetime_h manquant")
            embodied_gwp = f(factor, "embedded_gwp")
            embodied_adpe = f(factor, "embedded_adpe")
            embodied_adpf = f(factor, "embedded_adpf")
            gwp = qty * ((embodied_gwp / lifetime) * hours
                         + f(factor, "use_gwp_per_h") * hours * grid_ratio * pue) * alloc
            adpe = qty * ((embodied_adpe / lifetime) * hours
                          + f(factor, "use_adpe_per_h") * hours * grid_ratio * pue) * alloc
            adpf = qty * ((embodied_adpf / lifetime) * hours
                          + f(factor, "use_adpf_per_h") * hours * grid_ratio * pue) * alloc
            formula = (f"{qty:g} × [(emb/{lifetime:g})×{hours:g} + "
                       f"usage×{hours:g}×({grid:g}/{ref_grid:g})×{pue:g}]×S_alloc({alloc:g})")
        assessed_indicators = {k: v is not None for k, v in (("gwp", gwp), ("adpe", adpe), ("adpf", adpf))}
        items_out.append({
            **item,
            "gwp": None if gwp is None else r(gwp),
            "adpe": None if adpe is None else r(adpe),
            "adpf": None if adpf is None else r(adpf),
            "assessed": all(assessed_indicators.values()),
            "assessed_indicators": assessed_indicators,
            "formula": formula,
            "factor_source_id": factor.get("source_id", ""),
            "factor_unit": factor.get("unit", ""),
        })

    totals = {}
    for k in INDICATORS:
        vals = [i[k] for i in items_out if i[k] is not None]
        totals[k] = r(sum(vals)) if vals else None

    def group(key: str) -> list[dict]:
        buckets: dict[Any, dict[str, list[float]]] = defaultdict(lambda: {k: [] for k in INDICATORS})
        for i in items_out:
            for k in INDICATORS:
                if i[k] is not None:
                    buckets[i[key]][k].append(i[k])
        out = []
        for value, sums in sorted(buckets.items(), key=lambda kv: str(kv[0])):
            row = {key: value}
            for k in INDICATORS:
                row[k] = r(sum(sums[k])) if sums[k] else None
            row["share_gwp"] = r(row["gwp"] / totals["gwp"] * 100, 6) if totals["gwp"] and row["gwp"] is not None else None
            out.append(row)
        return out

    shares = {f"by_{key}": group(key) for key in ("tier", "stage", "category")}
    gwp_items = [i for i in items_out if i["gwp"] is not None]
    hotspots = sorted(gwp_items, key=lambda i: i["gwp"], reverse=True)[:5]
    for h in hotspots:
        h["share_gwp"] = r(h["gwp"] / totals["gwp"] * 100, 6) if totals["gwp"] else None

    indicator_status = {}
    for k in INDICATORS:
        assessed_count = sum(1 for i in items_out if i[k] is not None)
        indicator_status[k] = {
            "assessed_items": assessed_count,
            "missing_items": len(items_out) - assessed_count,
            "status": "évalué" if assessed_count == len(items_out) else ("partiel" if assessed_count else "indisponible"),
        }
        if totals[k] is None:
            warnings.append(f"total {k} indisponible : aucune valeur disponible")
        elif totals[k] <= 0:
            warnings.append(f"total {k} nul : résultat non significatif")

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "engine": "calc.py",
            "version": ENGINE_VERSION,
            "grid_intensity_gco2e_per_kwh": grid,
            "grid_source_id": scope.get("grid_source_id"),
            "factor_files": [str(p) for p in getattr(calculate, "_factor_files", [])],
        },
        "functional_unit": audit["functional_unit"],
        "scope": scope,
        "items": items_out,
        "totals": {**totals, "unit_gwp": "kg CO2e", "unit_adpe": "kg Sb eq", "unit_adpf": "MJ"},
        "indicator_status": indicator_status,
        "shares": shares,
        "hotspots": hotspots,
        "uncertainty": {
            "method": "±30 % par défaut sur le total, en l’absence de distribution de facteurs. Les valeurs absentes restent null, jamais zéro.",
            "low": {k: (None if totals[k] is None else r(totals[k] * 0.7)) for k in INDICATORS},
            "base": totals,
            "high": {k: (None if totals[k] is None else r(totals[k] * 1.3)) for k in INDICATORS},
        },
        "quality": {**audit.get("quality", {}), "warnings": warnings},
        "assumptions": audit.get("assumptions", []),
        "sources": sorted({i.get("source_id", "") for i in items_out
                           if any(i.get("assessed_indicators", {}).values()) and i.get("source_id")}),
    }


def write_markdown(metrics: dict, out: Path) -> None:
    t = metrics["totals"]
    lines = [
        "# Résultats de calcul — ACV screening",
        "",
        f"Unité fonctionnelle : **{metrics['functional_unit']['description']}**",
        "",
        "| Indicateur | Total | Unité |",
        "|---|---:|---|",
        f"| GWP100 | {nfmt(t['gwp'])} | kg CO2e |",
        f"| ADPe | {nfmt(t['adpe'])} | kg Sb eq |",
        f"| ADPf | {nfmt(t['adpf'])} | MJ |",
        "",
        "## Parts par tier",
        "",
        "| Tier | GWP (kg CO2e) | Part GWP |",
        "|---:|---:|---:|",
    ]
    for row in metrics["shares"]["by_tier"]:
        lines.append(f"| {row['tier']} | {nfmt(row['gwp'])} | {nfmt(row['share_gwp'])} % |")
    lines += ["", "## Hotspots", "", "| Item | GWP (kg CO2e) | Part |", "|---|---:|---:|"]
    for h in metrics["hotspots"]:
        lines.append(f"| {h['label']} | {nfmt(h['gwp'])} | {nfmt(h['share_gwp'])} % |")
    lines += ["", "## Incertitude", "", metrics["uncertainty"]["method"], "",
              f"- Bas : {nfmt(metrics['uncertainty']['low']['gwp'])} kg CO2e",
              f"- Base : {nfmt(t['gwp'])} kg CO2e",
              f"- Haut : {nfmt(metrics['uncertainty']['high']['gwp'])} kg CO2e", ""]
    if metrics["quality"].get("limitations"):
        lines += ["## Limites", ""] + [f"- {x}" for x in metrics["quality"]["limitations"]] + [""]
    out.write_text("\n".join(lines), encoding="utf-8")


def write_calculation_notes(metrics: dict, out: Path) -> None:
    lines = ["# Note de calcul", "",
             "Chaque ligne applique la même unité fonctionnelle et la même frontière.", "",
             "| Item | Catégorie | Tier | Formule | GWP (kg CO2e) | ADPe (kg Sb eq) | ADPf (MJ) | Source |",
             "|---|---|---|---|---:|---:|---:|---|"]
    for i in metrics["items"]:
        lines.append(f"| {i['label']} | {i['category']} | {i['tier']} | {i['formula']} | {nfmt(i['gwp'])} | {nfmt(i['adpe'])} | {nfmt(i['adpf'])} | {i['source_id']} |")
    lines += ["", "## Hypothèses", ""]
    for a in metrics["assumptions"]:
        lines.append(f"- **{a['id']}** — {a['statement']} Valeur : {a['value']} {a['unit']} ; source : {a['source_id']} ; confiance : {a['confidence']}.")
    lines += ["", "## Limites", ""] + [f"- {x}" for x in metrics["quality"].get("limitations", [])] + [""]
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--factors", type=Path, action="append")
    ap.add_argument("--out", type=Path, default=Path("metrics.json"))
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--allow-missing-factors", action="store_true")
    args = ap.parse_args()
    factor_paths = args.factors or [DEFAULT_FACTORS]
    calculate._factor_files = factor_paths
    audit = load_yaml(args.input)
    factors = load_factors(factor_paths)
    metrics = calculate(audit, factors, allow_missing=args.allow_missing_factors)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(metrics, args.out.with_name("metrics.md"))
        write_calculation_notes(metrics, args.out.with_name("calculation-notes.md"))
    print(f"OK GWP={nfmt(metrics['totals']['gwp'])} kg CO2e, ADPe={nfmt(metrics['totals']['adpe'])} kg Sb eq, ADPf={nfmt(metrics['totals']['adpf'])} MJ -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
