"""
SETUP command handler - View and manage setup profiles.

This command provides access to setup information stored in the Wizard Server.
It can display user and installation profiles, or launch the setup story.
"""

from pathlib import Path
from typing import Dict, List
import requests

from core.commands.base import BaseCommandHandler
from core.services.logging_manager import get_repo_root


class SetupHandler(BaseCommandHandler):
    """Handler for SETUP command - view setup profiles."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        SETUP command - view or manage setup profiles.
        
        Usage:
            SETUP              Run the setup story (default)
            SETUP --profile    Show your setup profile (from Wizard Server)
            SETUP --story      Run the setup story
            SETUP --wizard     Show how to access setup in Wizard console
            
        Quick start:
            1. SETUP                    (Run setup story)
            2. SETUP --profile          (View your profile)
            3. WIZARD start             (Start Wizard Server)
            4. WIZARD setup             (Access setup in dashboard)
        """
        if not params:
            return self._run_story()
        
        action = params[0].lower()
        
        if action in {"--story", "--run"}:
            return self._run_story()
        elif action in {"--profile", "--view"}:
            return self._show_profile()
        elif action == "--wizard":
            return self._show_wizard_help()
        else:
            return {
                "status": "error",
                "message": f"Unknown option: {action}",
                "help": "Usage: SETUP [--profile|--story|--wizard]"
            }
    
    def _show_profile(self) -> Dict:
        """Fetch and display setup profile from Wizard Server or local file."""
        try:
            # First, try local profile file
            local_profile = self._load_local_profile()
            if local_profile:
                return self._format_local_profile(local_profile)
            
            # Then try Wizard Server
            token_path = get_repo_root() / "memory" / "private" / "wizard_admin_token.txt"
            if not token_path.exists():
                return {
                    "status": "warning",
                    "output": """
╔═════════════════════════════════════════════════════════════╗
║  ⚠️  No Setup Profile Found                                 ║
╚═════════════════════════════════════════════════════════════╝

You haven't run the setup story yet. To get started:

  STORY wizard-setup

This will ask questions about your setup and save the answers.
Then use SETUP to view your profile.
"""
                }
            
            token = token_path.read_text().strip()
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to fetch profile
            response = requests.get(
                "http://localhost:8765/api/v1/setup/profile/combined",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 404:
                return {
                    "status": "warning",
                    "output": """
╔═════════════════════════════════════════════════════════════╗
║  ⚠️  No Setup Profile Found                                 ║
╚═════════════════════════════════════════════════════════════╝

You haven't run the setup story yet. To get started:

  STORY wizard-setup

This will ask questions about your setup and save the answers.
Then use SETUP to view your profile.
"""
                }
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Failed to fetch profile: HTTP {response.status_code}",
                    "help": "Is Wizard Server running? ./bin/start_wizard.sh"
                }
            
            data = response.json()
            user = data.get("user_profile", {})
            install = data.get("install_profile", {})
            metrics = data.get("install_metrics", {})
            
            if not user and not install:
                return {
                    "status": "warning",
                    "output": """
╔═════════════════════════════════════════════════════════════╗
║  ⚠️  No Setup Profile Found                                 ║
╚═════════════════════════════════════════════════════════════╝

You haven't run the setup story yet. To get started:

  STORY wizard-setup

This will ask questions about your setup and save the answers.
Then use SETUP to view your profile.
"""
                }
            
            # Format output
            lines = ["\n🧙 SETUP PROFILE:\n"]
            
            if user:
                lines.append("  User Identity:")
                lines.append(f"    • Username: {user.get('username', 'N/A')}")
                lines.append(f"    • Role: {user.get('role', 'N/A')}")
                lines.append(f"    • Timezone: {user.get('timezone', 'N/A')}")
                lines.append(f"    • Location: {user.get('location_name', 'N/A')} ({user.get('location_id', 'N/A')})")
                lines.append("")
            
            if install:
                lines.append("  Installation:")
                lines.append(f"    • ID: {install.get('installation_id', 'N/A')}")
                lines.append(f"    • OS Type: {install.get('os_type', 'N/A')}")
                lines.append(f"    • Lifespan: {install.get('lifespan_mode', 'infinite')}")
                
                caps = install.get("capabilities", {})
                if caps:
                    lines.append("")
                    lines.append("  Capabilities:")
                    for cap, enabled in sorted(caps.items()):
                        status = "✅" if enabled else "❌"
                        cap_name = cap.replace('_', ' ').title()
                        lines.append(f"    {status} {cap_name}")
                lines.append("")
            
            if metrics:
                moves_used = metrics.get("moves_used", 0)
                moves_limit = metrics.get("moves_limit")
                if moves_used > 0 or moves_limit:
                    lines.append("  Metrics:")
                    lines.append(f"    • Moves Used: {moves_used}")
                    if moves_limit:
                        remaining = moves_limit - moves_used
                        lines.append(f"    • Remaining: {remaining}/{moves_limit}")
                    lines.append("")
            
            return {
                "status": "success",
                "message": "\n".join(lines)
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "help": "Start Wizard Server: ./bin/start_wizard.sh"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to fetch profile: {e}",
                "help": "Check Wizard Server status"
            }
    
    def _run_story(self) -> Dict:
        """Launch the setup story."""
        try:
            from core.commands.story_handler import StoryHandler

            return StoryHandler().handle("STORY", ["wizard-setup"])
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to start setup story: {exc}",
                "help": "Ensure the wizard-setup story exists in seed data or memory/story",
            }
    
    def _load_local_profile(self) -> Dict:
        """Load user profile from local file (memory/user/profile.json)."""
        try:
            import json
            profile_file = get_repo_root() / "memory" / "user" / "profile.json"
            
            if profile_file.exists():
                with open(profile_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        
        return None
    
    def _format_local_profile(self, profile: Dict) -> Dict:
        """Format local profile data for display."""
        try:
            data = profile.get("data", {})
            if not data:
                return {
                    "status": "warning",
                    "output": "Profile file exists but is empty. Run STORY wizard-setup to populate it."
                }
            
            lines = ["🧙 YOUR SETUP PROFILE\n", "=" * 60]
            
            # User Identity section
            lines.append("\n📋 User Identity")
            lines.append("-" * 60)
            lines.append(f"  • Username:     {data.get('user_username', 'N/A')}")
            lines.append(f"  • DOB:          {data.get('user_dob', 'N/A')}")
            lines.append(f"  • Role:         {data.get('user_role', 'N/A')}")
            lines.append(f"  • Permissions:  {data.get('user_permissions', '(none)')}")
            
            # Time & Place section
            lines.append("\n📍 Time & Place")
            lines.append("-" * 60)
            lines.append(f"  • Timezone:     {data.get('user_timezone', 'N/A')}")
            lines.append(f"  • Local Time:   {data.get('user_local_time', 'N/A')}")
            lines.append(f"  • Location:     {data.get('user_location', 'N/A')}")
            
            # Installation section
            lines.append("\n⚙️  Installation")
            lines.append("-" * 60)
            install_id = data.get('install_id') or "(auto-generated)"
            lines.append(f"  • Install ID:   {install_id}")
            lines.append(f"  • OS Type:      {data.get('install_os_type', 'N/A')}")
            lines.append(f"  • Lifespan:     {data.get('install_lifespan_mode', 'infinite')}")
            lines.append(f"  • Moves Limit:  {data.get('install_moves_limit', 'N/A')}")
            
            # Capabilities section
            lines.append("\n🔧 Capabilities & Permissions")
            lines.append("-" * 60)
            
            capability_fields = {
                'capability_web_proxy': 'Web Proxy (APIs + scraping)',
                'capability_gmail_relay': 'Gmail Relay',
                'capability_ai_gateway': 'AI Gateway Routing',
                'capability_github_push': 'GitHub Push',
                'capability_notion': 'Notion Integration',
                'capability_hubspot': 'HubSpot Integration',
                'capability_icloud': 'iCloud Integration',
                'capability_plugin_repo': 'Plugin Repository',
                'capability_plugin_auto_update': 'Plugin Auto-Update',
            }
            
            for field_key, field_label in capability_fields.items():
                value = data.get(field_key, 'N/A')
                status = "✅" if value in ['yes', 'true', '1', True] else "❌"
                lines.append(f"  {status} {field_label}")
            
            lines.append("\n" + "=" * 60)
            lines.append(f"Profile updated: {profile.get('updated', 'N/A')}")
            
            return {
                "status": "success",
                "output": "\n".join(lines)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to format profile: {e}"
            }

    def _show_wizard_help(self) -> Dict:
        """Show how to access Wizard console setup."""
        return {
            "status": "info",
            "message": "\n".join([
                "",
                "To view setup in Wizard console:",
                "  1. Start Wizard Server: ./bin/start_wizard.sh",
                "  2. In the console, type: setup",
                "",
                "Or use SETUP (without --wizard) to view here in TUI.",
                ""
            ])
        }
