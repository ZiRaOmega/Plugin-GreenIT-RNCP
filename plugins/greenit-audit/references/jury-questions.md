# Questions de jury RNCP39388 — 40 questions

1. **Pourquoi avoir choisi l’ACV plutôt qu’un simple bilan carbone ?** L’ACV couvre plusieurs indicateurs et tout le cycle de vie ; le bilan carbone est mono-indicateur et organisationnel.
2. **Quelle est votre unité fonctionnelle ?** Une semaine d’émargement pour 100 étudiants et 1 staff, avec un niveau de disponibilité défini.
3. **Quelles sont les frontières de votre étude ?** Terminaux, réseau, serveur, développement, maintenance, fin de vie documentée.
4. **Qu’avez-vous exclu ?** Bâtiments, impacts sociaux, effets rebond, réseau inactif ; ces exclusions sont explicitées.
5. **Pourquoi la fabrication domine-t-elle ?** Les équipements ont une forte intensité matière et énergie incorporée, répartie sur la durée de vie.
6. **Comment avez-vous alloué le serveur ?** Au prorata des ressources ou du temps du service, avec une sensibilité.
7. **Comment avez-vous traité les terminaux partagés ?** Allocation au temps d’usage, plus un scénario « terminal dédié ».
8. **Quelle incertitude ?** ±20 à ±30 % sur les facteurs dominants, avec scénarios bas/base/haut.
9. **Pourquoi le réseau est-il faible ?** Peu de données transférées et facteur par Go ; ce n’est pas une généralité.
10. **Pourquoi le développement pèse-t-il ?** 3 développeurs × 30 h, avec un facteur laptop incluant fabrication et usage.
11. **Qu’est-ce que l’ADPe ?** Épuisement des ressources minérales, en kg Sb eq.
12. **Qu’est-ce que l’ADPf ?** Épuisement des ressources fossiles, en MJ.
13. **Pourquoi ne pas additionner ADPe et ADPf ?** Ce sont des indicateurs et des unités différents.
14. **Qu’est-ce que le PUE ?** Énergie totale du datacenter / énergie IT.
15. **Pourquoi PUE 1,5 ?** Hypothèse de datacenter mutualisé ; à remplacer par la valeur de l’hébergeur.
16. **Quelle différence entre PE et EF ?** PE = énergie primaire, EF = énergie finale.
17. **Pourquoi EcoIndex ne suffit-il pas ?** Il ne couvre que le web, trois métriques, et ne fait pas l’ACV.
18. **Qu’est-ce que la SCI ?** Un taux d’émission par unité fonctionnelle.
19. **Comment avez-vous évité le greenwashing ?** Sources, fourchettes, limites, pas de compensation, pas de « neutre ».
20. **Quel est le principal hotspot ?** Le serveur et le développement dans notre scénario ; les terminaux augmentent si dédiés.
21. **Quelle action a le meilleur rapport impact/effort ?** Cache/compression, suppression du polling, images optimisées, index SQL.
22. **Quel gain avez-vous mesuré ?** Voir `metrics.json` et le delta avant/après ; ne pas additionner les gains qui se recouvrent.
23. **Comment vérifiez-vous l’additivité ?** Chaque action est recalculée avec la même UF et la même frontière ; les recouvrements sont signalés.
24. **Quel est l’effet rebond ?** Une page plus légère peut être consultée plus souvent ; à surveiller par les usages.
25. **Comment avez-vous sécurisé le service ?** Revue OWASP, moindre privilège, secrets hors code, en-têtes, sauvegardes.
26. **Comment avez-vous pris en compte le RGPD ?** Minimisation, durée de conservation, base légale, droits.
27. **Comment avez-vous pris en compte l’accessibilité ?** RGAA, contrastes, labels, navigation clavier, alternatives.
28. **Quelle est votre stratégie de mesure énergétique ?** Supervision, PUE/WUE, mesures avant/après, incertitude.
29. **Comment avez-vous formé les équipes ?** Module de 10 slides, quiz, exercice pratique.
30. **Comment avez-vous piloté le projet ?** Plan, RACI, risques, jalons, revue de conformité.
31. **Quelle a été votre plus grande difficulté ?** Données serveur/hébergeur manquantes ; hypothèses et sensibilité.
32. **Qu’est-ce que vous feriez différemment ?** Mesurer plus tôt, obtenir les factures et le PUE réel, impliquer l’hébergeur.
33. **Pourquoi 78 critères RGESN ?** Version 2024, 9 chapitres, extraction de l’outil officiel.
34. **Pourquoi GR491 en plus ?** Vision cycle de vie et recommandations complémentaires.
35. **Pourquoi RWEB ?** Bonnes pratiques web concrètes.
36. **Quelle différence entre RGESN et RWEB ?** RGESN réglementaire français ; RWEB communautaire web.
37. **Comment avez-vous calculé le score RGESN ?** Poids officiels, statuts, couverture ; ce n’est pas le score officiel.
38. **Que signifie une couverture de 40 % ?** Le score n’est pas significatif ; il faut évaluer davantage.
39. **Quelle est la limite de votre audit ?** Screening, pas ACV avec revue critique, pas audit certifié.
40. **Quelle est votre recommandation prioritaire ?** Réduire le poste dominant, mesurer, puis itérer ; ne pas acheter de compensation.
