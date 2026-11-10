---
name: discover-palette
description: Découvre la direction artistique et la palette du projet audité (CSS, tokens, Tailwind, logo) et écrit design.yml pour le rapport et le deck.
argument-hint: "<projet> <dist>"
disable-model-invocation: true
---

# Découvrir la palette du projet

## Commande

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/../greenit-studio/scripts/extract_project_palette.py" \
  --project /chemin/mon-projet \
  --out /chemin/mon-projet/dist/design.yml
```

## Sources inspectées

- variables CSS `--primary`, `--brand`, `--green`, `--accent`, `--bg`, `--text`, `--muted`, `--alert` ;
- couleurs hexadécimales des CSS/SCSS/HTML/JS ;
- configurations Tailwind/design tokens ;
- logos et favicons (via Pillow).

## Sortie

`design.yml` contient :

- `source` : `css`, `logo`, `tokens` ou `fallback` ;
- `confidence` : `high`, `medium`, `low` ;
- `colors` : rôles sémantiques + clés de compatibilité `green_*` ;
- `warnings` : contraste insuffisant, palette absente, etc.

## Règles

- Ne jamais inventer une couleur de marque.
- Si le projet n’a pas de palette, utiliser une palette neutre et le signaler.
- Si la palette projet est verte, l’utiliser : la règle est la cohérence avec le projet, pas l’interdiction du vert.
- Le reviewer doit refuser une source `fallback` pour un livrable client.
