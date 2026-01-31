"""
Configuration Sync Manager - Bidirectional sync between .env and Wizard keystore

Manages synchronization of user identity and system configuration between:
  - .env (Core identity - local only, never shared)
  - Wizard keystore (Extended data - sensitive integrations)

The boundary is clear:
  .env ONLY contains:
    - USER_NAME, USER_DOB, USER_ROLE, USER_PASSWORD
    - USER_LOCATION, USER_TIMEZONE
    - OS_TYPE
    - WIZARD_KEY (gateway to keystore)

All other sensitive data (API keys, OAuth, integrations) stays in Wizard keystore.

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from datetime import datetime
import uuid

from core.services.logging_service import get_logger, get_repo_root, LogTags

logger = get_logger("config-sync-manager")


class ConfigSyncManager:
    """Manages bidirectional sync between .env and Wizard profiles."""

    # Defined boundary: these fields ONLY go in .env
    ENV_ONLY_FIELDS = {
        'USER_NAME': 'user_username',
        'USER_DOB': 'user_dob',
        'USER_ROLE': 'user_role',
        'USER_PASSWORD': 'user_password',
        'USER_LOCATION': 'user_location',
        'USER_TIMEZONE': 'user_timezone',
        'OS_TYPE': 'install_os_type',
        'WIZARD_KEY': 'wizard_key',
    }

    # Reverse mapping
    FORM_TO_ENV = {v: k for k, v in ENV_ONLY_FIELDS.items()}

    # System-only fields (auto-detected, not user-editable)
    SYSTEM_ONLY_FIELDS = {
        'ENVIRONMENT',
        'LOG_LEVEL',
        'CORE_ROOT',
    }

    def __init__(self):
        """Initialize sync manager."""
        self.repo_root = get_repo_root()
        self.env_file = self.repo_root / ".env"
        self.env_file.parent.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # .env File Operations
    # ========================================================================

    def load_env_dict(self) -> Dict[str, str]:
        """Load all variables from .env file.

        Returns:
            Dictionary of all environment variables
        """
        if not self.env_file.exists():
            return {}

        env_vars = {}
        try:
            for line in self.env_file.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    env_vars[key] = value
            return env_vars
        except Exception as e:
            logger.error(f"[LOCAL] Failed to load .env: {e}")
            return {}

    def load_identity_from_env(self) -> Dict[str, str]:
        """Load ONLY identity fields from .env (the boundary).

        Returns:
            Dictionary with user_* keys
        """
        env_dict = self.load_env_dict()
        identity = {}

        for env_key, form_key in self.ENV_ONLY_FIELDS.items():
            if env_key in env_dict:
                identity[form_key] = env_dict[env_key]

        return identity

    def save_identity_to_env(self, data: Dict[str, str]) -> Tuple[bool, str]:
        """Save identity fields to .env, preserving other variables.

        Args:
            data: Dictionary with form field names (user_username, etc.)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Load existing .env
            env_dict = self.load_env_dict()

            # Update identity fields
            for form_key, env_key in self.FORM_TO_ENV.items():
                if form_key in data:
                    value = data[form_key]
                    if value:
                        env_dict[env_key] = str(value)
                    else:
                        env_dict.pop(env_key, None)

            # Ensure WIZARD_KEY exists (if not already set)
            if 'WIZARD_KEY' not in env_dict:
                env_dict['WIZARD_KEY'] = str(uuid.uuid4())
                logger.info(f"[LOCAL] Generated new WIZARD_KEY")

            # Write .env file
            self._write_env_file(env_dict)
            logger.info(f"[LOCAL] Identity saved to .env: {list(self.FORM_TO_ENV.keys())}")
            return True, "✅ Identity saved to .env"

        except Exception as e:
            logger.error(f"[LOCAL] Failed to save identity to .env: {e}")
            return False, f"❌ Failed to save: {e}"

    def _write_env_file(self, env_dict: Dict[str, str]) -> None:
        """Write environment variables to .env file, maintaining formatting.

        Args:
            env_dict: Dictionary of key-value pairs to write
        """
        # Group variables by category for readability
        lines = []
        written_keys = set()

        # System section
        system_vars = {}
        identity_vars = {}
        other_vars = {}

        for key, value in env_dict.items():
            if key in self.SYSTEM_ONLY_FIELDS:
                system_vars[key] = value
            elif key in self.ENV_ONLY_FIELDS or key == 'WIZARD_KEY':
                identity_vars[key] = value
            else:
                other_vars[key] = value

        # Write identity section (the boundary)
        if identity_vars:
            lines.append("# ============================================================================")
            lines.append("# USER IDENTITY (Essential Core settings)")
            lines.append("# ============================================================================")
            for key in ['USER_NAME', 'USER_DOB', 'USER_ROLE', 'USER_PASSWORD',
                       'USER_LOCATION', 'USER_TIMEZONE', 'OS_TYPE', 'WIZARD_KEY']:
                if key in identity_vars:
                    value = identity_vars[key]
                    # Quote strings
                    if isinstance(value, str) and not value.isdigit():
                        lines.append(f'{key}="{value}"')
                    else:
                        lines.append(f'{key}={value}')
                    written_keys.add(key)

        # Write system section
        if system_vars:
            lines.append("")
            lines.append("# ========================================================================")
            lines.append("# SYSTEM (Do not edit)")
            lines.append("# ========================================================================")
            for key, value in sorted(system_vars.items()):
                lines.append(f'{key}={value}')
                written_keys.add(key)

        # Write any other vars
        if other_vars:
            lines.append("")
            lines.append("# ============================================================================")
            lines.append("# EXTENDED CONFIGURATION (Wizard keystore)")
            lines.append("# ============================================================================")
            for key, value in sorted(other_vars.items()):
                if not key.startswith('_'):
                    lines.append(f'{key}={value}')
                    written_keys.add(key)

        # Ensure newline at end
        content = "\n".join(lines)
        if content and not content.endswith("\n"):
            content += "\n"

        self.env_file.write_text(content)

    # ========================================================================
    # Wizard Profile Operations
    # ========================================================================

    def sync_env_to_wizard(self, wizard_api_url: str = None) -> Tuple[bool, str]:
        """Sync .env identity to Wizard profiles via API.

        Args:
            wizard_api_url: Wizard API base URL (default: http://localhost:8765/api/v1)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if wizard_api_url is None:
            wizard_api_url = "http://localhost:8765/api/v1"

        try:
            import requests

            # Get admin token from file
            token_path = self.repo_root / "memory" / "private" / "wizard_admin_token.txt"
            if not token_path.exists():
                return False, "⚠️  Wizard admin token not found (Wizard not initialized?)"

            token = token_path.read_text().strip()
            if not token:
                return False, "⚠️  Wizard admin token is empty"

            # Load identity from .env
            identity = self.load_identity_from_env()
            if not identity.get('user_username'):
                return False, "⚠️  No identity configured in .env yet"

            # Prepare payload for Wizard API
            payload = {
                "answers": {
                    "user_username": identity.get('user_username'),
                    "user_dob": identity.get('user_dob'),
                    "user_role": identity.get('user_role'),
                    "user_password": identity.get('user_password', ''),
                    "user_location": identity.get('user_location'),
                    "user_timezone": identity.get('user_timezone'),
                    "install_os_type": identity.get('install_os_type'),
                }
            }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Submit to Wizard API
            response = requests.post(
                f"{wizard_api_url}/setup/story/submit",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"[WIZ] Synced .env identity to Wizard keystore")
                return True, "✅ Identity synced to Wizard"
            else:
                error = response.json().get("detail", f"HTTP {response.status_code}")
                logger.warning(f"[WIZ] Sync failed: {error}")
                return False, f"⚠️  Wizard sync failed: {error}"

        except Exception as e:
            logger.warning(f"[WIZ] Sync failed: {e}")
            return False, f"⚠️  Could not sync to Wizard: {e}"

    def sync_wizard_to_env(self, wizard_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Sync Wizard profile back to .env (pull updates).

        This is called when Wizard updates identity and we need to keep .env in sync.

        Args:
            wizard_data: Dictionary from Wizard profile (user_profile or install_profile)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Map Wizard field names to form keys
            form_data = {
                'user_username': wizard_data.get('username'),
                'user_dob': wizard_data.get('date_of_birth'),
                'user_role': wizard_data.get('role'),
                'user_password': wizard_data.get('password', ''),
                'user_location': wizard_data.get('location_name'),
                'user_timezone': wizard_data.get('timezone'),
                'install_os_type': wizard_data.get('os_type'),
            }

            # Filter out None values
            form_data = {k: v for k, v in form_data.items() if v}

            success, msg = self.save_identity_to_env(form_data)
            if success:
                logger.info(f"[WIZ] Synced Wizard updates back to .env")
            else:
                logger.warning(f"[WIZ] Failed to sync Wizard to .env: {msg}")
            return success, msg

        except Exception as e:
            logger.error(f"[WIZ] Sync from Wizard failed: {e}")
            return False, f"Failed to sync from Wizard: {e}"

    # ========================================================================
    # Validation
    # ========================================================================

    def validate_identity(self, data: Dict[str, str]) -> Tuple[bool, str]:
        """Validate identity data before saving.

        Args:
            data: Identity data to validate

        Returns:
            Tuple of (valid: bool, message: str)
        """
        # Check required fields
        required = ['user_username', 'user_dob', 'user_role', 'user_timezone']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"

        # Validate role
        if data['user_role'] not in {'admin', 'user', 'ghost'}:
            return False, f"Invalid role: {data['user_role']}"

        # Validate DOB format
        dob = data.get('user_dob', '')
        if dob and not self._is_valid_date(dob, '%Y-%m-%d'):
            return False, "DOB must be in YYYY-MM-DD format"

        # Validate timezone (basic check)
        tz = data.get('user_timezone', '')
        if tz and '/' not in tz and tz != 'UTC':
            # Simple check - real validation would use pytz
            logger.warning(f"[LOCAL] Timezone may be invalid: {tz}")

        return True, "✅ Valid identity"

    @staticmethod
    def _is_valid_date(date_str: str, fmt: str) -> bool:
        """Check if string matches date format."""
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            return False

    # ========================================================================
    # Status & Diagnostics
    # ========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get current sync status and configuration state.

        Returns:
            Dictionary with status information
        """
        env_identity = self.load_identity_from_env()
        has_identity = bool(env_identity.get('user_username'))

        return {
            "env_identity_configured": has_identity,
            "env_file_exists": self.env_file.exists(),
            "env_identity": env_identity if has_identity else None,
            "wizard_key_set": bool(env_identity.get('wizard_key')),
        }

    def print_status(self) -> None:
        """Print current configuration status."""
        status = self.get_status()

        print("\n🔄 CONFIGURATION SYNC STATUS:\n")

        if status['env_identity_configured']:
            identity = status['env_identity']
            print(f"  ✅ .env identity configured:")
            print(f"     • Username: {identity.get('user_username')}")
            print(f"     • Role: {identity.get('user_role')}")
            print(f"     • Location: {identity.get('user_location')}")
            print(f"     • Timezone: {identity.get('user_timezone')}")
        else:
            print(f"  ⚠️  No identity configured in .env")
            print(f"     Run: SETUP to configure")

        if status['wizard_key_set']:
            print(f"\n  ✅ Wizard gateway: {status['env_identity']['wizard_key'][:8]}...")
        else:
            print(f"\n  ⚠️  Wizard gateway not configured")

        print()
