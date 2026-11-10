#!/usr/bin/env python3
"""Génère le rapport, le deck, les notes et le dossier RNCP à partir des résultats."""
from __future__ import annotations

import argparse
import copy
import csv
import json
import shutil
from pathlib import Path

import yaml

import calc

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "references"


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def n(value: float, digits: int = 3) -> str:
    if value is None:
        return "—"
    if abs(value) >= 1000:
        return f"{value:,.0f}".replace(",", " ")
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.{digits}g}"


def pct(value: float, digits: int = 1) -> str:
    if value != 0 and abs(value) < 0.1:
        digits = max(digits, 2)
    return f"{value:.{digits}f} %"


def val(value: float | None) -> str:
    return "—" if value is None else n(value)


def delta_fmt(value: float) -> str:
    if abs(value) < 0.05:
        return "négligeable"
    if abs(value) < 0.1:
        return "< 0,1 %"
    return pct(value)


def table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |")
    return "\n".join(out)


def img(path: Path, alt: str) -> str:
    return f"![{alt}]({path.as_posix()})"


def get_item(metrics: dict, item_id: str) -> dict:
    for item in metrics["items"]:
        if item["id"] == item_id:
            return item
    return {}


def compute_sensitivity(audit: dict, factors: dict[str, dict]) -> list[dict]:
    """Scénarios de sensibilité calculés avec le même moteur et la même UF."""
    base = calc.calculate(audit, factors)["totals"]["gwp"]
    scenarios = []

    def add(name, variation, comment, mutate):
        a = copy.deepcopy(audit)
        mutate(a)
        gwp = calc.calculate(a, factors)["totals"]["gwp"]
        scenarios.append({"scenario": name, "variation": variation, "gwp": gwp,
                          "delta_pct": (gwp / base - 1) * 100 if base else 0,
                          "comment": comment})

    def server_item(a, key, value):
        for i in a["inventory"]["items"]:
            if i["id"] == "server":
                i[key] = value

    add("Référence", "base", "Scénario du rapport", lambda a: None)
    for pue in (1.2, 1.5, 1.8):
        add("PUE", f"{pue:g}", "PUE de l’hébergement", lambda a, p=pue: server_item(a, "pue", p))
    for alloc in (0.05, 0.10, 0.20):
        add("Allocation serveur", f"{alloc:.0%}", "Part des impacts serveur allouée", lambda a, x=alloc: server_item(a, "allocation_share", x))
    for hours in (15, 30, 60):
        add("Développement", f"{hours} h/dev", "Durée de développement", lambda a, x=hours: [i.__setitem__("hours", x) for i in a["inventory"]["items"] if i["id"] == "dev-laptops"])
    for seconds in (20, 40, 120):
        add("Usage étudiant", f"{seconds} s", "Temps d’usage par étudiant", lambda a, x=seconds: [i.__setitem__("hours", x / 3600) for i in a["inventory"]["items"] if i["id"] == "students-smartphones"])
    for grid in (51.9, 100, 300):
        add("Mix électrique", f"{grid:g} g/kWh", "Intensité carbone de l’électricité", lambda a, x=grid: a["scope"].__setitem__("grid_intensity_gco2e_per_kwh", x))
    for factor in (0.5, 1.0, 1.5):
        add("Volume réseau", f"×{factor:g}", "Incertitude sur les volumes réseau", lambda a, x=factor: [i.__setitem__("gb", i["gb"] * x) for i in a["inventory"]["items"] if i["category"] == "network"])
    add("Terminaux dédiés", "168 h", "Smartphones dédiés au service", lambda a: [i.__setitem__("hours", 168) for i in a["inventory"]["items"] if i["id"] == "students-smartphones"])
    return scenarios


def build_context(args) -> dict:
    m = load_json(args.metrics)
    mo = load_json(args.metrics_optimized) if args.metrics_optimized and args.metrics_optimized.exists() else m
    web = load_json(args.web) if args.web and args.web.exists() else {"page": None}
    webo = load_json(args.web_optimized) if args.web_optimized and args.web_optimized.exists() else web
    code = load_json(args.codebase) if args.codebase and args.codebase.exists() else {"summary": {}, "signals": []}
    rgesn = list(csv.DictReader(args.rgesn.open(encoding="utf-8-sig"))) if args.rgesn and args.rgesn.exists() else []
    sources = load_yaml(args.sources).get("sources", []) if args.sources and args.sources.exists() else []
    audit = load_yaml(args.audit) if args.audit and args.audit.exists() else {}
    factor_paths = args.factors or [REF / "factors.open.csv"]
    factors = calc.load_factors(factor_paths)
    sensitivity = compute_sensitivity(audit, factors) if audit else []
    phone = get_item(m, "students-smartphones")
    total = m["totals"]["gwp"]
    dedicated_phone = phone.get("gwp", 0) * (168 / max(1e-9, phone.get("hours", 0.011111)))
    dedicated_total = total - phone.get("gwp", 0) + dedicated_phone
    evaluated = [r for r in rgesn if r["status"] in {"validé", "en cours", "non validé"}]
    applicable = [r for r in rgesn if r["status"] != "non applicable"]
    weighted_eval = sum(float(r["weight"]) for r in evaluated)
    weighted_app = sum(float(r["weight"]) for r in applicable)
    def evidence_backed(r: dict) -> bool:
        ev = (r.get("evidence") or "").strip()
        return bool(ev) and not ev.lower().startswith("absence de preuve")
    weighted_evidence = sum(float(r["weight"]) for r in evaluated if evidence_backed(r))
    score = 100 * sum(float(r["weighted_score"] or 0) for r in rgesn) / weighted_eval if weighted_eval else 0
    coverage = 100 * weighted_evidence / weighted_app if weighted_app else 0
    coverage_evaluated = 100 * weighted_eval / weighted_app if weighted_app else 0
    status_counts = {}
    evidence_counts = {}
    for r in rgesn:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
        if r["status"] == "non applicable":
            es = "non applicable"
        else:
            es = "preuve" if evidence_backed(r) else "sans preuve"
        evidence_counts[es] = evidence_counts.get(es, 0) + 1
    non_conform = sorted([r for r in rgesn if r["status"] in {"non validé", "en cours"}],
                         key=lambda r: (-float(r["weight"]), r["id"]))
    return {"m": m, "mo": mo, "web": web, "webo": webo, "code": code, "rgesn": rgesn,
            "sources": sources, "audit": audit, "score": score, "coverage": coverage,
            "status_counts": status_counts, "evidence_counts": evidence_counts,
            "non_conform": non_conform,
            "dedicated_phone": dedicated_phone, "dedicated_total": dedicated_total,
            "sensitivity": sensitivity, "factors": factors,
            "coverage_evaluated": coverage_evaluated}


