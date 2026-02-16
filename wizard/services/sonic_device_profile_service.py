"""Sonic device profile auto-detection and recommendations."""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Any, Dict, Optional


class SonicDeviceProfileService:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent

    @staticmethod
    def _detect_ram_gb() -> Optional[float]:
        # POSIX path
        try:
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
            if isinstance(pages, int) and isinstance(page_size, int) and pages > 0 and page_size > 0:
                return round((pages * page_size) / (1024 ** 3), 2)
        except Exception:
            pass
        return None

    @staticmethod
    def _detect_uefi() -> bool:
        if os.name == "posix" and Path("/sys/firmware/efi").exists():
            return True
        # On macOS and Windows, modern machines are effectively UEFI.
        if platform.system().lower() in {"darwin", "windows"}:
            return True
        return False

    def auto_detect_profile(self) -> Dict[str, Any]:
        ram_gb = self._detect_ram_gb()
        cpu_count = os.cpu_count() or 1
        arch = platform.machine().lower()
        system = platform.system().lower()
        uefi_native = self._detect_uefi()

        if (ram_gb is not None and ram_gb >= 16) and cpu_count >= 8:
            tier = "high"
        elif (ram_gb is not None and ram_gb >= 8) and cpu_count >= 4:
            tier = "medium"
        else:
            tier = "baseline"

        return {
            "detected": {
                "hostname": platform.node(),
                "system": system,
                "arch": arch,
                "cpu_count": cpu_count,
                "ram_gb": ram_gb,
                "uefi_native": uefi_native,
            },
            "tier": tier,
        }

    def get_recommendations(self) -> Dict[str, Any]:
        profile = self.auto_detect_profile()
        tier = profile["tier"]
        detected = profile["detected"]

        if tier == "high":
            windows_mode = "gaming"
            boot_profile = "udos-windows-entertainment"
            launcher = "playnite"
        elif tier == "medium":
            windows_mode = "media"
            boot_profile = "udos-windows-entertainment"
            launcher = "kodi"
        else:
            windows_mode = "install"
            boot_profile = "udos-alpine"
            launcher = "kodi"

        return {
            "profile": profile,
            "recommendations": {
                "boot_profile_id": boot_profile,
                "windows_mode": windows_mode,
                "windows_launcher": launcher,
                "wizard_profile": "udos-ubuntu-wizard" if tier in {"high", "medium"} else "udos-alpine",
                "notes": [
                    "Auto-detected recommendations are advisory and should be confirmed before flashing.",
                    "Use Sonic boot route + Windows launcher mode endpoints to apply these values.",
                ],
            },
            "confidence": 0.55 if detected["ram_gb"] is None else 0.7,
        }


def get_sonic_device_profile_service(repo_root: Optional[Path] = None) -> SonicDeviceProfileService:
    return SonicDeviceProfileService(repo_root=repo_root)
