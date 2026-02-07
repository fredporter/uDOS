"""System stats service for Wizard."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class SystemStatsService:
    repo_root: Path

    def get_system_stats(self) -> Dict[str, Any]:
        cpu_count = os.cpu_count() or 1
        try:
            load1, load5, load15 = os.getloadavg()
        except OSError:
            load1 = load5 = load15 = 0.0

        load_per_cpu = round(load1 / cpu_count, 2) if cpu_count else 0.0
        memory = self._read_memory_stats()
        swap = self._read_swap_stats()
        disk = self._read_disk_stats()
        uptime_seconds = self._get_uptime_seconds()
        process_count = self._get_process_count()

        overload_reasons: List[str] = []
        if load_per_cpu > 1.25:
            overload_reasons.append("cpu_load_high")
        if memory["used_percent"] > 95:
            overload_reasons.append("memory_high")
        if disk["used_percent"] > 90:
            overload_reasons.append("disk_high")

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "cpu": {
                "count": cpu_count,
                "load1": round(load1, 2),
                "load5": round(load5, 2),
                "load15": round(load15, 2),
                "load_per_cpu": load_per_cpu,
            },
            "memory": memory,
            "swap": swap,
            "disk": disk,
            "uptime_seconds": uptime_seconds,
            "process_count": process_count,
            "overload": bool(overload_reasons),
            "overload_reasons": overload_reasons,
        }

    def _read_memory_stats(self) -> Dict[str, Any]:
        meminfo_path = Path("/proc/meminfo")
        total_kb = available_kb = None
        if meminfo_path.exists():
            try:
                for line in meminfo_path.read_text().splitlines():
                    if line.startswith("MemTotal:"):
                        total_kb = int(line.split()[1])
                    elif line.startswith("MemAvailable:"):
                        available_kb = int(line.split()[1])
            except (OSError, ValueError):
                total_kb = available_kb = None

        total_bytes = (total_kb or 0) * 1024
        available_bytes = (available_kb or 0) * 1024
        used_bytes = max(total_bytes - available_bytes, 0)

        to_mb = lambda b: round(b / (1024 * 1024), 1)
        used_percent = round((used_bytes / total_bytes) * 100, 1) if total_bytes else 0.0

        return {
            "total_mb": to_mb(total_bytes),
            "available_mb": to_mb(available_bytes),
            "used_mb": to_mb(used_bytes),
            "used_percent": used_percent,
        }

    def _read_swap_stats(self) -> Dict[str, Any]:
        meminfo_path = Path("/proc/meminfo")
        swap_total_kb = swap_free_kb = None

        if meminfo_path.exists():
            try:
                for line in meminfo_path.read_text().splitlines():
                    if line.startswith("SwapTotal:"):
                        swap_total_kb = int(line.split()[1])
                    elif line.startswith("SwapFree:"):
                        swap_free_kb = int(line.split()[1])
            except (OSError, ValueError):
                swap_total_kb = swap_free_kb = None

        total_bytes = (swap_total_kb or 0) * 1024
        free_bytes = (swap_free_kb or 0) * 1024
        used_bytes = max(total_bytes - free_bytes, 0)

        to_gb = lambda b: round(b / (1024 * 1024 * 1024), 2)
        used_percent = round((used_bytes / total_bytes) * 100, 1) if total_bytes else 0.0

        return {
            "total_gb": to_gb(total_bytes),
            "used_gb": to_gb(used_bytes),
            "free_gb": to_gb(free_bytes),
            "used_percent": used_percent,
            "active": total_bytes > 0,
        }

    def _read_disk_stats(self) -> Dict[str, Any]:
        try:
            usage = shutil.disk_usage(str(self.repo_root))
        except OSError:
            return {
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "used_percent": 0.0,
            }

        total_bytes = usage.total
        used_bytes = usage.total - usage.free
        free_bytes = usage.free
        used_percent = round((used_bytes / total_bytes) * 100, 1) if total_bytes else 0.0

        to_gb = lambda b: round(b / (1024 * 1024 * 1024), 2)
        return {
            "total_gb": to_gb(total_bytes),
            "used_gb": to_gb(used_bytes),
            "free_gb": to_gb(free_bytes),
            "used_percent": used_percent,
        }

    def _get_uptime_seconds(self) -> Optional[float]:
        uptime_path = Path("/proc/uptime")
        if uptime_path.exists():
            try:
                return float(uptime_path.read_text().split()[0])
            except (OSError, ValueError):
                return None
        return None

    def _get_process_count(self) -> Optional[int]:
        proc_path = Path("/proc")
        if not proc_path.exists():
            return None
        try:
            return len([p for p in proc_path.iterdir() if p.is_dir() and p.name.isdigit()])
        except OSError:
            return None
