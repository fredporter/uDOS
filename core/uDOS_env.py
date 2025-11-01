"""
uDOS Environment Manager
Handles loading and accessing environment variables from .env file
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

class EnvironmentManager:
    """
    Manages environment configuration for uDOS.
    Loads variables from .env file and provides safe access methods.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the environment manager.

        Args:
            project_root: Path to project root. If None, auto-detects from this file.
        """
        if project_root is None:
            # Auto-detect project root (parent of core/)
            project_root = Path(__file__).parent.parent

        self.project_root = project_root
        self.env_file = project_root / '.env'
        self.env_example = project_root / '.env.example'
        self._loaded = False
        self._env_vars: Dict[str, str] = {}

        # Load environment
        self.load()

    def load(self, force: bool = False) -> bool:
        """
        Load environment variables from .env file.

        Args:
            force: Force reload even if already loaded

        Returns:
            True if loaded successfully, False otherwise
        """
        if self._loaded and not force:
            return True

        if not self.env_file.exists():
            print(f"⚠️  Warning: .env file not found at {self.env_file}")
            print(f"📝 Copy {self.env_example} to .env and configure your settings")
            return False

        # Load .env file
        load_dotenv(self.env_file, override=force)

        # Cache loaded variables
        self._cache_env_vars()
        self._loaded = True

        return True

    def _cache_env_vars(self):
        """Cache environment variables for quick access."""
        # API Keys
        self._env_vars['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY', '')
        self._env_vars['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', '')
        self._env_vars['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

        # User Preferences
        self._env_vars['DEFAULT_MODEL'] = os.getenv('DEFAULT_MODEL', 'anthropic/claude-3.5-sonnet')
        self._env_vars['MAX_SESSION_HISTORY'] = os.getenv('MAX_SESSION_HISTORY', '100')
        self._env_vars['AUTO_SAVE_SESSION'] = os.getenv('AUTO_SAVE_SESSION', 'true')

        # Server Configuration
        self._env_vars['HTTP_SERVER_PORT'] = os.getenv('HTTP_SERVER_PORT', '8080')
        self._env_vars['AUTO_START_SERVER'] = os.getenv('AUTO_START_SERVER', 'false')

        # Logging
        self._env_vars['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')
        self._env_vars['SESSION_LOG_RETENTION_DAYS'] = os.getenv('SESSION_LOG_RETENTION_DAYS', '30')

    def get(self, key: str, default: Any = None) -> str:
        """
        Get an environment variable value.

        Args:
            key: Variable name
            default: Default value if not found

        Returns:
            Variable value or default
        """
        return self._env_vars.get(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get an environment variable as integer.

        Args:
            key: Variable name
            default: Default value if not found or invalid

        Returns:
            Integer value or default
        """
        try:
            return int(self._env_vars.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get an environment variable as boolean.

        Args:
            key: Variable name
            default: Default value if not found

        Returns:
            Boolean value or default
        """
        value = self._env_vars.get(key, '').lower()
        if value in ('true', '1', 'yes', 'on'):
            return True
        elif value in ('false', '0', 'no', 'off'):
            return False
        return default

    def require(self, key: str) -> str:
        """
        Get a required environment variable.

        Args:
            key: Variable name

        Returns:
            Variable value

        Raises:
            ValueError: If variable is not set or empty
        """
        value = self._env_vars.get(key)
        if not value:
            raise ValueError(
                f"Required environment variable '{key}' is not set.\n"
                f"Please configure it in {self.env_file}"
            )
        return value

    def is_configured(self) -> bool:
        """
        Check if .env file exists and is configured.

        Returns:
            True if .env exists, False otherwise
        """
        return self.env_file.exists()

    def get_api_key(self, service: str = 'openrouter') -> Optional[str]:
        """
        Get API key for a specific service.

        Args:
            service: Service name (openrouter, anthropic, openai)

        Returns:
            API key or None if not configured
        """
        key_map = {
            'openrouter': 'OPENROUTER_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY'
        }

        key_name = key_map.get(service.lower())
        if not key_name:
            return None

        return self._env_vars.get(key_name) or None

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate environment configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check .env exists
        if not self.is_configured():
            errors.append(f".env file not found at {self.env_file}")
            errors.append(f"Copy {self.env_example} to .env")
            return False, errors

        # Check for at least one API key
        has_api_key = any([
            self._env_vars.get('OPENROUTER_API_KEY'),
            self._env_vars.get('ANTHROPIC_API_KEY'),
            self._env_vars.get('OPENAI_API_KEY')
        ])

        if not has_api_key:
            errors.append("No API keys configured. Set at least one API key in .env")

        # Validate integer values
        try:
            self.get_int('HTTP_SERVER_PORT', 8080)
        except ValueError:
            errors.append("HTTP_SERVER_PORT must be a valid integer")

        try:
            self.get_int('MAX_SESSION_HISTORY', 100)
        except ValueError:
            errors.append("MAX_SESSION_HISTORY must be a valid integer")

        try:
            self.get_int('SESSION_LOG_RETENTION_DAYS', 30)
        except ValueError:
            errors.append("SESSION_LOG_RETENTION_DAYS must be a valid integer")

        return len(errors) == 0, errors

    def __repr__(self) -> str:
        """String representation of environment manager."""
        status = "✅ Loaded" if self._loaded else "❌ Not loaded"
        configured = "✅ Configured" if self.is_configured() else "❌ Not configured"
        return f"<EnvironmentManager {status} {configured}>"


# Global instance
_env_manager: Optional[EnvironmentManager] = None

def get_env() -> EnvironmentManager:
    """
    Get the global EnvironmentManager instance.

    Returns:
        EnvironmentManager singleton
    """
    global _env_manager
    if _env_manager is None:
        _env_manager = EnvironmentManager()
    return _env_manager

def reload_env():
    """Reload environment variables from .env file."""
    global _env_manager
    if _env_manager:
        _env_manager.load(force=True)
    else:
        _env_manager = EnvironmentManager()
