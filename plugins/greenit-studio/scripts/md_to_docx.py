#!/usr/bin/env python3
"""Convertit un rapport Markdown en DOCX stylé, puis PDF via LibreOffice."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import THEME, hex_to_rgb, load_design, theme_from_design  # noqa: E402

GREEN = RGBColor.from_string(THEME["green_900"].lstrip("#"))
MUTED = RGBColor.from_string(THEME["muted"].lstrip("#"))
CALLOUT_COLORS = {}
CALLOUT_COLORS = {
    "info": "E8EEFF",
    "hypothese": "FFF3CD",
    "limite": "F8D7DA",
    "decision": "D1ECF1",
    "aretenir": "E8EEFF",
}


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill.lstrip("#"))
    tc_pr.append(shd)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_page_number(paragraph) -> None:
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr)
    run._r.append(fld_char2)
    run.add_text(" / ")
    run2 = paragraph.add_run()
    fld_char3 = OxmlElement("w:fldChar")
    fld_char3.set(qn("w:fldCharType"), "begin")
    instr2 = OxmlElement("w:instrText")
    instr2.set(qn("xml:space"), "preserve")
    instr2.text = "NUMPAGES"
    fld_char4 = OxmlElement("w:fldChar")
    fld_char4.set(qn("w:fldCharType"), "end")
    run2._r.append(fld_char3)
    run2._r.append(instr2)
    run2._r.append(fld_char4)


def add_toc_field(paragraph) -> None:
    run = paragraph.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-2" \\h \\z \\u'
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "separate")
    fld_char3 = OxmlElement("w:fldChar")
    fld_char3.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char)
    run._r.append(instr)
    run._r.append(fld_char2)
    run._r.append(fld_char3)


def make_cover(metadata: dict, out: Path) -> Path:
    width, height = 1600, 1000
    img = Image.new("RGB", (width, height), THEME["green_900"])
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, width, 18), fill=THEME["accent"])
    d.ellipse((width - 420, -180, width + 180, 420), fill=THEME["green_700"])
    d.ellipse((-220, height - 280, 320, height + 220), fill=THEME["green_800"])
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    except OSError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_small = ImageFont.load_default()
    title = metadata.get("title", "Audit Green IT")
    lines = []
    current = ""
    for word in title.split():
        if len(current) + len(word) > 28:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        lines.append(current)
    y = 210
    for line in lines:
        d.text((110, y), line, font=font_title, fill="#FFFFFF")
        y += 78
    d.text((110, y + 30), metadata.get("subtitle", "Rapport d’audit GreenIT"), font=font_sub, fill=THEME["green_200"])
    d.text((110, 760), f"Client : {metadata.get('client', '—')}", font=font_small, fill="#FFFFFF")
    d.text((110, 810), f"Auteurs : {', '.join(metadata.get('authors', []))}", font=font_small, fill="#FFFFFF")
    d.text((110, 860), f"Date : {metadata.get('date', '—')}  •  Version : {metadata.get('version', '1.0')}", font=font_small, fill="#FFFFFF")
    d.text((110, 920), "Document pédagogique — ACV screening, pas audit certifié", font=font_small, fill=THEME["green_300"])
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return out


def add_runs(paragraph, text: str, size: float | None = None) -> None:
    token = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")
    parts = token.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Liberation Mono"
            run.font.size = Pt(8.5)
        else:
            run = paragraph.add_run(part)
        if size:
            run.font.size = Pt(size)


def add_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    table = doc.add_table(rows=0, cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for cidx in range(ncols):
            text = row[cidx] if cidx < len(row) else ""
            cell = cells[cidx]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            add_runs(p, text, 8.5)
            if ridx == 0:
                for run in p.runs:
                    run.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                set_cell_shading(cell, THEME["green_900"])
        if ridx == 0:
            set_repeat_table_header(table.rows[0])
    doc.add_paragraph()


def add_callout(doc: Document, tone: str, title: str, body: list[str]) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    cell.text = ""
    p = cell.paragraphs[0]
    if title:
        run = p.add_run(title)
        run.bold = True
        run.font.color.rgb = GREEN
        run.font.size = Pt(10.5)
    for line in body:
        if line.strip():
            p2 = cell.add_paragraph()
            add_runs(p2, line.strip(), 10)
    set_cell_shading(cell, CALLOUT_COLORS.get(tone, "D8F3DC"))
    doc.add_paragraph()


def apply_theme(theme: dict) -> None:
    global GREEN, MUTED, CALLOUT_COLORS
    GREEN = RGBColor.from_string(theme["green_900"].lstrip("#"))
    MUTED = RGBColor.from_string(theme["muted"].lstrip("#"))
    light = theme.get("green_200", "D8F3DC").lstrip("#")
    CALLOUT_COLORS = {
        "info": light, "hypothese": "FFF3CD", "limite": "F8D7DA",
        "decision": "D1ECF1", "aretenir": light,
    }


def build(md_path: Path, metadata: dict, figures_dir: Path, out: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    doc = Document()
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)
    normal = doc.styles["Normal"]
    normal.font.name = "Liberation Sans"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.line_spacing = 1.25
    normal.paragraph_format.space_after = Pt(6)
    for i, size in [(1, 22), (2, 16), (3, 13)]:
        style = doc.styles[f"Heading {i}"]
        style.font.name = "Liberation Sans"
        style.font.size = Pt(size)
        style.font.color.rgb = GREEN
        style.paragraph_format.space_before = Pt(14 if i == 1 else 10)
        style.paragraph_format.space_after = Pt(6)

    header = section.header.paragraphs[0]
    header.text = metadata.get("header", "Audit Green IT").replace("—", "-").replace("–", "-")
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.runs[0].font.size = Pt(8.5)
    header.runs[0].font.color.rgb = MUTED
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Page ")
    add_page_number(footer)
    for run in footer.runs:
        run.font.size = Pt(8.5)
        run.font.color.rgb = MUTED

    cover = metadata.get("cover")
    cover_path = Path(cover) if cover else make_cover(metadata, out.parent / "cover.png")
    if cover_path.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(cover_path), width=Cm(16.6))
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Sommaire")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = GREEN
    add_toc_field(doc.add_paragraph())
    doc.add_page_break()

    sections = figures = tables = 0
    i = 0
    paragraph_lines: list[str] = []

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            p = doc.add_paragraph()
            add_runs(p, " ".join(paragraph_lines))
            paragraph_lines = []

    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("```"):
            flush_paragraph()
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            p = doc.add_paragraph()
            run = p.add_run("\n".join(code))
            run.font.name = "Liberation Mono"
            run.font.size = Pt(8)
            i += 1
            continue
        if line.startswith("::: callout"):
            flush_paragraph()
            m = re.search(r"tone=([a-zA-Z]+)", line)
            t = re.search(r'title="([^"]*)"', line)
            tone = (m.group(1) if m else "info").lower()
            title = t.group(1) if t else ""
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith(":::"):
                body.append(lines[i])
                i += 1
            add_callout(doc, tone, title, body)
            i += 1
            continue
        if line.strip() == "\\pagebreak":
            flush_paragraph()
            doc.add_page_break()
            i += 1
            continue
        if re.match(r"^#{1,3} ", line):
            flush_paragraph()
            level = len(line) - len(line.lstrip("#"))
            title = line[level:].strip()
            doc.add_heading(title, level=min(level, 3))
            if level == 1:
                sections += 1
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-: |]+\|$", lines[i + 1].strip()):
            flush_paragraph()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                raw = lines[i].strip().strip("|")
                cells = [c.strip() for c in raw.split("|")]
                if not re.match(r"^[-: ]+$", "".join(cells)):
                    rows.append(cells)
                i += 1
            add_table(doc, rows)
            tables += 1
            continue
        img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if img:
            flush_paragraph()
            alt, src = img.group(1), img.group(2)
            path = Path(src)
            if not path.is_absolute():
                path = (md_path.parent / path).resolve()
            if path.exists():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(str(path), width=Cm(16.2))
                try:
                    inline = run._r.xpath(".//wp:docPr")[0]
                    inline.set("descr", alt)
                except Exception:
                    pass
                cap = doc.add_paragraph()
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_runs(cap, f"*{alt}*", 9)
                figures += 1
            i += 1
            continue
        if line.startswith("> "):
            flush_paragraph()
            p = doc.add_paragraph(style="Intense Quote")
            add_runs(p, line[2:].strip(), 10)
            i += 1
            continue
        if re.match(r"^\s*[-*] ", line):
            flush_paragraph()
            p = doc.add_paragraph(style="List Bullet")
            add_runs(p, re.sub(r"^\s*[-*] ", "", line))
            i += 1
            continue
        if re.match(r"^\s*\d+\. ", line):
            flush_paragraph()
            p = doc.add_paragraph(style="List Number")
            add_runs(p, re.sub(r"^\s*\d+\. ", "", line))
            i += 1
            continue
        if not line.strip():
            flush_paragraph()
            i += 1
            continue
        paragraph_lines.append(line.strip())
        i += 1
    flush_paragraph()
    doc.core_properties.title = metadata.get("title", "Audit Green IT")
    doc.core_properties.author = ", ".join(metadata.get("authors", []))
    doc.core_properties.subject = metadata.get("subtitle", "Rapport d’audit GreenIT")
    doc.core_properties.keywords = "GreenIT, ACV, RGESN, RNCP39388"
    doc.core_properties.language = "fr-FR"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    result = {"docx": str(out), "sections": sections, "figures": figures, "tables": tables}
    pdf = out.with_suffix(".pdf")
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out.parent), str(out)],
                       check=True, capture_output=True, timeout=180)
        result["pdf"] = str(pdf)
    except Exception as e:
        result["pdf_error"] = str(e)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    out.with_suffix(".json").write_text(payload, encoding="utf-8")
    if out.stem.startswith("rapport"):
        (out.parent / "docx-report.json").write_text(payload, encoding="utf-8")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--metadata", type=Path)
    ap.add_argument("--figures", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--design", type=Path)
    args = ap.parse_args()
    metadata = {}
    if args.metadata and args.metadata.exists():
        import yaml
        metadata = yaml.safe_load(args.metadata.read_text(encoding="utf-8")) or {}
    design_path = args.design or (args.input.parent / "design.yml")
    if design_path.exists():
        apply_theme(theme_from_design(load_design(design_path)))
    result = build(args.input, metadata, args.figures or Path("figures"), args.out)
    print(f"OK DOCX {result['docx']} ({result['sections']} sections, {result['figures']} figures, {result['tables']} tableaux)")
    if "pdf" in result:
        print(f"OK PDF {result['pdf']}")
    elif "pdf_error" in result:
        print(f"AVERTISSEMENT PDF : {result['pdf_error']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
