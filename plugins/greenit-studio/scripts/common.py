"""Constantes et helpers partagés par les scripts studio."""
from __future__ import annotations

import json
from pathlib import Path

THEME = {
    "green_900": "#1E2761",
    "green_800": "#2A3A7A",
    "green_700": "#3B4E9B",
    "green_600": "#5A6FC0",
    "green_500": "#7D8FD6",
    "green_400": "#A9B7E8",
    "green_300": "#CADCFC",
    "green_200": "#E8EEFF",
    "accent": "#C06C4A",
    "alert": "#C1121F",
    "text": "#1F2933",
    "bg": "#F7F4EE",
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


def load_design(path: Path) -> dict:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def theme_from_design(design: dict) -> dict:
    """Fusionne une palette projet dans le thème de rendu."""
    theme = dict(THEME)
    colors = design.get("colors", {}) if isinstance(design, dict) else {}
    for key, value in colors.items():
        if key in theme and isinstance(value, str):
            theme[key] = value
    return theme
