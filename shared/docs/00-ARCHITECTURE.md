# Architecture du bundle

```text
Utilisateur
  → greenit-audit (orchestrateur)
      → greenit-studio (DOCX, PPTX, vidéo, figures, analyse codebase)
      → greenit-engineering (refactor, fix, brainstorm, benchmark, revue)
      → références et scripts de calcul
  → dist/ (livrables)
```

## Dépendances

`greenit-audit` dépend de `greenit-studio` et `greenit-engineering`. Les deux autres plugins sont autonomes. Installer `greenit-audit` installe tout le bundle ; installer `greenit-engineering` seul reste possible.

## Flux de données

1. `audit.yml` : unité fonctionnelle, périmètre, inventaire, hypothèses.
2. `codebase-audit.json` : signaux statiques.
3. `web-metrics.json` : DOM, requêtes, octets, cache, EcoIndex.
4. `metrics.json` : GWP, ADPe, ADPf, parts, hotspots, incertitude.
5. `rgesn-score.csv` : 78 critères.
6. `hypotheses.csv` : registre des hypothèses, statuts, owners et preuves.
7. `report.md` → DOCX/PDF.
7bis. `synthese-client.md` → DOCX/PDF client 2–4 pages.
7. `deck.yml` → PPTX/PDF + notes.
8. `narration.md` → MP4 + SRT.
9. `rncp39388/` : matrice, preuves, plan projet, formation, rétrospective.

## Contrats

- Aucun chiffre sans source.
- Aucune hypothèse sans ID.
- Aucun terme non défini.
- Les scripts sont locaux, sans exfiltration.
- `factors.local.example.csv` ne contient que l’en-tête. La démonstration utilise `factors.local.csv`, ignoré par Git et à fournir sous licence pour GWP/ADPe/ADPf réseau.
