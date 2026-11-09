#!/usr/bin/env python3
"""Software Carbon Intensity (SCI), ISO/IEC 21031:2024.

SCI = (O + M) / R
O = E × I
M = TE × (t / D) × RS
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SCIResult:
    operational_g: float
    embodied_g: float
    sci_g_per_unit: float


def compute(energy_kwh: float, intensity_g_per_kwh: float, embodied_g: float,
            use_hours: float, lifetime_hours: float, resource_share: float,
            functional_unit: float) -> SCIResult:
    if min(energy_kwh, intensity_g_per_kwh, embodied_g, use_hours,
           lifetime_hours, resource_share, functional_unit) < 0:
        raise ValueError("Les valeurs SCI doivent être positives")
    if lifetime_hours <= 0:
        raise ValueError("lifetime_hours doit être > 0")
    if functional_unit <= 0:
        raise ValueError("functional_unit doit être > 0")
    if resource_share > 1:
        raise ValueError("resource_share doit être dans [0, 1]")
    operational = energy_kwh * intensity_g_per_kwh
    embodied = embodied_g * (use_hours / lifetime_hours) * resource_share
    return SCIResult(operational, embodied, (operational + embodied) / functional_unit)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--energy-kwh", type=float, required=True)
    ap.add_argument("--intensity-g-per-kwh", type=float, required=True)
    ap.add_argument("--embodied-g", type=float, required=True)
    ap.add_argument("--use-hours", type=float, required=True)
    ap.add_argument("--lifetime-hours", type=float, required=True)
    ap.add_argument("--resource-share", type=float, required=True)
    ap.add_argument("--functional-unit", type=float, required=True)
    a = ap.parse_args()
    r = compute(a.energy_kwh, a.intensity_g_per_kwh, a.embodied_g, a.use_hours,
                a.lifetime_hours, a.resource_share, a.functional_unit)
    print(f"O={r.operational_g:.6g} g M={r.embodied_g:.6g} g SCI={r.sci_g_per_unit:.6g} g/unité")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
