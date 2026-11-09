# 1. Fiche d’identité du projet

**Projet** : Service d’émargement Zone01 — démonstration  
**Client** : Zone01 Normandie (cas pédagogique)  
**Version** : 1.0 — **Date** : 2026-11-09  
**Auteurs** : Équipe GreenIT RNCP39388

Nous avons audité un service fictif d’émargement utilisé par 100 étudiants et un membre du staff pendant une semaine. Le service est volontairement perfectible : image PNG lourde, CSS dupliqué, JavaScript non minifié, polling, `SELECT *`, absence d’index et `alt` manquant. Notre objectif est de montrer une démarche complète, traçable et honnête, pas de certifier un service réel.

::: callout {tone=info title="À retenir"}
Le cas est une **ACV screening**. Les chiffres servent à prioriser et à apprendre ; ils ne remplacent pas une ACV avec revue critique ni un audit RGESN officiel.
:::

# 2. Synthèse exécutive

Trois chiffres suffisent à raconter l’essentiel :

- **1.76 kg CO2e** pour une semaine d’émargement, soit environ **17.6 g CO2e par étudiant**.
- **63.6 %** du GWP vient du serveur mutualisé ; **32.4 %** vient du développement.
- **100.0 %** des critères RGESN ont un statut, mais **39.6 %** seulement ont une preuve : le score de **15.0/100** est donc **non significatif**.

::: callout {tone=decision title="Notre décision"}
Nous priorisons d’abord la mesure du serveur et de l’hébergement, puis les quick wins web. Optimiser le frontend est utile, mais ne doit pas masquer le poste serveur, qui domine dans notre scénario.
:::

# 3. Objectifs et questions d’audit

Nos questions étaient les suivantes :

1. Quels sont les postes qui contribuent le plus au GWP, à l’ADPe et à l’ADPf ?
2. Les terminaux sont-ils un hotspot dans un usage partagé ? Que se passe-t-il s’ils sont dédiés ?
3. Les optimisations web réduisent-elles le poids, les requêtes et l’EcoIndex ?
4. Le service respecte-t-il les grands principes RGESN, GR491 et RWEB ?
5. Quelles actions sont réalistes dans le temps et le budget d’une équipe pédagogique ?
6. Quelles preuves pouvons-nous fournir pour le RNCP39388 ?

# 4. Unité fonctionnelle et scénarios

**Unité fonctionnelle** : Permettre à 100 étudiants de s’émarger dix fois et de consulter leurs présences, et à un membre du staff de consulter les présences, pendant une semaine, avec un serveur mutualisé.

| Scénario | Acteur | Fréquence | Durée | Requêtes | Données | Terminal | Réseau |
|---|---|---|---|---|---|---|---|
| SC1 | étudiant | 10 | 3 s | 2 | 0.5 Ko | smartphone | 4G |
| SC2 | étudiant | 1 | 10 s | 5 | 1595.305 Ko | smartphone | 4G |
| SC3 | staff | 1 | 20 s | 3 | 1595.305 Ko | laptop | fixe |

Nous ramenons tous les résultats à cette UF. Les scénarios sont des hypothèses de travail : ils ne sont pas issus d’une journalisation réelle. C’est une limite explicite.

# 5. Méthodologie

Nous appliquons les quatre phases d’ISO 14040/14044 [S12][S13] : objectifs et champ, inventaire, évaluation des impacts, interprétation. La frontière est une ACV screening attributionnelle :

- terminaux (fabrication + usage) ;
- réseau fixe et mobile ;
- serveur et hébergement (fabrication + usage) ;
- développement et maintenance ;
- fin de vie exclue faute de facteur spécifique.

Les indicateurs sont le GWP100 (kg CO2 eq), l’ADPe (kg Sb eq) et l’ADPf (MJ). Les facteurs viennent de Boavizta [S26] ; pour le réseau, nous utilisons le facteur local NegaOctet [S35] afin de couvrir GWP, ADPe et ADPf. Le facteur ouvert Green Coding [S42] reste disponible comme variante de screening pour le GWP seul.

::: callout {tone=hypothese title="Notre hypothèse"}
Le mix électrique est celui de la France en 2024 : **51,9 g CO2e/kWh** [S10]. Le serveur est un 2U mutualisé, avec un PUE de 1,5 et 10 % des impacts alloués au service.
:::

# 6. Inventaire et facteurs

