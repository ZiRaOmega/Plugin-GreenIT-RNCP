#!/usr/bin/env python3
"""Construit un diaporama PPTX 16:9 depuis deck.yml."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import THEME  # noqa: E402

W, H = 13.333, 7.5
GREEN = RGBColor.from_string(THEME["green_900"].lstrip("#"))
GREEN_700 = RGBColor.from_string(THEME["green_700"].lstrip("#"))
TEXT = RGBColor.from_string(THEME["text"].lstrip("#"))
MUTED = RGBColor.from_string(THEME["muted"].lstrip("#"))
BG = RGBColor.from_string(THEME["bg"].lstrip("#"))
ACCENT = RGBColor.from_string(THEME["accent"].lstrip("#"))
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


def fill(shape, color: RGBColor):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def textbox(slide, left, top, width, height, text="", size=20, bold=False,
            color=TEXT, align=PP_ALIGN.LEFT, font="Liberation Sans", anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = font
    run.font.color.rgb = color
    return box


def add_bullets(slide, bullets, left=0.9, top=1.75, width=11.7, height=4.9):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for idx, bullet in enumerate(bullets):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(12)
        p.level = 0
        run = p.add_run()
        run.text = "•  " + str(bullet)
        run.font.size = Pt(20)
        run.font.name = "Liberation Sans"
        run.font.color.rgb = TEXT
    return box


def chrome(slide, meta, number, source=""):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    fill(bg, BG)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(0.12))
    fill(bar, GREEN)
    textbox(slide, 0.55, 7.02, 7.8, 0.3, meta.get("footer", "Audit Green IT"), 9, False, MUTED)
    textbox(slide, 11.7, 7.02, 1.1, 0.3, str(number), 9, False, MUTED, PP_ALIGN.RIGHT)
    if source:
        textbox(slide, 0.55, 6.62, 12.2, 0.3, "Source : " + source, 8.5, False, MUTED)


def heading(slide, kicker, title, subtitle=""):
    if kicker:
        textbox(slide, 0.85, 0.55, 11.5, 0.35, kicker.upper(), 11, True, GREEN_700)
    textbox(slide, 0.8, 0.95, 11.8, 0.9, title, 30, True, GREEN)
    if subtitle:
        textbox(slide, 0.85, 1.55, 11.6, 0.5, subtitle, 14, False, MUTED)


def slide_title(prs, s, meta, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    fill(bg, GREEN)
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.18), Inches(H))
    fill(accent, ACCENT)
    textbox(slide, 0.9, 1.45, 11.5, 1.7, s.get("title", meta.get("title", "")), 40, True, WHITE)
    textbox(slide, 0.95, 3.25, 10.8, 1.0, s.get("subtitle", meta.get("subtitle", "")), 21, False, RGBColor(0xD8, 0xF3, 0xDC))
    textbox(slide, 0.95, 5.0, 10.8, 0.5, f"{meta.get('client', '')}  •  {meta.get('date', '')}", 14, False, WHITE)
    textbox(slide, 0.95, 5.5, 10.8, 0.5, " • ".join(meta.get("authors", [])), 13, False, RGBColor(0xB7, 0xE4, 0xC7))
    add_notes(slide, s)
    return slide


def slide_section(prs, s, meta, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    fill(bg, GREEN)
    textbox(slide, 0.9, 2.4, 11.4, 0.4, s.get("kicker", "").upper(), 12, True, ACCENT)
    textbox(slide, 0.9, 2.9, 11.4, 1.6, s.get("title", ""), 36, True, WHITE)
    if s.get("subtitle"):
        textbox(slide, 0.95, 4.55, 10.8, 0.8, s["subtitle"], 17, False, RGBColor(0xD8, 0xF3, 0xDC))
    add_notes(slide, s)
    return slide


def slide_bullets(prs, s, meta, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, meta, number, s.get("source", ""))
    heading(slide, s.get("kicker", ""), s.get("title", ""), s.get("subtitle", ""))
    bullets = s.get("bullets", [])
    if len(bullets) > 6:
        print(f"AVERTISSEMENT slide {number} : {len(bullets)} puces, réduire.")
    add_bullets(slide, bullets[:6])
    add_notes(slide, s)
    return slide


def slide_metrics(prs, s, meta, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, meta, number, s.get("source", ""))
    heading(slide, s.get("kicker", ""), s.get("title", ""), s.get("subtitle", ""))
    cards = s.get("cards", [])[:3]
    n = max(1, len(cards))
    width = 11.4 / n
    for i, card in enumerate(cards):
        left = 0.9 + i * width
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(2.1), Inches(width - 0.25), Inches(3.8))
        fill(box, WHITE)
        textbox(slide, left + 0.25, 2.35, width - 0.7, 1.0, str(card.get("value", "")), 34, True, GREEN)
        textbox(slide, left + 0.25, 3.35, width - 0.7, 0.7, str(card.get("label", "")), 15, True, TEXT)
        if card.get("detail"):
            textbox(slide, left + 0.25, 4.05, width - 0.7, 1.5, str(card["detail"]), 12, False, MUTED)
    add_notes(slide, s)
    return slide


def slide_chart(prs, s, meta, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, meta, number, s.get("source", ""))
    heading(slide, s.get("kicker", ""), s.get("title", ""), s.get("subtitle", ""))
    img = s.get("image")
    if img and Path(img).exists():
        slide.shapes.add_picture(str(img), Inches(0.9), Inches(1.85), width=Inches(9.4))
    else:
        textbox(slide, 1.0, 2.2, 8.0, 1.0, "[figure manquante]", 20, True, MUTED)
    if s.get("takeaway"):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.35), Inches(2.0), Inches(2.2), Inches(3.4))
        fill(box, RGBColor(0xD8, 0xF3, 0xDC))
        textbox(slide, 10.5, 2.2, 1.9, 3.0, s["takeaway"], 13, True, GREEN)
    add_notes(slide, s)
    return slide


def slide_matrix(prs, s, meta, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, meta, number, s.get("source", ""))
    heading(slide, s.get("kicker", ""), s.get("title", ""), s.get("subtitle", ""))
    x0, y0, size = 1.0, 1.9, 5.0
    colors = [RGBColor(0xD8, 0xF3, 0xDC), RGBColor(0xB7, 0xE4, 0xC7),
              RGBColor(0xF7, 0xF5, 0xEF), RGBColor(0xE9, 0xC4, 0x6A)]
    labels = ["Quick wins", "Projets structurants", "À éviter", "À planifier"]
    for i in range(2):
        for j in range(2):
            shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x0 + j * size / 2), Inches(y0 + i * size / 2), Inches(size / 2), Inches(size / 2))
            fill(shp, colors[i * 2 + j])
            textbox(slide, x0 + j * size / 2 + 0.1, y0 + i * size / 2 + 0.1, size / 2 - 0.2, 0.3, labels[i * 2 + j], 10, True, GREEN)
    for item in s.get("items", [])[:8]:
        effort = float(item.get("effort", 0.5))
        impact = float(item.get("impact", 0.5))
        left = x0 + effort * size - 0.1
        top = y0 + (1 - impact) * size - 0.1
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(left), Inches(top), Inches(0.2), Inches(0.2))
        fill(dot, GREEN)
        textbox(slide, left + 0.12, top - 0.12, 1.25, 0.25, str(item.get("label", ""))[:18], 8.0, False, TEXT)
    textbox(slide, 6.4, 2.0, 5.8, 4.5, s.get("takeaway", ""), 16, False, TEXT)
    add_notes(slide, s)
    return slide


def slide_timeline(prs, s, meta, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, meta, number, s.get("source", ""))
    heading(slide, s.get("kicker", ""), s.get("title", ""), s.get("subtitle", ""))
    items = s.get("items", [])[:8]
    top = 2.0
    for i, item in enumerate(items):
        y = top + i * 0.55
        phase = str(item.get("phase", ""))
        textbox(slide, 0.9, y, 1.9, 0.35, phase, 11, True, GREEN)
        start = float(item.get("start", 0))
        end = float(item.get("end", 1))
        max_end = max([float(x.get("end", 1)) for x in items] + [1])
        left = 2.9 + (start / max_end) * 8.8
        width = max(0.3, ((end - start) / max_end) * 8.8)
        bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(y + 0.02), Inches(width), Inches(0.28))
        fill(bar, RGBColor.from_string(THEME["green_600"].lstrip("#")) if i % 2 == 0 else GREEN_700)
        textbox(slide, min(left + width + 0.1, 12.0), y, 1.2, 0.3, str(item.get("label", "")), 8.5, False, MUTED)
    add_notes(slide, s)
    return slide


def slide_quote(prs, s, meta, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    fill(bg, RGBColor(0xF7, 0xF5, 0xEF))
    textbox(slide, 0.9, 1.6, 0.8, 1.0, "“", 80, True, ACCENT)
    textbox(slide, 1.2, 2.2, 10.8, 2.6, s.get("quote", ""), 28, True, GREEN)
    textbox(slide, 1.25, 5.0, 10.5, 0.5, s.get("attribution", ""), 14, False, MUTED)
    add_notes(slide, s)
    return slide


def slide_closing(prs, s, meta, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    fill(bg, GREEN)
    textbox(slide, 0.9, 1.8, 11.4, 1.2, s.get("title", "Merci"), 42, True, WHITE)
    textbox(slide, 0.95, 3.2, 10.8, 0.8, s.get("subtitle", "Questions et échanges"), 22, False, RGBColor(0xD8, 0xF3, 0xDC))
    if s.get("bullets"):
        add_bullets(slide, s["bullets"][:3], top=4.2, height=2.0)
        for p in slide.shapes[-1].text_frame.paragraphs:
            for r in p.runs:
                r.font.color.rgb = WHITE
    add_notes(slide, s)
    return slide


def add_notes(slide, s):
    notes = str(s.get("notes", "")).strip()
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


BUILDERS = {"title": slide_title, "section": slide_section, "bullets": slide_bullets,
            "metrics": slide_metrics, "chart": slide_chart, "matrix": slide_matrix,
            "timeline": slide_timeline, "quote": slide_quote, "closing": slide_closing}


def build(deck: dict, out: Path, notes_path: Path | None = None) -> dict:
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    meta = deck.get("meta", {})
    warnings = []
    slides = deck.get("slides", [])
    if len(slides) > 15:
        warnings.append(f"{len(slides)} slides : dépassement de la limite de 15.")
    for idx, s in enumerate(slides, start=1):
        kind = s.get("layout", "bullets")
        if kind not in BUILDERS:
            raise ValueError(f"Layout inconnu : {kind}")
        BUILDERS[kind](prs, s, meta, idx)
        if kind == "bullets" and len(s.get("bullets", [])) > 6:
            warnings.append(f"Slide {idx} : plus de 6 puces.")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out)
    notes = []
    total_words = 0
    for idx, s in enumerate(slides, start=1):
        words = len(str(s.get("notes", "")).split())
        total_words += words
        notes.append(f"## Slide {idx} — {s.get('title', '')}\n\n{s.get('notes', '').strip()}\n")
    notes_md = "# Notes orales\n\n" + "\n".join(notes)
    notes_path = notes_path or out.with_name("notes-orales.md")
    notes_path.write_text(notes_md, encoding="utf-8")
    pdf = out.with_suffix(".pdf")
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out.parent), str(out)],
                       check=True, capture_output=True, timeout=180)
        pdf_ok = True
    except Exception as e:
        pdf_ok = False
        warnings.append(f"PDF non généré : {e}")
    report = {"pptx": str(out), "slides": len(slides), "notes_words": total_words,
              "warnings": warnings, "pdf": str(pdf) if pdf_ok else None}
    out.with_name("deck-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--notes", type=Path)
    ap.add_argument("--pdf", action="store_true")
    args = ap.parse_args()
    import yaml
    deck = yaml.safe_load(args.input.read_text(encoding="utf-8"))
    report = build(deck, args.out, args.notes)
    print(f"OK PPTX {report['pptx']} ({report['slides']} slides, {report['notes_words']} mots de notes)")
    for w in report["warnings"]:
        print(f"AVERTISSEMENT : {w}")
    if report["pdf"]:
        print(f"OK PDF {report['pdf']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
