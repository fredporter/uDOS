"""
Sonic service wrapper for device catalog + manifest status.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("sonic-service")


class SonicService:
    """Lightweight Sonic Screwdriver helper."""

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.dataset_root = self.repo_root / "sonic" / "datasets"
        self.db_path = self.repo_root / "memory" / "sonic" / "sonic-devices.db"
        self.flash_pack_root = self.repo_root / "memory" / "sandbox" / "screwdriver" / "flash_packs"

    def health(self) -> Dict[str, Any]:
        table_exists = (self.dataset_root / "sonic-devices.table.md").exists()
        schema_exists = (self.dataset_root / "sonic-devices.schema.json").exists()
        db_exists = self.db_path.exists()
        return {
            "datasets_available": table_exists,
            "schema_available": schema_exists,
            "database_compiled": db_exists,
            "db_path": str(self.db_path),
            "flash_pack_root": str(self.flash_pack_root),
        }


def get_sonic_service() -> SonicService:
    return SonicService()