| Poste | Catégorie | Tier | GWP (kg CO2e) | ADPe (kg Sb eq) | ADPf (MJ) | Source |
|---|---|---|---|---|---|---|
| Smartphones des étudiants | device | 1 | 0.00428 | 1.04e-07 | 0.0567 | S26 |
| Laptop du staff | device | 1 | 3.52e-05 | 1.4e-09 | 0.000534 | S26 |
| Laptops des développeurs | development | 1 | 0.57 | 2.21e-05 | 8.65 | S26 |
| Serveur 2U mutualisé | server | 3 | 1.12 | 1.82e-05 | 40.4 | S26 |
| Réseau fixe | network | 2 | 1.89e-06 | 3e-10 | 0.000154 | S35 |
| Réseau mobile | network | 2 | 0.002 | 1.24e-07 | 0.218 | S35 |
| Maintenance applicative | maintenance | 1 | 0.0633 | 2.46e-06 | 0.961 | S26 |

Les facteurs utilisés sont documentés dans `factors.open.csv` et `factors.local.example.csv`. Les valeurs Boavizta sont datées du 2026-11-09. Le facteur réseau de la démonstration est NegaOctet local [S35], utilisé comme exemple pédagogique non redistribuable. Green Coding [S42] reste une variante ouverte pour le GWP seul.

| ID | Hypothèse | Valeur | Source | Confiance | Statut | Preuve | Owner | Détail preuve |
|---|---|---|---|---|---|---|---|---|
| H1 | Le serveur est un 2U mutualisé dont les caractéristiques sont inconnues ; les valeurs Boavizta par défaut sont utilisées. | 900 kg CO2e embarqué | S26 | low | évalué - scénario | sans preuve | Ops / Achats | Fiche serveur absente ; scénario Boavizta. |
| H2 | Le PUE de l’hébergement est de 1,5. | 1.5 ratio | S26 | low | évalué - scénario | sans preuve | Achats | PUE contractuel absent ; scénario 1,5. |
| H3 | 10 % des impacts du serveur sont alloués au service. | 0.1 part | S26 | medium | évalué - convention | convention | GreenIT | Convention de travail ; matrice d’allocation non signée. |
| H4 | Le développement représente 30 h par développeur. | 30 heures | S36 | medium | évalué - estimation | sans preuve | Tech lead | Timesheet absent ; scénario 30 h. |
| H5 | Chaque étudiant utilise le service 40 s sur la semaine. | 40 secondes | S36 | medium | évalué - scénario | sans preuve | Produit | Logs absents ; scénario 40 s. |
| H6 | Le mix électrique français est de 51,9 g CO2e/kWh. | 51.9 g CO2e/kWh | S10 | high | évalué - documenté | preuve | GreenIT | Base Empreinte [S10]. |
| H7 | Le volume réseau est dérivé de la page mesurée (1595.3 Ko) : 0.001521 Go fixe et 0.152617 Go mobile. | 0.154138 Go | S28 | medium | évalué - mesuré | preuve | Tech lead | web-metrics.json ; page mesurée. |

# 7. Résultats par étape du cycle de vie

![Graphique des impacts GWP par étape du cycle de vie](/home/mister_omega/greenITPlugins/greenit-rncp39388/dist/figures/lifecycle.png)

| Étape | GWP (kg CO2e) | Part |
|---|---|---|
| Développement | 0.57 | 32.4 % |
| Maintenance | 0.0633 | 3.6 % |
| Utilisation | 1.13 | 64.0 % |

Le serveur et le développement dominent. La maintenance reste faible. La fin de vie n’est pas évaluée : nous préférons l’assumer plutôt que d’inventer un facteur.

# 8. Résultats par tier

![Diagramme de la répartition du GWP par tier](/home/mister_omega/greenITPlugins/greenit-rncp39388/dist/figures/tiers.png)

| Tier | GWP (kg CO2e) | Part |
|---|---|---|
| Tier 1 | 0.638 | 36.3 % |
| Tier 2 | 0.002 | 0.1 % |
| Tier 3 | 1.12 | 63.6 % |

Le tier 3 (serveur) représente la majorité du GWP. Le tier 1 (terminaux) est faible **parce que** les appareils sont partagés et utilisés très peu de temps pour le service. Ce résultat serait très différent avec des terminaux dédiés.

# 9. Résultats par fonction

Nous n’avons pas alloué les impacts scénario par scénario, car les facteurs disponibles ne permettent pas une répartition fiable. Le tableau suivant donne les volumes de données, qui ne sont pas proportionnels aux impacts :

