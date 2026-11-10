---
name: rncp39388
description: Produit la matrice de compétences et le dossier de preuves pour le titre RNCP39388 Responsable green IT.
argument-hint: "<dist/> [BC01,BC04]"
disable-model-invocation: true
---

# Dossier RNCP39388

## Question obligatoire

**Demander quels blocs auditer avant de produire le dossier.** Exemples : `BC01 et BC04`, `BC02 et BC03`, ou les quatre blocs.

La matrice complète reste à 19 lignes ; les blocs non sélectionnés sont marqués `hors périmètre`.


## Cible

RNCP39388, niveau 6, Efficom, 4 blocs, 19 compétences, fiche active jusqu’au 19/07/2027. Ne pas utiliser RNCP42198, qui est un autre titre.

## Blocs

- BC01 Concevoir une solution numérique responsable (4).
- BC02 Déployer un système informatique responsable (5).
- BC03 Maintenir un système informatique responsable (5).
- BC04 Conduire un projet numérique responsable (5).

## Livrables

`01-matrice-competences.csv`, `02-dossier-preuves.md`, `03-checklist-livrables.md`, `04-questions-jury.md`, `05-plan-soutenance-15min.md`, `06-charte-numerique-responsable.md`, `07-plan-mesure-energetique.md`, `08-plan-projet.md`, `09-formation-greenit.md`, `10-retrospective.md`.

## Règles

- Chaque compétence a au moins une preuve existante.
- Chaque preuve est un fichier ou un livrable vérifiable.
- Ne pas inventer une expérience professionnelle.
- Ne pas confondre les blocs.
- Vérifier que la matrice a 19 lignes et 4 blocs, avec les blocs non sélectionnés en `hors périmètre`.

## Vérification

`check_outputs.py` vérifie la matrice, le dossier et la formation.
