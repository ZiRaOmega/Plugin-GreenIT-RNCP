# Service d’émargement — démonstration

Service web fictif utilisé par le bundle pour prouver qu’un audit GreenIT complet peut être produit de bout en bout. Il permet à 100 étudiants de s’émarger et à un membre du staff de consulter les présences pendant une semaine.

## Lancement

```bash
python api/server.py --port 8765
```

Ouvrir `http://127.0.0.1:8765/`.

## Perfections volontaires

Le code contient des défauts mesurables : image PNG lourde, CSS dupliqué, JS non minifié, `console.log`, polling toutes les 5 s, `innerHTML`, `SELECT *`, absence d’index, CORS `*`, secret factice, `alt` manquant, `target="_blank"` sans `rel`.

Aucun secret réel n’est présent. Le code est conçu pour être optimisé par `scripts/optimize_demo.py` et mesuré avant/après.

## Limites

Ce service n’est pas un produit de production. Il ne représente pas un vrai système d’information et ne contient pas de données personnelles réelles.
