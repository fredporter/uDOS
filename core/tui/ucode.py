"""
uCODE - Unified Terminal TUI
=============================

The pivotal single-entry-point Terminal TUI for uDOS.

Features:
- Auto-detects available components (core, wizard, extensions)
- Graceful fallback to core-only mode if components are missing
- Integrated Wizard server control (start/stop/status)
- Extension/plugin distribution (via Wizard)
- Core command dispatch with context-aware pages
- Dynamic capability loading based on available folders

Architecture:
  1. On startup, detect available components
  2. Build capability registry dynamically
  3. Expose only commands/pages for what's present
  4. If wizard exists, allow server control + Wizard pages
  5. Plugin management is routed through Wizard distribution tooling
  6. Fallback gracefully to core-only mode

Commands:
  STATUS          - System status and component detection
  HELP            - Show available commands
  WIZARD [cmd]    - Wizard server control (if available)
  + Core commands (routed to dispatcher)

Version: v1.0.0 (uCODE Unified)
Status: Production
Date: 2026-01-28
"""

import sys
import os
import json
import logging
import subprocess
import threading
import time
import warnings
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.tui.dispatcher import CommandDispatcher
from core.tui.renderer import GridRenderer
from core.tui.state import GameState
from core.tui.fkey_handler import FKeyHandler
from core.tui.status_bar import TUIStatusBar
from core.ui.command_selector import CommandSelector
from core.input import SmartPrompt, EnhancedPrompt, ContextualCommandPrompt, create_default_registry
from core.services.health_training import read_last_summary
from core.services.hotkey_map import write_hotkey_payload
from core.services.theme_service import get_theme_service
from core.services.logging_api import get_logger
from core.services.memory_test_scheduler import MemoryTestScheduler
from core.services.self_healer import collect_self_heal_summary
from core.services.prompt_parser_service import get_prompt_parser_service
from core.services.todo_reminder_service import get_reminder_service
from core.services.todo_service import (
    CalendarGridRenderer as TodoCalendarGridRenderer,
    GanttGridRenderer as TodoGanttGridRenderer,
    get_service as get_todo_manager,
)
from core.tui.advanced_form_handler import AdvancedFormField
from core.services.system_script_runner import SystemScriptRunner
from wizard.services.monitoring_manager import MonitoringManager


def get_repo_root() -> Path:
    """Get uDOS repository root."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / "core" / "tui").exists() and (current / "wizard").exists():
            return current
        current = current.parent
    # Fallback: current working directory
    return Path.cwd()


class ComponentState(Enum):
    """Component availability state."""
    AVAILABLE = "available"
    MISSING = "missing"
    ERROR = "error"


@dataclass
class Component:
    """Component registration."""
    name: str
    path: Path
    state: ComponentState
    version: Optional[str] = None
    description: str = ""


class ComponentDetector:
    """Detect and validate available components."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.logger = get_logger("core", category="ucode-detector", name="ucode")
        self.components: Dict[str, Component] = {}

    def detect_all(self) -> Dict[str, Component]:
        """Detect all available components."""
        self.components = {
            "core": self._detect_core(),
            "wizard": self._detect_wizard(),
            "extensions": self._detect_extensions(),
            "app": self._detect_app(),
        }
        return self.components

    def _detect_core(self) -> Component:
        """Detect core component."""
        path = self.repo_root / "core"
        if path.exists() and (path / "__init__.py").exists():
            version = self._get_version(path / "version.json")
            return Component(
                name="core",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Core TUI runtime"
            )
        return Component(
            name="core",
            path=path,
            state=ComponentState.MISSING,
            description="Core TUI runtime (missing)"
        )

    def _detect_wizard(self) -> Component:
        """Detect Wizard server component."""
        path = self.repo_root / "wizard"
        if path.exists() and (path / "server.py").exists():
            version = self._get_version(path / "version.json")
            return Component(
                name="wizard",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Wizard server & services"
            )
        return Component(
            name="wizard",
            path=path,
            state=ComponentState.MISSING,
            description="Wizard server (not installed)"
        )

    def _detect_extensions(self) -> Component:
        """Detect extensions component."""
        path = self.repo_root / "extensions"
        plugin_repo_path = self.repo_root / "wizard" / "distribution" / "plugins"
        has_extension_dirs = path.exists() and (
            (path / "api").exists() or (path / "transport").exists()
        )
        has_plugin_catalog = plugin_repo_path.exists()

        if has_extension_dirs or has_plugin_catalog:
            version = self._get_version(path / "version.json")
            if not version:
                wizard_version = self._get_version(self.repo_root / "wizard" / "version.json")
                version = wizard_version or "0.0.0"
            return Component(
                name="extensions",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Extensions + Wizard plugin catalog"
            )
        return Component(
            name="extensions",
            path=path,
            state=ComponentState.MISSING,
            description="Extensions system (not installed)"
        )

    def _detect_app(self) -> Component:
        """Detect app component."""
        path = self.repo_root / "app"
        if path.exists() and (path / "package.json").exists():
            version = self._get_version(path / "version.json")
            return Component(
                name="app",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Desktop GUI application"
            )
        return Component(
            name="app",
            path=path,
            state=ComponentState.MISSING,
            description="Desktop app (not installed)"
        )

    def _get_version(self, version_file: Path) -> Optional[str]:
        """Read version from component's version.json."""
        try:
            if version_file.exists():
                with open(version_file) as f:
                    data = json.load(f)
                    return data.get("display") or data.get("version")
        except Exception as e:
            self.logger.debug(f"Failed to read version from {version_file}: {e}")
        return None

    def is_available(self, component_name: str) -> bool:
        """Check if component is available."""
        comp = self.components.get(component_name)
        return comp and comp.state == ComponentState.AVAILABLE