| Fonction | Volume indicatif | Lecture |
|---|---|---|
| Émargement étudiant | 5 Ko | Très faible poids, mais 10 interactions par étudiant. |
| Consultation étudiante | 120 Ko | Poste web le plus lourd. |
| Consultation staff | 10 Ko | Faible volume. |

::: callout {tone=limite title="Notre limite"}
Nous donnons une répartition indicative par volume de données, sans l’utiliser comme score ; une répartition par fonction serait une fausse précision.
:::

# 10. Hotspots et contributeurs principaux

![Graphique des cinq premiers contributeurs au GWP](/home/mister_omega/greenITPlugins/greenit-rncp39388/dist/figures/hotspots.png)

| Rang | Poste | GWP (kg CO2e) | Part |
|---|---|---|---|
| 1 | Serveur 2U mutualisé | 1.12 | 63.6 % |
| 2 | Laptops des développeurs | 0.57 | 32.4 % |
| 3 | Maintenance applicative | 0.0633 | 3.6 % |
| 4 | Smartphones des étudiants | 0.00428 | 0.2 % |
| 5 | Réseau mobile | 0.002 | 0.1 % |

Le serveur représente **63.6 %** du GWP. Le développement représente **32.4 %**. Les smartphones, dans notre scénario partagé, ne représentent que **0.2 %**.

# 11. Conditions de validité, sensibilité et plan de consolidation

Le rapport reste un **screening**. Nous ne supprimons pas les incertitudes : nous les quantifions et nous indiquons comment les réduire.

## Fourchette globale

Nous appliquons une fourchette de ±30 % sur le total, faute de distribution de facteurs :

- bas : **1.23 kg CO2e** ;
- base : **1.76 kg CO2e** ;
- haut : **2.29 kg CO2e**.

## Scénarios de sensibilité

| Scénario | Variation | GWP (kg CO2e) | Δ vs base | Lecture |
|---|---|---|---|---|
| Référence | base | 1.76 | négligeable | Scénario du rapport |
| PUE | 1.2 | 1.62 | -7.8 % | PUE de l’hébergement |
| PUE | 1.5 | 1.76 | négligeable | PUE de l’hébergement |
| PUE | 1.8 | 1.89 | 7.8 % | PUE de l’hébergement |
| Allocation serveur | 5% | 1.2 | -31.8 % | Part des impacts serveur allouée |
| Allocation serveur | 10% | 1.76 | négligeable | Part des impacts serveur allouée |
| Allocation serveur | 20% | 2.88 | 63.7 % | Part des impacts serveur allouée |
| Développement | 15 h/dev | 1.47 | -16.2 % | Durée de développement |
| Développement | 30 h/dev | 1.76 | négligeable | Durée de développement |
| Développement | 60 h/dev | 2.33 | 32.5 % | Durée de développement |
| Usage étudiant | 20 s | 1.75 | -0.1 % | Temps d’usage par étudiant |
| Usage étudiant | 40 s | 1.76 | négligeable | Temps d’usage par étudiant |
| Usage étudiant | 120 s | 1.77 | 0.5 % | Temps d’usage par étudiant |
| Mix électrique | 51.9 g/kWh | 1.76 | négligeable | Intensité carbone de l’électricité |
| Mix électrique | 100 g/kWh | 2.5 | 42.4 % | Intensité carbone de l’électricité |
| Mix électrique | 300 g/kWh | 5.6 | 218.9 % | Intensité carbone de l’électricité |
| Volume réseau | ×0.5 | 1.76 | négligeable | Incertitude sur les volumes réseau |
| Volume réseau | ×1 | 1.76 | négligeable | Incertitude sur les volumes réseau |
| Volume réseau | ×1.5 | 1.76 | négligeable | Incertitude sur les volumes réseau |
| Terminaux dédiés | 168 h | 66.4 | 3679.5 % | Smartphones dédiés au service |

Le scénario « terminaux dédiés » est le plus structurant : le GWP passerait à environ **66.4 kg CO2e**, soit **37.8×** le scénario de partage. Ce n’est pas une prédiction : c’est la démonstration que l’allocation change la conclusion.

## Conditions de validité

