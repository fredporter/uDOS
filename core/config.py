"""
uDOS Unified Configuration Manager
Consolidates .env, user.json, and runtime settings

This replaces:
- core/utils/config_manager.py (UserConfigManager)
- core/services/config_manager.py (ConfigManager for .env)
- core/uDOS_env.py (EnvironmentManager)

Version: 1.1.0
Author: Fred Porter
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from dotenv import load_dotenv


class Config:
    """
    Unified configuration manager for uDOS.
    Handles .env files, user.json, and runtime state.
    """

    # Allowed .env keys (SYSTEM configuration only - NO user data)
    ENV_KEYS = {
        'GEMINI_API_KEY': 'Gemini AI API Key',
        'OPENROUTER_API_KEY': 'OpenRouter API Key',
        'ANTHROPIC_API_KEY': 'Anthropic API Key',
        'OPENAI_API_KEY': 'OpenAI API Key',
        'UDOS_INSTALLATION_ID': 'Installation ID',
        'DEFAULT_WORKSPACE': 'Default workspace',
        'DEFAULT_MODEL': 'Default AI model',
        'AUTO_START_WEB': 'Auto-start web dashboard',
        'AUTO_START_SERVER': 'Auto-start HTTP server',
        'HTTP_SERVER_PORT': 'HTTP server port',
        'THEME': 'Color theme',
        'MAX_SESSION_HISTORY': 'Max session history',
        'AUTO_SAVE_SESSION': 'Auto-save session',
        'CLI_EDITOR': 'CLI text editor (micro, nano, vim, vi) - default: micro',
        'WEB_EDITOR': 'Web-based editor (typo)',
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            project_root: Path to project root. Auto-detects if None.
        """
        if project_root is None:
            # Auto-detect from this file's location
            project_root = Path(__file__).parent.parent

        self.project_root = project_root
        self.env_file = project_root / '.env'
        self.user_config_file = project_root / 'memory' / 'bank' / 'user' / 'user.json'

        self._env_loaded = False
        self._user_config: Optional[Dict] = None
        self._runtime_state: Dict[str, Any] = {}

        # Auto-load on initialization
        self.load()

    # =========================================================================
    # LOADING & INITIALIZATION
    # =========================================================================

    def load(self, force: bool = False) -> bool:
        """
        Load all configuration sources.

        Args:
            force: Force reload even if already loaded

        Returns:
            True if loaded successfully
        """
        env_ok = self._load_env(force)
        user_ok = self._load_user_config(force)
        return env_ok and user_ok

    def _load_env(self, force: bool = False) -> bool:
        """Load environment variables from .env file."""
        if self._env_loaded and not force:
            return True

        if not self.env_file.exists():
            self._create_default_env()

        load_dotenv(self.env_file, override=force)
        self._env_loaded = True
        return True

    def _load_user_config(self, force: bool = False) -> bool:
        """Load user configuration from user.json."""
        if self._user_config is not None and not force:
            return True

        if not self.user_config_file.exists():
            print(f"⚠️  User config not found: {self.user_config_file}")
            return False

        try:
            with open(self.user_config_file, 'r') as f:
                self._user_config = json.load(f)
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Error loading user config: {e}")
            return False

    def _create_default_env(self) -> None:
        """Create default .env file."""
        self.env_file.write_text("""# uDOS Environment Configuration
# Edit using: CONFIG SET <key> <value>

# AI API Keys
GEMINI_API_KEY=''
OPENROUTER_API_KEY=''
ANTHROPIC_API_KEY=''
OPENAI_API_KEY=''

# Installation Identity (not user identity - see user.json for username)
UDOS_INSTALLATION_ID='default'

# Default Settings
DEFAULT_WORKSPACE='sandbox'
DEFAULT_MODEL='anthropic/claude-3.5-sonnet'
THEME='dark'

# Server Configuration
AUTO_START_WEB='false'
AUTO_START_SERVER='false'
HTTP_SERVER_PORT='8080'

# Session Settings
MAX_SESSION_HISTORY='100'
AUTO_SAVE_SESSION='true'
""")

    # =========================================================================
    # ENVIRONMENT VARIABLES (.env)
    # =========================================================================

    def get_env(self, key: str, default: str = '') -> str:
        """
        Get environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value
        """
        return os.getenv(key, default)

    def set_env(self, key: str, value: str) -> None:
        """
        Set environment variable in .env file.

        Args:
            key: Variable name
            value: Variable value

        Raises:
            ValueError: If key is not in ENV_KEYS
        """
        if key not in self.ENV_KEYS:
            allowed = ', '.join(self.ENV_KEYS.keys())
            raise ValueError(f"Unknown key: {key}\nAllowed: {allowed}")

        # Read current .env
        lines = []
        found = False

        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                lines = f.readlines()

        # Update or add key
        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}='{value}'\n")
                found = True
            else:
                new_lines.append(line)

        # Add if not found
        if not found:
            new_lines.append(f"\n# {self.ENV_KEYS[key]}\n")
            new_lines.append(f"{key}='{value}'\n")

        # Write back
        with open(self.env_file, 'w') as f:
            f.writelines(new_lines)

        # Update in environment
        os.environ[key] = value

    def list_env(self) -> Dict[str, str]:
        """List all environment variables."""
        return {
            key: self.get_env(key, '<not set>')
            for key in self.ENV_KEYS.keys()
        }

    # =========================================================================
    # USER CONFIGURATION (user.json)
    # =========================================================================

    def get_user(self, path: str, default: Any = None) -> Any:
        """
        Get user configuration value using dot notation.

        Args:
            path: Dot-separated path (e.g., 'user_profile.username')
            default: Default value if not found

        Returns:
            Configuration value

        Example:
            config.get_user('system_settings.viewport.device_type')
        """
        if self._user_config is None:
            return default

        keys = path.split('.')
        value = self._user_config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set_user(self, path: str, value: Any) -> None:
        """
        Set user configuration value using dot notation.

        Args:
            path: Dot-separated path
            value: Value to set

        Example:
            config.set_user('system_settings.theme', 'synthwave')
        """
        if self._user_config is None:
            self._load_user_config(force=True)
            if self._user_config is None:
                raise RuntimeError("Cannot load user config")

        keys = path.split('.')
        config_section = self._user_config

        # Navigate to parent
        for key in keys[:-1]:
            if key not in config_section:
                config_section[key] = {}
            config_section = config_section[key]

        # Set value (with type conversion)
        final_key = keys[-1]
        if isinstance(value, str):
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').replace('-', '').isdigit():
                value = float(value)

        config_section[final_key] = value
        self._save_user_config()

    def _save_user_config(self) -> None:
        """Save user configuration to file."""
        if self._user_config is None:
            return

        # Update timestamp
        if 'user_profile' in self._user_config:
            self._user_config['user_profile']['last_updated'] = \
                datetime.now(timezone.utc).isoformat()

        with open(self.user_config_file, 'w') as f:
            json.dump(self._user_config, f, indent=2, ensure_ascii=False)

    # =========================================================================
    # RUNTIME STATE (temporary, not persisted)
    # =========================================================================

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get runtime state value.

        Args:
            key: State key
            default: Default value

        Returns:
            State value
        """
        return self._runtime_state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set runtime state value.

        Args:
            key: State key
            value: State value
        """
        self._runtime_state[key] = value

    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================

    @property
    def username(self) -> str:
        """Get username from user config only (single source of truth)."""
        # Read from USER_PROFILE.NAME (sandbox/user/user.json)
        name = self.get_user('USER_PROFILE.NAME')
        if not name:
            # Fallback to lowercase structure (legacy)
            name = self.get_user('user_profile.username', 'user')
        return name

    @property
    def timezone(self) -> str:
        """Get timezone from user config."""
        # Read from USER_PROFILE.TIMEZONE (sandbox/user/user.json)
        tz = self.get_user('USER_PROFILE.TIMEZONE')
        if not tz:
            # Fallback to lowercase structure (legacy)
            tz = self.get_user('user_profile.timezone', 'UTC')
        return tz

    @property
    def location(self) -> str:
        """Get location from user config."""
        # Read from USER_PROFILE.LOCATION (sandbox/user/user.json)
        loc = self.get_user('USER_PROFILE.LOCATION')
        if not loc:
            # Try LOCATION_DATA structure
            city = self.get_user('LOCATION_DATA.CITY')
            country = self.get_user('LOCATION_DATA.COUNTRY')
            if city and country:
                loc = f"{city}, {country}"
            else:
                # Fallback to lowercase structure (legacy)
                loc = self.get_user('user_profile.location', 'Unknown')
        return loc

    @property
    def installation_id(self) -> str:
        """Get installation ID."""
        return self.get_env('UDOS_INSTALLATION_ID', 'default')

    @property
    def theme(self) -> str:
        """Get current theme."""
        return self.get_env('THEME') or \
               self.get_user('system_settings.interface.theme', 'dark')

    @property
    def default_workspace(self) -> str:
        """Get default workspace."""
        return self.get_env('DEFAULT_WORKSPACE', 'sandbox')

    @property
    def color_palette(self) -> str:
        """Get current color palette."""
        return self.get_user('system_settings.interface.color_palette', 'polaroid')

    @property
    def dev_mode(self) -> bool:
        """Get Dev Mode status (runtime or user config)."""
        return self.get('DEV_MODE', False) or self.get_user('DEV_MODE', False)

    @property
    def cli_editor(self) -> str:
        """Get CLI editor preference (default: micro)."""
        return self.get_env('CLI_EDITOR', 'micro')

    def has_api_key(self, service: str) -> bool:
        """
        Check if API key is configured.

        Args:
            service: Service name (gemini, openrouter, anthropic, openai)

        Returns:
            True if API key exists
        """
        key_map = {
            'gemini': 'GEMINI_API_KEY',
            'openrouter': 'OPENROUTER_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
        }

        env_key = key_map.get(service.lower())
        if not env_key:
            return False

        api_key = self.get_env(env_key)
        return bool(api_key and api_key != '')


# Singleton instance
_config = None


def get_config(project_root: Optional[Path] = None) -> Config:
    """
    Get singleton Config instance.

    Args:
        project_root: Project root path (only used on first call)

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(project_root)
    return _config
