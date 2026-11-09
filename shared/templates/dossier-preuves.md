# Dossier de preuves RNCP39388

Titre : Responsable green IT (RNCP39388, niveau 6, Efficom).

Chaque compétence est reliée à une preuve existante. Les preuves sont des fichiers du bundle ou des livrables générés dans `dist/`.

## BC01 — Concevoir une solution numérique responsable

### BC01-1 — Conduire une veille socio-environnementale, technologique et réglementaire en réalisant un benchmark des solutions numériques existantes.

- **Preuve** : `shared/docs/08-RESEARCH-NOTES.md`
- **Emplacement** : Veille et benchmark
- **Statut** : validé

### BC01-2 — Effectuer le diagnostic Green IT de l’organisation en cartographiant les ressources, les besoins et les impacts environnementaux.

- **Preuve** : `dist/audit-demo/report.md`
- **Emplacement** : Sections 2, 7 et 8
- **Statut** : validé

### BC01-3 — Organiser le déploiement d’une solution numérique durable et accessible en tenant compte des contraintes technologiques, réglementaires et budgétaires.

- **Preuve** : `shared/docs/07-USAGE.md`
- **Emplacement** : Déploiement et contraintes
- **Statut** : validé

### BC01-4 — Définir les spécifications techniques du système informatique durable selon les normes d’écoconception, les ressources, les coûts et l’obsolescence.

- **Preuve** : `examples/demo-service/audit.yml`
- **Emplacement** : UF, périmètre, inventaire
- **Statut** : validé

## BC02 — Déployer un système informatique responsable

### BC02-1 — Installer et configurer un Système d’Information Développement Durable (SIDD) en privilégiant les infrastructures green et leur compatibilité.

- **Preuve** : `examples/demo-service/README.md`
- **Emplacement** : Architecture du service de démonstration
- **Statut** : validé

### BC02-2 — Développer des applications et des outils métiers responsables et accessibles, adaptables et testés avec les utilisateurs.

- **Preuve** : `dist/audit-demo/codebase-audit.md`
- **Emplacement** : Diagnostic frontend/backend
- **Statut** : validé

### BC02-3 — Garantir l’évolutivité du SIDD en intégrant des tests, en contrôlant l’adaptation en production et en corrigeant.

- **Preuve** : `tests/`
- **Emplacement** : Tests de non-régression et de bout en bout
- **Statut** : validé

### BC02-4 — Mettre en place des solutions d’automatisation et de virtualisation du SIDD en respectant l’écoconception et la maintenabilité.

- **Preuve** : `scripts/optimize_demo.py`
- **Emplacement** : Optimisation automatisée de la démo
- **Statut** : validé

### BC02-5 — Assurer la stabilité et la pérennité du système informatique avec supervision, mesure des coûts et maintenance.

- **Preuve** : `shared/docs/07-USAGE.md`
- **Emplacement** : Supervision et maintenance
- **Statut** : validé

## BC03 — Maintenir un système informatique responsable

### BC03-1 — Réduire la surface d’attaque du SI en restreignant les vulnérabilités, en contrôlant la durée de vie des données et en ajustant les flux.

- **Preuve** : `plugins/greenit-engineering/references/greenit-code-checklist.md`
- **Emplacement** : Sécurité et minimisation
- **Statut** : validé

### BC03-2 — Gérer le versionning, documenter la solution, choisir des sauvegardes et sécuriser les données conformément au Green et Fair IT.

- **Preuve** : `shared/docs/10-CHANGELOG.md`
- **Emplacement** : Versionning et documentation
- **Statut** : validé

### BC03-3 — Analyser la consommation énergétique des infrastructures avec des outils de supervision pour identifier les pics et incidents.

- **Preuve** : `dist/audit-demo/metrics.json`
- **Emplacement** : Indicateurs et hotspots
- **Statut** : validé

### BC03-4 — Élaborer des recommandations d’économie d’énergie tenant compte du cadre réglementaire et des évolutions technologiques.

- **Preuve** : `dist/audit-demo/report.md`
- **Emplacement** : Plan d’action et gains
- **Statut** : validé

### BC03-5 — Encadrer les pratiques professionnelles numériques : privilèges, alertes, charte numérique responsable et événements Green IT.

- **Preuve** : `shared/templates/charter.md`
- **Emplacement** : Charte et gouvernance
- **Statut** : validé

## BC04 — Conduire un projet numérique responsable

### BC04-1 — Planifier le développement d’un projet Green IT : étapes, ressources matérielles, technologiques et humaines, budget et délais.

- **Preuve** : `shared/templates/project-plan.md`
- **Emplacement** : Plan projet et RACI
- **Statut** : validé

### BC04-2 — Coordonner l’activité des équipes projet avec des outils collaboratifs accessibles pour suivre l’avancement et optimiser les échanges.

- **Preuve** : `shared/templates/raci.csv`
- **Emplacement** : RACI et rituels
- **Statut** : validé

### BC04-3 — Participer à la formation des équipes techniques aux normes d’écoconception, à la réglementation et aux calculs d’impact.

- **Preuve** : `dist/rncp39388/09-formation-greenit.md`
- **Emplacement** : Formation 10 slides, quiz, exercice
- **Statut** : validé

### BC04-4 — Réaliser le suivi et la livraison du projet avec un pilotage des échéances et un contrôle de conformité Green IT.

- **Preuve** : `dist/rncp39388/03-checklist-livrables.md`
- **Emplacement** : Checklist et critères d’acceptation
- **Statut** : validé

### BC04-5 — Formaliser un bilan de projet, recenser les actions et problématiques, identifier les axes d’amélioration.

- **Preuve** : `dist/rncp39388/10-retrospective.md`
- **Emplacement** : Rétrospective et capitalisation
- **Statut** : validé
