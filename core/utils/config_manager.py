#!/usr/bin/env python3
"""
uDOS Configuration Manager

Utility for managing structured user.json configuration.
Provides commands for viewing, updating, and validating settings.

Version: 2.0.0
Author: Fred Porter
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone


class UserConfigManager:
    """Manage structured user.json configuration."""

    def __init__(self, config_path="memory/sandbox/user.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self):
        """Load user configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_config(self):
        """Save user configuration."""
        # Update last_updated timestamp
        self.config["user_profile"]["last_updated"] = datetime.now(timezone.utc).isoformat()

        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_setting(self, path):
        """Get a setting using dot notation (e.g., 'system_settings.viewport.device_type')."""
        keys = path.split('.')
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None

    def set_setting(self, path, value):
        """Set a setting using dot notation."""
        keys = path.split('.')
        config_section = self.config

        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in config_section:
                config_section[key] = {}
            config_section = config_section[key]

        # Set the value
        final_key = keys[-1]

        # Type conversion
        if isinstance(value, str):
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                value = float(value)

        config_section[final_key] = value
        self.save_config()

        return f"Set {path} = {value}"

    def show_info(self):
        """Show configuration summary."""
        profile = self.config["user_profile"]
        location = self.config["location"]
        viewport = self.config["system_settings"]["viewport"]
        interface = self.config["system_settings"]["interface"]

        print("🔧 uDOS Configuration Summary")
        print("=" * 40)
        print(f"📊 Schema: {profile['schema_version']}")
        print(f"🆔 Installation ID: {profile['installation_id']}")
        print(f"📅 Last Updated: {profile['last_updated']}")
        print()
        print(f"🌍 Location: {location['city_name']}, {location['country']}")
        print(f"🏷️  TIZO Code: {location['tizo_code']}")
        print(f"⏰ Timezone: {location['timezone']['name']} ({location['timezone']['offset']})")
        print()
        print(f"🖥️  Device Type: {viewport['device_type']}")
        print(f"📐 Terminal Size: {viewport['terminal_size']['width']}×{viewport['terminal_size']['height']}")
        print(f"⌨️  CLI Only: {interface['cli_only']}")
        print(f"📴 Offline Mode: {interface['offline_mode']}")
        print(f"🎨 Theme: {self.config['system_settings']['display']['theme']}")

    def show_viewport(self):
        """Show viewport and display settings."""
        viewport = self.config["system_settings"]["viewport"]
        display = self.config["system_settings"]["display"]

        print("🖥️  Viewport & Display Settings")
        print("=" * 40)
        print(f"Device Type: {viewport['device_type']}")
        print(f"Terminal Size: {viewport['terminal_size']['width']}×{viewport['terminal_size']['height']}")
        print(f"Grid Dimensions: {viewport['grid_dimensions']['width']}×{viewport['grid_dimensions']['height']}")
        print(f"Precision Mode: {viewport['precision_mode']}")
        print(f"Coordinate System: {viewport['coordinate_system']}")
        print()
        print(f"Color Support: {display['color_support']}")
        print(f"Unicode Support: {display['unicode_support']}")
        print(f"Theme: {display['theme']}")
        print(f"Render Mode: {display['render_mode']}")

    def show_interface(self):
        """Show interface settings."""
        interface = self.config["system_settings"]["interface"]
        performance = self.config["system_settings"]["performance"]

        print("⚙️  Interface & Performance Settings")
        print("=" * 40)
        print(f"CLI Only: {interface['cli_only']}")
        print(f"Offline Mode: {interface['offline_mode']}")
        print(f"Verbose Logging: {interface['verbose_logging']}")
        print(f"Confirm Destructive: {interface['confirm_destructive']}")
        print(f"Auto Save: {interface['auto_save']}")
        print()
        print(f"Auto Update Check: {performance['auto_update_check']}")
        print(f"Telemetry Enabled: {performance['telemetry_enabled']}")
        print(f"Cache Enabled: {performance['cache_enabled']}")
        print(f"Compression Enabled: {performance['compression_enabled']}")

    def show_location(self):
        """Show location and world navigation settings."""
        location = self.config["location"]
        world_nav = self.config["world_navigation"]

        print("🌍 Location & World Navigation")
        print("=" * 40)
        print(f"TIZO Code: {location['tizo_code']}")
        print(f"City: {location['city_name']}, {location['country']}")
        print(f"Continent: {location['continent']}")
        print(f"Region: {location['region']}")
        print(f"Coordinates: {location['coordinates']['latitude']}, {location['coordinates']['longitude']}")
        print(f"Timezone: {location['timezone']['name']} ({location['timezone']['offset']})")
        print()
        print("Nearby Cities:")
        for city in location['nearby_cities']:
            print(f"  {city['name']} ({city['code']}) - {city['distance_km']} km")
        print()
        print("Accessible Layers:")
        for layer in world_nav['accessible_layers']:
            print(f"  {layer}")
        print()
        print("Connection Quality:")
        for region, quality in world_nav['connection_quality'].items():
            print(f"  {region.title()}: {quality}")

    def enable_cli_only(self):
        """Enable CLI-only mode."""
        self.set_setting("system_settings.interface.cli_only", True)
        self.set_setting("system_settings.viewport.device_type", "TERMINAL")
        self.set_setting("accessibility.keyboard_only", True)
        print("✅ CLI-only mode enabled")

    def disable_cli_only(self):
        """Disable CLI-only mode."""
        self.set_setting("system_settings.interface.cli_only", False)
        self.set_setting("system_settings.viewport.device_type", "DESKTOP")
        self.set_setting("accessibility.keyboard_only", False)
        print("✅ CLI-only mode disabled")

    def enable_offline_mode(self):
        """Enable offline mode."""
        self.set_setting("system_settings.interface.offline_mode", True)
        self.set_setting("system_settings.performance.auto_update_check", False)
        print("✅ Offline mode enabled")

    def disable_offline_mode(self):
        """Disable offline mode."""
        self.set_setting("system_settings.interface.offline_mode", False)
        self.set_setting("system_settings.performance.auto_update_check", True)
        print("✅ Offline mode disabled")

    def set_viewport_size(self, width, height):
        """Set terminal viewport size."""
        self.set_setting("system_settings.viewport.terminal_size.width", int(width))
        self.set_setting("system_settings.viewport.terminal_size.height", int(height))
        print(f"✅ Viewport size set to {width}×{height}")

    def validate_config(self):
        """Validate configuration structure."""
        required_sections = [
            "user_profile", "location", "system_settings",
            "session_preferences", "world_navigation",
            "accessibility", "advanced", "metadata"
        ]

        errors = []
        warnings = []

        # Check required sections
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Missing required section: {section}")

        # Check schema version
        if self.config.get("user_profile", {}).get("schema_version") != "USER_PROFILE_V2":
            warnings.append("Schema version may be outdated")

        # Check TIZO code
        tizo_code = self.config.get("location", {}).get("tizo_code")
        if not tizo_code:
            errors.append("Missing TIZO location code")

        # Check viewport settings
        viewport = self.config.get("system_settings", {}).get("viewport", {})
        if not viewport.get("terminal_size"):
            errors.append("Missing viewport terminal size")

        # Print validation results
        print("🔍 Configuration Validation")
        print("=" * 40)

        if not errors and not warnings:
            print("✅ Configuration is valid")
        else:
            if errors:
                print("❌ Errors:")
                for error in errors:
                    print(f"  {error}")

            if warnings:
                print("⚠️  Warnings:")
                for warning in warnings:
                    print(f"  {warning}")

        return len(errors) == 0


