# Utilisation dans OMP

Le bundle est exposé dans OMP par un skill managé unique :

```text
~/.omp/agent/managed-skills/greenit-rncp39388/SKILL.md
```

Ce skill d’orchestration contient la carte des 22 skills du bundle et les commandes absolues. Les skills détaillés restent dans :

```text
$BUNDLE_ROOT/plugins/*/skills/*/SKILL.md
```

## Invocation

Demander à OMP d’utiliser le skill `greenit-rncp39388`, par exemple :

```text
Utilise greenit-rncp39388 sur /chemin/mon-projet.
Crée audit.yml à partir de l’exemple, fais valider les données, calcule les impacts,
évalue les 78 critères RGESN, puis génère le rapport, le deck et la vidéo.
```

## Préparation d’un projet

```bash
cd $BUNDLE_ROOT
uv sync
mkdir -p /chemin/mon-projet/audit
cp plugins/greenit-audit/assets/example-audit.yml /chemin/mon-projet/audit/audit.yml
cp examples/demo-service/rgesn-assessment.yml /chemin/mon-projet/audit/rgesn-assessment.yml
```

Remplir `audit.yml` : projet, unité fonctionnelle, scénarios, périmètre, stack, matériel, contraintes, inventaire, hypothèses.

## Sorties

Le workflow produit :

- `metrics.json` : GWP100, ADPe, ADPf, hotspots, incertitude ;
- `codebase-audit.json` : signaux techniques ;
- `web-metrics.json` : DOM, requêtes, octets, cache, EcoIndex ;
- `rgesn-score.csv` : 78 statuts + `evidence_status` ;
- `hypotheses.csv` : statuts, preuve, owner, échéance ;
- `report.md`, DOCX, PDF ;
- `synthese-client.md`, DOCX, PDF ;
- `deck.yml`, PPTX, PDF, notes orales ;
- MP4 + SRT ;
- dossier `rncp39388/` ;
- `manifest.json`.

## Ordre impératif

1. `build_audit_pack.py` : crée `report.md`, `deck.yml`, `metadata.yml`, `narration.md`, `synthese-client.md`, `hypotheses.csv`, les figures et le dossier RNCP.
2. `md_to_docx.py` sur `report.md` : rapport DOCX/PDF.
3. `md_to_docx.py` sur `synthese-client.md` : synthèse client DOCX/PDF.
4. `build_deck.py` : PPTX/PDF + notes.
5. `build_video.py` : MP4 + SRT.
6. `check_outputs.py` et `check_sources.py`.

Ne jamais lancer les rendus avant l’étape 1 : les fichiers d’entrée n’existent pas encore.

## Point d’attention

La démonstration utilise `factors.local.example.csv` (NegaOctet) pour évaluer GWP/ADPe/ADPf réseau. Ce fichier est un exemple local non redistribuable. Pour un rapport public, remplacer ce facteur par une source sous licence compatible.

Le score RGESN est calculé sur les statuts ; la couverture des preuves est affichée séparément. Un score de 15/100 avec 100 % de statuts et 39,6 % de preuves est **non significatif** : les 42 critères sans preuve sont comptés comme non validés, pas comme conformes.

## Mode guidé OMP

Dans OMP, il n’y a pas de slash-command `plugin:skill`. Demander :

```text
Utilise le skill greenit-audit en mode guidé : pose-moi les questions une par une, attends mes réponses, puis appelle le skill suivant. Ne lance pas run_audit.py d’un coup.
```

Ou :

```text
Utilise greenit-rncp39388 en mode guidé pour auditer /chemin/mon-projet. Commence par me demander quels blocs RNCP auditer.
```

Questions : blocs RNCP, racine projet, UF, frontières, stack/hardware, données, niveau de preuve, livrables.

Séquence : discover-palette → codebase-analysis → greenit-calculations → greenit-norms → greenit-report → greenit-defense → rncp39388 → design-review → content-challenge → sanitize-ai-text.
