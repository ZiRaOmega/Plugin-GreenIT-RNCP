---
name: refactor
description: Refactorise un codebase avec mesure avant/après, tests, delta GreenIT et rollback documenté.
argument-hint: "<chemin> [objectif]"
disable-model-invocation: true
---

# Refactoriser avec preuve

## Préconditions

- Tests verts ou baseline capturée.
- Git propre ou commit de sauvegarde.
- Comportement caractérisé.

## Étapes

1. Mesurer avant : `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/measure_delta.py --before ...`.
2. Modifier par petits pas.
3. Lancer les tests après chaque pas.
4. Mesurer après avec la même méthode.
5. Documenter le delta : bundle, requêtes, CPU, mémoire, temps de build.
6. Donner un rollback.

## Interdictions

- Mélanger refactor et feature.
- Changer le comportement sans test.
- Supprimer des tests.
- Optimiser sans mesure.
- Affirmer un gain non mesuré.

## Sortie

Diff, rationale, tests, delta, risque, rollback, impact GreenIT estimé.
