# Formules de calcul

Les symboles sont explicités dans chaque formule. Les exemples sont des ordres de grandeur de démonstration ; les valeurs réelles viennent de `audit.yml` et des facteurs.

## 1. Appareil utilisateur

```text
I_appareil = N × [ (I_emb / D_vie) × t_use + I_use_h × t_use × (I_grid / I_ref) × PUE ] × S_alloc
```

- `N` : nombre d’appareils.
- `I_emb` : impacts incorporés d’un appareil (kg CO2e, kg Sb eq, MJ).
- `D_vie` : durée de vie en heures.
- `t_use` : heures d’usage du service par appareil.
- `I_use_h` : impacts d’usage par heure, au mix de référence.
- `I_grid / I_ref` : ratio d’intensité carbone du mix réel / mix de référence. La valeur par défaut de `I_ref` est **380 g CO2e/kWh** dans les facteurs Boavizta du bundle.
- `PUE` : 1,0 pour un terminal.
- `S_alloc` : part allouée au service.

Exemple : `N=100`, `I_emb=181`, `D_vie=35040`, `t_use=1,5`, `I_use_h=0,00856`, `I_grid=51,9`, `I_ref=380`, `PUE=1`, `S_alloc=0,01` → environ `1,75 g CO2e` pour les 100 appareils.

## 2. Serveur

```text
I_serveur = N × [ (I_emb / D_vie) × t_res + I_use_h × t_res × (I_grid / I_ref) × PUE ] × S_res
```

Exemple : `N=1`, `I_emb=900`, `D_vie=35040`, `t_res=168`, `I_use_h=0,19977`, `I_grid/I_ref=0,1366`, `PUE=1,5`, `S_res=0,1` → environ `1,12 kg CO2e`.

## 3. Réseau

```text
I_réseau = D_GB × F_GB × (I_grid / I_ref) × S_alloc
```

`D_GB` : données transférées en Go. `F_GB` : facteur par Go (kg CO2e/Go, kg Sb eq/Go, MJ/Go), mesuré à `I_ref`. Le ratio `I_grid / I_ref` ajuste le GWP réseau au mix électrique du scénario. Le facteur doit préciser le réseau (fixe, mobile), l’année et les indicateurs couverts. Le facteur Green Coding, utilisé en variante, a `I_ref = 51,9 g CO2e/kWh` et ne couvre que le GWP. La démonstration utilise le facteur local NegaOctet pour les trois indicateurs. Le moteur sait représenter une valeur absente par `None`, jamais par zéro.

## 4. Développement

```text
I_dev = N_dev × t_dev × F_laptop_h
```

`F_laptop_h` inclut fabrication + usage du laptop de développement. Ne pas ajouter une seconde fois la fabrication si elle est déjà dans le facteur.

## 5. Maintenance

```text
I_maintenance = N_op × t_op × F_appareil_h
```

## 6. Fin de vie

```text
I_fin_de_vie = N × F_eol
```

`F_eol` : impact de fin de vie par appareil. Si le facteur n’existe pas, le dire et ne pas inventer.

## 7. Total

```text
I_total = Σ I
```

Additionner uniquement des indicateurs de même unité et de même frontière.

## 8. Part

```text
part = I_poste / I_total × 100
```

## 9. Delta

```text
Δ = I_baseline − I_action
Δ% = Δ / I_baseline × 100
```

Un delta positif est un gain. Vérifier l’additivité : deux actions qui réduisent le même poste ne s’additionnent pas linéairement.

## 10. Score RGESN

```text
score = 100 × Σ(poids × valeur) / Σ(poids des critères évalués)
couverture = Σ(poids évalués) / Σ(poids applicables) × 100
```

## 11. EcoIndex

La formule exacte et les quantiles sont implémentés dans `ecoindex.py`, avec la licence CC BY-NC-ND. Exemple de contrôle : `dom=47`, `req=2`, `size=1,37 Mo` → score 95, note A.

## 12. SCI

```text
SCI = (E × I + TE × (t/D) × RS) / R
```

Exemple : `E=10`, `I=100`, `TE=1000`, `t=100`, `D=1000`, `RS=0,5`, `R=10` → `105 g CO2e/unité`.

## 13. PUE, WUE, CUE

```text
PUE = E_datacenter / E_IT
WUE = eau_litres / E_IT_kWh
CUE = emissions_kg / E_IT_kWh
```

## 14. Incertitude

```text
low = base × (1 − u)
high = base × (1 + u)
```

`u` : incertitude relative (par exemple 0,3 pour ±30 %). Pour une analyse de sensibilité, faire varier un facteur à la fois, puis les facteurs dominants ensemble.

## Pièges

- Le scaling ADPe/ADPf par `I_grid / I_ref` est une approximation de screening. Pour une ACV complète, utiliser des facteurs d’usage spécifiques au mix et au matériel, ou Boavizta avec le lieu d’usage.
- Ne pas mélanger kg CO2e et g CO2e.
- Ne pas additionner GWP, ADPe et ADPf.
- Ne pas comparer un résultat par utilisateur avec un résultat par requête.
- Ne pas oublier la fabrication des terminaux : elle domine souvent.
- Ne pas oublier l’effet rebond : une optimisation peut augmenter l’usage.
