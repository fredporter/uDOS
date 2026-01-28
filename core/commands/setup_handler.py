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
            SETUP              Show setup profile from Wizard
            SETUP --story      Run the setup story
            SETUP --wizard     Open Wizard console setup view
        """
        if not params:
            return self._show_profile()
        
        action = params[0].lower()
        
        if action == "--story":
            return self._run_story()
        elif action == "--wizard":
            return self._show_wizard_help()
        else:
            return {
                "status": "error",
                "message": f"Unknown option: {action}",
                "help": "Usage: SETUP [--story|--wizard]"
            }
    
    def _show_profile(self) -> Dict:
        """Fetch and display setup profile from Wizard Server."""
        try:
            # Try to get admin token
            token_path = get_repo_root() / "memory" / "private" / "wizard_admin_token.txt"
            if not token_path.exists():
                return {
                    "status": "error",
                    "message": "Admin token not found. Is Wizard Server configured?",
                    "help": "Run Wizard Server first: ./bin/start_wizard.sh"
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
                    "message": "No setup profile found. Run the setup story first.",
                    "help": "Command: SETUP --story or STORY wizard-setup"
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
                    "message": "Setup profiles are empty. Run setup story first.",
                    "help": "Command: SETUP --story"
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
        return {
            "status": "info",
            "message": "To run the setup story, use: STORY wizard-setup",
            "help": "Note: This requires the TypeScript runtime. Build it with: core/tools/build_ts_runtime.sh"
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
