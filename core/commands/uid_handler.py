"""
UID Command Handler - View and decode user IDs.

Usage:
    UID                    Show current user ID
    UID decode <uid>       Decode a scrambled UID
    UID --help             Show help
"""
from pathlib import Path
from typing import Dict, List
from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_repo_root


class UIDHandler(BaseCommandHandler):
    """Handler for UID command."""
    
    def __init__(self):
        self.env_file = get_repo_root() / ".env"
    
    def handle(self, command: str, params: List[str]) -> Dict:
        """
        Handle UID command.
        
        Args:
            command: Command name (UID)
            params: Command parameters
        
        Returns:
            Result dictionary
        """
        if not params:
            return self._show_current_uid()
        
        action = params[0].lower()
        
        if action == "decode" and len(params) > 1:
            return self._decode_uid(params[1])
        elif action == "--help":
            return self._show_help()
        else:
            return {
                "status": "error",
                "message": f"Unknown option: {action}",
                "help": "Usage: UID | UID decode <uid> | UID --help"
            }
    
    def _show_current_uid(self) -> Dict:
        """Show the current user ID from .env."""
        try:
            from core.services.uid_generator import descramble_uid, parse_uid
            
            # Load USER_ID from .env
            user_id = self._load_user_id()
            
            if not user_id:
                return {
                    "status": "warning",
                    "output": """
⚠️  No User ID found

Run SETUP to generate your unique User ID.
"""
                }
            
            # Descramble and parse
            try:
                uid_plain = descramble_uid(user_id)
                parsed = parse_uid(uid_plain)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to decode UID: {e}"
                }
            
            lines = [
                "\n🆔 YOUR USER ID\n",
                "=" * 60,
                f"\nPlain:      {uid_plain}",
                f"Scrambled:  {user_id[:40]}{'...' if len(user_id) > 40 else ''}",
                "\n" + "-" * 60,
                "\n📋 Components:",
                f"  • Date of Birth: {parsed.get('dob', 'N/A')}",
                f"  • Timezone:      {parsed.get('timezone', 'N/A')}",
                f"  • Setup Time:    {parsed.get('hour', '00')}:{parsed.get('minute', '00')}:{parsed.get('second', '00')}.{parsed.get('millisecond', '000')}",
                "\n" + "=" * 60,
                "\nThis ID uniquely identifies your uDOS installation.",
                "It's generated from your profile data and setup timestamp.",
            ]
            
            return {
                "status": "success",
                "output": "\n".join(lines)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to show UID: {e}"
            }
    
    def _decode_uid(self, uid: str) -> Dict:
        """Decode a scrambled or plain UID."""
        try:
            from core.services.uid_generator import descramble_uid, parse_uid
            
            # Try descrambling
            uid_plain = descramble_uid(uid)
            parsed = parse_uid(uid_plain)
            
            if not parsed:
                return {
                    "status": "error",
                    "message": "Invalid UID format"
                }
            
            lines = [
                "\n🔍 UID DECODED\n",
                "=" * 60,
                f"\nPlain Format: {uid_plain}",
                "\n" + "-" * 60,
                "\n📋 Components:",
                f"  • Date of Birth: {parsed.get('dob', 'N/A')}",
                f"  • Timezone:      {parsed.get('timezone', 'N/A')}",
                f"  • Setup Time:    {parsed.get('hour', '00')}:{parsed.get('minute', '00')}:{parsed.get('second', '00')}.{parsed.get('millisecond', '000')}",
                "\n" + "=" * 60,
            ]
            
            return {
                "status": "success",
                "output": "\n".join(lines)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to decode UID: {e}"
            }
    
    def _load_user_id(self) -> str:
        """Load USER_ID from .env file."""
        try:
            if not self.env_file.exists():
                return ""
            
            for line in self.env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("USER_ID="):
                    value = line.split("=", 1)[1].strip().strip('"\'')
                    return value
            
            return ""
        except Exception:
            return ""
    
    def _show_help(self) -> Dict:
        """Show help for UID command."""
        return {
            "status": "success",
            "output": """
╔═════════════════════════════════════════════════════════════╗
║                    UID - User ID Manager                     ║
╚═════════════════════════════════════════════════════════════╝

USAGE:
  UID                    Show your current User ID
  UID decode <uid>       Decode a scrambled UID
  UID --help             Show this help

ABOUT USER IDs:
  User IDs are unique identifiers generated during SETUP.
  They combine your date of birth, timezone, and setup timestamp.
  
  Format: UID-YYYY-MM-DD-TZ-HH-MM-SS-mmm
  
  The ID is scrambled (base64) for storage in .env but can be
  decoded at any time to recover the original components.

EXAMPLES:
  UID                           View your UID
  UID decode VUlELTE5NzU...     Decode a scrambled UID

SEE ALSO:
  SETUP --profile        View full user profile
  CONFIG                 View all environment variables
"""
        }