def main():
    """Command-line interface for configuration management."""
    parser = argparse.ArgumentParser(description="uDOS Configuration Manager")
    parser.add_argument("--config", default="memory/sandbox/user.json", help="Path to user.json")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    subparsers.add_parser("info", help="Show configuration summary")

    # Show commands
    subparsers.add_parser("viewport", help="Show viewport settings")
    subparsers.add_parser("interface", help="Show interface settings")
    subparsers.add_parser("location", help="Show location settings")

    # Get/Set commands
    get_parser = subparsers.add_parser("get", help="Get a setting value")
    get_parser.add_argument("path", help="Setting path (e.g., system_settings.viewport.device_type)")

    set_parser = subparsers.add_parser("set", help="Set a setting value")
    set_parser.add_argument("path", help="Setting path")
    set_parser.add_argument("value", help="New value")

    # Mode commands
    subparsers.add_parser("cli-only", help="Enable CLI-only mode")
    subparsers.add_parser("gui-mode", help="Disable CLI-only mode")
    subparsers.add_parser("offline", help="Enable offline mode")
    subparsers.add_parser("online", help="Disable offline mode")

    # Viewport command
    viewport_parser = subparsers.add_parser("resize", help="Set viewport size")
    viewport_parser.add_argument("width", type=int, help="Terminal width")
    viewport_parser.add_argument("height", type=int, help="Terminal height")

    # Validation
    subparsers.add_parser("validate", help="Validate configuration")

    args = parser.parse_args()

    try:
        manager = UserConfigManager(args.config)

        if args.command == "info":
            manager.show_info()
        elif args.command == "viewport":
            manager.show_viewport()
        elif args.command == "interface":
            manager.show_interface()
        elif args.command == "location":
            manager.show_location()
        elif args.command == "get":
            value = manager.get_setting(args.path)
            print(f"{args.path} = {value}")
        elif args.command == "set":
            result = manager.set_setting(args.path, args.value)
            print(result)
        elif args.command == "cli-only":
            manager.enable_cli_only()
        elif args.command == "gui-mode":
            manager.disable_cli_only()
        elif args.command == "offline":
            manager.enable_offline_mode()
        elif args.command == "online":
            manager.disable_offline_mode()
        elif args.command == "resize":
            manager.set_viewport_size(args.width, args.height)
        elif args.command == "validate":
            manager.validate_config()
        else:
            manager.show_info()

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
