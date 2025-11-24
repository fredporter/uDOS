#!/usr/bin/env python3
"""
uDOS JSON Configuration Generator

Creates structured user.json with standard fields and system settings.
Integrates TIZO location codes and comprehensive configuration options.

Version: 2.0.0
Author: Fred Porter
"""

import json
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone
import sys

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))
from core.utils.tizo_manager import TIZOLocationManager


class UserConfigGenerator:
    """Generate structured user.json configuration."""

    def __init__(self, workspace_dir="."):
        self.workspace_dir = Path(workspace_dir)
        self.sandbox_dir = self.workspace_dir / "sandbox"
        self.tizo_manager = TIZOLocationManager(self.workspace_dir / "data" / "system")

    def load_legacy_config(self):
        """Load any existing configuration."""
        configs = []

        # Try user.json first
        user_json = self.sandbox_dir / "user.json"
        if user_json.exists():
            try:
                with open(user_json, 'r') as f:
                    configs.append(("user.json", json.load(f)))
            except Exception as e:
                print(f"⚠️  Could not load user.json: {e}")

        # Try USER.UDO.backup
        user_udo_backup = self.sandbox_dir / "USER.UDO.backup"
        if user_udo_backup.exists():
            try:
                with open(user_udo_backup, 'r') as f:
                    configs.append(("USER.UDO.backup", json.load(f)))
            except Exception as e:
                print(f"⚠️  Could not load USER.UDO.backup: {e}")

        # Try USER.UDO
        user_udo = self.sandbox_dir / "USER.UDO"
        if user_udo.exists():
            try:
                with open(user_udo, 'r') as f:
                    configs.append(("USER.UDO", json.load(f)))
            except Exception as e:
                print(f"⚠️  Could not load USER.UDO: {e}")

        return configs

    def detect_installation_settings(self, legacy_configs):
        """Detect installation settings from legacy configs and system."""
        settings = {
            "installation_id": uuid.uuid4().hex[:16],
            "username": "user",
            "tizo_code": "UTC",
            "viewport": {"device_type": "DESKTOP", "terminal_size": {"width": 80, "height": 24}},
            "theme": "DUNGEON_CRAWLER",
            "cli_only": False,
            "offline_mode": False
        }

        # Extract from legacy configs
        for config_name, config_data in legacy_configs:
            if config_name == "user.json" and "user_profile" in config_data:
                # Already structured - use existing ID
                settings["installation_id"] = config_data["user_profile"].get("installation_id", settings["installation_id"])
                if "location" in config_data:
                    settings["tizo_code"] = config_data["location"].get("tizo_code", "MEL")
                return settings

            # Extract from USER.UDO format
            user_profile = config_data.get("USER_PROFILE", {})
            system_config = config_data.get("SYSTEM_CONFIG", {})
            display_settings = config_data.get("DISPLAY_SETTINGS", {})
            session_prefs = config_data.get("SESSION_PREFERENCES", {})

            # Extract user info
            if "NAME" in user_profile:
                settings["username"] = user_profile["NAME"]
            elif "NAME" in config_data:
                settings["username"] = config_data["NAME"]

            # Extract location
            location = config_data.get("LOCATION", user_profile.get("LOCATION"))
            if location and "melbourne" in location.lower():
                settings["tizo_code"] = "MEL"
            elif location:
                # Try to detect from location string
                detection = self.tizo_manager.auto_detect_location()
                settings["tizo_code"] = detection["recommended_city"]["code"]

            # Extract display settings
            if "DEVICE_TYPE" in display_settings:
                settings["viewport"]["device_type"] = display_settings["DEVICE_TYPE"]

            if "TERMINAL_SIZE" in display_settings:
                term_size = display_settings["TERMINAL_SIZE"]
                if "×" in term_size:
                    width, height = term_size.split("×")
                    settings["viewport"]["terminal_size"] = {
                        "width": int(width),
                        "height": int(height)
                    }

            # Extract preferences
            if "THEME" in session_prefs:
                settings["theme"] = session_prefs["THEME"]

            # Detect CLI-only mode
            if display_settings.get("DEVICE_TYPE") == "TERMINAL":
                settings["cli_only"] = True

            # Detect offline mode
            if system_config.get("OFFLINE_MODE_ALLOWED") is True:
                settings["offline_mode"] = True

            break  # Use first valid config

        # Auto-detect if no legacy config
        if not legacy_configs:
            detection = self.tizo_manager.auto_detect_location()
            settings["tizo_code"] = detection["recommended_city"]["code"]

        return settings

    def generate_user_config(self, installation_settings):
        """Generate complete user.json configuration."""

        # Get TIZO location data
        tizo_code = installation_settings["tizo_code"]
        if tizo_code != "UTC":
            location_data = self.tizo_manager.generate_user_profile_data(tizo_code)
        else:
            location_data = {
                "tizo_code": "UTC",
                "city_name": "Coordinated Universal Time",
                "country": "Global",
                "continent": "GLOBAL",
                "region": "Universal",
                "coordinates": {"lat": 0.0, "lon": 0.0},
                "timezone": "UTC",
                "timezone_offset": "+00:00",
                "nearby_cities": [],
                "connection_quality": {"global": "STANDARD"}
            }

        now = datetime.now(timezone.utc)

        config = {
            "user_profile": {
                "schema_version": "USER_PROFILE_V2",
                "installation_id": installation_settings["installation_id"],
                "profile_version": "2.0",
                "created_at": now.isoformat(),
                "last_updated": now.isoformat(),
                "last_session": f"session_{int(now.timestamp())}"
            },

            "location": {
                "tizo_code": location_data["tizo_code"],
                "city_name": location_data["city_name"],
                "country": location_data["country"],
                "continent": location_data["continent"],
                "region": location_data["region"],
                "coordinates": {
                    "latitude": location_data["coordinates"]["lat"],
                    "longitude": location_data["coordinates"]["lon"]
                },
                "timezone": {
                    "name": location_data["timezone"],
                    "offset": location_data["timezone_offset"],
                    "description": f"{location_data['timezone']} timezone"
                },
                "nearby_cities": [
                    {
                        "code": city["code"],
                        "name": city["name"],
                        "distance_km": city["distance_km"],
                        "timezone": city["timezone"]
                    }
                    for city in location_data.get("nearby_cities", [])[:5]
                ]
            },

            "system_settings": {
                "viewport": {
                    "device_type": installation_settings["viewport"]["device_type"],
                    "terminal_size": installation_settings["viewport"]["terminal_size"],
                    "grid_dimensions": {"width": 10, "height": 9},
                    "precision_mode": "UCELL_16x16",
                    "coordinate_system": "ZERO_INDEXED"
                },

                "display": {
                    "color_support": True,
                    "unicode_support": True,
                    "theme": installation_settings["theme"],
                    "render_mode": "TERMINAL"
                },

                "interface": {
                    "cli_only": installation_settings["cli_only"],
                    "offline_mode": installation_settings["offline_mode"],
                    "verbose_logging": False,
                    "confirm_destructive": True,
                    "auto_save": True
                },

                "performance": {
                    "auto_update_check": True,
                    "telemetry_enabled": False,
                    "cache_enabled": True,
                    "compression_enabled": False
                }
            },

            "session_preferences": {
                "assist_mode": False,
                "preferred_mode": "STANDARD",
                "default_layer": "MAIN",
                "text_grid_position": {"x": 0, "y": 0},
                "workspace_bookmarks": [],
                "recent_files": [],
                "command_history_size": 1000
            },

            "world_navigation": {
                "accessible_layers": location_data.get("udos_layers", ["SURFACE"]),
                "connection_quality": location_data.get("connection_quality", {"global": "STANDARD"}),
                "default_locations": {
                    "surface": location_data["tizo_code"],
                    "cloud": f"{location_data['tizo_code']}-CLOUD",
                    "satellite": f"{location_data['tizo_code']}-SAT",
                    "dungeon": f"{location_data['tizo_code']}-D1"
                }
            },

            "accessibility": {
                "screen_reader": False,
                "high_contrast": False,
                "large_text": False,
                "reduced_motion": False,
                "keyboard_only": installation_settings["cli_only"]
            },

            "advanced": {
                "developer_mode": False,
                "debug_logging": False,
                "experimental_features": False,
                "beta_access": False,
                "api_rate_limit": 60
            },

            "metadata": {
                "installation_type": "STANDARD",
                "backup_status": "AUTO_ENABLED",
                "sync_status": "LOCAL_ONLY",
                "config_format": "JSON_V2",
                "migration_source": "AUTO_GENERATED"
            }
        }

        return config

    def save_user_config(self, config):
        """Save user.json configuration."""
        user_json_file = self.sandbox_dir / "user.json"

        with open(user_json_file, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✅ Created user.json: {user_json_file}")
        return user_json_file

    def generate_config(self):
        """Generate complete structured user configuration."""
        print("🔧 uDOS Structured Configuration Generator")
        print("=" * 50)

        # Load existing configs
        print("\n📂 Loading existing configurations...")
        legacy_configs = self.load_legacy_config()

        if legacy_configs:
            for config_name, _ in legacy_configs:
                print(f"✅ Found: {config_name}")
        else:
            print("ℹ️  No existing configurations found")

        # Detect installation settings
        print("\n🔍 Detecting installation settings...")
        installation_settings = self.detect_installation_settings(legacy_configs)

        print(f"👤 Username: {installation_settings['username']}")
        print(f"🆔 Installation ID: {installation_settings['installation_id']}")
        print(f"🌍 Location: {installation_settings['tizo_code']}")
        print(f"💻 Device: {installation_settings['viewport']['device_type']}")
        print(f"🎨 Theme: {installation_settings['theme']}")
        print(f"⌨️  CLI Only: {installation_settings['cli_only']}")
        print(f"📴 Offline Mode: {installation_settings['offline_mode']}")

        # Generate configuration
        print("\n📝 Generating structured configuration...")
        config = self.generate_user_config(installation_settings)

        # Save configuration
        user_json_file = self.save_user_config(config)

        # Summary
        print("\n✅ Configuration Generated!")
        print(f"📄 File: {user_json_file}")
        print(f"📊 Schema: {config['user_profile']['schema_version']}")
        print(f"🌍 Location: {config['location']['city_name']} ({config['location']['tizo_code']})")
        print(f"⏰ Timezone: {config['location']['timezone']['name']} ({config['location']['timezone']['offset']})")
        print(f"🖥️  Viewport: {config['system_settings']['viewport']['terminal_size']['width']}×{config['system_settings']['viewport']['terminal_size']['height']}")

        return {
            "config_file": user_json_file,
            "config": config,
            "installation_settings": installation_settings
        }


def main():
    """Generate structured user configuration."""
    generator = UserConfigGenerator()
    result = generator.generate_config()

    print("\n🎉 Structured configuration ready!")
    print("💡 Configuration includes:")
    print("   - 📍 TIZO location codes and timezone data")
    print("   - 🖥️  Viewport and display settings")
    print("   - ⚙️  System settings (CLI-only, offline mode)")
    print("   - 🌍 World navigation and connection quality")
    print("   - ♿ Accessibility options")
    print("   - 🔧 Advanced developer settings")


if __name__ == "__main__":
    main()
