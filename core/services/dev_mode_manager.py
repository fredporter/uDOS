"""
DEV MODE Manager - Master User Development Environment

Provides secure development mode with:
- Master user authentication
- Session management and tracking
- Permission system for dangerous operations
- Activity logging and audit trail
- Hot reload capabilities

Version: 1.0.0
Author: uDOS Development Team
Created: 2025-11-25
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import hashlib
import getpass


class DevModeManager:
    """
    Manages DEV MODE state, authentication, and permissions.

    DEV MODE provides unrestricted access to dangerous operations
    and development tools. Only available to master users.
    """

    def __init__(self, config_manager=None, base_path: Optional[Path] = None):
        """
        Initialize DEV MODE manager.

        Args:
            config_manager: ConfigManager instance for master user credentials
            base_path: Project root path (defaults to current directory)
        """
        self.config = config_manager
        self.base_path = base_path or Path.cwd()
        self.log_path = self.base_path / 'memory' / 'logs' / 'dev_mode.log'
        self.session_file = self.base_path / 'memory' / 'logs' / 'dev_mode_session.json'

        # Session state
        self.is_active = False
        self.session_start = None
        self.authenticated_user = None
        self.command_count = 0

        # Dangerous commands that require DEV MODE
        self.dangerous_commands = {
            'DELETE', 'DESTROY', 'REPAIR', 'RESET', 'WIPE',
            'EXECUTE', 'SHELL', 'EVAL', 'IMPORT', 'LOAD'
        }

        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing session if any
        self._load_session()

    def authenticate(self, password: str) -> bool:
        """
        Authenticate master user with password.

        Args:
            password: Password to verify

        Returns:
            True if authentication successful, False otherwise
        """
        if not self.config:
            self._log("Authentication failed: No config manager")
            return False

        # Get master password from config
        master_password = self.config.get('UDOS_MASTER_PASSWORD', '')
        master_user = self.config.get('UDOS_MASTER_USER', '')
        current_user = self.config.get('username', '')

        # Validate master user is configured
        if not master_password or not master_user:
            self._log("Authentication failed: Master user not configured")
            return False

        # Verify current user matches master user
        if current_user != master_user:
            self._log(f"Authentication failed: User '{current_user}' is not master user '{master_user}'")
            return False

        # Verify password (simple comparison - in production use hashing)
        if password != master_password:
            self._log("Authentication failed: Invalid password")
            return False

        self.authenticated_user = master_user
        self._log(f"Authentication successful: {master_user}")
        return True

    def enable(self, password: Optional[str] = None, interactive: bool = True) -> tuple[bool, str]:
        """
        Enable DEV MODE with authentication.

        Args:
            password: Master password (if None, prompts interactively)
            interactive: Whether to prompt for password if not provided

        Returns:
            (success: bool, message: str)
        """
        if self.is_active:
            return False, "⚠️ DEV MODE already active"

        # Get password if not provided
        if password is None and interactive:
            try:
                password = getpass.getpass("🔐 Enter master password: ")
            except Exception as e:
                return False, f"❌ Password input failed: {e}"

        if password is None:
            return False, "❌ Password required for DEV MODE"

        # Authenticate
        if not self.authenticate(password):
            return False, "❌ Authentication failed - Invalid credentials"

        # Enable DEV MODE
        self.is_active = True
        self.session_start = datetime.now()
        self.command_count = 0

        # Save session
        self._save_session()

        # Log activation
        self._log(f"DEV MODE ACTIVATED by {self.authenticated_user}")

        message = (
            f"✅ DEV MODE ACTIVATED\n"
            f"⚠️  You now have unrestricted system access\n"
            f"⚠️  All actions are logged to {self.log_path}\n"
            f"👤 Authenticated as: {self.authenticated_user}\n"
            f"🕐 Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        return True, message

    def disable(self) -> tuple[bool, str]:
        """
        Disable DEV MODE.

        Returns:
            (success: bool, message: str)
        """
        if not self.is_active:
            return False, "⚠️ DEV MODE not active"

        # Calculate session duration
        duration = datetime.now() - self.session_start if self.session_start else None
        duration_str = str(duration).split('.')[0] if duration else "Unknown"

        # Log deactivation
        self._log(
            f"DEV MODE DEACTIVATED by {self.authenticated_user} "
            f"(Duration: {duration_str}, Commands: {self.command_count})"
        )

        # Disable DEV MODE
        self.is_active = False
        self.session_start = None
        self.authenticated_user = None
        self.command_count = 0

        # Clear session file
        if self.session_file.exists():
            self.session_file.unlink()

        message = (
            f"✅ DEV MODE DEACTIVATED\n"
            f"📊 Session duration: {duration_str}\n"
            f"📋 Commands executed: {self.command_count}\n"
            f"🔐 Returned to standard user permissions"
        )

        return True, message

    def check_permission(self, command: str) -> tuple[bool, Optional[str]]:
        """
        Check if command is allowed based on current mode.

        Args:
            command: Command name to check

        Returns:
            (allowed: bool, warning_message: Optional[str])
        """
        command_upper = command.upper()

        # Check if command is dangerous
        if command_upper in self.dangerous_commands:
            if self.is_active:
                # Allow in DEV MODE but warn
                warning = f"⚠️ Dangerous operation: {command} (DEV MODE enabled)"
                return True, warning
            else:
                # Deny without DEV MODE
                error = (
                    f"❌ Command '{command}' requires DEV MODE\n"
                    f"💡 Enable with: DEV MODE ON"
                )
                return False, error

        # Command is safe - allow
        return True, None

    def log_command(self, command: str, params: List[str], result: str = "Success"):
        """
        Log command execution in DEV MODE.

        Args:
            command: Command name
            params: Command parameters
            result: Execution result
        """
        if not self.is_active:
            return

        self.command_count += 1

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': self.authenticated_user,
            'command': command,
            'params': params,
            'result': result,
            'command_number': self.command_count
        }

        self._log(f"Command #{self.command_count}: {command} {' '.join(params)} -> {result}")

        # Also save to JSON for programmatic access
        self._append_command_log(log_entry)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current DEV MODE status.

        Returns:
            Status dictionary with all relevant information
        """
        if not self.is_active:
            return {
                'active': False,
                'master_user': self.config.get('UDOS_MASTER_USER', 'Not configured') if self.config else 'Unknown',
                'message': 'DEV MODE inactive'
            }

        duration = datetime.now() - self.session_start if self.session_start else None
        duration_str = str(duration).split('.')[0] if duration else "Unknown"

        return {
            'active': True,
            'user': self.authenticated_user,
            'session_start': self.session_start.isoformat() if self.session_start else None,
            'duration': duration_str,
            'commands_executed': self.command_count,
            'log_file': str(self.log_path),
            'dangerous_commands': list(self.dangerous_commands)
        }

    def _log(self, message: str):
        """Write message to DEV MODE log file."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] {message}\n"

            with open(self.log_path, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠️ Failed to write to DEV MODE log: {e}")

    def _append_command_log(self, log_entry: Dict[str, Any]):
        """Append command to JSON log file."""
        try:
            log_file = self.log_path.parent / 'dev_mode_commands.json'

            # Load existing logs
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            # Append new entry
            logs.append(log_entry)

            # Save (keep last 1000 entries)
            with open(log_file, 'w') as f:
                json.dump(logs[-1000:], f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to write command log: {e}")

    def _save_session(self):
        """Save current session state to file."""
        try:
            session_data = {
                'active': self.is_active,
                'user': self.authenticated_user,
                'session_start': self.session_start.isoformat() if self.session_start else None,
                'command_count': self.command_count
            }

            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save session: {e}")

    def _load_session(self):
        """Load previous session state if exists."""
        try:
            if not self.session_file.exists():
                return

            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

            # Only restore if session is recent (within 1 hour)
            if session_data.get('session_start'):
                session_start = datetime.fromisoformat(session_data['session_start'])
                age = datetime.now() - session_start

                if age.total_seconds() < 3600:  # 1 hour
                    self.is_active = session_data.get('active', False)
                    self.authenticated_user = session_data.get('user')
                    self.session_start = session_start
                    self.command_count = session_data.get('command_count', 0)

                    self._log(f"Session restored: {self.authenticated_user} (age: {age})")
                else:
                    # Session too old, clear it
                    self.session_file.unlink()
        except Exception as e:
            print(f"⚠️ Failed to load session: {e}")


# Global instance
_dev_mode_manager = None


def get_dev_mode_manager(config_manager=None) -> DevModeManager:
    """
    Get or create global DevModeManager instance.

    Args:
        config_manager: ConfigManager instance (required for first call)

    Returns:
        Global DevModeManager instance
    """
    global _dev_mode_manager

    if _dev_mode_manager is None:
        _dev_mode_manager = DevModeManager(config_manager=config_manager)

    return _dev_mode_manager


def reset_dev_mode_manager():
    """Reset global DevModeManager instance (for testing)."""
    global _dev_mode_manager
    _dev_mode_manager = None
