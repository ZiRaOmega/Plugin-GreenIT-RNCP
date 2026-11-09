# RGESN 2024 — synthèse opérationnelle

Le **Référentiel général d’écoconception des services numériques** (RGESN) est publié par l’Arcep, l’Arcom et l’ADEME, en application de l’article 25 de la loi REEN. La version utilisée ici est celle de **mai 2024**. Elle comporte **78 critères** répartis en **9 chapitres**. La source de vérité est l’outil de déclaration officiel `[S04]` ; le PDF `[S03]` sert de référence de lecture.

## Chapitres et volumes

| Chapitre | Critères |
|---|---:|
| 1 — Stratégie | 10 |
| 2 — Spécifications | 10 |
| 3 — Architecture | 7 |
| 4 — Expérience et interface utilisateur | 15 |
| 5 — Contenus | 8 |
| 6 — Frontend | 7 |
| 7 — Backend | 4 |
| 8 — Hébergement | 10 |
| 9 — Algorithmie | 7 |
| **Total** | **78** |

Le fichier `rgesn-2024.csv` est généré par `scripts/import_rgesn.py` depuis le XLSX officiel. Il contient l’ID, le chapitre, le libellé, la priorité, la difficulté, la cible, le moyen de test, le poids, l’URL, la version et la date de récupération.

## Poids indicatifs

| Priorité | Poids |
|---|---:|
| Prioritaire | 1,5 |
| Recommandé | 1,25 |
| Modéré | 1,0 |

Ces poids reprennent le dénominateur de l’outil officiel. Ils servent à produire un **score d’avancement transparent**, pas le score officiel de l’outil.

## Statuts d’évaluation

- `validé` : preuve vérifiable, valeur 1.
- `en cours` : action engagée mais preuve incomplète, valeur 0,5.
- `non validé` : critère applicable et non satisfait, valeur 0.
- `non applicable` : exclu du score et du dénominateur.

## Formule

```text
score = 100 × Σ(poids × valeur) / Σ(poids des critères évalués)
couverture = Σ(poids évalués) / Σ(poids applicables) × 100
applicables = total − non applicables
```

Si la couverture est inférieure à 50 %, le score est affiché comme **non significatif**. Un score élevé avec une faible couverture est un signal de greenwashing potentiel, pas une performance.

## Usage dans le bundle

`score_rgesn.py` produit `rgesn-score.csv` et `rgesn-summary.md`. Le rapport cite les IDs, les preuves et les actions. Les 78 critères ne sont pas recopiés intégralement dans le rapport : le CSV et le PDF officiel restent les références.

## Limites

Le RGESN est un référentiel d’écoconception de service numérique. Il ne remplace ni une ACV, ni un bilan GES réglementaire, ni un audit de sécurité. L’évaluation reste déclarative et doit être étayée par des preuves.
