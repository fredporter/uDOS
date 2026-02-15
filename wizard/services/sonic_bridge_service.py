"""Sonic bridge service for Wizard GUI integration.

Sonic remains independently runnable, but Wizard can introspect Sonic metadata,
datasets, and artifacts when the Sonic repo/module is present.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List
import json


class SonicBridgeService:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.sonic_root = self.repo_root / "sonic"

    def _read_version(self) -> str | None:
        path = self.sonic_root / "version.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("display") or data.get("version")
        except Exception:
            return None

    def _count_files(self, root: Path, patterns: List[str]) -> int:
        if not root.exists():
            return 0
        total = 0
        for pattern in patterns:
            total += len(list(root.rglob(pattern)))
        return total

    def get_status(self) -> Dict[str, Any]:
        available = self.sonic_root.exists() and (self.sonic_root / "core").exists()

        datasets_root = self.sonic_root / "datasets"
        scripts_root = self.sonic_root / "scripts"
        payloads_root = self.sonic_root / "payloads"
        docs_root = self.sonic_root / "docs"

        status = {
            "available": available,
            "independent_runtime": True,
            "wizard_integrated": available,
            "root": str(self.sonic_root),
            "version": self._read_version(),
            "datasets": {
                "root": str(datasets_root),
                "sql_present": (datasets_root / "sonic-devices.sql").exists(),
                "schema_present": (datasets_root / "sonic-devices.schema.json").exists(),
                "files": self._count_files(datasets_root, ["*.sql", "*.json", "*.md"]),
            },
            "scripts": {
                "root": str(scripts_root),
                "files": self._count_files(scripts_root, ["*.sh", "*.py"]),
            },
            "payloads": {
                "root": str(payloads_root),
                "files": self._count_files(payloads_root, ["*"]),
            },
            "docs": {
                "root": str(docs_root),
                "files": self._count_files(docs_root, ["*.md"]),
            },
        }
        return status

    def list_artifacts(self, limit: int = 200) -> Dict[str, Any]:
        roots = [
            self.sonic_root / "datasets",
            self.sonic_root / "config",
            self.sonic_root / "payloads",
            self.sonic_root / "scripts",
        ]
        artifacts: List[Dict[str, Any]] = []
        for root in roots:
            if not root.exists():
                continue
            for path in sorted(root.rglob("*")):
                if not path.is_file():
                    continue
                rel = path.relative_to(self.sonic_root)
                artifacts.append(
                    {
                        "path": str(rel),
                        "size_bytes": path.stat().st_size,
                        "modified_ts": int(path.stat().st_mtime),
                    }
                )

        artifacts = sorted(artifacts, key=lambda x: x["modified_ts"], reverse=True)
        capped = artifacts[: max(1, min(limit, 1000))]
        return {
            "available": self.sonic_root.exists(),
            "count": len(capped),
            "total_found": len(artifacts),
            "artifacts": capped,
        }


def get_sonic_bridge_service(repo_root: Path | None = None) -> SonicBridgeService:
    return SonicBridgeService(repo_root=repo_root)
