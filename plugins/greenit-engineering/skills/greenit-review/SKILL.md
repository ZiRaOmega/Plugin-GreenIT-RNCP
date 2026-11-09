---
name: greenit-review
description: Réalise une revue de code GreenIT par tier et étape de cycle de vie, avec preuves et recommandations.
argument-hint: "<codebase> [diff]"
---

# Revue de code GreenIT

## Checklist

- **Front** : images, fonts, JS/CSS, DOM, requêtes, cache, tiers, animations, dark mode, responsive, accessibilité.
- **Back** : requêtes, index, pagination, cache, compression, rétention, jobs, logs, payloads, N+1, `SELECT *`, ORM, batch, async, carbon-aware.
- **Infra** : hébergement, PUE/WUE, région, renouvelable, autoscaling, idle, conteneurs, CI, stockage, backups, fin de vie.
- **Data/IA** : nécessité, entraînement, inférence, taille, quantization, dataset, réentraînement, RAG vs fine-tuning.
- **Sécurité** : surface d’attaque, dépendances, secrets, auth, CORS, headers, backups.
- **Accessibilité** : RGAA.

## Sortie

`greenit-review.md` avec sévérité, preuve, mapping norme, recommandation, effort, impact, owner.

## Règle

Ne pas affirmer un gain sans mesure ou estimation. Distinguer constat, hypothèse et recommandation.
