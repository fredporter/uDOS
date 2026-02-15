"""Theme/CSS extension discovery for Wizard GUI."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List


class ThemeExtensionService:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent

    def list_css_extensions(self) -> Dict[str, Any]:
        themes_root = self.repo_root / "themes"
        wizard_styles_root = self.repo_root / "wizard" / "dashboard" / "src" / "styles"

        theme_packs: List[Dict[str, Any]] = []
        if themes_root.exists():
            for theme_dir in sorted(themes_root.iterdir()):
                if not theme_dir.is_dir():
                    continue
                css_file = theme_dir / "theme.css"
                shell_file = theme_dir / "shell.html"
                theme_packs.append(
                    {
                        "id": theme_dir.name,
                        "path": str(theme_dir),
                        "theme_css": str(css_file) if css_file.exists() else None,
                        "shell_html": str(shell_file) if shell_file.exists() else None,
                        "valid_pack": css_file.exists() and shell_file.exists(),
                    }
                )

        wizard_css: List[Dict[str, Any]] = []
        if wizard_styles_root.exists():
            for css_file in sorted(wizard_styles_root.rglob("*.css")):
                wizard_css.append(
                    {
                        "name": css_file.name,
                        "path": str(css_file.relative_to(self.repo_root)),
                        "size_bytes": css_file.stat().st_size,
                    }
                )

        return {
            "themes_root": str(themes_root),
            "wizard_styles_root": str(wizard_styles_root),
            "theme_packs": theme_packs,
            "wizard_css_extensions": wizard_css,
            "counts": {
                "theme_packs": len(theme_packs),
                "valid_theme_packs": sum(1 for p in theme_packs if p["valid_pack"]),
                "wizard_css_extensions": len(wizard_css),
            },
        }


def get_theme_extension_service(repo_root: Path | None = None) -> ThemeExtensionService:
    return ThemeExtensionService(repo_root=repo_root)
