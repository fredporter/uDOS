"""
SETUP command handler - Local offline setup for TUI.

This command manages user identity and installation settings stored locally
in Core. It does NOT require Wizard Server to be running.

When Wizard Server is eventually installed, it can import this local setup data.
"""

from pathlib import Path
from typing import Dict, List
import json
from datetime import datetime

from core.commands.base import BaseCommandHandler
from core.services.logging_manager import get_repo_root


class SetupHandler(BaseCommandHandler):
    """Handler for SETUP command - local offline setup."""

    def __init__(self):
        """Initialize storage paths."""
        super().__init__()
        repo_root = get_repo_root()
        self.setup_file = repo_root / "memory" / "user" / "setup.json"
        self.setup_file.parent.mkdir(parents=True, exist_ok=True)

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        SETUP command - manage local offline user setup.
        
        Usage:
            SETUP              Run the setup story (configure user + timezone + location)
            SETUP --profile    Show your current setup profile
            SETUP --edit       Edit setup interactively
            SETUP --clear      Clear setup data (start over)
            SETUP --help       Show help
            
        Data stored locally in:
            - memory/user/setup.json   (user identity, timezone, location)
        
        When Wizard Server is installed later, it imports this data.
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
        """Display the current setup profile from local storage."""
        try:
            setup_data = self._load_setup()
            
            if not setup_data:
                return {
                    "status": "warning",
                    "output": """
╔═════════════════════════════════════════════════════════════╗
║  ⚠️  No Setup Profile Found                                 ║
╚═════════════════════════════════════════════════════════════╝

You haven't configured your identity yet. To get started:

  SETUP

This will run the setup story and ask you for:
  • Name and role
  • Timezone and location
  • Installation preferences

Your settings are stored locally in:
  memory/user/setup.json

When Wizard Server is installed later, it will import this data.
"""
                }
            
            lines = ["\n🧙 YOUR LOCAL SETUP PROFILE\n", "=" * 60]
            
            # User Identity
            lines.append("\n📋 User Identity")
            lines.append("-" * 60)
            lines.append(f"  • Name:         {setup_data.get('name', 'Not set')}")
            lines.append(f"  • DOB:          {setup_data.get('dob', 'Not set')}")
            lines.append(f"  • Role:         {setup_data.get('role', 'Not set')}")
            
            # Time & Place
            lines.append("\n📍 Time & Place")
            lines.append("-" * 60)
            lines.append(f"  • Timezone:     {setup_data.get('timezone', 'Not set')}")
            lines.append(f"  • Local Time:   {setup_data.get('local_time', 'Not set')}")
            lines.append(f"  • Location:     {setup_data.get('location', 'Not set')}")
            
            # Installation
            lines.append("\n⚙️  Installation")
            lines.append("-" * 60)
            lines.append(f"  • OS Type:      {setup_data.get('os_type', 'Not set')}")
            lines.append(f"  • Lifespan:     {setup_data.get('lifespan_mode', 'infinite')}")
            
            lines.append("\n" + "=" * 60)
            lines.append(f"Last updated: {setup_data.get('updated', 'unknown')}")
            lines.append("Data stored in: memory/user/setup.json")
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
        """Launch the setup story to configure user identity."""
        try:
            from core.commands.story_handler import StoryHandler
            
            # Run the wizard-setup story
            result = StoryHandler().handle("STORY", ["wizard-setup"])
            
            # If story was successful and returned form data, save it
            if result.get("status") == "success" and "form_data" in result:
                self._save_setup(result["form_data"])
                return {
                    "status": "success",
                    "output": "✅ Setup complete! Your profile has been saved.\n\nRun 'SETUP --profile' to view your settings."
                }
            
            return result
            
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to start setup story: {exc}",
                "help": "Ensure memory/story/wizard-setup-story.md exists"
            }
    
    def _edit_interactively(self) -> Dict:
        """Edit setup interactively (prompts for each field)."""
        try:
            return {
                "status": "info",
                "output": """
To configure your setup interactively, run:

  SETUP

This will guide you through setting up:
  ✓ Your identity (name, DOB, role)
  ✓ Your location and timezone
  ✓ Installation preferences

Your answers are saved to: memory/user/setup.json

Alternatively, edit the file directly:
  nano memory/user/setup.json
"""
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Edit failed: {e}"
            }
    
    def _clear_setup(self) -> Dict:
        """Clear all setup data (start fresh)."""
        try:
            if self.setup_file.exists():
                self.setup_file.unlink()
            return {
                "status": "success",
                "output": "✅ Setup data cleared. Run 'SETUP' to configure again."
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

SETUP configures your user identity and installation settings
locally in Core. This works WITHOUT needing Wizard Server.

When Wizard Server is later installed, it imports this data.

USAGE:
  SETUP              Run setup story (interactive questions)
  SETUP --profile    Show your current setup
  SETUP --edit       Edit setup (manually)
  SETUP --clear      Clear all setup data
  SETUP --help       Show this help

WHAT GETS CONFIGURED:
  ✓ Your name and date of birth
  ✓ Your role (admin/user/ghost)
  ✓ Timezone and location
  ✓ Installation OS type and lifespan
  ✓ Feature capabilities

DATA STORAGE:
  Location: memory/user/setup.json
  Later: Wizard Server imports and extends this data

EXAMPLES:
  SETUP                     # Start interactive setup
  SETUP --profile           # View current settings
  SETUP --clear && SETUP    # Reset and reconfigure
"""
        }
    
    # ========================================================================
    # Helper Methods - Local Storage
    # ========================================================================
    
    def _load_setup(self) -> Dict:
        """Load setup data from local JSON file."""
        try:
            if self.setup_file.exists():
                return json.loads(self.setup_file.read_text())
        except Exception:
            pass
        return None
    
    def _save_setup(self, data: Dict) -> bool:
        """Save setup data to local JSON file."""
        try:
            self.setup_file.parent.mkdir(parents=True, exist_ok=True)
            data['updated'] = datetime.now().isoformat()
            self.setup_file.write_text(json.dumps(data, indent=2))
            return True
        except Exception:
            return False
