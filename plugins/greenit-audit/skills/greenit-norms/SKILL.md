---
name: greenit-norms
description: Évalue un service numérique avec RGESN 2024, GR491, RWEB et le cadre réglementaire français.
argument-hint: "<rgesn-assessment.yml>"
---

# Évaluer les référentiels

## RGESN 2024

- 78 critères, 9 chapitres, extraits de l’outil officiel `[S04]`.
- Statuts : `validé`, `en cours`, `non validé`, `non applicable` ; tout critère applicable doit être évalué.
- Score : `100 × Σ(poids × valeur) / Σ(poids évalués)`.
- Statuts évalués : `Σ(poids avec statut) / Σ(poids applicables) × 100`.
- Preuves disponibles : `Σ(poids avec preuve) / Σ(poids applicables) × 100`.
- Si la couverture des preuves < 50 %, afficher « score non significatif ».
- Ce n’est pas le score officiel de l’outil RGESN.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/score_rgesn.py" \
  --assessment /chemin/mon-projet/audit/rgesn-assessment.yml \
  --out /chemin/mon-projet/dist/rgesn-score.csv \
  --markdown /chemin/mon-projet/dist/rgesn-summary.md
```

## GR491

8 familles, 61 recommandations, 516 critères. Évaluer par famille et citer les recommandations utilisées. Ne pas produire un score global.

## RWEB

119 critères, 7 étapes de cycle de vie. Cibler les fiches pertinentes et citer les IDs. Ne pas recopier l’intégralité.

## Cadre réglementaire

Loi REEN, décret 2022-1084, AGEC, BEGES, CSRD/ESRS, RGPD, RGAA, ISO 14040/44, ISO/IEC 21031, ITU-T, PEF. Voir `references/regulations-fr.md`.

## Règles

- Ne pas prétendre à une conformité sans preuve.
- Ne pas confondre RGESN et RWEB.
- Ne pas recopier les référentiels.
- Relier chaque constat à une preuve.
