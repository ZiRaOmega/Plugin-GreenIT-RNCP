---
name: fix
description: Corrige un défaut à partir d’une reproduction, avec test de régression et analyse du co-bénéfice GreenIT.
argument-hint: "<bug> [fichier]"
disable-model-invocation: true
---

# Corriger un défaut

## Étapes

1. Reproduire par un test rouge.
2. Identifier la cause racine, pas le symptôme.
3. Faire le fix minimal.
4. Ajouter un test de régression.
5. Vérifier la sécurité (OWASP, secrets, entrées).
6. Estimer le co-bénéfice GreenIT : requêtes, poids, CPU, mémoire.
7. Documenter le risque et le rollback.

## Interdictions

- Publier un exploit.
- Committer sans accord.
- Élargir le périmètre.
- Corriger sans test.
- Utiliser le GreenIT comme argument pour un fix non mesuré.

## Sortie

Issue, reproduction, cause, fix, test, risque, rollback, co-bénéfice.
