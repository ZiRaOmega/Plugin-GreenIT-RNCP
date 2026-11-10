# Changelog

## 0.1.2 — 2026-11-09

- Tri-état des indicateurs : une valeur absente n’est jamais un zéro.
- Réseau ADPe/ADPf évalué dans la démo avec le facteur local NegaOctet.
- Tous les critères RGESN applicables ont un statut ; absence de preuve = non validé.
- Suppression du statut « à évaluer » du schéma et du parcours utilisateur.
- Score RGESN recalculé : 15,0/100, couverture 100 %.
- Version moteur `0.1.2`.

## 0.1.1 — 2026-11-09

- H7 corrigée : volumes réseau dérivés de la page réellement mesurée (1 595 Ko).
- Facteur réseau ouvert Green Coding (0,04106063 kWh/Go) à la place de NegaOctet dans la démo.
- 42 sources.
- Registre d’hypothèses avec statut, owner, échéance et preuve (`hypotheses.csv`).
- Scénarios de sensibilité PUE, allocation, développement, usage, mix, réseau, terminaux dédiés.
- Section 11 renommée « Conditions de validité, sensibilité et plan de consolidation ».
- Synthèse client autonome DOCX/PDF (4 pages).
- Playbook de collecte de données légitime.
- Tests et contrôles mis à jour.

## 0.1.0 — 2026-11-09

- Création du marketplace `greenit-rncp39388`.
- Trois plugins : `greenit-studio`, `greenit-audit`, `greenit-engineering`.
- 18 skills, puis 22 avec le plugin reviewer (4 skills + 1 agent).
- Import RGESN 2024 : 78 critères, 9 chapitres.
- Références GR491, RWEB, ACV, indicateurs, réglementation.
- 41 sources.
- Moteur de calcul GWP/ADPe/ADPf, EcoIndex, SCI.
- Démonstration service d’émargement, avant/après.
- Rapport DOCX/PDF, soutenance PPTX/PDF, vidéo MP4.
- Dossier RNCP39388 : matrice 19 compétences, preuves, charte, plan de mesure, plan projet, formation, rétrospective.
- Tests unitaires et contrôles de sortie.
