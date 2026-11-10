#!/usr/bin/env python3
"""Détecte et remplace les caractères typographiques typiques des textes générés par IA.

Le nettoyage conserve les accents français et ne touche pas au code source.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

CHAR_MAP = {
    "\u2014": "-", "\u2013": "-", "\u2012": "-", "\u2015": "-",
    "\u201c": '"', "\u201d": '"', "\u201e": '"',
    "\u2026": "...", "\u00a0": " ", "\u202f": " ",
    "\u2009": " ", "\u200a": " ", "\u200b": "", "\ufeff": "",
    "\u2022": "-", "\u25cf": "-", "\u25aa": "-", "\u25a0": "-",
    "\u2192": "->", "\u21d2": "=>", "\u2190": "<-",
    "\u2705": "[OK]", "\u2714": "[OK]", "\u2716": "[X]",
    "\u274c": "[X]", "\u26a0": "[!]", "\u26a0\ufe0f": "[!]",
}
EMOJI_RE = re.compile(
    "[" 
    "\U0001F300-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "]+"
)
AI_PHRASES = [
    (r"\bEn tant que modèle(?: de langage)?\b[^.]*\.?", ""),
    (r"\bIl est important de noter que\b", ""),
    (r"\bDans le monde (?:complexe |passionnant )?de\b", "Dans"),
    (r"\bplongeons dans\b", "examinons"),
    (r"\bn['’]hésitez pas à\b", ""),
    (r"\brévolutionnaire\b", "important"),
    (r"\bgame[- ]changer\b", "changement important"),
]


def find_ai_chars(text: str) -> list[dict]:
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for col, ch in enumerate(line, start=1):
            if ch in CHAR_MAP:
                hits.append({"line": lineno, "column": col, "char": ch,
                             "codepoint": f"U+{ord(ch):04X}",
                             "replacement": CHAR_MAP[ch]})
        for m in EMOJI_RE.finditer(line):
            hits.append({"line": lineno, "column": m.start() + 1, "char": m.group(0),
                         "codepoint": "emoji", "replacement": ""})
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pat, _ in AI_PHRASES:
            if re.search(pat, line, flags=re.I):
                hits.append({"line": lineno, "column": 1, "char": "phrase IA",
                             "codepoint": "phrase", "replacement": pat})
    return hits


def sanitize(text: str) -> str:
    for src, dst in CHAR_MAP.items():
        text = text.replace(src, dst)
    text = EMOJI_RE.sub("", text)
    for pat, repl in AI_PHRASES:
        text = re.sub(pat, repl, text, flags=re.I)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\b(de|le|la|les|des|du)\s{2,}", r"\1 ", text)
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = []
    for path in args.paths:
        text = path.read_text(encoding="utf-8")
        hits = find_ai_chars(text)
        report.append({"path": str(path), "hits": hits, "count": len(hits)})
        if args.apply and hits:
            cleaned = sanitize(text)
            path.write_text(cleaned, encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for row in report:
            print(f"{row['path']}: {row['count']} caractère(s)/phrase(s) IA")
    return 1 if any(r["count"] for r in report) and not args.apply else 0


if __name__ == "__main__":
    raise SystemExit(main())
