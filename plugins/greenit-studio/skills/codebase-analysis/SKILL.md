---
name: codebase-analysis
description: Analyse statiquement une codebase et mesure les métriques web locales pour produire un diagnostic GreenIT traçable.
argument-hint: "<racine> [--url http://127.0.0.1:8000/]"
---

# Analyser une codebase

## Quand l’utiliser

Utiliser ce skill au début d’un audit, avant les calculs. Il produit des preuves techniques, pas une note de conformité.

## Commandes

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/scan_codebase.py" \
  --root /chemin/mon-projet \
  --out /chemin/mon-projet/dist/codebase-audit.json --markdown

# Démarrer le serveur du projet :
# démo : cd /chemin/mon-projet && python3 api/server.py --port 8000
# statique : cd /chemin/mon-projet/web && python3 -m http.server 8000

python3 "${CLAUDE_PLUGIN_ROOT}/scripts/web_metrics.py" \
  --url http://127.0.0.1:8000/ \
  --out /chemin/mon-projet/dist/web-metrics.json --markdown
```

## Règles

- Ne jamais exfiltrer le code ; tout est local.
- Distinguer `mesuré`, `observé`, `hypothèse`.
- Masquer les secrets détectés.
- Ne pas remplacer un scanner de sécurité.
- Si Playwright échoue, continuer avec l’analyse statique et le signaler.
- Chaque signal contient `id`, `severity`, `confidence`, `file`, `line`, `evidence`, `why`, `greenit`, `tier`, `stage`, `effort`, `recommendation`.

## Vérification

`codebase-audit.json` contient les compteurs et les signaux. `web-metrics.json` contient DOM, requêtes, octets, cache, compression et EcoIndex. Comparer avant/après optimisation avec la même méthode.
