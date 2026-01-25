"""
Wizard Setup State
==================

Tracks first-time setup progress for Wizard server.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from wizard.services.path_utils import get_repo_root


class SetupState:
    def __init__(self, path: Path | None = None) -> None:
        default_path = get_repo_root() / "memory" / "wizard" / "setup-state.json"
        self.path = path or default_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "setup_complete": False,
                "initialized_at": None,
                "variables_configured": [],
                "services_enabled": [],
            }
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return {
                "setup_complete": False,
                "initialized_at": None,
                "variables_configured": [],
                "services_enabled": [],
            }

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2))

    def get_status(self) -> Dict[str, Any]:
        return self.data

    def mark_variable_configured(self, name: str) -> None:
        if name not in self.data["variables_configured"]:
            self.data["variables_configured"].append(name)
        if not self.data.get("initialized_at"):
            self.data["initialized_at"] = datetime.utcnow().isoformat()
        self._save()

    def mark_setup_complete(self) -> None:
        self.data["setup_complete"] = True
        if not self.data.get("initialized_at"):
            self.data["initialized_at"] = datetime.utcnow().isoformat()
        self._save()


setup_state = SetupState()
