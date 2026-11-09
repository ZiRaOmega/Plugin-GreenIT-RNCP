# GreenIT Audit

GreenIT Audit couvre l’audit Green IT français : cadrage, unité fonctionnelle, ACV screening ISO 14040/44, calculs GWP/ADPe/ADPf, RGESN 2024, GR491, RWEB, benchmark, rapport, soutenance et preuves RNCP39388.

## Installation

```text
/plugin install greenit-audit --marketplace <owner>/<repo>
```

## Usage

Le skill `greenit-audit` orchestre le flux complet. Les skills `greenit-calculations`, `greenit-norms`, `greenit-report`, `greenit-defense`, `greenit-benchmark` et `rncp39388` peuvent être invoqués séparément.

## Prérequis

Python 3.10+, `openpyxl`, `PyYAML`, `jsonschema`, `matplotlib`, `python-docx` et `python-pptx`. Le plugin dépend de `greenit-studio` et `greenit-engineering`. `factors.local.example.csv` ne contient que l’en-tête : aucune valeur NegaOctet n’est publiée. La démonstration utilise `factors.local.csv`, ignoré par Git, à fournir sous licence pour évaluer GWP/ADPe/ADPf réseau.
