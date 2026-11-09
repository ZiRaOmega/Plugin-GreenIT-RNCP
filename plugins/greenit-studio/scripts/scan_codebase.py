#!/usr/bin/env python3
"""Analyse statique locale d’une codebase pour un diagnostic GreenIT."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "dist", "build", "vendor", "__pycache__", ".pytest_cache"}
TEXT_EXT = {".html", ".htm", ".css", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".py", ".sql",
            ".json", ".yml", ".yaml", ".toml", ".md", ".txt", ".xml", ".svg", ".php", ".rb", ".go", ".rs"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".bmp", ".ico"}
CODE_EXT = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".php", ".rb", ".go", ".rs", ".java", ".kt", ".c", ".cpp", ".cs"}
SIGNALS = [
    ("sql-select-star", r"\bSELECT\s+\*", "Requête SELECT * : transfère des colonnes inutiles.", "backend", "7.1", "high"),
    ("console-log", r"\bconsole\.log\s*\(", "Trace de debug laissée dans le code.", "frontend", "6.5", "low"),
    ("debugger", r"\bdebugger\b", "Point d’arrêt de debug.", "frontend", "6.5", "medium"),
    ("eval", r"\beval\s*\(", "Évaluation dynamique de code.", "frontend", "6.5", "high"),
    ("inner-html", r"\.innerHTML\s*=", "Injection HTML directe, risque XSS et rendu inutile.", "frontend", "4.2", "medium"),
    ("http-plain", r"http://(?!127\.0\.0\.1|localhost)", "URL HTTP non chiffrée.", "security", "3.3", "high"),
    ("todo", r"\b(TODO|FIXME)\b", "Dette technique non suivie.", "quality", "6.5", "low"),
    ("secret", r"(?i)(password|secret|api[_-]?key|token)\s*[:=]\s*['\"][^'\"]{4,}['\"]", "Secret potentiel en clair.", "security", "3.3", "critical"),
    ("autoplay", r"\bautoplay\b", "Lecture automatique de média.", "frontend", "4.1", "medium"),
    ("preload-auto", r'preload\s*=\s*["\']auto["\']', "Préchargement automatique de média.", "frontend", "4.1", "medium"),
    ("set-interval", r"\bsetInterval\s*\(", "Polling périodique.", "frontend", "4.9", "high"),
    ("short-timeout", r"\bsetTimeout\s*\(\s*[^,]+,\s*([0-9]{1,3})\s*\)", "Timeout très court, requêtes répétées possibles.", "frontend", "4.9", "medium"),
]
SECRET_RE = re.compile(r"(?i)(password|secret|api[_-]?key|token)\s*[:=]\s*['\"]([^'\"]{4,})['\"]")


def mask(value: str) -> str:
    return value[:2] + "***" + value[-2:] if len(value) > 4 else "***"


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def scan(root: Path) -> dict:
    files = []
    by_ext: Counter[str] = Counter()
    by_ext_bytes: Counter[int] = Counter()
    loc_by_ext: Counter[int] = Counter()
    total_bytes = 0
    largest = []
    images = []
    dependencies = {}
    ci = []
    dockerfiles = []
    signals = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            rel = p.relative_to(root).as_posix()
            try:
                size = p.stat().st_size
            except OSError:
                continue
            ext = p.suffix.lower()
            by_ext[ext] += 1
            by_ext_bytes[ext] += size
            total_bytes += size
            largest.append((size, rel))
            if ext in IMAGE_EXT:
                images.append({"path": rel, "bytes": size})
            if name in {"package.json", "requirements.txt", "pyproject.toml", "Cargo.toml", "composer.json"}:
                try:
                    dependencies[rel] = p.read_text(encoding="utf-8", errors="replace")[:4000]
                except OSError:
                    dependencies[rel] = ""
            if rel.startswith(".github/workflows/") or name in {".gitlab-ci.yml", "Jenkinsfile"}:
                ci.append(rel)
            if name.lower().startswith("dockerfile"):
                dockerfiles.append(rel)
            if ext in TEXT_EXT or name.lower() in {"dockerfile", "makefile"}:
                try:
                    text = p.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                loc = sum(1 for line in text.splitlines() if line.strip())
                if ext in CODE_EXT:
                    loc_by_ext[ext] += loc
                files.append({"path": rel, "bytes": size, "ext": ext, "loc": loc})
                signal_exts = CODE_EXT | {".sql", ".html", ".htm", ".css"}
                for sid, pattern, why, tier, greenit, severity in (SIGNALS if ext in signal_exts else []):
                    if not pattern:
                        continue
                    for m in re.finditer(pattern, text):
                        evidence = m.group(0)
                        if sid == "secret":
                            evidence = mask(m.group(2)) if m.lastindex and m.lastindex >= 2 else "***"
                        signals.append({
                            "id": sid, "severity": severity, "confidence": "medium",
                            "file": rel, "line": line_of(text, m.start()),
                            "evidence": evidence[:160], "why": why,
                            "greenit": greenit, "tier": tier,
                            "stage": "Réalisation" if ext in CODE_EXT else "Conception",
                            "effort": "faible" if severity in {"low", "medium"} else "moyen",
                            "recommendation": why,
                        })
    # Dédoublonner les signaux par (id, file, line)
    seen = set()
    unique = []
    for s in signals:
        key = (s["id"], s["file"], s["line"])
        if key not in seen:
            seen.add(key)
            unique.append(s)
    # HTML-specific checks
    for f in files:
        if f["ext"] not in {".html", ".htm"}:
            continue
        p = root / f["path"]
        try:
            html = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in re.finditer(r"<img\b(?![^>]*\balt\s*=)[^>]*>", html, re.I):
            unique.append({"id": "img-no-alt", "severity": "high", "confidence": "high",
                           "file": f["path"], "line": line_of(html, m.start()),
                           "evidence": m.group(0)[:120], "why": "Image sans attribut alt.",
                           "greenit": "4.2", "tier": "frontend", "stage": "Réalisation",
                           "effort": "faible", "recommendation": "Ajouter un texte alternatif."})
        for m in re.finditer(r"<input\b(?![^>]*\bid\s*=)[^>]*>", html, re.I):
            unique.append({"id": "input-no-id", "severity": "medium", "confidence": "medium",
                           "file": f["path"], "line": line_of(html, m.start()),
                           "evidence": m.group(0)[:120], "why": "Champ sans id, label difficile à associer.",
                           "greenit": "4.2", "tier": "frontend", "stage": "Réalisation",
                           "effort": "faible", "recommendation": "Ajouter un id et un label."})
        for m in re.finditer(r"<a\b[^>]*target\s*=\s*[\"']_blank[\"'][^>]*>", html, re.I):
            tag = m.group(0)
            if "noopener" not in tag.lower():
                unique.append({"id": "target-blank-noopener", "severity": "medium", "confidence": "high",
                               "file": f["path"], "line": line_of(html, m.start()),
                               "evidence": tag[:120], "why": "Ouverture d’onglet sans rel=noopener.",
                               "greenit": "4.2", "tier": "frontend", "stage": "Réalisation",
                               "effort": "faible", "recommendation": "Ajouter rel=\"noopener noreferrer\"."})
    unique.sort(key=lambda s: ({"critical": 0, "high": 1, "medium": 2, "low": 3}.get(s["severity"], 9), s["file"], s["line"]))
    largest.sort(reverse=True)
    return {
        "meta": {"root": str(root), "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "engine": "scan_codebase.py"},
        "summary": {
            "files": len(files), "total_bytes": total_bytes,
            "loc_by_ext": dict(sorted(loc_by_ext.items())),
            "files_by_ext": dict(sorted(by_ext.items())),
            "bytes_by_ext": dict(sorted(by_ext_bytes.items())),
            "signals": len(unique),
            "severity": dict(Counter(s["severity"] for s in unique)),
            "images": len(images), "image_bytes": sum(i["bytes"] for i in images),
            "ci": ci, "dockerfiles": dockerfiles,
        },
        "largest_files": [{"path": p, "bytes": b} for b, p in largest[:10]],
        "images": sorted(images, key=lambda i: i["bytes"], reverse=True)[:20],
        "dependencies": dependencies,
        "signals": unique,
    }


def markdown(report: dict) -> str:
    s = report["summary"]
    lines = ["# Diagnostic codebase", "",
             f"Racine : `{report['meta']['root']}`", "",
             f"- Fichiers : {s['files']}",
             f"- Octets : {s['total_bytes']}",
             f"- Signaux : {s['signals']} ({s['severity']})",
             f"- Images : {s['images']} ({s['image_bytes']} octets)", "",
             "## Plus gros fichiers", "", "| Fichier | Octets |", "|---|---:|"]
    for f in report["largest_files"]:
        lines.append(f"| {f['path']} | {f['bytes']} |")
    lines += ["", "## Signaux", "", "| Sévérité | Fichier:Ligne | Signal | Pourquoi | RGESN |", "|---|---|---|---|---|"]
    for x in report["signals"][:80]:
        lines.append(f"| {x['severity']} | {x['file']}:{x['line']} | {x['id']} | {x['why']} | {x['greenit']} |")
    if len(report["signals"]) > 80:
        lines.append(f"| … | | {len(report['signals']) - 80} autres | | |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()
    if not args.root.is_dir():
        print(f"ERREUR : {args.root} n’est pas un dossier", file=sys.stderr)
        return 2
    report = scan(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(f"OK {report['summary']['files']} fichiers, {report['summary']['signals']} signaux -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
