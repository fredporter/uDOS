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
from core.services.health_training import read_last_summary
from core.services.hotkey_map import write_hotkey_payload
from core.services.logging_service import get_logger
from core.services.memory_test_scheduler import MemoryTestScheduler
from core.services.self_healer import collect_self_heal_summary
from core.tui.advanced_form_handler import AdvancedFormField
from core.services.system_script_runner import SystemScriptRunner


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
            "EXIT": self._cmd_exit,
            "QUIT": self._cmd_exit,
            "FKEYS": self._cmd_fkeys,
            "FKEY": self._cmd_fkeys,
            "F": self._cmd_fkeys,
        }

        # Conditional commands
        if self.detector.is_available("wizard"):
            self.commands["WIZARD"] = self._cmd_wizard
            self.commands["WIZ"] = self._cmd_wizard

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

        if self.prompt.use_fallback:
            self.logger.info(f"[ContextualPrompt] Using fallback mode: {self.prompt.fallback_reason}")
        else:
            self.logger.info("[ContextualPrompt] Initialized with command suggestions")

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

                    # Parse command
                    parts = user_input.split(None, 1)
                    cmd = parts[0].upper()
                    args = parts[1] if len(parts) > 1 else ""

                    # Check for uCODE commands
                    if cmd in self.commands:
                        self.commands[cmd](args)
                        continue

                    # Special handling for STORY and SETUP commands with forms
                    if cmd in ("STORY", "SETUP"):
                        result = self.dispatcher.dispatch(user_input, parser=self.prompt)

                        # Check if this is a form-based story
                        if result.get("story_form"):
                            collected_data = self._handle_story_form(result["story_form"])
                            
                            # Save collected data if this came from SETUP command
                            if cmd == "SETUP" and collected_data:
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

                        self.state.update_from_handler(result)
                        self.logger.info(f"[COMMAND] {user_input} -> {result.get('status')}")
                        self.state.add_to_history(user_input)
                        continue

                    # Route to core dispatcher with smart parsing
                    # Pass parser so handlers can show interactive menus
                    result = self.dispatcher.dispatch(user_input, parser=self.prompt)
                    self.state.update_from_handler(result)
                    self.logger.info(f"[COMMAND] {user_input} -> {result.get('status')}")
                    self.state.add_to_history(user_input)

                    output = self.renderer.render(result)
                    print(output)

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
        print("\n  💡 Start with: SETUP (first-time) | HELP (all commands) | STORY tui-setup (quick setup)")
        print("     Or try: MAP | TELL location | GOTO location | WIZARD start")
        print("     Press TAB for command selection | Type command for suggestions\n")

    def _show_banner(self) -> None:
        """Show startup banner."""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                        uCODE v1.0.1                           ║
