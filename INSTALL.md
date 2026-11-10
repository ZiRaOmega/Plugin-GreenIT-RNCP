# Installation — Plugin-GreenIT-RNCP

<p align="center"><img src="assets/WARNING_RED.png" alt="INTERDIT SANS AUTORISATION ÉCRITE — consultation seule, utilisation et installation interdites" width="100%"></p>

> **INTERDIT SANS AUTORISATION ÉCRITE.** Ce dépôt est public pour consultation uniquement. Les étapes d’installation ci-dessous sont documentaires et réservées au titulaire et aux collaborateurs autorisés. Elles ne accordent aucun droit d’utilisation. Voir `LICENSE` et la section « Avertissement légal » du `README.md`.


> **Licence View-Only.** Ce dépôt est public pour consultation uniquement. Les étapes ci-dessous sont documentaires et réservées au titulaire du copyright et aux collaborateurs autorisés. Elles ne accordent aucun droit d’utilisation, d’installation ou d’exécution. Voir `LICENSE`.

## Prérequis

- Python 3.10+
- `uv`
- LibreOffice (`soffice`)
- `ffmpeg`, `ffprobe`
- `pdftoppm`, `pdfinfo`, `pdftotext`
- Chromium ou Google Chrome pour Playwright

## Récupérer le dépôt

```bash
git clone https://github.com/ZiRaOmega/Plugin-GreenIT-RNCP.git
cd Plugin-GreenIT-RNCP
uv sync
```

## Facteurs locaux

Les valeurs NegaOctet ne sont pas publiées. `plugins/greenit-audit/references/factors.local.example.csv` ne contient que l’en-tête.

Pour un usage local autorisé :

```bash
cp plugins/greenit-audit/references/factors.local.example.csv \
   plugins/greenit-audit/references/factors.local.csv
# remplir avec des facteurs sous licence
```

`factors.local.csv` est ignoré par Git.

## Claude Code

```bash
claude plugin install greenit-audit \
  --marketplace /chemin/vers/Plugin-GreenIT-RNCP \
  --scope user -y

claude plugin install greenit-reviewer \
  --marketplace /chemin/vers/Plugin-GreenIT-RNCP \
  --scope user -y
```

Puis, dans Claude Code :

```text
/reload-plugins
```

Vérifier :

```bash
claude plugin list
claude plugin details greenit-audit
claude plugin details greenit-studio
claude plugin details greenit-engineering
```

Invocation :

```text
/greenit-audit:greenit-audit
/greenit-reviewer:design-review
/greenit-reviewer:content-challenge
```

## OMP

```bash
mkdir -p ~/.omp/agent/managed-skills
cp -a integrations/omp/greenit-rncp39388 ~/.omp/agent/managed-skills/
export BUNDLE_ROOT="/chemin/vers/Plugin-GreenIT-RNCP"
```

Puis demander à OMP d’utiliser le skill `greenit-rncp39388`.

## Harness générique

Le bundle suit le standard Agent Skills : chaque skill est un dossier avec `SKILL.md`.

```text
plugins/greenit-studio/skills/*/SKILL.md
plugins/greenit-audit/skills/*/SKILL.md
plugins/greenit-engineering/skills/*/SKILL.md
```

Pour un harness qui lit les `SKILL.md` :

1. exposer le dossier `plugins/` ou copier les skills dans le répertoire attendu ;
2. définir `BUNDLE_ROOT` vers la racine du dépôt ;
3. appeler les scripts avec des chemins absolus.

Workflow générique :

```bash
export BUNDLE_ROOT="/chemin/vers/Plugin-GreenIT-RNCP"
python3 "$BUNDLE_ROOT/scripts/run_audit.py" \
  --project /chemin/mon-projet \
  --audit /chemin/mon-projet/audit/audit.yml \
  --assessment /chemin/mon-projet/audit/rgesn-assessment.yml \
  --url http://127.0.0.1:8000/ \
  --out /chemin/mon-projet/dist
```

## Sorties

```text
dist/
├── metrics.json
├── codebase-audit.json
├── web-metrics.json
├── rgesn-score.csv
├── hypotheses.csv
├── report.md
├── rapport.docx / .pdf
├── synthese-client.md / .docx / .pdf
├── deck.yml
├── soutenance.pptx / .pdf
├── notes-orales.md
├── teaser.mp4 / .srt
├── figures/
├── rncp39388/
└── manifest.json
```

## Vérification

```bash
make test
make validate
```

`make demo` et `make check` nécessitent `factors.local.csv` et les dépendances de rendu ; ils ne fonctionnent pas sur un clone public sans facteurs sous licence.

## Désinstallation Claude Code

```bash
claude plugin uninstall greenit-audit --scope user
claude plugin marketplace remove Plugin-GreenIT-RNCP
```
