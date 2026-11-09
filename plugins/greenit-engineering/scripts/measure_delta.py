#!/usr/bin/env python3
"""Compare deux fichiers JSON de métriques et produit un delta."""
from __future__ import annotations
import argparse, json
from pathlib import Path


def find_numbers(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(find_numbers(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        out[prefix] = float(obj)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", type=Path, required=True)
    ap.add_argument("--after", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    before = json.loads(args.before.read_text(encoding="utf-8"))
    after = json.loads(args.after.read_text(encoding="utf-8"))
    b, a = find_numbers(before), find_numbers(after)
    keys = sorted(set(b) & set(a))
    rows = []
    for k in keys:
        delta = a[k] - b[k]
        pct = (delta / b[k] * 100) if b[k] else None
        rows.append({"metric": k, "before": b[k], "after": a[k], "delta": delta, "delta_pct": pct})
    report = {"before": str(args.before), "after": str(args.after), "metrics": rows}
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
