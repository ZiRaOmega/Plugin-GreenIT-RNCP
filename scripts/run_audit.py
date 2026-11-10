#!/usr/bin/env python3
"""Workflow complet d’audit GreenIT sur un projet quelconque.

Utilisable depuis n’importe quel cwd. Tous les scripts du bundle sont appelés
par chemin absolu ; les facteurs sont résolus dans le bundle.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PLUGIN = ROOT / "plugins/greenit-audit"
STUDIO = ROOT / "plugins/greenit-studio"
LOCAL_FACTORS = AUDIT_PLUGIN / "references" / "factors.local.csv"
if not LOCAL_FACTORS.exists():
    LOCAL_FACTORS = AUDIT_PLUGIN / "references" / "factors.local.example.csv"
DEFAULT_FACTORS = [
    AUDIT_PLUGIN / "references" / "factors.open.csv",
    LOCAL_FACTORS,
]


def run(cmd: list[Path | str]) -> None:
    print("$", " ".join(str(x) for x in cmd))
    p = subprocess.run([str(x) for x in cmd], text=True, capture_output=True)
    if p.returncode:
        print(p.stdout)
        print(p.stderr, file=sys.stderr)
        raise SystemExit(p.returncode)
    if p.stdout.strip():
        print(p.stdout.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True, help="Racine du projet à auditer")
    ap.add_argument("--audit", type=Path, help="audit.yml (défaut : <projet>/audit.yml)")
    ap.add_argument("--assessment", type=Path, help="rgesn-assessment.yml (défaut : <projet>/rgesn-assessment.yml)")
    ap.add_argument("--codebase", type=Path, help="Codebase à scanner (défaut : projet)")
    ap.add_argument("--url", help="URL locale du service pour web_metrics.py")
    ap.add_argument("--out", type=Path, help="Dossier de sortie (défaut : <projet>/dist)")
    ap.add_argument("--factors", type=Path, action="append", help="Facteur CSV ; répétable")
    args = ap.parse_args()

    project = args.project.resolve()
    audit = (args.audit or (project / "audit.yml")).resolve()
    assessment = (args.assessment or (project / "rgesn-assessment.yml")).resolve()
    codebase = (args.codebase or project).resolve()
    out = (args.out or (project / "dist")).resolve()
    figures = out / "figures"
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    factors = [p.resolve() for p in (args.factors or DEFAULT_FACTORS)]
    for p in [audit, assessment, *factors]:
        if not p.exists():
            raise SystemExit(f"Fichier introuvable : {p}")

    py = sys.executable
    run([py, AUDIT_PLUGIN / "scripts" / "validate_audit.py", "--input", audit,
         *sum((["--factors", f] for f in factors), [])])
    run([py, STUDIO / "scripts" / "scan_codebase.py", "--root", codebase,
         "--out", out / "codebase-audit.json", "--markdown"])

    web = out / "web-metrics.json"
    if args.url:
        run([py, STUDIO / "scripts" / "web_metrics.py", "--url", args.url,
             "--out", web, "--markdown"])
    else:
        print("AVERTISSEMENT : --url absent ; métriques web non mesurées.")

    run([py, AUDIT_PLUGIN / "scripts" / "calc.py", "--input", audit,
         *sum((["--factors", f] for f in factors), []),
         "--out", out / "metrics.json", "--markdown"])
    run([py, AUDIT_PLUGIN / "scripts" / "score_rgesn.py", "--assessment", assessment,
         "--out", out / "rgesn-score.csv", "--markdown", out / "rgesn-summary.md"])

    pack = [py, AUDIT_PLUGIN / "scripts" / "build_audit_pack.py",
            "--metrics", out / "metrics.json",
            "--codebase", out / "codebase-audit.json",
            "--rgesn", out / "rgesn-score.csv",
            "--audit", audit,
            "--project", project,
            "--out", out,
            "--figures", figures,
            "--dist", out,
            "--factors", factors[0]]
    if web.exists():
        pack += ["--web", web]
    for f in factors[1:]:
        pack += ["--factors", f]
    run(pack)

    run([py, STUDIO / "scripts" / "md_to_docx.py",
         "--input", out / "report.md", "--metadata", out / "metadata.yml",
         "--figures", figures, "--out", out / "rapport.docx", "--pdf"])
    run([py, STUDIO / "scripts" / "md_to_docx.py",
         "--input", out / "synthese-client.md", "--metadata", out / "metadata.yml",
         "--figures", figures, "--out", out / "synthese-client.docx", "--pdf"])
    run([py, STUDIO / "scripts" / "build_deck.py",
         "--input", out / "deck.yml", "--out", out / "soutenance.pptx",
         "--notes", out / "notes-orales.md", "--pdf"])
    run([py, STUDIO / "scripts" / "build_video.py",
         "--deck", out / "soutenance.pptx", "--narration", out / "narration.md",
         "--out", out / "teaser.mp4"])
    run([py, ROOT / "scripts" / "write_manifest.py", "--dist", out])

    print(f"AUDIT OK -> {out}")
    for name in ["metrics.json", "rgesn-score.csv", "report.md", "rapport.pdf",
                 "synthese-client.pdf", "soutenance.pdf", "teaser.mp4", "manifest.json"]:
        p = out / name
        print(f"  {name}: {'OK' if p.exists() else 'MANQUANT'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
