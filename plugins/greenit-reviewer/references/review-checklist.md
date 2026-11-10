# Checklist de revue

## PPTX

- [ ] 12–15 slides, notes présentes
- [ ] aucun texte hors slide
- [ ] aucun chevauchement de textes
- [ ] tailles de police conformes
- [ ] sources en pied de page
- [ ] palette projet respectée
- [ ] pas de vert générique non justifié
- [ ] pas de caractères IA

## PDF

- [ ] pages > 12 pour le rapport
- [ ] texte dans les marges
- [ ] sections obligatoires
- [ ] sources, glossaire, note de calcul
- [ ] pas de caractères IA

## Données

- [ ] GWP/ADPe/ADPf > 0 et unités
- [ ] parts par tier = 100 ± 0,1
- [ ] 78 critères RGESN, aucun « à évaluer »
- [ ] preuves et statuts séparés
- [ ] hypothèses avec statut et preuve
- [ ] sources `[Sxx]` valides

## Graphiques

- [ ] titre, source, alt, objectif, légende
- [ ] image non vide, dimensions correctes
- [ ] pas de 3D, pas de camembert > 5 parts
- [ ] lisible en noir et blanc

## RNCP

- [ ] 19 compétences, 4 blocs
- [ ] chaque preuve existe
- [ ] dossier de preuves complet
- [ ] formation avec quiz et exercice
- [ ] challenge indépendant effectué

## Limites de couverture

- La revue PDF est textuelle (pypdf + pdftotext -bbox) : elle ne rasterise pas les pages et ne détecte pas un chevauchement purement visuel dans le PDF.
- La revue PPTX est structurelle : positions, tailles, couleurs, notes. Elle ne remplace pas une inspection visuelle humaine.
- `review_rncp` vérifie 19 lignes, 4 blocs, l’existence des fichiers et la présence des IDs ; il ne juge pas la qualité ou la circularité d’une preuve.
- `review_palette` compare le PPTX à `design.yml` ; il ne prouve pas que `design.yml` est la seule palette du projet.
- Le challenge indépendant doit être exécuté séparément ; s’il n’a pas lu les fichiers réels, le dire explicitement.