- Le serveur est un profil Boavizta par défaut ; il doit être remplacé par la fiche fournisseur (H1).
- Le PUE de 1,5 doit être confirmé par l’hébergeur (H2) ; les scénarios 1,2 et 1,8 encadrent la valeur.
- L’allocation de 10 % est une convention de travail (H3) ; les scénarios 5 % et 20 % montrent la sensibilité.
- Les 30 h de développement et les 40 s d’usage sont des scénarios (H4, H5), pas des mesures.
- Le facteur réseau NegaOctet local couvre GWP, ADPe et ADPf ; sa licence interdit la redistribution.
- La fin de vie, les impacts sociaux et l’effet rebond sont hors périmètre.

## Plan de consolidation

1. Obtenir la fiche serveur, la facture d’électricité et le PUE contractuel.
2. Mesurer les usages réels (logs, entretiens) et remplacer H4/H5.
3. Ajouter les facteurs ADPe/ADPf réseau ou déclarer le tier 2 partiellement évalué.
4. Intégrer la fin de vie avec un facteur documenté.
5. Faire une revue critique externe avant de présenter le rapport comme une ACV complète.

::: callout {tone=limite title="Ce que nous ne savons pas encore"}
Les caractéristiques réelles du serveur, le PUE de l’hébergeur et les usages réels ne sont pas mesurés. Le rapport le dit et fournit les scénarios qui encadrent l’incertitude. Il ne prétend pas à une ACV complète.
:::

# 12. Diagnostic technique

## Frontend

- Image PNG de **1,6 Mo** : elle domine le poids de la page.
- CSS dupliqué et non minifié.
- JavaScript non minifié, `console.log`, `innerHTML`, polling toutes les 5 s.
- `alt` manquant, champ sans label, `target="_blank"` sans `rel`.

## Backend

- `SELECT *` sur la table des présences.
- Absence d’index sur `created_at`.
- CORS `*`.
- Secret factice dans le code (à ne jamais faire en production).

## Infrastructure

- Un serveur 2U mutualisé, PUE 1,5 supposé, 10 % alloués.
- Pas de mesure réelle de consommation.
- Pas de politique de cache ni de compression.

| Sévérité | Fichier:Ligne | Signal | Pourquoi | RGESN |
|---|---|---|---|---|
| high | api/server.py:44 | sql-select-star | Requête SELECT * : transfère des colonnes inutiles. | 7.1 |
| high | web/app.js:34 | set-interval | Polling périodique. | 4.9 |
| high | web/index.html:11 | img-no-alt | Image sans attribut alt. | 4.2 |
| medium | web/app.js:8 | inner-html | Injection HTML directe, risque XSS et rendu inutile. | 4.2 |
| medium | web/index.html:19 | input-no-id | Champ sans id, label difficile à associer. | 4.2 |
| medium | web/index.html:29 | target-blank-noopener | Ouverture d’onglet sans rel=noopener. | 4.2 |
| low | web/app.js:17 | console-log | Trace de debug laissée dans le code. | 6.5 |
| low | web/app.js:33 | todo | Dette technique non suivie. | 6.5 |

# 13. Benchmark et correspondance normative

| Outil | Périmètre | Licence | Sorties | Usage | Source |
|---|---|---|---|---|---|
| Boavizta API | Serveur, terminal, cloud | AGPL-3.0 / données ouvertes | GWP, PE, ADPe, ADPf | API et méthodologie | [S26] |
| EcoIndex | Web | CC BY-NC-ND | Score, GES, eau | Screening navigateur | [S28] |
| GreenIT Analysis | Web | AGPL-3.0 | EcoIndex | Extension | [S30] |
| CodeCarbon | Compute Python | MIT | Énergie, carbone | Mesure d’entraînement | [S31] |
| Scaphandre | Hôte / processus | Apache-2.0 | Énergie | Métrologie | [S32] |
| Cloud Carbon Footprint | Cloud | Apache-2.0 | Carbone estimé | Facturation cloud | [S33] |
| NegaOctet | ACV multicritère | Commerciale | 526 facteurs | ACV détaillée | [S35] |
| Base Empreinte | Facteurs ADEME | Licence Ouverte | GWP, multicritères | Facteurs génériques | [S07] |
| OpenLCA | ACV | Open source + jeux de données | Multi-indicateurs | ACV complète | [S08] |

Nous ne comparons pas les scores entre eux : Boavizta, EcoIndex et NegaOctet ne mesurent pas la même chose. Nous utilisons Boavizta pour les équipements, EcoIndex pour le web et NegaOctet local pour le réseau ; Green Coding reste une variante ouverte pour le GWP seul.

