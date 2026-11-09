#!/usr/bin/env python3
"""Génère des figures reproductibles depuis charts.yml."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
from common import THEME, hex_to_rgb  # noqa: E402

GREEN = THEME["green_900"]
MUTED = THEME["muted"]
ACCENT = THEME["accent"]
ALERT = THEME["alert"]


def style(ax, title: str, subtitle: str, source: str) -> None:
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", color=GREEN, pad=18)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9, color=MUTED)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    if source:
        ax.figure.text(0.01, 0.01, source, fontsize=7, color=MUTED)


def bar(spec: dict, out: Path) -> None:
    data = spec.get("data", [])
    labels = [str(d["label"]) for d in data]
    values = [float(d["value"]) for d in data]
    colors = [spec.get("color", THEME["green_700"])] * len(values)
    if spec.get("highlight"):
        colors = [ACCENT if str(d["label"]) in spec["highlight"] else c for d, c in zip(data, colors)]
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
    if spec.get("orientation") == "horizontal":
        ax.barh(labels, values, color=colors)
        ax.invert_yaxis()
        ax.grid(axis="x", color="#D9D9D9", linewidth=0.6)
        ax.grid(axis="y", visible=False)
        for i, v in enumerate(values):
            ax.text(v, i, f" {v:.3g}", va="center", fontsize=8, color=GREEN)
    else:
        ax.bar(labels, values, color=colors)
        for i, v in enumerate(values):
            ax.text(i, v, f"{v:.3g}", ha="center", va="bottom", fontsize=8, color=GREEN)
        plt.xticks(rotation=25, ha="right")
    ax.set_ylabel(spec.get("unit", ""))
    style(ax, spec.get("title", ""), spec.get("subtitle", ""), spec.get("source", ""))
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pil_kwargs={"optimize": True})
    plt.close(fig)


def stacked_bar(spec: dict, out: Path) -> None:
    data = spec.get("data", [])
    series = spec.get("series", [])
    labels = [str(d["label"]) for d in data]
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
    bottom = [0.0] * len(data)
    palette = [THEME["green_900"], THEME["green_600"], THEME["green_300"], ACCENT, ALERT]
    for idx, name in enumerate(series):
        vals = [float(d.get("values", {}).get(name, 0)) for d in data]
        ax.bar(labels, vals, bottom=bottom, label=name, color=palette[idx % len(palette)])
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.legend(frameon=False, fontsize=8, ncol=min(3, len(series)))
    ax.set_ylabel(spec.get("unit", ""))
    style(ax, spec.get("title", ""), spec.get("subtitle", ""), spec.get("source", ""))
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pil_kwargs={"optimize": True})
    plt.close(fig)


def donut(spec: dict, out: Path) -> None:
    data = spec.get("data", [])
    labels = [str(d["label"]) for d in data]
    values = [float(d["value"]) for d in data]
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=200)
    colors = [THEME["green_900"], THEME["green_700"], THEME["green_500"], THEME["green_300"], ACCENT, ALERT]
    wedges, _ = ax.pie(values, colors=colors[:len(values)], startangle=90, counterclock=False,
                       wedgeprops={"width": 0.38, "edgecolor": "white"})
    ax.legend(wedges, [f"{l} — {v:.3g}" for l, v in zip(labels, values)], loc="center left",
              bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=8)
    ax.text(0, 0, spec.get("center", ""), ha="center", va="center", fontsize=12, color=GREEN, fontweight="bold")
    style(ax, spec.get("title", ""), spec.get("subtitle", ""), spec.get("source", ""))
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pil_kwargs={"optimize": True})
    plt.close(fig)


def tornado(spec: dict, out: Path) -> None:
    data = spec.get("data", [])
    labels = [str(d["label"]) for d in data]
    low = [float(d["low"]) for d in data]
    high = [float(d["high"]) for d in data]
    base = [float(d.get("base", 0)) for d in data]
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
    y = range(len(labels))
    ax.barh(y, [b - l for b, l in zip(base, low)], left=low, color=THEME["green_300"], label="Bas")
    ax.barh(y, [h - b for b, h in zip(base, high)], left=base, color=THEME["green_700"], label="Haut")
    ax.set_yticks(list(y), labels)
    ax.invert_yaxis()
    ax.legend(frameon=False, fontsize=8)
    style(ax, spec.get("title", ""), spec.get("subtitle", ""), spec.get("source", ""))
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pil_kwargs={"optimize": True})
    plt.close(fig)


def matrix(spec: dict, out: Path) -> None:
    data = spec.get("data", [])
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
    ax.axhline(0.5, color="#CCCCCC", linewidth=0.8)
    ax.axvline(0.5, color="#CCCCCC", linewidth=0.8)
    ax.add_patch(Rectangle((0, 0.5), 0.5, 0.5, color=THEME["green_200"], alpha=0.5))
    ax.text(0.25, 0.93, "Quick wins", ha="center", fontsize=9, color=GREEN)
    ax.text(0.75, 0.93, "Projets structurants", ha="center", fontsize=9, color=GREEN)
    ax.text(0.25, 0.06, "À éviter", ha="center", fontsize=9, color=MUTED)
    ax.text(0.75, 0.06, "À planifier", ha="center", fontsize=9, color=MUTED)
    for d in data:
        ax.scatter(float(d["effort"]), float(d["impact"]), s=80, color=ACCENT, edgecolor=GREEN, zorder=3)
        ax.annotate(str(d["label"]), (float(d["effort"]), float(d["impact"])), xytext=(5, 4),
                    textcoords="offset points", fontsize=7, color=GREEN)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Effort (faible → fort)")
    ax.set_ylabel("Impact (faible → fort)")
    style(ax, spec.get("title", ""), spec.get("subtitle", ""), spec.get("source", ""))
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pil_kwargs={"optimize": True})
    plt.close(fig)


def timeline(spec: dict, out: Path) -> None:
    data = spec.get("data", [])
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
    labels = [str(d["label"]) for d in data]
    for i, d in enumerate(data):
        start, end = float(d.get("start", 0)), float(d.get("end", 1))
        ax.barh(i, end - start, left=start, color=THEME["green_600"] if i % 2 == 0 else THEME["green_900"], height=0.5)
        ax.text(end + 0.05, i, str(d.get("note", "")), va="center", fontsize=8, color=GREEN)
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_xlabel(spec.get("unit", "semaines"))
    style(ax, spec.get("title", ""), spec.get("subtitle", ""), spec.get("source", ""))
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pil_kwargs={"optimize": True})
    plt.close(fig)


def gauge(spec: dict, out: Path) -> None:
    value = float(spec.get("value", 0))
    fig, ax = plt.subplots(figsize=(5, 3.2), dpi=200)
    ax.barh([0], [100], color="#E5E7EB", height=0.35)
    ax.barh([0], [value], color=THEME["green_700"], height=0.35)
    ax.text(value / 2, 0, f"{value:.0f}/100", ha="center", va="center", color="white", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel(spec.get("unit", "score"))
    style(ax, spec.get("title", ""), spec.get("subtitle", ""), spec.get("source", ""))
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pil_kwargs={"optimize": True})
    plt.close(fig)


BUILDERS = {"bar": bar, "stacked_bar": stacked_bar, "donut": donut, "tornado": tornado,
            "matrix": matrix, "timeline": timeline, "gauge": gauge}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    import yaml
    specs = yaml.safe_load(args.spec.read_text(encoding="utf-8"))
    charts = specs.get("charts", specs if isinstance(specs, list) else [])
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for spec in charts:
        kind = spec.get("type")
        if kind not in BUILDERS:
            raise ValueError(f"Type de figure inconnu : {kind}")
        path = args.out / f"{spec['id']}.png"
        BUILDERS[kind](spec, path)
        manifest.append({"id": spec["id"], "path": str(path), "alt": spec.get("alt", spec.get("title", "")),
                         "source": spec.get("source", ""), "bytes": path.stat().st_size})
    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    alts = ["# Textes alternatifs", ""] + [f"- **{m['id']}** : {m['alt']}" for m in manifest]
    (args.out / "alt-text.md").write_text("\n".join(alts) + "\n", encoding="utf-8")
    print(f"OK {len(manifest)} figures -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
