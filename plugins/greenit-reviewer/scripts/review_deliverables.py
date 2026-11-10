#!/usr/bin/env python3
"""Revue indépendante des livrables PDF/PPTX, données, graphiques et RNCP39388."""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Emu
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "references"
AI_RE = re.compile(r"[\u2014\u2013\u201c\u201d\u2026\u00a0\u202f\u200b\U0001F300-\U0001FAFF]")
GREEN_HUE = range(80, 171)
ALLOWED_STATUS = {"validé", "en cours", "non validé", "non applicable"}


def load_json(p: Path | None) -> dict | None:
    if not p or not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def first(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def hex_to_rgb(value: str) -> tuple[int, int, int] | None:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        return None
    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def rgb_to_hue(rgb: tuple[int, int, int]) -> float:
    r, g, b = [x / 255 for x in rgb]
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn:
        return 0
    d = mx - mn
    if mx == r:
        h = (g - b) / d + (6 if g < b else 0)
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60


def color_hex(color) -> str | None:
    try:
        if color and color.type == 1:
            return "#" + str(color.rgb)
    except Exception:
        return None
    return None


def shape_text(shape) -> str:
    return shape.text_frame.text if getattr(shape, "has_text_frame", False) else ""


def overlap_area(a, b) -> float:
    l = max(a.left, b.left)
    t = max(a.top, b.top)
    r = min(a.left + a.width, b.left + b.width)
    btm = min(a.top + a.height, b.top + b.height)
    return max(0, r - l) * max(0, btm - t)


def review_pptx(path: Path, findings: list[dict]) -> dict:
    prs = Presentation(path)
    slide_w, slide_h = prs.slide_width, prs.slide_height
    out = {"path": str(path), "slides": len(prs.slides), "warnings": []}
    data_slides = 0
    all_notes = 0
    fonts = Counter()
    colors = Counter()
    for idx, slide in enumerate(prs.slides, start=1):
        text_shapes = []
        for shape in slide.shapes:
            txt = shape_text(shape).strip()
            if txt:
                text_shapes.append(shape)
                if shape.left < 0 or shape.top < 0 or shape.left + shape.width > slide_w + 1000 or shape.top + shape.height > slide_h + 1000:
                    findings.append({"severity": "blocker", "file": path.name, "slide": idx,
                                     "code": "text-out-of-bounds", "message": "Texte hors des limites de la slide.",
                                     "evidence": txt[:120]})
                for p in shape.text_frame.paragraphs:
                    for run in p.runs:
                        if run.font.size:
                            pt = run.font.size.pt
                            if pt < 8:
                                findings.append({"severity": "major", "file": path.name, "slide": idx,
                                                 "code": "font-too-small", "message": f"Police {pt:g} pt < 8 pt.",
                                                 "evidence": run.text[:80]})
                        if run.font.name:
                            fonts[run.font.name] += 1
                        c = color_hex(run.font.color)
                        if c:
                            colors[c] += 1
            for fill in (getattr(shape, "fill", None),):
                try:
                    c = color_hex(fill.fore_color)
                    if c:
                        colors[c] += 1
                except Exception:
                    pass
        for i in range(len(text_shapes)):
            for j in range(i + 1, len(text_shapes)):
                a, b = text_shapes[i], text_shapes[j]
                inter = overlap_area(a, b)
                small = min(a.width * a.height, b.width * b.height)
                if small and inter / small > 0.12:
                    findings.append({"severity": "blocker", "file": path.name, "slide": idx,
                                     "code": "text-overlap", "message": "Chevauchement de zones de texte > 12 %.",
                                     "evidence": f"{shape_text(a)[:40]!r} / {shape_text(b)[:40]!r}"})
        slide_text = " ".join(shape_text(s) for s in slide.shapes)
        if idx not in (1, len(prs.slides)) and ("source" in slide_text.lower() or "sources" in slide_text.lower()):
            data_slides += 1
        notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
        all_notes += len(notes.split())
        if not notes.strip():
            findings.append({"severity": "major", "file": path.name, "slide": idx,
                             "code": "missing-notes", "message": "Notes orales absentes."})
        if AI_RE.search(slide_text):
            findings.append({"severity": "major", "file": path.name, "slide": idx,
                             "code": "ai-characters", "message": "Caractère typographique IA détecté.",
                             "evidence": AI_RE.search(slide_text).group(0)})
    if not (12 <= len(prs.slides) <= 15):
        findings.append({"severity": "major", "file": path.name, "code": "slide-count",
                         "message": f"{len(prs.slides)} slides, attendu 12–15."})
    if data_slides < 10:
        findings.append({"severity": "major", "file": path.name, "code": "source-footers",
                         "message": f"Seulement {data_slides} slides de données avec source."})
    if not (1800 <= all_notes <= 2200):
        findings.append({"severity": "major", "file": path.name, "code": "notes-word-count",
                         "message": f"{all_notes} mots de notes, attendu 1800–2200."})
    out["notes_words"] = all_notes
    out["data_slides_with_source"] = data_slides
    out["fonts"] = dict(fonts)
    out["colors"] = dict(colors)
    return out


def review_pdf(path: Path, findings: list[dict], min_pages: int = 12, required: tuple[str, ...] = ("Synthèse", "Unité fonctionnelle", "Sources", "Glossaire")) -> dict:
    reader = PdfReader(path)
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    out = {"path": str(path), "pages": len(reader.pages), "text_chars": len(text)}
    if min_pages and len(reader.pages) < min_pages:
        findings.append({"severity": "major", "file": path.name, "code": "pdf-pages",
                         "message": f"{len(reader.pages)} pages, attendu > 12 pour le rapport."})
    if AI_RE.search(text):
        findings.append({"severity": "major", "file": path.name, "code": "ai-characters",
                         "message": "Caractère typographique IA détecté dans le PDF.",
                         "evidence": AI_RE.search(text).group(0)})
    for needle in required:
        if needle.lower() not in text.lower():
            findings.append({"severity": "major", "file": path.name, "code": "missing-section",
                             "message": f"Chaîne absente du PDF : {needle!r}."})
    # marges approximatives via pdftotext -bbox
    try:
        xml = subprocess.run(["pdftotext", "-bbox", str(path), "-"], capture_output=True, text=True, check=True).stdout
        pages = re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', xml, re.S)
        outside = 0; words = 0
        for w, h, body in pages:
            W, H = float(w), float(h)
            for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">', body):
                x0, y0, x1, y1 = map(float, m.groups()); words += 1
                if x0 < 20 or x1 > W - 20 or y0 < 12 or y1 > H - 12:
                    outside += 1
        out["pdf_words"] = words
        out["pdf_outside_margin"] = outside
        if words and outside / words > 0.02:
            findings.append({"severity": "major", "file": path.name, "code": "pdf-margins",
                             "message": f"{outside}/{words} mots hors marges."})
    except Exception as e:
        out["bbox_error"] = str(e)
    return out


def review_metrics(path: Path | None, findings: list[dict]) -> dict:
    m = load_json(path)
    if not m:
        findings.append({"severity": "blocker", "file": str(path), "code": "metrics-missing",
                         "message": "metrics.json absent."})
        return {}
    for k in ("gwp", "adpe", "adpf"):
        if m.get("totals", {}).get(k) is None:
            findings.append({"severity": "blocker", "file": path.name, "code": "metric-null",
                             "message": f"Total {k} non évalué."})
    tiers = m.get("shares", {}).get("by_tier", [])
    s = sum((r.get("share_gwp") or 0) for r in tiers)
    if abs(s - 100) > 0.1:
        findings.append({"severity": "blocker", "file": path.name, "code": "share-sum",
                         "message": f"Somme des parts par tier = {s:.3f}, attendu 100 ±0,1."})
    for item in m.get("items", []):
        if not item.get("factor_id") or not item.get("source_id"):
            findings.append({"severity": "blocker", "file": path.name, "code": "item-source",
                             "message": f"Item {item.get('id')} sans facteur/source."})
        if item.get("category") == "network" and (item.get("adpe") is None or item.get("adpf") is None):
            findings.append({"severity": "major", "file": path.name, "code": "network-indicator",
                             "message": f"Indicateur réseau incomplet pour {item.get('id')}."})
    return m


def review_rgesn(path: Path | None, findings: list[dict]) -> dict:
    if not path or not path.exists():
        findings.append({"severity": "blocker", "file": str(path), "code": "rgesn-missing",
                         "message": "rgesn-score.csv absent."})
        return {}
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    if len(rows) != 78:
        findings.append({"severity": "blocker", "file": path.name, "code": "rgesn-count",
                         "message": f"{len(rows)} critères, attendu 78."})
    for r in rows:
        if r.get("status") == "à évaluer" or not r.get("status"):
            findings.append({"severity": "blocker", "file": path.name, "code": "rgesn-status",
                             "message": f"Critère {r.get('id')} sans statut évalué."})
        if r.get("status") != "non applicable" and not r.get("evidence_status"):
            findings.append({"severity": "major", "file": path.name, "code": "rgesn-evidence",
                             "message": f"Critère {r.get('id')} sans evidence_status."})
    return {"rows": len(rows), "status": dict(Counter(r.get("status") for r in rows))}


def review_charts(charts_path: Path | None, figures: Path, findings: list[dict]) -> dict:
    if not charts_path or not charts_path.exists():
        findings.append({"severity": "major", "file": str(charts_path), "code": "charts-missing",
                         "message": "charts.yml absent."})
        return {}
    import yaml
    data = yaml.safe_load(charts_path.read_text(encoding="utf-8")) or {}
    charts = data.get("charts", data if isinstance(data, list) else [])
    for spec in charts:
        for key in ("id", "title", "source", "alt", "purpose"):
            if not spec.get(key):
                findings.append({"severity": "major", "file": charts_path.name, "code": "chart-field",
                                 "message": f"Figure {spec.get('id')} sans {key}."})
        img = figures / f"{spec.get('id')}.png"
        if not img.exists():
            findings.append({"severity": "blocker", "file": str(img), "code": "chart-missing",
                             "message": "Image de figure absente."})
            continue
        if img.stat().st_size < 2000:
            findings.append({"severity": "major", "file": str(img), "code": "chart-empty",
                             "message": "Figure trop petite, probablement vide."})
        try:
            im = Image.open(img).convert("L")
            if im.width < 800 or im.height < 450:
                findings.append({"severity": "major", "file": str(img), "code": "chart-size",
                                 "message": f"Dimensions {im.width}x{im.height} trop faibles."})
            hist = im.resize((64, 64)).getextrema()
            if hist[0] == hist[1]:
                findings.append({"severity": "blocker", "file": str(img), "code": "chart-blank",
                                 "message": "Figure uniforme, probablement vide."})
        except Exception:
            pass
        if spec.get("type") in {"stacked_bar", "donut", "tornado", "bar"} and spec.get("series") and not spec.get("legend"):
            findings.append({"severity": "minor", "file": charts_path.name, "code": "chart-legend",
                             "message": f"Figure {spec.get('id')} multi-séries sans légende explicite."})
    return {"charts": len(charts)}


def review_rncp(root: Path, findings: list[dict]) -> dict:
    base = root / "rncp39388"
    matrix = base / "01-matrice-competences.csv"
    if not matrix.exists():
        findings.append({"severity": "blocker", "file": str(matrix), "code": "rncp-matrix",
                         "message": "Matrice RNCP absente."})
        return {}
    rows = list(csv.DictReader(matrix.open(encoding="utf-8-sig")))
    if len(rows) != 19:
        findings.append({"severity": "blocker", "file": matrix.name, "code": "rncp-rows",
                         "message": f"{len(rows)} compétences, attendu 19."})
    blocks = {r.get("block") for r in rows}
    if len(blocks) != 4:
        findings.append({"severity": "blocker", "file": matrix.name, "code": "rncp-blocks",
                         "message": f"{len(blocks)} blocs, attendu 4."})
    for r in rows:
        ev = r.get("evidence")
        if ev and not (root / ev).exists() and not (root.parent / ev).exists():
            findings.append({"severity": "major", "file": matrix.name, "code": "rncp-evidence",
                             "message": f"Preuve absente pour {r.get('competency_id')} : {ev}."})
    proof = base / "02-dossier-preuves.md"
    if proof.exists():
        text = proof.read_text(encoding="utf-8")
        for r in rows:
            if r.get("competency_id") not in text:
                findings.append({"severity": "major", "file": proof.name, "code": "rncp-proof",
                                 "message": f"Compétence {r.get('competency_id')} absente du dossier."})
    return {"competencies": len(rows), "blocks": len(blocks)}


def review_glossary(text: str, findings: list[dict]) -> dict:
    required = [line.strip("- ").strip() for line in (REF / "required-glossary.md").read_text(encoding="utf-8").splitlines() if line.strip().startswith("- ")]
    missing = [t for t in required if t.lower() not in text.lower()]
    for t in missing:
        findings.append({"severity": "major", "file": "report.pdf", "code": "glossary-missing",
                         "message": f"Terme non défini dans le document : {t}."})
    return {"required": len(required), "missing": missing}


def review_palette(deck: Path | None, design: Path | None, findings: list[dict]) -> dict:
    if not design or not design.exists():
        findings.append({"severity": "major", "file": str(design), "code": "design-missing",
                         "message": "design.yml absent : impossible de vérifier la palette projet."})
        return {}
    import yaml
    d = yaml.safe_load(design.read_text(encoding="utf-8")) or {}
    source = str(d.get("source", "fallback")).lower()
    if source not in {"css", "logo", "tokens", "tailwind"}:
        findings.append({"severity": "major", "file": str(design), "code": "design-source",
                         "message": f"Palette non extraite du projet (source={source})."})
    allowed = {c.lower() for c in (d.get("colors") or {}).values() if isinstance(c, str)}
    allowed.add("#ffffff")
    if deck:
        prs = Presentation(deck)
        seen = set()
        for slide in prs.slides:
            for shape in slide.shapes:
                for fill in (getattr(shape, "fill", None),):
                    try:
                        c = color_hex(fill.fore_color)
                        if c: seen.add(c.lower())
                    except Exception: pass
                if shape.has_text_frame:
                    for p in shape.text_frame.paragraphs:
                        for run in p.runs:
                            c = color_hex(run.font.color)
                            if c: seen.add(c.lower())
        bad = sorted(c for c in seen if c not in allowed)
        for c in bad:
            findings.append({"severity": "major", "file": deck.name, "code": "palette",
                             "message": f"Couleur hors palette projet : {c}.",
                             "evidence": c})
        greens = [c for c in seen if (rgb := hex_to_rgb(c)) and 90 <= rgb_to_hue(rgb) <= 160]
        if greens and not any(c in allowed for c in greens):
            findings.append({"severity": "major", "file": deck.name, "code": "green-default",
                             "message": "Couleurs vertes dominantes hors palette projet."})
        return {"seen": len(seen), "outside": len(bad), "greens": len(greens)}
    return {}


def review_docx_palette(docx: Path | None, design: Path | None, findings: list[dict]) -> dict:
    if not docx or not docx.exists() or not design or not design.exists():
        return {}
    import yaml
    from docx import Document
    d = yaml.safe_load(design.read_text(encoding="utf-8")) or {}
    allowed = {str(c).lower() for c in (d.get("colors") or {}).values()}
    allowed.add("#ffffff")
    doc = Document(docx)
    bad = set()
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for shd in cell._tc.xpath('.//w:shd'):
                    fill = shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill')
                    if fill and fill.lower() not in {a.lstrip('#') for a in allowed}:
                        bad.add(fill.lower())
    for b in sorted(bad):
        findings.append({"severity": "major", "file": docx.name, "code": "docx-palette",
                         "message": f"Fond de tableau hors palette projet : #{b}."})
    return {"outside": len(bad)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("dist"))
    ap.add_argument("--report", type=Path)
    ap.add_argument("--deck", type=Path)
    ap.add_argument("--docx", type=Path)
    ap.add_argument("--synthese-pdf", type=Path)
    ap.add_argument("--soutenance-pdf", type=Path)
    ap.add_argument("--synthese-docx", type=Path)
    ap.add_argument("--metrics", type=Path)
    ap.add_argument("--rgesn", type=Path)
    ap.add_argument("--charts", type=Path)
    ap.add_argument("--figures", type=Path)
    ap.add_argument("--design", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    root = args.root.resolve()
    report = args.report or first([root / "rapport-audit-greenit-demo.pdf", root / "rapport.pdf"])
    deck = args.deck or first([root / "soutenance-greenit-demo.pptx", root / "soutenance.pptx"])
    docx = args.docx or first([root / "rapport-audit-greenit-demo.docx", root / "rapport.docx"])
    synthese_pdf = args.synthese_pdf or first([root / "synthese-client-greenit-demo.pdf", root / "synthese-client.pdf"])
    soutenance_pdf = args.soutenance_pdf or first([root / "soutenance-greenit-demo.pdf", root / "soutenance.pdf"])
    synthese_docx = args.synthese_docx or first([root / "synthese-client-greenit-demo.docx", root / "synthese-client.docx"])
    metrics = args.metrics or first([root / "audit-demo/metrics.json", root / "metrics.json"])
    rgesn = args.rgesn or first([root / "audit-demo/rgesn-score.csv", root / "rgesn-score.csv"])
    charts = args.charts or first([root / "audit-demo/charts.yml", root / "charts.yml"])
    figures = args.figures or root / "figures"
    design = args.design or first([root / "design.yml", root / "audit-demo/design.yml"])
    findings: list[dict] = []
    summary = {}
    if deck:
        summary["pptx"] = review_pptx(deck, findings)
    else:
        findings.append({"severity": "blocker", "file": str(deck), "code": "pptx-missing", "message": "PPTX absent."})
    if report:
        summary["pdf"] = review_pdf(report, findings)
        pdf_text = "\n".join((p.extract_text() or "") for p in PdfReader(report).pages)
        summary["glossary"] = review_glossary(pdf_text, findings)
    if synthese_pdf:
        summary["synthese_pdf"] = review_pdf(synthese_pdf, findings, min_pages=2, required=("Décisions", "Conditions"))
    if soutenance_pdf:
        summary["soutenance_pdf"] = review_pdf(soutenance_pdf, findings, min_pages=10, required=())
    else:
        findings.append({"severity": "blocker", "file": str(report), "code": "pdf-missing", "message": "PDF absent."})
    summary["metrics"] = review_metrics(metrics, findings)
    summary["rgesn"] = review_rgesn(rgesn, findings)
    summary["charts"] = review_charts(charts, figures, findings)
    summary["palette"] = review_palette(deck, design, findings)
    summary["docx_palette"] = review_docx_palette(docx, design, findings)
    if synthese_docx:
        summary["synthese_docx_palette"] = review_docx_palette(synthese_docx, design, findings)
    summary["rncp"] = review_rncp(root, findings)
    order = {"blocker": 0, "major": 1, "minor": 2}
    findings.sort(key=lambda f: (order.get(f["severity"], 9), f.get("file", ""), f.get("slide", 0)))
    result = {"root": str(root), "files": {"report": str(report), "deck": str(deck),
                                             "synthese_pdf": str(synthese_pdf), "soutenance_pdf": str(soutenance_pdf),
                                             "docx": str(docx), "synthese_docx": str(synthese_docx)},
              "summary": summary, "findings": findings,
              "counts": dict(Counter(f["severity"] for f in findings))}
    out = args.out or root / "review-report.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# Revue indépendante des livrables", "", f"Racine : `{root}`", "",
          "## Synthèse", "", "| Sévérité | Nombre |", "|---|---:|"]
    for sev in ("blocker", "major", "minor"):
        md.append(f"| {sev} | {result['counts'].get(sev, 0)} |")
    md += ["", "## Constats", ""]
    for f in findings:
        loc = f.get("file", "")
        if f.get("slide"):
            loc += f":{f['slide']}"
        md.append(f"- **{f['severity'].upper()}** `{f.get('code')}` — {f['message']} ({loc})")
    if not findings:
        md.append("Aucun constat.")
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"OK revue {len(findings)} constats -> {out}")
    return 1 if result["counts"].get("blocker") else 0


if __name__ == "__main__":
    raise SystemExit(main())
