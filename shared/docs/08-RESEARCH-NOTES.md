# Notes de recherche

## RNCP39388

- Titre : Responsable green IT, niveau 6, certificateur Efficom (Sciences-U Lille).
- Fiche active jusqu’au 19/07/2027.
- 4 blocs : BC01 Concevoir (4 compétences), BC02 Déployer (5), BC03 Maintenir (5), BC04 Conduire (5), soit 19 compétences.
- Modalités : études de cas et mises en situation professionnelle en mode projet.
- RNCP42198 est un autre titre « Responsable green IT » (niveau 7, IPSA) : ne pas l’utiliser.
- Sources : `[S01]`, `[S02]`.

## RGESN 2024

- 78 critères, 9 chapitres : Stratégie 10, Spécifications 10, Architecture 7, UX/UI 15, Contenus 8, Frontend 7, Backend 4, Hébergement 10, Algorithmie 7.
- Poids : Prioritaire 1,5 ; Recommandé 1,25 ; Modéré 1,0.
- Source de vérité : outil de déclaration XLSX `[S04]`.
- Le score du bundle est un score d’avancement, pas le score officiel.

## GR491

- 8 familles, 61 recommandations, 516 critères.
- Familles : Stratégie 8/76, Spécifications 6/56, UX/UI 10/64, Contenus 5/48, Front-end 10/75, Architecture 10/62, Back-end 6/72, Hébergement 6/63.
- Source : `[S05]`.

## RWEB 5.0.0

- 119 critères, 7 étapes : Spécifications, Conception, Réalisation, Production, Utilisation, Support/maintenance, Fin de vie.
- Source : `[S06]`.

## ACV

- ISO 14040/14044 : 4 phases, UF, frontière, allocation, ICV, LCIA, interprétation.
- ADEME RCP service numérique v2 : `[S08]`.
- PEF / EF 3.1 : 16 catégories, `[S15]`, `[S16]`.
- ITU-T L.1410 / L.1450 : `[S17]`, `[S18]`.
- SCI / ISO/IEC 21031 : `[S14]`, `[S34]`.

## Chiffres ADEME

### Étude 2020

- 17,2 Mt CO2e, soit 2,5 % de l’empreinte carbone française.
- Répartition : 79 % terminaux, 16 % datacenters, 5 % réseaux.
- Fabrication : 80 % ; usage : 20 %.
- Source : `[S09]`.

### Mise à jour 2025, données 2022

- 29,5 Mt CO2e, soit 4,4 % de l’empreinte carbone française.
- 11 % de la consommation électrique française : 51,5 TWh ; 65 TWh avec les datacenters étrangers.
- 117 Mt de ressources consommées, soit 1,7 t/personne.
- Répartition : 50 % terminaux, 46 % datacenters, 4 % réseaux.
- Fabrication : 60 % ; usage : 40 %.
- Source : `[S10]`.

### Lecture

Les deux études ne sont pas directement comparables : périmètres, méthodes et années différents. Le bundle cite l’année et la source. Il ne mélange pas 2020 et 2022 dans un même calcul.

## Outils et licences

- Boavizta : AGPL-3.0 pour le code, données ouvertes ; API publique.
- EcoIndex : CC BY-NC-ND ; usage non commercial.
- GreenIT Analysis : AGPL-3.0.
- CodeCarbon : MIT.
- Scaphandre : Apache-2.0.
- Cloud Carbon Footprint : Apache-2.0.
- NegaOctet : commercial, 526 facteurs, non redistribuable (exemple local optionnel).
- Green Coding : documentation publique, facteur réseau 0,04106063 kWh/Go, utilisé pour le GWP réseau.
- Base Empreinte : Licence Ouverte.
- OpenLCA : open source, jeux de données avec licences propres.

## Critique du support local

Le PPTX ACV Zone01 `[S37]` fournit une structure pédagogique utile : contexte, UF, tiers, résultats, plan d’action. Il faut corriger :

- l’incohérence possible entre les chiffres 2020 et 2022 ;
- le périmètre embarqué parfois implicite ;
- l’additivité des gains ;
- les sources manquantes ;
- les formulations de greenwashing potentielles.

Le classeur `ACV initiale.xlsx` `[S36]` donne des facteurs NegaOctet horaires et par Go. Ils restent disponibles dans `factors.local.example.csv`, avec avertissement de licence. La démonstration utilise le facteur local NegaOctet `[S35]` pour couvrir GWP, ADPe et ADPf. Le facteur ouvert Green Coding `[S42]` reste disponible comme variante de screening pour le GWP seul (0,04106063 kWh/Go × 51,9 g CO2e/kWh = 2,13 g CO2e/Go).

## Décisions de design

- Trois plugins, dépendance `greenit-audit` → `greenit-studio` + `greenit-engineering`.
- Calculs Python testés, pas de tableur opaque.
- Sources versionnées dans `sources.yml`.
- Rapport en 19 sections, deck en 15 slides.
- Vidéo silencieuse sous-titrée, voix off optionnelle.
- Pas de TTS, pas de service cloud.
