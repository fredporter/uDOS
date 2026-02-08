"""
Function Key Handler for uCODE TUI

Maps F1-F8 to common operations:
- F1: Create new Markdown file
- F2: Open TUI file picker
- F3: Select workspace folder
- F4: Open binder
- F5: Show workflows
- F6: TUI settings/status
- F7: Display function key map
- F8: Manage wizard server and open dashboard

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""

import sys
import os
import subprocess
import webbrowser
import time
from pathlib import Path
from typing import Dict, Callable, Optional, List
from datetime import datetime
from enum import Enum

from core.services.logging_api import get_repo_root


class FunctionKeyCode(Enum):
    """Function key codes for different terminals."""
    # Standard escape sequences for function keys
    F1 = "\x1bOP"
    F2 = "\x1bOQ"
    F3 = "\x1bOR"
    F4 = "\x1bOS"
    F5 = "\x1b[15~"
    F6 = "\x1b[17~"
    F7 = "\x1b[18~"
    F8 = "\x1b[19~"


class FKeyHandler:
    """Handler for function key shortcuts in uCODE TUI."""

    def __init__(self, dispatcher=None, prompt=None, game_state=None):
        """
        Initialize function key handler.

        Args:
            dispatcher: CommandDispatcher instance
            prompt: Prompt instance for user interaction
            game_state: Shared GameState instance
        """
        self.dispatcher = dispatcher
        self.prompt = prompt
        self.game_state = game_state
        self.repo_root = get_repo_root()
        self.handlers = {
            "F1": self._handle_new_file,
            "F2": self._handle_file_picker,
            "F3": self._handle_select_workspace,
            "F4": self._handle_binder,
            "F5": self._handle_workflows,
            "F6": self._handle_settings,
            "F7": self._handle_fkey_help,
            "F8": self._handle_wizard,
        }

    def handle_key(self, key_code: str) -> Optional[Dict]:
        """
        Handle a function key press.

        Args:
            key_code: Raw key code from terminal

        Returns:
            Result dict from handler, or None if not a function key
        """
        # Convert escape sequence to F-key name
        fkey = self._parse_key_code(key_code)
        if not fkey:
            return None

        # Dispatch to appropriate handler
        handler = self.handlers.get(fkey)
        if handler:
            try:
                return handler()
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"F-key handler error: {e}",
                }

        return None

    def _parse_key_code(self, key_code: str) -> Optional[str]:
        """
        Parse escape sequence to F-key name.

        Args:
            key_code: Raw escape sequence

        Returns:
            F-key name (F1-F8) or None
        """
        # Try direct mapping
        for fkey in FunctionKeyCode:
            if key_code == fkey.value:
                return fkey.name

        # Try numeric parsing for F5-F8 variants
        if key_code.startswith("\x1b["):
            if "~" in key_code:
                try:
                    num = int(key_code[2:-1])
                    # F5=15, F6=17, F7=18, F8=19
                    fkey_map = {15: "F5", 17: "F6", 18: "F7", 19: "F8"}
                    return fkey_map.get(num)
                except ValueError:
                    pass

        return None

    def _handle_new_file(self) -> Dict:
        """F1: Create new Markdown file."""
        if not self.prompt:
            return {
                "status": "error",
                "message": "Prompt not available",
            }

        filename = self.prompt.ask("New file name (without .md): ")
        if not filename:
            return {"status": "cancelled", "message": "Cancelled"}

        # Create in memory/sandbox by default
        target_dir = self.repo_root / "memory" / "sandbox"
        target_dir.mkdir(parents=True, exist_ok=True)
        filepath = target_dir / f"{filename}.md"

        # Check if exists
        if filepath.exists():
            return {
                "status": "error",
                "message": f"File already exists: {filepath}",
            }

        # Create with template
        template = f"""---
title: {filename}
created: {datetime.now().isoformat()}
tags: [sandbox, draft]
---

# {filename}

