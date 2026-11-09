# Collecte de données — méthodes légitimes

Objectif : réduire les hypothèses sans inventer de chiffres. Chaque donnée collectée doit avoir une source, une date, un périmètre et un niveau de confiance.

## Serveur et hébergement

- Fiche fournisseur ou facture : modèle, CPU, RAM, disques, année.
- API ou portail de l’hébergeur : instance, région, PUE, WUE, mix électrique.
- Inventaire interne : hyperviseur, CMDB, `dmidecode`/`lscpu` avec autorisation.
- Facture d’électricité : kWh, puissance souscrite, PUE si disponible.
- À défaut : profil Boavizta explicite + scénarios bas/base/haut.

## Usages

- Logs serveur ou reverse proxy : requêtes, volumes, durées.
- Analytics respectueux de la vie privée : pages vues, sessions, appareils.
- Entretiens ou observation : durée d’une tâche, nombre d’émargements.
- Échantillonnage : une semaine représentative, puis extrapolation documentée.
- Ne pas collecter de données personnelles inutiles ; minimiser et agréger.

## Réseau

- `performance.getEntriesByType('resource')` : octets transférés, requêtes.
- Logs CDN ou serveur : volume par région, cache hit.
- Mesure Playwright : page réelle, cache désactivé, viewport fixe.
- Facteur ouvert Green Coding : 0,04106063 kWh/Go, à multiplier par l’intensité carbone.
- ADPe/ADPf réseau : utiliser un facteur documenté. La démonstration utilise le facteur local NegaOctet pour les trois indicateurs.

## Développement et maintenance

- Historique Git : commits, périodes, auteurs (agrégé).
- Timesheets ou outil de gestion de projet.
- Vélocité d’équipe : heures par story, nombre de releases.
- Entretiens : temps de revue, de test, de déploiement.
- Ne pas convertir les lignes de code en heures sans coefficient validé.

## Fin de vie

- Fiche produit ou éco-organisme : filière, taux de collecte, traitement.
- Facteur ADEME/Base Empreinte ou étude ACV documentée.
- À défaut : exclure explicitement et expliquer pourquoi.

## Règle de triangulation

1. Privilégier une mesure directe.
2. Sinon, utiliser une donnée fournisseur.
3. Sinon, utiliser un facteur public daté.
4. Sinon, poser une hypothèse avec fourchette et scénario.
5. Toujours écrire : mesuré, estimé, supposé.

## Interdits

- Inventer une facture, un PUE ou un volume.
- Modifier une source pour qu’elle confirme la conclusion.
- Supprimer une limite gênante.
- Présenter une estimation comme une mesure.
- Utiliser la compensation pour masquer une absence de réduction.
