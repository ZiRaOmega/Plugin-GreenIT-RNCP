---
name: greenit-rncp39388
description: "Utiliser le bundle GreenIT RNCP39388 dans OMP : cadrage, audit ACV/RGESN, rapport DOCX/PDF, soutenance PPTX, vidéo et dossier de preuves."
---

# GreenIT RNCP39388 — bundle OMP

## Quand utiliser ce skill

Utiliser ce skill pour :

- auditer un service ou une codebase avec une ACV screening ;
- calculer GWP100, ADPe et ADPf ;
- évaluer les 78 critères RGESN 2024 ;
- produire un rapport DOCX/PDF, une soutenance PPTX/PDF et une vidéo ;
- constituer un dossier de preuves RNCP39388 ;
- encadrer un refactor, un correctif, un brainstorm ou une revue GreenIT.

## Emplacement du bundle

```text
$BUNDLE_ROOT
```

Définir `BUNDLE_ROOT` vers la racine du dépôt cloné.

## Carte des 22 skills

### greenit-studio

| Skill | Fichier |
|---|---|
| Rapport DOCX/PDF | `plugins/greenit-studio/skills/docx-report/SKILL.md` |
| Diaporama PPTX | `plugins/greenit-studio/skills/pptx-deck/SKILL.md` |
| Vidéo de pitch | `plugins/greenit-studio/skills/video-pitch/SKILL.md` |
| Figures PNG | `plugins/greenit-studio/skills/images-charts/SKILL.md` |
| Analyse de codebase | `plugins/greenit-studio/skills/codebase-analysis/SKILL.md` |

### greenit-audit

| Skill | Fichier |
|---|---|
| Orchestrateur d’audit | `plugins/greenit-audit/skills/greenit-audit/SKILL.md` |
| Calculs ACV | `plugins/greenit-audit/skills/greenit-calculations/SKILL.md` |
| Normes RGESN/GR491/RWEB | `plugins/greenit-audit/skills/greenit-norms/SKILL.md` |
| Rapport | `plugins/greenit-audit/skills/greenit-report/SKILL.md` |
| Soutenance | `plugins/greenit-audit/skills/greenit-defense/SKILL.md` |
| Benchmark | `plugins/greenit-audit/skills/greenit-benchmark/SKILL.md` |
| Dossier RNCP39388 | `plugins/greenit-audit/skills/rncp39388/SKILL.md` |

### greenit-engineering

| Skill | Fichier |
|---|---|
| Refactor | `plugins/greenit-engineering/skills/refactor/SKILL.md` |
| Correctif | `plugins/greenit-engineering/skills/fix/SKILL.md` |
| Proposition | `plugins/greenit-engineering/skills/proposal/SKILL.md` |
| Brainstorm | `plugins/greenit-engineering/skills/brainstorm/SKILL.md` |
| Benchmark engineering | `plugins/greenit-engineering/skills/benchmark/SKILL.md` |
| Revue GreenIT | `plugins/greenit-engineering/skills/greenit-review/SKILL.md` |

## Installation et prérequis

```bash
cd $BUNDLE_ROOT
uv sync
make validate
make test
```

Outils attendus : Python 3.10+, LibreOffice (`soffice`), `ffmpeg`, `ffprobe`, `pdftoppm`, `pdfinfo`, `pdftotext`, Chromium pour Playwright.

## Mode guidé

Pour un déclenchement un par un, demander à OMP :

```text
Utilise le skill greenit-audit en mode guidé : pose-moi les questions une par une, attends mes réponses, puis appelle le skill suivant. Ne lance pas run_audit.py d’un coup.
```

Séquence : discover-palette → codebase-analysis → greenit-calculations → greenit-norms → greenit-report → greenit-defense → rncp39388 → design-review → content-challenge → sanitize-ai-text.

## Workflow sur un projet réel

### 1. Cadrer

Créer un dossier de travail :

```bash
mkdir -p mon-projet/audit
cp $BUNDLE_ROOT/plugins/greenit-audit/assets/example-audit.yml mon-projet/audit/audit.yml
```

Remplir :

- `project` : nom, client, version, date, auteurs, contexte ;
- `functional_unit` : description, utilisateurs, période, scénarios ;
- `scope` : tiers, étapes, inclusions, exclusions, allocation, mix électrique ;
- `stack` et `hardware` ;
- `constraints` ;
- `inventory.items` : quantités, heures, Go, facteurs, allocation, PUE, source ;
- `assumptions` : H1… avec statut, preuve et impact si faux.

Chaque critère RGESN doit avoir un statut. L’absence de preuve se traduit par `non validé`, jamais par un statut non évalué.

### 2. Valider et calculer

```bash
cd $BUNDLE_ROOT
.venv/bin/python plugins/greenit-audit/scripts/validate_audit.py \
  --input /chemin/mon-projet/audit/audit.yml \
  --factors $BUNDLE_ROOT/plugins/greenit-audit/references/factors.open.csv \
  --factors $BUNDLE_ROOT/plugins/greenit-audit/references/factors.local.example.csv

.venv/bin/python plugins/greenit-audit/scripts/calc.py \
  --input /chemin/mon-projet/audit/audit.yml \
  --factors $BUNDLE_ROOT/plugins/greenit-audit/references/factors.open.csv \
  --factors $BUNDLE_ROOT/plugins/greenit-audit/references/factors.local.example.csv \
  --out /chemin/mon-projet/dist/metrics.json --markdown
```