Correspondance normative : RGESN [S03][S04] pour les 78 critères, GR491 [S05] pour les 8 familles, RWEB [S06] pour les 119 fiches web. Le rapport ne recopie pas les référentiels ; il cite les IDs utilisés.

# 14. Évaluation RGESN

| Statut | Nombre |
|---|---|
| validé | 5 |
| en cours | 9 |
| non validé | 54 |
| non applicable | 10 |

| Preuve | Nombre |
|---|---|
| preuve | 26 |
| sans preuve | 42 |
| non applicable | 10 |

**Score d’avancement** : 15.0/100. **Statuts évalués** : 100.0 %. **Preuves disponibles** : 39.6 %. Le score est **non significatif** : le taux de statuts ne vaut pas taux de preuves. Les 54 critères non validés le sont pour l’essentiel faute de preuve. Ce n’est pas le score officiel de l’outil RGESN.

![Jauge du score RGESN d’avancement](/home/mister_omega/greenITPlugins/greenit-rncp39388/dist/figures/rgesn.png)

| ID | Priorité | Statut | Critère |
|---|---|---|---|
| 1.2 | Prioritaire | en cours | Le service numérique a-t-il défini ses cibles utilisatrices, les besoins métiers et les attentes réelles des u |
| 1.4 | Prioritaire | en cours | Le service numérique réalise-t-il régulièrement des revues pour s’assurer du respect de sa démarche d’écoconce |
| 1.5 | Prioritaire | non validé | Le service numérique s’est-il fixé des objectifs en matière de réduction ou de limitation de ses propres impac |
| 1.9 | Prioritaire | non validé | Le service numérique a-t-il été conçu avec des technologies standard interopérables plutôt que des technologie |
| 2.1 | Prioritaire | en cours | Le service numérique a-t-il défini la liste des profils de matériels que les utilisateurs vont pouvoir employe |
| 2.10 | Prioritaire | non validé | Le service numérique a-t-il pris en compte les impacts environnementaux des services tiers utilisés lors de le |
| 2.2 | Prioritaire | en cours | Le service numérique est-il utilisable sur d’anciens modèles de terminaux ? |
| 2.4 | Prioritaire | non validé | Le service numérique est-il utilisable sur d’anciennes versions de système d’exploitation et de navigateurs we |
| 2.5 | Prioritaire | non validé | Le service numérique s’adapte-t-il à différents types de terminaux d’affichage ? |
| 2.8 | Prioritaire | non validé | Le service numérique impose-t-il à ses fournisseurs de garantir une démarche de réduction de leurs impacts env |

Les 54 critères non validés le sont majoritairement faute de preuve : nous les déclarons non conformes au stade du screening, plutôt que de les déclarer conformes sans preuve.

# 15. Brainstorm

Nous avons divergé sans filtrer, puis convergence avec une matrice impact/effort. Les 32 idées sont listées ci-dessous ; les idées écartées sont celles qui relèvent de la compensation, de l’énergie verte seule ou d’un gain non mesurable.

1. Supprimer le polling et les appels réseau périodiques.
2. Remplacer les images PNG par WebP/AVIF avec `srcset`.
3. Supprimer les images décoratives et les vidéos non porteuses d’information.
4. Minifier CSS et JS, supprimer le code mort.
5. Activer la compression et le cache HTTP.
6. Définir un budget de poids par page.
7. Réduire le DOM et le nombre de composants.
8. Éviter les polices web propriétaires.
9. Limiter les bibliothèques tierces.
10. Préférer les composants natifs du navigateur.
11. Paginer les listes et limiter les champs retournés.
12. Ajouter les index manquants et revoir les requêtes N+1.
13. Mettre en cache les réponses API stables.
14. Supprimer les logs de debug et les traces verbeuses.
15. Réduire la durée de conservation des données.
16. Minimiser les données collectées.
17. Documenter le PUE et la région de l’hébergement.
18. Choisir un hébergement bas carbone et mutualisé.
19. Mesurer la consommation réelle du serveur.
20. Adapter la taille des instances à la charge.
21. Éteindre les environnements de test la nuit.
22. Mutualiser les serveurs et les bases de données.
23. Allonger la durée de vie des terminaux.
24. Réemployer ou reconditionner les équipements.
25. Former les équipes aux gestes sobres.
26. Intégrer un contrôle GreenIT en CI.
27. Ajouter un critère GreenIT aux revues de code.
28. Mettre en place une charte numérique responsable.
29. Suivre un KPI énergie et un KPI poids.
30. Éviter la compensation carbone comme argument de vente.
31. Mesurer l’effet rebond après optimisation.
32. Comparer les scénarios terminal partagé / dédié.

