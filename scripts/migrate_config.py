#!/usr/bin/env python3
"""
uDOS Configuration Migration Script

Migrates from old USER.UDO format to new user.md + .env structure.
Integrates TIZO location codes and timezone detection.

Version: 1.0.0
Author: Fred Porter
"""

import json
import os
import uuid
from pathlib import Path
from datetime import datetime
import sys

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))
from core.utils.tizo_manager import TIZOLocationManager


class ConfigMigrator:
    """Migrate uDOS configuration to new structure."""

    def __init__(self, workspace_dir="."):
        self.workspace_dir = Path(workspace_dir)
        self.sandbox_dir = self.workspace_dir / "sandbox"
        self.tizo_manager = TIZOLocationManager(self.workspace_dir / "data" / "system")

    def load_old_user_config(self, filepath=None):
        """Load old USER.UDO configuration."""
        if filepath is None:
            filepath = self.sandbox_dir / "USER.UDO.backup"

        if not filepath.exists():
            # Try the current USER.UDO
            filepath = self.sandbox_dir / "USER.UDO"

        if not filepath.exists():
            print(f"⚠️  No old configuration found at {filepath}")
            return None

        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading old config: {e}")
            return None

    def generate_installation_id(self):
        """Generate a unique installation ID."""
        return uuid.uuid4().hex[:16]

    def detect_user_location(self, old_config):
        """Detect user location from old config or auto-detect."""
        # Try to get location from old config
        old_location = None
        old_timezone = None

        if old_config:
            old_location = old_config.get("LOCATION", old_config.get("USER_PROFILE", {}).get("LOCATION"))
            old_timezone = old_config.get("TIMEZONE", old_config.get("USER_PROFILE", {}).get("TIMEZONE"))

        # Auto-detect current location
        detection = self.tizo_manager.auto_detect_location()

        # If old config had Melbourne/Australia, use MEL
        if old_location and ("melbourne" in old_location.lower() or "australia" in old_location.lower()):
            return "MEL"

        # Use auto-detected location
        return detection["recommended_city"]["code"]

    def create_env_file(self, old_config, installation_id):
        """Create new .env file with sensitive data."""
        env_content = """# uDOS Environment Configuration
# Edit these values using CLI commands only: udos config set <key> <value>

# User Information (sensitive data)
UDOS_USERNAME='{username}'
UDOS_PASSWORD=''

# Gemini OK Assisted Task API Key
GEMINI_API_KEY='{api_key}'

# System Timezone (captured from system at installation)
SYSTEM_TIMEZONE='{timezone}'
SYSTEM_TIMEZONE_OFFSET='{timezone_offset}'

# Unique Installation ID (auto-generated)
UDOS_INSTALLATION_ID='{installation_id}'

# System Configuration
OFFLINE_MODE_ALLOWED={offline_mode}
AUTO_UPDATE_CHECK={auto_update}
TELEMETRY_ENABLED={telemetry}
""".format(
            username=old_config.get("USER_PROFILE", {}).get("NAME", old_config.get("NAME", "user")),
            api_key=old_config.get("SYSTEM_CONFIG", {}).get("GEMINI_API_KEY", ""),
            timezone="AEST",  # Default for Melbourne
            timezone_offset="+10:00",
            installation_id=installation_id,
            offline_mode=str(old_config.get("SYSTEM_CONFIG", {}).get("OFFLINE_MODE_ALLOWED", True)).lower(),
            auto_update=str(old_config.get("SYSTEM_CONFIG", {}).get("AUTO_UPDATE_CHECK", True)).lower(),
            telemetry=str(old_config.get("SYSTEM_CONFIG", {}).get("TELEMETRY_ENABLED", False)).lower()
        )

        env_file = self.workspace_dir / ".env"
        with open(env_file, 'w') as f:
            f.write(env_content)

        print(f"✅ Created .env file: {env_file}")
        return env_file

    def create_user_md(self, old_config, tizo_code, installation_id):
        """Create new user.md file with TIZO location data."""

        # Get TIZO profile data
        profile_data = self.tizo_manager.generate_user_profile_data(tizo_code)

        # Get session preferences from old config
        session_prefs = old_config.get("SESSION_PREFERENCES", {}) if old_config else {}
        display_settings = old_config.get("DISPLAY_SETTINGS", {}) if old_config else {}
        location_data = old_config.get("LOCATION_DATA", {}) if old_config else {}

        user_md_content = f"""# uDOS User Profile
**Installation ID**: `{installation_id}`
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 🌍 Location Configuration

### TIZO Location Code
**Primary Location**: `{profile_data['tizo_code']}` ({profile_data['city_name']}, {profile_data['country']})
**Coordinates**: {profile_data['coordinates']['lat']}°, {profile_data['coordinates']['lon']}°
**Continent**: {profile_data['continent']}
**Region**: {profile_data['region']}

### Default Locations
| Layer | Location | Code | Description |
|-------|----------|------|-------------|
| **SURFACE** | {profile_data['city_name']} | {profile_data['tizo_code']} | Physical world location |
| **CLOUD** | {profile_data['continent']} Cloud | {profile_data['tizo_code']}-CLOUD | Regional cloud node |
| **SATELLITE** | {profile_data['continent']} Satellite | {profile_data['tizo_code']}-SAT | Regional satellite network |
| **DUNGEON-1** | {profile_data['city_name']} Archives | {profile_data['tizo_code']}-D1 | Local data tunnels |

### Nearby TIZO Cities
| City | Code | Distance | Timezone | Status |
|------|------|----------|----------|--------|
| **{profile_data['city_name']}** | {profile_data['tizo_code']} | 0 km | {profile_data['timezone']} ({profile_data['timezone_offset']}) | **Current** |
"""

        # Add nearby cities
        for city in profile_data['nearby_cities'][:4]:
            user_md_content += f"| {city['name']} | {city['code']} | {city['distance_km']} km | {city['timezone']} ({city['timezone_offset']}) | Available |\n"

        user_md_content += f"""
---

## ⚙️ User Preferences

### Session Preferences
- **Assist Mode**: {session_prefs.get('ASSIST_MODE', False)}
- **Verbose Logging**: {session_prefs.get('VERBOSE_LOGGING', False)}
- **Theme**: {session_prefs.get('THEME', 'DUNGEON_CRAWLER')}
- **Auto Save**: {session_prefs.get('AUTO_SAVE', True)}
- **Confirm Destructive**: {session_prefs.get('CONFIRM_DESTRUCTIVE', True)}

### Display Settings
- **Device Type**: {display_settings.get('DEVICE_TYPE', 'DESKTOP')}
- **Terminal Size**: {display_settings.get('TERMINAL_SIZE', '80×24')}
- **Grid Dimensions**: {display_settings.get('GRID_DIMENSIONS', '10×9')}
- **Color Support**: {display_settings.get('COLOR_SUPPORT', True)}
- **Unicode Support**: {display_settings.get('UNICODE_SUPPORT', True)}

### Location Data
- **Text Grid Position**: {location_data.get('TEXT_GRID_POSITION', '0,0')}
- **Current Layer**: {location_data.get('CURRENT_LAYER', 'MAIN')}
- **Coordinate System**: {location_data.get('COORDINATE_SYSTEM', 'ZERO_INDEXED')}
- **Precision Mode**: {location_data.get('PRECISION_MODE', 'UCELL_16x16')}

---

## 🗺️ World Navigation

### Timezone Information
**Primary**: {profile_data['timezone']}
**Offset**: {profile_data['timezone_offset']}

### Connection Quality
"""

        # Add connection quality information
        for region, quality in profile_data['connection_quality'].items():
            user_md_content += f"- **{region.title()}**: {quality}\n"

        user_md_content += f"""
### Accessible Layers
"""

        # Add accessible layers
        for layer in profile_data['udos_layers']:
            user_md_content += f"- **{layer}**: Available\n"

        user_md_content += f"""
---

## 📊 Installation Metadata

| Field | Value |
|-------|-------|
| **Schema Version** | USER_PROFILE_V2 |
| **Installation Type** | Standard |
| **Profile Version** | 2.0 |
| **Backup Status** | Auto-enabled |
| **Sync Status** | Local-only |

---

## 🎯 Customization Notes

### Default City Override
Current: **{profile_data['city_name']}** ({profile_data['tizo_code']})
*You can change this to any TIZO city using:*
`udos config set location <CITY_CODE>`

### Available TIZO Cities
Use `udos map cities` to see all available location codes.

---

*This profile is automatically synchronized with your installation environment variables.*
*Sensitive data (credentials, API keys) are stored securely in `.env`*
"""

        user_md_file = self.sandbox_dir / "user.md"
        with open(user_md_file, 'w') as f:
            f.write(user_md_content)

        print(f"✅ Created user.md file: {user_md_file}")
        return user_md_file

    def migrate_configuration(self):
        """Perform complete configuration migration."""
        print("🔄 uDOS Configuration Migration")
        print("=" * 50)

        # Load old configuration
        print("\n📂 Loading old configuration...")
        old_config = self.load_old_user_config()

        if old_config:
            print(f"✅ Loaded configuration for user: {old_config.get('USER_PROFILE', {}).get('NAME', 'Unknown')}")
        else:
            print("ℹ️  No old configuration found, creating fresh setup")

        # Generate installation ID
        installation_id = self.generate_installation_id()
        print(f"🆔 Generated installation ID: {installation_id}")

        # Detect location
        print("\n🌍 Detecting location...")
        tizo_code = self.detect_user_location(old_config)
        location_data = self.tizo_manager.generate_user_profile_data(tizo_code)
        print(f"📍 Detected location: {location_data['city_name']} ({tizo_code})")

        # Create new files
        print("\n📝 Creating new configuration files...")
        env_file = self.create_env_file(old_config, installation_id)
        user_md_file = self.create_user_md(old_config, tizo_code, installation_id)

        # Summary
        print("\n✅ Migration Complete!")
        print(f"📁 Environment file: {env_file}")
        print(f"📄 User profile: {user_md_file}")
        print(f"🌍 Location: {location_data['city_name']} ({tizo_code})")
        print(f"⏰ Timezone: {location_data['timezone']} ({location_data['timezone_offset']})")

        if old_config:
            backup_file = self.sandbox_dir / "USER.UDO.backup"
            print(f"💾 Old config backed up: {backup_file}")

        return {
            "env_file": env_file,
            "user_md_file": user_md_file,
            "installation_id": installation_id,
            "tizo_code": tizo_code,
            "location_data": location_data
        }


def main():
    """Run the configuration migration."""
    migrator = ConfigMigrator()
    result = migrator.migrate_configuration()

    print("\n🎉 Ready to use the new uDOS configuration system!")
    print("💡 You can now:")
    print("   - Edit sensitive settings with: udos config set <key> <value>")
    print("   - Change location with: udos config set location <TIZO_CODE>")
    print("   - View available cities with: udos map cities")


if __name__ == "__main__":
    main()
