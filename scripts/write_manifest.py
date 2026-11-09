#!/usr/bin/env python3
"""Écrit un manifest SHA256 des livrables d’un dossier dist."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", type=Path, required=True)
    args = ap.parse_args()
    dist = args.dist.resolve()
    files = []
    for p in sorted(dist.rglob("*")):
        if not p.is_file() or p.name == "manifest.json":
            continue
        files.append({"path": p.relative_to(dist).as_posix(), "bytes": p.stat().st_size,
                      "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    (dist / "manifest.json").write_text(json.dumps({"files": files}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK manifest {len(files)} fichiers -> {dist / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
