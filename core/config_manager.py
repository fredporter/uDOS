"""
⚠️ DEPRECATED: This module is deprecated as of v1.1.5.1 (November 30, 2025)
Use `core.config.Config` instead for new code.

This ConfigManager will be removed in v2.1.0.

Migration:
    # OLD (deprecated):
    from core.config_manager import ConfigManager
    config = ConfigManager()
    value = config.get('key')
    config.set('key', 'value', persist=True)

    # NEW (v1.1.5.1+):
    from core.config import Config
    config = Config()
    # For user data:
    value = config.get_user('USER_PROFILE.KEY', default)
    config.set_user('USER_PROFILE.KEY', value)
    # For env variables:
    value = config.get_env('API_KEY', default)
    config.set_env('API_KEY', value)

---

uDOS Unified Configuration Manager (v1.5.0+)

Provides a single source of truth for configuration across .env, user.json, and runtime state.
Implements bidirectional synchronization to ensure consistency.

Key Features:
- Auto-load from multiple sources with priority: runtime > user.json > .env > defaults
- Bidirectional sync (runtime ↔ files)
- Automatic validation and type checking
- Configuration backup/restore
- Migration support for old formats

Usage:
    from core.config_manager import ConfigManager

    # Initialize (typically done once at startup)
    config = ConfigManager()

    # Get values
    username = config.get('username')
    api_key = config.get('GEMINI_API_KEY')

    # Set values (auto-persists to appropriate files)
    config.set('username', 'Fred', persist=True)

    # Manual save (if needed)
    config.save()
"""

import json
import warnings

# Deprecation warning
warnings.warn(
    "ConfigManager is deprecated as of v1.1.5.1. "
    "Use 'from core.config import Config' instead. "
    "See module docstring for migration guide. "
    "ConfigManager will be removed in v2.1.0.",
    DeprecationWarning,
    stacklevel=2
)
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime

# Import grid utilities for TILE code validation
try:
    from core.utils.grid_utils import validate_tile_code, parse_tile_code
except ImportError:
    # Fallback if grid_utils not available yet
    def validate_tile_code(code: str) -> bool:
        return '-' in code
    def parse_tile_code(code: str) -> dict:
        return {}


