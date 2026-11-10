---
name: content-challenge
description: Lance un agent indépendant qui challenge chaque livrable GreenIT pour trouver les zones d’ombre, le jargon, les incohérences et les affirmations non prouvées.
argument-hint: "<dist>"
disable-model-invocation: true
---

# Challenge indépendant des livrables

## Rôle

Un second regard, en lecture seule, qui ne réécrit pas les documents. Il cherche :

- les zones d’ombre et les preuves manquantes ;
- les passages trop techniques pour un jury ou un client ;
- les incohérences entre chiffres, sources, hypothèses et slides ;
- les affirmations de greenwashing ou de survente ;
- les compétences RNCP remplies sans preuve réelle ;
- les livrables qui ne ressemblent pas au travail d’un étudiant.

## Agent

Invoquer l’agent `independent-challenger` du plugin `greenit-reviewer`.

Si le harness ne supporte pas les agents, lire `agents/independent-challenger.md` et appliquer la même grille manuellement.

## Sortie

`dist/challenge-report.md` :

```markdown
# Challenge indépendant

## Verdict global
- conforme / à corriger / bloquant

## Par livrable
### Rapport
- constat
- preuve ou citation
- question à poser
- correction attendue

### Soutenance
...

### Dossier RNCP
...

## Questions à préparer pour le jury
```

## Règle

L’agent ne modifie aucun fichier. Il cite les passages et propose des questions, pas des réécritures complètes.
