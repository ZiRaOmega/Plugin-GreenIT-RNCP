#!/usr/bin/env python3
"""Crée une copie optimisée du service de démonstration et documente les changements."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from PIL import Image


def minify_css(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([{}:;,>])\s*", r"\1", text)
    return text.strip()


def optimize_html(text: str) -> tuple[str, list[str]]:
    changes = []
    if "<img" in text and not re.search(r"<img[^>]*\balt=", text):
        text = re.sub(r"<img\b", '<img alt="Illustration de la page d’émargement"', text, count=1)
        changes.append("Ajout d’un texte alternatif sur l’image.")
    if 'target="_blank"' in text and "noopener" not in text:
        text = text.replace('target="_blank"', 'target="_blank" rel="noopener noreferrer"')
        changes.append("Ajout de rel=noopener noreferrer.")
    if 'type="text"' in text and "id=" not in text.split("type=\"text\"")[1].split(">")[0]:
        text = text.replace('<input type="text" placeholder="Votre nom">',
                            '<label for="name">Votre nom</label>\n        <input id="name" name="name" type="text" placeholder="Votre nom">')
        changes.append("Ajout d’un label et d’un id au champ de saisie.")
    return text, changes


def optimize_js(text: str) -> tuple[str, list[str]]:
    changes = []
    if "console.log" in text:
        text = re.sub(r"^\s*console\.log\(.*?\);\s*$", "", text, flags=re.M)
        changes.append("Suppression des traces console.log.")
    if "setInterval" in text:
        text = re.sub(r"^\s*setInterval\([^;]+\);\s*$", "", text, flags=re.M)
        changes.append("Suppression du polling setInterval toutes les 5 s.")
    if "// TODO" in text:
        text = re.sub(r"^\s*// TODO.*$", "", text, flags=re.M)
        changes.append("Suppression du TODO de debug.")
    if "innerHTML" in text:
        text = text.replace('list.innerHTML = "";', "list.replaceChildren();")
        changes.append("Remplacement de innerHTML par replaceChildren pour vider la liste.")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, changes


def optimize_server(text: str) -> tuple[str, list[str]]:
    changes = []
    if 'Access-Control-Allow-Origin", "*"' in text:
        text = text.replace('self.send_header("Access-Control-Allow-Origin", "*")',
                            'self.send_header("Cache-Control", "public, max-age=3600")')
        changes.append("Suppression du CORS permissif et ajout de Cache-Control.")
    if "SELECT * FROM presences" in text:
        text = text.replace("SELECT * FROM presences", "SELECT id, name, created_at FROM presences")
        changes.append("Remplacement de SELECT * par une sélection explicite.")
    if "SECRET" in text:
        text = re.sub(r"^SECRET\s*=.*$\n?", "", text, flags=re.M)
        changes.append("Suppression d’un secret factice.")
    return text, changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=Path("examples/demo-service"))
    ap.add_argument("--dst", type=Path, default=Path("examples/demo-service-optimized"))
    args = ap.parse_args()
    if args.dst.exists():
        shutil.rmtree(args.dst)
    shutil.copytree(args.src, args.dst)
    changes: list[str] = []
    # HTML
    html_path = args.dst / "web" / "index.html"
    html, c = optimize_html(html_path.read_text(encoding="utf-8"))
    changes += c
    # Image
    img_path = args.dst / "web" / "images" / "hero.png"
    if img_path.exists():
        img = Image.open(img_path).convert("RGB")
        img.thumbnail((640, 640))
        jpg = img_path.with_suffix(".jpg")
        img.save(jpg, quality=72, optimize=True)
        img_path.unlink()
        html = html.replace("images/hero.png", "images/hero.jpg")
        changes.append(f"Image redimensionnée et convertie en JPEG ({jpg.stat().st_size} octets).")
    html_path.write_text(html, encoding="utf-8")
    # CSS
    css_path = args.dst / "web" / "styles.css"
    css = minify_css(css_path.read_text(encoding="utf-8"))
    css_path.write_text(css, encoding="utf-8")
    changes.append(f"CSS minifié ({len(css)} octets).")
    # JS
    js_path = args.dst / "web" / "app.js"
    js, c = optimize_js(js_path.read_text(encoding="utf-8"))
    js_path.write_text(js, encoding="utf-8")
    changes += c
    # Server
    server_path = args.dst / "api" / "server.py"
    server, c = optimize_server(server_path.read_text(encoding="utf-8"))
    server_path.write_text(server, encoding="utf-8")
    changes += c
    # SQL
    sql_path = args.dst / "api" / "db" / "schema.sql"
    sql = sql_path.read_text(encoding="utf-8")
    if "INDEX" not in sql:
        sql += "\nCREATE INDEX IF NOT EXISTS idx_presences_created_at ON presences(created_at);\n"
        changes.append("Ajout d’un index sur created_at.")
    sql_path.write_text(sql, encoding="utf-8")
    # Remove local db if copied
    db = args.dst / "api" / "emargement.db"
    if db.exists():
        db.unlink()
    report = {"src": str(args.src), "dst": str(args.dst), "changes": changes}
    (args.dst / "optimization-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {len(changes)} changements -> {args.dst}")
    for c in changes:
        print(f"  - {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
