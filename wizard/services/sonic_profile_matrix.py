"""Canonical Sonic device/gaming profile matrix."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from core.services.system_capability_service import get_system_capability_service


class SonicTier(StrEnum):
    BASELINE = "baseline"
    MEDIUM = "medium"
    HIGH = "high"


class SonicGpuLane(StrEnum):
    AMD = "amd"
    INTEL = "intel"
    HEADLESS = "headless"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SonicHardwareContext:
    hostname: str
    system: str
    arch: str
    processor: str
    cpu_count: int
    ram_gb: float | None
    uefi_native: bool
    headless: bool


def detect_hardware_context() -> SonicHardwareContext:
    capability = get_system_capability_service().measure()
    return SonicHardwareContext(
        hostname=capability.hostname,
        system=capability.system.lower(),
        arch=capability.arch,
        processor=capability.processor,
        cpu_count=capability.cpu_cores,
        ram_gb=capability.ram_gb,
        uefi_native=capability.uefi_native,
        headless=capability.headless,
    )


_RECOMMENDATIONS_BY_TIER: dict[SonicTier, dict[str, str]] = {
    SonicTier.HIGH: {
        "windows_mode": "gaming",
        "boot_profile_id": "udos-windows-entertainment",
        "windows_launcher": "playnite",
        "wizard_profile": "udos-ubuntu-wizard",
    },
    SonicTier.MEDIUM: {
        "windows_mode": "media",
        "boot_profile_id": "udos-windows-entertainment",
        "windows_launcher": "kodi",
        "wizard_profile": "udos-ubuntu-wizard",
    },
    SonicTier.BASELINE: {
        "windows_mode": "install",
        "boot_profile_id": "udos-alpine",
        "windows_launcher": "kodi",
        "wizard_profile": "udos-alpine",
    },
}

_GPU_HINT_BY_LANE: dict[SonicGpuLane, str] = {
    SonicGpuLane.AMD: "max_performance",
    SonicGpuLane.INTEL: "balanced",
    SonicGpuLane.HEADLESS: "encoder_priority",
    SonicGpuLane.UNKNOWN: "balanced",
}


def resolve_tier(*, ram_gb: float | None, cpu_count: int) -> SonicTier:
    match (ram_gb, cpu_count):
        case (ram, cpus) if ram is not None and ram >= 16 and cpus >= 8:
            return SonicTier.HIGH
        case (ram, cpus) if ram is not None and ram >= 8 and cpus >= 4:
            return SonicTier.MEDIUM
        case _:
            return SonicTier.BASELINE


def resolve_gpu_lane(*, arch: str, processor: str, headless: bool) -> SonicGpuLane:
    if headless:
        return SonicGpuLane.HEADLESS

    fingerprint = f"{arch} {processor}".lower()
    match fingerprint:
        case text if "amd" in text or "ryzen" in text or "radeon" in text:
            return SonicGpuLane.AMD
        case text if "intel" in text:
            return SonicGpuLane.INTEL
        case _:
            return SonicGpuLane.UNKNOWN


def get_tier_recommendations(tier: SonicTier) -> dict[str, str]:
    return dict(_RECOMMENDATIONS_BY_TIER[tier])


def get_windows_profile_templates(gpu_lane: SonicGpuLane) -> dict[str, dict[str, Any]]:
    gpu_hint = _GPU_HINT_BY_LANE[gpu_lane]
    return {
        "performance": {
            "power_plan": "high_performance",
            "launchers": ["steam", "epic", "playnite"],
            "background_services": {"windows_update": "deferred", "indexing": "reduced"},
            "gpu_hint": gpu_hint if gpu_lane != SonicGpuLane.HEADLESS else "encoder_priority",
        },
        "balanced": {
            "power_plan": "balanced",
            "launchers": ["steam", "playnite"],
            "background_services": {"windows_update": "normal", "indexing": "normal"},
            "gpu_hint": "balanced",
        },
        "streaming": {
            "power_plan": "balanced",
            "launchers": ["steam", "obs", "playnite"],
            "background_services": {"windows_update": "deferred", "indexing": "reduced"},
            "gpu_hint": "encoder_priority",
        },
    }