class uCODETUI:
    """Unified Terminal TUI for uDOS."""

    def __init__(self):
        """Initialize uCODE TUI."""
        self.repo_root = get_repo_root()
        self.logger = get_logger("core", category="ucode-tui", name="ucode")
        self.quiet = os.getenv("UDOS_QUIET", "").strip() in ("1", "true", "yes")
        self.ucode_version = os.getenv("UCODE_VERSION", "1.0.1")
        self.running = False
        self.ghost_mode = False
        # Ensure system seeds are present (startup/reboot/setup stories)
        self._ensure_system_seeds()
        # Component detection
        self.detector = ComponentDetector(self.repo_root)
        self.components = self.detector.detect_all()
        self.ai_modes_config = self._load_ai_modes_config()

        # Core components (always available)
        self.dispatcher = CommandDispatcher()
        self.renderer = GridRenderer()
        self.renderer.set_mood("idle", pace=0.7, blink=True)
        self.state = GameState()

        # Create command registry and contextual prompt (Phase 1)
        self.command_registry = create_default_registry()
        self.prompt = ContextualCommandPrompt(registry=self.command_registry)

        # Command selector (Phase 3)
        self.command_selector = CommandSelector(self.command_registry)
        self.prompt.set_tab_handler(self._open_command_selector)

        # Function key handler
        self.fkey_handler = FKeyHandler(
            dispatcher=self.dispatcher,
            prompt=self.prompt,
            game_state=self.state,
        )
        self.prompt.set_function_key_handler(self.fkey_handler)
        self.status_bar = TUIStatusBar()

        # Command registry (maps commands to methods)
        self.commands = {
            "STATUS": self._cmd_status,
            "HELP": self._cmd_help,
            "LOCAL": self._cmd_ok_local,
            "VIBE": self._cmd_ok_local,
            "EXPLAIN": self._cmd_ok_explain,
            "DIFF": self._cmd_ok_diff,
            "PATCH": self._cmd_ok_patch,
            "EXIT": self._cmd_exit,
        }

        # Conditional commands
        # WIZARD command now handled by dispatcher (WizardHandler)

        self.health_log_path = self.repo_root / "memory" / "logs" / "health-training.log"
        self.health_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.self_heal_summary: Optional[Dict[str, Any]] = None
        self.hot_reload_mgr = None
        self.hot_reload_stats: Optional[Dict[str, Any]] = None
        self.previous_health_log: Optional[Dict[str, Any]] = None
        self.ok_local_outputs: List[Dict[str, Any]] = []
        self.ok_local_counter = 0
        self.ok_local_limit = 50
        self._setup_health_monitoring()
        self.system_script_runner = SystemScriptRunner()
        self.memory_test_scheduler: Optional[MemoryTestScheduler] = None
        self.memory_test_summary: Optional[Dict[str, Any]] = None
        self.theme = get_theme_service()
        self.todo_manager = get_todo_manager()
        self.calendar_renderer = TodoCalendarGridRenderer()
        self.gantt_renderer = TodoGanttGridRenderer()
        self.prompt_parser = get_prompt_parser_service()
        self.todo_reminder = get_reminder_service(self.todo_manager)
        self._init_ok_prompt_context()

        if self.prompt.use_fallback:
            self.logger.info(f"[ContextualPrompt] Using fallback mode: {self.prompt.fallback_reason}")
        else:
            self.logger.info("[ContextualPrompt] Initialized with command suggestions")

    def _ensure_system_seeds(self) -> None:
        """Seed /memory/system files if they are missing."""
        try:
            from core.framework.seed_installer import SeedInstaller

            system_dir = self.repo_root / "memory" / "system"
            required = [
                "startup-script.md",
                "reboot-script.md",
                "tui-setup-story.md",
                "wizard-setup-story.md",
            ]
            missing = [name for name in required if not (system_dir / name).exists()]
            if missing:
                installer = SeedInstaller()
                installer.install_system_seeds(force=False)
                self.logger.info(
                    f"[LOCAL] Seeded memory/system files: {', '.join(missing)}"
                )
        except Exception as e:
            self.logger.warning(f"[LOCAL] System seed check failed: {e}")

    def _handle_special_commands(self, command: str) -> bool:
        """Handle special REPL commands (EXIT/STATUS/HISTORY)."""
        if not command:
            return False
        parts = command.strip().split(None, 1)
        cmd = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in self.commands:
            self.commands[cmd](args)
            return True

        if cmd == "HISTORY":
            self._show_history()
            return True

        return False

    def _show_history(self, limit: int = 10) -> None:
        """Print recent command history."""
        history = self.state.session_history[-limit:]
        if not history:
            print("No history yet.")
            return
        print("Recent history:")
        for entry in history:
            print(f"  {entry}")

    def _route_input(self, user_input: str) -> Dict[str, Any]:
        """
        Route input based on prefix: '?', 'OK', '/', or question mode.

        Returns:
            Dict with status, message, and routed result
        """
        user_input = user_input.strip()
        if not user_input:
            return {"status": "error", "message": "Empty input"}

        # Mode 1: Command mode (OK ... or ?...)
        is_ok = user_input.lower().startswith("ok ")
        if is_ok or user_input.startswith("?"):
            # Normalize ? to remove the marker and pass the rest as a normal command
            if user_input.startswith("?"):
                # Remove the ? and pass the rest to dispatcher
                normalized = user_input[1:].strip()
            else:
                # Remove "OK " prefix and pass the rest to dispatcher
                normalized = user_input[3:].strip()

                if normalized:
                    parts = normalized.split(None, 1)
                    cmd_name = parts[0].upper()
                    args = parts[1] if len(parts) > 1 else ""
                    if cmd_name in {"LOCAL", "VIBE", "EXPLAIN", "DIFF", "PATCH"}:
                        self.commands[cmd_name](args)
                        return {"status": "success", "command": cmd_name}
                    # Treat other OK input as a local prompt
                    self._run_ok_request(normalized, mode="LOCAL")
                    return {"status": "success", "command": "OK"}

            if normalized:
                parts = normalized.split(None, 1)
                cmd_name = parts[0].upper()
                args = parts[1] if len(parts) > 1 else ""
                if cmd_name in self.commands and cmd_name not in self.dispatcher.handlers:
                    self.commands[cmd_name](args)
                    return {"status": "success", "command": cmd_name}

            # Now route the normalized command to dispatcher
            return self.dispatcher.dispatch(normalized, parser=self.prompt, game_state=self.state)

        # Mode 2: Slash mode
        if user_input.startswith("/"):
            return self._handle_slash_input(user_input)

        # Mode 3: Question mode (natural language routing)
        return self._handle_question_mode(user_input)

    def _handle_slash_input(self, user_input: str) -> Dict[str, Any]:
        """
        Handle slash-prefixed input.

        If first token is a known slash command, route to uCODE.
        Otherwise, treat as shell command.
        """
        tokens = user_input[1:].strip().split(None, 1)  # Remove leading /
        if not tokens:
            return {"status": "error", "message": "Empty slash command"}

        first_token = tokens[0].lower()
        rest_of_line = tokens[1] if len(tokens) > 1 else ""

        # Known slash commands (from UCODE-PROMPT-SPEC.md)
        slash_commands = {
            "render": "RENDER",
            "help": "HELP",
            "whoami": "WHOAMI",
        }

        if first_token in slash_commands:
            # Route to uCODE command (without OK prefix)
            ucode_cmd = slash_commands[first_token]
            if rest_of_line:
                ucode_cmd += " " + rest_of_line
            return self.dispatcher.dispatch(ucode_cmd, parser=self.prompt, game_state=self.state)
        else:
            # Treat as shell command
            return self._execute_shell_command(user_input[1:].strip())

    def _execute_shell_command(self, shell_cmd: str) -> Dict[str, Any]:
        """
        Execute a shell command safely.

        Logs destructive patterns and requires confirmation.
        """
        # Log the command
        self.logger.info(f"[SHELL] {shell_cmd}")

        # Detect destructive patterns
        destructive_keywords = {"rm", "mv", ">", "|", "sudo", "rmdir", "dd", "format"}
        cmd_lower = shell_cmd.lower()

        if any(kw in cmd_lower for kw in destructive_keywords):
            # Ask for confirmation
            confirm = self.prompt.ask_yes_no(
                f"Destructive command detected: {shell_cmd}\nProceed?",
                default=False,
                variant="skip",
            )
            if not confirm:
                return {"status": "cancelled", "message": "Command cancelled by user"}

        try:
            result = subprocess.run(
                shell_cmd,
                shell=True,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout or result.stderr
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": output or "Command executed successfully",
                    "shell_output": output
                }
            else:
                return {
                    "status": "error",
                    "message": output or f"Command failed with exit code {result.returncode}",
                    "shell_output": output
                }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out (30s limit)"}
        except Exception as e:
            return {"status": "error", "message": f"Shell execution failed: {str(e)}"}


    def _handle_question_mode(self, user_input: str) -> Dict[str, Any]:
        """
        Handle question mode (natural language routing).

        Simple: Uppercase first word and dispatch as command.
        Complex sentences are treated as HELP queries.
        """
        words = user_input.strip().split(None, 1)
        if not words:
            return {"status": "error", "message": "Empty input"}

        first_word = words[0].upper()
        rest = words[1] if len(words) > 1 else ""

        # Map common commands (case insensitive shortcuts)
        cmd_map = {
            "HELP": "HELP",
            "H": "HELP",
            "?": "HELP",
            "STATUS": "STATUS",
            "STAT": "STATUS",
            "STATE": "STATUS",
            "WIZARD": "WIZARD",
            "CONFIG": "CONFIG",
            "SETUP": "SETUP",
            "FILE": "FILE",
            "NEW": "NEW",
            "EDIT": "EDIT",
            "MAP": "MAP",
            "FIND": "FIND",
            "SEARCH": "FIND",
            "LOGS": "LOGS",
            "BINDER": "BINDER",
            "STORY": "STORY",
            "RUN": "RUN",
            "REPAIR": "REPAIR",
            "SHAKEDOWN": "SHAKEDOWN",
        }

        # Try to resolve to known command
        cmd = cmd_map.get(first_word, first_word)

        # Build command with arguments
        full_cmd = f"{cmd} {rest}".strip()

        # Handle internal commands not in dispatcher
        if cmd in self.commands and cmd not in self.dispatcher.handlers:
            self.commands[cmd](rest)
            return {"status": "success", "command": cmd}

        # Dispatch the command
        return self.dispatcher.dispatch(full_cmd, parser=self.prompt, game_state=self.state)

    def run(self) -> None:
        """Start uCODE TUI."""
        self.running = True
        self._run_startup_script()
        self._show_banner()
        self._show_health_summary()
        self._show_ai_startup_sequence()
        self._show_startup_hints()

        # Check if in ghost mode and prompt for setup
        self._check_ghost_mode()
        self._show_first_run_ai_setup_hint()

        # Get current user role for status bar
        try:
            from core.services.user_service import get_current_user
            current_user = get_current_user()
            user_role = current_user.role.name.lower() if current_user else "ghost"
        except Exception:
            user_role = "ghost"

        try:
            while self.running:
                try:
                    # Use contextual command prompt with suggestions (Phase 1)
                    self._show_status_bar()
                    indicator = self.renderer.get_prompt_indicator()
                    user_input = self.prompt.ask_command(f"{indicator} ▶ ")

                    if not user_input:
                        continue

                    # Route input based on prefix (? / OK) or question mode
                    # This implements the uCODE Prompt Spec
                    result = self._route_input(user_input)

                    # Check for EXIT before processing
                    normalized_input = user_input.strip().upper()
                    if normalized_input in ("EXIT", "?EXIT", "? EXIT", "OK EXIT"):
                        self.running = False
                        print("👋 See you later!")
                        break

                    # Special handling for STORY and SETUP commands with forms
                    normalized_cmd = result.get("command", "").upper()
                    if normalized_cmd in ("STORY", "SETUP"):
                        # Check if this is a form-based story
                        if result.get("story_form"):
                            collected_data = self._handle_story_form(result["story_form"])

                            # Save collected data if this came from SETUP command
                            if normalized_cmd == "SETUP" and collected_data:
                                self._save_user_profile(collected_data)

                            print("\n✅ Setup form completed!")
                            print(f"\nCollected {len(collected_data)} values")
                            if collected_data:
                                print("\nData saved. Next steps:")
                                print("  SETUP --profile    - View your profile")
                                print("  CONFIG             - View variables")
                        else:
                            # Show the result for non-form stories
                            output = self.renderer.render(result)
                            print(output)
                    else:
                        # Render normal command output
                        output = self.renderer.render(result)
                        print(output)

                    self.state.update_from_handler(result)
                    self.logger.info(f"[COMMAND] {user_input} -> {result.get('status')}")
                    self.state.add_to_history(user_input)

                except KeyboardInterrupt:
                    print()
                    continue
                except Exception as e:
                    self.logger.error(f"[ERROR] {e}", exc_info=True)
                    print(f"ERROR: {e}")

        except KeyboardInterrupt:
            print("\nInterrupt. Type EXIT to quit.")
        except EOFError:
            self.running = False
        finally:
            self._cleanup()

    def _open_command_selector(self) -> Optional[str]:
        """Open TAB command selector and return selected command text."""
        try:
            return self.command_selector.pick()
        except Exception as exc:
            self.logger.error(f"[COMMAND_SELECTOR] Failed: {exc}")
            return None

    def _show_startup_hints(self) -> None:
        """Show startup hints once at beginning."""
        if self.quiet:
            return
        try:
            from core.services.vault_md_validator import validate_vault_md

            _, warnings = validate_vault_md()
            if warnings:
                print(self._theme_text("\n  ⚠ Vault-MD checks:"))
                for line in warnings:
                    print(self._theme_text(f"     - {line}"))
        except Exception:
            pass
        print(self._theme_text("\n  💡 Start with: SETUP (first-time) | HELP (all commands) | STORY tui-setup (quick setup)"))
        print(self._theme_text("     Or try: MAP | TELL location | GOTO location | WIZARD start"))
        print(self._theme_text("     Try: OK EXPLAIN <file> | OK LOCAL (local Vibe outputs)"))
        print(self._theme_text("     Press TAB for command selection | Type command for suggestions\n"))

    def _show_status_bar(self) -> None:
        """Render status bar line for the current session."""
        if self.quiet or not sys.stdout.isatty():
            return
        try:
            from core.services.user_service import get_user_manager, is_ghost_mode

            user = get_user_manager().current()
            user_role = user.role.value if user else "ghost"
            status_line = self.status_bar.get_status_line(
                user_role=user_role,
                ghost_mode=is_ghost_mode(),
            )
            print(self._theme_text(status_line))
        except Exception:
            pass

    def _show_first_run_ai_setup_hint(self) -> None:
        """Show a first-run hint for local AI setup."""
        try:
            if self.quiet:
                return
            # Only hint on first run: no identity configured yet.
            from core.services.config_sync_service import ConfigSyncManager

            identity = ConfigSyncManager().load_identity_from_env()
            if identity.get("user_username"):
                return
        except Exception:
            pass

        print(self._theme_text("\n🧠 First-Run AI Setup"))
        print(self._theme_text("  Run: SETUP  → add Mistral API key + local models"))
        print(self._theme_text("  Check: WIZARD status  (server)\n"))

    def _show_banner(self) -> None:
        """Show startup banner."""
        if self.quiet:
            return
        grid = self._build_startup_grid()
        print(self._theme_text(grid))

    def _build_startup_grid(self) -> str:
        """Build a 40x15 startup grid with ASCII art and color."""
        width = 40
        height = 15
        pattern = [".", ":"]
        grid = [
            [pattern[(r + c) % len(pattern)] for c in range(width)]
            for r in range(height)
        ]

        art = [
            " _   _  ____   ___  ____ ",
            "| | | |/ ___| / _ \\|  _ \\",
            "| |_| | |    | | | | | | |",
            "|  _  | |___ | |_| | |_| |",
            "|_| |_|\\____| \\___/|____/",
        ]

        start_row = 3
        start_col = (width - max(len(line) for line in art)) // 2
        for row_idx, line in enumerate(art):
            grid_row = start_row + row_idx
            if grid_row >= height:
                break
            for col_idx, ch in enumerate(line):
                if ch == " ":
                    continue
                col = start_col + col_idx
                if 0 <= col < width:
                    grid[grid_row][col] = ch

        version_line = f"uCODE v{self.ucode_version}"
        version_row = height - 3
        version_col = max(0, (width - len(version_line)) // 2)
        for idx, ch in enumerate(version_line):
            if version_col + idx < width:
                grid[version_row][version_col + idx] = ch

        hint = "Type HELP for commands"
        hint_row = height - 2
        hint_col = max(0, (width - len(hint)) // 2)
        for idx, ch in enumerate(hint):
            if hint_col + idx < width:
                grid[hint_row][hint_col + idx] = ch

        colors = [
            "\033[91m",
            "\033[93m",
            "\033[92m",
            "\033[96m",
            "\033[94m",
            "\033[95m",
        ]
        reset = "\033[0m"

        lines = []
        for row_idx, row in enumerate(grid):
            color = colors[row_idx % len(colors)]
            line = "".join(row)
            lines.append(f"{color}{line}{reset}")

        return "\n".join(lines)

    def _run_startup_script(self) -> None:
        """Execute the system startup script once per launch."""
        # Pre-flight check: Ensure TS runtime is built
        self._check_and_build_ts_runtime()

        result = self.system_script_runner.run_startup_script()
        if result.get("status") == "success":
            output = result.get("output")
            if output and not self.quiet:
                print(output)
        else:
            message = result.get("message")
            if message and not self.quiet:
                print(f"\n⚡ {message}")

    def _show_health_summary(self) -> None:
        """Show Self-Heal + Hot Reload overview (banner/log hook)."""
        if self.quiet:
            return
        if not self.self_heal_summary and not self.hot_reload_stats:
            return

        print("\n📊 System Health Training Summary")
        print("-" * 60)

        if self.self_heal_summary:
            success = self.self_heal_summary.get("success", False)
            status = "✅ Healthy" if success else "⚠️ Attention"
            issues = self.self_heal_summary.get("issues", 0)
            repaired = self.self_heal_summary.get("repaired", 0)
            remaining = self.self_heal_summary.get("remaining", 0)
            print(f"  Self-Heal: {status} | Issues: {issues} | Repaired: {repaired} | Remaining: {remaining}")

        if self.hot_reload_stats:
            enabled = "enabled" if self.hot_reload_stats.get("enabled") else "disabled"
            running = "running" if self.hot_reload_stats.get("running") else "stopped"
            reloads = self.hot_reload_stats.get("reload_count", 0)
            success_rate = self.hot_reload_stats.get("success_rate", 0.0)
            print(
                f"  Hot Reload: {enabled}, {running} | Reloads: {reloads} | Success: {success_rate:0.1f}%"
            )

        print(f"  Training log: {self.health_log_path}")

        prev_remaining = (self.previous_health_log or {}).get("self_heal", {}).get("remaining", 0)
        if prev_remaining > 0:
            print(f"  ⚠️ Last health log recorded {prev_remaining} remaining issues; automation will rerun diagnostics on drift.")

        if self.self_heal_summary and self.self_heal_summary.get("remaining", 0) > 0:
            print("  ⚠️ Automation will rerun REPAIR/SHAKEDOWN until remaining issues drop to zero.")

        if self.memory_test_summary:
            status = self.memory_test_summary.get("status", "idle")
            pending = self.memory_test_summary.get("pending", 0)
            result = self.memory_test_summary.get("result") or "pending"
            last_run_ts = self.memory_test_summary.get("last_run")
            last_run = (
                datetime.fromtimestamp(last_run_ts).isoformat()
                if isinstance(last_run_ts, (int, float)) and last_run_ts > 0
                else "never"
            )
            print(f"  Memory Tests: {status} | Result: {result} | Pending: {pending} | Last run: {last_run}")
            log_path = self.memory_test_summary.get("log_path")
            if log_path:
                print(f"    Logs: {log_path}")
            if status in ("scheduled", "running"):
                print("    ✅ Tests are running in the background as part of startup health checks.")

        print("-" * 60 + "\n")

        self._prompt_health_actions()

    def _prompt_health_actions(self) -> None:
        """Prompt for REPAIR/RESTORE/DESTROY when health checks report issues."""
        # Skip prompts for non-interactive or automation runs.
        if self.quiet or os.getenv("UDOS_AUTOMATION") == "1":
            return
        has_self_heal_issue = False
        has_test_failure = False

        if self.self_heal_summary:
            success = self.self_heal_summary.get("success", False)
            remaining = self.self_heal_summary.get("remaining", 0)
            if not success or remaining > 0:
                has_self_heal_issue = True

        if self.memory_test_summary:
            result = (self.memory_test_summary.get("result") or "").lower()
            if result in {"failed", "error"}:
                has_test_failure = True

        if not (has_self_heal_issue or has_test_failure):
            return

        try:
            choice = input(
                "Health check issues detected. Choose: REPAIR | RESTORE | DESTROY | SKIP: "
            ).strip().upper()
        except Exception:
            return

        if choice in {"", "SKIP"}:
            return

        if choice == "DESTROY":
            try:
                confirm = input("Type DESTROY to confirm reset: ").strip().upper()
            except Exception:
                return
            if confirm != "DESTROY":
                return

        if choice in {"REPAIR", "RESTORE", "DESTROY"}:
            self.dispatcher.dispatch(choice, parser=self.prompt, game_state=self.state)

    def _get_ai_modes_path(self) -> Path:
        """Return path to OK modes configuration."""
        return self.repo_root / "core" / "config" / "ok_modes.json"

    def _load_ai_modes_config(self) -> Dict[str, Any]:
        """Load OK modes configuration (safe fallback)."""
        path = self._get_ai_modes_path()
        if not path.exists():
            return {"modes": {}}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception as exc:
            self.logger.warning("[AI] Failed to load ok_modes.json: %s", exc)
            return {"modes": {}}

    def _get_ok_default_model(self) -> str:
        """Return the default local model for OK commands."""
        mode = (self.ai_modes_config.get("modes") or {}).get("ofvibe", {})
        default_models = mode.get("default_models") or {}
        model = default_models.get("core") or default_models.get("dev")
        try:
            from core.services.dev_state import get_dev_active

            if get_dev_active():
                model = default_models.get("dev") or model
        except Exception:
            if os.getenv("UDOS_DEV_MODE") in ("1", "true", "yes"):
                model = default_models.get("dev") or model
        return model or "devstral-small-2"

    def _get_ok_context_window(self) -> int:
        """Return the local Vibe context window size."""
        try:
            from wizard.services.vibe_service import VibeConfig

            return VibeConfig().context_window
        except Exception:
            return 8192

    def _get_ok_cloud_status(self) -> Dict[str, Any]:
        """Return Mistral cloud availability status."""
        try:
            from wizard.services.mistral_api import MistralAPI

            client = MistralAPI()
            if client.available():
                return {"ready": True, "issue": None}
            return {"ready": False, "issue": "mistral api key missing"}
        except Exception as exc:
            return {"ready": False, "issue": str(exc)}

    def _init_ok_prompt_context(self) -> None:
        """Expose OK local model info to the prompt toolbar."""
        try:
            self.prompt.ok_model = self._get_ok_default_model()
            self.prompt.ok_context_window = self._get_ok_context_window()
        except Exception as exc:
            self.logger.debug(f"[OK] Failed to set prompt context: {exc}")

    def _show_ai_startup_sequence(self) -> None:
        """Show Vibe startup summary if Vibe CLI is installed."""
        if self.quiet:
            return
        ok_status = self._get_ok_local_status()
        cloud_status = self._get_ok_cloud_status()
        model = ok_status.get("model") or self._get_ok_default_model()
        ctx = self._get_ok_context_window()

        lines = []
        if ok_status.get("ready"):
            lines.append(f"✅ Vibe ready ({model}, ctx {ctx})")
        else:
            issue = ok_status.get("issue") or "setup required"
            lines.append(f"⚠️ Vibe attention: {issue} ({model}, ctx {ctx})")
            if ok_status.get("ollama_endpoint"):
                lines.append(f"ℹ️  Ollama endpoint: {ok_status.get('ollama_endpoint')}")
            if issue == "ollama down":
                lines.append("💡 Start Ollama: `ollama serve`")
            if issue == "missing model":
                lines.append(f"💡 Pull model: `ollama pull {model}`")
            if issue == "vibe-cli missing":
                lines.append("💡 Install Vibe CLI: `pip install mistral-vibe`")
            if issue in {"setup required", "ollama down", "missing model", "vibe-cli missing"}:
                lines.append("💡 First run: SETUP to configure Mistral key + local models")
        if cloud_status.get("ready"):
            lines.append("✅ Mistral cloud ready (required)")
        else:
            issue = cloud_status.get("issue") or "setup required"
            lines.append(f"⚠️ Mistral cloud required: {issue}")
            lines.append("💡 Set MISTRAL_API_KEY or run SETUP")
        lines.append("Tip: OK EXPLAIN <file> | OK LOCAL")

        print(self._theme_text("\n🤖 Vibe (Local)"))
        self.renderer.stream_text("\n".join(lines), prefix="vibe> ")

    def _format_ai_status_line(self, label: str, status: Dict[str, Any]) -> str:
        """Format a single AI mode status line."""
        if status.get("ready"):
            return f"  ✅ {label}: ready"
        issues = status.get("issues") or []
        if issues:
            return f"  ⚠️ {label}: " + ", ".join(issues)
        return f"  ⚠️ {label}: setup required"

    def _fetch_ollama_models(self, endpoint: str) -> Dict[str, Any]:
        """Query Ollama tags endpoint."""
        url = endpoint.rstrip("/") + "/api/tags"
        try:
            with warnings.catch_warnings():
                try:
                    from urllib3.exceptions import NotOpenSSLWarning
                    warnings.simplefilter("ignore", NotOpenSSLWarning)
                except Exception:
                    pass
                response = requests.get(url, timeout=1.5)
            if response.status_code != 200:
                return {"reachable": False, "error": f"HTTP {response.status_code}"}
            data = response.json()
            models = [m.get("name") for m in data.get("models", []) if m.get("name")]
            return {"reachable": True, "models": models}
        except Exception as exc:
            return {"reachable": False, "error": str(exc)}

    def _get_ok_local_status(self) -> Dict[str, Any]:
        """Return OK local Vibe status (Ollama + model)."""
        mode = (self.ai_modes_config.get("modes") or {}).get("ofvibe", {})
        endpoint = mode.get("ollama_endpoint", "http://127.0.0.1:11434")
        model = self._get_ok_default_model()
        tags = self._fetch_ollama_models(endpoint)
        if not tags.get("reachable"):
            return {
                "ready": False,
                "issue": "ollama down",
                "model": model,
                "ollama_endpoint": endpoint,
                "detail": tags.get("error"),
            }
        models = tags.get("models") or []
        if model and model not in models:
            return {
                "ready": False,
                "issue": "missing model",
                "model": model,
                "ollama_endpoint": endpoint,
                "detail": None,
            }
        return {
            "ready": True,
            "issue": None,
            "model": model,
            "ollama_endpoint": endpoint,
            "detail": None,
        }

    def _setup_health_monitoring(self) -> None:
        """Initialize Self-Healer diagnostics + Hot Reload stats for automation."""
        self.previous_health_log = read_last_summary()
        self.self_heal_summary = self._run_self_healer()
        self.hot_reload_mgr = self._init_hot_reload_manager()
        self.hot_reload_stats = self.hot_reload_mgr.stats() if self.hot_reload_mgr else None
        self.memory_test_summary = self._schedule_memory_tests()
        self._log_health_training_summary()

    def _schedule_memory_tests(self) -> Dict[str, Any]:
        """Run memory/tests automation if new or modified files exist."""
        tests_root = self.repo_root / 'memory' / 'tests'
        try:
            scheduler = MemoryTestScheduler(self.repo_root, logger=self.logger)
            self.memory_test_scheduler = scheduler
            return scheduler.schedule()
        except Exception as exc:
            log_path = tests_root.parent / 'logs' / 'memory-tests.log'
            self.logger.warning("[MemoryTests] Scheduler unavailable: %s", exc)
            return {
                'status': 'error',
                'pending': 0,
                'last_run': None,
                'result': None,
                'log_path': str(log_path),
                'error': str(exc),
            }

    def _run_self_healer(self) -> Dict[str, Any]:
        """Run Self-Healer diagnostics (no auto repair) and summarise."""
        try:
            summary = collect_self_heal_summary(component="core", auto_repair=False)
            self.logger.info(f"[Self-Heal] {summary}")
            return summary
        except Exception as exc:
            self.logger.warning(f"[Self-Heal] Diagnostics unavailable: {exc}")
            return {"success": False, "error": str(exc)}

    def _init_hot_reload_manager(self):
        """Initialize global hot reload manager (stats only)."""
        try:
            from core.services.hot_reload import init_hot_reload

            manager = init_hot_reload(self.dispatcher, enabled=True)
            if manager:
                self.logger.info("[Hot Reload] Manager ready")
            return manager
        except Exception as exc:
            self.logger.warning(f"[Hot Reload] Manager not available: {exc}")
            return None

    def _log_health_training_summary(self) -> None:
        """Append health training summary to memory/logs/health-training.log."""
        try:
            memory_root = self.health_log_path.parent.parent
            hotkey_payload = write_hotkey_payload(memory_root)
            monitoring_summary = self._load_monitoring_summary(memory_root)
            notification_history = self._read_notification_history(memory_root)
            payload = {
                "timestamp": datetime.now().isoformat(),
                "self_heal": self.self_heal_summary or {},
                "hot_reload": self.hot_reload_stats or {},
                "hotkeys": hotkey_payload,
                "monitoring_summary": monitoring_summary,
                "notification_history": notification_history,
            }
            with open(self.health_log_path, "a") as log_file:
                log_file.write(json.dumps(payload) + "\n")
        except Exception as exc:
            self.logger.warning(f"[Health Log] Failed to write summary: {exc}")

    def _load_monitoring_summary(self, memory_root: Path) -> Dict[str, Any]:
        summary_path = memory_root / "monitoring" / "monitoring-summary.json"
        if summary_path.exists():
            try:
                return json.loads(summary_path.read_text())
            except Exception as exc:
                self.logger.warning("[Monitoring] Failed to read summary: %s", exc)
        monitoring = MonitoringManager(data_dir=memory_root / "monitoring")
        return monitoring.log_training_summary()

    def _check_and_build_ts_runtime(self) -> None:
        """Check if TS runtime is built, auto-build if missing (first-time setup)."""
        try:
            from core.services.ts_runtime_service import TSRuntimeService
            service = TSRuntimeService()

            # Check with auto_build=True to trigger automatic build if missing
            check_result = service._check_runtime_entry(auto_build=True)

            if check_result and check_result.get("status") == "error":
                # Auto-build failed or runtime still missing
                if not self.quiet:
                    print("\n⚠️  TypeScript Runtime Issue:")
                    print(f"   {check_result.get('message')}")
                    if check_result.get('details'):
                        print(f"   Details: {check_result.get('details')}")
                    if check_result.get('suggestion'):
                        print(f"   -> {check_result.get('suggestion')}")
                    print()
        except Exception as exc:
            self.logger.warning(f"[STARTUP] TS runtime check failed: {exc}")

    def _read_notification_history(self, memory_root: Path, limit: int = 5) -> list[Dict[str, Any]]:
        log_path = memory_root / "logs" / "notification-history.log"
        if not log_path.exists():
            return []
        try:
            lines = [line.strip() for line in log_path.read_text().splitlines() if line.strip()]
            recent = lines[-limit:]
            return [json.loads(line) for line in recent]
        except Exception as exc:
            self.logger.warning("[Notification] Failed to read history: %s", exc)
            return []

    def _ask_confirm(
        self,
        question: str,
        default: bool = True,
        help_text: str = None,
        context: str = None,
        variant: str = "ok",
    ) -> str:
        """Ask a standardized confirmation question and return the choice."""
        if hasattr(self.prompt, "ask_confirmation_choice"):
            return self.prompt.ask_confirmation_choice(
                question=question,
                default=default,
                help_text=help_text,
                context=context,
                variant=variant,
            )
        # Fallback to simple prompt
        response = input(f"{question}? ").strip().lower()
        return "yes" if response in {"y", "yes", "1", "ok"} else "no"

    def _ask_yes_no(self, question: str, default: bool = True, help_text: str = None, context: str = None) -> bool:
        """Ask a standardized [Yes|No|OK] question.

        Prompt format with 2-line context display:
          ╭─ Context or current state
          ╰─ [Yes|No|OK]
          Question? [YES]

        Accepts:
          - 1, y, yes, ok, Enter (if default=True) = True
          - 0, n, no, Enter (if default=False) = False

        Args:
            question: The question to ask (without punctuation)
            default: Default answer if user just presses Enter
            help_text: Optional help text for line 2
            context: Optional context for line 1

        Returns:
            True for yes/ok, False for no/cancel
        """
        choice = self._ask_confirm(
            question=question,
            default=default,
            help_text=help_text,
            context=context,
            variant="ok",
        )
        return choice in {"yes", "ok"}

    def _ask_menu_choice(self, prompt: str, num_options: int, allow_cancel: bool = True, help_text: str = None) -> Optional[int]:
        """Ask user to select from a numbered menu with 2-line context display.

        Shows:
          ╭─ Valid choices: 1-N or 0 to cancel
          ╰─ Enter number and press Enter

        Args:
            prompt: Prompt to display
            num_options: Number of valid options
            allow_cancel: If True, 0/Enter cancels; if False, user must pick 1-N
            help_text: Optional help text for line 2

        Returns:
            Selected number (1-N), or None if cancelled
        """
        # Build context display
        range_display = f"1-{num_options}" + (" or 0 to cancel" if allow_cancel else "")

        # Display context lines
        if self.prompt.show_context:
            print(f"\n  ╭─ Valid choices: {range_display}")
            if help_text:
                print(f"  ╰─ {help_text}")
            else:
                print(f"  ╰─ Enter number and press Enter")

        # Get choice using standard menu handler
        return self.prompt.ask_menu_choice(prompt, num_options, allow_zero=allow_cancel)

    def _handle_story_form(self, form_data: Dict) -> Dict:
        """Handle interactive story form - collect user responses for all sections.

        Args:
            form_data: Form structure with title and sections or fields

        Returns:
            Dictionary of collected field values from all sections
        """
        collected = {}

        # Show form title
        title = form_data.get("title", "Form")
        print(f"\n📋 {title}")
        print("=" * 60)

        # Check if this is multi-section form
        sections = form_data.get("sections", [])

        # DEBUG: Log what we received
        self.logger.debug(f"[STORY] Form sections: {len(sections)} sections, form_data keys: {list(form_data.keys())}")
        if sections:
            self.logger.debug(f"[STORY] Section titles: {[s.get('title') for s in sections]}")

        if sections:
            # Process each section
            for section_idx, section in enumerate(sections):
                section_title = section.get("title", "Section")
                section_text = section.get("text", "").strip()
                fields = section.get("fields", [])

                self.logger.debug(f"[STORY] Processing section {section_idx}: '{section_title}' with {len(fields)} fields")

                if fields:  # Only show sections that have fields
                    print(f"\n## {section_title}\n")
                    if section_text:
                        print(f"{section_text}\n")
                        print("-" * 60)

                    # Collect responses for each field in section
                    for field in fields:
                        response = self._collect_field_response(field)
                        if response is not None:
                            field_name = field.get("name", "")
                            collected[field_name] = response
        else:
            # Single section form (backward compatibility)
            fields = form_data.get("fields", [])
            text = form_data.get("text", "").strip()

            if text:
                print(f"\n{text}\n")
                print("-" * 60)

            for field in fields:
                response = self._collect_field_response(field)
                if response is not None:
                    field_name = field.get("name", "")
                    collected[field_name] = response

        print("\n" + "=" * 60)
        return collected

    def _save_user_profile(self, collected_data: Dict) -> None:
        """Save collected form data to user profile.

        Enhanced to use ConfigSyncManager for bidirectional .env ↔ Wizard sync:
        1. Save identity fields to .env (local boundary: 7 fields)
        2. Sync to Wizard keystore via API (extended fields + identity)
        3. Enrich with UDOS Crypt ID and Profile ID

        Args:
            collected_data: Dictionary of field names and values from form
        """
        try:
            # Step 1: Enrich identity with UDOS Crypt fields
            from core.services.identity_encryption import IdentityEncryption

            # Extract location for Profile ID generation
            location = collected_data.get("user_location", "Earth")
            identity_enc = IdentityEncryption()
            enriched_data = identity_enc.enrich_identity(collected_data, location=location)

            # Step 2: Save identity fields + optional API keys to .env using ConfigSyncManager
            try:
                from core.services.config_sync_service import ConfigSyncManager

                sync_manager = ConfigSyncManager()

                # Validate and save identity to .env (7-field boundary enforced)
                if sync_manager.validate_identity(enriched_data):
                    sync_manager.save_identity_to_env(enriched_data)
                    self.logger.info("[SETUP] Identity saved to .env (7 fields)")
                    print("\n✅ Identity saved to .env file")
                    # Mistral key is now part of .env boundary (optional)
                    try:
                        from core.services.user_service import is_ghost_identity

                        if is_ghost_identity(enriched_data.get("user_username"), enriched_data.get("user_role")):
                            print("👻 Ghost Mode remains active (role or username is Ghost).")
                            print("   To exit Ghost Mode, change role to user/admin and set a non-Ghost username.")
                    except Exception:
                        pass
                else:
                    self.logger.warning("[SETUP] Identity validation failed")
                    print("\n⚠️  Some required fields are missing")

            except Exception as e:
                self.logger.warning(f"[SETUP] Could not save to .env: {e}")
                print(f"\n⚠️  Could not save to .env: {e}")

            # Step 3: Sync to Wizard keystore (if available)
            try:
                import requests

                # Get the token
                token_path = self.repo_root / "memory" / "private" / "wizard_admin_token.txt"

                if token_path.exists():
                    token = token_path.read_text().strip()
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }

                    # Submit to the story endpoint which handles splitting
                    response = requests.post(
                        "http://localhost:8765/api/setup/story/submit",
                        headers=headers,
                        json={"answers": enriched_data},  # Include enriched fields
                        timeout=10
                    )

                    if response.status_code == 200:
                        self.logger.info("[SETUP] Setup data synced to Wizard keystore")
                        print("✅ Data synced to Wizard keystore")

                        # Display UDOS Crypt identity
                        if enriched_data.get("_crypt_id"):
                            identity_enc.print_identity_summary(enriched_data, location=location)

                        return
                    elif response.status_code == 503:
                        self.logger.warning(f"[SETUP] Wizard secret store locked")
                        print(f"\n⚠️  Wizard secret store is locked. Please ensure WIZARD_KEY is set.")
                    else:
                        error_detail = response.json().get("detail", f"HTTP {response.status_code}")
                        self.logger.warning(f"[SETUP] Wizard API error: {error_detail}")
                        print(f"\n⚠️  Could not sync to Wizard: {error_detail}")

            except requests.exceptions.ConnectionError:
                self.logger.debug("Wizard server not running, trying direct save")
                print("⚠️  Wizard server not running - data saved locally only")
            except Exception as e:
                self.logger.debug(f"Wizard API submission failed: {e}")

            # Fallback: Try direct save via Wizard services (if Wizard is available but server isn't running)
            try:
                from wizard.services.setup_profiles import save_user_profile, save_install_profile

                # Split the collected data into user and install sections
                # User profile fields
                user_profile = {
                    "username": collected_data.get("user_username"),
                    "date_of_birth": collected_data.get("user_dob"),
                    "role": collected_data.get("user_role"),
                    "timezone": collected_data.get("user_timezone"),
                    "local_time": collected_data.get("user_local_time"),
                    "location_id": collected_data.get("user_location_id"),
                    "permissions": collected_data.get("user_permissions"),
                }

                # Install profile fields
                install_profile = {
                    "installation_id": collected_data.get("install_id"),
                    "os_type": collected_data.get("install_os_type"),
                    "lifespan_mode": collected_data.get("install_lifespan_mode"),
                    "moves_limit": collected_data.get("install_moves_limit"),
                    "permissions": collected_data.get("install_permissions"),
                    "capabilities": {
                        "web_proxy": bool(collected_data.get("capability_web_proxy")),
                        "ok_gateway": bool(collected_data.get("capability_ok_gateway")),
                        "github_push": bool(collected_data.get("capability_github_push")),
                        "icloud": bool(collected_data.get("capability_icloud")),
                        "plugin_repo": bool(collected_data.get("capability_plugin_repo")),
                        "plugin_auto_update": bool(collected_data.get("capability_plugin_auto_update")),
                    },
                }

                user_result = save_user_profile(user_profile)
                install_result = save_install_profile(install_profile)

                if user_result.data and install_result.data:
                    self.logger.info("[SETUP] Setup data saved via direct Wizard services")
                    print("\n✅ Setup data saved to Wizard keystore.")
                    return
                elif user_result.locked or install_result.locked:
                    error = user_result.error or install_result.error
                    self.logger.warning(f"[SETUP] Secret store locked: {error}")
                    print(f"\n⚠️  Secret store is locked: {error}")
                    print("Please ensure WIZARD_KEY is set in .env file.")

            except (ImportError, Exception) as e:
                self.logger.debug(f"Wizard direct save not available: {e}")

            # Final fallback: Save to local profile file in memory/
            profile_dir = self.repo_root / "memory" / "user"
            profile_dir.mkdir(parents=True, exist_ok=True)
            profile_file = profile_dir / "profile.json"

            import json
            from datetime import datetime

            # Create profile structure with timestamp
            profile = {
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "data": collected_data
            }

            with open(profile_file, "w") as f:
                json.dump(profile, f, indent=2)

            self.logger.info(f"[SETUP] User profile saved to local file: {profile_file}")
            print(f"\n💾 Setup data saved locally to {profile_file}")
            print("⚠️  Note: Start Wizard server to sync this data to the keystore.")

        except Exception as e:
            self.logger.error(f"[SETUP] Failed to save user profile: {e}", exc_info=True)
            print(f"\n⚠️  Warning: Could not save profile: {e}")


    def _collect_field_response(self, field: Dict, previous_value: Optional[str] = None) -> Optional[str]:
        """Collect response for a single form field using AdvancedFormField.

        Enhanced with:
        - Syntax-highlighted field display
        - System-detected suggestions (timezone, date, etc.)
        - Tab/Enter to accept suggestions
        - Per-field validation

        Args:
            field: Field definition with name, label, type, etc.
            previous_value: Previous value if editing

        Returns:
            User's response or None
        """
        try:
            # Create AdvancedFormField instance
            form_field = AdvancedFormField()

            # Load system suggestions for relevant fields
            suggestions = form_field.load_system_suggestions()

            # Determine suggestion for this specific field
            field_name = field.get("name", "").lower()
            suggestion = None

            # Check for explicit default in field definition
            if field.get("default"):
                suggestion = field.get("default")
            # Check for system-based suggestions
            elif "timezone" in field_name:
                suggestion = suggestions.get("timezone") or suggestions.get("user_timezone")
            elif "time" in field_name:
                suggestion = suggestions.get("time") or suggestions.get("user_local_time")
            elif "date" in field_name or "dob" in field_name:
                suggestion = suggestions.get("date") or suggestions.get("user_date")

            # Use previous value as suggestion if available
            if previous_value:
                suggestion = previous_value

            # Collect field input with enhanced UI
            value = form_field.collect_field_input(field, suggestion)

            return value

        except Exception as e:
            # Fallback to basic prompt if advanced form handler fails
            self.logger.warning(f"[FORM] Advanced form handler failed, using fallback: {e}")
            return self.prompt.ask_story_field(field, previous_value)

    def _check_fresh_install(self) -> None:
        """Check if this is a fresh install and run setup story if needed.

        A fresh install is detected when:
        - No user profile exists in Wizard
        - No setup has been completed

        Self-healing: Automatically builds TS runtime if missing.
        """
        try:
            # Check if Wizard is available
            if not self.detector.is_available("wizard"):
                self.logger.debug("Wizard not available, skipping fresh install check")
                return

            # Try to load user profile from Wizard
            try:
                from wizard.services.setup_profiles import load_user_profile

                result = load_user_profile()

                # If we have user data, not a fresh install
                if result.data and not result.locked:
                    self.logger.debug("User profile exists, not a fresh install")
                    return

                # If locked due to no encryption key, still consider it fresh
                if result.locked and "not set" in str(result.error).lower():
                    self.logger.debug("Wizard not yet initialized, treating as fresh install")

            except (ImportError, Exception) as e:
                self.logger.debug(f"Could not check user profile: {e}")
                return

            # Fresh install detected
            print("\n" + "="*60)
            print("⚙️  FRESH INSTALLATION DETECTED")
            print("="*60)
            print("\nNo user profile found. Let's set up your uDOS installation!")
            print("\nWe'll capture:")
            print("  • Your identity (username, role, timezone, location)")
            print("  • Installation settings (OS type, lifespan mode)")
            print("  • Capability preferences (cloud services, integrations)")
            print("\nThis data will be stored securely in the Wizard keystore.")
            print("-"*60)

            # Check if TS runtime is built
            ts_runtime_path = self.repo_root / "core" / "grid-runtime" / "dist" / "index.js"
            if not ts_runtime_path.exists():
                print("\n🔨 Building TypeScript runtime (auto-heal)...")
                print("   This may take 30-60 seconds on first build...\n")

                # Verify Node.js and npm are available before attempting build
                try:
                    node_check = subprocess.run(
                        ["node", "--version"],
                        capture_output=True,
                        timeout=5,
                        text=True
                    )
                    npm_check = subprocess.run(
                        ["npm", "--version"],
                        capture_output=True,
                        timeout=5,
                        text=True
                    )

                    if node_check.returncode != 0 or npm_check.returncode != 0:
                        print("   ❌ Node.js/npm not available.\n")
                        print("   The TypeScript runtime requires Node.js and npm.")
                        print("\n   Please install Node.js from: https://nodejs.org/")
                        print("   Then try again with:")
                        print("      bash /Users/fredbook/Code/uDOS/core/tools/build_ts_runtime.sh")
                        return

                except Exception as e:
                    print("   ⚠️  Could not verify Node.js/npm availability.\n")
                    print(f"   Error: {e}")
                    print("\n   Try manually building:")
                    build_script = self.repo_root / "core" / "tools" / "build_ts_runtime.sh"
                    print(f"      bash {build_script}")
                    return

                # Self-heal: automatically build the TS runtime
                build_script = self.repo_root / "core" / "tools" / "build_ts_runtime.sh"
                if build_script.exists():
                    try:
                        import threading

                        # Spinner animation
                        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
                        spinner_idx = [0]
                        build_complete = [False]

                        def show_spinner():
                            """Show animated spinner while build runs."""
                            while not build_complete[0]:
                                sys.stdout.write(f'\r   {spinner_chars[spinner_idx[0]]} Building...')
                                sys.stdout.flush()
                                spinner_idx[0] = (spinner_idx[0] + 1) % len(spinner_chars)
                                time.sleep(0.1)

                        # Start spinner in background thread
                        spinner_thread = threading.Thread(target=show_spinner, daemon=True)
                        spinner_thread.start()

                        # Run build with combined output for better error visibility
                        result = subprocess.run(
                            ["bash", str(build_script)],
                            cwd=str(self.repo_root),
                            capture_output=True,
                            timeout=300,  # 5 minute timeout for build
                            text=True
                        )

                        build_complete[0] = True
                        spinner_thread.join(timeout=1)

                        # Clear the spinner line
                        sys.stdout.write('\r' + ' ' * 50 + '\r')
                        sys.stdout.flush()

                        if result.returncode == 0:
                            print("   ✅ TypeScript runtime built successfully!")
                            self.logger.info("[SETUP] TS runtime auto-built")

                            # Small delay for visual clarity
                            time.sleep(0.5)
                        else:
                            print("   ❌ Build failed.\n")

                            # Combine stdout and stderr for complete error picture
                            output_text = result.stdout + result.stderr

                            if output_text.strip():
                                print("   Error details:")
                                # Show last 20 lines of output
                                lines = output_text.split("\n")
                                for line in lines[-20:]:
                                    if line.strip():
                                        print("   " + line)
                            else:
                                print("   (No error output captured)")

                            print("\n   To fix manually, run:")
                            print(f"      bash {build_script}")
                            print("\n   Or check the build logs:")
                            log_path = self.repo_root / "core" / "grid-runtime" / "build.log"
                            print(f"      tail -100 {log_path}")
                            return
                    except subprocess.TimeoutExpired:
                        build_complete[0] = True
                        sys.stdout.write('\r' + ' ' * 50 + '\r')
                        sys.stdout.flush()
                        print("   ❌ Build timed out (>5 minutes).\n")
                        print("   The TypeScript runtime is taking too long to build.")
                        print("   Try manually:")
                        print(f"      bash {build_script}")
                        return
                    except Exception as e:
                        build_complete[0] = True
                        sys.stdout.write('\r' + ' ' * 50 + '\r')
                        sys.stdout.flush()
                        print(f"   ❌ Build error: {e}\n")
                        print("   To fix manually, run:")
                        print(f"      bash {build_script}")
                        return
                else:
                    print(f"   ❌ Build script not found: {build_script}")
                    return

            # TS runtime is available - run setup story automatically
            print()
            if self._ask_yes_no("Run setup story now"):
                print("\n🚀 Launching setup story...\n")

                # Auto-execute the STORY tui-setup command
                result = self.dispatcher.dispatch("STORY tui-setup", game_state=self.state)

                # Check if this is a form-based story
                if result.get("story_form"):
                    collected_data = self._handle_story_form(result["story_form"])
                    print("\n✅ Setup form completed!")
                    print(f"\nCollected {len(collected_data)} values")

                    # Save the collected data to user profile
                    if collected_data:
                        self._save_user_profile(collected_data)
                        print("\nData saved. Next steps:")
                        print("  SETUP              - View your profile")
                        print("  CONFIG             - View variables")
                else:
                    # Show the result for non-form stories
                    output = self.renderer.render(result)
                    print(output)

                self.logger.info("[SETUP] Fresh install setup completed")
            else:
                print("\n⏭️  Setup skipped. You can run it anytime with:")
                print("   STORY tui-setup")
                print()

        except Exception as e:
            self.logger.error(f"[SETUP] Fresh install check failed: {e}", exc_info=True)
            # Non-fatal error, continue with startup

    def _theme_text(self, text: str) -> str:
        """Apply the active theme to the provided message."""
        return self.theme.format(text)

    def _show_component_status(self) -> None:
        """Show detected components."""
        print("\n📦 Component Detection:\n")
        for comp_name, comp in self.components.items():
            status = "✅" if comp.state == ComponentState.AVAILABLE else "❌"
            version_str = f" ({comp.version})" if comp.version else ""
            line = f"  {status} {comp.name.upper():12} {comp.description}{version_str}"
            print(self._theme_text(line))
        print()

    def _cmd_status(self, args: str) -> None:
        """Show system status."""
        print(self._theme_text("\n═══ uCODE STATUS ═══\n"))
        self._show_component_status()

        if self.detector.is_available("wizard"):
            print(self._theme_text("🧙 Wizard Server control available: Use WIZARD [start|stop|status]"))
        print()

    def _cmd_help(self, args: str) -> None:
        """Show help."""
        help_text = """
═══ uCODE HELP ═══

Core Commands:
  STATUS              - Show system status
  HELP                - This help message
  EXIT                - Exit uCODE

System Management:
  SETUP               - Run setup story (default)
  SETUP --profile     - View your setup profile
  CONFIG              - Manage configuration variables
  DESTROY             - System cleanup (wipe user, compost, reset)
  SHAKEDOWN           - Validate system health
  REPAIR              - Fix issues and self-heal
  RESTART             - Restart/reload system
  USER                - User profile and permission management
  LOGS                - View unified system logs

Data & Stories:
  BINDER              - Multi-chapter project management
  STORY [name]        - Run story files (.md with questions/flow)
  RUN [file]          - Execute TypeScript scripts or Python files
  DATASET             - Manage data imports and datasets

Navigation & Info:
  MAP                 - Show spatial map
  GOTO [location]     - Travel to location
  FIND [query]        - Search for locations
  TELL [query]        - Get information
  BAG                 - Inventory management

AI Modes:
  OK EXPLAIN <file>   - Explain code via local Vibe (offline)
  OK DIFF <file>      - Propose a diff via local Vibe
  OK PATCH <file>     - Draft a patch via local Vibe
  OK LOCAL [N]        - Show recent OK local outputs

"""
        if self.detector.is_available("wizard"):
            help_text += """Wizard Server:
  WIZARD start        - Start Wizard server
  WIZARD stop         - Stop Wizard server
  WIZARD status       - Check Wizard status
  WIZARD console      - Enter Wizard interactive console
  WIZARD [page]       - Show Wizard page (status, ai, devices, quota, logs)

"""
        help_text += """
Examples:
  SETUP                      - Run setup story
  SETUP --profile            - View your setup profile
  UID                        - Show your User ID
  STORY tui-setup            - Run setup story
  DESTROY --wipe-user        - Wipe user data
  WIZARD start               - Start Wizard Server
  BINDER open my-project     - Open a project
  MAP                        - Show spatial map

For detailed help on any command, type the command name followed by --help
(e.g., CONFIG --help, DESTROY --help)

"""
        print(self._theme_text(help_text))

    def _record_ok_output(
        self,
        prompt: str,
        response: str,
        model: str,
        source: str,
        mode: str,
        file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Store OK local output and emit a unified log entry."""
        self.ok_local_counter += 1
        entry = {
            "id": self.ok_local_counter,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
            "model": model,
            "source": source,
            "mode": mode,
            "file_path": file_path,
        }
        self.ok_local_outputs.append(entry)
        if len(self.ok_local_outputs) > self.ok_local_limit:
            self.ok_local_outputs = self.ok_local_outputs[-self.ok_local_limit :]

        try:
            ok_logger = get_logger("core", category="ok-local-output", name="ucode")
            preview = (response or "").strip().splitlines()
            ok_logger.event(
                "info",
                "ok.local.output",
                f"OK {mode} output stored",
                ctx={
                    "mode": mode,
                    "model": model,
                    "source": source,
                    "file_path": file_path,
                    "prompt_preview": (prompt or "")[:120],
                    "response_preview": " ".join(preview[:2])[:160] if preview else "",
                },
            )
        except Exception:
            pass

        return entry

    def _format_ok_output_summary(self, entry: Dict[str, Any]) -> str:
        """Return a collapsed summary line for an OK output entry."""
        prompt = (entry.get("prompt") or "").replace("\n", " ").strip()
        response = (entry.get("response") or "").strip().splitlines()
        preview = " ".join(response[:2]).strip()
        if len(preview) > 120:
            preview = preview[:117] + "..."
        if len(prompt) > 80:
            prompt = prompt[:77] + "..."
        return (
            f"[{entry.get('id')}] {entry.get('timestamp')} "
            f"{entry.get('model')} ({entry.get('source')})\n"
            f"  Prompt: {prompt}\n"
            f"  Preview: {preview or '(no output)'}\n"
            f"  Tip: OK LOCAL SHOW {entry.get('id')}"
        )

    def _format_ok_output_full(self, entry: Dict[str, Any]) -> str:
        """Return full output text for an OK output entry."""
        header = [
            "═══ OK LOCAL OUTPUT ═══",
            f"ID: {entry.get('id')}",
            f"Time: {entry.get('timestamp')}",
            f"Model: {entry.get('model')} ({entry.get('source')})",
        ]
        if entry.get("file_path"):
            header.append(f"File: {entry.get('file_path')}")
        header.append("")
        header.append("Prompt:")
        header.append(entry.get("prompt") or "")
        header.append("")
        header.append("Response:")
        header.append(entry.get("response") or "")
        return "\n".join(header)

    def _cmd_ok_local(self, args: str) -> None:
        """Show stored OK local outputs."""
        tokens = args.strip().split()
        if not tokens:
            limit = 5
            entries = self.ok_local_outputs[-limit:]
        elif tokens[0].upper() in ("SHOW", "OPEN"):
            if len(tokens) < 2 or not tokens[1].isdigit():
                print(self._theme_text("Usage: OK LOCAL SHOW <id>"))
                return
            entry_id = int(tokens[1])
            entry = next((e for e in self.ok_local_outputs if e["id"] == entry_id), None)
            if not entry:
                print(self._theme_text(f"No OK output with id {entry_id}"))
                return
            print(self._theme_text(self._format_ok_output_full(entry)))
            return
        elif tokens[0].upper() == "CLEAR":
            self.ok_local_outputs = []
            print(self._theme_text("OK local output log cleared."))
            return
        else:
            try:
                limit = int(tokens[0])
            except ValueError:
                print(self._theme_text("Usage: OK LOCAL [N] | OK LOCAL SHOW <id> | OK LOCAL CLEAR"))
                return
            entries = self.ok_local_outputs[-limit:]

        if not entries:
            print(self._theme_text("No OK local outputs yet."))
            return
        print(self._theme_text("\n═══ OK LOCAL OUTPUTS ═══\n"))
        for entry in entries:
            print(self._theme_text(self._format_ok_output_summary(entry)))
            print(self._theme_text(""))

    def _parse_ok_file_args(self, args: str) -> Dict[str, Any]:
        """Parse OK command args for file + optional range + cloud flag."""
        tokens = args.strip().split()
        use_cloud = False
        clean_tokens: List[str] = []
        for token in tokens:
            if token.lower() in ("--cloud", "--onvibe"):
                use_cloud = True
            else:
                clean_tokens.append(token)
        if not clean_tokens:
            return {"error": "Missing file path", "use_cloud": use_cloud}

        file_token = clean_tokens[0]
        line_start = None
        line_end = None

        if len(clean_tokens) >= 3 and clean_tokens[1].isdigit() and clean_tokens[2].isdigit():
            line_start = int(clean_tokens[1])
            line_end = int(clean_tokens[2])
        elif len(clean_tokens) >= 2 and any(sep in clean_tokens[1] for sep in (":", "-", "..")):
            parts = (
                clean_tokens[1]
                .replace("..", ":")
                .replace("-", ":")
                .split(":")
            )
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                line_start = int(parts[0])
                line_end = int(parts[1])

        path = Path(file_token)
        if not path.is_absolute():
            path = self.repo_root / path
        return {
            "path": path,
            "line_start": line_start,
            "line_end": line_end,
            "use_cloud": use_cloud,
        }

    def _run_ok_cloud(self, prompt: str) -> Dict[str, Any]:
        """Run a cloud AI request (Mistral) for OK commands."""
        from wizard.services.mistral_api import MistralAPI

        mode = (self.ai_modes_config.get("modes") or {}).get("onvibe", {})
        model = mode.get("default_model") or "mistral-small-latest"
        client = MistralAPI()
        if not client.available():
            raise RuntimeError("Mistral API key required for cloud OK")
        return {"response": client.chat(prompt, model=model), "model": model}

    def _run_ok_local(self, prompt: str, model: Optional[str] = None) -> str:
        """Run a local Vibe request via Ollama."""
        from wizard.services.vibe_service import VibeService, VibeConfig

        config = VibeConfig(model=model or self._get_ok_default_model())
        vibe = VibeService(config=config)
        return vibe.generate(prompt, format="markdown")

    def _run_with_spinner(self, label: str, func: Callable[[], Any], mood: str = "busy") -> Any:
        """Run a long action with a lightweight spinner + elapsed seconds."""
        from core.tui.ui_elements import Spinner

        spinner = Spinner(label=label, show_elapsed=True)
        previous_mood = self.renderer.get_mood()
        self.renderer.set_mood(mood, pace=0.4, blink=True)

        stop = threading.Event()

        def spin() -> None:
            spinner.start()
            while not stop.is_set():
                spinner.tick()
                time.sleep(spinner.interval)
            spinner.stop(f"{label} done")

        thread = threading.Thread(target=spin, daemon=True)
        thread.start()
        try:
            result = func()
        except Exception:
            self.renderer.set_mood(previous_mood, pace=0.7, blink=True)
            stop.set()
            thread.join(timeout=0.5)
            raise
        stop.set()
        thread.join(timeout=0.5)
        self.renderer.set_mood(previous_mood, pace=0.7, blink=True)
        return result

    def _run_ok_request(
        self,
        prompt: str,
        mode: str,
        file_path: Optional[str] = None,
        use_cloud: bool = False,
    ) -> None:
        """Execute OK request with optional cloud fallback."""
        model = self._get_ok_default_model()
        source = "local"
        response = None

        if use_cloud:
            try:
                print(self._theme_text("OK → Cloud (Mistral)"))
                cloud_result = self._run_with_spinner(
                    "⏳ OK cloud",
                    lambda: self._run_ok_cloud(prompt),
                )
                response = cloud_result.get("response")
                model = cloud_result.get("model") or model
                source = "cloud"
            except Exception as exc:
                print(self._theme_text(f"⚠️  Cloud failed ({exc}). Falling back to Vibe (offline)."))
                response = None

        if response is None:
            print(self._theme_text(f"OK → Vibe ({model}, local)"))
            try:
                response = self._run_with_spinner(
                    "⏳ OK local",
                    lambda: self._run_ok_local(prompt, model=model),
                )
            except Exception as exc:
                print(self._theme_text(f"❌ Vibe local failed: {exc}"))
                return

        entry = self._record_ok_output(
            prompt=prompt,
            response=response,
            model=model,
            source=source,
            mode=mode,
            file_path=str(file_path) if file_path else None,
        )
        print(self._theme_text(""))
        self.renderer.stream_text(entry.get("response") or "", prefix="ok> ")

    def _cmd_ok_explain(self, args: str) -> None:
        """OK EXPLAIN <file> [start end] [--cloud]."""
        parsed = self._parse_ok_file_args(args)
        if parsed.get("error"):
            print(self._theme_text("Usage: OK EXPLAIN <file> [start end] [--cloud]"))
            return
        path = parsed["path"]
        if not path.exists():
            print(self._theme_text(f"File not found: {path}"))
            return
        content = path.read_text(encoding="utf-8", errors="ignore")
        if parsed.get("line_start") and parsed.get("line_end"):
            lines = content.splitlines()
            content = "\n".join(
                lines[parsed["line_start"] - 1 : parsed["line_end"]]
            )
        prompt = (
            f"Explain this code from {path}:\n\n"
            f"```python\n{content}\n```\n\n"
            "Provide: 1) purpose, 2) key logic, 3) risks or follow-ups."
        )
        self._run_ok_request(prompt, mode="EXPLAIN", file_path=path, use_cloud=parsed.get("use_cloud"))

    def _cmd_ok_diff(self, args: str) -> None:
        """OK DIFF <file> [start end] [--cloud]."""
        parsed = self._parse_ok_file_args(args)
        if parsed.get("error"):
            print(self._theme_text("Usage: OK DIFF <file> [start end] [--cloud]"))
            return
        path = parsed["path"]
        if not path.exists():
            print(self._theme_text(f"File not found: {path}"))
            return
        content = path.read_text(encoding="utf-8", errors="ignore")
        if parsed.get("line_start") and parsed.get("line_end"):
            lines = content.splitlines()
            content = "\n".join(
                lines[parsed["line_start"] - 1 : parsed["line_end"]]
            )
        prompt = (
            f"Propose a unified diff for improvements to {path}.\n\n"
            f"```python\n{content}\n```\n\n"
            "Return a unified diff only (no commentary)."
        )
        self._run_ok_request(prompt, mode="DIFF", file_path=path, use_cloud=parsed.get("use_cloud"))

    def _cmd_ok_patch(self, args: str) -> None:
        """OK PATCH <file> [start end] [--cloud]."""
        parsed = self._parse_ok_file_args(args)
        if parsed.get("error"):
            print(self._theme_text("Usage: OK PATCH <file> [start end] [--cloud]"))
            return
        path = parsed["path"]
        if not path.exists():
            print(self._theme_text(f"File not found: {path}"))
            return
        content = path.read_text(encoding="utf-8", errors="ignore")
        if parsed.get("line_start") and parsed.get("line_end"):
            lines = content.splitlines()
            content = "\n".join(
                lines[parsed["line_start"] - 1 : parsed["line_end"]]
            )
        prompt = (
            f"Draft a patch (unified diff) for {path}. Keep the diff minimal.\n\n"
            f"```python\n{content}\n```\n\n"
            "Return a unified diff only."
        )
        self._run_ok_request(prompt, mode="PATCH", file_path=path, use_cloud=parsed.get("use_cloud"))

    def _cmd_fkeys(self, args: str) -> None:
        """Show or trigger function key actions."""
        arg = args.strip().upper()

        if not arg or arg in ("HELP", "?"):
            result = self.fkey_handler._handle_fkey_help()
            if result and result.get("output"):
                print(result["output"])
            else:
                print("No function key help available.")
            return

        if arg.isdigit():
            arg = f"F{arg}"

        if not arg.startswith("F"):
            print("Usage: FKEYS [F1-F8]")
            return

        handler = self.fkey_handler.handlers.get(arg)
        if not handler:
            print("Unknown function key. Use FKEYS for help.")
            return

        result = handler()
        if result:
            output = result.get("output") or result.get("message")
            if output:
                print(output)

    # Legacy _cmd_wizard removed - now handled by dispatcher WizardHandler

    def _wizard_start(self) -> None:
        """Start Wizard server."""
        try:
            # Check if already running
            try:
                resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                if resp.status_code == 200:
                    print("  ✅ Wizard already running")
                    return
            except requests.exceptions.ConnectionError:
                pass  # Not running, proceed

            print("  Starting Wizard Server...")
            venv_activate = self.repo_root / ".venv" / "bin" / "activate"

            # Build command - use module execution for correct imports
            # Use bash explicitly for 'source' command (not sh)
            if venv_activate.exists():
                cmd = f"bash -c 'source {venv_activate} && python -m wizard.server --no-interactive 2>&1'"
            else:
                cmd = "python -m wizard.server --no-interactive 2>&1"

            # Create a log file for debugging
            log_file = self.repo_root / ".wizard_startup.log"

            # Start in background with log capture for debugging
            try:
                with open(str(log_file), 'w') as log:
                    # Redirect stderr to stdout in the shell command so we capture it
                    proc = subprocess.Popen(
                        cmd,
                        shell=True,
                        cwd=str(self.repo_root),
                        stdin=subprocess.DEVNULL,
                        stdout=log,
                        stderr=log,
                        preexec_fn=os.setsid if sys.platform != 'win32' else None
                    )
            except Exception as start_err:
                raise Exception(f"Failed to spawn wizard process: {start_err}")

            # Wait for server to be ready (increased to 30 seconds to allow slow initialization)
            max_wait = 30
            start = time.time()
            attempt = 0
            while time.time() - start < max_wait:
                try:
                    resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                    if resp.status_code == 200:
                        print(f"  ✅ Wizard Server started (PID: {proc.pid})")
                        sys.stdout.flush()  # Ensure output is flushed
                        return
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    attempt += 1
                    time.sleep(0.5)
                except Exception as e:
                    # Other request errors, keep trying
                    time.sleep(0.5)

            # If we get here, server didn't respond
            print("  ⚠️  Wizard Server started but not responding (timeout after 30s)")
            print(f"  📝 Check {log_file} for startup logs")
            print(f"  💡 Try: tail -f {log_file}")
            sys.stdout.flush()

        except Exception as e:
            self.logger.error(f"Failed to start Wizard: {e}")
            print(f"  ❌ Error: {e}")
            sys.stdout.flush()

    def _wizard_stop(self) -> None:
        """Stop Wizard server."""
        try:
            # Kill all python processes running wizard server
            # Match both 'wizard/server.py' and 'python -m wizard.server' (module form)
            if sys.platform == 'win32':
                cmd = "taskkill /F /IM python.exe"
            else:
                # Use more specific pattern to avoid matching avahi-daemon
                cmd = "pkill -f 'python.*wizard.server' || pkill -f 'python.*wizard/server.py' || true"
            time.sleep(0.5)

            # Verify it stopped
            try:
                resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                if resp.status_code == 200:
                    print("  ⚠️  Wizard Server still responding after stop command")
                else:
                    print("  ✅ Wizard Server stopped")
            except requests.exceptions.ConnectionError:
                print("  ✅ Wizard Server stopped")

            sys.stdout.flush()

        except Exception as e:
            self.logger.error(f"Failed to stop Wizard: {e}")
            print(f"  ❌ Error: {e}")
            sys.stdout.flush()

    def _wizard_status(self) -> None:
        """Check Wizard status."""
        try:
            resp = requests.get("http://127.0.0.1:8765/health", timeout=2)
            if resp.status_code == 200:
                print("  ✅ Wizard running on http://127.0.0.1:8765")
                data = resp.json()
                if "status" in data:
                    print(f"     Status: {data['status']}")
            else:
                print("  ❌ Wizard not responding")
        except requests.exceptions.ConnectionError:
            print("  ❌ Wizard not running")
        except Exception as e:
            print(f"  ⚠️  Error checking status: {e}")

    def _wizard_console(self) -> None:
        """Enter Wizard interactive console."""
        try:
            print("  Launching Wizard interactive console...")
            venv_activate = self.repo_root / ".venv" / "bin" / "activate"

            if venv_activate.exists():
                cmd = f"source {venv_activate} && python wizard/wizard_tui.py"
            else:
                cmd = "python wizard/wizard_tui.py"

            subprocess.run(cmd, shell=True, cwd=str(self.repo_root))

        except Exception as e:
            self.logger.error(f"Failed to launch Wizard console: {e}")
            print(f"  ❌ Error: {e}")

    def _wizard_page(self, page: str) -> None:
        """Show Wizard page via API."""
        try:
            # Map page names to API endpoints
            page_map = {
                "status": "/health",
                "ai": "/api/ai/status",
                "services": "/api/status",
                "devices": "/api/devices",
                "quota": "/api/ai/quota",
                "logs": "/api/logs",
            }

            endpoint = page_map.get(page.lower())
            if not endpoint:
                print(f"  ❌ Unknown page: {page}")
                print(f"     Available: {', '.join(page_map.keys())}")
                return

            resp = requests.get(f"http://127.0.0.1:8765{endpoint}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                print(json.dumps(data, indent=2))
            else:
                print(f"  ❌ Request failed: {resp.status_code}")

        except requests.exceptions.ConnectionError:
            print("  ❌ Wizard not running. Start with: WIZARD start")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _cmd_exit(self, args: str) -> None:
        """Exit uCODE."""
        self.running = False
        print("\n👋 Goodbye!")

    def _cleanup(self) -> None:
        """Cleanup on exit."""
        self.logger.info("uCODE TUI shutting down")

    def _is_ghost_user(self) -> bool:
        """Return True if current user is the demo ghost profile.

        A user is considered "ghost" (demo mode) only if:
        - .env identity sets role or username to Ghost, OR
        - Current user is guest role or username ghost.
        """
        from core.services.user_service import is_ghost_mode

        return is_ghost_mode()


    def _check_ghost_mode(self) -> None:
        """Check if running in ghost mode and prompt for setup.

        When user variables are destroyed/reset, the system defaults to
        ghost mode (demo/test access only). This method detects that and
        prompts the user to run SETUP to establish their identity.
        """
        self.ghost_mode = self._is_ghost_user()

        if self.ghost_mode:
            # In ghost mode
            print("\n" + "="*60)
            print("👻 Ghost Mode (Demo/Test Access)")
            print("="*60)
            print("\nYou're currently in ghost mode with limited access.")
            print("To set up your identity and unlock full features:\n")
            print("  SETUP\n")
            print("Or view this setup prompt later:")
            print("  SETUP --profile\n")
            print("="*60 + "\n")



def main():
    """Main entry point for uCODE."""
    tui = uCODETUI()
    tui.run()


if __name__ == "__main__":
    main()
