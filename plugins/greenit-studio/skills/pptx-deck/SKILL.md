---
name: pptx-deck
description: Génère un diaporama PPTX 16:9 depuis deck.yml, avec notes orales, pieds de page source et export PDF.
argument-hint: "<deck.yml> [--out dist/soutenance.pptx]"
---

# Générer une soutenance PPTX

## Quand l’utiliser

Utiliser ce skill après `/greenit-audit:greenit-defense`. Le deck doit tenir en 12–15 slides pour 15 minutes, avec une idée par slide.

## Commande

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_deck.py \
  --input /chemin/mon-projet/dist/deck.yml \
  --out /chemin/mon-projet/dist/soutenance.pptx \
  --notes /chemin/mon-projet/dist/notes-orales.md --pdf
```

## Layouts

`title`, `section`, `bullets`, `metrics`, `chart`, `image`, `matrix`, `timeline`, `quote`, `closing`.

## Exigences

- 16:9, palette `assets/theme.json`, police `Liberation Sans`.
- 3 puces maximum, 1 visuel, titre-message.
- Notes de 60–90 s par slide ; total 1800–2200 mots pour 15 slides.
- Pied de page source sur chaque slide de données.
- Numéro de slide.
- Avertir si plus de 6 puces, plus de 90 caractères par puce ou plus de 15 slides.
- Export PDF via LibreOffice.
- `deck-report.json` contient le nombre de slides et de mots.

## Vérification

Ouvrir le PDF : aucune slide ne doit être surchargée. Vérifier que les notes sont présentes dans le PPTX et que `notes-orales-demo.md` respecte le minutage.
