"""
Dataset Manager (Core)

Unified access layer for datasets used by Core services.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.logging_service import get_logger, get_repo_root

logger = get_logger("core.dataset")


class DatasetManager:
    """Load dataset metadata and content from config."""

    def __init__(self, config_path: Optional[Path] = None):
        repo_root = get_repo_root()
        self.config_path = config_path or repo_root / "core" / "config" / "datasets.json"
        self.repo_root = repo_root
        self._datasets = self._load_config()

    def _load_config(self) -> List[Dict[str, Any]]:
        if not self.config_path.exists():
            logger.warning(f"[LOCAL] Dataset config missing: {self.config_path}")
            return []
        try:
            data = json.loads(self.config_path.read_text())
            return data.get("datasets", [])
        except json.JSONDecodeError:
            logger.error("[LOCAL] Invalid dataset config JSON")
            return []

    def list_datasets(self) -> List[Dict[str, Any]]:
        return self._datasets

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        for ds in self._datasets:
            if ds.get("id") == dataset_id:
                return ds
        return None

    def load_json(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        ds = self.get_dataset(dataset_id)
        if not ds:
            return None
        path = self._resolve_path(ds.get("path", ""))
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            return None

    def _resolve_path(self, rel_path: str) -> Path:
        path = Path(rel_path)
        if not path.is_absolute():
            return self.repo_root / path
        return path
