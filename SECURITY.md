# Security policy

## Secrets

Le dépôt public ne contient pas de secret réel :

- le secret factice de la démo a été retiré ;
- `factors.local.csv` est ignoré par Git ;
- `dist/`, `.venv/`, `build/`, `*.db`, `*.local.csv` et les vidéos générées sont ignorés ;
- les chemins personnels ont été remplacés par `$BUNDLE_ROOT` ou `$HOME`.

Avant chaque publication :

```bash
git grep -nE 'AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|password[[:space:]]*[:=][[:space:]]*["'"']|api[_-]?key[[:space:]]*[:=][[:space:]]*["'"']|token[[:space:]]*[:=][[:space:]]*["'"']' || true
```

## Signaler une vulnérabilité

Contacter **ZiRaOmega** en privé. Ne pas ouvrir d’issue publique contenant un exploit ou une donnée sensible.

## Avertissement légal

Voir `README.md` et `LICENSE`. Toute utilisation non autorisée peut entraîner des poursuites civiles et pénales.

## Licence

Le dépôt est en consultation seule. Voir `LICENSE`. La présence d’instructions d’installation ne constitue pas une autorisation d’usage.
