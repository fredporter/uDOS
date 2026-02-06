"""
Theme Pack Validator
====================

Validates theme packs against docs/Theme-Pack-Contract.md.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("theme-validator")

REQUIRED_SLOTS = {"{{content}}", "{{title}}", "{{nav}}", "{{meta}}", "{{footer}}"}
REQUIRED_SLOT_NAMES = {"content", "title", "nav", "meta", "footer"}
ALLOWED_MODES = {"article", "retro", "slides", "forms"}


@dataclass
class ThemeValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


class ThemePackValidator:
    def __init__(self, themes_root: Optional[Path] = None):
        self.repo_root = get_repo_root()
        self.themes_root = themes_root or (self.repo_root / "themes")

    def validate_theme(self, theme_dir: Path) -> ThemeValidationResult:
        result = ThemeValidationResult(valid=True)
        if not theme_dir.exists():
            result.add_error(f"Theme directory missing: {theme_dir}")
            return result

        shell_path = theme_dir / "shell.html"
        css_path = theme_dir / "theme.css"
        json_path = theme_dir / "theme.json"
        assets_path = theme_dir / "assets"

        for path in (shell_path, css_path, json_path):
            if not path.exists():
                result.add_error(f"Missing required file: {path.name}")

        if not assets_path.exists():
            result.add_error("Missing required directory: assets/")

        shell_text = ""
        if shell_path.exists():
            shell_text = shell_path.read_text(encoding="utf-8", errors="ignore")
            missing_slots = [s for s in REQUIRED_SLOTS if s not in shell_text]
            if missing_slots:
                result.add_error(f"shell.html missing slots: {', '.join(missing_slots)}")
            if "<!DOCTYPE" not in shell_text:
                result.add_warning("shell.html missing DOCTYPE")
            if "<html" not in shell_text or "<body" not in shell_text:
                result.add_warning("shell.html missing <html> or <body>")
            if re.search(r"https?://", shell_text):
                result.add_warning("shell.html references external URLs")

        css_text = ""
        if css_path.exists():
            css_text = css_path.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"https?://", css_text):
                result.add_warning("theme.css references external URLs")

        if json_path.exists():
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
                for key in ("name", "version", "mode"):
                    if not payload.get(key):
                        result.add_error(f"theme.json missing '{key}'")
                if payload.get("mode") and payload["mode"] not in ALLOWED_MODES:
                    result.add_error(
                        f"theme.json invalid mode '{payload['mode']}'"
                    )
                if payload.get("slots"):
                    declared = set()
                    for slot in payload.get("slots", []):
                        val = str(slot).replace("{{", "").replace("}}", "").strip()
                        declared.add(val)
                    missing = REQUIRED_SLOT_NAMES - declared
                    if missing:
                        result.add_warning(
                            f"theme.json slots missing required entries: {', '.join(sorted(missing))}"
                        )
            except json.JSONDecodeError:
                result.add_error("theme.json is not valid JSON")

        return result

    def validate_all(self) -> Dict[str, ThemeValidationResult]:
        results: Dict[str, ThemeValidationResult] = {}
        if not self.themes_root.exists():
            results["themes"] = ThemeValidationResult(valid=False, errors=["themes/ not found"])
            return results

        for theme_dir in sorted(p for p in self.themes_root.iterdir() if p.is_dir()):
            if not (theme_dir / "theme.json").exists() and not (theme_dir / "shell.html").exists():
                continue
            results[theme_dir.name] = self.validate_theme(theme_dir)
        return results

    def summarize(self, results: Dict[str, ThemeValidationResult]) -> Dict[str, int]:
        total = len(results)
        valid = sum(1 for r in results.values() if r.valid)
        return {
            "total": total,
            "valid": valid,
            "invalid": total - valid,
        }
