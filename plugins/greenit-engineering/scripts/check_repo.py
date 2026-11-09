#!/usr/bin/env python3
"""Contrôle rapide d’un dépôt : gros fichiers, secrets, TODO, tests, git."""
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path

SKIP = {".git", "node_modules", ".venv", "dist", "build", "vendor", "__pycache__"}
SECRET = re.compile(r"(?i)(password|secret|api[_-]?key|token)\s*[:=]\s*['\"]([^'\"]{4,})['\"]")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    root = args.root.resolve()
    files = []
    for p in root.rglob("*"):
        if p.is_file() and not any(part in SKIP for part in p.parts):
            files.append(p)
    big = [{"path": str(p.relative_to(root)), "bytes": p.stat().st_size} for p in files if p.stat().st_size > 1_000_000]
    todos = []
    secrets = []
    for p in files:
        if p.suffix.lower() not in {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".sql", ".yml", ".yaml", ".md"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if re.search(r"\b(TODO|FIXME)\b", line):
                todos.append({"file": str(p.relative_to(root)), "line": i})
            if SECRET.search(line):
                secrets.append({"file": str(p.relative_to(root)), "line": i})
    git = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True)
    report = {"root": str(root), "files": len(files), "big_files": big[:20],
              "todos": todos[:50], "secrets": secrets[:20],
              "tests_present": (root / "tests").is_dir(),
              "git_dirty": bool(git.stdout.strip()) if git.returncode == 0 else None}
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
