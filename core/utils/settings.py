"""
uDOS Settings Management System
User preferences, timezone, location, and system configuration
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class FontSystemManager:
    """Manages font system configuration from core/data/font-system.json"""

    _instance = None
    _font_system = None

    @classmethod
    def get_instance(cls):
        """Singleton pattern for font system access"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Load font system configuration"""
        self.font_system_path = Path("core/data/font-system.json")
        self.load_font_system()

    def load_font_system(self) -> Dict[str, Any]:
        """Load font system configuration from JSON"""
        if self._font_system is not None:
            return self._font_system

        if self.font_system_path.exists():
            try:
                with open(self.font_system_path) as f:
                    self._font_system = json.load(f)
                return self._font_system
            except json.JSONDecodeError as e:
                print(f"⚠️  Font system config corrupted: {e}")
                return self._get_fallback_config()
        else:
            print(f"⚠️  Font system config not found: {self.font_system_path}")
            return self._get_fallback_config()

    def _get_fallback_config(self) -> Dict[str, Any]:
        """Provide minimal fallback configuration"""
        return {
            "color_palette": {
                "black": {"hex": "#000000"},
                "white_bright": {"hex": "#FFFFFF"}
            },
            "font_families": {
                "chicago": {"fallback_stack": "monospace"},
                "mallard": {"fallback_stack": "monospace"},
                "petme": {"fallback_stack": "monospace"}
            }
        }

    def get_color_palette(self) -> Dict[str, Any]:
        """Get Synthwave DOS color palette"""
        font_sys = self.load_font_system()
        return font_sys.get("color_palette", {})

    def get_font_families(self) -> Dict[str, Any]:
        """Get available font families"""
        font_sys = self.load_font_system()
        return font_sys.get("font_families", {})

    def get_font_for_extension(self, extension_name: str) -> Optional[str]:
        """Get recommended font for an extension"""
        font_sys = self.load_font_system()
        ext_config = font_sys.get("extensions_integration", {}).get(extension_name, {})
        return ext_config.get("font")

    def get_fallback_stack(self, font_family: str) -> str:
        """Get CSS fallback stack for a font family"""
        font_sys = self.load_font_system()
        families = font_sys.get("font_families", {})

        if font_family.lower() in families:
            return families[font_family.lower()].get("fallback_stack", "monospace")
        return "monospace"

    def get_block_graphics(self, charset: str = "unicode") -> Dict[str, Any]:
        """Get block graphics character set"""
        font_sys = self.load_font_system()
        return font_sys.get("block_graphics", {}).get(charset, {})


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
            "color_mode": "DARK",
            "font_family": "chicago",  # Default to Chicago retro font
            "font_profile": None  # Optional: path to custom font profile JSON
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

    def __init__(self, settings_file: str = "sandbox/user/USER.UDT"):
        self.settings_file = Path(settings_file)
        self.settings = self.load_settings()
        self.font_system = FontSystemManager.get_instance()

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

    def get_font_system(self) -> FontSystemManager:
        """Get font system manager instance"""
        return self.font_system

    def get_current_font(self) -> str:
        """Get current font family setting"""
        return self.get("system.font_family", "chicago")

    def get_font_fallback_stack(self) -> str:
        """Get CSS fallback stack for current font"""
        font = self.get_current_font()
        return self.font_system.get_fallback_stack(font)

    def load_user_font_profile(self, profile_path: Optional[str] = None) -> Optional[Dict]:
        """Load custom user font profile"""
        if profile_path is None:
            profile_path = self.get("system.font_profile")

        if not profile_path:
            return None

        profile_file = Path(profile_path)
        if not profile_file.exists():
            print(f"⚠️  Font profile not found: {profile_path}")
            return None

        try:
            with open(profile_file) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️  Font profile corrupted: {e}")
            return None


# Alias for backward compatibility with tests
uDOSSettings = SettingsManager

