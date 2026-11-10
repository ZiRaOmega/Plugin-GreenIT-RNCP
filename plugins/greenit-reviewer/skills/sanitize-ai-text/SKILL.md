---
name: sanitize-ai-text
description: Détecte et remplace les caractères typographiques et formulations typiques des textes générés par IA dans les sources Markdown/YAML, puis reconstruit les livrables.
argument-hint: "<fichiers...> [--apply]"
disable-model-invocation: true
---

# Nettoyer les caractères IA

## Commande

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sanitize_ai_text.py" \
  /chemin/mon-projet/dist/report.md \
  /chemin/mon-projet/dist/notes-orales.md \
  /chemin/mon-projet/dist/deck.yml \
  --apply
```

Le nettoyage traite :

- tirets longs, guillemets courbes, points de suspension ;
- espaces insécables/fines et largeurs nulles ;
- puces, flèches, emojis, coches ;
- formulations « En tant que modèle », « Il est important de noter », « Plongeons dans ».

Il conserve les accents français, les unités et les symboles mathématiques légitimes.

## Après application

Reconstruire :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/../greenit-studio/scripts/md_to_docx.py" ...
python3 "${CLAUDE_PLUGIN_ROOT}/../greenit-studio/scripts/build_deck.py" ...
```

Puis relancer `/greenit-reviewer:design-review`.

## Règle

Ne pas appliquer le nettoyage au code source, aux URL, aux identifiants ou aux données brutes. Cibler les textes de restitution.
