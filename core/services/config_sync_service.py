"""Configuration Sync Manager - Bidirectional sync between .env and Wizard keystore

Manages synchronization of user identity and system configuration between:
  - .env (Core identity - local only, never shared)
  - Wizard keystore (Extended data - sensitive integrations)

The boundary is clear:
  .env ONLY contains:
    - USER_NAME, USER_DOB, USER_ROLE, USER_PASSWORD
    - UDOS_LOCATION, UDOS_TIMEZONE
    - OS_TYPE

All other sensitive data (API keys, OAuth, integrations) stays in Wizard keystore.

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""
from __future__ import annotations

from datetime import datetime
import json
import os
from typing import Any
from urllib.parse import urlparse
import uuid

from core.services.logging_api import get_logger, get_repo_root
from core.services.paths import get_memory_root, get_vault_md_root, get_vault_root
from core.services.rate_limit_helpers import guard_wizard_endpoint
from core.services.stdlib_http import HTTPError, http_post
from core.services.unified_config_loader import get_process_env

logger = get_logger("config-sync-manager")


class ConfigSyncManager:
    """Manages bidirectional sync between .env and Wizard profiles."""

    # Defined boundary: these fields ONLY go in .env
    ENV_ONLY_FIELDS = {
        'USER_NAME': 'user_username',
        'USER_DOB': 'user_dob',
        'USER_ROLE': 'user_role',
        'USER_PASSWORD': 'user_password',
        'UDOS_LOCATION': 'user_location',
        'UDOS_TIMEZONE': 'user_timezone',
        'OS_TYPE': 'install_os_type',
        'VAULT_ROOT': 'setup_vault_md_root',
        'WIZARD_KEY': 'wizard_key',
    }

    # Reverse mapping
    FORM_TO_ENV = {v: k for k, v in ENV_ONLY_FIELDS.items()}

    # System-only fields (auto-detected, not user-editable)
    SYSTEM_ONLY_FIELDS = {
        'ENVIRONMENT',
        'LOG_LEVEL',
        'CORE_ROOT',
        'UDOS_ROOT',
    }

    RUNTIME_KEYS = (
        "WIZARD_KEY",
        "WIZARD_ADMIN_TOKEN",
        "WIZARD_BASE_URL",
        "VIBE_PRIMARY_PROVIDER",
        "VIBE_SECONDARY_PROVIDER",
        "MISTRAL_API_KEY",
        "STAGING_MISTRAL_API_KEY",
        "USER_NAME",
        "USER_ROLE",
    )
    # Keys where host shell env should not override repo/secret/user state.
    _HOST_ENV_LAST_KEYS = {
        "USER_NAME",
        "USER_ROLE",
        "MISTRAL_API_KEY",
        "STAGING_MISTRAL_API_KEY",
    }
    _LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})

    def __init__(self):
        """Initialize sync manager."""
        self.repo_root = get_repo_root()
        self.env_file = self.repo_root / ".env"
        self.env_file.parent.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # .env File Operations
    # ========================================================================

    def load_env_dict(self) -> dict[str, str]:
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

    def load_identity_from_env(self) -> dict[str, str]:
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

    def save_identity_to_env(self, data: dict[str, str]) -> tuple[bool, str]:
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
                        # Normalize username to lowercase for case-insensitive handling
                        if form_key == 'user_username':
                            value = value.lower()
                        env_dict[env_key] = str(value)
                    else:
                        env_dict.pop(env_key, None)

            # Ensure WIZARD_KEY exists (if not already set)
            if not env_dict.get('WIZARD_KEY'):
                env_dict['WIZARD_KEY'] = str(uuid.uuid4())
                logger.info("[LOCAL] Generated new WIZARD_KEY")

            # Ensure UDOS_ROOT exists (absolute path to repo)
            if 'UDOS_ROOT' not in env_dict:
                env_dict['UDOS_ROOT'] = str(self.repo_root.resolve())
                logger.info(f"[LOCAL] Set UDOS_ROOT={env_dict['UDOS_ROOT']}")

            if 'UDOS_MEMORY_ROOT' not in env_dict:
                env_dict['UDOS_MEMORY_ROOT'] = str(get_memory_root())
                logger.info(f"[LOCAL] Set UDOS_MEMORY_ROOT={env_dict['UDOS_MEMORY_ROOT']}")

            if 'VAULT_ROOT' not in env_dict:
                env_dict['VAULT_ROOT'] = str(get_vault_root())
                logger.info(f"[LOCAL] Set VAULT_ROOT={env_dict['VAULT_ROOT']}")
            if 'VAULT_MD_ROOT' not in env_dict:
                env_dict['VAULT_MD_ROOT'] = str(get_vault_md_root())
                logger.info(f"[LOCAL] Set VAULT_MD_ROOT={env_dict['VAULT_MD_ROOT']}")

            # Write .env file
            self._write_env_file(env_dict)
            logger.info(f"[LOCAL] Identity saved to .env: {list(self.FORM_TO_ENV.keys())}")
            return True, "✅ Identity saved to .env"

        except Exception as e:
            logger.error(f"[LOCAL] Failed to save identity to .env: {e}")
            return False, f"❌ Failed to save: {e}"

    def update_env_vars(self, updates: dict[str, str | None]) -> tuple[bool, str]:
        """Update arbitrary .env variables, preserving existing content."""
        try:
            env_dict = self.load_env_dict()

            for key, value in updates.items():
                if value is None:
                    env_dict.pop(key, None)
                else:
                    env_dict[key] = str(value)

            if not env_dict.get('WIZARD_KEY'):
                env_dict['WIZARD_KEY'] = str(uuid.uuid4())
                logger.info("[LOCAL] Generated new WIZARD_KEY")

            if 'UDOS_ROOT' not in env_dict:
                env_dict['UDOS_ROOT'] = str(self.repo_root.resolve())
                logger.info(f"[LOCAL] Set UDOS_ROOT={env_dict['UDOS_ROOT']}")

            if 'UDOS_MEMORY_ROOT' not in env_dict:
                env_dict['UDOS_MEMORY_ROOT'] = str(get_memory_root())
                logger.info(f"[LOCAL] Set UDOS_MEMORY_ROOT={env_dict['UDOS_MEMORY_ROOT']}")

            if 'VAULT_ROOT' not in env_dict:
                env_dict['VAULT_ROOT'] = str(get_vault_root())
                logger.info(f"[LOCAL] Set VAULT_ROOT={env_dict['VAULT_ROOT']}")
            if 'VAULT_MD_ROOT' not in env_dict:
                env_dict['VAULT_MD_ROOT'] = str(get_vault_md_root())
                logger.info(f"[LOCAL] Set VAULT_MD_ROOT={env_dict['VAULT_MD_ROOT']}")

            self._write_env_file(env_dict)
            return True, "✅ Updated .env"
        except Exception as e:
            logger.error(f"[LOCAL] Failed to update .env: {e}")
            return False, f"❌ Failed to update .env: {e}"

    def _write_env_file(self, env_dict: dict[str, str]) -> None:
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
            elif key in self.ENV_ONLY_FIELDS:
                identity_vars[key] = value
            else:
                other_vars[key] = value

        # Write identity section (the boundary)
        if identity_vars:
            lines.append("# ============================================================================")
            lines.append("# USER IDENTITY (Essential Core settings)")
            lines.append("# ============================================================================")
            for key in ['USER_NAME', 'USER_DOB', 'USER_ROLE', 'USER_PASSWORD',
                       'UDOS_LOCATION', 'UDOS_TIMEZONE', 'OS_TYPE',
                       'WIZARD_KEY']:
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

    def _load_user_state(self) -> dict[str, str]:
        """Load current username/role from memory user state files."""
        users_file = self.repo_root / "memory" / "bank" / "private" / "users.json"
        current_file = self.repo_root / "memory" / "bank" / "private" / "current_user.txt"
        try:
            if not users_file.exists() or not current_file.exists():
                return {}
            current = current_file.read_text().strip().lower()
            if not current:
                return {}
            payload = json.loads(users_file.read_text())
            user = payload.get(current) or {}
            role = str(user.get("role") or "").strip().lower()
            return {
                "USER_NAME": current,
                "USER_ROLE": role,
            }
        except Exception:
            return {}

    def _secret_store_env_lookup(self, key: str) -> str | None:
        """Resolve secrets from Wizard secret store for env-style keys."""
        try:
            from wizard.security.key_store import get_wizard_key

            value = get_wizard_key(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            return None
        except Exception:
            return None

    def resolve_runtime_value(self, key: str) -> str:
        """Resolve a runtime value with explicit precedence.

        Precedence:
          - Default keys:
              1) exported shell env
              2) repo .env
              3) wizard secret store (for known secret keys)
              4) memory user state (USER_NAME/USER_ROLE)
          - Host-env-last keys (identity/secrets):
              1) repo .env
              2) wizard secret store
              3) memory user state
              4) exported shell env
        """
        host_env_value = str(get_process_env(key, "")).strip()
        env_dict = self.load_env_dict()
        file_value = str(env_dict.get(key, "")).strip()
        secret_value = self._secret_store_env_lookup(key)
        user_state = self._load_user_state()
        user_value = str(user_state.get(key, "")).strip()

        if key in self._HOST_ENV_LAST_KEYS:
            return file_value or secret_value or user_value or host_env_value

        return host_env_value or file_value or secret_value or user_value

    def hydrate_runtime_env(self, keys: list[str] | None = None) -> dict[str, str]:
        """Populate os.environ from canonical config sources for runtime stability."""
        resolved: dict[str, str] = {}
        for key in (keys or list(self.RUNTIME_KEYS)):
            value = self.resolve_runtime_value(key)
            if value:
                os.environ[key] = value
                resolved[key] = value

        # Canonical aliases
        if resolved.get("USER_NAME") and not get_process_env("USER_USERNAME"):
            os.environ["USER_USERNAME"] = resolved["USER_NAME"]
            resolved["USER_USERNAME"] = resolved["USER_NAME"]
        if resolved.get("USER_ROLE") and not get_process_env("UDOS_USER_ROLE"):
            os.environ["UDOS_USER_ROLE"] = resolved["USER_ROLE"]
            resolved["UDOS_USER_ROLE"] = resolved["USER_ROLE"]

        return resolved

    # ========================================================================
    # Wizard Profile Operations
    # ========================================================================

    def sync_env_to_wizard(self, wizard_api_url: str = None) -> tuple[bool, str]:
        """Sync .env identity to Wizard profiles via API.

        Args:
            wizard_api_url: Wizard API base URL (default: http://localhost:8765/api/v1)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if wizard_api_url is None:
            wizard_api_url = "http://localhost:8765/api/v1"
        wizard_api_url = wizard_api_url.rstrip("/")
        parsed = urlparse(wizard_api_url)
        host = (parsed.hostname or "").strip().lower()
        if host not in self._LOOPBACK_HOSTS:
            logger.warning("[WIZ] Blocked non-loopback sync target: %s", wizard_api_url)
            return False, "⚠️  Boundary policy blocks non-loopback Wizard sync target"

        try:
            # Get admin token from file
            token_path = self.repo_root / "memory" / "bank" / "private" / "wizard_admin_token.txt"
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
            guard = guard_wizard_endpoint("/api/setup/story/submit")
            if guard:
                return False, guard.get("message", "⚠️ Wizard sync rate limited")
            response = http_post(
                f"{wizard_api_url}/setup/story/submit",
                headers=headers,
                json_data=payload,
                timeout=10
            )

            if response.get("status_code") == 200:
                logger.info("[WIZ] Synced .env identity to Wizard keystore")
                return True, "✅ Identity synced to Wizard"
            else:
                payload = response.get("json")
                if isinstance(payload, dict):
                    error = payload.get("detail", f"HTTP {response.get('status_code')}")
                else:
                    error = f"HTTP {response.get('status_code')}"
                logger.warning(f"[WIZ] Sync failed: {error}")
                return False, f"⚠️  Wizard sync failed: {error}"

        except HTTPError as e:
            logger.warning(f"[WIZ] Sync failed: {e}")
            return False, f"⚠️  Could not sync to Wizard: {e}"
        except Exception as e:
            logger.warning(f"[WIZ] Sync failed: {e}")
            return False, f"⚠️  Could not sync to Wizard: {e}"

    def sync_wizard_to_env(self, wizard_data: dict[str, Any]) -> tuple[bool, str]:
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
                logger.info("[WIZ] Synced Wizard updates back to .env")
            else:
                logger.warning(f"[WIZ] Failed to sync Wizard to .env: {msg}")
            return success, msg

        except Exception as e:
            logger.error(f"[WIZ] Sync from Wizard failed: {e}")
            return False, f"Failed to sync from Wizard: {e}"

    # ========================================================================
    # Validation
    # ========================================================================

    def validate_identity(self, data: dict[str, str]) -> tuple[bool, str]:
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
        data['user_role'] = str(data['user_role']).lower()
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

    def get_status(self) -> dict[str, Any]:
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
            print("  ✅ .env identity configured:")
            print(f"     • Username: {identity.get('user_username')}")
            print(f"     • Role: {identity.get('user_role')}")
            print(f"     • Location: {identity.get('user_location')}")
            print(f"     • Timezone: {identity.get('user_timezone')}")
        else:
            print("  ⚠️  No identity configured in .env")
            print("     Run: SETUP to configure")

        if status['wizard_key_set']:
            print(f"\n  ✅ Wizard gateway: {status['env_identity']['wizard_key'][:8]}...")
        else:
            print("\n  ⚠️  Wizard gateway not configured")

        print()
