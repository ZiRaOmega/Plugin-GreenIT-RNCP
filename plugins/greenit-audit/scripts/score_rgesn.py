#!/usr/bin/env python3
"""Calcule un score d’avancement RGESN transparent (non officiel)."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DEFAULT_CRITERIA = HERE.parent / "references" / "rgesn-2024.csv"
STATUS_VALUES = {"validé": 1.0, "en cours": 0.5, "non validé": 0.0}
EXCLUDED = {"non applicable"}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} ne contient pas un objet YAML")
    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--criteria", type=Path, default=DEFAULT_CRITERIA)
    ap.add_argument("--assessment", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("rgesn-score.csv"))
    ap.add_argument("--markdown", type=Path)
    args = ap.parse_args()

    with args.criteria.open(encoding="utf-8-sig", newline="") as f:
        criteria = list(csv.DictReader(f))
    by_id = {r["id"]: r for r in criteria}
    assessment = load_yaml(args.assessment).get("assessment", [])
    assessed = {a["id"]: a for a in assessment}
    missing = [cid for cid in by_id if cid not in assessed]
    extra = [aid for aid in assessed if aid not in by_id]
    if missing:
        raise ValueError(f"Critères absents de l’évaluation : {missing}")
    if extra:
        raise ValueError(f"IDs inconnus dans l’évaluation : {extra}")

    rows = []
    counts = Counter()
    weighted_evaluated = 0.0
    weighted_evidence = 0.0
    weighted_applicable = 0.0
    weighted_score = 0.0
    evidence_counts = Counter()
    for cid, crit in by_id.items():
        a = assessed[cid]
        status = a["status"]
        counts[status] += 1
        weight = float(crit["weight"])
        if status in EXCLUDED:
            value = ""
            evidence_status = "non applicable"
        elif status in STATUS_VALUES:
            value = STATUS_VALUES[status]
            weighted_applicable += weight
            weighted_evaluated += weight
            weighted_score += weight * value
            ev = a.get("evidence", "").strip()
            evidence_status = "sans preuve" if (not ev or ev.lower().startswith("absence de preuve")) else "preuve"
            if evidence_status == "preuve":
                weighted_evidence += weight
        else:
            raise ValueError(f"{cid}: statut invalide {status!r} ; évaluer le critère")
        evidence_counts[evidence_status] += 1
        rows.append({
            "id": cid, "chapter": crit["chapter"], "title": crit["title"],
            "priority": crit["priority"], "difficulty": crit["difficulty"],
            "status": status, "evidence_status": evidence_status, "weight": weight,
            "value": STATUS_VALUES.get(status, ""),
            "weighted_score": round(weight * STATUS_VALUES.get(status, 0.0), 6),
            "evidence": a.get("evidence", ""), "action": a.get("action", ""),
            "owner": a.get("owner", ""), "due": a.get("due", ""),
        })

    score = 100 * weighted_score / weighted_evaluated if weighted_evaluated else 0.0
    coverage_evaluated = 100 * weighted_evaluated / weighted_applicable if weighted_applicable else 0.0
    coverage_evidence = 100 * weighted_evidence / weighted_applicable if weighted_applicable else 0.0
    coverage_status = "significatif" if coverage_evidence >= 50 else "non significatif"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["id", "chapter", "title", "priority", "difficulty", "status", "evidence_status",
              "weight", "value", "weighted_score", "evidence", "action", "owner", "due"]
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    non_conform = [r for r in rows if r["status"] in {"non validé", "en cours"}]
    non_conform.sort(key=lambda r: (-r["weight"], r["id"]))
    md = [
        "# Score d’avancement RGESN 2024",
        "",
        f"- **Score** : {score:.1f}/100",
        f"- **Statuts évalués** : {coverage_evaluated:.1f} % des critères applicables",
        f"- **Preuves disponibles** : {coverage_evidence:.1f} % des critères applicables",
        f"- **Lecture du score** : {coverage_status}",
        f"- **Critères** : {len(rows)} ; applicables pondérés : {weighted_applicable:.2f}",
        "",
        "| Statut | Nombre |",
        "|---|---:|",
    ]
    for status in ("validé", "en cours", "non validé", "non applicable"):
        if counts[status]:
            md.append(f"| {status} | {counts[status]} |")
    md += ["", "| Preuve | Nombre |", "|---|---:|"]
    for st in ("preuve", "sans preuve", "non applicable"):
        if evidence_counts[st]:
            md.append(f"| {st} | {evidence_counts[st]} |")
    md += ["", "## Top 10 des critères non conformes ou en cours", "",
           "| ID | Priorité | Statut | Libellé |", "|---|---|---|---|"]
    for r in non_conform[:10]:
        md.append(f"| {r['id']} | {r['priority']} | {r['status']} | {r['title'][:120]} |")
    md += ["", "Tous les critères ont un statut évalué (validé, en cours, non validé ou non applicable).", ""]
    md += ["", "Ce score est un indicateur d’avancement transparent, pas le score officiel de l’outil RGESN. Le taux de statuts évalués ne vaut pas taux de preuves : les critères « sans preuve » sont comptés comme non validés, pas comme conformes.", ""]
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text("\n".join(md), encoding="utf-8")
    print(f"OK score={score:.1f}/100 statuts={coverage_evaluated:.1f}% preuves={coverage_evidence:.1f}% ({coverage_status}) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
