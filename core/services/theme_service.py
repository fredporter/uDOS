"""
Theme Service
=============

Lightweight mapping that keeps the Core TUI voice simple and safe by
replacing a handful of words before they reach the terminal.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Optional

from core.services.logging_service import get_logger, get_repo_root

logger = get_logger("theme")


class ThemeService:
    """Simple service that loads theme files and applies replacements."""

    SEED_DIR = Path("core/framework/seed/bank/system/themes")

    def __init__(self):
        self.repo_root = get_repo_root()
        env_memory = os.environ.get("UDOS_MEMORY_ROOT")
        if env_memory:
            self.memory_root = Path(env_memory)
        else:
            self.memory_root = self.repo_root / "memory"

        self.theme_dir = self.memory_root / "bank" / "system" / "themes"
        self.seed_dir = self.repo_root / self.SEED_DIR
        self.theme_dir.mkdir(parents=True, exist_ok=True)
        self._seed_templates()

        self.active_theme = os.environ.get("UDOS_THEME", "default")
        self.replacements: Dict[str, str] = {}
        self.load_theme(self.active_theme)

    def _seed_templates(self) -> None:
        """Copy seed themes into memory if they are missing."""
        if not self.seed_dir.exists():
            logger.warning("[THEME] Seed theme directory missing: %s", self.seed_dir)
            return

        for seed_file in self.seed_dir.glob("*.json"):
            target = self.theme_dir / seed_file.name
            if not target.exists():
                try:
                    shutil.copy(seed_file, target)
                except Exception as exc:
                    logger.warning("[THEME] Failed to seed %s: %s", seed_file, exc)

    def list_themes(self) -> Dict[str, Path]:
        """Return available theme files."""
        return {theme.stem: theme for theme in self.theme_dir.glob("*.json")}

    def load_theme(self, name: str) -> None:
        """Load replacements for a named theme."""
        theme_path = self.theme_dir / f"{name}.json"
        if not theme_path.exists():
            if name != "default":
                self.load_theme("default")
            else:
                self.replacements = {}
            return

        try:
            payload = json.loads(theme_path.read_text(encoding="utf-8"))
            self.replacements = {
                str(k): str(v)
                for k, v in payload.get("replacements", {}).items()
                if k and v
            }
            self.active_theme = payload.get("name", name)
        except Exception as exc:
            logger.warning("[THEME] Failed to load %s: %s", theme_path, exc)
            self.replacements = {}

    def format(self, text: Optional[str]) -> str:
        """Return themed version of the provided text."""
        if not text or not self.replacements:
            return text or ""

        result = text
        for key, value in self.replacements.items():
            result = result.replace(key, value)
        return result


_THEME_SERVICE = ThemeService()


def get_theme_service() -> ThemeService:
    """Return the singleton theme service."""
    return _THEME_SERVICE
