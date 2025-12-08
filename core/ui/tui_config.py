"""
TUI Configuration Handler (v1.2.13)

Manages TUI system settings:
- Keypad navigation toggle
- Pager preferences
- File browser filters
- Command prediction options
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json


class TUIConfig:
    """
    TUI system configuration manager.
    
    Settings:
    - keypad_enabled: Enable numpad navigation
    - preserve_scroll: Keep scroll position between commands
    - show_scroll_indicators: Show ▲/▼ in pager
    - prediction_max_results: Number of predictions to show
    - browser_filter: File extensions to show
    - auto_save_state: Save TUI state on exit
    """
    
    DEFAULT_CONFIG = {
        "keypad_enabled": False,  # Disabled by default
        "preserve_scroll": True,
        "show_scroll_indicators": True,
        "prediction_max_results": 5,
        "browser_filter": [".upy", ".md", ".json"],
        "auto_save_state": True,
        "viewport_height": 20,
        "show_breadcrumbs": True,
        "enable_fuzzy_match": True,
        "syntax_highlighting": True
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        from core.utils.paths import PATHS
        self.config_path = config_path or (PATHS.MEMORY_SYSTEM_USER / "tui_config.json")
        self.settings = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception as e:
                print(f"Warning: Could not load TUI config: {e}")
    
    def save(self):
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving TUI config: {e}")
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.settings[key] = value
        if self.get("auto_save_state"):
            self.save()
    
    def toggle(self, key: str) -> bool:
        """Toggle boolean setting"""
        current = self.get(key, False)
        new_value = not current
        self.set(key, new_value)
        return new_value
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
    
    def export_config(self, path: Path):
        """Export config to file"""
        with open(path, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def import_config(self, path: Path):
        """Import config from file"""
        if path.exists():
            with open(path) as f:
                imported = json.load(f)
                self.settings.update(imported)
            self.save()


# Global config instance
_tui_config: Optional[TUIConfig] = None


def get_tui_config() -> TUIConfig:
    """Get global TUI config instance"""
    global _tui_config
    if _tui_config is None:
        _tui_config = TUIConfig()
    return _tui_config
