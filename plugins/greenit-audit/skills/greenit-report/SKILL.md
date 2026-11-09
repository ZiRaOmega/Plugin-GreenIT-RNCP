---
name: greenit-report
description: Rédige et structure le rapport d’audit GreenIT en 19 sections, avec style étudiant, sources et limites.
argument-hint: "<dist>"
---

# Rédiger le rapport

## Structure obligatoire (19 sections)

1. Fiche d’identité.
2. Synthèse exécutive.
3. Objectifs et questions.
4. Unité fonctionnelle et scénarios.
5. Méthodologie.
6. Inventaire et facteurs.
7. Résultats par étape de cycle de vie.
8. Résultats par tier.
9. Résultats par fonction.
10. Hotspots.
11. Conditions de validité, sensibilité et plan de consolidation.
12. Diagnostic technique.
13. Benchmark et correspondance normative.
14. Évaluation RGESN.
15. Brainstorm.
16. Plan d’action.
17. Quantification des gains.
18. Bénéfices collatéraux et gouvernance.
19. Conclusion, sources, glossaire, annexes.

## Style étudiant

- « nous », « notre groupe ».
- Phrases courtes, définitions, vulgarisation.
- Encadrés « À retenir », « Notre hypothèse », « Notre limite », « Notre décision ».
- Pas de jargon non défini.
- Pas de fausse précision : arrondir, donner des fourchettes.
- Assumer les données manquantes.
- Citer les sources `[Sxx]` et les hypothèses `Hxx`.
- Exporter le registre `hypotheses.csv` avec statut, owner, échéance et preuve.
- Produire une synthèse client autonome de 4 pages, distincte du rapport complet.

## Génération

Utiliser `scripts/run_audit.py` ou `build_audit_pack.py` si les données sont disponibles, puis `/greenit-studio:docx-report`. Vérifier la grille locale 9+7 dans `references/local/zone01-grading-grid.md`.

## Interdictions

- Pas de « compensation », « neutre en carbone », « 100 % vert » comme revendication.
- Pas de gain non mesuré présenté comme mesuré.
- Pas d’addition de gains qui se recouvrent.
- Pas de conclusion sans limite.
