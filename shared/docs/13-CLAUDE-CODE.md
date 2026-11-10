# Utilisation dans Claude Code

## Installation effectuée

Le marketplace local est ajouté et le plugin principal est installé au scope utilisateur :

```text
greenit-rncp39388
  greenit-audit       0.1.2  (7 skills)
  greenit-studio      0.1.2  (5 skills, dépendance)
  greenit-engineering 0.1.2  (6 skills, dépendance)
greenit-reviewer    0.1.2  (4 skills, 1 agent)
```

Vérifier :

```bash
claude plugin list
claude plugin marketplace list
claude plugin details greenit-audit
claude plugin details greenit-studio
claude plugin details greenit-engineering
```

Le plugin est installé depuis :

```text
$BUNDLE_ROOT
```

## Préparer l’environnement Python

Les skills appellent `python3`. Pour que `python-pptx`, `docx`, `playwright` et les autres dépendances soient disponibles, activer le venv du bundle avant de lancer Claude Code :

```bash
export PATH="$BUNDLE_ROOT/.venv/bin:$PATH"
```

Ou, pour une session :

```bash
cd $BUNDLE_ROOT
source .venv/bin/activate
claude
```

Sans cela, les calculs peuvent fonctionner mais la génération PPTX peut échouer faute de `python-pptx`.

## Lancer Claude Code sur un projet

```bash
cd /chemin/mon-projet
export PATH="$BUNDLE_ROOT/.venv/bin:$PATH"
claude
```

Le plugin est au scope utilisateur : il est disponible dans tous les projets. Après une modification des fichiers du plugin, exécuter `/reload-plugins` ou démarrer une nouvelle session Claude Code.

## Invocation explicite

Les skills de plugin sont namespaceés. Utiliser :

```text
/greenit-audit:greenit-audit
```

Les autres skills :

```text
/greenit-audit:greenit-calculations
/greenit-audit:greenit-norms
/greenit-audit:greenit-report
/greenit-audit:greenit-defense
/greenit-audit:greenit-benchmark
/greenit-audit:rncp39388

/greenit-studio:codebase-analysis
/greenit-studio:docx-report
/greenit-studio:pptx-deck
/greenit-studio:video-pitch
/greenit-studio:images-charts

/greenit-engineering:refactor
/greenit-engineering:fix
/greenit-engineering:proposal
/greenit-engineering:brainstorm
/greenit-engineering:benchmark
/greenit-engineering:greenit-review
/greenit-reviewer:design-review
/greenit-reviewer:content-challenge
/greenit-reviewer:sanitize-ai-text
/greenit-reviewer:discover-palette
```

Certains skills ont `disable-model-invocation: true` : ils doivent être appelés explicitement, pas déclenchés par une phrase vague.

## Workflow projet

### 1. Créer le dossier d’audit

```bash
mkdir -p audit dist
cp $BUNDLE_ROOT/plugins/greenit-audit/assets/example-audit.yml audit/audit.yml
cp $BUNDLE_ROOT/examples/demo-service/rgesn-assessment.yml audit/rgesn-assessment.yml
```

### 2. Remplir audit.yml

Renseigner projet, UF, scénarios, périmètre, stack, matériel, contraintes, inventaire, hypothèses.

### 3. Démarrer le serveur

Pour la démonstration :

```bash
cd /chemin/mon-projet
python3 api/server.py --port 8000
```

Pour un site statique :

```bash
cd /chemin/mon-projet/web
python3 -m http.server 8000
```

Pour une application réelle, lancer son serveur habituel. L’URL passée à `--url` doit pointer vers la page applicative, pas vers un listing de répertoire.

### 4. Invoquer l’orchestrateur

```text
/greenit-audit:greenit-audit
```

Puis préciser :

```text
Le projet est dans /chemin/mon-projet.
L’audit est dans audit/audit.yml.
La codebase est dans /chemin/mon-projet.
L’URL locale est http://127.0.0.1:8000/.
Exécute le workflow complet et produis les livrables dans dist/.
```

Le skill appelle `scripts/run_audit.py` avec les chemins du projet. Il exécute :

1. validation `audit.yml` ;
2. scan de la codebase ;
3. mesure web ;
4. calculs GWP/ADPe/ADPf ;
5. score RGESN ;
6. `build_audit_pack` : `report.md`, `deck.yml`, `metadata.yml`, `narration.md`, `synthese-client.md`, `hypotheses.csv`, figures, dossier RNCP ;
7. rapport DOCX/PDF ;
8. synthèse client DOCX/PDF ;
9. PPTX/PDF + notes ;
10. MP4/SRT ;
11. manifest SHA256.

Commande directe équivalente :

```bash
export CLAUDE_PLUGIN_ROOT=$BUNDLE_ROOT/plugins/greenit-audit
python3 "${CLAUDE_PLUGIN_ROOT}/../../scripts/run_audit.py" \
  --project /chemin/mon-projet \
  --audit /chemin/mon-projet/audit/audit.yml \
  --assessment /chemin/mon-projet/audit/rgesn-assessment.yml \
  --url http://127.0.0.1:8000/ \
  --out /chemin/mon-projet/dist
```

### 5. Vérifier

```bash
claude plugin list
ls -lh dist/
```

Les sorties attendues :

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

## Cas d’usage ciblés

### Audit complet

```text
/greenit-audit:greenit-audit
```

### Calculs seuls

```text
/greenit-audit:greenit-calculations
```

### Rapport à partir de résultats existants

```text
/greenit-audit:greenit-report
/greenit-studio:docx-report
```

### Soutenance

```text
/greenit-audit:greenit-defense
/greenit-studio:pptx-deck
/greenit-studio:video-pitch
```

### Revue de code

```text
/greenit-engineering:greenit-review
/greenit-reviewer:design-review
/greenit-reviewer:content-challenge
/greenit-reviewer:sanitize-ai-text
/greenit-reviewer:discover-palette
```

### Refactor ou correctif

```text
/greenit-engineering:refactor
/greenit-engineering:fix
```

### Dossier RNCP39388

```text
/greenit-audit:rncp39388
```

## Désinstallation

```bash
claude plugin uninstall greenit-audit --scope user
claude plugin marketplace remove greenit-rncp39388
```

Les dépendances `greenit-studio` et `greenit-engineering` sont retirées avec le plugin principal.

## Dépannage

- Skill absent : redémarrer Claude Code après l’installation.
- `python-pptx` absent : activer le `.venv` du bundle ou `uv sync`.
- Playwright sans navigateur : `CHROMIUM_PATH=/usr/bin/chromium`.
- PDF absent : vérifier `soffice`.
- Vidéo absente : vérifier `ffmpeg` et `pdftoppm`.
- Facteur NegaOctet : exemple local non diffusable ; remplacer pour publication.
