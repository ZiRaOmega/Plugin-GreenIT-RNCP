# Checklist revue de code GreenIT

## Frontend

- Images optimisées, `srcset`, `alt`.
- CSS/JS minifiés, pas de code mort.
- Cache et compression.
- Pas de polling, pas d’autoplay.
- DOM raisonnable, composants natifs.
- Accessibilité RGAA.

## Backend

- `SELECT` ciblé, index, pagination.
- Cache, compression, payloads.
- Pas de N+1, pas de logs verbeux.
- Rétention des données.
- Secrets hors code, CORS restrictif.
- Jobs et batch.

## Infra

- Région, PUE, WUE, mix.
- Dimensionnement, autoscaling, idle.
- CI, stockage, backups, fin de vie.
- Supervision kWh et requêtes.
