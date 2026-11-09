# Utilisation

## Installation

Depuis la racine du bundle :

```bash
uv sync
make validate
```

Pour installer le marketplace dans Claude Code :

```text
/plugin marketplace add <owner>/<repo>
/plugin install greenit-audit --marketplace <owner>/<repo>
```

## Démonstration

```bash
make demo
make check
```

`make demo` produit `dist/` : rapport DOCX/PDF, soutenance PPTX/PDF, vidéo MP4, figures, métriques, dossier RNCP.

## Audit réel

1. Copier `plugins/greenit-audit/assets/example-audit.yml` vers `audit.yml`.
2. Remplacer le projet, l’UF, l’inventaire, les hypothèses.
3. Lancer :

```bash
python3 plugins/greenit-audit/scripts/validate_audit.py --input audit.yml \
  --factors plugins/greenit-audit/references/factors.open.csv
python3 plugins/greenit-audit/scripts/calc.py --input audit.yml \
  --factors plugins/greenit-audit/references/factors.open.csv \
  --out dist/audit-demo/metrics.json --markdown
```

4. Évaluer les 78 critères RGESN dans `rgesn-assessment.yml`.
5. Générer le rapport et le deck.

## Dépannage

- `python-pptx` manquant : `uv pip install python-pptx==1.0.2`.
- Playwright sans navigateur : `CHROMIUM_PATH=/usr/bin/chromium` ou `playwright install chromium`.
- LibreOffice absent : DOCX/PPTX générés, PDF sauté.
- `ffmpeg` absent : vidéo sautée.
- Facteur réseau absent : le calcul continue et le poste est signalé ; la démonstration fournit les facteurs locaux pour les trois indicateurs.
