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

from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("theme")


class ThemeService:
    """Simple service that loads theme files and applies replacements."""

    SEED_DIR = Path("core/framework/seed/bank/system/themes")
    SIMPLE_TUI_PRESETS: Dict[str, Dict[str, str]] = {
        "default": {},
        "dungeon": {
            "Tip:": "Delve Tip:",
            "Health:": "Delve Health:",
            "Wizard": "Dungeon Ops",
            "WIZARD": "DUNGEON OPS",
        },
        "fantasy": {
            "Tip:": "Quest Tip:",
            "Health:": "Guild Health:",
            "Wizard": "Arcane Ops",
            "WIZARD": "ARCANE OPS",
        },
        "role-play": {
            "Tip:": "Role Tip:",
            "Health:": "Party Health:",
            "Wizard": "Narrator Ops",
            "WIZARD": "NARRATOR OPS",
        },
        "stranger-things": {
            "Tip:": "Upside Tip:",
            "Health:": "Upside Health:",
            "Wizard": "Signal Ops",
            "WIZARD": "SIGNAL OPS",
        },
        "explorer": {
            "Tip:": "Expedition Tip:",
            "Health:": "Field Health:",
            "Wizard": "Survey Ops",
            "WIZARD": "SURVEY OPS",
        },
        "lonely-planet": {
            "Tip:": "Trail Tip:",
            "Health:": "Camp Health:",
            "Wizard": "Guide Ops",
            "WIZARD": "GUIDE OPS",
        },
        "doomsday": {
            "Tip:": "Survival Tip:",
            "Health:": "Bunker Health:",
            "Wizard": "Fallback Ops",
            "WIZARD": "FALLBACK OPS",
        },
        "foundation": {
            "Tip:": "Foundation Tip:",
            "Health:": "Foundation Health:",
            "Wizard": "Control Ops",
            "WIZARD": "CONTROL OPS",
        },
        "galaxy": {
            "Tip:": "Galaxy Tip:",
            "Health:": "Fleet Health:",
            "Wizard": "Star Ops",
            "WIZARD": "STAR OPS",
        },
        "scientist": {
            "Tip:": "Lab Tip:",
            "Health:": "Systems Health:",
            "Wizard": "Research Ops",
            "WIZARD": "RESEARCH OPS",
        },
        "hitchhikers": {
            "Tip:": "42 Tip:",
            "Health:": "Ship Health:",
            "Wizard": "Guide Console",
            "WIZARD": "GUIDE CONSOLE",
        },
    }
    THEME_ALIASES: Dict[str, str] = {
        "galxy": "galaxy",
        "roleplay": "role-play",
    }
    MAP_LEVEL_THEME: Dict[str, str] = {
        "dungeon": "dungeon",
        "sub": "dungeon",
        "subterranean": "dungeon",
        "fantasy": "fantasy",
        "role-play": "role-play",
        "roleplay": "role-play",
        "foundation": "foundation",
        "surface": "foundation",
        "sur": "foundation",
        "regional": "foundation",
        "explorer": "explorer",
        "galaxy": "galaxy",
        "stellar": "galaxy",
        "orbital": "galaxy",
        "udn": "galaxy",
        "scientist": "scientist",
    }

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

    def _canonical_theme_name(self, name: Optional[str]) -> str:
        if not name:
            return "default"
        raw = str(name).strip().lower()
        return self.THEME_ALIASES.get(raw, raw)

    def _resolve_message_theme(self, map_level: Optional[str] = None) -> str:
        override = os.environ.get("UDOS_TUI_MESSAGE_THEME", "").strip().lower()
        if override:
            return self._canonical_theme_name(override)

        if map_level:
            mapped = self.MAP_LEVEL_THEME.get(str(map_level).strip().lower())
            if mapped:
                return mapped

        env_level = os.environ.get("UDOS_TUI_MAP_LEVEL", "").strip().lower()
        if env_level:
            mapped = self.MAP_LEVEL_THEME.get(env_level)
            if mapped:
                return mapped

        return self._canonical_theme_name(self.active_theme)

    def _apply_replacements(self, text: str, replacements: Dict[str, str]) -> str:
        result = text
        for key, value in replacements.items():
            result = result.replace(key, value)
        return result

    def format(self, text: Optional[str], map_level: Optional[str] = None) -> str:
        """
        Return themed version of the provided text.

        Default mode: simplified TUI message vocabulary only.
        Legacy mode: full historical replacements (`UDOS_TUI_LEGACY_REPLACEMENTS=1`).
        """
        if not text:
            return ""

        legacy_mode = os.environ.get("UDOS_TUI_LEGACY_REPLACEMENTS", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if legacy_mode:
            return self._apply_replacements(text, self.replacements)

        theme_name = self._resolve_message_theme(map_level=map_level)
        simple = self.SIMPLE_TUI_PRESETS.get(theme_name) or {}
        return self._apply_replacements(text, simple)


_THEME_SERVICE = ThemeService()


def get_theme_service() -> ThemeService:
    """Return the singleton theme service."""
    return _THEME_SERVICE
