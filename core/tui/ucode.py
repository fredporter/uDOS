"""
uCODE - Unified Terminal TUI
=============================

The pivotal single-entry-point Terminal TUI for uDOS.

Features:
- Auto-detects available components (core, wizard, extensions)
- Graceful fallback to core-only mode if components are missing
- Integrated Wizard server control (start/stop/status)
- Extension/plugin packaging, installation, and distribution
- Core command dispatch with context-aware pages
- Dynamic capability loading based on available folders

Architecture:
  1. On startup, detect available components
  2. Build capability registry dynamically
  3. Expose only commands/pages for what's present
  4. If wizard exists, allow server control + Wizard pages
  5. If extensions exist, allow plugin management
  6. Fallback gracefully to core-only mode

Commands:
  STATUS          - System status and component detection
  HELP            - Show available commands
  WIZARD [cmd]    - Wizard server control (if available)
  PLUGIN [cmd]    - Extension/plugin management (if available)
  EXT [cmd]       - Extension management (alias for PLUGIN)
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
import time
import shutil
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
from core.ui.command_selector import CommandSelector
from core.input import SmartPrompt, EnhancedPrompt, ContextualCommandPrompt, create_default_registry
from core.services.health_training import read_last_summary, log_plugin_install_event
from core.services.hotkey_map import write_hotkey_payload
from core.services.theme_service import get_theme_service
from core.services.logging_service import get_logger
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
from wizard.services.plugin_validation import load_manifest, validate_manifest


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
        self.logger = get_logger("ucode-detector")
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
        self.logger = get_logger("ucode-tui")
        self.running = False
        self.ghost_mode = False
        # Ensure bank/system seeds are present (startup/reboot/setup stories)
        self._ensure_bank_system_seeds()
        # Component detection
        self.detector = ComponentDetector(self.repo_root)
        self.components = self.detector.detect_all()

        # Core components (always available)
        self.dispatcher = CommandDispatcher()
        self.renderer = GridRenderer()
        self.state = GameState()

        # Create command registry and contextual prompt (Phase 1)
        self.command_registry = create_default_registry()
        self.prompt = ContextualCommandPrompt(registry=self.command_registry)

        # Command selector (Phase 3)
        self.command_selector = CommandSelector(self.command_registry)
        self.prompt.set_tab_handler(self._open_command_selector)

        # Function key handler
        self.fkey_handler = FKeyHandler(dispatcher=self.dispatcher, prompt=self.prompt)
        self.prompt.set_function_key_handler(self.fkey_handler)

        # Command registry (maps commands to methods)
        self.commands = {
            "STATUS": self._cmd_status,
            "HELP": self._cmd_help,
            "VIBE": self._cmd_vibe,
            "NL": self._cmd_nl,
            "PROMPT": self._cmd_prompt,
            "EXIT": self._cmd_exit,
            "QUIT": self._cmd_exit,
            "FKEYS": self._cmd_fkeys,
            "FKEY": self._cmd_fkeys,
            "F": self._cmd_fkeys,
        }

        # Conditional commands
        # WIZARD command now handled by dispatcher (WizardHandler)

        if self.detector.is_available("extensions"):
            self.commands["PLUGIN"] = self._cmd_plugin
            self.commands["EXT"] = self._cmd_plugin
            self.commands["EXTENSION"] = self._cmd_plugin

        self.health_log_path = self.repo_root / "memory" / "logs" / "health-training.log"
        self.health_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.self_heal_summary: Optional[Dict[str, Any]] = None
        self.hot_reload_mgr = None
        self.hot_reload_stats: Optional[Dict[str, Any]] = None
        self.previous_health_log: Optional[Dict[str, Any]] = None
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

        if self.prompt.use_fallback:
            self.logger.info(f"[ContextualPrompt] Using fallback mode: {self.prompt.fallback_reason}")
        else:
            self.logger.info("[ContextualPrompt] Initialized with command suggestions")

    def _ensure_bank_system_seeds(self) -> None:
        """Seed /memory/bank/system files if they are missing."""
        try:
            from core.framework.seed_installer import SeedInstaller

            system_dir = self.repo_root / "memory" / "bank" / "system"
            required = [
                "startup-script.md",
                "reboot-script.md",
                "tui-setup-story.md",
                "wizard-setup-story.md",
            ]
            missing = [name for name in required if not (system_dir / name).exists()]
            if missing:
                installer = SeedInstaller()
                installer.install_bank_seeds(force=False)
                self.logger.info(
                    f"[LOCAL] Seeded memory/bank/system files: {', '.join(missing)}"
                )
        except Exception as e:
            self.logger.warning(f"[LOCAL] Bank/system seed check failed: {e}")

    def _handle_special_commands(self, command: str) -> bool:
        """Handle special REPL commands (EXIT/QUIT/STATUS/HISTORY)."""
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
        Route input based on prefix: ':', 'OK', '/', or question mode.

        Returns:
            Dict with status, message, and routed result
        """
        user_input = user_input.strip()
        if not user_input:
            return {"status": "error", "message": "Empty input"}

        # Mode 1: Command mode (OK ... or :...)
        if user_input.startswith("OK ") or user_input.startswith(":"):
            # Normalize : to remove the colon and pass the rest as a normal command
            if user_input.startswith(":"):
                # Remove the : and pass the rest to dispatcher
                normalized = user_input[1:].strip()
            else:
                # Remove "OK " prefix and pass the rest to dispatcher
                normalized = user_input[3:].strip()

            # Now route the normalized command to dispatcher
            return self.dispatcher.dispatch(normalized, parser=self.prompt)

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
            return self.dispatcher.dispatch(ucode_cmd, parser=self.prompt)
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
                default=False
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
        Handle question mode (natural language routing via Vibe CLI).

        Routes to 'NL ROUTE' command for Vibe-powered analysis.
        """
        # Try to use NL ROUTE if vibe is available
        vibe_cmd = f"NL ROUTE {user_input}"
        return self.dispatcher.dispatch(vibe_cmd, parser=self.prompt)

    def run(self) -> None:
        """Start uCODE TUI."""
        self.running = True
        self._run_startup_script()
        self._show_banner()
        self._show_health_summary()
        self._show_startup_hints()

        # Check if in ghost mode and prompt for setup
        self._check_ghost_mode()

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
                    user_input = self.prompt.ask_command("▶ ")

                    if not user_input:
                        continue

                    # Route input based on prefix (: / OK) or question mode
                    # This implements the uCODE Prompt Spec
                    result = self._route_input(user_input)

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
        print(self._theme_text("\n  💡 Start with: SETUP (first-time) | HELP (all commands) | STORY tui-setup (quick setup)"))
        print(self._theme_text("     Or try: MAP | TELL location | GOTO location | WIZARD start"))
        print(self._theme_text("     Press TAB for command selection | Type command for suggestions\n"))

    def _show_banner(self) -> None:
        """Show startup banner."""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                        uCODE v1.0.1                           ║
║                 Unified Terminal TUI for uDOS                 ║
║                    Type HELP for commands                     ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(self._theme_text(banner))

    def _run_startup_script(self) -> None:
        """Execute the system startup script once per launch."""
        # Pre-flight check: Ensure TS runtime is built
        self._check_and_build_ts_runtime()

        result = self.system_script_runner.run_startup_script()
        if result.get("status") == "success":
            output = result.get("output")
            if output:
                print(output)
        else:
            message = result.get("message")
            if message:
                print(f"\n⚡ {message}")

    def _show_health_summary(self) -> None:
        """Show Self-Heal + Hot Reload overview (banner/log hook)."""
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

    def _ask_yes_no(self, question: str, default: bool = True, help_text: str = None, context: str = None) -> bool:
        """Ask a standardized [1|0|Yes|No|OK|Cancel] question.

        Prompt format with 2-line context display:
          ╭─ Context or current state
          ╰─ [1|0|Yes|No|OK|Cancel]
          Question? [YES]

        Accepts:
          - 1, y, yes, ok, Enter (if default=True) = True
          - 0, n, no, x, cancel, Enter (if default=False) = False

        Args:
            question: The question to ask (without punctuation)
            default: Default answer if user just presses Enter
            help_text: Optional help text for line 2
            context: Optional context for line 1

        Returns:
            True for yes/ok, False for no/cancel
        """
        return self.prompt.ask_confirmation(
            question=question,
            default=default,
            help_text=help_text,
            context=context,
        )

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

            # Step 2: Save identity fields to .env using ConfigSyncManager
            try:
                from core.services.config_sync_service import ConfigSyncManager

                sync_manager = ConfigSyncManager()

                # Validate and save identity to .env (7-field boundary enforced)
                if sync_manager.validate_identity(enriched_data):
                    sync_manager.save_identity_to_env(enriched_data)
                    self.logger.info("[SETUP] Identity saved to .env (7 fields)")
                    print("\n✅ Identity saved to .env file")
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
                token_path = self.repo_root / "memory" / "bank" / "private" / "wizard_admin_token.txt"

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
                        "gmail_relay": bool(collected_data.get("capability_gmail_relay")),
                        "ai_gateway": bool(collected_data.get("capability_ai_gateway")),
                        "github_push": bool(collected_data.get("capability_github_push")),
                        "notion": bool(collected_data.get("capability_notion")),
                        "hubspot": bool(collected_data.get("capability_hubspot")),
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
                result = self.dispatcher.dispatch("STORY tui-setup")

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
        if self.detector.is_available("extensions"):
            print(self._theme_text("🔌 Extension management available: Use PLUGIN [list|install|remove]"))
        print()

    def _cmd_help(self, args: str) -> None:
        """Show help."""
        help_text = """