Write your content here...
"""

        with open(filepath, "w") as f:
            f.write(template)

        return {
            "status": "success",
            "message": f"Created: {filepath}",
            "output": f"✅ File created: {filepath}\n\nTo edit: EDIT {filename}",
        }

    def _handle_file_picker(self) -> Dict:
        """F2: Open TUI file picker."""
        # Route to file picker command
        if self.dispatcher:
            return self.dispatcher.dispatch("FILEPICKER", game_state=self.game_state)
        else:
            return {
                "status": "error",
                "message": "Dispatcher not available",
            }

    def _handle_select_workspace(self) -> Dict:
        """F3: Select workspace folder."""
        if not self.prompt:
            return {
                "status": "error",
                "message": "Prompt not available",
            }

        # List available workspaces
        workspaces = [
            ("@sandbox", "memory/sandbox", "User test area"),
            ("@bank", "memory/bank", "Saved data"),
            ("@shared", "memory/shared", "Shared with others"),
            ("@knowledge", "knowledge", "Knowledge bank"),
            ("@dev", "dev", "Development area (admin only)"),
        ]

        print("\n📂 Available Workspaces:")
        for idx, (name, path, desc) in enumerate(workspaces, 1):
            print(f"  {idx}. {name:15} -> {path:30} ({desc})")

        choice = self.prompt.ask_menu_choice("Select workspace", num_options=len(workspaces))
        if not choice:
            return {"status": "cancelled"}

        name, path, _ = workspaces[choice - 1]
        return {
            "status": "success",
            "message": f"Selected workspace: {name}",
            "output": f"📂 Workspace: {name}\n   Path: {path}",
            "workspace": name,
        }

    def _handle_binder(self) -> Dict:
        """F4: Open binder."""
        if self.dispatcher:
            return self.dispatcher.dispatch("BINDER list", game_state=self.game_state)
        else:
            return {
                "status": "error",
                "message": "Dispatcher not available",
            }

    def _handle_workflows(self) -> Dict:
        """F5: Show workflows."""
        if self.dispatcher:
            return self.dispatcher.dispatch("WORKFLOW list", game_state=self.game_state)
        else:
            return {
                "status": "error",
                "message": "Dispatcher not available",
            }

    def _handle_settings(self) -> Dict:
        """F6: TUI settings and status."""
        if self.dispatcher:
            return self.dispatcher.dispatch("SETUP", game_state=self.game_state)
        else:
            return {
                "status": "error",
                "message": "Dispatcher not available",
            }

    def _handle_fkey_help(self) -> Dict:
        """F7: Display function key map."""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║                    Function Key Reference                      ║
╚════════════════════════════════════════════════════════════════╝

F1  New File          Create a new Markdown file in @sandbox
F2  File Picker       Open the TUI file picker/browser
F3  Workspace         Select and switch workspace folder
F4  Binder            Open/manage multi-chapter documents
F5  Workflows         List and manage automation workflows
F6  Settings          Show TUI settings and system status
F7  Fkey Help         Display this function key reference
F8  Wizard            Manage Wizard server (start/stop/dashboard)

═══════════════════════════════════════════════════════════════════
Tips:
  • Press F6 to see system status and server health
  • Press F8 to start Wizard and open the web dashboard
  • Press F3 to change your active workspace
  • Type HELP at any time for command reference
═══════════════════════════════════════════════════════════════════
"""
        return {
            "status": "success",
            "message": "Function Key Reference",
            "output": help_text,
        }

    def _handle_wizard(self) -> Dict:
        """F8: Manage Wizard server and dashboard."""
        menu_options = [
            "Start Wizard Server",
            "Stop Wizard Server",
            "Show Server Status",
            "Open Dashboard (http://localhost:8765)",
            "View Server Logs",
        ]

        print("\n🧙 Wizard Server Management:")
        for idx, option in enumerate(menu_options, 1):
            print(f"  {idx}. {option}")

        if not self.prompt:
            return {
                "status": "error",
                "message": "Prompt not available",
            }

        choice = self.prompt.ask_menu_choice("Select option", num_options=len(menu_options))
        if not choice:
            return {"status": "cancelled"}

        if choice == 1:
            return self._start_wizard()
        elif choice == 2:
            return self._stop_wizard()
        elif choice == 3:
            return self._wizard_status()
        elif choice == 4:
            return self._open_dashboard()
        elif choice == 5:
            return self._wizard_logs()

        return {"status": "cancelled"}

    def _start_wizard(self) -> Dict:
        """Start Wizard server."""
        try:
            # Check if already running
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("localhost", 8765))
            sock.close()

            if result == 0:
                return {
                    "status": "info",
                    "message": "Wizard server is already running",
                    "output": "✅ Wizard is running on http://localhost:8765",
                }

            # Start wizard
            wizard_dir = self.repo_root / "wizard"
            if not wizard_dir.exists():
                return {
                    "status": "error",
                    "message": "Wizard not found",
                }

            # Start in background
            import subprocess
            subprocess.Popen(
                [sys.executable, "-m", "wizard.server", "--no-interactive"],
                cwd=self.repo_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Give it time to start
            time.sleep(2)

            # Open dashboard
            webbrowser.open("http://localhost:8765")

            return {
                "status": "success",
                "message": "Wizard server started",
                "output": "✅ Wizard started on http://localhost:8765\n📊 Dashboard opening in browser...",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not start Wizard: {e}",
            }

    def _stop_wizard(self) -> Dict:
        """Stop Wizard server."""
        try:
            # This would require a control endpoint
            return {
                "status": "info",
                "message": "Use WIZARD stop command to stop server",
                "help": "Type: WIZARD stop",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not stop Wizard: {e}",
            }

    def _wizard_status(self) -> Dict:
        """Check Wizard server status."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("localhost", 8765))
            sock.close()

            if result == 0:
                return {
                    "status": "success",
                    "message": "Wizard is running",
                    "output": "🟢 Wizard Server Status:\n   http://localhost:8765\n   Status: RUNNING ✅",
                }
            else:
                return {
                    "status": "warning",
                    "message": "Wizard is not running",
                    "output": "🔴 Wizard Server Status:\n   Status: STOPPED\n   Run: WIZARD start",
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not check status: {e}",
            }

    def _open_dashboard(self) -> Dict:
        """Open Wizard dashboard in browser."""
        try:
            webbrowser.open("http://localhost:8765")
            return {
                "status": "success",
                "message": "Opening Wizard dashboard...",
                "output": "📊 Opening http://localhost:8765 in default browser...",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not open dashboard: {e}",
            }

    def _wizard_logs(self) -> Dict:
        """Show Wizard server logs."""
        try:
            log_file = self.repo_root / "memory" / "logs" / "wizard.log"
            if not log_file.exists():
                return {
                    "status": "warning",
                    "message": "No logs found",
                    "output": "⚠️  Wizard log file not found",
                }

            # Show last 20 lines
            with open(log_file, "r") as f:
                lines = f.readlines()[-20:]

            output = "📋 Wizard Server Logs (last 20 lines):\n\n"
            output += "".join(lines)

            return {
                "status": "success",
                "message": "Wizard logs",
                "output": output,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not read logs: {e}",
            }

    # Repo root is resolved from UDOS_ROOT via logging_api.get_repo_root()
