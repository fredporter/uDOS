"""
uDOS Configuration Manager
Handles .env file configuration via CLI only
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import re

class ConfigManager:
    """Manage uDOS .env configuration securely"""

    ALLOWED_KEYS = {
        'GEMINI_API_KEY': 'Gemini AI API Key',
        'UDOS_USERNAME': 'Username',
        'UDOS_INSTALLATION_ID': 'Installation ID',
        'DEFAULT_WORKSPACE': 'Default workspace',
        'AUTO_START_WEB': 'Auto-start web dashboard (true/false)',
        'THEME': 'Color theme (dark/light)',
    }

    def __init__(self, env_path: Optional[Path] = None):
        """Initialize configuration manager"""
        self.env_path = env_path or Path(__file__).parent.parent / '.env'
        self._ensure_env_exists()

    def _ensure_env_exists(self) -> None:
        """Ensure .env file exists"""
        if not self.env_path.exists():
            # Create default .env
            self.env_path.write_text("""# uDOS Environment Configuration
# Edit these values using CLI commands only: udos config set <key> <value>

# Gemini AI API Key
GEMINI_API_KEY=''

# User Information
UDOS_USERNAME='user'

# Unique Installation ID (auto-generated)
UDOS_INSTALLATION_ID='default'

# Default Workspace
DEFAULT_WORKSPACE='sandbox'

# Auto-start Web Dashboard
AUTO_START_WEB='false'

# Color Theme
THEME='dark'
""")

    def get(self, key: str) -> Optional[str]:
        """Get configuration value"""
        if key not in self.ALLOWED_KEYS:
            raise ValueError(f"Unknown configuration key: {key}\nAllowed: {', '.join(self.ALLOWED_KEYS.keys())}")

        env_vars = self._load_env()
        return env_vars.get(key)

    def set(self, key: str, value: str) -> None:
        """Set configuration value"""
        if key not in self.ALLOWED_KEYS:
            raise ValueError(f"Unknown configuration key: {key}\nAllowed: {', '.join(self.ALLOWED_KEYS.keys())}")

        # Read current .env
        lines = []
        found = False

        if self.env_path.exists():
            with open(self.env_path, 'r') as f:
                lines = f.readlines()

        # Update or add key
        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key}="):
                # Update existing key
                new_lines.append(f"{key}='{value}'\n")
                found = True
            else:
                new_lines.append(line)

        # Add if not found
        if not found:
            new_lines.append(f"\n# {self.ALLOWED_KEYS[key]}\n")
            new_lines.append(f"{key}='{value}'\n")

        # Write back
        with open(self.env_path, 'w') as f:
            f.writelines(new_lines)

    def list_all(self) -> Dict[str, str]:
        """List all configuration values"""
        env_vars = self._load_env()
        return {
            key: env_vars.get(key, '<not set>')
            for key in self.ALLOWED_KEYS.keys()
        }

    def _load_env(self) -> Dict[str, str]:
        """Load all environment variables from .env"""
        env_vars = {}

        if not self.env_path.exists():
            return env_vars

        with open(self.env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes
                        value = value.strip().strip('"\'')
                        env_vars[key.strip()] = value

        return env_vars

    def validate(self) -> Dict[str, bool]:
        """Validate configuration"""
        env_vars = self._load_env()
        validation = {}

        # Check API key
        api_key = env_vars.get('GEMINI_API_KEY', '')
        validation['GEMINI_API_KEY'] = bool(api_key and len(api_key) > 10)

        # Check username
        username = env_vars.get('UDOS_USERNAME', '')
        validation['UDOS_USERNAME'] = bool(username and len(username) > 0)

        # Check installation ID
        install_id = env_vars.get('UDOS_INSTALLATION_ID', '')
        validation['UDOS_INSTALLATION_ID'] = bool(install_id and len(install_id) > 0)

        return validation


# CLI interface
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='uDOS Configuration Manager')
    parser.add_argument('action', choices=['get', 'set', 'list', 'validate'],
                       help='Configuration action')
    parser.add_argument('key', nargs='?', help='Configuration key')
    parser.add_argument('value', nargs='?', help='Configuration value (for set)')

    args = parser.parse_args()

    try:
        config = ConfigManager()

        if args.action == 'list':
            print("\n🔮 uDOS Configuration:\n")
            for key, value in config.list_all().items():
                # Hide API key
                display_value = value
                if key == 'GEMINI_API_KEY' and value != '<not set>':
                    display_value = value[:10] + '...' + value[-4:]

                desc = ConfigManager.ALLOWED_KEYS[key]
                print(f"  {key:25} = {display_value:30} # {desc}")
            print()

        elif args.action == 'validate':
            print("\n🔍 Configuration Validation:\n")
            validation = config.validate()
            all_valid = True

            for key, is_valid in validation.items():
                status = "✓" if is_valid else "✗"
                desc = ConfigManager.ALLOWED_KEYS[key]
                print(f"  {status} {key:25} # {desc}")
                all_valid = all_valid and is_valid

            print()
            if all_valid:
                print("✓ All configuration valid\n")
            else:
                print("⚠ Some configuration missing or invalid\n")
                sys.exit(1)

        elif args.action == 'get':
            if not args.key:
                print("Error: key required for 'get'", file=sys.stderr)
                sys.exit(1)

            value = config.get(args.key)
            if value:
                # Hide API key
                if args.key == 'GEMINI_API_KEY':
                    print(f"{value[:10]}...{value[-4:]}")
                else:
                    print(value)
            else:
                print(f"<not set>")

        elif args.action == 'set':
            if not args.key or not args.value:
                print("Error: key and value required for 'set'", file=sys.stderr)
                sys.exit(1)

            config.set(args.key, args.value)
            print(f"✓ Set {args.key} = {args.value}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
