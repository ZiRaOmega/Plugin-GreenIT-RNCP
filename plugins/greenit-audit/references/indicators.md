# Indicateurs d’impact — définitions et unités

| Indicateur | Définition | Unité | Modèle / source |
|---|---|---|---|
| **GWP100** | Potentiel de réchauffement global à 100 ans | kg CO2 eq | IPCC 2013, EF 3.1 `[S16]` |
| **ADPe** | Épuisement des ressources abiotiques, éléments et minéraux | kg Sb eq | CML v4.8 / PEF `[S15]` |
| **ADPf** | Épuisement des ressources abiotiques, ressources fossiles | MJ | CML v4.8 / PEF `[S15]` |
| **PE** | Énergie primaire cumulée | MJ | Cumulative Energy Demand |
| **EF** | Énergie finale | MJ | Physique |
| **Water use** | Consommation d’eau | m³ eq | EF 3.1 |
| **PUE** | Énergie totale du datacenter / énergie IT | sans dimension | ISO/IEC 30134-2 |
| **WUE** | Eau / énergie IT | L/kWh | ISO/IEC 30134-4 |
| **CUE** | Émissions de carbone / énergie IT | kg CO2e/kWh | ISO/IEC 30134-3 |
| **EcoIndex** | Score de performance environnementale web | 0–100, note A–G | EcoIndex `[S28]` |
| **SCI** | Software Carbon Intensity | g CO2e / unité fonctionnelle | ISO/IEC 21031 `[S14]` |

## GWP100

Le GWP100 convertit les émissions de différents gaz en équivalent CO2 sur 100 ans. Il ne mesure pas l’énergie ni l’épuisement des ressources. Un résultat en kg CO2e ne doit pas être appelé « énergie » ou « empreinte carbone » sans précision.

## ADPe et ADPf

- **ADPe** : « abiotic depletion potential, elements ». Concerné par les métaux et minéraux (cuivre, or, terres rares, etc.). Unité kg Sb eq.
- **ADPf** : « abiotic depletion potential, fossil ». Concerné par les combustibles fossiles. Unité MJ.
- **ADP** seul est ambigu : toujours préciser ADPe ou ADPf.
- Le facteur ADPe est dominé par la fabrication des équipements ; ADPf par l’énergie fossile.

## PE et EF

- **PE** (primary energy) : énergie primaire, avant conversion. Elle inclut les pertes de production et de transport.
- **EF** (final energy) : énergie finale, telle que consommée.
- Ne pas comparer PE et EF sans conversion.

## PUE, WUE, CUE

- **PUE** = énergie totale du datacenter / énergie des équipements IT. PUE 1,5 signifie 50 % de surconsommation.
- **WUE** = eau consommée / énergie IT.
- **CUE** = émissions / énergie IT.
- Un PUE bas ne garantit pas un impact faible : le mix électrique et le taux d’utilisation comptent.

## EcoIndex

EcoIndex combine trois mesures :

- complexité du DOM ;
- poids de la page transférée ;
- nombre de requêtes HTTP.

Il produit un score 0–100, une note A–G, une estimation de GES par page et une estimation d’eau par page. C’est un **outil de screening web**, pas une ACV. La licence est CC BY-NC-ND ; l’usage commercial nécessite un accord.

## SCI

La Software Carbon Intensity (SCI) est un taux d’émission par unité fonctionnelle :

```text
SCI = (O + M) / R
O = E × I
M = TE × (t / D) × RS
```

- `E` : énergie consommée (kWh).
- `I` : intensité carbone de l’électricité (g CO2e/kWh).
- `TE` : émissions incorporées du matériel (g CO2e).
- `t` : temps d’utilisation.
- `D` : durée de vie.
- `RS` : part des ressources allouée.
- `R` : unité fonctionnelle.

La SCI est un **taux**, pas une émission totale. Elle permet de comparer des architectures à service rendu égal.

## Scope 1/2/3

- **Scope 1** : émissions directes (combustion, véhicules).
- **Scope 2** : émissions indirectes liées à l’électricité achetée.
- **Scope 3** : autres émissions indirectes (achats, déplacements, usage des produits).

Un audit de service numérique peut contribuer au scope 3 amont (équipements) et aval (usage). Ne pas confondre scope organisationnel et cycle de vie produit.

## Règles de lecture

- Toujours donner l’unité et l’année du facteur.
- Toujours distinguer mesuré, estimé, supposé.
- Ne pas additionner des indicateurs différents.
- Ne pas comparer des résultats avec des frontières différentes.
- Afficher les hotspots et les incertitudes.
