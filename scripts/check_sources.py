#!/usr/bin/env python3
"""Vérifie que les sources citées existent et que les hypothèses sont traçables."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "plugins" / "greenit-audit" / "references"
DIST = ROOT / "dist"
SOURCE_RE = re.compile(r"\[S(\d{2})\]")
HYP_RE = re.compile(r"\bH(\d{1,2})\b")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> int:
    errors: list[str] = []
    sources = load_yaml(REF / "sources.yml").get("sources", [])
    ids = {s["id"] for s in sources}
    expected = {f"S{i:02d}" for i in range(1, 43)}
    if ids != expected:
        errors.append(f"Registre : IDs manquants ou en trop : {sorted(expected ^ ids)}")
    docs = [
        DIST / "audit-demo" / "report.md",
        DIST / "audit-demo" / "deck.yml",
        DIST / "audit-demo" / "rgesn-summary.md",
        DIST / "notes-orales-demo.md",
    ]
    cited: set[str] = set()
    for doc in docs:
        if not doc.exists():
            errors.append(f"Document manquant : {doc}")
            continue
        text = doc.read_text(encoding="utf-8")
        for m in SOURCE_RE.finditer(text):
            sid = f"S{m.group(1)}"
            cited.add(sid)
            if sid not in ids:
                errors.append(f"{doc.name} cite {sid}, absent de sources.yml")
    # Figures : source non vide et, si elle cite un ID, l'ID doit exister.
    fig_manifest = DIST / "figures" / "manifest.json"
    if fig_manifest.exists():
        for fig in json.loads(fig_manifest.read_text(encoding="utf-8")):
            if not fig.get("source"):
                errors.append(f"Figure {fig.get('id')} sans source")
            for m in SOURCE_RE.finditer(fig.get("source", "")):
                sid = f"S{m.group(1)}"
                cited.add(sid)
                if sid not in ids:
                    errors.append(f"Figure {fig.get('id')} cite {sid}, absent de sources.yml")
    else:
        errors.append("figures/manifest.json manquant")
    # Hypothèses
    audit_path = ROOT / "examples" / "demo-service" / "audit.yml"
    audit = load_yaml(audit_path)
    h_ids = {a["id"] for a in audit.get("assumptions", [])}
    report = (DIST / "audit-demo" / "report.md").read_text(encoding="utf-8") if (DIST / "audit-demo" / "report.md").exists() else ""
    for hid in h_ids:
        if hid not in report:
            errors.append(f"Hypothèse {hid} absente du rapport")
    for hid in set(HYP_RE.findall(report)):
        if f"H{hid}" not in h_ids:
            errors.append(f"Le rapport cite H{hid}, absent de audit.yml")
    print(f"Sources : {len(ids)} ; IDs cités : {len(cited)} ; hypothèses : {len(h_ids)}")
    if errors:
        for e in errors:
            print("ERREUR :", e, file=sys.stderr)
        return 1
    print("CHECK SOURCES OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
