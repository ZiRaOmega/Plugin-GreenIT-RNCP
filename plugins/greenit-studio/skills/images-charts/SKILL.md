---
name: images-charts
description: Génère des figures PNG reproductibles pour le rapport et les slides depuis charts.yml, avec source et texte alternatif.
argument-hint: "<charts.yml> [--out figures/]"
---

# Générer des figures

## Quand l’utiliser

Utiliser ce skill pour les graphiques du rapport et du deck. Les figures doivent être compréhensibles sans le texte et citées.

## Commande

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/make_chart.py" \
  --spec /chemin/mon-projet/dist/charts.yml \
  --out /chemin/mon-projet/dist/figures
```

## Types

`bar`, `stacked_bar`, `donut`, `tornado`, `matrix`, `timeline`, `gauge`.

## Règles

- Tri décroissant, labels directs, unités, source en pied de figure.
- Pas de 3D, pas de camembert à plus de 5 catégories.
- Palette daltonienne, contraste, texte ≥ 10 pt.
- PNG 1600×900, optimisation < 300 Ko si possible.
- `figures/manifest.json` et `figures/alt-text.md` générés.
- Chaque figure a un `id`, un `alt` et une `source`.

## Vérification

Ouvrir chaque PNG. Vérifier que la source est lisible, que les labels ne se chevauchent pas et que la figure reste compréhensible en noir et blanc.