![Matrice impact / effort des actions d’écoconception](/home/mister_omega/greenITPlugins/greenit-rncp39388/dist/figures/actions.png)

::: callout {tone=info title="Idées écartées"}
« Acheter de la compensation carbone », « passer au cloud vert sans preuve » et « Optimiser le frontend pour compenser le serveur » sont écartées : elles ne réduisent pas les impacts du service et peuvent relever du greenwashing.
:::

# 16. Plan d’action priorisé

| ID | Action | Horizon | Effort | Responsable | Échéance | KPI |
|---|---|---|---|---|---|---|
| A1 | Supprimer le polling et les traces de debug | quick win | faible | Frontend | S1 | 0 requête périodique |
| A2 | Activer Cache-Control et compression | quick win | faible | Backend | S1 | cache hit > 80 % |
| A3 | Optimiser les images (WebP/AVIF, srcset) | quick win | faible | Contenu | S2 | poids < 300 Ko |
| A4 | Indexer les requêtes et sélectionner les colonnes utiles | quick win | faible | Backend | S2 | temps P95 < 100 ms |
| A5 | Définir un budget de poids et de requêtes | moyen | moyen | Tech lead | S3 | budget respecté en CI |
| A6 | Documenter le PUE et la région de l’hébergeur | moyen | moyen | Achats | S3 | PUE < 1,5 |
| A7 | Mesurer la consommation réelle du serveur | moyen | moyen | Ops | S4 | kWh/semaine |
| A8 | Former les équipes à l’écoconception | moyen | moyen | RH/GreenIT | S4 | quiz > 80 % |
| A9 | Réduire les terminaux dédiés et allonger leur durée de vie | long | fort | Direction | S6 | part terminaux < 5 % |
| A10 | Intégrer un contrôle GreenIT en CI | long | moyen | DevOps | S6 | seuils bloquants |

Les quick wins sont A1 à A4. Ils sont peu risqués et mesurables. Les actions A5 à A8 structurent la démarche. A9 et A10 sont des projets longs, à décider avec la direction.

# 17. Quantification des gains

| Indicateur | Baseline | Optimisé | Delta |
|---|---|---|---|
| Poids transféré | 1 595 Ko | 91.6 Ko | 94.3 % |
| Requêtes | 7 | 6 | 14.3 % |
| Nœuds DOM | 25 | 26 | stable |
| Ressources avec cache | 0 | 4 | ajout de cache |
| EcoIndex | 87 (A) | 95 (A) | amélioration |
| GWP du service | 1.76 kg CO2e | 1.76 kg CO2e | 0.1 % |

La page passe de **1 595 Ko** à **91.6 Ko**, soit une réduction de **94.3 %**. L’EcoIndex passe de **87** à **95**. Le GWP du service ne baisse que de **moins de 0,1 %** : le réseau n’est pas le hotspot, et le serveur n’a pas changé. C’est un résultat honnête : optimiser le frontend ne suffit pas.

::: callout {tone=decision title="Notre décision"}
Nous ne présentons pas la réduction du poids de la page comme une réduction du GWP. Ce sont deux indicateurs différents. Le gain GWP est faible dans ce scénario, et nous le disons.
:::

# 18. Bénéfices collatéraux et gouvernance

- **Accessibilité** : labels, `alt`, contrastes, navigation clavier.
- **Sécurité** : suppression du CORS `*`, du secret factice, des `SELECT *`.
- **Qualité** : code plus léger, cache, index, moins de debug.
- **Coûts** : moins de bande passante, moins de CPU, moins de stockage.
- **UX** : page plus rapide, surtout sur mobile.
- **Gouvernance** : charte numérique responsable, revue GreenIT en CI, KPI poids/énergie.

# 19. Conclusion, bibliographie, glossaire et annexes

## Conclusion

Le service peut réduire fortement son poids web, mais son GWP reste dominé par le serveur et le développement. La priorité est de **mesurer** l’hébergement et la consommation réelle, puis de décider. Nous recommandons de ne pas acheter de compensation et de ne pas revendiquer la neutralité carbone.

## Sources et bibliographie

