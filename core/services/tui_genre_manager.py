"""TUI GENRE Manager - Terminal UI theming system."""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("tui-genre")


class TuiGenreManager:
    """Manage TUI GENRE definitions and apply theming to terminal output."""

    DEFAULT_GENRE = "minimal"
    GENRE_DIR = "core/themes/genre"

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or get_repo_root()
        self.genre_dir = self.repo_root / self.GENRE_DIR
        self._genres: Dict[str, Dict] = {}
        self._active_genre: Optional[str] = None
        self._load_genres()

    def _load_genres(self) -> None:
        """Load all available GENRE definitions from filesystem."""
        if not self.genre_dir.exists():
            logger.warning(f"GENRE directory not found: {self.genre_dir}")
            return

        for genre_dir in self.genre_dir.iterdir():
            if not genre_dir.is_dir():
                continue

            genre_yaml = genre_dir / "genre.yaml"
            if not genre_yaml.exists():
                continue

            try:
                with open(genre_yaml, 'r') as f:
                    genre_data = yaml.safe_load(f)
                    genre_name = genre_data['metadata']['name']
                    self._genres[genre_name] = genre_data
                    logger.info(f"Loaded GENRE: {genre_name}")
            except Exception as exc:
                logger.error(f"Failed to load GENRE {genre_dir.name}: {exc}")

    def list_genres(self) -> List[Dict[str, str]]:
        """List all available GENREs with metadata."""
        return [
            {
                "name": name,
                "display_name": data["metadata"]["display_name"],
                "description": data["metadata"]["description"]
            }
            for name, data in self._genres.items()
        ]

    def get_genre(self, name: str) -> Optional[Dict]:
        """Get GENRE definition by name."""
        return self._genres.get(name)

    def set_active_genre(self, name: str) -> bool:
        """Set the active GENRE. Returns True if successful."""
        if name not in self._genres:
            return False
        
        self._active_genre = name
        logger.info(f"Activated GENRE: {name}")
        return True

    def get_active_genre(self) -> Optional[str]:
        """Get the currently active GENRE name."""
        return self._active_genre or self.DEFAULT_GENRE

    def format_error(self, message: str) -> str:
        """Format an error message according to active GENRE."""
        genre = self._get_active_genre_data()
        if not genre:
            return f"ERROR: {message}"

        template = genre.get("templates", {}).get("error", "ERROR")
        return f"{template}: {message}"

    def format_warning(self, message: str) -> str:
        """Format a warning message according to active GENRE."""
        genre = self._get_active_genre_data()
        if not genre:
            return f"WARNING: {message}"

        template = genre.get("templates", {}).get("warning", "WARNING")
        return f"{template}: {message}"

    def format_success(self, message: str) -> str:
        """Format a success message according to active GENRE."""
        genre = self._get_active_genre_data()
        if not genre:
            return f"SUCCESS: {message}"

        template = genre.get("templates", {}).get("success", "SUCCESS")
        return f"{template}: {message}"

    def format_info(self, message: str) -> str:
        """Format an info message according to active GENRE."""
        genre = self._get_active_genre_data()
        if not genre:
            return f"INFO: {message}"

        template = genre.get("templates", {}).get("info", "INFO")
        return f"{template}: {message}"

    def _get_active_genre_data(self) -> Optional[Dict]:
        """Get the full data for the active GENRE."""
        active = self.get_active_genre()
        return self._genres.get(active)

    def create_box(self, title: str, content: str, width: int = 60) -> str:
        """Create a styled box according to active GENRE."""
        genre = self._get_active_genre_data()
        if not genre:
            # Fallback to simple box
            border = "─" * min(width, len(title) + 4)
            return f"┌{border}┐\n│ {title.center(width - 2)} │\n└{border}┘\n│{content[:width-2].ljust(width-2)}│"

        borders = genre.get("borders", {})
        h = borders.get("horizontal", "─")
        v = borders.get("vertical", "│")
        tl = borders.get("corner_top_left", "┌")
        tr = borders.get("corner_top_right", "┐")
        bl = borders.get("corner_bottom_left", "└")
        br = borders.get("corner_bottom_right", "┘")

        # Adjust width to fit content
        effective_width = max(len(title) + 4, min(width, 80))
        border_line = h * (effective_width - 2)
        
        lines = [
            f"{tl}{border_line}{tr}",
            f"{v} {title.center(effective_width - 4)} {v}",
            f"{bl}{border_line}{br}"
        ]
        
        # Add content lines
        for line in content.split('\n'):
            lines.append(f"{v} {line[:effective_width-4].ljust(effective_width-4)} {v}")
        
        return "\n".join(lines)


# Singleton instance
_genre_manager: Optional[TuiGenreManager] = None


def get_tui_genre_manager() -> TuiGenreManager:
    """Return singleton TUI GENRE manager."""
    global _genre_manager
    if _genre_manager is None:
        _genre_manager = TuiGenreManager()
    return _genre_manager