║                 Unified Terminal TUI for uDOS                 ║
║                    Type HELP for commands                     ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(banner)

    def _run_startup_script(self) -> None:
        """Execute the system startup script once per launch."""
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
            payload = {
                "timestamp": datetime.now().isoformat(),
                "self_heal": self.self_heal_summary or {},
                "hot_reload": self.hot_reload_stats or {},
                "hotkeys": hotkey_payload,
            }
            with open(self.health_log_path, "a") as log_file:
                log_file.write(json.dumps(payload) + "\n")
        except Exception as exc:
            self.logger.warning(f"[Health Log] Failed to write summary: {exc}")

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
                token_path = self.repo_root / "memory" / "private" / "wizard_admin_token.txt"

                if token_path.exists():
                    token = token_path.read_text().strip()
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }

                    # Submit to the story endpoint which handles splitting
                    response = requests.post(
                        "http://localhost:8765/api/v1/setup/story/submit",
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

    def _show_component_status(self) -> None:
        """Show detected components."""
        print("\n📦 Component Detection:\n")
        for comp_name, comp in self.components.items():
            status = "✅" if comp.state == ComponentState.AVAILABLE else "❌"
            version_str = f" ({comp.version})" if comp.version else ""
            print(f"  {status} {comp.name.upper():12} {comp.description}{version_str}")
        print()

    def _cmd_status(self, args: str) -> None:
        """Show system status."""
        print("\n═══ uCODE STATUS ═══\n")
        self._show_component_status()

        if self.detector.is_available("wizard"):
            print("🧙 Wizard Server control available: Use WIZARD [start|stop|status]")
        if self.detector.is_available("extensions"):
            print("🔌 Extension management available: Use PLUGIN [list|install|remove]")
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
  RUN [file]          - Execute uPy scripts or USCRIPT files
  DATASET             - Manage data imports and datasets

Navigation & Info:
  MAP                 - Show spatial map
  GOTO [location]     - Travel to location
  FIND [query]        - Search for locations
  TELL [query]        - Get information
  BAG                 - Inventory management

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
        print(help_text)

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

    def _cmd_wizard(self, args: str) -> None:
        """Wizard server control."""
        if not self.detector.is_available("wizard"):
            print("❌ Wizard component not available.")
            return

        parts = args.split(None, 1)
        action = parts[0].lower() if parts else "status"
        subargs = parts[1] if len(parts) > 1 else ""

        if action in ("start", "stop") and self._is_ghost_user():
            print("\n  👻 Ghost mode prevents Wizard server control.")
            print("  Run SETUP in uCODE to unlock a full profile before starting/stopping Wizard.\n")
            return

        if action == "start":
            print("\n🧙 Starting Wizard Server...")
            self._wizard_start()
        elif action == "stop":
            print("\n🧙 Stopping Wizard Server...")
            self._wizard_stop()
        elif action == "status":
            print("\n🧙 Wizard Server Status:")
            self._wizard_status()
        elif action == "console":
            print("\n🧙 Entering Wizard interactive console...")
            self._wizard_console()
        elif action in ("pages", "help"):
            print("\nWizard pages: status, ai, services, quota, devices, logs, config")
        else:
            print(f"\n🧙 Wizard [{action}]:")
            self._wizard_page(action)

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
            if venv_activate.exists():
                cmd = f"source {venv_activate} && python -m wizard.server --no-interactive"
            else:
                cmd = "python -m wizard.server --no-interactive"

            # Start in background with proper I/O isolation
            try:
                with open(os.devnull, 'w') as devnull:
                    with open(os.devnull, 'r') as devnull_in:
                        proc = subprocess.Popen(
                            cmd,
                            shell=True,
                            cwd=str(self.repo_root),
                            stdin=devnull_in,
                            stdout=devnull,
                            stderr=devnull,
                            preexec_fn=os.setsid if sys.platform != 'win32' else None
                        )
            except Exception as start_err:
                raise Exception(f"Failed to spawn wizard process: {start_err}")

            # Wait for server to be ready
            max_wait = 10
            start = time.time()
            while time.time() - start < max_wait:
                try:
                    resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                    if resp.status_code == 200:
                        print(f"  ✅ Wizard Server started (PID: {proc.pid})")
                        sys.stdout.flush()  # Ensure output is flushed
                        return
                except requests.exceptions.ConnectionError:
                    time.sleep(0.5)

            print("  ⚠️  Wizard Server started but not responding (timeout)")
            sys.stdout.flush()

        except Exception as e:
            self.logger.error(f"Failed to start Wizard: {e}")
            print(f"  ❌ Error: {e}")
            sys.stdout.flush()

    def _wizard_stop(self) -> None:
        """Stop Wizard server."""
        try:
            # Kill all python processes running wizard/server.py
            if sys.platform == 'win32':
                cmd = "taskkill /F /IM python.exe"
            else:
                cmd = "pkill -f 'wizard/server.py' || pkill -f 'wizard.server' || true"

            subprocess.run(cmd, shell=True, timeout=5)
            print("  ✅ Wizard Server stopped")
            sys.stdout.flush()  # Ensure output is flushed
            time.sleep(0.5)

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
                "ai": "/api/v1/ai/status",
                "services": "/api/v1/status",
                "devices": "/api/v1/devices",
                "quota": "/api/v1/ai/quota",
                "logs": "/api/v1/logs",
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

        evidence = plugin_src / "manifest.json"
        manifest_data = {}
        if evidence.exists():
            try:
                manifest_data = json.loads(evidence.read_text())
            except Exception:
                pass

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
        """Return True if current user is the demo ghost profile."""
        from core.services.user_service import get_user_manager, UserRole

        user_mgr = get_user_manager()
        current = user_mgr.current()

        return bool(current and current.role == UserRole.GUEST and current.username == "ghost")

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
