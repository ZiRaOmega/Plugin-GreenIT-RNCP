"""Constantes et helpers partagés par les scripts studio."""
from __future__ import annotations

import json
from pathlib import Path

THEME = {
    "green_900": "#1B4332",
    "green_800": "#2D6A4F",
    "green_700": "#40916C",
    "green_600": "#52B788",
    "green_500": "#74C69D",
    "green_400": "#95D5B2",
    "green_300": "#B7E4C7",
    "green_200": "#D8F3DC",
    "accent": "#E9C46A",
    "alert": "#C1121F",
    "text": "#1F2933",
    "bg": "#F7F5EF",
    "muted": "#5C6B73",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def fmt(value: float, digits: int = 3) -> str:
    if value is None:
        return "—"
    if abs(value) >= 1000:
        return f"{value:,.0f}".replace(",", " ")
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.{digits}g}"
