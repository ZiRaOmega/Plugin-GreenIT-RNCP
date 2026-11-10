---
name: greenit-audit
description: Orchestre un audit GreenIT complet depuis le cadrage jusqu’aux livrables et aux preuves RNCP39388.
argument-hint: "<projet> [blocs BC01,BC04] [url] [audit.yml] [rgesn-assessment.yml]"
disable-model-invocation: true
---

# Orchestrer un audit GreenIT

## Question obligatoire

**Avant de lancer l’audit, demander : « Quels blocs RNCP faut-il auditer ? »**

Exemples :

- `BC01 et BC04` — conception et conduite de projet ;
- `BC02 et BC03` — déploiement et maintenance ;
- `BC01, BC02, BC03, BC04` — audit complet.

Ne pas supposer « tous les blocs ». Reporter la réponse dans `--blocks`.


## Commande unique

Le script `run_audit.py` exécute le workflow complet : validation, scan, mesure web, calculs, score RGESN, `build_audit_pack`, rapport, synthèse client, deck, vidéo et manifest.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/../../scripts/run_audit.py" \
  --project /chemin/mon-projet \
  --audit /chemin/mon-projet/audit/audit.yml \
  --assessment /chemin/mon-projet/audit/rgesn-assessment.yml \
  --url http://127.0.0.1:8000/ \
  --blocks BC01,BC04 \
  --out /chemin/mon-projet/dist
```

- `--project` : racine de la codebase.
- `--audit` : fichier `audit.yml`.
- `--assessment` : fichier `rgesn-assessment.yml`.
- `--url` : URL locale du service. Omettre si aucun serveur web n’est disponible ; les métriques web seront alors absentes.
- `--out` : dossier des livrables.
- `--blocks` : blocs RNCP à auditer (`BC01,BC04`, `BC02,BC03`, etc.). Demander la réponse à l’utilisateur avant de lancer.
- Les facteurs sont résolus automatiquement depuis le bundle : `factors.open.csv` et `factors.local.example.csv`.

## Démarrer le serveur local

Pour la démonstration fournie :

```bash
cd /chemin/mon-projet
python3 api/server.py --port 8000
```

Pour un site statique :

```bash
cd /chemin/mon-projet/web
python3 -m http.server 8000
```

Pour une application réelle : lancer son serveur habituel, puis passer son URL à `--url`. Ne pas mesurer un listing de répertoire à la place de la page applicative.

## Séquence exécutée

1. `validate_audit.py` : schéma, facteurs, sources.
2. `scan_codebase.py` : signaux statiques.
3. `web_metrics.py` : DOM, requêtes, octets, cache, EcoIndex.
4. `calc.py` : GWP100, ADPe, ADPf.
5. `score_rgesn.py` : 78 statuts + `evidence_status`.
6. `build_audit_pack.py` : `report.md`, `deck.yml`, `metadata.yml`, `narration.md`, `synthese-client.md`, `hypotheses.csv`, figures, dossier RNCP.
7. `md_to_docx.py` : rapport DOCX/PDF.
8. `md_to_docx.py` : synthèse client DOCX/PDF.
9. `build_deck.py` : PPTX/PDF + notes.
10. `build_video.py` : MP4 + SRT.
11. `write_manifest.py` : SHA256.

## Inputs

Créer `audit.yml` et `rgesn-assessment.yml` à partir de :

```text
${CLAUDE_PLUGIN_ROOT}/assets/example-audit.yml
${CLAUDE_PLUGIN_ROOT}/../../examples/demo-service/rgesn-assessment.yml
```

Les chemins peuvent être à la racine du projet ou dans `audit/` ; il faut alors les passer explicitement à `--audit` et `--assessment`.

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

## Skills spécialisés

Après le workflow, utiliser si besoin :

- `/greenit-audit:greenit-calculations` ;
- `/greenit-audit:greenit-norms` ;
- `/greenit-audit:greenit-report` ;
- `/greenit-audit:greenit-defense` ;
- `/greenit-audit:greenit-benchmark` ;
- `/greenit-audit:rncp39388` ;
- `/greenit-studio:docx-report`, `/greenit-studio:pptx-deck`, `/greenit-studio:video-pitch` ;
- `/greenit-engineering:brainstorm`, `/greenit-engineering:greenit-review`.

## Règles dures

- Aucun chiffre sans `[Sxx]`.
- Aucune hypothèse sans `Hxx`.
- Aucun terme non défini dans le glossaire.
- Distinguer mesuré / estimé / supposé.
- Ne pas additionner des gains qui se recouvrent.
- Ne pas écrire « compensation », « neutre en carbone », « 100 % vert » comme revendication.
- Signaler l’effet rebond et les limites.
- Le fichier `factors.local.example.csv` contient des valeurs NegaOctet non diffusable ; pour un rapport public, le remplacer par un facteur sous licence compatible.
