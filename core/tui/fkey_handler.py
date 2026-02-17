"""
Function Key Handler for uCLI

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
import threading
import json
from pathlib import Path
from typing import Dict, Callable, Optional, List
from datetime import datetime
from enum import Enum

from core.services.logging_api import get_repo_root
from core.tui.ui_elements import Spinner, ProgressBar
from core.utils.tty import parse_special_key, normalize_terminal_input


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
    """Handler for function key shortcuts in uCLI."""

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

    def _progress_line(self, phase: str, label: str, percent: int) -> None:
        """Render consistent progress output for long-running F-key actions."""
        pct = max(0, min(100, int(percent)))
        bar = ProgressBar(total=100, width=24).render(pct, label=phase.upper())
        print(f"{bar}  {label}")

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
        key_code = normalize_terminal_input(key_code)

        # Try shared parser first (includes OS/env-aware mapping + self-heal).
        parsed = parse_special_key(key_code)
        if parsed and parsed.startswith("F"):
            return parsed

        # Try direct mapping
        for fkey in FunctionKeyCode:
            if key_code == fkey.value:
                return fkey.name

        # Additional terminal variants (xterm/rxvt) + Meta-digit aliases.
        alias_map = {
            "\x1b[OP": "F1",
            "\x1b[OQ": "F2",
            "\x1b[OR": "F3",
            "\x1b[OS": "F4",
            "\x1b[11~": "F1",
            "\x1b[12~": "F2",
            "\x1b[13~": "F3",
            "\x1b[14~": "F4",
            "\x1b[[A": "F1",
            "\x1b[[B": "F2",
            "\x1b[[C": "F3",
            "\x1b[[D": "F4",
            "\x1b1": "F1",
            "\x1b2": "F2",
            "\x1b3": "F3",
            "\x1b4": "F4",
            "\x1b5": "F5",
            "\x1b6": "F6",
            "\x1b7": "F7",
            "\x1b8": "F8",
        }
        if key_code in alias_map:
            return alias_map[key_code]

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
            "output": f"OK File created: {filepath}\nTo edit: EDIT {filename}",
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
            ("@vault", "memory/vault", "Primary knowledge store"),
            ("@shared", "memory/sharing", "Shared with others"),
            ("@knowledge", "knowledge", "Knowledge bank"),
            ("@dev", "dev", "Development area (admin only)"),
        ]

        print("\nAvailable Workspaces:")
        for idx, (name, path, desc) in enumerate(workspaces, 1):
            print(f"  {idx}. {name:15} -> {path:30} ({desc})")

        choice = self.prompt.ask_menu_choice("Select workspace", num_options=len(workspaces))
        if not choice:
            return {"status": "cancelled"}

        name, path, _ = workspaces[choice - 1]
        return {
            "status": "success",
            "message": f"Selected workspace: {name}",
            "output": f"Workspace: {name}\nPath: {path}",
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
        base_url, dashboard_url = self._wizard_urls()
        menu_options = [
            "Start Wizard Server",
            "Stop Wizard Server",
            "Show Server Status",
            f"Open Dashboard ({dashboard_url})",
            "View Server Logs",
        ]

        print("\nWizard Server Management:")
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
            host, port = self._wizard_host_port()
            connect_host = self._wizard_connect_host(host)
            base_url, dashboard_url = self._wizard_urls()
            # Check if already running
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((connect_host, port))
            sock.close()

            if result == 0:
                return {
                    "status": "info",
                    "message": "Wizard server is already running",
                    "output": f"OK Wizard is running on {base_url}",
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
            stop = threading.Event()
            spinner = Spinner(label="Starting Wizard", show_elapsed=False)
            thread = spinner.start_background(stop)
            self._progress_line("loading", "Wizard startup", 0)
            time.sleep(2)
            stop.set()
            thread.join(timeout=1)
            spinner.stop("Wizard start complete")
            self._progress_line("loading", "Wizard startup complete", 100)

            # Open dashboard
            webbrowser.open(dashboard_url)

            return {
                "status": "success",
                "message": "Wizard server started",
                "output": f"OK Wizard started on {base_url}\nDashboard opening in browser...",
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
            host, port = self._wizard_host_port()
            connect_host = self._wizard_connect_host(host)
            base_url, _ = self._wizard_urls()
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((connect_host, port))
            sock.close()

            if result == 0:
                return {
                    "status": "success",
                    "message": "Wizard is running",
                    "output": f"Wizard Server Status:\n  {base_url}\n  Status: RUNNING (OK)",
                }
            else:
                return {
                    "status": "warning",
                    "message": "Wizard is not running",
                    "output": "Wizard Server Status:\n  Status: STOPPED\n  Run: WIZARD start",
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not check status: {e}",
            }

    def _open_dashboard(self) -> Dict:
        """Open Wizard dashboard in browser."""
        try:
            _, dashboard_url = self._wizard_urls()
            webbrowser.open(dashboard_url)
            return {
                "status": "success",
                "message": "Opening Wizard dashboard...",
                "output": f"Opening {dashboard_url} in default browser...",
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
                    "output": "WARN Wizard log file not found",
                }

            # Show last 20 lines
            with open(log_file, "r") as f:
                lines = f.readlines()[-20:]

            output = "Wizard Server Logs (last 20 lines):\n"
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

    def _wizard_host_port(self) -> tuple:
        host = "127.0.0.1"
        port = 8765
        try:
            config_path = self.repo_root / "wizard" / "config" / "wizard.json"
            if config_path.exists():
                data = json.loads(config_path.read_text())
                if isinstance(data, dict):
                    raw_port = data.get("port")
                    if isinstance(raw_port, int):
                        port = raw_port
                    elif isinstance(raw_port, str) and raw_port.isdigit():
                        port = int(raw_port)
                    raw_host = data.get("host")
                    if isinstance(raw_host, str) and raw_host.strip():
                        host = raw_host.strip()
        except Exception:
            pass
        return host, port

    def _wizard_connect_host(self, host: str) -> str:
        if host in {"0.0.0.0", "::"}:
            return "127.0.0.1"
        return host

    def _wizard_urls(self) -> tuple:
        host, port = self._wizard_host_port()
        connect_host = self._wizard_connect_host(host)
        base_url = f"http://{connect_host}:{port}"
        dashboard_url = f"{base_url}/dashboard"
        return base_url, dashboard_url

    # Repo root is resolved from UDOS_ROOT via logging_api.get_repo_root()