### 3. Analyser la codebase et le web

Démarrer le serveur applicatif du projet, ou pour la démo `python3 api/server.py --port 8000`, puis utiliser l’URL correspondante.

```bash
.venv/bin/python plugins/greenit-studio/scripts/scan_codebase.py \
  --root /chemin/mon-projet \
  --out /chemin/mon-projet/dist/codebase-audit.json --markdown

.venv/bin/python plugins/greenit-studio/scripts/web_metrics.py \
  --url http://127.0.0.1:8000/ \
  --out /chemin/mon-projet/dist/web-metrics.json --markdown
```

### 4. Évaluer le RGESN

Copier et remplir `examples/demo-service/rgesn-assessment.yml`, puis :

```bash
.venv/bin/python plugins/greenit-audit/scripts/score_rgesn.py \
  --assessment /chemin/mon-projet/audit/rgesn-assessment.yml \
  --out /chemin/mon-projet/dist/rgesn-score.csv \
  --markdown /chemin/mon-projet/dist/rgesn-summary.md
```

Le CSV distingue `status` et `evidence_status`. Le score est calculé sur les statuts ; la couverture des preuves est affichée séparément.

### 5. Construire le pack

`build_audit_pack.py` doit tourner **avant** les rendus : il crée `report.md`, `deck.yml`, `metadata.yml`, `narration.md`, `synthese-client.md`, `hypotheses.csv`, les figures et le dossier RNCP.

```bash
.venv/bin/python plugins/greenit-audit/scripts/build_audit_pack.py \
  --metrics /chemin/mon-projet/dist/metrics.json \
  --web /chemin/mon-projet/dist/web-metrics.json \
  --codebase /chemin/mon-projet/dist/codebase-audit.json \
  --rgesn /chemin/mon-projet/dist/rgesn-score.csv \
  --audit /chemin/mon-projet/audit/audit.yml \
  --out /chemin/mon-projet/dist \
  --figures /chemin/mon-projet/dist/figures \
  --dist /chemin/mon-projet/dist
```

### 6. Rendre les livrables

```bash
# Rapport complet
.venv/bin/python plugins/greenit-studio/scripts/md_to_docx.py \
  --input /chemin/mon-projet/dist/report.md \
  --metadata /chemin/mon-projet/dist/metadata.yml \
  --figures /chemin/mon-projet/dist/figures \
  --out /chemin/mon-projet/dist/rapport.docx --pdf

# Synthèse client
.venv/bin/python plugins/greenit-studio/scripts/md_to_docx.py \
  --input /chemin/mon-projet/dist/synthese-client.md \
  --metadata /chemin/mon-projet/dist/metadata.yml \
  --figures /chemin/mon-projet/dist/figures \
  --out /chemin/mon-projet/dist/synthese-client.docx --pdf

# Soutenance
.venv/bin/python plugins/greenit-studio/scripts/build_deck.py \
  --input /chemin/mon-projet/dist/deck.yml \
  --out /chemin/mon-projet/dist/soutenance.pptx \
  --notes /chemin/mon-projet/dist/notes-orales.md --pdf

# Vidéo
.venv/bin/python plugins/greenit-studio/scripts/build_video.py \
  --deck /chemin/mon-projet/dist/soutenance.pptx \
  --narration /chemin/mon-projet/dist/narration.md \
  --out /chemin/mon-projet/dist/teaser.mp4
```

### 7. Vérifier

```bash
.venv/bin/python scripts/write_manifest.py --dist /chemin/mon-projet/dist
.venv/bin/python scripts/check_outputs.py
.venv/bin/python scripts/check_sources.py
```

## Démonstration complète

```bash
cd $BUNDLE_ROOT
make demo
make check
```

Livrables : rapport, synthèse client, soutenance, vidéo, figures, métriques, dossier RNCP, manifest SHA256.

## Règles dures

- Ne pas inventer de données client.
- Chaque chiffre a une source et une unité.
- Chaque hypothèse a un ID, un statut et un niveau de preuve.
- `sans preuve` n’est pas `conforme` ; le score doit être lu avec la couverture des preuves.
- Ne pas supprimer les limites : les transformer en conditions de validité et plan de collecte.
- Ne pas revendiquer la neutralité carbone ni la compensation.
- La démonstration utilise `factors.local.csv`, ignoré par Git, pour GWP/ADPe/ADPf réseau. `factors.local.example.csv` ne contient que l’en-tête ; aucune valeur NegaOctet n’est publiée.
- Les scripts restent dans le bundle ; OMP lit les SKILL.md et exécute les commandes.

## Sortie attendue

Un audit complet dans son périmètre, avec :

- `audit.yml` validé ;
- `metrics.json` avec GWP/ADPe/ADPf et incertitude ;
- `rgesn-score.csv` avec 78 statuts et `evidence_status` ;
- `report.md`, DOCX, PDF ;
- `synthese-client.md`, DOCX, PDF ;
- `deck.yml`, PPTX, PDF, notes ;
- MP4 et SRT ;
- `hypotheses.csv` ;
- `rncp39388/01…10` ;
- `manifest.json`.
