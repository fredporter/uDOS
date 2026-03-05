"""
Function Key Handler for uCODE

Maps F1-F10 to system-level teletext actions:
- F1: Help
- F2: System status
- F3: Logs
- F4: Extensions
- F5: Refresh
- F6: Toggle panels
- F7: Missions
- F8: Environment
- F9: Settings
- F10: Exit

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""

import os
import socket
import webbrowser
import json
from pathlib import Path
from typing import Dict, Callable, Optional, List
from datetime import datetime
from enum import Enum

from core.services.logging_api import get_repo_root
from core.services.background_service_manager import get_wizard_process_manager
from core.services.loopback_host_utils import is_loopback_host, normalize_loopback_host
from core.tui.ui_elements import ProgressBar
from core.input.keymap import decode_key_input
from core.utils.tty import normalize_terminal_input


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
    F9 = "\x1b[20~"
    F10 = "\x1b[21~"


class FKeyHandler:
    """Handler for function key shortcuts in uCODE."""

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
            "F1": self._handle_help,
            "F2": self._handle_system_status,
            "F3": self._handle_logs,
            "F4": self._handle_extensions,
            "F5": self._handle_refresh,
            "F6": self._handle_toggle_panels,
            "F7": self._handle_missions,
            "F8": self._handle_environment,
            "F9": self._handle_settings,
            "F10": self._handle_exit,
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
            F-key name (F1-F10) or None
        """
        key_code = normalize_terminal_input(key_code)

        # Try shared parser first (includes OS/env-aware mapping + self-heal).
        decoded = decode_key_input(key_code, env=os.environ)
        if decoded.action.startswith("FKEY_"):
            return f"F{decoded.action.split('_', 1)[1]}"

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
            "\x1b9": "F9",
            "\x1b0": "F10",
        }
        if key_code in alias_map:
            return alias_map[key_code]

        # Try numeric parsing for F5-F10 variants
        if key_code.startswith("\x1b["):
            if "~" in key_code:
                try:
                    num = int(key_code[2:-1])
                    # F5=15, F6=17, F7=18, F8=19, F9=20, F10=21
                    fkey_map = {15: "F5", 17: "F6", 18: "F7", 19: "F8", 20: "F9", 21: "F10"}
                    return fkey_map.get(num)
                except ValueError:
                    pass

        return None

    def _dispatch_or_notice(self, command: str, label: str) -> Dict:
        """Dispatch a command when available, otherwise return a visible notice."""
        if self.dispatcher:
            try:
                return self.dispatcher.dispatch(command, game_state=self.game_state)
            except Exception as exc:
                return {"status": "error", "message": f"{label} failed: {exc}"}
        return {"status": "ok", "message": f"{label}: {command}"}

    def _handle_help(self) -> Dict:
        """F1: Help."""
        return self._dispatch_or_notice("HELP", "Help")

    def _handle_system_status(self) -> Dict:
        """F2: System status."""
        return self._dispatch_or_notice("STATUS", "System status")

    def _handle_logs(self) -> Dict:
        """F3: Logs."""
        return self._dispatch_or_notice("WIZARD logs", "Logs")

    def _handle_extensions(self) -> Dict:
        """F4: Extensions."""
        return self._dispatch_or_notice("UCODE EXTENSION LIST", "Extensions")

    def _handle_refresh(self) -> Dict:
        """F5: Refresh current surface."""
        return self._dispatch_or_notice("STATUS", "Refresh")

    def _handle_toggle_panels(self) -> Dict:
        """F6: Toggle panel layout."""
        return {
            "status": "success",
            "message": "Toggle panels requested",
            "output": "Panels toggle action acknowledged.",
        }

    def _handle_missions(self) -> Dict:
        """F7: Missions."""
        return self._dispatch_or_notice("MISSION LIST", "Missions")

    def _handle_environment(self) -> Dict:
        """F8: Environment."""
        return self._dispatch_or_notice("UCODE ENV", "Environment")

    def _handle_settings(self) -> Dict:
        """F9: Settings."""
        return self._dispatch_or_notice("SETUP", "Settings")

    def _handle_exit(self) -> Dict:
        """F10: Exit."""
        return {"status": "exit", "message": "Exit requested via F10", "output": "Exit requested (F10)."}

    def _handle_fkey_help(self) -> Dict:
        """Display function key map."""
        help_text = """
┌──────────────────────────────────────────────────────────────┐
│ uDOS Teletext Function Keys                                 │
├──────────────────────────────────────────────────────────────┤
│ F1   Help            F6   Toggle panels                     │
│ F2   System status   F7   Missions                          │
│ F3   Logs            F8   Environment                       │
│ F4   Extensions      F9   Settings                          │
│ F5   Refresh         F10  Exit                              │
└──────────────────────────────────────────────────────────────┘
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
            base_url, dashboard_url = self._wizard_urls()
            manager = get_wizard_process_manager()
            before = manager.status(base_url=base_url)
            status = manager.ensure_running(base_url=base_url, wait_seconds=45)
            if not status.connected:
                return {
                    "status": "error",
                    "message": f"Wizard unavailable ({status.message})",
                    "output": "Wizard failed to start. Check memory/logs/wizard-daemon.log",
                }

            webbrowser.open(dashboard_url)
            verb = "already running" if before.connected else "started"
            return {
                "status": "success",
                "message": f"Wizard server {verb}",
                "output": f"OK Wizard {verb} on {base_url}\nDashboard opening in browser...",
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
            if self._is_wizard_port_open(connect_host, port):
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
        normalized = normalize_loopback_host(host, fallback="127.0.0.1")
        if is_loopback_host(normalized):
            return normalized
        return "127.0.0.1"

    @staticmethod
    def _is_wizard_port_open(host: str, port: int) -> bool:
        """Probe wizard TCP port using a short timeout."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            return sock.connect_ex((host, port)) == 0
        finally:
            sock.close()

    def _wizard_urls(self) -> tuple:
        host, port = self._wizard_host_port()
        connect_host = self._wizard_connect_host(host)
        base_url = f"http://{connect_host}:{port}"
        dashboard_url = f"{base_url}/dashboard"
        return base_url, dashboard_url

    # Repo root is resolved from UDOS_ROOT via logging_api.get_repo_root()
