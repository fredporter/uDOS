"""
SETUP command handler - Local offline setup for Core.

Stores user identity in .env (local, never shared):
  - Name, DOB, Role, Location, Timezone, OS-Type
  - Optional password (User/Admin roles only)
  - Wizard Key (gateway to keystore for sensitive extensions)

When Wizard Server is installed, it imports these local settings.
Sensitive extensions (AI routes, webhooks, etc.) use Wizard keystore.
"""

from pathlib import Path
from typing import Dict, List
import os
from datetime import datetime

from core.commands.base import BaseCommandHandler
from core.services.logging_manager import get_repo_root


class SetupHandler(BaseCommandHandler):
    """Handler for SETUP command - local offline setup via .env."""

    def __init__(self):
        """Initialize paths."""
        super().__init__()
        self.env_file = get_repo_root() / ".env"
        self.env_file.parent.mkdir(parents=True, exist_ok=True)

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        SETUP command - manage local offline user setup in .env.
        
        Usage:
            SETUP              Run the setup story (configure local identity)
            SETUP --profile    Show your current setup profile
            SETUP --edit       Edit setup values
            SETUP --clear      Clear setup data (start over)
            SETUP --help       Show help
            
        Local data stored in .env:
            USER_NAME          Your name
            USER_DOB           Date of birth (YYYY-MM-DD)
            USER_ROLE          admin | user | ghost
            USER_LOCATION      City / grid location
            USER_TIMEZONE      Timezone (e.g. America/Los_Angeles)
            OS_TYPE            alpine | ubuntu | mac | windows
            USER_PASSWORD      Optional password (user/admin only, leave blank for ghost)
            WIZARD_KEY         Gateway to Wizard keystore (auto-generated)
        
        Sensitive extensions go in Wizard keystore (when installed):
            - API keys, OAuth tokens, credentials
            - Integrations (GitHub, Gmail, Notion, etc.)
            - Cloud routing and webhooks
        """
        if not params:
            return self._run_story()
        
        action = params[0].lower()
        
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
                "help": "Usage: SETUP [--profile|--edit|--clear|--help]"
            }
    
    def _show_profile(self) -> Dict:
        """Display the current setup profile from .env."""
        try:
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
  • Your name and date of birth
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
            lines.append(f"  • Name:         {env_data.get('USER_NAME', 'Not set')}")
            lines.append(f"  • DOB:          {env_data.get('USER_DOB', 'Not set')}")
            lines.append(f"  • Role:         {env_data.get('USER_ROLE', 'ghost')}")
            has_password = "yes" if env_data.get('USER_PASSWORD') else "no"
            lines.append(f"  • Password:     {has_password}")
            
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
            lines.append("When Wizard Server is installed, it will import this.")
            
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
            from core.commands.story_handler import StoryHandler
            
            # Run the wizard-setup story
            result = StoryHandler().handle("STORY", ["wizard-setup"])
            
            # If story was successful and returned form data, save to .env
            if result.get("status") == "success" and "form_data" in result:
                self._save_to_env(result["form_data"])
                return {
                    "status": "success",
                    "output": "✅ Setup complete! Your profile has been saved to .env\n\nRun 'SETUP --profile' to view your settings."
                }
            
            return result
            
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to start setup story: {exc}",
                "help": "Ensure memory/story/wizard-setup-story.md exists"
            }
    
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
  USER_NAME              Your name
  USER_DOB               YYYY-MM-DD
  USER_ROLE              ghost | user | admin
  USER_LOCATION          City / grid location
  USER_TIMEZONE          America/Los_Angeles, etc.
  OS_TYPE                alpine | ubuntu | mac | windows
  USER_PASSWORD          Optional (leave blank for ghost)
"""
        }
    
    def _clear_setup(self) -> Dict:
        """Clear setup data from .env."""
        try:
            env_vars = [
                'USER_NAME', 'USER_DOB', 'USER_ROLE', 
                'USER_LOCATION', 'USER_TIMEZONE', 'OS_TYPE',
                'USER_PASSWORD'
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
  SETUP --profile    Show your current setup
  SETUP --edit       Edit setup manually
  SETUP --clear      Clear all setup data
  SETUP --help       Show this help

LOCAL SETTINGS (.env):
  USER_NAME          Your name
  USER_DOB           Birth date (YYYY-MM-DD)
  USER_ROLE          ghost | user | admin
  USER_LOCATION      City or grid coordinates
  USER_TIMEZONE      Timezone identifier
  OS_TYPE            alpine | ubuntu | mac | windows
  USER_PASSWORD      Optional password (user/admin only)
  WIZARD_KEY         Gateway to Wizard keystore

EXTENDED SETTINGS (Wizard Keystore - installed later):
  GitHub tokens, Gmail OAuth, Notion API keys
  Cloud integrations, webhooks, AI routing
  Provider credentials and activation settings

EXAMPLES:
  SETUP                     # Start interactive setup
  SETUP --profile           # View current settings
  SETUP --clear && SETUP    # Reset and reconfigure
  nano .env                 # Manual editing
"""
        }
    
    # ========================================================================
    # Helper Methods - .env Storage
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
            # Map form data to .env keys
            key_mapping = {
                'user_username': 'USER_NAME',
                'user_dob': 'USER_DOB',
                'user_role': 'USER_ROLE',
                'user_location': 'USER_LOCATION',
                'user_timezone': 'USER_TIMEZONE',
                'install_os_type': 'OS_TYPE',
                'user_password': 'USER_PASSWORD',
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
            
            # Generate or keep Wizard Key
            if 'WIZARD_KEY' not in existing:
                import uuid
                existing['WIZARD_KEY'] = f'"{str(uuid.uuid4())}"'
            
            # Write back to .env
            lines = []
            for key, value in sorted(existing.items()):
                lines.append(f"{key}={value}")
            
            self.env_file.write_text("\n".join(lines) + "\n")
            return True
        except Exception as e:
            from core.services.logging_manager import get_logger
            get_logger("setup").error(f"Failed to save to .env: {e}")
            return False