- **S01** — France Compétences, *RNCP39388 — Responsable green IT*, 2026-11-09. https://www.francecompetences.fr/recherche/rncp/39388
- **S02** — France Compétences, *RNCP42198 — autre titre Responsable green IT*, 2026-11-09. https://www.francecompetences.fr/recherche/rncp/42198
- **S03** — Arcep / Arcom / ADEME, *Référentiel général d’écoconception des services numériques — version 2024*, 2024-05. https://ecoresponsable.numerique.gouv.fr/docs/2024/rgesn-mai2024/referentiel_general_ecoconception_des_services_numeriques_version_2024.pdf
- **S04** — Arcep / Arcom / ADEME, *Outil de déclaration RGESN 2024 (XLSX)*, 2024-05. https://ecoresponsable.numerique.gouv.fr/docs/2024/rgesn-mai2024/rgesn_2024_outil_declaration_ecoconception.xlsx
- **S05** — INR, *GR491 — Guide de référence de l’écoconception de services numériques*, 2024. https://gr491.isit-europe.org/
- **S06** — Collectif Green IT, *RWEB 5.0.0 — Référentiel de bonnes pratiques*, 2024. https://rweb.greenit.fr/fr/fiches
- **S07** — ADEME, *Base Empreinte — facteurs d’impact*, 2026. https://base-empreinte.ademe.fr/
- **S08** — ADEME, *Méthodologie d’évaluation environnementale basée sur l’ACV pour un service numérique — RCP v2*, 2025. https://librairie.ademe.fr/societe-et-politiques-publiques/9418-methodologie-d-evaluation-environnementale-basee-sur-l-analyse-du-cycle-de-vie-acv-pour-un-service-numerique.html
- **S09** — ADEME / Arcep, *Étude de l’empreinte environnementale du numérique en France — 2020-2030-2050*, 2023-03. https://www.arcep.fr/uploads/tx_gspublication/dossier-presse-Etude-Ademe-Arcep-lot3_mars2023.pdf
- **S10** — ADEME, *Impacts environnementaux du numérique en France — mise à jour 2025*, 2025. https://ecoresponsable.numerique.gouv.fr/docs/2024/etude-ademe-impacts-environnementaux-numerique.pdf
- **S11** — MiNumEco, *Guide pratique pour des achats numériques responsables — ACV*, 2024. https://ecoresponsable.numerique.gouv.fr/publications/guide-pratique-achats-numeriques-responsables/demarche-numerique-responsable/analyse-cycle-de-vie
- **S12** — ISO, *ISO 14040:2006 — Management environnemental, ACV, principes et cadre*, 2006. https://www.iso.org/fr/standard/37456.html
- **S13** — ISO, *ISO 14044:2006 — Management environnemental, ACV, exigences et lignes directrices*, 2006. https://www.iso.org/fr/standard/38498.html
- **S14** — ISO/IEC, *ISO/IEC 21031:2024 — Software Carbon Intensity (SCI)*, 2024. https://www.iso.org/fr/standard/86612.html
- **S15** — Commission européenne, *Product Environmental Footprint (PEF) method*, 2021. https://green-forum.ec.europa.eu/green-business/environmental-footprint-methods/pef-method_en
- **S16** — JRC, *EF 3.1 — characterisation and normalisation factors*, 2023. https://publications.jrc.ec.europa.eu/repository/bitstream/JRC130796/JRC130796_01.pdf
- **S17** — ITU-T, *L.1410 — Methodology for environmental impact assessment of ICT goods, networks and services*, 2024-11. https://www.itu.int/rec/T-REC-L.1410/en
- **S18** — ITU-T, *L.1450 — Methodologies for environmental impact assessment of ICT*, 2023. https://www.itu.int/rec/T-REC-L.1450
- **S19** — ITU-T, *L.1470 — GHG emissions trajectories for the ICT sector*, 2020. https://www.itu.int/rec/T-REC-L.1470
- **S20** — République française, *Loi n° 2021-1485 du 15 novembre 2021 dite REEN*, 2021-11-15. https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000044327272
- **S21** — République française, *Décret n° 2022-1084 du 29 juillet 2022*, 2022-07-29. https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000046113741
- **S22** — République française, *Code de l’environnement, article L229-25 — BEGES*, 2026. https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051559662
- **S23** — Commission européenne, *Corporate Sustainability Reporting Directive (CSRD) et ESRS*, 2026. https://finance.ec.europa.eu/capital-markets-union-and-financial-markets/company-reporting-and-auditing/company-reporting/corporate-sustainability-reporting_en
- **S24** — CNIL, *Règlement général sur la protection des données (RGPD)*, 2016. https://www.cnil.fr/fr/reglement-europeen-protection-donnees
- **S25** — DINUM, *RGAA 4.1.2 — critères et tests*, 2023. https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/
- **S26** — Boavizta, *Documentation de l’API Boavizta*, 2026. https://doc.api.boavizta.org/
- **S27** — Boavizta, *Outils Boavizta*, 2026. https://www.boavizta.org/tools
- **S28** — EcoIndex, *Comment ça marche — méthode EcoIndex*, 2026. https://www.ecoindex.fr/comment-ca-marche
- **S29** — CNUMR, *EcoIndex Python — code source*, 2026. https://github.com/cnumr/EcoIndex_python
- **S30** — CNUMR, *GreenIT Analysis — code source*, 2026. https://github.com/cnumr/GreenIT-Analysis
- **S31** — MLCO2, *CodeCarbon — code source*, 2026. https://github.com/mlco2/codecarbon
- **S32** — Hubblo, *Scaphandre — code source*, 2026. https://github.com/hubblo-org/scaphandre
- **S33** — Cloud Carbon Footprint, *Cloud Carbon Footprint — code source*, 2026. https://github.com/cloud-carbon-footprint/cloud-carbon-footprint
- **S34** — Green Software Foundation, *Software Carbon Intensity (SCI) specification*, 2024. https://sci.greensoftware.foundation/
- **S35** — GreenIT.fr / NegaOctet, *NegaOctet — facteurs d’impacts ACV*, 2024. https://www.greenit.fr/negaoctet-acv-facteurs-dimpacts/
- **S36** — Zone01 Normandie, *Supports de formation GreenIT, modules 1–2*, 2025. $HOME/Downloads/Docs référent GreenIT.zip
- **S37** — Zone01 Normandie, *Présentation ACV Green IT*, 2025. $HOME/Downloads/ACV Green IT – Zone01 Normandie (1).pptx
- **S38** — Zone01 Normandie, *Questions jury RNCP*, 2025. $HOME/Downloads/Questions RNCP.odt
- **S39** — OWASP Foundation, *OWASP Top 10*, 2025. https://owasp.org/www-project-top-ten/
- **S40** — ANSSI, *Recommandations et guides d’hygiène numérique*, 2026. https://cyber.gouv.fr/
- **S41** — GHG Protocol, *Greenhouse Gas Protocol — Corporate Standard*, 2004. https://ghgprotocol.org/
- **S42** — Green Coding, *Network Carbon Intensity — méthodologie et facteur 0,04106063 kWh/Go*, 2025. https://docs.green-coding.io/docs/measuring/carbon/network-carbon-intensity/

