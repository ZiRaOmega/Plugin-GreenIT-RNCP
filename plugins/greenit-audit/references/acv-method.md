# ACV d’un service numérique — méthode

L’analyse du cycle de vie (ACV) est encadrée par **ISO 14040** `[S12]` et **ISO 14044** `[S13]`. Elle permet d’évaluer les impacts environnementaux d’un service sur l’ensemble de son cycle de vie, avec une unité fonctionnelle explicite.

## Les 4 phases

1. **Définition des objectifs et du champ de l’étude** : question, public, unité fonctionnelle, frontière, catégories d’impact, règles d’allocation, qualité des données.
2. **Inventaire (ICV)** : quantités de matériels, durées d’usage, consommations électriques, données réseau, données de fin de vie.
3. **Évaluation des impacts (LCIA)** : caractérisation (GWP, ADPe, ADPf, etc.), éventuellement normalisation et pondération.
4. **Interprétation** : contributions, hotspots, sensibilité, incertitude, limites, recommandations.

## Unité fonctionnelle

L’unité fonctionnelle (UF) décrit **le service rendu**, pas le produit. Exemple : « permettre à 100 étudiants de s’émarger et au staff de consulter les présences pendant une semaine, avec un taux de disponibilité de 99 % ». Toutes les quantités sont ramenées à cette UF.

## Frontière du système

Le bundle utilise une frontière de **screening** :

- terminaux utilisateurs (fabrication + usage) ;
- réseau d’accès et de transport ;
- serveur et hébergement (fabrication + usage) ;
- développement et maintenance ;
- fin de vie lorsque des facteurs existent.

Sont exclus par défaut, et documentés : fabrication des bâtiments, infrastructure réseau inactive, effets rebond, impacts sociaux, pollution diffuse non caractérisée.

## Allocation

Pour un serveur partagé, allouer au service une part des impacts :

```text
S_alloc = ressources du service / ressources totales du serveur
```

Pour un terminal utilisé par plusieurs services, allouer au prorata du temps d’usage :

```text
S_alloc = temps d’usage du service / temps d’usage total du terminal
```

Toute allocation est un choix méthodologique. Le rapport doit la rendre explicite et proposer une sensibilité (par exemple terminal dédié vs partagé).

## Cut-off

Les flux dont la masse ou l’impact est inférieur à un seuil (souvent 1 %) peuvent être exclus, mais le seuil et les flux exclus doivent être documentés. Le cut-off ne doit pas masquer un hotspot.

## ACV attributionnelle vs conséquentielle

- **Attributionnelle** : quelle part des impacts existants attribuer au service ? C’est la approche utilisée pour le screening.
- **Conséquentielle** : quels impacts supplémentaires ou évités le service provoque-t-il ? Nécessite des hypothèses de marché et d’effet rebond.

Le bundle produit une ACV **attributionnelle de screening**. Il ne prétend pas à une ACV conséquentielle.

## Screening vs ACV complète

Une ACV complète exige des données spécifiques, une revue critique et une incertitude quantifiée. Le screening utilise des facteurs génériques, des hypothèses et des fourchettes. Il sert à **prioriser**, pas à certifier.

## Données et incertitude

- **Mesuré** : métriques web, consommation observée, factures.
- **Spécifique** : fiche fournisseur, configuration réelle.
- **Générique** : Boavizta, Base Empreinte, NegaOctet.
- **Hypothèse** : valeur par défaut, non vérifiée.

L’incertitude se traite par une analyse de sensibilité : ±20 % ou ±30 % sur les facteurs dominants, scénarios bas/base/haut. Le rapport affiche une fourchette, pas une valeur unique faussement précise.

## Références ADEME

- `[S08]` : RCP service numérique v2, méthodologie ACV.
- `[S11]` : guide achats numériques responsables, ACV.
- `[S09]` et `[S10]` : empreinte du numérique en France.
- `[S07]` : Base Empreinte, facteurs d’impact.

## Limites

Le screening ne remplace pas une ACV conforme avec revue critique. Il ne couvre pas les impacts sociaux, la biodiversité de manière détaillée, ni les effets rebond. Les facteurs génériques peuvent ne pas représenter le contexte réel.
