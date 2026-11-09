---
name: greenit-calculations
description: Calcule les impacts ACV screening, GWP, ADPe, ADPf, EcoIndex et SCI avec hypothèses, unités et incertitudes.
argument-hint: "<audit.yml> [factors.csv]"
---

# Calculer les impacts

## Commandes

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_audit.py" \
  --input /chemin/mon-projet/audit.yml \
  --factors "${CLAUDE_PLUGIN_ROOT}/references/factors.open.csv" \
  --factors "${CLAUDE_PLUGIN_ROOT}/references/factors.local.example.csv"

python3 "${CLAUDE_PLUGIN_ROOT}/scripts/calc.py" \
  --input /chemin/mon-projet/audit.yml \
  --factors "${CLAUDE_PLUGIN_ROOT}/references/factors.open.csv" \
  --factors "${CLAUDE_PLUGIN_ROOT}/references/factors.local.example.csv" \
  --out /chemin/mon-projet/dist/metrics.json --markdown
```

## Formules

- Appareil : `N × [(I_emb / D_vie) × t + I_use_h × t × (I_grid / I_ref) × PUE] × S_alloc`.
- Serveur : idem avec `S_res`.
- Réseau : `D_GB × F_GB × (I_grid / I_ref) × S_alloc`.
- Développement / maintenance : `N × t × F_appareil_h`.
- Total : somme des indicateurs de même unité.
- Part : `I_poste / I_total × 100`.
- Delta : `I_baseline − I_action`.
- SCI : `(E × I + TE × (t/D) × RS) / R`.

## Règles

- GWP en kg CO2e, ADPe en kg Sb eq, ADPf en MJ.
- Ne pas additionner des indicateurs différents.
- Le scaling ADPe/ADPf par le mix est une approximation de screening.
- Les facteurs NegaOctet sont locaux et non redistribuables.
- `--allow-missing-factors` signale un facteur absent ; ne pas l’utiliser pour masquer un hotspot.

## Vérification

`metrics.json` contient `totals`, `items`, `shares`, `hotspots`, `uncertainty`, `quality`. La somme des parts par tier doit être 100 ± 0,1. Chaque item a `factor_id` et `source_id`.
