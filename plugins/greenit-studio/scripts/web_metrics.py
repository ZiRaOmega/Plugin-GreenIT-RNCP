#!/usr/bin/env python3
"""Mesure locale des métriques web avec Playwright et calcule EcoIndex."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "greenit-audit" / "scripts"))
try:
    from ecoindex import compute as ecoindex_compute
except Exception:  # pragma: no cover
    ecoindex_compute = None


def measure(url: str) -> dict:
    from playwright.sync_api import sync_playwright
    executable = os.environ.get("CHROMIUM_PATH") or shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    with sync_playwright() as p:
        launch_kwargs = {"headless": True}
        if executable:
            launch_kwargs["executable_path"] = executable
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
        page = context.new_page()
        responses: dict[str, dict] = {}

        def on_response(resp):
            try:
                headers = resp.headers
                req = resp.request
                responses[req.url] = {
                    "url": req.url, "status": resp.status, "resource_type": req.resource_type,
                    "cache_control": headers.get("cache-control", ""),
                    "content_encoding": headers.get("content-encoding", ""),
                    "content_type": headers.get("content-type", ""),
                }
            except Exception:
                pass

        page.on("response", on_response)
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)
        data = page.evaluate("""() => {
          const resources = performance.getEntriesByType('resource').map(r => ({
            name: r.name, initiatorType: r.initiatorType,
            transferSize: r.transferSize || 0, encodedBodySize: r.encodedBodySize || 0,
            decodedBodySize: r.decodedBodySize || 0, duration: r.duration || 0
          }));
          const nav = performance.getEntriesByType('navigation')[0] || {};
          const all = document.querySelectorAll('*');
          let svgChildren = 0;
          all.forEach(el => { if (el.closest('svg')) svgChildren++; });
          return {
            dom_nodes: all.length - svgChildren,
            resource_count: resources.length,
            resources,
            navigation: {transferSize: nav.transferSize || 0, encodedBodySize: nav.encodedBodySize || 0,
                         decodedBodySize: nav.decodedBodySize || 0, domContentLoaded: nav.domContentLoadedEventEnd || 0,
                         load: nav.loadEventEnd || 0},
            title: document.title,
            lang: document.documentElement.lang || ''
          };
        }""")
        browser.close()
    total_bytes = data["navigation"]["transferSize"] + sum(
        (r["transferSize"] or r["encodedBodySize"]) for r in data["resources"]
    )
    size_kb = total_bytes / 1024
    request_count = data["resource_count"] + 1
    by_type: dict[str, dict] = {}
    domains: dict[str, int] = {}
    cache_ok = 0
    compressed = 0
    for r in data["resources"]:
        t = r["initiatorType"] or "other"
        by_type.setdefault(t, {"count": 0, "bytes": 0})
        by_type[t]["count"] += 1
        by_type[t]["bytes"] += r["transferSize"] or r["encodedBodySize"]
        host = urlparse(r["name"]).netloc
        domains[host] = domains.get(host, 0) + 1
        meta = responses.get(r["name"], {})
        if meta.get("cache_control"):
            cache_ok += 1
        if meta.get("content_encoding") in {"gzip", "br", "deflate"}:
            compressed += 1
    base_host = urlparse(url).netloc
    third_party = {h: n for h, n in domains.items() if h and h != base_host}
    eco = None
    if ecoindex_compute:
        try:
            eco = ecoindex_compute(dom=int(data["dom_nodes"]), requests=int(request_count), size_kb=float(size_kb))
            eco = eco.__dict__
        except Exception:
            eco = None
    return {
        "meta": {"url": url, "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "engine": "web_metrics.py"},
        "page": {"title": data.get("title"), "lang": data.get("lang"), "dom_nodes": data["dom_nodes"],
                 "requests": request_count, "bytes": total_bytes, "size_kb": round(size_kb, 3),
                 "cache_control_resources": cache_ok, "compressed_resources": compressed,
                 "third_party_domains": third_party, "by_type": by_type},
        "navigation": data["navigation"],
        "resources": data["resources"],
        "ecoindex": eco,
    }


def markdown(m: dict) -> str:
    p = m["page"]
    lines = ["# Métriques web", "", f"URL : `{m['meta']['url']}`", "",
             "| Métrique | Valeur |", "|---|---:|",
             f"| Nœuds DOM | {p['dom_nodes']} |",
             f"| Requêtes | {p['requests']} |",
             f"| Octets transférés | {p['bytes']} |",
             f"| Taille | {p['size_kb']} Ko |",
             f"| Ressources avec cache | {p['cache_control_resources']} |",
             f"| Ressources compressées | {p['compressed_resources']} |"]
    if m.get("ecoindex"):
        e = m["ecoindex"]
        lines += ["", f"EcoIndex : **{e['score']}** ({e['grade']}), GES {e['ges_g']} g, eau {e['water_cl']} cl."]
    if p["third_party_domains"]:
        lines += ["", "Domaines tiers : " + ", ".join(f"`{k}` ({v})" for k, v in p["third_party_domains"].items())]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()
    try:
        m = measure(args.url)
    except Exception as e:
        print(f"AVERTISSEMENT : mesure web impossible ({e})", file=sys.stderr)
        m = {"meta": {"url": args.url, "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                      "engine": "web_metrics.py", "error": str(e)}, "page": None, "resources": [], "ecoindex": None}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.out.with_suffix(".md").write_text(markdown(m) if m.get("page") else "# Métriques web\n\nMesure indisponible.\n", encoding="utf-8")
    if m.get("page"):
        print(f"OK DOM={m['page']['dom_nodes']} req={m['page']['requests']} size={m['page']['size_kb']} Ko -> {args.out}")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
