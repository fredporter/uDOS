"""
uDOS Settings Management System
User preferences, timezone, location, and system configuration
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class SettingsManager:
    """Manages user settings and preferences"""

    DEFAULT_SETTINGS = {
        "user": {
            "username": os.getenv('USER', 'user'),
            "email": "",
            "display_name": "",
            "avatar_emoji": "🌀",
            "location": ""
        },
        "system": {
            "timezone": "UTC",
            "theme": "DUNGEON",
            "color_mode": "DARK"
        },
        "workspace": {
            "default_workspace": "sandbox",
            "auto_save": True,
            "backup_enabled": True
        },
        "output": {
            "markdown_viewer_port": 9000,
            "dashboard_port": 8887,
            "terminal_port": 8888,
            "auto_open_browser": True
        }
    }

    def __init__(self, settings_file: str = "data/USER.UDT"):
        self.settings_file = Path(settings_file)
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create defaults"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file) as f:
                    data = json.load(f)
                    # Check if it's USER.UDO format (has USER_PROFILE key)
                    if 'USER_PROFILE' in data:
                        return self._convert_from_user_profile(data)
                    return self._merge_settings(self.DEFAULT_SETTINGS, data)
            except json.JSONDecodeError:
                print("⚠️  Settings file corrupted, using defaults")
                return self.DEFAULT_SETTINGS.copy()
        else:
            return self.DEFAULT_SETTINGS.copy()

    def _convert_from_user_profile(self, user_data: Dict) -> Dict:
        """Convert USER.UDO format to settings format"""
        profile = user_data.get('USER_PROFILE', {})
        system_opts = user_data.get('SYSTEM_OPTIONS', {})

        return {
            "user": {
                "username": profile.get('NAME', self.DEFAULT_SETTINGS['user']['username']),
                "email": profile.get('EMAIL', ''),
                "display_name": profile.get('NAME', ''),
                "avatar_emoji": "🌀",
                "location": profile.get('LOCATION', '')
            },
            "system": {
                "timezone": profile.get('TIMEZONE', 'UTC'),
                "theme": system_opts.get('THEME', 'DUNGEON'),
                "color_mode": system_opts.get('COLOR_MODE', 'DARK')
            },
            "workspace": self.DEFAULT_SETTINGS['workspace'].copy(),
            "output": self.DEFAULT_SETTINGS['output'].copy()
        }

    def _merge_settings(self, defaults: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded settings with defaults"""
        result = defaults.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result

    def save_settings(self, settings: Optional[Dict] = None) -> bool:
        """Save settings to file"""
        if settings is None:
            settings = self.settings

        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            self.settings = settings
            return True
        except Exception as e:
            print(f"❌ Failed to save settings {e}")
            return False

    def get(self, path: str, default: Any = None) -> Any:
        """Get setting value by dot-notation path"""
        keys = path.split('.')
        value = self.settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, path: str, value: Any) -> bool:
        """Set setting value by dot-notation path"""
        keys = path.split('.')
        current = self.settings

        # Navigate to parent
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set value
        current[keys[-1]] = value
        return self.save_settings()

    def get_available_timezones(self) -> list:
        """Get list of common timezones"""
        return [
            'UTC',
            'America/New_York',
            'America/Chicago',
            'America/Denver',
            'America/Los_Angeles',
            'America/Phoenix',
            'Europe/London',
            'Europe/Paris',
            'Europe/Berlin',
            'Asia/Tokyo',
            'Asia/Shanghai',
            'Australia/Sydney',
            'Pacific/Auckland'
        ]