═══ uCODE HELP ═══

Core Commands:
  STATUS              - Show system status
  HELP                - This help message
  EXIT, QUIT          - Exit uCODE

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
  VIBE                - Vibe CLI integration (chat/context/history)
  NL                  - Natural language routing (prototype)

"""
        if self.detector.is_available("wizard"):
            help_text += """Wizard Server:
  WIZARD start        - Start Wizard server
  WIZARD stop         - Stop Wizard server
  WIZARD status       - Check Wizard status
  WIZARD console      - Enter Wizard interactive console
  WIZARD [page]       - Show Wizard page (status, ai, devices, quota, logs)

"""
        if self.detector.is_available("extensions"):
            help_text += """Extensions:
  PLUGIN list         - List installed plugins
  PLUGIN install      - Install new plugin
  PLUGIN remove       - Remove plugin
  PLUGIN pack         - Package plugin for distribution
  EXT [cmd]           - Alias for PLUGIN

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

    def _cmd_vibe(self, args: str) -> None:
        """Vibe CLI integration commands."""
        tokens = [t for t in args.split() if t.strip()]
        if not tokens or tokens[0].lower() in {"help", "--help", "?"}:
            print(self._theme_text(self._vibe_help_text()))
            return

        action = tokens[0].lower()
        rest = tokens[1:]

        if action == "chat":
            self._vibe_chat(rest)
            return
        if action == "context":
            self._vibe_context(rest)
            return
        if action == "history":
            self._vibe_history(rest)
            return
        if action == "config":
            self._vibe_config()
            return
        if action == "analyze":
            self._vibe_analyze(rest)
            return
        if action == "explain":
            self._vibe_explain(rest)
            return
        if action == "suggest":
            self._vibe_suggest(rest)
            return

        print(self._theme_text(f"Unknown VIBE action '{tokens[0]}'. Use VIBE HELP."))

    def _vibe_help_text(self) -> str:
        return """
═══ VIBE HELP ═══

VIBE CHAT <prompt> [--no-context] [--model <name>] [--format text|json]
VIBE CONTEXT [--files a,b,c] [--notes \"...\"]
VIBE HISTORY [--limit N]
VIBE CONFIG
VIBE ANALYZE <path>
VIBE EXPLAIN <symbol>
VIBE SUGGEST <task>

Notes:
  - Goblin endpoints are preferred for local dev: http://localhost:8767
  - Wizard endpoints are used if Goblin is unavailable: http://localhost:8765
  - Wizard may require WIZARD_ADMIN_TOKEN in the environment.
"""

    def _vibe_chat(self, args: List[str]) -> None:
        flags, prompt = self._parse_vibe_flags(args)
        if not prompt:
            prompt = self.prompt.ask_command("vibe> ").strip()
            if not prompt:
                print(self._theme_text("No prompt provided."))
                return

        provider, base_url = self._resolve_vibe_provider()
        if not provider:
            print(self._theme_text("Vibe service unavailable (Goblin/Wizard not reachable)."))
            return

        if provider == "goblin":
            payload = {
                "prompt": prompt,
                "system": flags.get("system", ""),
                "format": flags.get("format") or "text",
                "with_context": flags.get("with_context", True),
            }
            result = self._vibe_request("POST", f"{base_url}/api/dev/vibe/chat", json=payload)
            if not result:
                return
            response = result.get("response", "")
        else:
            payload = {
                "prompt": prompt,
                "include_context": flags.get("with_context", True),
                "model": flags.get("model") or "devstral-small",
            }
            result = self._vibe_request("POST", f"{base_url}/api/ai/query", json=payload, use_auth=True)
            if not result:
                return
            response = result.get("response", "")

        self.renderer.stream_text(str(response), prefix="vibe> ")

    def _vibe_context(self, args: List[str]) -> None:
        flags, _ = self._parse_vibe_flags(args)
        provider, base_url = self._resolve_vibe_provider()
        if not provider:
            print(self._theme_text("Vibe service unavailable (Goblin/Wizard not reachable)."))
            return

        if provider == "goblin":
            payload = {
                "files": flags.get("files"),
                "notes": flags.get("notes"),
            }
            result = self._vibe_request("POST", f"{base_url}/api/dev/vibe/context-inject", json=payload)
            if result:
                print(self._theme_text(f"Context updated. Files: {result.get('files', 0)}"))
            return

        # Wizard context is managed server-side
        result = self._vibe_request("GET", f"{base_url}/api/ai/context", use_auth=True)
        if result:
            files = result.get("files", [])
            print(self._theme_text(f"Wizard context files ({len(files)}):"))
            for item in files:
                print(f"  - {item}")

    def _vibe_history(self, args: List[str]) -> None:
        flags, _ = self._parse_vibe_flags(args)
        provider, base_url = self._resolve_vibe_provider()
        if not provider:
            print(self._theme_text("Vibe service unavailable (Goblin/Wizard not reachable)."))
            return

        if provider != "goblin":
            print(self._theme_text("History is available via Goblin only."))
            return

        limit = flags.get("limit") or 10
        result = self._vibe_request("GET", f"{base_url}/api/dev/vibe/history", params={"limit": limit})
        if not result:
            return
        history = result.get("history", [])
        print(self._theme_text(f"Vibe history (last {len(history)}):"))
        for entry in history:
            ts = entry.get("timestamp", "")
            status = entry.get("status", "")
            prompt = entry.get("prompt", "")
            print(f"  - {ts} [{status}] {prompt}")

    def _vibe_config(self) -> None:
        provider, base_url = self._resolve_vibe_provider(check_only=True)
        token = os.getenv("WIZARD_ADMIN_TOKEN") or os.getenv("ADMIN_TOKEN") or ""
        print(self._theme_text("Vibe configuration:"))
        print(f"  Provider: {provider or 'unknown'}")
        print(f"  Goblin URL: {os.getenv('GOBLIN_URL', 'http://localhost:8767')}")
        print(f"  Wizard URL: {os.getenv('WIZARD_URL', 'http://localhost:8765')}")
        print(f"  Wizard admin token set: {'yes' if token else 'no'}")
        print(f"  Active base URL: {base_url or '-'}")

    def _vibe_analyze(self, args: List[str]) -> None:
        flags, prompt = self._parse_vibe_flags(args)
        target = prompt.strip()
        if not target:
            target = self.prompt.ask_command("vibe/analyze> ").strip()
            if not target:
                print(self._theme_text("No target provided."))
                return

        provider, base_url = self._resolve_vibe_provider()
        if not provider:
            print(self._theme_text("Vibe service unavailable (Goblin/Wizard not reachable)."))
            return

        if provider == "goblin":
            payload = {"path": target, "with_context": flags.get("with_context", True)}
            result = self._vibe_request("POST", f"{base_url}/api/dev/vibe/analyze", json=payload)
        else:
            payload = {"path": target, "include_context": flags.get("with_context", True)}
            result = self._vibe_request("POST", f"{base_url}/api/ai/analyze", json=payload, use_auth=True)

        if result is None:
            return
        response = result.get("response", result)
        self.renderer.stream_text(str(response), prefix="vibe> ")

    def _vibe_explain(self, args: List[str]) -> None:
        flags, prompt = self._parse_vibe_flags(args)
        target = prompt.strip()
        if not target:
            target = self.prompt.ask_command("vibe/explain> ").strip()
            if not target:
                print(self._theme_text("No target provided."))
                return

        provider, base_url = self._resolve_vibe_provider()
        if not provider:
            print(self._theme_text("Vibe service unavailable (Goblin/Wizard not reachable)."))
            return

        if provider == "goblin":
            payload = {"symbol": target, "with_context": flags.get("with_context", True)}
            result = self._vibe_request("POST", f"{base_url}/api/dev/vibe/explain", json=payload)
        else:
            payload = {"symbol": target, "include_context": flags.get("with_context", True)}
            result = self._vibe_request("POST", f"{base_url}/api/ai/explain", json=payload, use_auth=True)

        if result is None:
            return
        response = result.get("response", result)
        self.renderer.stream_text(str(response), prefix="vibe> ")

    def _vibe_suggest(self, args: List[str]) -> None:
        flags, prompt = self._parse_vibe_flags(args)
        target = prompt.strip()
        if not target:
            target = self.prompt.ask_command("vibe/suggest> ").strip()
            if not target:
                print(self._theme_text("No task provided."))
                return

        provider, base_url = self._resolve_vibe_provider()
        if not provider:
            print(self._theme_text("Vibe service unavailable (Goblin/Wizard not reachable)."))
            return

        if provider == "goblin":
            payload = {"task": target, "with_context": flags.get("with_context", True)}
            result = self._vibe_request("POST", f"{base_url}/api/dev/vibe/suggest", json=payload)
        else:
            payload = {"task": target, "include_context": flags.get("with_context", True)}
            result = self._vibe_request("POST", f"{base_url}/api/ai/suggest", json=payload, use_auth=True)

        if result is None:
            return
        response = result.get("response", result)
        self.renderer.stream_text(str(response), prefix="vibe> ")

    def _cmd_nl(self, args: str) -> None:
        """Natural language routing prototype."""
        tokens = [t for t in args.split() if t.strip()]
        if not tokens or tokens[0].lower() in {"help", "--help", "?"}:
            print(self._theme_text(self._nl_help_text()))
            return

        action = tokens[0].lower()
        rest = tokens[1:]

        if action == "route":
            self._nl_route(rest)
            return

        print(self._theme_text(f"Unknown NL action '{tokens[0]}'. Use NL HELP."))

    def _nl_help_text(self) -> str:
        return """
═══ NL HELP ═══

NL ROUTE <prompt> [--dry-run] [--no-context]

Notes:
  - Uses the same Vibe transport as VIBE commands.
  - Returns a route plan and optional execution (unless --dry-run).
"""

    def _nl_route(self, args: List[str]) -> None:
        flags, prompt = self._parse_vibe_flags(args)
        dry_run = bool(flags.get("dry_run"))
        prompt_text = prompt.strip()
        if not prompt_text:
            prompt_text = self.prompt.ask_command("nl> ").strip()
            if not prompt_text:
                print(self._theme_text("No prompt provided."))
                return

        provider, base_url = self._resolve_vibe_provider()
        if not provider:
            print(self._theme_text("Vibe service unavailable (Goblin/Wizard not reachable)."))
            return

        if provider == "goblin":
            payload = {
                "prompt": prompt_text,
                "with_context": flags.get("with_context", True),
                "dry_run": dry_run,
            }
            result = self._vibe_request("POST", f"{base_url}/api/dev/vibe/nl-route", json=payload)
        else:
            payload = {
                "prompt": prompt_text,
                "include_context": flags.get("with_context", True),
                "dry_run": dry_run,
            }
            result = self._vibe_request("POST", f"{base_url}/api/ai/nl-route", json=payload, use_auth=True)

        if result is None:
            return

        plan = result.get("plan") or result.get("route") or result.get("response", result)
        self.renderer.stream_text(str(plan), prefix="vibe> ")

    def _parse_vibe_flags(self, args: List[str]) -> (Dict[str, Any], str):
        flags: Dict[str, Any] = {"with_context": True}
        parts: List[str] = []
        it = iter(args)
        for token in it:
            if token == "--dry-run":
                flags["dry_run"] = True
                continue
            if token == "--no-context":
                flags["with_context"] = False
                continue
            if token == "--context":
                flags["with_context"] = True
                continue
            if token == "--model":
                flags["model"] = next(it, None)
                continue
            if token == "--format":
                flags["format"] = next(it, None)
                continue
            if token == "--files":
                raw = next(it, None) or ""
                flags["files"] = [v.strip() for v in raw.split(",") if v.strip()]
                continue
            if token == "--notes":
                flags["notes"] = next(it, None)
                continue
            if token == "--limit":
                raw = next(it, None) or "10"
                try:
                    flags["limit"] = int(raw)
                except ValueError:
                    flags["limit"] = 10
                continue
            parts.append(token)
        return flags, " ".join(parts)

    def _resolve_vibe_provider(self, check_only: bool = False) -> (Optional[str], Optional[str]):
        if os.getenv("UDOS_VIBE_TEST_MODE") == "1":
            provider = os.getenv("UDOS_VIBE_TEST_PROVIDER", "goblin")
            url = os.getenv("UDOS_VIBE_TEST_URL", "http://localhost:8767")
            return provider, url

        goblin_url = os.getenv("GOBLIN_URL", "http://localhost:8767")
        wizard_url = os.getenv("WIZARD_URL", "http://localhost:8765")

        def _ok(url: str) -> bool:
            try:
                resp = requests.get(url, timeout=1.0)
                return resp.status_code == 200
            except Exception:
                return False

        if _ok(f"{goblin_url}/health"):
            return "goblin", goblin_url
        if _ok(f"{wizard_url}/health"):
            return "wizard", wizard_url
        return (None, None)

    def _vibe_request(self, method: str, url: str, json: Optional[Dict[str, Any]] = None,
                      params: Optional[Dict[str, Any]] = None, use_auth: bool = False) -> Optional[Dict[str, Any]]:
        if os.getenv("UDOS_VIBE_TEST_MODE") == "1":
            return self._vibe_test_stub_response(method, url, payload=json, params=params)

        headers = {}
        if use_auth:
            token = os.getenv("WIZARD_ADMIN_TOKEN") or os.getenv("ADMIN_TOKEN") or ""
            if token:
                headers["Authorization"] = f"Bearer {token}"

        try:
            resp = requests.request(method, url, json=json, params=params, headers=headers, timeout=10)
        except Exception as exc:
            print(self._theme_text(f"Vibe request failed: {exc}"))
            return None

        if resp.status_code in {401, 403}:
            print(self._theme_text("Wizard auth required. Set WIZARD_ADMIN_TOKEN."))
            return None
        if resp.status_code >= 400:
            print(self._theme_text(f"Vibe request error: HTTP {resp.status_code}"))
            return None

        try:
            return resp.json()
        except Exception:
            return {"response": resp.text}

    def _vibe_test_stub_response(self, method: str, url: str,
                                 payload: Optional[Dict[str, Any]] = None,
                                 params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        capture_path = os.getenv("UDOS_VIBE_TEST_CAPTURE_FILE")
        if capture_path:
            try:
                payload = {
                    "method": method,
                    "url": url,
                    "json": payload,
                    "params": params,
                }
                Path(capture_path).write_text(json.dumps(payload, indent=2))
            except Exception:
                pass

        raw = os.getenv("UDOS_VIBE_TEST_RESPONSE")
        if not raw:
            response_file = os.getenv("UDOS_VIBE_TEST_RESPONSE_FILE")
            if response_file and Path(response_file).exists():
                raw = Path(response_file).read_text()

        if raw:
            try:
                return json.loads(raw)
            except Exception:
                return {"response": raw}

        if "history" in url:
            return {"history": []}
        if "context" in url:
            return {"files": []}
        return {"response": "TEST_STUB"}

    def _cmd_prompt(self, args: str) -> None:
        """Parse an instruction using the PROMPT parser."""
        instruction = args.strip()
        if not instruction:
            print(self._theme_text("Usage: PROMPT <instruction text>"))
            return

        result = self.prompt_parser.parse(instruction)
        tasks = result.get("tasks", [])
        for task in tasks:
            self.todo_manager.add(task)

        calendar_lines = self.calendar_renderer.render_calendar(
            self.todo_manager.list_pending(), view="weekly"
        )
        gantt_lines = self.gantt_renderer.render_gantt(
            self.todo_manager.list_pending(), window_days=30
        )
        reminder = self.todo_reminder.log_reminder(
            horizon_hours=result.get("reminder", {}).get("horizon_hours")
        )

        print(self._theme_text(""))
        print(self._theme_text(f"🔍 Instruction type: {result['instruction_label']}"))
        print(self._theme_text(f"   {result['instruction_description']}"))
        if result.get("story_guidance"):
            print(self._theme_text(f"   Guidance: {result['story_guidance']}"))
        if result.get("reference_links"):
            print(self._theme_text(f"   References: {', '.join(result['reference_links'])}"))

        if tasks:
            print(self._theme_text("\n📝 Tasks added:"))
            for idx, task in enumerate(tasks, start=1):
                block = task.to_notion_block()
                print(self._theme_text(f" {idx}. {task.title} (due {task.due_date.isoformat()})"))
                print(self._theme_text(f"    Notion block: {json.dumps(block)}"))
        else:
            print(self._theme_text("No actionable tasks detected."))

        print(self._theme_text("\n📅 Calendar preview (weekly):"))
        for line in calendar_lines:
            print(self._theme_text(line))

        print(self._theme_text("\n🧮 Gantt preview:"))
        for line in gantt_lines:
            print(self._theme_text(line))

        if reminder:
            print(self._theme_text(f"\n⏰ Reminder: {reminder['message']}"))

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

    def _cmd_plugin(self, args: str) -> None:
        """Plugin/extension management."""
        if not self.detector.is_available("extensions"):
            print("❌ Extensions component not available.")
            return

        parts = args.split(None, 1)
        action = parts[0].lower() if parts else "list"
        subargs = parts[1] if len(parts) > 1 else ""

        if action == "list":
            print("\n🔌 Plugin catalog & installed extensions:\n")
            self._plugin_list()
        elif action == "install":
            print(f"\n🔌 Installing plugin from Wizard catalog: {subargs}")
            self._plugin_install(subargs)
        elif action == "remove":
            print(f"\n🔌 Removing plugin: {subargs}")
            self._plugin_remove(subargs)
        elif action == "pack":
            print(f"\n🔌 Packaging plugin: {subargs}")
            self._plugin_pack(subargs)
        elif action in ("help", "info"):
            print("\nPlugin commands: list, install <id>, remove <name>, pack <name>")
        else:
            print(f"\n🔌 Unknown plugin action: {action}")

    def _plugin_list(self) -> None:
        """List Wizard plugin catalog plus any installed extensions."""
        try:
            plugin_root = self.repo_root / "wizard" / "distribution" / "plugins"
            remote_plugins = self._load_remote_plugins(plugin_root)

            if remote_plugins:
                print("  Wizard Plugin Catalog:")
                for entry in remote_plugins:
                    status = "✅" if entry["installed"] else "  "
                    print(
                        f"    {status} {entry['id']:<16} {entry['version']:<8} {entry['name']}"
                    )
                    description = entry.get("description")
                    if description:
                        print(f"       {description}")
                print()
                print("  Use `PLUGIN install <id>` to copy a catalog entry into extensions.")
            else:
                print("  Wizard plugin catalog is empty or missing.")

            ext_path = self.repo_root / "extensions"
            if ext_path.exists():
                installed = []
                for item in ext_path.iterdir():
                    if item.is_dir():
                        version = "unknown"
                        version_file = item / "version.json"
                        if version_file.exists():
                            try:
                                data = json.loads(version_file.read_text())
                                version = data.get("display") or data.get("version", "unknown")
                            except Exception:
                                version = "error reading version"
                        installed.append((item.name, version))

                if installed:
                    print("\n  Installed Extensions:")
                    for name, version in sorted(installed):
                        print(f"    ✅ {name:15} {version}")
                else:
                    print("\n  No extensions currently installed.")
            else:
                print("\n  Extensions folder not found.")
        except Exception as exc:
            print(f"  ❌ Error listing plugins: {exc}")

    def _plugin_install(self, name: str) -> None:
        """Install a plugin from Wizard's distribution catalog."""
        if not name:
            print("  ❌ Specify a plugin ID to install (use `PLUGIN list`).")
            return

        plugin_src = self.repo_root / "wizard" / "distribution" / "plugins" / name
        if not plugin_src.exists():
            print(f"  ❌ Plugin not found in catalog: {name}")
            return

        try:
            from wizard.services.plugin_repository import get_repository
            from wizard.services.library_manager_service import get_library_manager
        except ImportError as exc:
            print(f"  ❌ Wizard services unavailable: {exc}")
            return

        repo = get_repository()
        repo_entry = repo.get_plugin(name)
        if not repo_entry:
            print(f"  ❌ Plugin registry entry missing for: {name}")
            return

        repo_entry_dict = repo_entry.to_dict()
        manifest_data = load_manifest(plugin_src)
        validation = validate_manifest(manifest_data, name, repo_entry_dict)

        library_root = self.repo_root / "library"
        library_root.mkdir(parents=True, exist_ok=True)
        library_target = library_root / name

        if library_target.exists():
            print(f"  ⚠️  Plugin already copied to library: {name}")
        else:
            try:
                shutil.copytree(plugin_src, library_target)
            except Exception as exc:
                print(f"  ❌ Failed to copy plugin to library: {exc}")
                return

        container_payload = {
            "container": {
                "description": manifest_data.get("description", repo_entry.description),
                "version": manifest_data.get("version", repo_entry.version),
            },
            "repo_path": str(library_target),
        }
        container_file = library_target / "container.json"
        try:
            container_file.write_text(json.dumps(container_payload, indent=2))
        except Exception as exc:
            print(f"  ❌ Failed to write container metadata: {exc}")
            return

        manager = get_library_manager(self.repo_root)
        result = manager.install_integration(name)
        log_plugin_install_event(
            name,
            "uCODE CLI",
            result,
            manifest=manifest_data,
            validation=validation,
        )
        if result.success:
            print(f"  ✅ Plugin installed via LibraryManager: {name}")
            print(f"  → {result.message}")
        else:
            print(f"  ❌ Installation failed: {result.error}")

    def _plugin_remove(self, name: str) -> None:
        """Remove a plugin."""
        try:
            ext_path = self.repo_root / "extensions" / name
            if not ext_path.exists():
                print(f"  ❌ Plugin not found: {name}")
                return

            # Safety confirmation
            print(f"  ⚠️  Remove plugin: {name}?")
            response = input("  Type 'yes' to confirm: ").strip().lower()
            if response == 'yes':
                import shutil
                shutil.rmtree(ext_path)
                print(f"  ✅ Plugin removed: {name}")
            else:
                print("  Cancelled")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _plugin_pack(self, name: str) -> None:
        """Package a plugin for distribution."""
        try:
            ext_path = self.repo_root / "extensions" / name
            if not ext_path.exists():
                print(f"  ❌ Extension not found: {name}")
                return

            # Create distribution package
            dist_path = self.repo_root / "distribution" / "plugins" / name
            print(f"  📦 Packaging {name}...")

            # TODO: Real packaging logic (copy to distribution, create manifest, etc)
            print(f"  [TODO] Package {name} for distribution")
            print(f"         Output: {dist_path}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _load_remote_plugins(self, plugin_root: Path) -> List[Dict[str, Any]]:
        """Read wizard/distribution/plugins manifest entries."""
        entries = []

        if not plugin_root.exists():
            return entries

        for item in sorted(plugin_root.iterdir()):
            if not item.is_dir():
                continue
            manifest_file = item / "manifest.json"
            if not manifest_file.exists():
                continue
            try:
                payload = json.loads(manifest_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            plugin_id = payload.get("id", item.name)
            installed = (self.repo_root / "extensions" / plugin_id).exists()
            entries.append(
                {
                    "id": plugin_id,
                    "name": payload.get("name", plugin_id),
                    "version": payload.get("version", "unknown"),
                    "description": payload.get("description", ""),
                    "installed": installed,
                }
            )
        return entries

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
        1. Current user in service is "ghost" with GUEST role, AND
        2. No configured user identity exists in .env

        Once user runs SETUP and configures identity in .env, they're no longer ghost.
        """
        from core.services.user_service import get_user_manager, UserRole
        from core.services.config_sync_service import ConfigSyncManager

        # Check user service
        user_mgr = get_user_manager()
        current = user_mgr.current()

        # If not ghost in service, definitely not ghost
        if not (current and current.role == UserRole.GUEST and current.username == "ghost"):
            return False

        # If ghost in service, check if they've configured identity in .env
        try:
            sync_mgr = ConfigSyncManager()
            identity = sync_mgr.load_identity_from_env()

            # If they have a username configured in .env, they've run SETUP
            # and are no longer in ghost mode
            if identity.get('user_username'):
                return False
        except Exception:
            # If we can't load config, assume they're ghost
            pass

        return True


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
