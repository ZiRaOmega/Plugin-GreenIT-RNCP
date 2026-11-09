#!/usr/bin/env python3
"""Implémentation de la formule EcoIndex.

Source : cnumr/EcoIndex_python, composant `ecoindex.compute.ecoindex`,
quantiles `ecoindex.data.quantiles`, licence CC BY-NC-ND.
Usage non commercial ; toute réutilisation commerciale nécessite un accord.
"""
from __future__ import annotations

from dataclasses import dataclass

QUANTILES_DOM = [0, 47, 75, 159, 233, 298, 358, 417, 476, 537, 603, 674, 753, 843,
                 949, 1076, 1237, 1459, 1801, 2479, 594601]
QUANTILES_REQ = [0, 2, 15, 25, 34, 42, 49, 56, 63, 70, 78, 86, 95, 105, 117, 130,
                 147, 170, 205, 281, 3920]
QUANTILES_SIZE = [0, 1.37, 144.7, 319.53, 479.46, 631.97, 783.38, 937.91, 1098.62,
                  1265.47, 1448.32, 1648.27, 1876.08, 2142.06, 2465.37, 2866.31,
                  3401.59, 4155.73, 5400.08, 8037.54, 223212.26]
GRADES = {"A": 80, "B": 70, "C": 55, "D": 40, "E": 25, "F": 10, "G": 0}


def quantile(quantiles: list[float], value: float) -> float:
    """Quantile interpolé, identique à `get_quantile` du projet upstream."""
    for i in range(1, len(quantiles)):
        if value < quantiles[i]:
            return (i - 1) + (value - quantiles[i - 1]) / (quantiles[i] - quantiles[i - 1])
    return len(quantiles) - 1


def score(dom: int, requests: int, size_kb: float) -> int:
    q_dom = quantile(QUANTILES_DOM, dom)
    q_req = quantile(QUANTILES_REQ, requests)
    q_size = quantile(QUANTILES_SIZE, size_kb)
    return round(100 - 5 * (3 * q_dom + 2 * q_req + q_size) / 6)


def grade(score_value: float) -> str:
    for letter in "ABCDEF":
        if score_value > GRADES[letter]:
            return letter
    return "G"


def greenhouse_gases(score_value: float) -> float:
    return round(100 * (2 + 2 * (50 - score_value) / 100)) / 100


def water(score_value: float) -> float:
    return round(100 * (3 + 3 * (50 - score_value) / 100)) / 100


@dataclass(frozen=True)
class EcoIndexResult:
    score: int
    grade: str
    ges_g: float
    water_cl: float


def compute(dom: int, requests: int, size_kb: float) -> EcoIndexResult:
    if dom < 0 or requests < 0 or size_kb < 0:
        raise ValueError("Les valeurs EcoIndex doivent être positives")
    s = score(dom, requests, size_kb)
    return EcoIndexResult(score=s, grade=grade(s), ges_g=greenhouse_gases(s), water_cl=water(s))


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dom", type=int, required=True)
    ap.add_argument("--requests", type=int, required=True)
    ap.add_argument("--size-kb", type=float, required=True)
    args = ap.parse_args()
    r = compute(args.dom, args.requests, args.size_kb)
    print(f"score={r.score} grade={r.grade} ges={r.ges_g} g eau={r.water_cl} cl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
