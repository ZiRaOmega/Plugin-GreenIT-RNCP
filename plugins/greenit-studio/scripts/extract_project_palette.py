#!/usr/bin/env python3
"""Découvre la palette du projet audité (CSS, tokens, Tailwind, logo) et écrit design.yml."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import yaml
from PIL import Image

SKIP = {".git", "node_modules", ".venv", "dist", "build", "vendor", "__pycache__", ".next", "coverage"}
HEX_RE = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
VAR_RE = re.compile(r"--([a-zA-Z0-9_-]+)\s*:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})\b")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}{]+)")
ROLE_WORDS = {
    "primary": ["primary", "brand", "main", "green", "blue", "navy", "accent"],
    "background": ["bg", "background", "surface", "paper"],
    "text": ["text", "ink", "foreground", "body"],
    "accent": ["accent", "secondary", "highlight", "gold", "orange", "terracotta"],
    "muted": ["muted", "subtle", "gray", "grey"],
    "alert": ["alert", "danger", "error", "red"],
}


def norm_hex(h: str) -> str:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h.upper()


def rgb(h: str) -> tuple[int, int, int]:
    h = norm_hex(h)[1:]
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    ra, rb = rgb(a), rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ra, rb))


def luminance(h: str) -> float:
    r, g, b = [c / 255 for c in rgb(h)]
    vals = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def is_neutral(h: str) -> bool:
    r, g, b = rgb(h)
    return max(r, g, b) - min(r, g, b) < 12


def collect(project: Path) -> tuple[dict, Counter, list[str], str]:
    named: dict[str, str] = {}
    freq: Counter = Counter()
    fonts: list[str] = []
    source = "fallback"
    for p in project.rglob("*"):
        if not p.is_file() or any(part in SKIP for part in p.parts):
            continue
        if p.suffix.lower() not in {".css", ".scss", ".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".json", ".yml", ".yaml"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in VAR_RE.finditer(text):
            name, val = m.group(1).lower(), norm_hex(m.group(2))
            named.setdefault(name, val)
            freq[val] += 1
            source = "css"
        for m in HEX_RE.finditer(text):
            freq[norm_hex(m.group(0))] += 1
            source = "css" if source == "fallback" else source
        for m in FONT_RE.finditer(text):
            f = m.group(1).split(",")[0].strip().strip('"\'')
            if f and f not in fonts:
                fonts.append(f)
    # logo dominant colors
    for pattern in ("logo*.png", "logo*.jpg", "logo*.jpeg", "favicon*.png"):
        for p in project.glob(pattern):
            try:
                im = Image.open(p).convert("RGB").resize((80, 80))
                for count, color in im.getcolors(80 * 80) or []:
                    h = "#" + "".join(f"{c:02X}" for c in color)
                    if not is_neutral(h) and luminance(h) < 0.85:
                        freq[h] += count
                source = "logo" if source == "fallback" else source
            except Exception:
                pass
    return named, freq, fonts, source


def pick(named: dict, freq: Counter) -> tuple[dict, list[str]]:
    warnings: list[str] = []
    def named_for(role: str) -> str | None:
        for word in ROLE_WORDS[role]:
            for k, v in named.items():
                if word in k:
                    return v
        return None

    primary = named_for("primary")
    if not primary:
        candidates = [h for h, _ in freq.most_common() if not is_neutral(h) and luminance(h) < 0.75]
        primary = candidates[0] if candidates else "#1F3A5F"
        warnings.append("Aucune variable CSS primaire ; couleur dominante utilisée.")
    background = named_for("background") or "#F7F4EE"
    text = named_for("text") or "#1F2933"
    secondary = named_for("accent") or mix(primary, "#FFFFFF", 0.25)
    accent = named_for("accent") or secondary
    muted = named_for("muted") or mix(text, background, 0.45)
    alert = named_for("alert") or "#C1121F"
    light = named.get("light") or mix(primary, "#FFFFFF", 0.88)
    if contrast(text, background) < 4.5:
        warnings.append("Contraste texte/fond inférieur à 4.5:1.")
    if contrast(primary, background) < 3:
        warnings.append("Contraste primaire/fond inférieur à 3:1.")
    colors = {
        "primary": primary, "secondary": secondary, "accent": accent,
        "background": background, "text": text, "muted": muted, "alert": alert,
        "green_900": primary, "green_800": mix(primary, "#000000", 0.15),
        "green_700": secondary, "green_600": mix(primary, "#FFFFFF", 0.30),
        "green_500": mix(primary, "#FFFFFF", 0.45), "green_400": mix(primary, "#FFFFFF", 0.60),
        "green_300": mix(primary, "#FFFFFF", 0.75), "green_200": light,
        "bg": background, "text": text, "muted": muted, "accent": accent, "alert": alert,
    }
    return colors, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    project = args.project.resolve()
    named, freq, fonts, source = collect(project)
    colors, warnings = pick(named, freq)
    design = {
        "project": project.name,
        "source": source,
        "confidence": "high" if source == "css" and named else ("medium" if source in {"css", "logo"} else "low"),
        "colors": colors,
        "fonts": {"body": fonts[0] if fonts else "Liberation Sans", "mono": "Liberation Mono"},
        "warnings": warnings,
        "rules": ["palette extraite du projet", "source sur chaque figure", "pas de 3D"],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(yaml.safe_dump(design, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"OK palette {source} ({design['confidence']}) -> {args.out}")
    for k in ("primary", "secondary", "accent", "background", "text"):
        print(f"  {k}: {colors[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
