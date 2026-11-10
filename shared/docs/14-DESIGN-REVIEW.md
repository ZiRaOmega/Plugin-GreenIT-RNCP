# Revue design et qualité

Plugin `greenit-reviewer` :

- `design-review` : PDF/PPTX, chevauchements, marges, polices, palette, glossaire, données, graphiques, RNCP.
- `sanitize-ai-text` : caractères et formulations IA.
- `content-challenge` : agent indépendant `independent-challenger`.
- `discover-palette` : extraction CSS/tokens/logo de la palette du projet.

## Commandes

```bash
python3 plugins/greenit-studio/scripts/extract_project_palette.py \
  --project examples/demo-service --out dist/design.yml
```

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

## Direction artistique du projet

`extract_project_palette.py` lit les variables CSS du projet, ses couleurs hexadécimales, ses tokens et son logo. Il écrit `design.yml` avec `source` et `confidence`. Les renderers chargent ce fichier : la palette du rapport et du deck est donc celle du projet, pas un thème générique.

Si le projet est vert, le rendu est vert. Le reviewer vérifie la cohérence avec `design.yml`, pas une interdiction universelle du vert.

## Blocs RNCP

Le reviewer accepte `--blocks BC01,BC04` et vérifie que les compétences des blocs non sélectionnés sont marquées `hors périmètre`.

## Filtrage des preuves par bloc

Le reviewer ignore les lignes `hors périmètre` dans le contrôle d’existence des preuves. Un audit BC01/BC04 ne signale donc pas les preuves manquantes de BC02/BC03, et inversement.

## Limites de couverture

- PDF : revue textuelle et marges, pas de rasterisation systématique.
- PPTX : revue structurelle, pas de rendu visuel exhaustif.
- RNCP : contrôle de complétude et d’existence des preuves, pas de jugement de qualité.
- Le challenge indépendant est un complément, pas une preuve automatique.

## Blocs 1 et 4 — dossier d’examen

Quand `--blocks BC01,BC04` est utilisé, le pack ajoute :

- `11-dossier-examen-bc01-bc04.md` : 9 parties, 16 compétences C1.1–C1.8 et C4.1–C4.8 ;
- `12-matrice-16-competences.csv` : correspondance partie / compétence / preuve / statut.

La correspondance C1.x/C4.x → RNCP39388 est indicative : vérifier le référentiel de l’école.
