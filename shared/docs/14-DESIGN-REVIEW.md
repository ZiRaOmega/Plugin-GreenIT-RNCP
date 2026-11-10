# Revue design et qualité

Plugin `greenit-reviewer` :

- `design-review` : PDF/PPTX, chevauchements, marges, polices, palette, glossaire, données, graphiques, RNCP.
- `sanitize-ai-text` : caractères et formulations IA.
- `content-challenge` : agent indépendant `independent-challenger`.

## Commandes

```bash
python3 plugins/greenit-reviewer/scripts/review_deliverables.py \
  --root dist --out dist/review-report.json

python3 plugins/greenit-reviewer/scripts/sanitize_ai_text.py \
  dist/audit-demo/report.md dist/notes-orales-demo.md --apply
```

Le rapport de revue contient `review-report.md` et `review-report.json`.

## Règles

- `blocker` : correction obligatoire.
- `major` : correction ou justification.
- `minor` : amélioration.
- Un graphique doit avoir `title`, `source`, `alt`, `purpose` et une légende si multi-séries.
- La palette doit être celle du projet ; le vert générique doit être justifié.
- Chaque bloc RNCP doit avoir une preuve existante.
- L’agent indépendant ne modifie rien.