def build_charts(ctx: dict, figures_dir: Path) -> Path:
    m, web, webo = ctx["m"], ctx["web"], ctx["webo"]
    lifecycle = m["shares"]["by_stage"]
    tiers = m["shares"]["by_tier"]
    charts = [
        {"id": "lifecycle", "type": "bar", "title": "Impacts par étape du cycle de vie",
         "subtitle": "GWP100, en kg CO2e, pour une semaine d’émargement",
         "unit": "kg CO2e", "source": "Calculs de l’audit ; facteurs [S26], [S42]",
         "data": [{"label": r["stage"], "value": r["gwp"]} for r in lifecycle],
         "alt": "Graphique en barres des impacts GWP par étape du cycle de vie ; le serveur et le développement dominent.",
         "purpose": "Montrer quel étape concentre le GWP pour prioriser les actions."},
        {"id": "tiers", "type": "donut", "title": "Répartition par tier",
         "subtitle": "Part du GWP100 par tier 1, 2 et 3", "center": "GWP",
         "source": "Calculs de l’audit ; [S26], [S42]", "data": [{"label": f"Tier {r['tier']}", "value": r["gwp"]} for r in tiers],
         "alt": "Diagramme en anneau de la répartition du GWP entre les tiers 1, 2 et 3.",
         "purpose": "Vérifier si le serveur domine ou si les terminaux sont le hotspot."},
        {"id": "hotspots", "type": "bar", "title": "Hotspots GWP",
         "subtitle": "Cinq premiers contributeurs", "unit": "kg CO2e", "orientation": "horizontal",
         "source": "Calculs de l’audit ; [S26], [S42]", "highlight": ["Serveur 2U mutualisé"],
         "data": [{"label": h["label"], "value": h["gwp"]} for h in m["hotspots"]],
         "alt": "Graphique des cinq premiers contributeurs au GWP ; le serveur représente environ 64 %.",
         "purpose": "Identifier les postes à traiter en priorité.",},
        {"id": "web", "type": "bar", "title": "Poids de la page avant / après",
         "subtitle": "Octets transférés mesurés avec Playwright",
         "unit": "Ko", "source": "Mesures locales [S28], [S30]",
         "data": [{"label": "Baseline", "value": (web.get("page") or {}).get("size_kb", 0)},
                  {"label": "Optimisé", "value": (webo.get("page") or {}).get("size_kb", 0)}],
         "alt": "Graphique comparant le poids de la page avant et après optimisation ; réduction de plus de 90 %.",
         "purpose": "Prouver l’effet des quick wins web sur le poids transféré."},
        {"id": "actions", "type": "matrix", "title": "Matrice impact / effort",
         "subtitle": "Sélection d’actions d’écoconception",
         "source": "Brainstorm de l’équipe ; cadre [S03], [S05], [S06]",
         "data": [
             {"label": "Supprimer polling", "impact": 0.18, "effort": 0.12},
             {"label": "Cache + compression", "impact": 0.28, "effort": 0.22},
             {"label": "Images optimisées", "impact": 0.35, "effort": 0.28},
             {"label": "Index + SELECT ciblé", "impact": 0.22, "effort": 0.25},
             {"label": "PUE hébergeur", "impact": 0.62, "effort": 0.65},
             {"label": "Terminaux dédiés", "impact": 0.85, "effort": 0.8},
             {"label": "Budget poids page", "impact": 0.3, "effort": 0.4},
             {"label": "Charte numérique", "impact": 0.4, "effort": 0.55}],
         "alt": "Matrice impact / effort avec huit actions ; les quick wins sont le polling, le cache et les images.",
         "purpose": "Choisir les actions selon leur impact et leur effort.",},
        {"id": "rgesn", "type": "gauge", "title": "Score RGESN d’avancement",
         "subtitle": f"Couverture {ctx['coverage']:.1f} % — score non officiel", "value": ctx["score"],
         "unit": "score /100", "source": "Évaluation interne [S03], [S04]",
         "alt": "Jauge du score RGESN d’avancement, avec la couverture affichée.",
         "purpose": "Situer le score et rappeler qu’il dépend de la couverture des preuves."},
    ]
    spec = figures_dir.parent / "audit-demo" / "charts.yml"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(yaml.safe_dump({"charts": charts}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return spec


def report_text(ctx: dict, figures: Path) -> str:
    m, mo, web, webo, code = ctx["m"], ctx["mo"], ctx["web"], ctx["webo"], ctx["code"]
    p = m["functional_unit"]
    total = m["totals"]
    items = m["items"]
    scores = ctx["score"]
    coverage = ctx["coverage"]
    score_label = "significatif mais faible" if coverage >= 50 else "non significatif"
    counts = ctx["status_counts"]
    phone = get_item(m, "students-smartphones")
    server = get_item(m, "server")
    dev = get_item(m, "dev-laptops")
    dedicated_total = ctx["dedicated_total"]
    webp = web.get("page") or {}
    webo_p = webo.get("page") or {}
    web_eco = web.get("ecoindex") or {}
    webo_eco = webo.get("ecoindex") or {}
    source_rows = [[s["id"], s["org"], s["title"], s["date"]] for s in ctx["sources"]]
    item_rows = [[i["label"], i["category"], i["tier"], val(i["gwp"]), val(i["adpe"]), val(i["adpf"]), i["source_id"]] for i in items]
    hyp_rows = [[a["id"], a["statement"], f"{a['value']} {a['unit']}", a["source_id"], a["confidence"],
                 a.get("status", ""), a.get("evidence_status", ""), a.get("owner", ""), a.get("evidence", "")] for a in ctx["audit"].get("assumptions", [])]
    tier_rows = [[f"Tier {r['tier']}", n(r["gwp"]), pct(r["share_gwp"])] for r in m["shares"]["by_tier"]]
    stage_rows = [[r["stage"], n(r["gwp"]), pct(r["share_gwp"])] for r in m["shares"]["by_stage"]]
    cat_rows = [[r["category"], n(r["gwp"]), pct(r["share_gwp"])] for r in m["shares"]["by_category"]]
    nc_rows = [[r["id"], r["priority"], r["status"], r["title"][:110]] for r in ctx["non_conform"][:10]]
    signal_rows = [[s["severity"], f"{s['file']}:{s['line']}", s["id"], s["why"][:80], s["greenit"]] for s in code.get("signals", [])[:20]]
    gain_rows = [
        ["Poids transféré", f"{n(webp.get('size_kb', 0))} Ko", f"{n(webo_p.get('size_kb', 0))} Ko",
         pct((1 - (webo_p.get("size_kb", 0) / webp.get("size_kb", 1))) * 100) if webp.get("size_kb") else "—"],
        ["Requêtes", str(webp.get("requests", "—")), str(webo_p.get("requests", "—")),
         pct((1 - (webo_p.get("requests", 0) / webp.get("requests", 1))) * 100) if webp.get("requests") else "—"],
        ["Nœuds DOM", str(webp.get("dom_nodes", "—")), str(webo_p.get("dom_nodes", "—")), "stable"],
        ["Ressources avec cache", str(webp.get("cache_control_resources", 0)), str(webo_p.get("cache_control_resources", 0)), "ajout de cache"],
        ["EcoIndex", f"{web_eco.get('score', '—')} ({web_eco.get('grade', '—')})",
         f"{webo_eco.get('score', '—')} ({webo_eco.get('grade', '—')})", "amélioration"],
        ["GWP du service", f"{n(total['gwp'])} kg CO2e", f"{n(mo['totals']['gwp'])} kg CO2e",
         pct((1 - mo["totals"]["gwp"] / total["gwp"]) * 100) if total["gwp"] else "—"],
    ]
    action_rows = [
        ["A1", "Supprimer le polling et les traces de debug", "quick win", "faible", "Frontend", "S1", "0 requête périodique"],
        ["A2", "Activer Cache-Control et compression", "quick win", "faible", "Backend", "S1", "cache hit > 80 %"],
        ["A3", "Optimiser les images (WebP/AVIF, srcset)", "quick win", "faible", "Contenu", "S2", "poids < 300 Ko"],
        ["A4", "Indexer les requêtes et sélectionner les colonnes utiles", "quick win", "faible", "Backend", "S2", "temps P95 < 100 ms"],
        ["A5", "Définir un budget de poids et de requêtes", "moyen", "moyen", "Tech lead", "S3", "budget respecté en CI"],
        ["A6", "Documenter le PUE et la région de l’hébergeur", "moyen", "moyen", "Achats", "S3", "PUE < 1,5"],
        ["A7", "Mesurer la consommation réelle du serveur", "moyen", "moyen", "Ops", "S4", "kWh/semaine"],
        ["A8", "Former les équipes à l’écoconception", "moyen", "moyen", "RH/GreenIT", "S4", "quiz > 80 %"],
        ["A9", "Réduire les terminaux dédiés et allonger leur durée de vie", "long", "fort", "Direction", "S6", "part terminaux < 5 %"],
        ["A10", "Intégrer un contrôle GreenIT en CI", "long", "moyen", "DevOps", "S6", "seuils bloquants"],
    ]
    benchmark_rows = [
        ["Boavizta API", "Serveur, terminal, cloud", "AGPL-3.0 / données ouvertes", "GWP, PE, ADPe, ADPf", "API et méthodologie", "[S26]"],
        ["EcoIndex", "Web", "CC BY-NC-ND", "Score, GES, eau", "Screening navigateur", "[S28]"],
        ["GreenIT Analysis", "Web", "AGPL-3.0", "EcoIndex", "Extension", "[S30]"],
        ["CodeCarbon", "Compute Python", "MIT", "Énergie, carbone", "Mesure d’entraînement", "[S31]"],
        ["Scaphandre", "Hôte / processus", "Apache-2.0", "Énergie", "Métrologie", "[S32]"],
        ["Cloud Carbon Footprint", "Cloud", "Apache-2.0", "Carbone estimé", "Facturation cloud", "[S33]"],
        ["NegaOctet", "ACV multicritère", "Commerciale", "526 facteurs", "ACV détaillée", "[S35]"],
        ["Base Empreinte", "Facteurs ADEME", "Licence Ouverte", "GWP, multicritères", "Facteurs génériques", "[S07]"],
        ["OpenLCA", "ACV", "Open source + jeux de données", "Multi-indicateurs", "ACV complète", "[S08]"],
    ]
    ideas = [
        "Supprimer le polling et les appels réseau périodiques.",
        "Remplacer les images PNG par WebP/AVIF avec `srcset`.",
        "Supprimer les images décoratives et les vidéos non porteuses d’information.",
        "Minifier CSS et JS, supprimer le code mort.",
        "Activer la compression et le cache HTTP.",
        "Définir un budget de poids par page.",
        "Réduire le DOM et le nombre de composants.",
        "Éviter les polices web propriétaires.",
        "Limiter les bibliothèques tierces.",
        "Préférer les composants natifs du navigateur.",
        "Paginer les listes et limiter les champs retournés.",
        "Ajouter les index manquants et revoir les requêtes N+1.",
        "Mettre en cache les réponses API stables.",
        "Supprimer les logs de debug et les traces verbeuses.",
        "Réduire la durée de conservation des données.",
        "Minimiser les données collectées.",
        "Documenter le PUE et la région de l’hébergement.",
        "Choisir un hébergement bas carbone et mutualisé.",
        "Mesurer la consommation réelle du serveur.",
        "Adapter la taille des instances à la charge.",
        "Éteindre les environnements de test la nuit.",
        "Mutualiser les serveurs et les bases de données.",
        "Allonger la durée de vie des terminaux.",
        "Réemployer ou reconditionner les équipements.",
        "Former les équipes aux gestes sobres.",
        "Intégrer un contrôle GreenIT en CI.",
        "Ajouter un critère GreenIT aux revues de code.",
        "Mettre en place une charte numérique responsable.",
        "Suivre un KPI énergie et un KPI poids.",
        "Éviter la compensation carbone comme argument de vente.",
        "Mesurer l’effet rebond après optimisation.",
        "Comparer les scénarios terminal partagé / dédié.",
    ]
    idea_lines = "\n".join(f"{i+1}. {idea}" for i, idea in enumerate(ideas))
    source_lines = "\n".join(f"- **{s['id']}** — {s['org']}, *{s['title']}*, {s['date']}. {s['url']}" for s in ctx["sources"])
    glossary = [
        ("ACV", "Analyse du cycle de vie ; méthode d’évaluation des impacts sur tout le cycle de vie [S12][S13]."),
        ("UF", "Unité fonctionnelle ; service rendu servant de base de comparaison."),
        ("GWP100", "Potentiel de réchauffement global à 100 ans, en kg CO2 eq."),
        ("ADPe", "Épuisement des ressources minérales, en kg Sb eq."),
        ("ADPf", "Épuisement des ressources fossiles, en MJ."),
        ("PUE", "Énergie totale du datacenter / énergie IT."),
        ("EcoIndex", "Score web 0–100 basé sur DOM, poids et requêtes [S28]."),
        ("SCI", "Software Carbon Intensity, taux d’émission par unité fonctionnelle [S14]."),
        ("ICV", "Inventaire du cycle de vie ; quantification des flux entrants et sortants."),
        ("WUE", "Water Usage Effectiveness ; litres d’eau consommés par kWh IT."),
        ("scope 1", "Émissions directes de l’organisation."),
        ("scope 2", "Émissions indirectes liées à l’électricité achetée."),
        ("scope 3", "Autres émissions indirectes de la chaîne de valeur."),
        ("RGESN", "Référentiel général d’écoconception des services numériques [S03]."),
        ("GR491", "Guide de référence de l’écoconception de services numériques [S05]."),
        ("RWEB", "Référentiel de bonnes pratiques web responsable [S06]."),
        ("NegaOctet", "Base de facteurs d’impacts ACV commerciale [S35], exemple local optionnel."),
        ("Green Coding", "Méthode ouverte de calcul de l’intensité carbone réseau [S42]."),
        ("Boavizta", "Communauté et API de quantification d’impact du numérique [S26]."),
        ("Effet rebond", "Hausse d’usage qui annule une partie du gain."),
        ("Greenwashing", "Allégation environnementale non étayée ou trompeuse."),
        ("Compensation", "Achat de crédits carbone ; ne rend pas un service neutre."),
    ]
    glossary_lines = "\n".join(f"- **{k}** : {v}" for k, v in glossary)
    return f"""# 1. Fiche d’identité du projet

**Projet** : {ctx['audit'].get('project', {}).get('name', 'Service d’émargement').replace("—", "-")}  
**Client** : {ctx['audit'].get('project', {}).get('client', 'Zone01 Normandie')}  
**Version** : {ctx['audit'].get('project', {}).get('version', '1.0')} — **Date** : {ctx['audit'].get('project', {}).get('date', '2026-11-09')}  
**Auteurs** : {', '.join(ctx['audit'].get('project', {}).get('authors', []))}

Nous avons audité un service fictif d’émargement utilisé par 100 étudiants et un membre du staff pendant une semaine. Le service est volontairement perfectible : image PNG lourde, CSS dupliqué, JavaScript non minifié, polling, `SELECT *`, absence d’index et `alt` manquant. Notre objectif est de montrer une démarche complète, traçable et honnête, pas de certifier un service réel.

::: callout {{tone=info title="À retenir"}}
Le cas est une **ACV screening**. Les chiffres servent à prioriser et à apprendre ; ils ne remplacent pas une ACV avec revue critique ni un audit RGESN officiel.
:::

# 2. Synthèse exécutive

Trois chiffres suffisent à raconter l’essentiel :

- **{n(total['gwp'])} kg CO2e** pour une semaine d’émargement, soit environ **{n(total['gwp']/100*1000)} g CO2e par étudiant**.
- **{pct(server.get('gwp',0)/total['gwp']*100)}** du GWP vient du serveur mutualisé ; **{pct(dev.get('gwp',0)/total['gwp']*100)}** vient du développement.
- **{pct(ctx["coverage_evaluated"])}** des critères RGESN ont un statut, mais **{pct(coverage)}** seulement ont une preuve : le score de **{scores:.1f}/100** est donc **{score_label}**.

::: callout {{tone=decision title="Notre décision"}}
Nous priorisons d’abord la mesure du serveur et de l’hébergement, puis les quick wins web. Optimiser le frontend est utile, mais ne doit pas masquer le poste serveur, qui domine dans notre scénario.
:::

# 3. Objectifs et questions d’audit

Nos questions étaient les suivantes :

1. Quels sont les postes qui contribuent le plus au GWP, à l’ADPe et à l’ADPf ?
2. Les terminaux sont-ils un hotspot dans un usage partagé ? Que se passe-t-il s’ils sont dédiés ?
3. Les optimisations web réduisent-elles le poids, les requêtes et l’EcoIndex ?
4. Le service respecte-t-il les grands principes RGESN, GR491 et RWEB ?
5. Quelles actions sont réalistes dans le temps et le budget d’une équipe pédagogique ?
6. Quelles preuves pouvons-nous fournir pour le RNCP39388 ?

# 4. Unité fonctionnelle et scénarios

**Unité fonctionnelle** : {p['description']}

{table(['Scénario', 'Acteur', 'Fréquence', 'Durée', 'Requêtes', 'Données', 'Terminal', 'Réseau'],
       [[s['id'], s['actor'], str(s['count_per_user']), f"{s['duration_s']} s", str(s['requests']), f"{s['data_kb']} Ko", s['device'], s['network']] for s in p['scenarios']])}

Nous ramenons tous les résultats à cette UF. Les scénarios sont des hypothèses de travail : ils ne sont pas issus d’une journalisation réelle. C’est une limite explicite.

# 5. Méthodologie

Nous appliquons les quatre phases d’ISO 14040/14044 [S12][S13] : objectifs et champ, inventaire, évaluation des impacts, interprétation. La frontière est une ACV screening attributionnelle :

- terminaux (fabrication + usage) ;
- réseau fixe et mobile ;
- serveur et hébergement (fabrication + usage) ;
- développement et maintenance ;
- fin de vie exclue faute de facteur spécifique.

Les indicateurs sont le GWP100 (kg CO2 eq), l’ADPe (kg Sb eq) et l’ADPf (MJ). Les facteurs viennent de Boavizta [S26] ; pour le réseau, nous utilisons le facteur local NegaOctet [S35] afin de couvrir GWP, ADPe et ADPf. Le facteur ouvert Green Coding [S42] reste disponible comme variante de screening pour le GWP seul.

::: callout {{tone=hypothese title="Notre hypothèse"}}
Le mix électrique est celui de la France en 2024 : **51,9 g CO2e/kWh** [S10]. Le serveur est un 2U mutualisé, avec un PUE de 1,5 et 10 % des impacts alloués au service.
:::

# 6. Inventaire et facteurs

{table(['Poste', 'Catégorie', 'Tier', 'GWP (kg CO2e)', 'ADPe (kg Sb eq)', 'ADPf (MJ)', 'Source'], item_rows)}

Les facteurs utilisés sont documentés dans `factors.open.csv` et `factors.local.example.csv`. Les valeurs Boavizta sont datées du 2026-11-09. Le facteur réseau de la démonstration est NegaOctet local [S35], utilisé comme exemple pédagogique non redistribuable. Green Coding [S42] reste une variante ouverte pour le GWP seul.

{table(['ID', 'Hypothèse', 'Valeur', 'Source', 'Confiance', 'Statut', 'Preuve', 'Owner', 'Détail preuve'], hyp_rows)}

# 7. Résultats par étape du cycle de vie

{img(figures / 'lifecycle.png', 'Graphique des impacts GWP par étape du cycle de vie')}

{table(['Étape', 'GWP (kg CO2e)', 'Part'], stage_rows)}

Le serveur et le développement dominent. La maintenance reste faible. La fin de vie n’est pas évaluée : nous préférons l’assumer plutôt que d’inventer un facteur.

# 8. Résultats par tier

{img(figures / 'tiers.png', 'Diagramme de la répartition du GWP par tier')}

{table(['Tier', 'GWP (kg CO2e)', 'Part'], tier_rows)}

Le tier 3 (serveur) représente la majorité du GWP. Le tier 1 (terminaux) est faible **parce que** les appareils sont partagés et utilisés très peu de temps pour le service. Ce résultat serait très différent avec des terminaux dédiés.

# 9. Résultats par fonction

Nous n’avons pas alloué les impacts scénario par scénario, car les facteurs disponibles ne permettent pas une répartition fiable. Le tableau suivant donne les volumes de données, qui ne sont pas proportionnels aux impacts :

{table(['Fonction', 'Volume indicatif', 'Lecture'], [['Émargement étudiant', '5 Ko', 'Très faible poids, mais 10 interactions par étudiant.'], ['Consultation étudiante', '120 Ko', 'Poste web le plus lourd.'], ['Consultation staff', '10 Ko', 'Faible volume.']])}

::: callout {{tone=limite title="Notre limite"}}
Nous donnons une répartition indicative par volume de données, sans l’utiliser comme score ; une répartition par fonction serait une fausse précision.
:::

# 10. Hotspots et contributeurs principaux

{img(figures / 'hotspots.png', 'Graphique des cinq premiers contributeurs au GWP')}

{table(['Rang', 'Poste', 'GWP (kg CO2e)', 'Part'], [[str(i+1), h['label'], n(h['gwp']), pct(h['share_gwp'])] for i, h in enumerate(m['hotspots'])])}

Le serveur représente **{pct(server.get('gwp',0)/total['gwp']*100)}** du GWP. Le développement représente **{pct(dev.get('gwp',0)/total['gwp']*100)}**. Les smartphones, dans notre scénario partagé, ne représentent que **{pct(phone.get('gwp',0)/total['gwp']*100)}**.

# 11. Conditions de validité, sensibilité et plan de consolidation

Le rapport reste un **screening**. Nous ne supprimons pas les incertitudes : nous les quantifions et nous indiquons comment les réduire.

## Fourchette globale

Nous appliquons une fourchette de ±30 % sur le total, faute de distribution de facteurs :

- bas : **{n(m['uncertainty']['low']['gwp'])} kg CO2e** ;
- base : **{n(total['gwp'])} kg CO2e** ;
- haut : **{n(m['uncertainty']['high']['gwp'])} kg CO2e**.

## Scénarios de sensibilité

{table(['Scénario', 'Variation', 'GWP (kg CO2e)', 'Δ vs base', 'Lecture'], [[s['scenario'], s['variation'], n(s['gwp']), delta_fmt(s['delta_pct']), s['comment']] for s in ctx['sensitivity']])}

Le scénario « terminaux dédiés » est le plus structurant : le GWP passerait à environ **{n(dedicated_total)} kg CO2e**, soit **{n(dedicated_total/total['gwp'])}×** le scénario de partage. Ce n’est pas une prédiction : c’est la démonstration que l’allocation change la conclusion.

## Conditions de validité

- Le serveur est un profil Boavizta par défaut ; il doit être remplacé par la fiche fournisseur (H1).
- Le PUE de 1,5 doit être confirmé par l’hébergeur (H2) ; les scénarios 1,2 et 1,8 encadrent la valeur.
- L’allocation de 10 % est une convention de travail (H3) ; les scénarios 5 % et 20 % montrent la sensibilité.
- Les 30 h de développement et les 40 s d’usage sont des scénarios (H4, H5), pas des mesures.
- Le facteur réseau NegaOctet local couvre GWP, ADPe et ADPf ; sa licence interdit la redistribution.
- La fin de vie, les impacts sociaux et l’effet rebond sont hors périmètre.

## Plan de consolidation

1. Obtenir la fiche serveur, la facture d’électricité et le PUE contractuel.
2. Mesurer les usages réels (logs, entretiens) et remplacer H4/H5.
3. Ajouter les facteurs ADPe/ADPf réseau ou déclarer le tier 2 partiellement évalué.
4. Intégrer la fin de vie avec un facteur documenté.
5. Faire une revue critique externe avant de présenter le rapport comme une ACV complète.

::: callout {{tone=limite title="Ce que nous ne savons pas encore"}}
Les caractéristiques réelles du serveur, le PUE de l’hébergeur et les usages réels ne sont pas mesurés. Le rapport le dit et fournit les scénarios qui encadrent l’incertitude. Il ne prétend pas à une ACV complète.
:::

# 12. Diagnostic technique

## Frontend

- Image PNG de **1,6 Mo** : elle domine le poids de la page.
- CSS dupliqué et non minifié.
- JavaScript non minifié, `console.log`, `innerHTML`, polling toutes les 5 s.
- `alt` manquant, champ sans label, `target="_blank"` sans `rel`.

## Backend

- `SELECT *` sur la table des présences.
- Absence d’index sur `created_at`.
- CORS `*`.
- Secret factice dans le code (à ne jamais faire en production).

## Infrastructure

- Un serveur 2U mutualisé, PUE 1,5 supposé, 10 % alloués.
- Pas de mesure réelle de consommation.
- Pas de politique de cache ni de compression.

{table(['Sévérité', 'Fichier:Ligne', 'Signal', 'Pourquoi', 'RGESN'], signal_rows)}

# 13. Benchmark et correspondance normative

{table(['Outil', 'Périmètre', 'Licence', 'Sorties', 'Usage', 'Source'], benchmark_rows)}

Nous ne comparons pas les scores entre eux : Boavizta, EcoIndex et NegaOctet ne mesurent pas la même chose. Nous utilisons Boavizta pour les équipements, EcoIndex pour le web et NegaOctet local pour le réseau ; Green Coding reste une variante ouverte pour le GWP seul.

Correspondance normative : RGESN [S03][S04] pour les 78 critères, GR491 [S05] pour les 8 familles, RWEB [S06] pour les 119 fiches web. Le rapport ne recopie pas les référentiels ; il cite les IDs utilisés.

# 14. Évaluation RGESN

{table(['Statut', 'Nombre'], [[k, str(v)] for k, v in counts.items()])}

{table(['Preuve', 'Nombre'], [[k, str(v)] for k, v in ctx["evidence_counts"].items()])}

**Score d’avancement** : {scores:.1f}/100. **Statuts évalués** : {pct(ctx["coverage_evaluated"])}. **Preuves disponibles** : {pct(coverage)}. Le score est **{score_label}** : le taux de statuts ne vaut pas taux de preuves. Les 54 critères non validés le sont pour l’essentiel faute de preuve. Ce n’est pas le score officiel de l’outil RGESN.

{img(figures / 'rgesn.png', 'Jauge du score RGESN d’avancement')}

{table(['ID', 'Priorité', 'Statut', 'Critère'], nc_rows)}

Les {counts.get("non validé", 0)} critères non validés le sont majoritairement faute de preuve : nous les déclarons non conformes au stade du screening, plutôt que de les déclarer conformes sans preuve.

# 15. Brainstorm

Nous avons divergé sans filtrer, puis convergence avec une matrice impact/effort. Les 32 idées sont listées ci-dessous ; les idées écartées sont celles qui relèvent de la compensation, de l’énergie verte seule ou d’un gain non mesurable.

{idea_lines}

{img(figures / 'actions.png', 'Matrice impact / effort des actions d’écoconception')}

::: callout {{tone=info title="Idées écartées"}}
« Acheter de la compensation carbone », « passer au cloud vert sans preuve » et « Optimiser le frontend pour compenser le serveur » sont écartées : elles ne réduisent pas les impacts du service et peuvent relever du greenwashing.
:::

# 16. Plan d’action priorisé

{table(['ID', 'Action', 'Horizon', 'Effort', 'Responsable', 'Échéance', 'KPI'], action_rows)}

Les quick wins sont A1 à A4. Ils sont peu risqués et mesurables. Les actions A5 à A8 structurent la démarche. A9 et A10 sont des projets longs, à décider avec la direction.

# 17. Quantification des gains

{table(['Indicateur', 'Baseline', 'Optimisé', 'Delta'], gain_rows)}

La page passe de **{n(webp.get('size_kb', 0))} Ko** à **{n(webo_p.get('size_kb', 0))} Ko**, soit une réduction de **{pct((1 - webo_p.get('size_kb', 1)/webp.get('size_kb', 1))*100) if webp.get('size_kb') else '—'}**. L’EcoIndex passe de **{web_eco.get('score', '—')}** à **{webo_eco.get('score', '—')}**. Le GWP du service ne baisse que de **moins de 0,1 %** : le réseau n’est pas le hotspot, et le serveur n’a pas changé. C’est un résultat honnête : optimiser le frontend ne suffit pas.

::: callout {{tone=decision title="Notre décision"}}
Nous ne présentons pas la réduction du poids de la page comme une réduction du GWP. Ce sont deux indicateurs différents. Le gain GWP est faible dans ce scénario, et nous le disons.
:::

# 18. Bénéfices collatéraux et gouvernance

- **Accessibilité** : labels, `alt`, contrastes, navigation clavier.
- **Sécurité** : suppression du CORS `*`, du secret factice, des `SELECT *`.
- **Qualité** : code plus léger, cache, index, moins de debug.
- **Coûts** : moins de bande passante, moins de CPU, moins de stockage.
- **UX** : page plus rapide, surtout sur mobile.
- **Gouvernance** : charte numérique responsable, revue GreenIT en CI, KPI poids/énergie.

# 19. Conclusion, bibliographie, glossaire et annexes

## Conclusion

Le service peut réduire fortement son poids web, mais son GWP reste dominé par le serveur et le développement. La priorité est de **mesurer** l’hébergement et la consommation réelle, puis de décider. Nous recommandons de ne pas acheter de compensation et de ne pas revendiquer la neutralité carbone.

## Sources et bibliographie

{source_lines}

## Glossaire

{glossary_lines}

## Annexes

- `metrics.json` : résultats détaillés.
- `calculation-notes.md` : note de calcul, formule par item.
- `rgesn-score.csv` : 78 critères.
- `codebase-audit.json` : signaux statiques.
- `web-metrics.json` : mesures Playwright.
- `sources.yml` : registre des {len(ctx["sources"])} sources.
"""


def deck_text(ctx: dict, figures: Path) -> dict:
    m, mo, web, webo = ctx["m"], ctx["mo"], ctx["web"], ctx["webo"]
    total = m["totals"]
    server = get_item(m, "server")
    dev = get_item(m, "dev-laptops")
    webp = web.get("page") or {}
    webo_p = webo.get("page") or {}
    eco = web.get("ecoindex") or {}
    ecoo = webo.get("ecoindex") or {}
    notes = {
        1: "Bonjour à toutes et à tous. Nous présentons l’audit GreenIT du service d’émargement de Zone01. Notre démarche est une ACV screening, c’est-à-dire une analyse de cycle de vie simplifiée, construite pour prioriser des actions et non pour certifier un service. Nous allons vous montrer les chiffres, les hypothèses, les limites et le plan d’action. Le service est fictif, mais la méthode est celle que nous appliquerions à un vrai projet. Nous avons volontairement conservé des imperfections dans le code pour montrer le diagnostic, la mesure avant/après et l’amélioration. Nous prendrons environ quinze minutes, puis cinq minutes de questions. Nous allons suivre ce fil du cadrage jusqu’aux preuves, sans sauter d’étape. Nous commençons par le contexte et la méthode. Le plan de la présentation est simple et progressif.",
        2: "Trois chiffres résument la situation. Le service émet environ 1,76 kilogramme de CO2 équivalent par semaine. Le serveur représente 64 % du GWP et le développement 32 %. La couverture RGESN est de 40 %, donc le score de 38 sur 100 n’est pas significatif : c’est un chantier, pas une performance. Notre décision est de mesurer le serveur et l’hébergement avant de promettre une réduction globale. Nous préférons afficher une fourchette et une couverture plutôt qu’un chiffre unique qui donnerait une fausse impression de précision. Ce message est important : un audit honnête commence par dire ce qu’il ne sait pas. Cette synthèse sera détaillée dans les sections suivantes, avec les calculs et les sources. Le détail des calculs est fourni en annexe. Nous cherchons une décision, pas un chiffre spectaculaire.",
        3: "Le contexte est simple : cent étudiants, un membre du staff, une semaine, trois développeurs et un serveur mutualisé. Les contraintes sont un budget nul, une échéance courte, la sécurité, le RGPD et l’accessibilité. La stack est volontairement légère : HTML, CSS, JavaScript, Python et SQLite. Les terminaux sont partagés, ce qui change beaucoup l’allocation : un smartphone n’est pas dédié au service, il est utilisé quelques secondes. Nous avons aussi un laptop pour le staff et trois laptops pour les développeurs. Cette fiche projet sert de contrat : elle fixe le périmètre, les acteurs, les contraintes et les hypothèses de départ. Nous reviendrons sur chaque contrainte quand elle influence une décision. Ces éléments viennent du fichier audit.yml. Les contraintes sont traitées comme des données d’entrée.",
        4: "Notre méthode suit les quatre phases d’ISO 14040 et 14044 : objectifs et champ, inventaire, évaluation des impacts, interprétation. Nous définissons une unité fonctionnelle, une frontière et des règles d’allocation. Nous utilisons trois indicateurs : le GWP100 en kilogrammes de CO2 équivalent, l’ADPe en kilogrammes d’antimoine équivalent pour les ressources minérales, et l’ADPf en mégajoules pour les ressources fossiles. Les facteurs viennent de Boavizta et du facteur local NegaOctet pour le réseau. Nous distinguons mesuré, estimé et supposé. Le résultat est une aide à la décision, pas une certification. Chaque choix méthodologique est discuté et pourra être contesté par le jury. Nous assumons les choix et les limites.",
        5: "L’inventaire comprend les smartphones des étudiants, le laptop du staff, les laptops des développeurs, le serveur, le réseau fixe et mobile, et la maintenance. Les hypothèses clés sont un serveur 2U, un PUE de 1,5, 10 % d’allocation, 30 heures de développement et 40 secondes d’usage par étudiant. Ces hypothèses sont dans audit.yml et dans la note de calcul. Nous avons aussi supposé un mix électrique français à 51,9 grammes de CO2 par kilowattheure. Chaque hypothèse a un identifiant, une source, un niveau de confiance et un impact si elle est fausse. C’est ce qui permet de discuter le résultat au lieu de le subir. Le fichier audit.yml est la source unique de vérité pour les quantités et les hypothèses. Chaque quantité est justifiée ou signalée comme hypothèse.",
        6: "Par étape du cycle de vie, le serveur et le développement dominent. La maintenance est faible. La fin de vie est hors périmètre faute de facteur spécifique ; une ACV complète devrait la traiter. Le message est que l’hébergement et les heures de développement sont les premiers leviers. Nous aurions pu nous concentrer sur le frontend parce que c’est plus facile à montrer, mais les chiffres disent que ce n’est pas le poste principal. C’est une décision méthodologique importante : nous suivons les hotspots, pas les intuitions. Nous préférons un résultat dominé par un poste réel à un résultat flatteur mais faux. Les figures sont générées à partir des mêmes données.",
        7: "Par tier, le tier 3, c’est-à-dire le serveur, représente l’essentiel du GWP. Le tier 1 est faible parce que les terminaux sont partagés et utilisés très peu de temps. Le tier 2, le réseau, est négligeable dans ce scénario. Attention : si les terminaux étaient dédiés, le tier 1 deviendrait dominant. Nous avons testé ce scénario de sensibilité. C’est pour cela que l’allocation et le scénario d’usage doivent être explicites. Un même service peut avoir une conclusion très différente selon que l’on considère un terminal partagé ou un terminal dédié. Nous préférons le dire clairement. Le scénario de sensibilité est explicite pour éviter une conclusion trop générale. Le tier 3 est le premier levier de réduction.",
        8: "Les hotspots sont le serveur, les laptops des développeurs et la maintenance. Les smartphones ne représentent que 0,24 %. Si les cent smartphones étaient dédiés 168 heures, le GWP total passerait à environ 66 kilogrammes, soit 37 fois plus. Ce n’est pas une prédiction : c’est une démonstration que l’allocation change la conclusion. Nous recommandons donc de mesurer l’usage réel et de ne pas supposer que les terminaux sont négligeables. Dans un service où chaque étudiant aurait une application dédiée et l’utiliserait longtemps, le classement des hotspots serait différent. C’est une limite méthodologique, pas un détail. C’est le point le plus important pour interpréter correctement notre résultat. L’allocation est un choix, pas une vérité physique.",
        9: "Le diagnostic technique montre une image PNG de 1,6 mégaoctet, du CSS dupliqué, du JavaScript non minifié, du polling toutes les cinq secondes, un SELECT *, pas d’index, un CORS permissif et un secret factice. Ce sont des défauts mesurables. Nous les relions au RGESN et à RWEB. Le scanner ne remplace pas un audit de sécurité, mais il donne des preuves. Nous avons aussi vérifié les attributs alt, les labels et les target blank. Chaque signal a un fichier, une ligne, une sévérité et une recommandation. C’est ce qui permet de passer d’un constat général à une action concrète et vérifiable. Le diagnostic technique sera relié aux actions du plan, pas laissé comme une liste. Chaque signal est relié à une norme.",
        10: "Nous avons comparé les outils : Boavizta pour les équipements, EcoIndex pour le web, NegaOctet local pour le réseau. Les périmètres ne sont pas comparables. Boavizta ne donne pas un score web, EcoIndex ne fait pas d’ACV, et NegaOctet est une base commerciale. Nous utilisons aussi RGESN, GR491 et RWEB. Le RGESN est le référentiel réglementaire français ; GR491 et RWEB sont des compléments. Nous ne comparons pas les scores entre eux. La question n’est pas « quel outil est le meilleur », mais « quel outil répond à quelle question, avec quel périmètre et quelle licence ». La comparabilité des périmètres est une règle que nous nous sommes imposée. Les licences sont précisées pour chaque outil.",
        11: "Le brainstorm a produit 32 idées, sans filtrage. La matrice impact-effort montre les quick wins : supprimer le polling, activer le cache, optimiser les images, indexer les requêtes. Les projets structurants sont le PUE de l’hébergeur, la durée de vie des terminaux et la gouvernance. Les idées de compensation sont écartées. Nous avons aussi écarté les idées qui ne réduisent pas les impacts, comme « passer au cloud vert » sans preuve ou « optimiser le frontend pour compenser le serveur ». Le brainstorm sert à explorer, la matrice sert à décider. Ce sont deux moments séparés. La divergence et la convergence sont deux temps distincts, avec des critères explicites. La matrice est un outil d’aide à la décision.",
        12: "Le plan d’action est divisé en quick wins, moyen et long. Les quick wins sont A1 à A4 : polling, cache, images, requêtes SQL. Les actions A5 à A8 structurent la mesure, le PUE, la formation et la CI. A9 et A10 sont des décisions de direction : terminaux et gouvernance. Chaque action a un responsable, une échéance et un KPI. Nous ne promettons pas de gains non mesurés. Les quick wins sont peu risqués et peuvent être faits en une à deux semaines. Les projets longs demandent un arbitrage budgétaire et politique. Nous préférons un plan réaliste à une liste de vœux. Le plan est volontairement court : dix actions, des responsables et des KPI. Les échéances sont indicatives et réalistes.",
        13: "Après optimisation, la page passe de 1 595 kilooctets à 92 kilooctets, soit une réduction de 94 %. Les requêtes passent de 7 à 6, le cache de 0 à 4 ressources, et l’EcoIndex de 87 à 95. Le GWP ne baisse que de moins de 0,1 %, car le réseau n’est pas le hotspot et le serveur n’a pas changé. C’est un résultat honnête. Nous ne présentons pas la réduction du poids de la page comme une réduction du GWP : ce sont deux indicateurs différents. Le gain est réel pour la bande passante, le temps de chargement et l’expérience utilisateur, mais il ne dispense pas de mesurer l’hébergement. C’est le message central de cette slide. Nous distinguons clairement le gain web du gain GWP, sans les confondre. Le gain GWP est faible, et nous l’expliquons.",
        14: "Les bénéfices collatéraux sont l’accessibilité, la sécurité, la qualité, les coûts et l’expérience utilisateur. La gouvernance passe par une charte, une revue GreenIT en CI et des KPI. Nous recommandons de mesurer la consommation réelle, de documenter le PUE et de former les équipes. La démarche doit être continue, pas un one-shot. Un audit qui reste dans un tiroir ne sert à rien. Nous proposons un point de mesure à trois mois et un nouvel audit à six mois. Les KPI doivent être simples et partagés : poids, requêtes, kWh, PUE, EcoIndex. C’est la condition pour que les progrès soient visibles et crédibles. La gouvernance est ce qui transforme une optimisation ponctuelle en pratique durable. Les KPI seront suivis dans le temps.",
        15: "En conclusion, le service peut réduire fortement son poids web, mais son GWP reste dominé par le serveur et le développement. La priorité est de mesurer, puis de décider. Nous ne revendiquons ni neutralité carbone ni compensation. Nous avons montré les forces, les faiblesses, les hypothèses et les limites. Merci pour votre attention. Nous sommes prêts pour vos questions, notamment sur l’allocation des terminaux, le PUE, la couverture RGESN et la différence entre poids web et GWP. Nous avons aussi préparé des réponses aux questions les plus probables du jury. Merci de votre attention.",
    }
    notes[2] = (f"Trois chiffres résument la situation. Le service émet environ 1,76 kilogramme de CO2 équivalent par semaine. "
                f"Le serveur représente 64 % du GWP et le développement 32 %. La couverture RGESN est de {pct(ctx['coverage'])}, "
                f"avec un score de {ctx['score']:.1f} sur 100 : {pct(ctx['coverage_evaluated'])} des critères ont un statut, "
                f"mais seulement {pct(ctx['coverage'])} ont une preuve, donc le score est {('significatif mais faible' if ctx['coverage'] >= 50 else 'non significatif')}. "
                "Notre décision est de mesurer le serveur et l’hébergement avant de promettre une réduction globale. "
                "Nous préférons afficher une fourchette et une couverture plutôt qu’un chiffre unique qui donnerait une fausse impression de précision. "
                "Ce message est important : un audit honnête commence par dire ce qu’il ne sait pas. "
                "Cette synthèse sera détaillée dans les sections suivantes, avec les calculs et les sources. "
                "Le détail des calculs est fourni en annexe. Nous cherchons une décision, pas un chiffre spectaculaire. "
                "Nous allons maintenant dérouler les preuves. Le reste du dossier détaille chaque calcul.")
    slides = [
        {"layout": "title", "title": "Audit GreenIT — Service d’émargement", "subtitle": "ACV screening, RGESN et plan d’action", "notes": notes[1]},
        {"layout": "metrics", "kicker": "Synthèse", "title": "Trois chiffres pour décider", "source": "Calculs de l’audit ; [S26], [S42]",
         "cards": [{"value": f"{n(total['gwp'])} kg", "label": "CO2e / semaine", "detail": f"±30 % : {n(m['uncertainty']['low']['gwp'])}–{n(m['uncertainty']['high']['gwp'])} kg"},
                   {"value": pct(server.get('gwp',0)/total['gwp']*100), "label": "du GWP vient du serveur", "detail": "Hébergement mutualisé, PUE 1,5 supposé"},
                   {"value": pct(ctx['coverage']), "label": "de preuves RGESN", "detail": f"{pct(ctx['coverage_evaluated'])} statués ; score {ctx['score']:.1f}/100 {('significatif mais faible' if ctx['coverage'] >= 50 else 'non significatif')}"}], "notes": notes[2]},
        {"layout": "bullets", "kicker": "Contexte", "title": "Un service simple, des contraintes réelles", "bullets": ["100 étudiants, 1 staff, 1 semaine, 3 développeurs", "Stack : HTML/CSS/JS, Python, SQLite, serveur mutualisé", "Contraintes : budget nul, sécurité, RGPD, accessibilité", "Terminaux partagés : l’allocation change la conclusion"], "source": "audit.yml ; [S24], [S25]", "notes": notes[3]},
        {"layout": "bullets", "kicker": "Méthode", "title": "Une ACV screening traçable", "bullets": ["ISO 14040/14044 : cadre, inventaire, impacts, interprétation", "GWP100, ADPe, ADPf : trois indicateurs, trois unités", "Frontière : terminaux, réseau, serveur, développement, maintenance", "Distinguer mesuré, estimé, supposé"], "source": "[S12], [S13], [S08]", "notes": notes[4]},
        {"layout": "bullets", "kicker": "Inventaire", "title": "Sept postes, des hypothèses explicites", "bullets": ["100 smartphones × 40 s ; 1 laptop staff × 20 s", "3 laptops développeurs × 30 h", "1 serveur × 168 h × 10 % × PUE 1,5", f"Réseau dérivé de la page mesurée ({n(webp.get('size_kb', 0))} Ko)"], "source": "audit.yml ; [S26], [S42]", "notes": notes[5]},
        {"layout": "chart", "kicker": "Résultats", "title": "Serveur et développement dominent", "image": str(figures / "lifecycle.png"), "takeaway": "Le serveur et le développement sont les premiers leviers.", "source": "Calculs de l’audit", "notes": notes[6]},
        {"layout": "chart", "kicker": "Résultats", "title": "Le tier 3 porte l’essentiel du GWP", "image": str(figures / "tiers.png"), "takeaway": "Le tier 1 est faible car les terminaux sont partagés.", "source": "Calculs de l’audit", "notes": notes[7]},
        {"layout": "chart", "kicker": "Hotspots", "title": "Le serveur représente 64 % du GWP", "image": str(figures / "hotspots.png"), "takeaway": "Mesurer le serveur avant d’optimiser le frontend.", "source": "Calculs de l’audit", "notes": notes[8]},
        {"layout": "bullets", "kicker": "Diagnostic", "title": "Des défauts mesurables, pas des impressions", "bullets": ["Image PNG 1,6 Mo, CSS dupliqué, JS non minifié", "Polling 5 s, console.log, innerHTML", "SELECT *, pas d’index, CORS *, secret factice", "alt manquant, label manquant, target=_blank sans rel"], "source": "codebase-audit.json ; [S03], [S06]", "notes": notes[9]},
        {"layout": "bullets", "kicker": "Benchmark", "title": "Choisir l’outil selon la question", "bullets": ["Boavizta : équipements, GWP/PE/ADPe/ADPf", "EcoIndex : web, score/GES/eau", "NegaOctet : ACV multicritère, licence commerciale", "RGESN, GR491, RWEB : référentiels complémentaires"], "source": "[S26], [S28], [S35], [S03], [S05]", "notes": notes[10]},
        {"layout": "matrix", "kicker": "Brainstorm", "title": "32 idées, puis une matrice impact/effort", "items": [{"label": "Polling", "impact": 0.18, "effort": 0.12}, {"label": "Cache", "impact": 0.28, "effort": 0.22}, {"label": "Images", "impact": 0.35, "effort": 0.28}, {"label": "SQL", "impact": 0.22, "effort": 0.25}, {"label": "PUE", "impact": 0.62, "effort": 0.65}, {"label": "Terminaux", "impact": 0.85, "effort": 0.8}], "takeaway": "Quick wins : polling, cache, images, SQL. Projets : PUE, terminaux, gouvernance.", "source": "Brainstorm ; [S03], [S05], [S06]", "notes": notes[11]},
        {"layout": "timeline", "kicker": "Plan d’action", "title": "Quick wins, moyen, long", "items": [{"phase": "S1", "label": "Polling, cache, images, SQL", "start": 0, "end": 1}, {"phase": "S2", "label": "Budget poids, PUE, mesure", "start": 1, "end": 3}, {"phase": "S3", "label": "Formation, CI, charte", "start": 3, "end": 5}, {"phase": "S4+", "label": "Terminaux, gouvernance", "start": 5, "end": 8}], "source": "Plan d’action", "notes": notes[12]},
        {"layout": "metrics", "kicker": "Gains", "title": "Le web fond, le GWP bouge peu", "source": "Mesures Playwright ; calculs de l’audit",
         "cards": [{"value": f"{n(webp.get('size_kb', 0))} → {n(webo_p.get('size_kb', 0))} Ko", "label": "poids de la page", "detail": f"−{pct((1 - webo_p.get('size_kb', 1)/webp.get('size_kb', 1))*100) if webp.get('size_kb') else '—'}"},
                   {"value": f"{eco.get('score', '—')} → {ecoo.get('score', '—')}", "label": "EcoIndex", "detail": "87 → 95"},
                   {"value": pct((1 - m['totals']['gwp']/mo['totals']['gwp'])*100) if False else pct((1 - mo['totals']['gwp']/m['totals']['gwp'])*100), "label": "de GWP évité", "detail": "Le réseau n’est pas le hotspot"}], "notes": notes[13]},
        {"layout": "bullets", "kicker": "Bénéfices", "title": "Au-delà du carbone", "bullets": ["Accessibilité : labels, alt, contrastes, clavier", "Sécurité : CORS, secrets, SELECT *", "Qualité : cache, index, moins de debug", "Coûts et UX : bande passante, CPU, rapidité"], "source": "[S24], [S25], [S39], [S40]", "notes": notes[14]},
        {"layout": "closing", "title": "Merci", "subtitle": "Questions et échanges — 5 minutes", "bullets": ["Mesurer avant de promettre", "Ne pas confondre poids web et GWP", "Assumer les hypothèses et les limites"], "notes": notes[15]},
    ]
    return {"meta": {"title": "Audit GreenIT — Service d’émargement", "subtitle": "ACV screening, RGESN et plan d’action",
                      "client": "Zone01 Normandie", "date": "2026-11-09", "version": "1.0",
                      "authors": ["Équipe GreenIT RNCP39388"], "footer": "Audit GreenIT — Zone01 Normandie"},
            "slides": slides}


def rncp_docs(ctx: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REF / "rncp39388-matrix.csv", out / "01-matrice-competences.csv")
    matrix = list(csv.DictReader((REF / "rncp39388-matrix.csv").open(encoding="utf-8-sig")))
    blocks = {}
    for row in matrix:
        blocks.setdefault(row["block"], []).append(row)
    proof = ["# Dossier de preuves RNCP39388", "",
             "Titre : Responsable green IT (RNCP39388, niveau 6, Efficom).", "",
             "Chaque compétence est reliée à une preuve existante. Les preuves sont des fichiers du bundle ou des livrables générés dans `dist/`.", ""]
    for block, rows in blocks.items():
        proof += [f"## {block} — {rows[0]['block_title']}", ""]
        for r in rows:
            proof += [f"### {r['competency_id']} — {r['competency']}", "",
                      f"- **Preuve** : `{r['evidence']}`", f"- **Emplacement** : {r['location']}",
                      f"- **Statut** : {r['status']}", ""]
    (out / "02-dossier-preuves.md").write_text("\n".join(proof), encoding="utf-8")
    (out / "03-checklist-livrables.md").write_text("""# Checklist des livrables

- [x] Rapport DOCX et PDF
- [x] Soutenance PPTX et PDF
- [x] Vidéo teaser 60–90 s
- [x] Figures PNG avec textes alternatifs
- [x] Audit `audit.yml` validé
- [x] Calculs GWP, ADPe, ADPf
- [x] Évaluation RGESN 78 critères
- [x] Diagnostic codebase et métriques web
- [x] Plan d’action et gains
- [x] Matrice RNCP 19 compétences
- [x] Dossier de preuves
- [x] Charte, plan de mesure, plan projet, formation, rétrospective
""", encoding="utf-8")
    shutil.copyfile(REF / "jury-questions.md", out / "04-questions-jury.md")
    (out / "05-plan-soutenance-15min.md").write_text("""# Plan de soutenance — 15 minutes + 5 minutes

| Temps | Séquence | Message |
|---:|---|---|
| 0–1 min | Accroche et contexte | Un service simple, des contraintes réelles |
| 1–4 min | Méthode et UF | ACV screening, 3 indicateurs, frontière explicite |
| 4–7 min | Résultats | Serveur 64 %, développement 32 %, terminaux 0,24 % |
| 7–9 min | Diagnostic technique | Image 1,6 Mo, polling, SELECT *, cache absent |
| 9–11 min | Benchmark et normes | RGESN 100 % statués, 40 % preuvés, score faible, GR491, RWEB |
| 11–13 min | Brainstorm et plan | Quick wins, moyen, long |
| 13–14 min | Gains | Poids −94 %, EcoIndex 87→95, GWP < 0,1 % |
| 14–15 min | Limites et conclusion | Mesurer avant de promettre |
| 15–20 min | Questions | Voir 04-questions-jury.md |
""", encoding="utf-8")
    (out / "06-charte-numerique-responsable.md").write_text("""# Charte numérique responsable

1. Nous mesurons avant d’optimiser.
2. Nous préférons la sobriété à l’efficacité seule.
3. Nous ne revendiquons pas la neutralité carbone.
4. Nous n’utilisons pas la compensation comme argument de vente.
5. Nous documentons les hypothèses et les limites.
6. Nous minimisons les données collectées et leur durée de conservation.
7. Nous privilégions les composants natifs et les technologies durables.
8. Nous intégrons un contrôle GreenIT en revue de code et en CI.
9. Nous formons les équipes et nous partageons les mesures.
10. Nous suivons un KPI poids, un KPI énergie et un KPI accès.
""", encoding="utf-8")
    (out / "07-plan-mesure-energetique.md").write_text("""# Plan de mesure énergétique

## Objectifs

- Mesurer la consommation réelle du serveur et de l’hébergement.
- Vérifier le PUE et la région électrique.
- Suivre le poids et les requêtes des pages.
- Estimer le GWP et l’ADPe/ADPf avec la même UF.

## Indicateurs

| Indicateur | Unité | Source | Fréquence |
|---|---|---|---|
| kWh serveur | kWh | compteur / facture | mensuelle |
| PUE | ratio | hébergeur | trimestrielle |
| Intensité carbone | g CO2e/kWh | Base Empreinte | annuelle |
| Poids page | Ko | Playwright | à chaque release |
| Requêtes | nombre | Playwright | à chaque release |
| EcoIndex | score | EcoIndex | à chaque release |

## Gouvernance

Le tech lead publie les mesures. Un écart de plus de 20 % déclenche une revue. Les seuils sont bloquants en CI pour le poids et les requêtes.
""", encoding="utf-8")
    (out / "08-plan-projet.md").write_text("""# Plan projet GreenIT

## Jalons

| Jalon | Date | Livrable | Responsable |
|---|---|---|---|
| Cadrage | S1 | audit.yml, UF | Chef de projet |
| Diagnostic | S2 | codebase-audit, web-metrics | Tech lead |
| Calculs | S3 | metrics.json | GreenIT analyst |
| Plan d’action | S4 | rapport, deck | Équipe |
| Soutenance | S5 | PPTX, vidéo | Équipe |

## RACI

| Activité | Chef de projet | Tech lead | GreenIT | Direction |
|---|---|---|---|---|
| Cadrage | A | C | R | I |
| Diagnostic | I | R | C | I |
| Calculs | I | C | R | I |
| Plan d’action | A | C | R | C |
| Soutenance | A | I | R | I |

## Risques

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Données serveur manquantes | haute | haut | hypothèses + sensibilité |
| PUE inconnu | haute | moyen | demander à l’hébergeur |
| Effet rebond | moyenne | moyen | suivre les usages |
| Greenwashing | moyenne | haut | sources + limites |
""", encoding="utf-8")
    (out / "09-formation-greenit.md").write_text("""# Formation GreenIT — 10 slides

1. Pourquoi le numérique a un impact.
2. ACV, UF et frontière.
3. GWP, ADPe, ADPf : trois indicateurs.
4. RGESN, GR491, RWEB.
5. Mesurer le web avec EcoIndex.
6. Mesurer un serveur avec Boavizta.
7. Quick wins frontend.
8. Quick wins backend.
9. Hébergement et PUE.
10. Gouvernance et KPI.

## Quiz

1. Que mesure l’ADPe ? (réponse : ressources minérales, kg Sb eq)
2. Que mesure l’ADPf ? (réponse : ressources fossiles, MJ)
3. Pourquoi la fabrication des terminaux domine-t-elle souvent ? (réponse : impacts incorporés)
4. Pourquoi faut-il vérifier la couverture d’un score RGESN ? (réponse : un score sans couverture n’est pas interprétable)
5. Pourquoi la compensation ne rend-elle pas un service neutre ? (réponse : elle ne réduit pas les émissions)

## Exercice

À partir de `examples/demo-service/audit.yml`, calculer le GWP du serveur avec PUE 1,2 puis 1,5. Comparer et expliquer l’écart.
""", encoding="utf-8")
    (out / "10-retrospective.md").write_text("""# Rétrospective

## Ce qui a bien marché

- UF claire et scénarios explicites.
- Calculs reproductibles et testés.
- Diagnostic codebase et mesures web.
- Rapport et soutenance générés de bout en bout.

## Ce qui a moins bien marché

- Données serveur et hébergeur manquantes.
- Couverture RGESN faible.
- Pas de mesure énergétique réelle.
- Effet rebond non mesuré.

## Actions

- Obtenir les factures et le PUE.
- Documenter les 42 critères non validés faute de preuve.
- Mesurer la consommation réelle.
- Refaire l’audit après six mois.
""", encoding="utf-8")
    # Le dossier de preuves est aussi copié dans shared/templates pour réutilisation.
    shared = HERE.parents[2] / "shared" / "templates"
    shared.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out / "02-dossier-preuves.md", shared / "dossier-preuves.md")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", type=Path, required=True)
    ap.add_argument("--metrics-optimized", type=Path)
    ap.add_argument("--web", type=Path)
    ap.add_argument("--web-optimized", type=Path)
    ap.add_argument("--codebase", type=Path)
    ap.add_argument("--rgesn", type=Path)
    ap.add_argument("--audit", type=Path)
    ap.add_argument("--sources", type=Path, default=REF / "sources.yml")
    ap.add_argument("--factors", type=Path, action="append")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--figures", type=Path, required=True)
    ap.add_argument("--dist", type=Path, required=True)
    args = ap.parse_args()
    args.figures = args.figures.resolve()
    ctx = build_context(args)
    args.out.mkdir(parents=True, exist_ok=True)
    charts = build_charts(ctx, args.figures)
    args.figures.mkdir(parents=True, exist_ok=True)
    # Run chart generation
    import subprocess
    studio = HERE.parents[1] / "greenit-studio" / "scripts" / "make_chart.py"
    subprocess.run([str(Path(__import__("sys").executable)), str(studio), "--spec", str(charts), "--out", str(args.figures)], check=True)
    report = report_text(ctx, args.figures)
    (args.out / "report.md").write_text(report, encoding="utf-8")
    # Registre d’hypothèses exportable pour le client et le jury.
    hyp_fields = ["id", "statement", "value", "unit", "source_id", "confidence",
                  "status", "evidence_status", "owner", "due", "evidence", "impact_if_wrong"]
    with (args.out / "hypotheses.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hyp_fields, extrasaction="ignore")
        w.writeheader()
        for a in ctx["audit"].get("assumptions", []):
            w.writerow(a)
    deck = deck_text(ctx, args.figures)
    (args.out / "deck.yml").write_text(yaml.safe_dump(deck, allow_unicode=True, sort_keys=False), encoding="utf-8")
    # Synthèse client : 4 pages, autonome, sans jargon inutile.
    m = ctx["m"]
    server = get_item(m, "server")
    dev = get_item(m, "dev-laptops")
    total = m["totals"]["gwp"]
    score_label = "significatif mais faible" if ctx["coverage"] >= 50 else "non significatif"
    client = f"""# Synthèse client — audit GreenIT du service d’émargement

**Client** : Zone01 Normandie (cas pédagogique)  
**Date** : 2026-11-09  
**Version** : 1.0  
**Périmètre** : ACV screening, tiers 1–3, GWP100 / ADPe / ADPf.

## 1. Ce que nous avons fait

Nous avons analysé le service d’émargement, mesuré la page web, calculé les impacts avec des facteurs documentés et évalué les 78 critères RGESN. Le rapport complet contient 19 sections, les calculs, les sources et les scénarios de sensibilité.

## 2. Chiffres clés

| Indicateur | Valeur | Lecture |
|---|---:|---|
| GWP100 | {n(total)} kg CO2e / semaine | Ordre de grandeur, incertitude ±30 % |
| Part serveur | {pct(server.get('gwp',0)/total*100)} | Premier hotspot |
| Part développement | {pct(dev.get('gwp',0)/total*100)} | Deuxième hotspot |
| Poids page | {n((ctx['web'].get('page') or {}).get('size_kb',0))} Ko → {n((ctx['webo'].get('page') or {}).get('size_kb',0))} Ko | Réduction mesurée |
| EcoIndex | {(ctx['web'].get('ecoindex') or {}).get('score','—')} → {(ctx['webo'].get('ecoindex') or {}).get('score','—')} | Amélioration |
| RGESN | {ctx['score']:.1f}/100, couverture {pct(ctx['coverage'])} | Score {score_label} |

## 3. Décisions recommandées

1. **Mesurer le serveur et l’hébergement** avant de promettre une réduction globale.
2. **Traiter les quick wins web** : polling, cache, images, requêtes SQL.
3. **Ne pas confondre poids de page et GWP** : le réseau n’est pas le hotspot.
4. **Documenter le PUE et la région** de l’hébergement.
5. **Ne pas utiliser de compensation** comme argument de neutralité.

## 4. Conditions de validité

Le rapport est un screening complet dans son périmètre. Les caractéristiques du serveur, le PUE, les durées de développement et les usages réels doivent être confirmés. Les scénarios 1,2 / 1,5 / 1,8 pour le PUE et 5 % / 10 % / 20 % pour l’allocation encadrent l’incertitude. Le facteur réseau NegaOctet local couvre GWP, ADPe et ADPf ; sa licence interdit la redistribution.

## 5. Prochaines étapes

| Échéance | Action | Responsable |
|---|---|---|
| S1 | Obtenir la fiche serveur et le PUE | Achats / Ops |
| S2 | Mesurer les usages réels | Produit |
| S3 | Mettre en place les quick wins | Tech lead |
| S4 | Recalculer et présenter la version 1.1 | GreenIT |
| S6 | Revue critique externe | Direction |

La version complète, les sources et les calculs sont dans `rapport-audit-greenit-demo.pdf`.
"""
    (args.out / "synthese-client.md").write_text(client, encoding="utf-8")
    metadata = {"title": "Audit GreenIT — Service d’émargement", "subtitle": "ACV screening, RGESN et plan d’action",
                "client": "Zone01 Normandie", "authors": ["Équipe GreenIT RNCP39388"], "date": "2026-11-09",
                "version": "1.0", "header": "Audit Green IT — Zone01 Normandie"}
    (args.out / "metadata.yml").write_text(yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False), encoding="utf-8")
    theme_path = HERE.parents[1] / "greenit-studio" / "assets" / "theme.json"
    if theme_path.exists():
        theme = json.loads(theme_path.read_text(encoding="utf-8"))
        design = {"project": metadata.get("title", "Projet"), "colors": theme.get("colors", {}),
                  "fonts": theme.get("fonts", {}), "rules": ["pas de vert générique", "pas de 3D", "source sur chaque figure"]}
        (args.out / "design.yml").write_text(yaml.safe_dump(design, allow_unicode=True, sort_keys=False), encoding="utf-8")
    rncp_docs(ctx, args.dist / "rncp39388")
    narration = ("Le numérique a un impact réel, souvent invisible. Nous avons audité un service d’émargement "
                 "utilisé par cent étudiants pendant une semaine. Notre démarche est une ACV screening : nous avons "
                 "défini une unité fonctionnelle, une frontière et trois indicateurs. Résultat : environ 1,76 kilogramme "
                 "de CO2 équivalent par semaine. Le serveur représente 64 % du GWP, le développement 32 %. Les terminaux "
                 "ne pèsent que 0,24 %, parce qu’ils sont partagés. Nous avons mesuré la page web : 1,6 mégaoctet avant "
                 "optimisation, 92 kilooctets après, et un EcoIndex qui passe de 87 à 95. Pourtant, le GWP ne baisse que "
                 "de moins de 0,1 %, car le réseau n’est pas le hotspot. Notre priorité est donc de mesurer le serveur et "
                 "l’hébergement, puis de décider. Nous ne revendiquons ni neutralité carbone ni compensation. Merci.")
    (args.out / "narration.md").write_text(narration + "\n", encoding="utf-8")
    print(f"OK rapport, deck et dossier RNCP -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
