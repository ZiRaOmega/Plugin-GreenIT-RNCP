# Checklist d’analyse codebase

## Frontend

- Images : format, dimensions, poids, `srcset`, `alt`.
- CSS : duplication, minification, taille, polices.
- JavaScript : minification, code mort, `console.log`, `debugger`, polling.
- DOM : profondeur, nombre de nœuds, composants.
- Réseau : requêtes, cache, compression, tiers.
- Accessibilité : labels, contrastes, clavier, `alt`.

## Backend

- Requêtes : `SELECT *`, N+1, index, pagination.
- Cache : HTTP, application, base.
- Payloads : taille, champs inutiles.
- Logs : niveau, verbosité, rétention.
- Sécurité : secrets, CORS, entrées, dépendances.
- Jobs : fréquence, idle, batch.

## Infrastructure

- Hébergement : région, PUE, WUE, mix.
- Dimensionnement : CPU, RAM, autoscaling.
- CI/CD : runners, cache, artefacts.
- Stockage : backups, rétention, fin de vie.
- Supervision : kWh, requêtes, erreurs.
