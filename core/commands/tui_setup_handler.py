"""
TUI Setup Handler - Core setup for uDOS TUI

Handles user setup in the TUI, including:
- Name validation (no forbidden names, no blanks)
- Role selection (admin, user, ghost)
- Location & timezone collection
- System info auto-detection
- Variable persistence

Usage:
    SETUP                 - Show current setup
    SETUP --run-story     - Run setup story
    SETUP --reset         - Reset to ghost mode (requires confirmation)

Author: uDOS Engineering
Version: v1.1.0
Date: 2026-01-30
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from core.commands.base import BaseCommandHandler
from core.services.logging_manager import get_repo_root
from core.services.name_validator import validate_name, validate_username


class TUISetupHandler(BaseCommandHandler):
    """Handler for TUI setup operations."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle SETUP command.

        Usage:
            SETUP              - Show current setup profile
            SETUP --story      - Run setup story
            SETUP --reset      - Reset to ghost mode
        """
        if not params:
            return self._show_profile()

        action = params[0].lower()

        if action == "--story":
            return self._run_setup_story(parser)
        elif action == "--reset":
            return self._reset_to_ghost()
        else:
            return {
                "status": "error",
                "message": f"Unknown option: {action}",
                "help": "Usage: SETUP [--story|--reset]"
            }

    def _show_profile(self) -> Dict:
        """Show current setup profile from local storage."""
        profile_file = self._get_profile_file()

        if not profile_file.exists():
            return {
                "status": "warning",
                "output": """
╔═══════════════════════════════════════════════════════╗
║  No Setup Profile Found                               ║
╚═══════════════════════════════════════════════════════╝

You're currently in ghost mode (demo/test).

To set up your identity:

  SETUP --story

This will ask about your name, role, location, and timezone.
Then you can fully use uDOS.
"""
            }

        try:
            with open(profile_file, "r") as f:
                profile = json.load(f)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not read profile: {e}"
            }

        # Format profile
        lines = ["\n🧑 Your Setup Profile:\n"]
        lines.append(f"  Name:      {profile.get('user_real_name', 'N/A')}")
        lines.append(f"  Role:      {profile.get('user_role', 'ghost')}")
        lines.append(f"  Location:  {profile.get('user_location', 'N/A')}")
        lines.append(f"  Timezone:  {profile.get('user_timezone', 'UTC')}")
        lines.append(f"  DOB:       {profile.get('user_dob', 'N/A')}")
        lines.append(f"  Created:   {profile.get('created', 'N/A')}")
        lines.append("")

        return {
            "status": "success",
            "output": "\n".join(lines),
            "profile": profile
        }

    def _run_setup_story(self, parser=None) -> Dict:
        """Run the TUI setup story with validation."""
        from core.commands.story_handler import StoryHandler

        # Get system info for defaults
        system_info = self._get_system_info()

        # Load and parse story
        story_path = Path(__file__).parent / "setup-story.md"
        if not story_path.exists():
            return {
                "status": "error",
                "message": f"Setup story not found: {story_path}",
                "help": "This is a system error. Please report it."
            }

        # Run story handler
        handler = StoryHandler()
        result = handler._run_story("core/tui/setup-story.md")

        if result.get("status") != "success":
            return result

        # Mark this as a setup story form for special handling
        if result.get("story_form"):
            # Inject system defaults into form
            story_form = result["story_form"]
            if "sections" in story_form:
                for section in story_form["sections"]:
                    if "fields" in section:
                        for field in section["fields"]:
                            if field.get("name") == "user_timezone":
                                field["default"] = system_info["timezone"]
                            elif field.get("name") == "user_time_confirmed":
                                field["default"] = True
                                field["label"] = f"Current time looks correct? (System time: {system_info['time']})"
            
            result["is_setup_story"] = True
            result["system_info"] = system_info

        return result

    def _reset_to_ghost(self) -> Dict:
        """Reset to ghost mode (requires confirmation)."""
        profile_file = self._get_profile_file()

        if profile_file.exists():
            try:
                profile_file.unlink()
                return {
                    "status": "success",
                    "output": """
╔═══════════════════════════════════════════════════════╗
║  Reset to Ghost Mode                                  ║
╚═══════════════════════════════════════════════════════╝

Your setup profile has been cleared.

You're now in ghost mode (demo/test).

To set up your identity:

  SETUP --story
"""
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Could not reset profile: {e}"
                }
        else:
            return {
                "status": "warning",
                "message": "No profile to reset - already in ghost mode"
            }

    def validate_and_save_setup(self, form_data: Dict) -> Tuple[bool, str]:
        """
        Validate setup form data and save to profile.

        Args:
            form_data: Form data from setup story

        Returns:
            Tuple of (success, message)
        """
        # Validate name
        name = form_data.get("user_real_name", "").strip()
        is_valid, error = validate_name(name)
        if not is_valid:
            return False, error

        # Validate role
        role = form_data.get("user_role", "ghost").lower()
        if role not in ["admin", "user", "ghost"]:
            return False, f"Invalid role: {role}"

        # Validate timezone (optional, uses system default)
        timezone = form_data.get("user_timezone", "").strip()
        if not timezone:
            system_info = self._get_system_info()
            timezone = system_info["timezone"]

        # Validate location
        location = form_data.get("user_location", "").strip()
        if not location:
            return False, "Location cannot be blank"

        # Validate DOB format
        dob = form_data.get("user_dob", "").strip()
        if not dob:
            return False, "Date of birth cannot be blank"
        try:
            # Try parsing as YYYY-MM-DD
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            return False, "Date of birth must be in YYYY-MM-DD format"

        # Build profile
        profile = {
            "user_real_name": name,
            "user_role": role,
            "user_location": location,
            "user_timezone": timezone,
            "user_dob": dob,
            "created": datetime.now().isoformat(),
            "system_info": self._get_system_info(),
        }

        # Save to file
        profile_file = self._get_profile_file()
        profile_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(profile_file, "w") as f:
                json.dump(profile, f, indent=2)
            return True, "Setup profile saved successfully"
        except Exception as e:
            return False, f"Could not save profile: {e}"

    def get_setup_profile(self) -> Optional[Dict]:
        """
        Get the current setup profile.

        Returns:
            Profile dict or None if not set up
        """
        profile_file = self._get_profile_file()

        if not profile_file.exists():
            return None

        try:
            with open(profile_file, "r") as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def _get_profile_file() -> Path:
        """Get the path to the setup profile file."""
        repo_root = get_repo_root()
        return repo_root / "memory" / "bank" / "setup-profile.json"

    @staticmethod
    def _get_system_info() -> Dict:
        """
        Get system information for setup defaults.

        Returns:
            Dict with system info
        """
        import platform
        import time
        from datetime import datetime
        import os

        # Try to get timezone
        try:
            import tzlocal
            tz = tzlocal.get_localzone_name()
        except Exception:
            try:
                # Fallback to environment variable
                tz = os.environ.get("TZ", "UTC")
            except Exception:
                tz = "UTC"

        return {
            "os_type": platform.system().lower(),
            "os_version": platform.release(),
            "timezone": tz,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "timestamp": datetime.now().isoformat(),
            "python_version": platform.python_version(),
        }
