---
name: docx-report
description: Convertit un rapport Markdown en DOCX stylé puis PDF, avec couverture, sommaire, figures, encadrés, sources et glossaire.
argument-hint: "<report.md> [metadata.yml] [figures/]"
---

# Générer un rapport DOCX et PDF

## Quand l’utiliser

Utiliser ce skill après `/greenit-audit:greenit-report`, quand `report.md`, `metadata.yml` et `figures/` existent. Le DOCX doit rester lisible par un humain, pas seulement valide.

## Commande

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/md_to_docx.py \
  --input /chemin/mon-projet/dist/report.md \
  --metadata /chemin/mon-projet/dist/metadata.yml \
  --figures /chemin/mon-projet/dist/figures \
  --out /chemin/mon-projet/dist/rapport.docx --pdf

# Synthèse client
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/md_to_docx.py" \
  --input /chemin/mon-projet/dist/synthese-client.md \
  --metadata /chemin/mon-projet/dist/metadata.yml \
  --figures /chemin/mon-projet/dist/figures \
  --out /chemin/mon-projet/dist/synthese-client.docx --pdf
```

## Exigences

- A4, marges 2,2 cm, corps 10,5–11 pt, interligne 1,25.
- Couverture générée par Pillow si `cover.png` est absent.
- Sommaire statique + champ TOC OOXML avec `w:updateFields`.
- Figures centrées, légende, texte alternatif dans `docPr.descr`.
- Tableaux avec en-tête vert, lignes alternées et en-tête répété.
- Encadrés `::: callout {tone=info|hypothese|limite|decision title="..."}`.
- Propriétés du document et langue `fr-FR`.
- PDF via `soffice --headless --convert-to pdf`.
- Si `python-docx` manque : échouer clairement, ne pas produire de faux DOCX.

## Vérification

`dist/docx-report.json` contient le nombre de sections, figures et tableaux. `pdfinfo` doit donner au moins 12 pages pour le rapport de démonstration. Ouvrir le PDF et vérifier les marges, les tableaux et les sources.