class ConfigManager:
    """
    Unified configuration manager - single source of truth for all uDOS configuration.

    Manages three configuration sources:
    1. .env file (system settings, API keys)
    2. user.json file (user profile, preferences)
    3. Runtime state (in-memory cache)

    Priority: runtime > user.json > .env > defaults
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            base_path: Root path of uDOS installation (auto-detected if not provided)
        """
        # Determine base path
        if base_path is None:
            # Auto-detect: go up from core/config_manager.py to project root
            base_path = Path(__file__).parent.parent
        self.base_path = Path(base_path)

        # Configuration file paths
        self.env_path = self.base_path / '.env'
        self.user_json_path = self.base_path / 'sandbox' / 'user.json'

        # In-memory configuration cache (single source of truth)
        self._config: Dict[str, Any] = {}

        # Track which fields have been modified (for smart persistence)
        self._modified_fields: set = set()

        # Configuration schema (for validation)
        self._schema = self._get_schema()

        # Load all configuration sources
        self.load_all()

    def _get_schema(self) -> Dict[str, Dict[str, Any]]:
        """
        Define configuration schema with types and defaults.

        Returns:
            Schema dictionary with field definitions
        """
        return {
            # API Keys
            'GEMINI_API_KEY': {
                'type': str,
                'default': '',
                'required': False,
                'source': 'env',
                'description': 'Gemini API key for AI features'
            },
            'GITHUB_TOKEN': {
                'type': str,
                'default': '',
                'required': False,
                'source': 'env',
                'description': 'GitHub token for extension marketplace'
            },

            # User Profile
            'USERNAME': {
                'type': str,
                'default': 'user',
                'required': True,
                'source': 'env',
                'description': 'User name'
            },
            'PASSWORD': {
                'type': str,
                'default': '',
                'required': False,
                'source': 'env',
                'description': 'User password (hashed)'
            },
            'ROLE': {
                'type': str,
                'default': 'admin',
                'required': False,
                'source': 'env',
                'description': 'User role (admin, user, guest)'
            },

            # Planet Configuration
            'PLANET': {
                'type': str,
                'default': 'Earth',
                'required': False,
                'source': 'env',
                'description': 'Current planet'
            },

            # Theme
            'ACTIVE_THEME': {
                'type': str,
                'default': 'dungeon',
                'required': False,
                'source': 'env',
                'description': 'Active theme (default, dungeon, cyberpunk)'
            },

            # Timezone
            'TIMEZONE': {
                'type': str,
                'default': 'UTC',
                'required': False,
                'source': 'env',
                'description': 'User timezone'
            },
            'TIMEZONE_OS': {
                'type': str,
                'default': '+00:00',
                'required': False,
                'source': 'env',
                'description': 'OS timezone offset'
            },

            # Installation
            'INSTALLATION_ID': {
                'type': str,
                'default': 'default',
                'required': False,
                'source': 'env',
                'description': 'Unique installation identifier'
            },

            # System Configuration
            'OFFLINE_MODE_ALLOWED': {
                'type': bool,
                'default': True,
                'required': False,
                'source': 'env',
                'description': 'Allow offline mode'
            },
            'AUTO_UPDATE_CHECK': {
                'type': bool,
                'default': True,
                'required': False,
                'source': 'env',
                'description': 'Check for updates automatically'
            },
            'TELEMETRY_ENABLED': {
                'type': bool,
                'default': False,
                'required': False,
                'source': 'env',
                'description': 'Enable telemetry'
            },

            # Editor Preferences
            'CLI_EDITOR': {
                'type': str,
                'default': 'micro',
                'required': False,
                'source': 'env',
                'description': 'CLI text editor (micro, nano, vim)'
            },
            'WEB_EDITOR': {
                'type': str,
                'default': 'typo',
                'required': False,
                'source': 'env',
                'description': 'Web text editor'
            },

            # User data fields (lowercase for dashboard compatibility)
            'username': {
                'type': str,
                'default': 'user',
                'required': False,
                'source': 'user_json',
                'description': 'User name (from user.json)'
            },
            'location': {
                'type': str,
                'default': 'Unknown',
                'required': False,
                'source': 'planets_json',
                'description': 'User location (from planets.json)'
            },
            'timezone': {
                'type': str,
                'default': 'UTC',
                'required': False,
                'source': 'user_json',
                'description': 'User timezone (from user.json)'
            },
            'planet': {
                'type': str,
                'default': 'Earth',
                'required': False,
                'source': 'planets_json',
                'description': 'Current planet (from planets.json)'
            },
            'project_name': {
                'type': str,
                'default': 'uDOS',
                'required': False,
                'source': 'user_json',
                'description': 'Project name (from user.json)'
            },
            'project_description': {
                'type': str,
                'default': 'CLI Framework',
                'required': False,
                'source': 'user_json',
                'description': 'Project description (from user.json)'
            },
            'mode': {
                'type': str,
                'default': 'STANDARD',
                'required': False,
                'source': 'user_json',
                'description': 'Preferred mode (from user.json)'
            },

            # TILE code system (v2.0.0)
            'tile_code': {
                'type': str,
                'default': None,
                'required': False,
                'source': 'user_json',
                'description': 'TILE code location (e.g., OC-AU-SYD)'
            },
            'grid_cell': {
                'type': str,
                'default': None,
                'required': False,
                'source': 'user_json',
                'description': 'Grid cell reference (e.g., AA340, YY320)'
            },
            'layer': {
                'type': int,
                'default': 100,
                'required': False,
                'source': 'user_json',
                'description': 'Map layer (100=base world map, aligns with teletext pages)'
            },
        }

    def get_defaults(self) -> Dict[str, Any]:
        """
        Get default configuration values from schema.

        Returns:
            Dictionary of default values
        """
        defaults = {}
        for key, spec in self._schema.items():
            defaults[key] = spec['default']
        return defaults

    def load_all(self) -> None:
        """
        Load configuration from all sources with priority system.

        Priority order:
        1. Defaults (lowest)
        2. .env file
        3. user.json file
        4. planets.json (for planet/location data)
        5. Runtime modifications (highest)
        """
        # 1. Start with defaults
        self._config = self.get_defaults()

        # 2. Load .env (overrides defaults)
        self.load_env()

        # 3. Load user.json (overrides .env where applicable)
        self.load_user_json()

        # 4. Load planet data from planets.json
        self.load_planet_data()

        # 5. Sync username between sources
        self._sync_username()

        # Clear modified fields after load
        self._modified_fields.clear()

    def load_env(self) -> None:
        """Load configuration from .env file."""
        if not self.env_path.exists():
            return

        try:
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')

                        # Type conversion
                        if key in self._schema:
                            expected_type = self._schema[key]['type']
                            if expected_type == bool:
                                value = value.lower() in ('true', '1', 'yes')
                            elif expected_type == int:
                                try:
                                    value = int(value)
                                except ValueError:
                                    pass

                        self._config[key] = value
        except Exception as e:
            print(f"⚠️  Error loading .env: {e}")

    def load_user_json(self) -> None:
        """Load configuration from user.json file."""
        if not self.user_json_path.exists():
            return

        try:
            with open(self.user_json_path, 'r') as f:
                user_data = json.load(f)

                # Handle both old (uppercase USER_PROFILE) and new (lowercase user_profile) formats
                profile = user_data.get('USER_PROFILE') or user_data.get('user_profile', {})

                if profile:
                    # Map profile fields to config keys (handles both old uppercase and new lowercase)
                    if 'NAME' in profile:
                        self._config['username'] = profile['NAME']
                    elif 'username' in profile:
                        self._config['username'] = profile['username']

                    if 'TIMEZONE' in profile:
                        self._config['timezone'] = profile['TIMEZONE']
                    elif 'timezone' in profile:
                        self._config['timezone'] = profile['timezone']

                    if 'PREFERRED_MODE' in profile:
                        self._config['mode'] = profile['PREFERRED_MODE']
                    elif 'mode' in profile:
                        self._config['mode'] = profile['mode']

                    if 'project_name' in profile:
                        self._config['project_name'] = profile['project_name']

                # Extract location data (TILE code system v2.0.0)
                location_data = user_data.get('LOCATION_DATA') or user_data.get('location', {})
                if location_data:
                    # Build location string from available fields
                    city = location_data.get('CITY') or location_data.get('city_name', '')
                    region = location_data.get('region', '')
                    country = location_data.get('COUNTRY') or location_data.get('country', '')

                    location_parts = [p for p in [city, region, country] if p]
                    if location_parts:
                        self._config['location'] = ', '.join(location_parts)

                    # Store TILE code if available (v2.0.0)
                    if 'tile_code' in location_data:
                        self._config['tile_code'] = location_data['tile_code']

                    # Store grid cell if available
                    if 'grid_cell' in location_data:
                        self._config['grid_cell'] = location_data['grid_cell']

                    # Store layer (default: 100 = base world map)
                    self._config['layer'] = location_data.get('layer', 100)

                # Extract PROJECT if present (old format)
                if 'PROJECT' in user_data:
                    proj = user_data['PROJECT']
                    if 'NAME' in proj:
                        self._config['project_name'] = proj['NAME']
                    if 'DESCRIPTION' in proj:
                        self._config['project_description'] = proj['DESCRIPTION']

        except Exception as e:
            print(f"⚠️  Error loading user.json: {e}")

    def load_planet_data(self) -> None:
        """Load planet and location data from planets.json."""
        planets_path = self.base_path / 'sandbox' / 'user' / 'planets.json'

        if not planets_path.exists():
            return

        try:
            with open(planets_path, 'r') as f:
                planet_data = json.load(f)

                # Get current planet
                current_planet_name = planet_data.get('current_planet', 'Earth')
                self._config['planet'] = current_planet_name

                # Get planet details
                user_planets = planet_data.get('user_planets', {})
                if current_planet_name in user_planets:
                    planet = user_planets[current_planet_name]

                    # Extract location if available (TILE code system v2.0.0)
                    if 'location' in planet and planet['location']:
                        loc = planet['location']

                        # Build location string
                        location_parts = []
                        if 'name' in loc:
                            location_parts.append(loc['name'])
                        if 'region' in loc and loc['region']:
                            location_parts.append(loc['region'])
                        if 'country' in loc:
                            location_parts.append(loc['country'])

                        if location_parts:
                            self._config['location'] = ', '.join(location_parts)

                        # Store TILE code (v2.0.0)
                        if 'tile_code' in loc:
                            self._config['tile_code'] = loc['tile_code']

                        # Store grid cell reference
                        if 'grid_cell' in loc:
                            self._config['grid_cell'] = loc['grid_cell']

                        # Store layer (default: 100 = base world map)
                        self._config['layer'] = loc.get('layer', 100)

                        # Store timezone
                        if 'timezone' in loc:
                            self._config['planet_timezone'] = loc['timezone']

        except Exception as e:
            print(f"⚠️  Error loading planets.json: {e}")

    def _sync_field(self, user_field: str, env_field: str) -> None:
        """
        Sync a field between user.json and .env formats.

        Args:
            user_field: Field name in user.json (e.g., 'username')
            env_field: Field name in .env (e.g., 'UDOS_USERNAME')
        """
        user_value = self._config.get(user_field)
        env_value = self._config.get(env_field)
        default_value = self._schema[user_field]['default']

        # If both exist and differ:
        if user_value and env_value and user_value != env_value:
            # If user_field is still default and .env has a value, .env wins
            if user_value == default_value:
                self._config[user_field] = env_value
                self._modified_fields.add(user_field)
            # Otherwise user.json takes priority
            else:
                self._config[env_field] = user_value
                self._modified_fields.add(env_field)
        # If only env_field exists, copy to user_field
        elif env_value and not user_value:
            self._config[user_field] = env_value
            self._modified_fields.add(user_field)
        # If only user_field exists, copy to env_field
        elif user_value and not env_value:
            self._config[env_field] = user_value
            self._modified_fields.add(env_field)

    def _sync_username(self) -> None:
        """No longer needed - all config in .env now."""
        pass

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any, persist: bool = True) -> None:
        """
        Set configuration value and optionally persist to files.

        Args:
            key: Configuration key
            value: New value
            persist: If True, save to appropriate file(s)
        """
        # Validate against schema if key is defined
        if key in self._schema:
            expected_type = self._schema[key]['type']
            if not isinstance(value, expected_type):
                # Try type conversion
                try:
                    if expected_type == str:
                        value = str(value)
                    elif expected_type == int:
                        value = int(value)
                    elif expected_type == bool:
                        value = bool(value)
                except (ValueError, TypeError):
                    raise TypeError(f"Invalid type for {key}: expected {expected_type}, got {type(value)}")

        # Update in-memory cache
        self._config[key] = value
        self._modified_fields.add(key)

        # Special case: sync username changes
        if key == 'username':
            self._config['UDOS_USERNAME'] = value
            self._modified_fields.add('UDOS_USERNAME')
        elif key == 'UDOS_USERNAME':
            self._config['username'] = value
            self._modified_fields.add('username')

        # Persist if requested
        if persist:
            self.save()

    def save(self) -> None:
        """Save configuration to appropriate files (.env and user.json)."""
        self.save_env()
        self.save_user_json()
        self._modified_fields.clear()

    def save_env(self) -> None:
        """Save .env file with current configuration."""
        try:
            lines = []
            lines.append("# uDOS Environment Configuration")
            lines.append(f"# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")

            # Group by category
            lines.append("# API Keys")
            for key in ['GEMINI_API_KEY', 'GITHUB_TOKEN']:
                if key in self._config:
                    lines.append(f"{key}={self._config[key]}")

            lines.append("")
            lines.append("# User Configuration")
            for key in ['UDOS_USERNAME', 'UDOS_LOCATION', 'UDOS_TIMEZONE']:
                if key in self._config:
                    value = self._config[key]
                    # Map from user.json names if needed
                    if key == 'UDOS_LOCATION':
                        value = self._config.get('location', value)
                    elif key == 'UDOS_TIMEZONE':
                        value = self._config.get('timezone', value)
                    lines.append(f"{key}={value}")

            lines.append("")
            lines.append("# Installation Settings")
            for key in ['UDOS_INSTALL_PATH', 'UDOS_INSTALLATION_ID', 'UDOS_VERSION']:
                if key in self._config:
                    lines.append(f"{key}={self._config[key]}")

            lines.append("")
            lines.append("# DEV MODE Settings (v1.5.0+)")
            for key in ['UDOS_MASTER_PASSWORD', 'UDOS_MASTER_USER']:
                if key in self._config and self._config[key]:
                    lines.append(f"{key}={self._config[key]}")

            lines.append("")
            lines.append("# Advanced Settings")
            for key in ['UDOS_DEBUG', 'UDOS_VIEWPORT_MODE']:
                if key in self._config and self._config[key] != self._schema[key]['default']:
                    lines.append(f"{key}={self._config[key]}")

            # Write to file
            self.env_path.write_text('\n'.join(lines) + '\n')
        except Exception as e:
            print(f"⚠️  Error saving .env: {e}")

    def save_user_json(self) -> None:
        """Save user.json file with current configuration."""
        try:
            # Ensure directory exists
            self.user_json_path.parent.mkdir(parents=True, exist_ok=True)

            # Build nested structure
            profile_data = {}
            display_data = {}

            for key, spec in self._schema.items():
                if spec['source'] == 'user_json' and key in self._config:
                    # Theme goes in system_settings.display
                    if key in ['theme', 'grid_size']:
                        display_data[key] = self._config[key]
                    else:
                        profile_data[key] = self._config[key]

            # Build final structure
            user_data = {
                "user_profile": profile_data
            }
            if display_data:
                user_data["system_settings"] = {
                    "display": display_data
                }

            # Write to file with pretty formatting
            with open(self.user_json_path, 'w') as f:
                json.dump(user_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving user.json: {e}")

    def validate(self) -> List[str]:
        """
        Validate configuration against schema.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required fields
        for key, spec in self._schema.items():
            if spec['required'] and not self._config.get(key):
                errors.append(f"Required field missing: {key}")

        # Check types
        for key, spec in self._schema.items():
            if key in self._config:
                value = self._config[key]
                expected_type = spec['type']
                if not isinstance(value, expected_type):
                    errors.append(f"Invalid type for {key}: expected {expected_type}, got {type(value)}")

        # Check username sync
        if self._config.get('username') != self._config.get('UDOS_USERNAME'):
            errors.append(f"Username mismatch: username={self._config.get('username')}, UDOS_USERNAME={self._config.get('UDOS_USERNAME')}")

        return errors

    def repair(self) -> List[str]:
        """
        Auto-repair common configuration issues.

        Returns:
            List of repairs performed
        """
        repairs = []

        # Set defaults for missing required fields
        for key, spec in self._schema.items():
            if spec['required'] and not self._config.get(key):
                self._config[key] = spec['default']
                repairs.append(f"Set default value for {key}: {spec['default']}")

        # Save repairs
        if repairs:
            self.save()

        return repairs

    def validate_tile_code(self, tile_code: str) -> bool:
        """
        Validate TILE code format using grid utilities.

        Args:
            tile_code: TILE code to validate (e.g., "QZ185-100")

        Returns:
            True if valid, False otherwise
        """
        return validate_tile_code(tile_code)

    def get_location_info(self) -> Dict[str, Any]:
        """
        Get parsed location information from TILE code.

        Returns:
            Dictionary with location details (grid, lat/long, layer)
        """
        tile_code = self._config.get('tile_code')
        if not tile_code:
            return {}

        try:
            parsed = parse_tile_code(tile_code)
            # Add lat/long conversion if available
            try:
                from core.utils.grid_utils import tile_to_latlong
                lat, lon, layer = tile_to_latlong(tile_code)
                parsed['latitude'] = lat
                parsed['longitude'] = lon
            except:
                pass

            return parsed
        except:
            return {}

    def backup(self, backup_dir: Optional[Path] = None) -> Path:
        """
        Create backup of current configuration.

        Args:
            backup_dir: Directory to store backup (default: memory/config_backups/)

        Returns:
            Path to backup directory
        """
        if backup_dir is None:
            backup_dir = self.base_path / 'memory' / 'config_backups'

        # Create timestamped backup directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)

        # Backup .env
        if self.env_path.exists():
            shutil.copy2(self.env_path, backup_path / '.env')

        # Backup user.json
        if self.user_json_path.exists():
            shutil.copy2(self.user_json_path, backup_path / 'user.json')

        return backup_path

    def restore(self, backup_path: Path) -> None:
        """
        Restore configuration from backup.

        Args:
            backup_path: Path to backup directory
        """
        # Restore .env
        backup_env = backup_path / '.env'
        if backup_env.exists():
            shutil.copy2(backup_env, self.env_path)

        # Restore user.json
        backup_user_json = backup_path / 'user.json'
        if backup_user_json.exists():
            shutil.copy2(backup_user_json, self.user_json_path)

        # Reload configuration
        self.load_all()

    def __repr__(self) -> str:
        """String representation of ConfigManager."""
        return f"ConfigManager(username={self._config.get('username')}, keys={len(self._config)})"


# Global instance (initialized in uDOS_main.py)
_global_config_manager: Optional[ConfigManager] = None


def get_config_manager(base_path: Optional[Path] = None) -> ConfigManager:
    """
    Get or create global ConfigManager instance.

    Args:
        base_path: Base path for uDOS installation

    Returns:
        Global ConfigManager instance
    """
    global _global_config_manager

    if _global_config_manager is None:
        _global_config_manager = ConfigManager(base_path)

    return _global_config_manager


def reset_config_manager() -> None:
    """Reset global ConfigManager (for testing)."""
    global _global_config_manager
    _global_config_manager = None