## Glossaire

- **ACV** : Analyse du cycle de vie ; méthode d’évaluation des impacts sur tout le cycle de vie [S12][S13].
- **UF** : Unité fonctionnelle ; service rendu servant de base de comparaison.
- **GWP100** : Potentiel de réchauffement global à 100 ans, en kg CO2 eq.
- **ADPe** : Épuisement des ressources minérales, en kg Sb eq.
- **ADPf** : Épuisement des ressources fossiles, en MJ.
- **PUE** : Énergie totale du datacenter / énergie IT.
- **EcoIndex** : Score web 0–100 basé sur DOM, poids et requêtes [S28].
- **SCI** : Software Carbon Intensity, taux d’émission par unité fonctionnelle [S14].
- **RGESN** : Référentiel général d’écoconception des services numériques [S03].
- **GR491** : Guide de référence de l’écoconception de services numériques [S05].
- **RWEB** : Référentiel de bonnes pratiques web responsable [S06].
- **NegaOctet** : Base de facteurs d’impacts ACV commerciale [S35], exemple local optionnel.
- **Green Coding** : Méthode ouverte de calcul de l’intensité carbone réseau [S42].
- **Boavizta** : Communauté et API de quantification d’impact du numérique [S26].
- **Effet rebond** : Hausse d’usage qui annule une partie du gain.
- **Greenwashing** : Allégation environnementale non étayée ou trompeuse.
- **Compensation** : Achat de crédits carbone ; ne rend pas un service neutre.

## Annexes

- `metrics.json` : résultats détaillés.
- `calculation-notes.md` : note de calcul, formule par item.
- `rgesn-score.csv` : 78 critères.
- `codebase-audit.json` : signaux statiques.
- `web-metrics.json` : mesures Playwright.
- `sources.yml` : registre des 42 sources.
