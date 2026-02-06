"""
Coverage Planning Tool

Estimates relay count + spacing for a given area and radio radius.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class CoveragePlan:
    area_km2: float
    relay_radius_km: float
    redundancy: int
    estimated_relays: int
    recommended_spacing_km: float
    coverage_per_relay_km2: float


def plan_coverage(area_km2: float, relay_radius_km: float, redundancy: int = 1) -> CoveragePlan:
    if area_km2 <= 0 or relay_radius_km <= 0 or redundancy <= 0:
        raise ValueError("Inputs must be positive")

    # Hex grid coverage: area per relay ~ 2.598 * r^2
    coverage_per_relay = 2.598 * (relay_radius_km ** 2)
    base_relays = math.ceil(area_km2 / coverage_per_relay)
    estimated_relays = base_relays * redundancy
    spacing = relay_radius_km * 1.5

    return CoveragePlan(
        area_km2=area_km2,
        relay_radius_km=relay_radius_km,
        redundancy=redundancy,
        estimated_relays=estimated_relays,
        recommended_spacing_km=round(spacing, 2),
        coverage_per_relay_km2=round(coverage_per_relay, 2),
    )
