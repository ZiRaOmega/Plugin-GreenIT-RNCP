#!/usr/bin/env python3
"""Importe les 78 critères du RGESN 2024 depuis l'outil de déclaration officiel.

Source : Arcep / Arcom / ADEME, référentiel général d'écoconception des services
numériques, version 2024, outil de déclaration XLSX.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from openpyxl import load_workbook

DEFAULT_URL = (
    "https://ecoresponsable.numerique.gouv.fr/docs/2024/rgesn-mai2024/"
    "rgesn_2024_outil_declaration_ecoconception.xlsx"
)
EXPECTED_COUNTS = {
    "1 — Stratégie": 10,
    "2 — Spécifications": 10,
    "3 — Architecture": 7,
    "4 — Expérience et interface utilisateur": 15,
    "5 — Contenus": 8,
    "6 — Frontend": 7,
    "7 — Backend": 4,
    "8 — Hébergement": 10,
    "9 — Algorithmie": 7,
}
WEIGHTS = {"Prioritaire": 1.5, "Recommandé": 1.25, "Modéré": 1.0}
ID_RE = re.compile(r"^\d{1,2}\.\d{1,2}$")


def clean(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\xa0", " ").split())


def chapter_from_sheet(sheet: str) -> str:
    # "1 Stratégie (1)" -> "1 — Stratégie"
    name = re.sub(r"\s*\(\d+/\d+\)\s*$", "", sheet).strip()
    m = re.match(r"^(\d+)\s+(.+)$", name)
    if not m:
        raise ValueError(f"Feuille inattendue : {sheet!r}")
    labels = {
        "1": "Stratégie",
        "2": "Spécifications",
        "3": "Architecture",
        "4": "Expérience et interface utilisateur",
        "5": "Contenus",
        "6": "Frontend",
        "7": "Backend",
        "8": "Hébergement",
        "9": "Algorithmie",
    }
    return f"{m.group(1)} — {labels[m.group(1)]}"


def find_header(ws) -> int:
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 12)):
        values = [clean(c.value) for c in row]
        if "ID" in values and any("Libellé du critère" in v for v in values):
            return row[0].row
    raise ValueError(f"En-tête introuvable dans {ws.title!r}")


def import_workbook(path: Path) -> list[dict[str, object]]:
    wb = load_workbook(path, data_only=True)
    records: list[dict[str, object]] = []
    for ws in wb.worksheets:
        if not re.match(r"^[1-9]\s", ws.title):
            continue
        header_row = find_header(ws)
        headers = [clean(c.value) for c in ws[header_row]]
        # Colonnes officielles : B=ID, C=libellé, D=priorité, H=difficulté,
        # N=cible, O=moyen de test. On privilégie les libellés quand ils existent.
        def col(label: str, fallback: int) -> int:
            for i, h in enumerate(headers, start=1):
                if label.lower() in h.lower():
                    return i
            return fallback

        # Attention : l'en-tête "ID" est en colonne A, mais les identifiants
        # de critères sont en colonne B dans l'outil officiel.
        c_id = 2
        c_title = col("Libellé du critère", 3)
        c_priority = col("Niveau de", 4)
        c_difficulty = col("Niveau de difficulté", 8)
        c_target = col("Cible", 14)
        c_test = col("Synthèse du moyen de test", 15)
        for row in ws.iter_rows(min_row=header_row + 1, values_only=False):
            raw_id = clean(row[c_id - 1].value) if c_id - 1 < len(row) else ""
            if not ID_RE.match(raw_id):
                continue
            title = clean(row[c_title - 1].value) if c_title - 1 < len(row) else ""
            priority = clean(row[c_priority - 1].value) if c_priority - 1 < len(row) else ""
            difficulty = clean(row[c_difficulty - 1].value) if c_difficulty - 1 < len(row) else ""
            target = clean(row[c_target - 1].value) if c_target - 1 < len(row) else ""
            test = clean(row[c_test - 1].value) if c_test - 1 < len(row) else ""
            if priority not in WEIGHTS:
                raise ValueError(f"{raw_id}: priorité inconnue {priority!r}")
            if difficulty not in {"Fort", "Moyen", "Faible"}:
                raise ValueError(f"{raw_id}: difficulté inconnue {difficulty!r}")
            records.append({
                "id": raw_id,
                "chapter": chapter_from_sheet(ws.title),
                "title": title,
                "priority": priority,
                "difficulty": difficulty,
                "target": target,
                "test_method": test,
                "weight": WEIGHTS[priority],
                "source_url": DEFAULT_URL,
                "version": "2024",
                "retrieved_at": "2026-11-09",
            })
    # dédoublonnage défensif
    by_id: dict[str, dict[str, object]] = {}
    for rec in records:
        by_id.setdefault(str(rec["id"]), rec)
    return sorted(by_id.values(), key=lambda r: tuple(int(x) for x in str(r["id"]).split(".")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, help="XLSX officiel déjà téléchargé")
    ap.add_argument("--out", type=Path, default=Path("references/rgesn-2024.csv"))
    ap.add_argument("--url", default=DEFAULT_URL)
    args = ap.parse_args()
    if args.input:
        path = args.input
    else:
        import requests
        path = Path("build/rgesn_2024.xlsx")
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(args.url, timeout=60)
        r.raise_for_status()
        path.write_bytes(r.content)
    records = import_workbook(path)
    counts: dict[str, int] = {}
    for rec in records:
        counts[str(rec["chapter"])] = counts.get(str(rec["chapter"]), 0) + 1
    if counts != EXPECTED_COUNTS or len(records) != 78:
        print("Counts obtenus :", counts, file=sys.stderr)
        print(f"Total : {len(records)} (attendu 78)", file=sys.stderr)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["id", "chapter", "title", "priority", "difficulty", "target",
              "test_method", "weight", "source_url", "version", "retrieved_at"]
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)
    print(f"OK {len(records)} critères -> {args.out}")
    for chapter, count in counts.items():
        print(f"  {chapter}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
