"""
Helper utilities for SETUP command handling.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import os
import uuid


def detect_udos_root(reference_file: Optional[Path] = None, logger=None) -> Path:
    """
    Auto-detect uDOS repository root for UDOS_ROOT .env variable.
    """
    env_root = os.getenv("UDOS_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser()
        marker = env_path / "uDOS.py"
        if marker.exists():
            if logger:
                logger.info(f"[LOCAL] UDOS_ROOT detected from environment: {env_path}")
            return env_path
        if logger:
            logger.warning(
                f"[LOCAL] UDOS_ROOT env var set but uDOS.py not found at {env_path}"
            )

    try:
        current_file = (reference_file or Path(__file__)).resolve()
        candidate = current_file.parent.parent.parent
        marker = candidate / "uDOS.py"
        if marker.exists():
            if logger:
                logger.info(f"[LOCAL] UDOS_ROOT auto-detected: {candidate}")
            return candidate
    except Exception as exc:
        if logger:
            logger.warning(f"[LOCAL] Relative path detection failed: {exc}")

    raise RuntimeError(
        "Cannot auto-detect uDOS root. Please:\n"
        "1. Ensure uDOS.py exists at repository root\n"
        "2. Or set UDOS_ROOT environment variable\n"
        "3. Or run setup from repository root directory"
    )


def initialize_env_from_example(env_file: Path, logger=None) -> None:
    """Initialize .env from .env.example if it doesn't exist."""
    if env_file.exists():
        return
    example_file = env_file.parent / ".env.example"
    if not example_file.exists():
        return
    try:
        env_file.write_text(example_file.read_text())
        if logger:
            logger.info("[LOCAL] Initialized .env from .env.example")
    except Exception as exc:
        if logger:
            logger.warning(f"[LOCAL] Could not initialize .env: {exc}")


def load_setup_env_vars(env_file: Path) -> Dict:
    """Load setup-related variables from .env file."""
    try:
        if not env_file.exists():
            return {}

        env_vars = {}
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                if key.startswith("USER_") or key in {
                    "OS_TYPE",
                    "UDOS_LOCATION",
                    "UDOS_TIMEZONE",
                    "WIZARD_KEY",
                }:
                    env_vars[key] = value
        return env_vars
    except Exception:
        return {}


def save_setup_to_env(env_file: Path, data: Dict, logger=None) -> bool:
    """Save setup data to .env file, preserving non-setup vars."""
    try:
        from core.services.uid_generator import generate_uid, scramble_uid

        try:
            udos_root = detect_udos_root(reference_file=Path(__file__), logger=logger)
            data["udos_root"] = str(udos_root)
        except RuntimeError as exc:
            if logger:
                logger.warning(f"[LOCAL] UDOS_ROOT detection failed: {exc}")

        key_mapping = {
            "user_username": "USER_NAME",
            "user_dob": "USER_DOB",
            "user_role": "USER_ROLE",
            "user_location": "UDOS_LOCATION",
            "user_timezone": "UDOS_TIMEZONE",
            "install_os_type": "OS_TYPE",
            "user_password": "USER_PASSWORD",
            "udos_root": "UDOS_ROOT",
        }

        existing = {}
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.split("=", 1)
                    existing[key.strip()] = value.strip()

        for form_key, env_key in key_mapping.items():
            if form_key in data:
                value = data[form_key]
                if value:
                    existing[env_key] = f'"{value}"' if isinstance(value, str) else str(value)
                else:
                    existing.pop(env_key, None)

        if "USER_ID" not in existing and "user_dob" in data and "user_timezone" in data:
            timestamp = datetime.now()
            if data.get("current_date") and data.get("current_time"):
                try:
                    timestamp = datetime.strptime(
                        f"{data['current_date']} {data['current_time']}",
                        "%Y-%m-%d %H:%M:%S",
                    )
                except ValueError:
                    pass
            uid = generate_uid(
                dob=data["user_dob"],
                timezone=data["user_timezone"],
                timestamp=timestamp,
            )
            existing["USER_ID"] = f'"{scramble_uid(uid)}"'

        if "UDOS_ROOT" not in existing:
            repo_root = Path(__file__).parent.parent.parent.resolve()
            existing["UDOS_ROOT"] = f'"{str(repo_root)}"'

        wizard_key = existing.get("WIZARD_KEY", "").strip().strip('"\'')
        if not wizard_key:
            existing["WIZARD_KEY"] = f'"{str(uuid.uuid4())}"'

        env_file.write_text("\n".join(f"{k}={v}" for k, v in sorted(existing.items())) + "\n")
        return True
    except Exception as exc:
        if logger:
            logger.error(f"Failed to save to .env: {exc}")
        return False


def clear_setup_env(env_file: Path) -> bool:
    """Clear setup keys from .env while preserving others."""
    env_vars = {
        "USER_NAME",
        "USER_DOB",
        "USER_ROLE",
        "UDOS_LOCATION",
        "UDOS_TIMEZONE",
        "OS_TYPE",
        "USER_PASSWORD",
        "USER_ID",
    }
    lines = []
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            key = line.split("=")[0].strip() if "=" in line else None
            if key not in env_vars:
                lines.append(line)
    env_file.write_text("\n".join(lines))
    return True


def setup_help_text() -> str:
    return """
╔═════════════════════════════════════════════════════════════╗
║              SETUP - Local Offline Configuration            ║
╚═════════════════════════════════════════════════════════════╝

SETUP configures your user identity locally in .env.
Works completely offline without needing Wizard Server.

When Wizard Server is installed, it imports this data and extends it
with sensitive integrations (credentials, API keys, webhooks, etc.)
stored in the Wizard keystore.

USAGE:
  SETUP              Run setup story (interactive questions)
  SETUP <provider>   Setup a provider (github, ollama, mistral, etc.)
  SETUP vibe         Install Vibe CLI + Ollama + Mistral models
  INSTALL vibe       Alias for SETUP vibe
  SETUP --profile    Show your current setup
  SETUP --edit       Edit setup manually
  SETUP --clear      Clear all setup data
  SETUP --help       Show this help

PROVIDERS:
  SETUP github       Configure GitHub authentication
  SETUP ollama       Setup local Ollama AI model
  SETUP mistral      Configure Mistral AI provider
  SETUP openrouter   Configure OpenRouter gateway
  SETUP vibe         Install Vibe CLI + Ollama + Mistral local models

LOCAL SETTINGS (.env):
    USER_NAME          Username
  USER_DOB           Birth date (YYYY-MM-DD)
  USER_ROLE          ghost | user | admin
  USER_PASSWORD      Optional password (user/admin - can be blank)
  UDOS_LOCATION      City or grid coordinates
  UDOS_TIMEZONE      Timezone identifier
  OS_TYPE            alpine | ubuntu | mac | windows

EXTENDED SETTINGS (Wizard Keystore - installed later):
    API Keys:          GitHub, OpenAI, Anthropic, etc.
  OAuth Tokens:      Calendar, Google Drive, etc.
  Cloud Services:    AWS, GCP, Azure credentials
  Webhooks:          Custom webhooks and secrets
  AI Routing:        Provider credentials and endpoints
  Activations:       Integration activation settings

EXAMPLES:
  SETUP                     # Start interactive setup
  SETUP github              # Setup GitHub authentication
  SETUP ollama              # Setup local Ollama
  SETUP vibe                # Install Vibe CLI + Ollama + Mistral models
  SETUP --profile           # View current settings
  SETUP --clear && SETUP    # Reset and reconfigure
  nano .env                 # Manual editing
""".strip()

