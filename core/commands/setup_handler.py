"""
SETUP command handler - Local offline setup for Core.

Stores user identity in .env (local, never shared):
    - Username, DOB, Role, Location, Timezone, OS-Type
  - Optional password (User/Admin roles only - can be blank)
  - Wizard Key (gateway to keystore for sensitive extensions)

All other sensitive data goes in Wizard keystore:
    - API keys (GitHub, OpenAI, etc.)
  - OAuth tokens (Gmail, Calendar, etc.)
  - Cloud credentials and webhooks
  - Integration activation settings

When Wizard Server is installed, it imports these local settings.
"""

from pathlib import Path
from typing import Dict, List
import os
from datetime import datetime

from core.commands.base import BaseCommandHandler
from core.services.logging_service import get_repo_root, get_logger

logger = get_logger('setup-handler')


def _detect_udos_root() -> Path:
    """
    Auto-detect uDOS repository root for UDOS_ROOT .env variable.

    Tries in order:
    1. UDOS_ROOT environment variable (container override)
    2. Relative path from this file (local development)
    3. Raise error if not found

    Returns:
        Path: Absolute path to uDOS repository root

    Raises:
        RuntimeError: If root cannot be detected
    """
    # Try environment first (containers will set this)
    env_root = os.getenv("UDOS_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser()
        marker = env_path / "uDOS.py"
        if marker.exists():
            logger.info(f"[LOCAL] UDOS_ROOT detected from environment: {env_path}")
            return env_path
        else:
            logger.warning(f"[LOCAL] UDOS_ROOT env var set but uDOS.py not found at {env_path}")

    # Fall back to relative path discovery
    try:
        current_file = Path(__file__).resolve()
        # setup_handler.py → core/commands → core → root
        candidate = current_file.parent.parent.parent
        marker = candidate / "uDOS.py"

        if marker.exists():
            logger.info(f"[LOCAL] UDOS_ROOT auto-detected: {candidate}")
            return candidate
    except Exception as e:
        logger.warning(f"[LOCAL] Relative path detection failed: {e}")

    raise RuntimeError(
        "Cannot auto-detect uDOS root. Please:\n"
        "1. Ensure uDOS.py exists at repository root\n"
        "2. Or set UDOS_ROOT environment variable\n"
        "3. Or run setup from repository root directory"
    )


class SetupHandler(BaseCommandHandler):
    """Handler for SETUP command - local offline setup via .env."""

    def __init__(self):
        """Initialize paths."""
        super().__init__()
        self.env_file = get_repo_root() / ".env"
        self.env_file.parent.mkdir(parents=True, exist_ok=True)

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        SETUP command - manage local offline user setup in .env, and provider configuration.

        Usage:
            SETUP              Run the setup story (configure local identity)
            SETUP webhook      Interactive GitHub & HubSpot webhook setup (vibe-cli style)
            SETUP <provider>   Setup a specific provider (github, ollama, mistral, etc.)
            SETUP --profile    Show your current setup profile
            SETUP --edit       Edit setup values
            SETUP --clear      Clear setup data (start over)
            SETUP --help       Show help

        Local data stored in .env:
            USER_NAME          Username
            USER_DOB           Date of birth (YYYY-MM-DD)
            USER_ROLE          admin | user | ghost
            USER_PASSWORD      Optional password (user/admin only, can be blank)
            USER_LOCATION      City / grid location
            USER_TIMEZONE      Timezone (e.g. America/Los_Angeles)
            OS_TYPE            alpine | ubuntu | mac | windows
            WIZARD_KEY         Gateway to Wizard keystore (auto-generated)

        Webhook Setup (interactive, vibe-cli style):
            SETUP webhook           Full setup (GitHub + HubSpot)
            SETUP webhook github    GitHub webhooks only
            SETUP webhook hubspot   HubSpot CRM only

        Provider Setup (delegates to Wizard):
            Supported: github, ollama, mistral, openrouter, hubspot, gmail

        Extended data in Wizard keystore (when installed):
            - API keys, OAuth tokens, credentials
            - Integrations (GitHub, Gmail, etc.)
            - Cloud routing, webhooks, activation settings
        """
        if not params:
            return self._run_story()

        action = params[0].lower()

        # Check if this is a webhook setup request (new!)
        if action == "webhook":
            from core.commands.webhook_setup_handler import WebhookSetupHandler
            handler = WebhookSetupHandler()
            return handler.handle("SETUP", params, grid, parser)

        # Check if this is a provider setup request
        provider_names = {"github", "ollama", "mistral", "openrouter", "hubspot", "gmail"}
        if action in provider_names:
            return self._setup_provider(action)

        if action in {"--story", "--run", "--wizard-setup"}:
            return self._run_story()
        elif action in {"--profile", "--view", "--show"}:
            return self._show_profile()
        elif action == "--edit":
            return self._edit_interactively()
        elif action == "--clear":
            return self._clear_setup()
        elif action == "--help":
            return self._show_help()
        else:
            return {
                "status": "error",
                "message": f"Unknown option: {action}",
                "help": "Usage: SETUP [webhook|provider|--profile|--edit|--clear|--help]\n       Webhook: SETUP webhook [github|hubspot]\n       Providers: github, ollama, mistral, openrouter, hubspot, gmail"
            }


    def _show_profile(self) -> Dict:
        """Display the current setup profile from .env."""
        try:
            from core.services.uid_generator import descramble_uid

            env_data = self._load_env_vars()

            if not env_data.get('USER_NAME'):
                return {
                    "status": "warning",
                    "output": """
╔═════════════════════════════════════════════════════════════╗
║  ⚠️  No Setup Profile Found                                 ║
╚═════════════════════════════════════════════════════════════╝

You haven't configured your identity yet. To get started:

  SETUP

This will run the setup story and ask you for:
    • Your username and date of birth
  • Your role (ghost/user/admin)
  • Your timezone and location
  • OS type and optional password (user/admin only)

Your settings are stored locally in: .env

When Wizard Server is installed, it imports this data.
"""
                }

            lines = ["\n🧙 YOUR LOCAL SETUP PROFILE\n", "=" * 60]

            # User Identity
            lines.append("\n📋 User Identity")
            lines.append("-" * 60)
            lines.append(f"  • Username:     {env_data.get('USER_NAME', 'Not set')}")
            lines.append(f"  • DOB:          {env_data.get('USER_DOB', 'Not set')}")
            lines.append(f"  • Role:         {env_data.get('USER_ROLE', 'ghost')}")
            has_password = "yes" if env_data.get('USER_PASSWORD') else "no (blank)"
            lines.append(f"  • Password:     {has_password}")

            # User ID (descrambled for viewing)
            if env_data.get('USER_ID'):
                try:
                    uid_plain = descramble_uid(env_data['USER_ID'])
                    lines.append(f"  • User ID:      {uid_plain}")
                except Exception:
                    lines.append(f"  • User ID:      {env_data['USER_ID'][:20]}... (scrambled)")

            # Location & Time
            lines.append("\n📍 Location & Time")
            lines.append("-" * 60)
            lines.append(f"  • Location:     {env_data.get('USER_LOCATION', 'Not set')}")
            lines.append(f"  • Timezone:     {env_data.get('USER_TIMEZONE', 'Not set')}")

            # Installation
            lines.append("\n⚙️  Installation")
            lines.append("-" * 60)
            lines.append(f"  • OS Type:      {env_data.get('OS_TYPE', 'Not set')}")

            # Security
            lines.append("\n🔐 Security")
            lines.append("-" * 60)
            wizard_key = env_data.get('WIZARD_KEY', 'Not set')
            if wizard_key and wizard_key != 'Not set':
                wizard_key = wizard_key[:8] + "..." if len(wizard_key) > 8 else "***"
            lines.append(f"  • Wizard Key:   {wizard_key}")
            lines.append("    (Gateway to Wizard keystore)")

            lines.append("\n" + "=" * 60)
            lines.append("Data stored in: .env (local, never shared)")
            lines.append("Extended data stored in: Wizard keystore (when installed)")
            lines.append("\nTo manage extended settings:")
            lines.append("  • Install Wizard Server (see wizard/README.md)")
            lines.append("  • Access: http://localhost:8765/dashboard")

            return {
                "status": "success",
                "output": "\n".join(lines)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load profile: {e}"
            }

    def _run_story(self) -> Dict:
        """Launch the setup story to configure user identity in .env."""
        try:
            # Initialize .env from .example if it doesn't exist
            self._initialize_env_from_example()
            from core.commands.story_handler import StoryHandler

            # Run the tui-setup story (minimal, focused setup)
            result = StoryHandler().handle("STORY", ["tui-setup"])

            # If story was successful and returned form data, save to .env
            if result.get("status") == "success" and "form_data" in result:
                form_data = result["form_data"]
                form_data = self._apply_system_datetime(form_data)
                self._save_to_env(form_data)
                return {
                    "status": "success",
                    "output": "✅ Setup complete! Your profile has been saved to .env\n\n"
                              "Run 'SETUP --profile' to view your settings.\n\n"
                              f"{self._seed_confirmation()}"
                }

            return result

        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to start setup story: {exc}",
                "help": "Ensure core/framework/seed/bank/system/tui-setup-story.md exists"
            }

    def _apply_system_datetime(self, form_data: Dict) -> Dict:
        """Apply system datetime approval or collect overrides when needed."""
        approval = form_data.get("system_datetime_approve")
        manual_override_keys = {"user_timezone", "current_date", "current_time"}
        has_manual_overrides = manual_override_keys.issubset(form_data.keys())
        if isinstance(approval, dict):
            if approval.get("approved"):
                form_data["user_timezone"] = approval.get("timezone")
                form_data["current_date"] = approval.get("date")
                form_data["current_time"] = approval.get("time")
                return form_data

            # User declined: collect overrides
            if has_manual_overrides:
                return form_data
            overrides = self._run_datetime_override_form(approval)
            if overrides.get("status") == "success":
                form_data.update(overrides.get("data", {}))
        if "user_timezone" not in form_data:
            form_data["user_timezone"] = self._get_system_timezone()
        return form_data

    def _get_system_timezone(self) -> str:
        now = datetime.now().astimezone()
        tzinfo = now.tzinfo
        if hasattr(tzinfo, "key"):
            return str(tzinfo.key)
        return str(tzinfo) or "UTC"

    def _run_datetime_override_form(self, approval: Dict) -> Dict:
        """Run a short override form for date/time/timezone."""
        try:
            from core.tui.story_form_handler import get_form_handler
            handler = get_form_handler()
            form_spec = {
                "title": "Adjust Local Date/Time",
                "description": "Edit local date, time, and timezone if auto-detected values are incorrect.",
                "fields": [
                    {
                        "name": "user_timezone",
                        "label": "Timezone",
                        "type": "select",
                        "required": True,
                        "options": [
                            "UTC",
                            "America/New_York",
                            "America/Los_Angeles",
                            "America/Chicago",
                            "Europe/London",
                            "Europe/Paris",
                            "Asia/Tokyo",
                            "Australia/Sydney",
                        ],
                        "default": approval.get("timezone") or "UTC",
                    },
                    {
                        "name": "current_date",
                        "label": "Current Date",
                        "type": "date",
                        "required": True,
                        "default": approval.get("date"),
                    },
                    {
                        "name": "current_time",
                        "label": "Current Time",
                        "type": "time",
                        "required": True,
                        "default": approval.get("time"),
                    },
                ],
            }
            return handler.process_story_form(form_spec)
        except Exception as e:
            return {"status": "error", "message": f"Override form failed: {e}"}

    def _seed_confirmation(self) -> str:
        """Confirm local memory/bank and seed structure after setup."""
        repo_root = get_repo_root()
        memory_bank = repo_root / "memory" / "bank"
        seed_dir = repo_root / "core" / "framework" / "seed"
        locations_seed = seed_dir / "locations-seed.json"

        lines = [
            "LOCAL SEED CONFIRMATION",
            "-" * 60,
            f"  • memory/bank: {'✅' if memory_bank.exists() else '❌'}",
            f"  • core/framework/seed: {'✅' if seed_dir.exists() else '❌'}",
            f"  • seed file (locations): {'✅' if locations_seed.exists() else '❌'}",
        ]
        return "\n".join(lines)

    def _edit_interactively(self) -> Dict:
        """Edit setup in .env file."""
        return {
            "status": "info",
            "output": """
To configure your setup interactively, run:

  SETUP

Or edit .env directly:

  nano .env

Key fields to edit:
    USER_NAME              Username
  USER_DOB               YYYY-MM-DD
  USER_ROLE              ghost | user | admin
  USER_PASSWORD          Optional (can be blank)
  USER_LOCATION          City / grid location
  USER_TIMEZONE          America/Los_Angeles, etc.
  OS_TYPE                alpine | ubuntu | mac | windows
"""
        }

    def _clear_setup(self) -> Dict:
        """Clear setup data from .env."""
        try:
            env_vars = [
                'USER_NAME', 'USER_DOB', 'USER_ROLE',
                'USER_LOCATION', 'USER_TIMEZONE', 'OS_TYPE',
                'USER_PASSWORD', 'USER_ID'
            ]

            # Remove these variables from .env while keeping others
            lines = []
            if self.env_file.exists():
                for line in self.env_file.read_text().splitlines():
                    key = line.split('=')[0].strip() if '=' in line else None
                    if key not in env_vars:
                        lines.append(line)

            self.env_file.write_text('\n'.join(lines))

            return {
                "status": "success",
                "output": "✅ Setup data cleared from .env. Run 'SETUP' to configure again."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to clear setup: {e}"
            }

    def _show_help(self) -> Dict:
        """Show help for SETUP command."""
        return {
            "status": "success",
            "output": """
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
  SETUP --profile    Show your current setup
  SETUP --edit       Edit setup manually
  SETUP --clear      Clear all setup data
  SETUP --help       Show this help

PROVIDERS:
  SETUP github       Configure GitHub authentication
  SETUP ollama       Setup local Ollama AI model
  SETUP mistral      Configure Mistral AI provider
  SETUP openrouter   Configure OpenRouter gateway
  SETUP hubspot      Configure HubSpot CRM
  SETUP gmail        Setup Gmail OAuth

LOCAL SETTINGS (.env):
    USER_NAME          Username
  USER_DOB           Birth date (YYYY-MM-DD)
  USER_ROLE          ghost | user | admin
  USER_PASSWORD      Optional password (user/admin - can be blank)
  USER_LOCATION      City or grid coordinates
  USER_TIMEZONE      Timezone identifier
  OS_TYPE            alpine | ubuntu | mac | windows
  WIZARD_KEY         Gateway to Wizard keystore

EXTENDED SETTINGS (Wizard Keystore - installed later):
    API Keys:          GitHub, OpenAI, Anthropic, etc.
  OAuth Tokens:      Gmail, Calendar, Google Drive, etc.
  Cloud Services:    AWS, GCP, Azure credentials
  Webhooks:          Custom webhooks and secrets
  AI Routing:        Provider credentials and endpoints
  Activations:       Integration activation settings

EXAMPLES:
  SETUP                     # Start interactive setup
  SETUP github              # Setup GitHub authentication
  SETUP ollama              # Setup local Ollama
  SETUP --profile           # View current settings
  SETUP --clear && SETUP    # Reset and reconfigure
  nano .env                 # Manual editing
"""
        }

    def _setup_provider(self, provider_id: str) -> Dict:
        """Setup a provider (github, ollama, mistral, etc.)."""
        import subprocess
        import sys

        output = [f"\n🔧 Setting up {provider_id.upper()}\n", "=" * 60]

        try:
            # Run the provider setup via wizard.check_provider_setup
            result = subprocess.run(
                [sys.executable, "-m", "wizard.check_provider_setup", "--provider", provider_id],
                capture_output=False,  # Show interactive output
                text=True,
            )

            if result.returncode == 0:
                output.append(f"\n✅ {provider_id} setup completed successfully")
                return {"status": "success", "output": "\n".join(output)}
            else:
                output.append(f"\n⚠️  {provider_id} setup had issues")
                output.append("Check the output above for details.")
                return {"status": "error", "output": "\n".join(output)}
        except FileNotFoundError:
            return {
                "status": "error",
                "message": f"Provider setup not available: {provider_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to setup {provider_id}: {str(e)}"
            }

    # ========================================================================
    # Helper Methods - .env Storage

    def _initialize_env_from_example(self) -> None:
        """Initialize .env from .env.example if it doesn't exist."""
        if self.env_file.exists():
            return

        example_file = self.env_file.parent / ".env.example"
        if not example_file.exists():
            return

        try:
            # Copy .env.example to .env
            example_content = example_file.read_text()
            self.env_file.write_text(example_content)
            from core.services.logging_service import get_logger
            get_logger("setup").info("[LOCAL] Initialized .env from .env.example")
        except Exception as e:
            from core.services.logging_service import get_logger
            get_logger("setup").warning(f"[LOCAL] Could not initialize .env: {e}")

    # ========================================================================

    def _load_env_vars(self) -> Dict:
        """Load setup variables from .env file."""
        try:
            if not self.env_file.exists():
                return {}

            env_vars = {}
            for line in self.env_file.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    # Only load setup-related vars
                    if key.startswith('USER_') or key in {'OS_TYPE', 'WIZARD_KEY'}:
                        env_vars[key] = value
            return env_vars
        except Exception:
            return {}

    def _save_to_env(self, data: Dict) -> bool:
        """Save setup data to .env file, preserving other vars."""
        try:
            from core.services.uid_generator import generate_uid, scramble_uid
            from datetime import datetime

            # Auto-detect and save UDOS_ROOT
            try:
                udos_root = _detect_udos_root()
                data['udos_root'] = str(udos_root)
                logger.info(f"[LOCAL] UDOS_ROOT will be saved: {udos_root}")
            except RuntimeError as e:
                logger.warning(f"[LOCAL] UDOS_ROOT detection failed: {e}")

            # Map form data to .env keys
            key_mapping = {
                'user_username': 'USER_NAME',
                'user_dob': 'USER_DOB',
                'user_role': 'USER_ROLE',
                'user_location': 'USER_LOCATION',
                'user_timezone': 'USER_TIMEZONE',
                'install_os_type': 'OS_TYPE',
                'user_password': 'USER_PASSWORD',
                'udos_root': 'UDOS_ROOT',
            }

            # Load existing .env
            existing = {}
            if self.env_file.exists():
                for line in self.env_file.read_text().splitlines():
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.split("=", 1)
                        existing[key.strip()] = value.strip()

            # Update with new data
            for form_key, env_key in key_mapping.items():
                if form_key in data:
                    value = data[form_key]
                    # Quote strings, but not empty values
                    if value:
                        existing[env_key] = f'"{value}"' if isinstance(value, str) else str(value)
                    else:
                        existing.pop(env_key, None)

            # Generate unique User ID from DOB, timezone, and current time
            if 'USER_ID' not in existing and 'user_dob' in data and 'user_timezone' in data:
                timestamp = datetime.now()
                if data.get('current_date') and data.get('current_time'):
                    try:
                        timestamp = datetime.strptime(
                            f"{data['current_date']} {data['current_time']}",
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except ValueError:
                        pass

                uid = generate_uid(
                    dob=data['user_dob'],
                    timezone=data['user_timezone'],
                    timestamp=timestamp
                )
                scrambled_uid = scramble_uid(uid)
                existing['USER_ID'] = f'"{scrambled_uid}"'

            # Generate or keep Wizard Key
            if 'WIZARD_KEY' not in existing:
                import uuid
                existing['WIZARD_KEY'] = f'"{str(uuid.uuid4())}"'

            # Add UDOS_ROOT (absolute path to repo root)
            if 'UDOS_ROOT' not in existing:
                from pathlib import Path
                repo_root = Path(__file__).parent.parent.parent.resolve()
                existing['UDOS_ROOT'] = f'"{str(repo_root)}"'

            # Write back to .env
            lines = []
            for key, value in sorted(existing.items()):
                lines.append(f"{key}={value}")

            self.env_file.write_text("\n".join(lines) + "\n")
            return True
        except Exception as e:
            from core.services.logging_service import get_logger
            get_logger("setup").error(f"Failed to save to .env: {e}")
            return False


def setup(*params: str) -> Dict:
    """Convenience wrapper for tests/scripts: run SETUP with params."""
    handler = SetupHandler()
    return handler.handle("SETUP", list(params), None, None)
