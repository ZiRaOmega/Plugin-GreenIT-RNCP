#!/usr/bin/env python3
"""Vérifie les livrables générés par la démonstration."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def check_metrics() -> None:
    p = DIST / "audit-demo" / "metrics.json"
    if not p.exists():
        err("metrics.json manquant")
        return
    m = json.loads(p.read_text(encoding="utf-8"))
    if m.get("meta", {}).get("version") != "0.1.2":
        err(f"metrics.json : version moteur {m.get('meta', {}).get('version')!r}, attendu 0.1.2")
    for k in ("gwp", "adpe", "adpf"):
        if m["totals"].get(k, 0) <= 0:
            err(f"total {k} non positif")
    tier_sum = sum(x["share_gwp"] for x in m["shares"]["by_tier"])
    if abs(tier_sum - 100) > 0.1:
        err(f"somme des parts par tier = {tier_sum}, attendu 100 ±0,1")
    for item in m["items"]:
        if not item.get("factor_id") or not item.get("source_id"):
            err(f"item {item.get('id')} sans factor_id ou source_id")
        for key in ("gwp", "adpe", "adpf"):
            if item.get(key) is None:
                err(f"{item.get('id')}: {key} non évalué")
    for key in ("gwp", "adpe", "adpf"):
        if m.get("indicator_status", {}).get(key, {}).get("status") != "évalué":
            err(f"{key} devrait être entièrement évalué")
    report = (DIST / "audit-demo" / "report.md").read_text(encoding="utf-8")
    if "non évalué" in report.lower() or "à évaluer" in report.lower():
        err("report.md contient encore une mention non évaluée")


def check_hypotheses() -> None:
    p = DIST / "audit-demo" / "hypotheses.csv"
    if not p.exists():
        err("hypotheses.csv manquant")
        return
    rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
    if len(rows) < 7:
        err(f"hypotheses.csv : {len(rows)} lignes, attendu 7")
    for r in rows:
        for key in ("status", "evidence_status", "owner", "due", "evidence"):
            if not r.get(key):
                err(f"hypothèse {r.get('id')} sans {key}")
        if r.get("status", "").startswith("à "):
            err(f"hypothèse {r.get('id')} encore non évaluée : {r.get('status')}")
        if r.get("evidence_status") not in {"preuve", "sans preuve", "convention"}:
            err(f"hypothèse {r.get('id')} : evidence_status invalide")


def check_rgesn() -> None:
    p = ROOT / "plugins/greenit-audit/references/rgesn-2024.csv"
    rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
    if len(rows) != 78:
        err(f"RGESN : {len(rows)} lignes, attendu 78")
    counts = Counter(r["chapter"] for r in rows)
    expected = {"1 — Stratégie": 10, "2 — Spécifications": 10, "3 — Architecture": 7,
                "4 — Expérience et interface utilisateur": 15, "5 — Contenus": 8,
                "6 — Frontend": 7, "7 — Backend": 4, "8 — Hébergement": 10,
                "9 — Algorithmie": 7}
    if dict(counts) != expected:
        err(f"RGESN counts inattendus : {dict(counts)}")
    score_csv = DIST / "audit-demo" / "rgesn-score.csv"
    if not score_csv.exists():
        err("rgesn-score.csv manquant")
        return
    score_rows = list(csv.DictReader(score_csv.open(encoding="utf-8-sig")))
    if len(score_rows) != 78:
        err(f"rgesn-score.csv : {len(score_rows)} lignes, attendu 78")
    if any(r["status"] == "à évaluer" for r in score_rows):
        err("rgesn-score.csv contient encore des critères à évaluer")
    if any(not r["status"] for r in score_rows):
        err("rgesn-score.csv contient un statut vide")


def check_docx_pdf() -> None:
    from docx import Document
    p = DIST / "rapport-audit-greenit-demo.docx"
    if not p.exists():
        err("DOCX manquant")
        return
    if p.stat().st_size < 30_000:
        err(f"DOCX trop petit : {p.stat().st_size} octets")
    doc = Document(p)
    h1 = [x for x in doc.paragraphs if x.style.name.lower().startswith("heading 1")]
    if len(h1) < 19:
        err(f"DOCX : {len(h1)} sections h1, attendu 19")
    text = "\n".join(x.text for x in doc.paragraphs)
    for needle in ("Sources", "Glossaire", "note de calcul", "Conditions de validité"):
        if needle.lower() not in text.lower():
            err(f"DOCX : chaîne absente {needle!r}")
    pdf = DIST / "rapport-audit-greenit-demo.pdf"
    if not pdf.exists():
        err("PDF du rapport manquant")
        return
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    m = re.search(r"^Pages:\s+(\d+)", info, re.M)
    if not m or int(m.group(1)) < 12:
        err(f"PDF : pages insuffisantes ({m.group(1) if m else '?'})")
    txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    for needle in ("Synthèse", "Unité fonctionnelle", "Sources"):
        if needle.lower() not in txt.lower():
            err(f"PDF : chaîne absente {needle!r}")


def check_client_summary() -> None:
    docx = DIST / "synthese-client-greenit-demo.docx"
    pdf = DIST / "synthese-client-greenit-demo.pdf"
    if not docx.exists() or not pdf.exists():
        err("synthèse client DOCX/PDF manquante")
        return
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    m = re.search(r"^Pages:\s+(\d+)", info, re.M)
    if not m or int(m.group(1)) < 2:
        err("synthèse client : moins de 2 pages")
    txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    if "Décisions recommandées" not in txt:
        err("synthèse client : section Décisions absente")


def check_pptx_video() -> None:
    from pptx import Presentation
    p = DIST / "soutenance-greenit-demo.pptx"
    if not p.exists():
        err("PPTX manquant")
        return
    prs = Presentation(p)
    if not (12 <= len(prs.slides) <= 15):
        err(f"PPTX : {len(prs.slides)} slides, attendu 12–15")
    data_slides = 0
    for i, slide in enumerate(prs.slides, start=1):
        text = " ".join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)
        if i not in (1, 15) and ("Source" in text or "source" in text):
            data_slides += 1
        if not slide.notes_slide.notes_text_frame.text.strip():
            err(f"PPTX slide {i} sans notes")
    if data_slides < 10:
        warn(f"PPTX : seulement {data_slides} slides avec source")
    notes = DIST / "notes-orales-demo.md"
    if not notes.exists():
        err("notes-orales-demo.md manquant")
    else:
        words = len(notes.read_text(encoding="utf-8").split())
        if not (1800 <= words <= 2200):
            err(f"notes orales : {words} mots, attendu 1800–2200")
    video = DIST / "teaser-greenit-demo.mp4"
    if not video.exists():
        err("vidéo manquante")
        return
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                      "-show_entries", "stream=width,height,codec_name", "-of", "json",
                                      str(video)], capture_output=True, text=True, check=True).stdout)
    duration = float(info["format"]["duration"])
    stream = info["streams"][0]
    if not (60 <= duration <= 90):
        err(f"vidéo : durée {duration:.1f}s hors 60–90")
    if (stream.get("width"), stream.get("height")) != (1920, 1080):
        err(f"vidéo : résolution {stream.get('width')}x{stream.get('height')}")
    if stream.get("codec_name") != "h264":
        err(f"vidéo : codec {stream.get('codec_name')}")


def check_rncp() -> None:
    p = DIST / "rncp39388" / "01-matrice-competences.csv"
    if not p.exists():
        err("matrice RNCP manquante")
        return
    rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
    if len(rows) != 19:
        err(f"matrice RNCP : {len(rows)} lignes, attendu 19")
    if len({r["block"] for r in rows}) != 4:
        err("matrice RNCP : blocs != 4")
    dossier = DIST / "rncp39388" / "02-dossier-preuves.md"
    if not dossier.exists():
        err("dossier de preuves manquant")
    else:
        text = dossier.read_text(encoding="utf-8")
        for r in rows:
            if r["competency_id"] not in text:
                err(f"preuve absente pour {r['competency_id']}")
    formation = DIST / "rncp39388" / "09-formation-greenit.md"
    if not formation.exists():
        err("formation manquante")
    else:
        t = formation.read_text(encoding="utf-8")
        if "Quiz" not in t or "Exercice" not in t:
            err("formation : quiz ou exercice manquant")


def check_quality() -> None:
    docs = [DIST / "audit-demo" / "report.md", DIST / "notes-orales-demo.md"]
    docs += list((DIST / "rncp39388").glob("*.md"))
    text = "\n".join(p.read_text(encoding="utf-8") for p in docs if p.exists())
    for bad in ("TODO", "Lorem", "placeholder"):
        if re.search(rf"\b{re.escape(bad)}\b", text):
            err(f"placeholder détecté : {bad}")
    if "100 % vert" in text.lower():
        err("formule greenwashing : 100 % vert")
    if "neutre en carbone" in text.lower():
        err("formule greenwashing : neutre en carbone")
    report = (DIST / "audit-demo" / "report.md").read_text(encoding="utf-8").lower()
    for needle in ("nous", "hypothèse", "limite", "source"):
        if needle not in report:
            err(f"rapport : {needle!r} absent")
    # Compensation autorisée seulement dans les limites / idées écartées.
    if "compensation" in report:
        for line in report.splitlines():
            if "compensation" in line.lower() and not any(k in line.lower() for k in ("écart", "ne pas", "pas de", "limite", "éviter", "ne rend pas")):
                warn(f"compensation citée hors limites : {line[:120]}")


def check_sources() -> None:
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_sources.py")], capture_output=True, text=True)
    if p.returncode != 0:
        err("check_sources.py a échoué\n" + p.stdout + p.stderr)


def main() -> int:
    if not DIST.exists():
        print("ERREUR : dist/ absent ; lancer make demo", file=sys.stderr)
        return 1
    check_metrics()
    check_hypotheses()
    check_rgesn()
    check_docx_pdf()
    check_client_summary()
    check_pptx_video()
    check_rncp()
    check_quality()
    check_sources()
    for w in WARNINGS:
        print("AVERTISSEMENT :", w)
    if ERRORS:
        for e in ERRORS:
            print("ERREUR :", e, file=sys.stderr)
        return 1
    print("CHECK OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
