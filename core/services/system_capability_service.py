"""Stdlib-only local system capability measurement for core and extensions."""

from __future__ import annotations

import os
import platform
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.services.path_service import get_repo_root


@dataclass(frozen=True)
class MinimumSystemSpec:
    cpu_cores: int = 2
    ram_gb: float = 4.0
    storage_free_gb: float = 5.0


@dataclass(frozen=True)
class SystemCapability:
    hostname: str
    system: str
    release: str
    arch: str
    processor: str
    cpu_cores: int
    ram_gb: float
    storage_free_gb: float
    storage_total_gb: float
    uefi_native: bool
    headless: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MinimumSpecResult:
    targets: MinimumSystemSpec
    overall: bool
    cpu: bool
    ram: bool
    storage: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "targets": asdict(self.targets),
            "result": {
                "overall": self.overall,
                "cpu": self.cpu,
                "ram": self.ram,
                "storage": self.storage,
            },
        }


class SystemCapabilityService:
    """Measure local device capability without network or optional deps."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()

    def measure(self) -> SystemCapability:
        disk = shutil.disk_usage(str(self.repo_root))
        return SystemCapability(
            hostname=platform.node(),
            system=platform.system(),
            release=platform.release(),
            arch=platform.machine().lower(),
            processor=(platform.processor() or "").lower(),
            cpu_cores=os.cpu_count() or 1,
            ram_gb=round(self._detect_ram_gb(), 2),
            storage_free_gb=round(disk.free / (1024**3), 2),
            storage_total_gb=round(disk.total / (1024**3), 2),
            uefi_native=self._detect_uefi(),
            headless=not bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")),
        )

    def evaluate_minimum_spec(
        self,
        minimum_spec: MinimumSystemSpec | None = None,
    ) -> tuple[SystemCapability, MinimumSpecResult]:
        targets = minimum_spec or MinimumSystemSpec()
        capability = self.measure()
        meets_cpu = capability.cpu_cores >= targets.cpu_cores
        meets_ram = capability.ram_gb >= targets.ram_gb
        meets_storage = capability.storage_free_gb >= targets.storage_free_gb
        return capability, MinimumSpecResult(
            targets=targets,
            overall=all((meets_cpu, meets_ram, meets_storage)),
            cpu=meets_cpu,
            ram=meets_ram,
            storage=meets_storage,
        )

    def _detect_ram_gb(self) -> float:
        if pages := self._sysconf_pages():
            return pages / (1024**3)
        try:
            import psutil

            return psutil.virtual_memory().total / (1024**3)
        except Exception:
            return 0.0

    def _sysconf_pages(self) -> int | None:
        try:
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
        except (ValueError, OSError, AttributeError):
            return None
        if not isinstance(pages, int) or not isinstance(page_size, int):
            return None
        if pages <= 0 or page_size <= 0:
            return None
        return pages * page_size

    def _detect_uefi(self) -> bool:
        if os.name == "posix" and Path("/sys/firmware/efi").exists():
            return True
        return platform.system().lower() in {"darwin", "windows"}


def get_system_capability_service(
    repo_root: Path | None = None,
) -> SystemCapabilityService:
    return SystemCapabilityService(repo_root=repo_root)
