#!/usr/bin/env python3
"""Orchestre la démonstration de bout en bout."""
from __future__ import annotations

import hashlib
import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
DIST = ROOT / "dist"
DEMO = ROOT / "examples" / "demo-service"
OPT = ROOT / "examples" / "demo-service-optimized"


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print("$", " ".join(str(x) for x in cmd))
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.returncode != 0:
        print(p.stdout)
        print(p.stderr, file=sys.stderr)
        raise SystemExit(f"Échec : {' '.join(str(x) for x in cmd)}")
    if p.stdout.strip():
        print(p.stdout.strip())


def wait_port(port: int, timeout: float = 15.0) -> None:
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.2)
    raise RuntimeError(f"port {port} indisponible")


def start_server(script: Path, port: int) -> subprocess.Popen:
    p = subprocess.Popen([PY, str(script), "--port", str(port)], cwd=ROOT,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        wait_port(port)
    except Exception:
        p.terminate()
        raise
    return p


def stop_server(p: subprocess.Popen) -> None:
    p.terminate()
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()


def write_manifest() -> None:
    manifest = []
    for path in sorted(DIST.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.append({"path": path.relative_to(DIST).as_posix(), "bytes": path.stat().st_size, "sha256": h})
    (DIST / "manifest.json").write_text(json.dumps({"files": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "audit-demo").mkdir(parents=True, exist_ok=True)
    (DIST / "figures").mkdir(parents=True, exist_ok=True)
    (DIST / "rncp39388").mkdir(parents=True, exist_ok=True)

    audit = DEMO / "audit.yml"
    local = ROOT / "plugins/greenit-audit/references/factors.local.csv"
    if not local.exists():
        local = ROOT / "plugins/greenit-audit/references/factors.local.example.csv"
    factors = ["--factors", str(ROOT / "plugins/greenit-audit/references/factors.open.csv"),
               "--factors", str(local)]
    run([PY, "plugins/greenit-audit/scripts/validate_audit.py", "--input", str(audit), *factors])
    run([PY, "plugins/greenit-studio/scripts/scan_codebase.py", "--root", str(DEMO),
         "--out", str(DIST / "audit-demo/codebase-audit.json"), "--markdown"])

    server = start_server(DEMO / "api" / "server.py", 8771)
    try:
        run([PY, "plugins/greenit-studio/scripts/web_metrics.py", "--url", "http://127.0.0.1:8771/",
             "--out", str(DIST / "audit-demo/web-metrics.json"), "--markdown"])
    finally:
        stop_server(server)

    run([PY, "scripts/optimize_demo.py", "--src", str(DEMO), "--dst", str(OPT)])
    run([PY, "plugins/greenit-studio/scripts/scan_codebase.py", "--root", str(OPT),
         "--out", str(DIST / "audit-demo/codebase-audit-optimized.json"), "--markdown"])
    server = start_server(OPT / "api" / "server.py", 8772)
    try:
        run([PY, "plugins/greenit-studio/scripts/web_metrics.py", "--url", "http://127.0.0.1:8772/",
             "--out", str(DIST / "audit-demo/web-metrics-optimized.json"), "--markdown"])
    finally:
        stop_server(server)

    # Les volumes réseau sont dérivés des pages réellement mesurées, pas saisis à la main.
    def network_gb(page_kb: float) -> tuple[float, float]:
        mobile = (100 * (10 * 0.5 + page_kb)) / (1024 * 1024)
        fixed = (1 * page_kb) / (1024 * 1024)
        return round(mobile, 6), round(fixed, 6)

    def with_network(source: Path, page_kb: float, out: Path) -> Path:
        a = yaml.safe_load(source.read_text(encoding="utf-8"))
        mobile, fixed = network_gb(page_kb)
        for item in a["inventory"]["items"]:
            if item["id"] == "network-mobile":
                item["gb"] = mobile
                item["notes"] = f"Volume mobile dérivé de la page mesurée ({page_kb:.1f} Ko) ; voir H7."
            if item["id"] == "network-fixed":
                item["gb"] = fixed
                item["notes"] = f"Volume fixe dérivé de la page mesurée ({page_kb:.1f} Ko) ; voir H7."
        for h in a.get("assumptions", []):
            if h["id"] == "H7":
                h["statement"] = f"Le volume réseau est dérivé de la page mesurée ({page_kb:.1f} Ko) : {fixed:g} Go fixe et {mobile:g} Go mobile."
                h["value"] = round(mobile + fixed, 6)
        out.write_text(yaml.safe_dump(a, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return out

    baseline_web = json.loads((DIST / "audit-demo/web-metrics.json").read_text(encoding="utf-8"))
    baseline_audit = with_network(audit, float(baseline_web["page"]["size_kb"]), DIST / "audit-demo/audit-baseline.yml")
    run([PY, "plugins/greenit-audit/scripts/calc.py", "--input", str(baseline_audit), *factors,
         "--out", str(DIST / "audit-demo/metrics.json"), "--markdown"])
    optimized_web = json.loads((DIST / "audit-demo/web-metrics-optimized.json").read_text(encoding="utf-8"))
    opt_audit_path = with_network(audit, float(optimized_web["page"]["size_kb"]), DIST / "audit-demo/audit-optimized.yml")
    run([PY, "plugins/greenit-audit/scripts/calc.py", "--input", str(opt_audit_path), *factors,
         "--out", str(DIST / "audit-demo/metrics-optimized.json"), "--markdown"])
    run([PY, "plugins/greenit-audit/scripts/score_rgesn.py", "--assessment", str(DEMO / "rgesn-assessment.yml"),
         "--out", str(DIST / "audit-demo/rgesn-score.csv"), "--markdown", str(DIST / "audit-demo/rgesn-summary.md")])
    run([PY, "plugins/greenit-audit/scripts/build_audit_pack.py",
         "--metrics", str(DIST / "audit-demo/metrics.json"),
         "--metrics-optimized", str(DIST / "audit-demo/metrics-optimized.json"),
         "--web", str(DIST / "audit-demo/web-metrics.json"),
         "--web-optimized", str(DIST / "audit-demo/web-metrics-optimized.json"),
         "--codebase", str(DIST / "audit-demo/codebase-audit.json"),
         "--rgesn", str(DIST / "audit-demo/rgesn-score.csv"),
         "--audit", str(baseline_audit),
         "--project", str(DEMO),
         "--factors", str(ROOT / "plugins/greenit-audit/references/factors.open.csv"),
         "--factors", str(ROOT / "plugins/greenit-audit/references/factors.local.example.csv"),
         "--out", str(DIST / "audit-demo"),
         "--figures", str(DIST / "figures"),
         "--dist", str(DIST)])
    run([PY, "plugins/greenit-studio/scripts/md_to_docx.py",
         "--input", str(DIST / "audit-demo/report.md"),
         "--metadata", str(DIST / "audit-demo/metadata.yml"),
         "--figures", str(DIST / "figures"),
         "--out", str(DIST / "rapport-audit-greenit-demo.docx"), "--pdf"])
    run([PY, "plugins/greenit-studio/scripts/md_to_docx.py",
         "--input", str(DIST / "audit-demo/synthese-client.md"),
         "--metadata", str(DIST / "audit-demo/metadata.yml"),
         "--figures", str(DIST / "figures"),
         "--out", str(DIST / "synthese-client-greenit-demo.docx"), "--pdf"])
    run([PY, "plugins/greenit-studio/scripts/build_deck.py",
         "--input", str(DIST / "audit-demo/deck.yml"),
         "--out", str(DIST / "soutenance-greenit-demo.pptx"),
         "--notes", str(DIST / "notes-orales-demo.md"), "--pdf"])
    run([PY, "plugins/greenit-studio/scripts/build_video.py",
         "--deck", str(DIST / "soutenance-greenit-demo.pptx"),
         "--narration", str(DIST / "audit-demo/narration.md"),
         "--out", str(DIST / "teaser-greenit-demo.mp4")])
    write_manifest()
    print("DEMO OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
