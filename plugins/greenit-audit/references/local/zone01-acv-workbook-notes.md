# Zone01 — classeur ACV initiale

Fichier local : `Fichiers partagés/ACV initiale.xlsx` `[S36]`. Non redistribué.

## Feuilles

- `FE` : facteurs d’impact NegaOctet utilisés dans l’exercice.
- `ACV` : inventaire par étape, fonction, tier et unité fonctionnelle.
- `Résultats détails` : résultats par étape et par tier.

## Facteurs observés

- Laptop, 1 h : GWP 0,0004389 kg CO2e ; ADPe 2,663e-10 kg Sb eq ; ADPf 0,05101 MJ.
- Smartphone, 1 h : GWP 1,8288e-5 kg CO2e ; ADPe 1,1096e-11 kg Sb eq ; ADPf 0,002126 MJ.
- Serveur rack, 1 h : GWP 0,043566 kg CO2e ; ADPe 1,8946e-6 kg Sb eq ; ADPf 1,827 MJ.
- Réseau fixe, 1 Go : GWP 0,00124 kg CO2e ; ADPe 1,84e-7 kg Sb eq ; ADPf 0,101 MJ.
- Réseau mobile, 1 Go : GWP 0,0131 kg CO2e ; ADPe 8,15e-7 kg Sb eq ; ADPf 1,43 MJ.

## Lecture critique

- Les facteurs horaires incluent probablement fabrication et usage ; ne pas ajouter une seconde fois la fabrication.
- Les résultats sont en kg CO2e pour GWP, kg Sb eq pour ADPe, MJ pour ADPf.
- Le classeur mélange parfois `ADP` et `ADPe` : toujours préciser.
- Les facteurs NegaOctet sont commerciaux et ne doivent pas être redistribués.
- Le bundle utilise ces valeurs uniquement dans `factors.local.example.csv`, avec avertissement.
