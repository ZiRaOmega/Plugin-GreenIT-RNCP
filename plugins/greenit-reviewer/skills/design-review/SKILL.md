---
name: design-review
description: Audite les PDF et PPTX d’un audit GreenIT : chevauchements, marges, typographie, palette projet, caractères IA, glossaire, données, graphiques et preuves RNCP39388.
argument-hint: "<dist> [--report pdf] [--deck pptx]"
disable-model-invocation: true
---

# Revue design et qualité des livrables

## Question obligatoire

Demander quels blocs RNCP ont été audités (`BC01,BC04`, `BC02,BC03`, etc.) avant de vérifier la matrice et le dossier de preuves.

## Quand l’utiliser

Après la génération du rapport PDF, de la soutenance PPTX et des figures. Cette revue est indépendante : elle ne modifie pas les livrables, elle produit un rapport de constats.

## Commande

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/review_deliverables.py" \
  --root /chemin/mon-projet/dist \
  --out /chemin/mon-projet/dist/review-report.json
```

Le script détecte automatiquement :

- `rapport*.pdf` ou `rapport.pdf` ;
- `soutenance*.pptx` ou `soutenance.pptx` ;
- `metrics.json` ;
- `rgesn-score.csv` ;
- `charts.yml` ;
- `rncp39388/01-matrice-competences.csv`.

## Contrôles

- PPTX : texte hors slide, chevauchement de zones de texte, polices < 8 pt, nombre de slides, notes, sources, caractères IA.
- PDF : pages, sections obligatoires, mots hors marges, caractères IA.
- Données : totaux GWP/ADPe/ADPf, parts par tier = 100 ± 0,1, facteurs et sources, indicateurs réseau.
- RGESN : 78 critères, aucun statut non évalué, `evidence_status` présent.
- Graphiques : `id`, `title`, `source`, `alt`, `purpose`, image non vide, dimensions, légende pour les multi-séries.
- RNCP : 19 compétences, 4 blocs, preuves existantes, dossier de preuves.
- Glossaire : termes obligatoires présents.

## Sorties

- `dist/review-report.json` ;
- `dist/review-report.md`.

## Règles

- Un `blocker` bloque la livraison.
- Un `major` doit être corrigé ou justifié.
- Un `minor` peut être accepté avec justification.
- Ne pas modifier les livrables dans ce skill ; utiliser `/greenit-reviewer:sanitize-ai-text` pour les caractères IA.
- Ne pas confondre « non validé faute de preuve » et « non évalué ».
