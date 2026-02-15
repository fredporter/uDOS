"""
SETUP command handler - Local offline setup for Core.

Stores user identity in .env (local, never shared):
    - Username, DOB, Role, Location, Timezone, OS-Type
  - Optional password (User/Admin roles only - can be blank)
  - Wizard Key (gateway to keystore for sensitive extensions)

All other sensitive data goes in Wizard keystore:
    - API keys (GitHub, OpenAI, etc.)
  - OAuth tokens (supported providers)
  - Cloud credentials and webhooks
  - Integration activation settings

When Wizard Server is installed, it imports these local settings.
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime

from core.commands.base import BaseCommandHandler
from core.commands.interactive_menu_mixin import InteractiveMenuMixin
from core.services.logging_api import get_repo_root, get_logger
from core.commands.setup_handler_helpers import (
    clear_setup_env,
    initialize_env_from_example,
    load_setup_env_vars,
    save_setup_to_env,
    setup_help_text,
)

logger = get_logger('setup-handler')


class SetupHandler(BaseCommandHandler, InteractiveMenuMixin):
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
            SETUP webhook      Interactive GitHub webhook setup (vibe-cli style)
            SETUP <provider>   Setup a specific provider (github, ollama, mistral, etc.)
            SETUP --profile    Show your current setup profile
            SETUP --edit       Edit setup values
            SETUP --clear      Clear setup data (start over)
            SETUP --help       Show help
            INSTALL vibe       Install Ollama + Vibe CLI + Mistral models

        Local data stored in .env:
            USER_NAME          Username
            USER_DOB           Date of birth (YYYY-MM-DD)
            USER_ROLE          admin | user | ghost
            USER_PASSWORD      Optional password (user/admin only, can be blank)
            UDOS_LOCATION      City / grid location
            UDOS_TIMEZONE      Timezone (e.g. America/Los_Angeles)
            OS_TYPE            alpine | ubuntu | mac | windows
            WIZARD_KEY         Gateway to Wizard keystore (auto-generated)

        Webhook Setup (interactive, vibe-cli style):
            SETUP webhook           Full setup (GitHub)
            SETUP webhook github    GitHub webhooks only

        Provider Setup (delegates to Wizard):
            Supported: github, ollama, mistral, openrouter

        Extended data in Wizard keystore (when installed):
            - API keys, OAuth tokens, credentials
            - Integrations (GitHub, etc.)
            - Cloud routing, webhooks, activation settings
        """
        if not params:
            choice = self.show_menu(
                "SETUP",
                [
                    ("Run setup story", "story", "Configure local identity"),
                    ("View profile", "profile", "Show current setup profile"),
                    ("Edit setup", "edit", "Update local .env values"),
                    ("Clear setup", "clear", "Reset local setup data"),
                    ("Webhook setup", "webhook", "Configure GitHub webhooks"),
                    ("Vibe helper setup", "vibe", "Install Ollama + Vibe CLI + Mistral models"),
                    ("Provider setup", "provider", "Configure provider (github/ollama/mistral/openrouter)"),
                    ("Help", "help", "Show SETUP help"),
                ],
            )
            if choice is None:
                return self._run_story()
            if choice == "story":
                return self._run_story()
            if choice == "profile":
                return self._show_profile()
            if choice == "edit":
                return self._edit_interactively()
            if choice == "clear":
                return self._clear_setup()
            if choice == "webhook":
                from core.commands.webhook_setup_handler import WebhookSetupHandler
                handler = WebhookSetupHandler()
                return handler.handle("SETUP", ["webhook"], grid, parser)
            if choice == "vibe":
                return self._setup_vibe()
            if choice == "provider":
                try:
                    provider = input("Provider (github/ollama/mistral/openrouter): ").strip().lower()
                except Exception:
                    provider = ""
                if provider:
                    return self._setup_provider(provider)
                return {"status": "warning", "message": "Provider not specified"}
            if choice == "help":
                return self._show_help()
            return self._run_story()

        action = params[0].lower()
        alias_map = {
            "help": "--help",
            "-h": "--help",
            "?": "--help",
            "profile": "--profile",
            "view": "--view",
            "show": "--show",
            "edit": "--edit",
            "clear": "--clear",
        }
        action = alias_map.get(action, action)

        # Check if this is a webhook setup request (new!)
        if action == "webhook":
            from core.commands.webhook_setup_handler import WebhookSetupHandler
            handler = WebhookSetupHandler()
            return handler.handle("SETUP", params, grid, parser)

        if action == "vibe":
            return self._setup_vibe()

        # Check if this is a provider setup request
        provider_names = {"github", "ollama", "mistral", "openrouter"}
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
                "help": "Usage: SETUP [webhook|provider|--profile|--edit|--clear|--help]\n       Webhook: SETUP webhook [github]\n       Providers: github, ollama, mistral, openrouter"
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
            lines.append(
                f"  • Location:     {env_data.get('UDOS_LOCATION', 'Not set')}"
            )
            lines.append(
                f"  • Timezone:     {env_data.get('UDOS_TIMEZONE', 'Not set')}"
            )

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
            if isinstance(result, dict):
                result.setdefault("command", "SETUP")

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
  UDOS_LOCATION          City / grid location
  UDOS_TIMEZONE          America/Los_Angeles, etc.
  OS_TYPE                alpine | ubuntu | mac | windows
"""
        }

    def _clear_setup(self) -> Dict:
        """Clear setup data from .env."""
        try:
            clear_setup_env(self.env_file)

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
            "output": setup_help_text(),
        }

    def _setup_vibe(self) -> Dict:
        """Install local Vibe helper stack (Ollama + Vibe CLI + models)."""
        output: List[str] = []
        output.append("\n⚙️  SETUP VIBE: Installing local AI helpers\n")
        output.append("=" * 60)
        try:
            from core.services.ok_setup import run_ok_setup
            from core.services.logging_api import get_repo_root

            result = run_ok_setup(
                get_repo_root(),
                log=lambda msg: output.append(msg),
                models=None,
            )
            for warning in result.get("warnings", []):
                output.append(f"  ⚠️  {warning}")
            output.append("✅ SETUP VIBE complete.")
            return {"status": "success", "output": "\n".join(output)}
        except Exception as exc:
            output.append(f"⚠️  SETUP VIBE failed: {exc}")
            return {"status": "error", "output": "\n".join(output)}

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
        initialize_env_from_example(self.env_file, logger=get_logger("setup"))

    # ========================================================================

    def _load_env_vars(self) -> Dict:
        """Load setup variables from .env file."""
        return load_setup_env_vars(self.env_file)

    def _save_to_env(self, data: Dict) -> bool:
        """Save setup data to .env file, preserving other vars."""
        return save_setup_to_env(self.env_file, data, logger=get_logger("setup"))


def setup(*params: str) -> Dict:
    """Convenience wrapper for tests/scripts: run SETUP with params."""
    handler = SetupHandler()
    return handler.handle("SETUP", list(params), None, None)
