"""
OK Configuration Settings
Manages OK assistant configuration (model, temperature, tokens, cost tracking)

Settings:
- Model selection (gemini-2.0-flash-exp, gemini-1.5-pro, etc.)
- Temperature (0.0-2.0)
- Max tokens (100-100000)
- Cost tracking enabled/disabled
- Context length
- Response format preferences

Storage: memory/system/user/ok_config.json

Version: 1.0.0 (v1.2.21)
Author: Fred Porter
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from core.config import Config


class OKConfig:
    """OK assistant configuration manager"""

    # Default settings
    DEFAULTS = {
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.7,
        "max_tokens": 8192,
        "cost_tracking": True,
        "context_length": 5,  # Last N commands for context
        "response_format": "markdown",
        "auto_save_history": True,
        "history_retention_days": 30
    }

    # Model options
    MODELS = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ]

    # Temperature range
    TEMP_MIN = 0.0
    TEMP_MAX = 2.0

    # Token limits
    TOKEN_MIN = 100
    TOKEN_MAX = 100000

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize OK config manager.

        Args:
            config: Config instance (auto-creates if None)
        """
        self.config = config or Config()
        self.project_root = self.config.project_root

        # Config file path
        self.config_dir = self.project_root / "memory" / "system" / "user"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "ok_config.json"

        # Settings
        self.settings: Dict[str, Any] = {}

        # Load settings
        self.load()

    def load(self) -> None:
        """Load OK configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    self.settings = {**self.DEFAULTS, **loaded}
            except Exception:
                # Use defaults if load fails
                self.settings = self.DEFAULTS.copy()
        else:
            # First run - use defaults
            self.settings = self.DEFAULTS.copy()
            self.save()

    def save(self) -> bool:
        """
        Save OK configuration to file.

        Returns:
            True if saved successfully
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get setting value.

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value
        """
        return self.settings.get(key, default or self.DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> bool:
        """
        Set setting value with validation.

        Args:
            key: Setting key
            value: New value

        Returns:
            True if set successfully
        """
        # Validate based on key
        if key == "model":
            if value not in self.MODELS:
                return False
        elif key == "temperature":
            try:
                temp = float(value)
                if not (self.TEMP_MIN <= temp <= self.TEMP_MAX):
                    return False
                value = temp
            except (ValueError, TypeError):
                return False
        elif key == "max_tokens":
            try:
                tokens = int(value)
                if not (self.TOKEN_MIN <= tokens <= self.TOKEN_MAX):
                    return False
                value = tokens
            except (ValueError, TypeError):
                return False
        elif key == "cost_tracking":
            value = bool(value)
        elif key == "context_length":
            try:
                length = int(value)
                if not (1 <= length <= 20):
                    return False
                value = length
            except (ValueError, TypeError):
                return False
        elif key == "auto_save_history":
            value = bool(value)
        elif key == "history_retention_days":
            try:
                days = int(value)
                if not (1 <= days <= 365):
                    return False
                value = days
            except (ValueError, TypeError):
                return False

        # Set value
        self.settings[key] = value
        return True

    def reset(self) -> None:
        """Reset all settings to defaults"""
        self.settings = self.DEFAULTS.copy()
        self.save()

    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings.

        Returns:
            Dictionary of all settings
        """
        return self.settings.copy()

    def get_summary(self) -> str:
        """
        Get human-readable settings summary.

        Returns:
            Formatted settings string
        """
        lines = [
            "🤖 OK Assistant Configuration",
            "",
            f"Model: {self.settings['model']}",
            f"Temperature: {self.settings['temperature']:.1f}",
            f"Max Tokens: {self.settings['max_tokens']:,}",
            f"Cost Tracking: {'Enabled' if self.settings['cost_tracking'] else 'Disabled'}",
            f"Context Length: {self.settings['context_length']} commands",
            f"Response Format: {self.settings['response_format']}",
            f"Auto-save History: {'Yes' if self.settings['auto_save_history'] else 'No'}",
            f"History Retention: {self.settings['history_retention_days']} days"
        ]
        return "\n".join(lines)


# Singleton instance
_ok_config: Optional[OKConfig] = None


def get_ok_config() -> OKConfig:
    """
    Get singleton OK config instance.

    Returns:
        OKConfig instance
    """
    global _ok_config
    if _ok_config is None:
        _ok_config = OKConfig()
    return _ok_config
