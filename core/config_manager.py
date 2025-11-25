"""
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
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime


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
            # Auto-detect: go up from core/config/ to project root
            base_path = Path(__file__).parent.parent.parent
        self.base_path = Path(base_path)

        # Configuration file paths
        self.env_path = self.base_path / '.env'
        self.user_json_path = self.base_path / 'memory' / 'sandbox' / 'user.json'

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
            'username': {
                'type': str,
                'default': 'user',
                'required': True,
                'source': 'user_json',
                'description': 'User display name'
            },
            'UDOS_USERNAME': {
                'type': str,
                'default': 'user',
                'required': False,
                'source': 'env',
                'description': 'Username in .env (synced with username)'
            },
            'password': {
                'type': (str, type(None)),
                'default': None,
                'required': False,
                'source': 'user_json',
                'description': 'User password (optional, hashed)'
            },
            'location': {
                'type': str,
                'default': 'Unknown',
                'required': False,
                'source': 'user_json',
                'description': 'User location'
            },
            'UDOS_LOCATION': {
                'type': str,
                'default': 'Unknown',
                'required': False,
                'source': 'env',
                'description': 'Location in .env (synced with location)'
            },
            'timezone': {
                'type': str,
                'default': 'UTC',
                'required': False,
                'source': 'user_json',
                'description': 'User timezone'
            },
            'UDOS_TIMEZONE': {
                'type': str,
                'default': 'UTC',
                'required': False,
                'source': 'env',
                'description': 'Timezone in .env (synced with timezone)'
            },

            # Installation Settings
            'UDOS_INSTALL_PATH': {
                'type': str,
                'default': str(self.base_path),
                'required': False,
                'source': 'env',
                'description': 'Installation directory path'
            },
            'UDOS_INSTALLATION_ID': {
                'type': str,
                'default': 'default',
                'required': False,
                'source': 'env',
                'description': 'Unique installation identifier'
            },
            'UDOS_VERSION': {
                'type': str,
                'default': '1.5.0',
                'required': False,
                'source': 'env',
                'description': 'uDOS version'
            },

            # UI Settings
            'theme': {
                'type': str,
                'default': 'dungeon',
                'required': False,
                'source': 'user_json',
                'description': 'Active theme (default, dungeon, cyberpunk)'
            },
            'grid_size': {
                'type': list,
                'default': [22, 15],
                'required': False,
                'source': 'user_json',
                'description': 'Grid size [width, height] in cells'
            },

            # DEV MODE Settings (v1.5.0+)
            'UDOS_MASTER_PASSWORD': {
                'type': str,
                'default': '',
                'required': False,
                'source': 'env',
                'description': 'Master user password for DEV MODE'
            },
            'UDOS_MASTER_USER': {
                'type': str,
                'default': 'user',
                'required': False,
                'source': 'env',
                'description': 'Master user name (must match username)'
            },

            # Advanced Settings
            'UDOS_DEBUG': {
                'type': bool,
                'default': False,
                'required': False,
                'source': 'env',
                'description': 'Debug mode enabled'
            },
            'UDOS_VIEWPORT_MODE': {
                'type': str,
                'default': 'auto',
                'required': False,
                'source': 'env',
                'description': 'Viewport mode (auto, terminal, mobile, desktop)'
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
        4. Runtime modifications (highest)
        """
        # 1. Start with defaults
        self._config = self.get_defaults()

        # 2. Load .env (overrides defaults)
        self.load_env()

        # 3. Load user.json (overrides .env where applicable)
        self.load_user_json()

        # 4. Sync username between sources
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

                # Support nested structure (user_profile, system_settings)
                flat_data = {}

                # Extract from user_profile
                if 'user_profile' in user_data:
                    flat_data.update(user_data['user_profile'])

                # Extract from system_settings.display
                if 'system_settings' in user_data and 'display' in user_data['system_settings']:
                    flat_data.update(user_data['system_settings']['display'])

                # If no nesting, use flat
                if not flat_data:
                    flat_data = user_data

                # Only load fields that are defined for user.json in schema
                for key, spec in self._schema.items():
                    if spec['source'] == 'user_json' and key in flat_data:
                        self._config[key] = flat_data[key]
        except Exception as e:
            print(f"⚠️  Error loading user.json: {e}")

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
        """Ensure username is synchronized between user.json and .env."""
        self._sync_field('username', 'UDOS_USERNAME')
        self._sync_field('location', 'UDOS_LOCATION')
        self._sync_field('timezone', 'UDOS_TIMEZONE')

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

        # Sync username
        if self._config.get('username') != self._config.get('UDOS_USERNAME'):
            self._config['UDOS_USERNAME'] = self._config['username']
            repairs.append(f"Synced UDOS_USERNAME to match username: {self._config['username']}")

        # Set defaults for missing required fields
        for key, spec in self._schema.items():
            if spec['required'] and not self._config.get(key):
                self._config[key] = spec['default']
                repairs.append(f"Set default value for {key}: {spec['default']}")

        # Save repairs
        if repairs:
            self.save()

        return repairs

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
