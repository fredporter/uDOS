"""uCODE - Unified Terminal TUI
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

from __future__ import annotations

from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import threading
import time
from typing import Any
from urllib.parse import quote, urlparse

import psutil

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.input import ContextualCommandPrompt, create_default_registry
from core.input.confirmation_utils import (
    format_error,
    format_options,
    format_prompt,
    is_help_response,
    normalize_default,
    parse_confirmation,
)
from core.services.background_service_manager import get_wizard_process_manager
from core.services.command_catalog import (
    SUBCOMMAND_ALIASES as SHARED_SUBCOMMAND_ALIASES,
    parse_slash_command,
)
from core.services.command_dispatch_service import match_ucode_command
from core.services.health_training import read_last_summary
from core.services.hotkey_map import write_hotkey_payload
from core.services.loopback_host_utils import is_loopback_host
from core.services.logging_api import (
    get_logger,
    get_repo_root,
    new_corr_id,
    reset_corr_id,
    set_corr_id,
)
from core.services.memory_test_scheduler import MemoryTestScheduler
from core.services.mode_policy import RuntimeMode, mode_summary, resolve_runtime_mode
from core.services.operator_mode_service import get_operator_mode_service
from core.services.network_gate_policy import (
    bootstrap_download_gate,
    close_bootstrap_gate,
    gate_status,
)
from core.services.permission_handler import Permission, get_permission_handler
from core.services.prompt_parser_service import get_prompt_parser_service
from core.services.self_healer import collect_self_heal_summary
from core.services.stdlib_http import HTTPError, http_get, http_post
from core.services.system_script_runner import SystemScriptRunner
from core.services.theme_service import get_theme_service
from core.services.todo_reminder_service import get_reminder_service
from core.services.todo_service import (
    CalendarGridRenderer as TodoCalendarGridRenderer,
    GanttGridRenderer as TodoGanttGridRenderer,
    get_service as get_todo_manager,
)
from core.services.unified_config_loader import get_config
from core.services.viewport_service import ViewportService
from core.ulogic.contracts import IntentFrame
from core.ulogic.parser import parse_primary_input
from core.tui.advanced_form_handler import AdvancedFormField
from core.tui.dispatcher import CommandDispatcher
from core.tui.fkey_handler import FKeyHandler
from core.tui.output import OutputToolkit
from core.tui.renderer import GridRenderer
from core.tui.state import GameState
from core.tui.status_bar import TUIStatusBar
from core.tui.stdout_guard import (
    atomic_print,
    atomic_stdout_write,
    install_stdout_guard,
)
from core.tui.ui_elements import ProgressBar
from core.tui.vibe_dispatch_adapter import get_vibe_adapter
from core.ui.command_selector import CommandSelector
from core.utils.text_width import truncate_ansi_to_width


class ComponentState(Enum):
    """Component availability state."""

    AVAILABLE = "available"
    MISSING = "missing"
    ERROR = "error"


class IOLifecyclePhase(Enum):
    """Prompt/output ownership lifecycle for interactive sessions."""

    INPUT = "input"  # exclusive stdin ownership
    RENDER = "render"  # exclusive stdout ownership
    BACKGROUND = "background"  # no direct stdout writes; queue/defer


@dataclass
class Component:
    """Component registration."""

    name: str
    path: Path
    state: ComponentState
    version: str | None = None
    description: str = ""


class ComponentDetector:
    """Detect and validate available components."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.logger = get_logger("core", category="ucode-detector", name="ucode")
        self.components: dict[str, Component] = {}

    def detect_all(self) -> dict[str, Component]:
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
                description="Core TUI runtime",
            )
        return Component(
            name="core",
            path=path,
            state=ComponentState.MISSING,
            description="Core TUI runtime (missing)",
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
                description="Wizard server & services",
            )
        return Component(
            name="wizard",
            path=path,
            state=ComponentState.MISSING,
            description="Wizard server (not installed)",
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
                wizard_version = self._get_version(
                    self.repo_root / "wizard" / "version.json"
                )
                version = wizard_version or "0.0.0"
            return Component(
                name="extensions",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Extensions + Wizard plugin catalog",
            )
        return Component(
            name="extensions",
            path=path,
            state=ComponentState.MISSING,
            description="Extensions system (not installed)",
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
                description="Desktop GUI application",
            )
        return Component(
            name="app",
            path=path,
            state=ComponentState.MISSING,
            description="Desktop app (not installed)",
        )

    def _get_version(self, version_file: Path) -> str | None:
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


class UCODE:
    """Unified Terminal TUI for uDOS."""


    def __init__(self):
        """Initialize uCODE TUI."""
        install_stdout_guard()
        self.repo_root = get_repo_root()
        self.logger = get_logger("core", category="ucode-tui", name="ucode")
        try:
            from core.services.config_sync_service import ConfigSyncManager

            ConfigSyncManager().hydrate_runtime_env()
        except Exception as exc:
            self.logger.debug(f"[CONFIG] Runtime env hydration skipped: {exc}")
        from core.services.unified_config_loader import get_bool_config, get_config

        self.quiet = get_bool_config("UDOS_QUIET")
        self.ucode_version = get_config("UCODE_VERSION", "1.0.1")
        self.running = False
        self.ghost_mode = False
        # Ensure system seeds are present (startup/reboot/setup stories)
        self._ensure_system_seeds()
        # Component detection
        self.detector = ComponentDetector(self.repo_root)
        self.components = self.detector.detect_all()
        self.dev_mode_config = self._load_dev_mode_config()

        # Core components (always available)
        self.dispatcher = CommandDispatcher()
        self.renderer = GridRenderer()
        self.renderer.set_mood("idle", pace=0.7, blink=True)
        self.state = GameState()

        # Create command registry and contextual prompt (Phase 1)
        self.command_registry = create_default_registry()
        self.prompt = ContextualCommandPrompt(registry=self.command_registry)
        self.ucode_command_set = {
            cmd.name.upper() for cmd in self.command_registry.list_all()
        }

        # Command selector (Phase 3)
        self.command_selector = CommandSelector(self.command_registry)
        self.prompt.set_tab_handler(self._open_command_selector)

        # Function key handler
        self.fkey_handler = FKeyHandler(
            dispatcher=self.dispatcher, prompt=self.prompt, game_state=self.state
        )
        self.prompt.set_function_key_handler(self.fkey_handler)
        self.status_bar = TUIStatusBar()

        # Command registry (maps commands to methods)
        self.commands = {
            "LOCAL": self._cmd_logic_local,
            "EXPLAIN": self._cmd_logic_explain,
            "DIFF": self._cmd_logic_diff,
            "PATCH": self._cmd_logic_patch,
            "ROUTE": self._cmd_logic_route,
            "FALLBACK": self._cmd_logic_fallback,
            "EXIT": self._cmd_exit,
        }
        self.ucode_command_set.add("OPERATOR")
        if self._dev_mode_active():
            self.ucode_command_set.update(self.commands.keys())
            self.ucode_command_set.add("LOGIC")
        # Conditional commands
        # WIZARD command now handled by dispatcher (WizardHandler)

        self.health_log_path = (
            self.repo_root / "memory" / "logs" / "health-training.log"
        )
        self.health_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.self_heal_summary: dict[str, Any] | None = None
        self.hot_reload_mgr = None
        self.hot_reload_stats: dict[str, Any] | None = None
        self.previous_health_log: dict[str, Any] | None = None
        self.logic_local_outputs: list[dict[str, Any]] = []
        self.logic_local_counter = 0
        self.logic_local_limit = 50
        self._setup_health_monitoring()
        self.system_script_runner = SystemScriptRunner()
        self.memory_test_scheduler: MemoryTestScheduler | None = None
        self.memory_test_summary: dict[str, Any] | None = None
        self.theme = get_theme_service()
        self.todo_manager = get_todo_manager()
        self.calendar_renderer = TodoCalendarGridRenderer()
        self.gantt_renderer = TodoGanttGridRenderer()
        self.prompt_parser = get_prompt_parser_service()
        self.todo_reminder = get_reminder_service(self.todo_manager)
        self._init_operator_prompt_context()
        self._io_phase = IOLifecyclePhase.BACKGROUND
        self._io_phase_lock = threading.RLock()

        # Initialize routing components without vibe.core runtime dependencies.
        try:
            from core.services.interactive_runtime import (
                CommandEngine,
                InputRouter,
                ResponseNormaliser,
            )
            from wizard.services.provider_registry import get_provider_registry

            self.input_router = InputRouter(
                shell_enabled=True, ucode_confidence_threshold=0.80
            )
            self.command_engine = CommandEngine()
            self.response_normaliser = ResponseNormaliser()
            self.provider_registry = get_provider_registry()
            self._register_providers()
            self.provider_engine = None
            self.logger.info("[v1.5.1] Routing components initialized")
        except Exception as exc:
            self.logger.warning(f"[v1.5.1] Failed to initialize routing: {exc}")
            # Fallback to None - old routing will be used
            self.input_router = None
            self.command_engine = None
            self.response_normaliser = None
            self.provider_engine = None
            self.provider_registry = None

        if self.prompt.use_fallback:
            self.logger.info(
                f"[ContextualPrompt] Using fallback mode: {self.prompt.fallback_reason}"
            )
        else:
            self.logger.info("[ContextualPrompt] Initialized with command suggestions")
        if not self.quiet:
            mode = "fallback" if self.prompt.use_fallback else "advanced"
            from core.services.unified_config_loader import get_config

            profile = get_config("UDOS_KEYMAP_PROFILE", "auto")
            self._ui_line(f"Prompt mode: {mode} | keymap: {profile}", level="info")

    def _ensure_system_seeds(self) -> None:
        """Seed /memory/system files if they are missing."""
        try:
            from core.framework.seed_installer import SeedInstaller

            system_dir = self.repo_root / "memory" / "system"
            required = ["startup-script.md", "reboot-script.md", "tui-setup-story.md"]
            missing = [name for name in required if not (system_dir / name).exists()]
            if missing:
                installer = SeedInstaller()
                installer.install_system_seeds(force=False)
                self.logger.info(
                    f"[LOCAL] Seeded memory/system files: {', '.join(missing)}"
                )
        except Exception as e:
            self.logger.warning(f"[LOCAL] System seed check failed: {e}")

    def _register_providers(self) -> None:
        """Register available providers with the routing registry."""
        import asyncio
        from wizard.services.provider_registry import ProviderType
        from wizard.services.adapters import MistralAdapter

        # Try registering Mistral (cloud)
        try:
            api_key = get_config("MISTRAL_API_KEY", "")
            if api_key:
                mistral = MistralAdapter(api_key=api_key)
                if asyncio.run(mistral.is_available()):
                    self.provider_registry.register_provider(
                        ProviderType.MISTRAL,
                        api_key=api_key,
                        default_model="mistral-small-latest",
                        priority=1,
                    )
                    self.logger.info("[v1.4.6] Registered Mistral provider")
        except Exception as exc:
            self.logger.warning(f"[v1.4.6] Failed to register Mistral: {exc}")

    def _handle_special_commands(self, command: str) -> bool:
        """Handle special REPL commands (EXIT/STATUS/HISTORY)."""
        if not command:
            return False
        parts = command.strip().split(None, 1)
        cmd = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in {"HELP", "STATUS"}:
            full_cmd = f"{cmd} {args}".strip()
            self.dispatcher.dispatch(
                full_cmd, parser=self.prompt, game_state=self.state
            )
            return True

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
            atomic_print("No history yet.")
            return
        lines = ["Recent history:"] + [f"  {entry}" for entry in history]
        atomic_stdout_write("\n".join(lines) + "\n")

    @staticmethod
    def _emit_lines(lines: list[str]) -> None:
        """Emit a set of lines as one stdout write to avoid interleaving."""
        if not lines:
            return
        atomic_stdout_write("\n".join(lines) + "\n")

    def _get_io_phase(self) -> IOLifecyclePhase:
        with self._io_phase_lock:
            return self._io_phase

    def _set_io_phase(self, phase: IOLifecyclePhase) -> None:
        with self._io_phase_lock:
            self._io_phase = phase

    @contextmanager
    def _io_phase_scope(self, phase: IOLifecyclePhase):
        previous = self._get_io_phase()
        self._set_io_phase(phase)
        try:
            yield
        finally:
            self._set_io_phase(previous)

    def _is_ucode_command(self, token: str) -> bool:
        """Return True if token is a known uCODE command."""
        return token.strip().upper() in self.ucode_command_set

    def _ucode_aliases(self) -> dict[str, str]:
        aliases = dict(SHARED_SUBCOMMAND_ALIASES)
        aliases.update({"?": "HELP", "H": "HELP", "LS": "BINDER"})
        return aliases

    def _match_ucode_command(self, input_str: str) -> tuple[str | None, float]:
        tokens = input_str.strip().split()
        if not tokens:
            return None, 0.0
        first = tokens[0].upper()
        if alias_target := self._ucode_aliases().get(first):
            return alias_target, 1.0
        return match_ucode_command(input_str)

    def _execute_ucode_command(self, cmd: str, rest: str) -> dict[str, Any]:
        full_cmd = f"{cmd} {rest}".strip()
        if cmd in self.commands and cmd not in self.dispatcher.handlers:
            self.commands[cmd](rest)
            return {"status": "success", "command": cmd}
        return self.dispatcher.dispatch(
            full_cmd, parser=self.prompt, game_state=self.state
        )

    def _dispatch_with_vibe(self, user_input: str) -> dict[str, Any]:
        """Three-stage dispatch with Dev extension vibe routing and local operator fallback.

        Uses command-first dispatch for:
          1. uCODE command matching (fuzzy, confidence scoring)
          2. Shell validation (safety checks)
          3. Dev extension skill routing
          4. Non-dev local operator fallback
          5. Dev-only logic fallback

        Returns:
            Dict with status, message, and routed result
        """
        adapter = get_vibe_adapter()
        dev_mode = resolve_runtime_mode() == RuntimeMode.DEV

        # Pass confirmation function for fuzzy matches (0.80-0.95 confidence)
        result = adapter.dispatch(
            user_input,
            ask_confirm_fn=self._ask_confirm,
            allow_skill_routing=dev_mode,
            allow_model_fallback=dev_mode,
        )

        # Log dispatch decision
        self.logger.debug(
            f"[Dispatch] {result.status}: cmd={result.command}, "
            f"skill={result.skill}, confidence={result.confidence}",
            extra={"user_input": user_input},
        )

        # Handle different result types
        if result.status == "success" and result.command:
            # uCODE command matched and confirmed (confidence ≥ 0.95 or confirmed at 0.80-0.95)
            rest = ""
            parts = user_input.strip().split(None, 1)
            if len(parts) > 1:
                rest = parts[1]
            return self._execute_ucode_command(result.command, rest)

        elif result.status == "dev_tool_routed":
            # Routed to a Dev Mode contributor tool skill from the reduced contributor set.
            skill = result.skill
            action = result.action

            self.logger.info(
                f"Dev extension skill routed: {skill}.{action}",
                extra={"user_input": user_input, "skill": skill, "action": action},
            )

            # For now, show message indicating routing to the contributor subset.
            message = f"Routing to Dev extension skill: {skill}"
            if action:
                message += f" → {action}"

            return {
                "status": "dev_tool_routed",
                "message": message,
                "skill": skill,
                "action": action,
                "command": f"{skill}:{action}",
            }

        elif result.status == "fallback_local":
            return self._route_to_operator(user_input)

        elif result.validation_reason == "shell_valid":
            # Shell command passed validation
            return self._execute_shell_command(user_input)

        elif result.status == "fallback_ok":
            # Fallback to logic-assist system
            self.logger.debug(f"Falling back to LOGIC: {user_input}")
            self._run_logic_request(
                user_input,
                mode="LOCAL",
                use_cloud=(self._get_dev_mode_primary_provider() == "cloud"),
            )
            return {
                "status": "success",
                "command": "LOGIC",
                "message": result.message,
                "dispatch_reason": "logic_fallback",
            }

        else:
            # Error or unhandled case
            if result.status == "error":
                return {"status": "error", "message": result.message}

            # Fallback to logic-assist as ultimate fallback
            self._run_logic_request(
                user_input,
                mode="LOCAL",
                use_cloud=(self._get_dev_mode_primary_provider() == "cloud"),
            )
            return {
                "status": "success",
                "command": "LOGIC",
                "message": result.message,
                "dispatch_reason": "final_fallback",
            }

    def _record_routing_event(
        self, frame: IntentFrame, route: str, command_text: str | None = None
    ) -> None:
        detail = f"{frame.input_class}:{frame.intent}"
        if command_text:
            detail += f" -> {command_text}"
        self.logger.info(
            f"[ROUTE] {route} {detail}",
            extra={
                "route": route,
                "input_class": frame.input_class,
                "intent": frame.intent,
                "command_text": command_text,
                "confidence": frame.confidence,
                "source": frame.source,
            },
        )

    def _with_route_metadata(
        self,
        result: dict[str, Any],
        frame: IntentFrame,
        route: str,
        command_text: str | None = None,
    ) -> dict[str, Any]:
        routed = dict(result)
        routed["routing"] = {
            "route": route,
            "input_class": frame.input_class,
            "intent": frame.intent,
            "confidence": frame.confidence,
            "source": frame.source,
            "command_text": command_text,
        }
        return routed

    def _dispatch_text_command(
        self, command_text: str, frame: IntentFrame, route: str
    ) -> dict[str, Any]:
        self._record_routing_event(frame, route, command_text)
        result = self.dispatcher.dispatch(
            command_text,
            parser=self.prompt,
            game_state=self.state,
        )
        return self._with_route_metadata(result, frame, route, command_text)

    def _route_workflow_frame(self, frame: IntentFrame) -> dict[str, Any]:
        slots = frame.slots
        intent = frame.intent
        workflow_id = str(slots.get("workflow_id", "")).strip()
        template_id = str(slots.get("template_id", "")).strip()

        if intent == "workflow.list":
            return self._dispatch_text_command(
                "WORKFLOW LIST TEMPLATES", frame, "dispatch.workflow"
            )
        if intent == "workflow.status" and workflow_id:
            return self._dispatch_text_command(
                f"WORKFLOW STATUS {workflow_id}", frame, "dispatch.workflow"
            )
        if intent == "workflow.run" and workflow_id:
            return self._dispatch_text_command(
                f"WORKFLOW RUN {workflow_id}", frame, "dispatch.workflow"
            )
        if intent == "workflow.approve" and workflow_id:
            return self._dispatch_text_command(
                f"WORKFLOW APPROVE {workflow_id}", frame, "dispatch.workflow"
            )
        if intent == "workflow.escalate" and workflow_id:
            return self._dispatch_text_command(
                f"WORKFLOW ESCALATE {workflow_id}", frame, "dispatch.workflow"
            )
        if intent == "workflow.new" and template_id and workflow_id:
            return self._dispatch_text_command(
                f"WORKFLOW NEW {template_id} {workflow_id}",
                frame,
                "dispatch.workflow",
            )

        self._record_routing_event(frame, "dispatch.guidance")
        return self._with_route_metadata(
            self._route_to_operator(
                "Create a workflow runbook plan for: "
                f"{template_id or workflow_id or frame.intent}"
            ),
            frame,
            "dispatch.guidance",
        )

    @staticmethod
    def _template_family_aliases() -> dict[str, str]:
        return {
            "workflow": "workflows",
            "workflows": "workflows",
            "mission": "missions",
            "missions": "missions",
            "capture": "captures",
            "captures": "captures",
            "submission": "submissions",
            "submissions": "submissions",
        }

    def _parse_template_reference(
        self, raw_ref: str
    ) -> tuple[str | None, str | None]:
        normalized = raw_ref.strip().strip("/")
        if not normalized:
            return None, None
        parts = [part for part in normalized.split("/") if part]
        if len(parts) >= 2:
            family = self._template_family_aliases().get(parts[0].lower())
            template_name = parts[-1]
            return family, template_name

        token = parts[0]
        family = self._template_family_aliases().get(token.lower())
        if family:
            return family, None

        lower = token.lower()
        if "workflow" in lower:
            return "workflows", token
        if "mission" in lower:
            return "missions", token
        if "capture" in lower:
            return "captures", token
        if "submission" in lower or "device" in lower:
            return "submissions", token
        return None, token

    def _knowledge_text_command(
        self, action: str, text: str, frame: IntentFrame
    ) -> dict[str, Any]:
        command_text = f"UCODE {action} prompt shell://input {text.strip()}".strip()
        return self._dispatch_text_command(
            command_text,
            frame,
            "dispatch.knowledge",
        )

    def _route_knowledge_frame(self, frame: IntentFrame) -> dict[str, Any]:
        slots = frame.slots
        intent = frame.intent
        if intent == "knowledge.browse":
            knowledge_path = str(slots.get("knowledge_path", "")).strip()
            family, template_name = self._parse_template_reference(knowledge_path)
            if family and template_name:
                return self._dispatch_text_command(
                    f"UCODE TEMPLATE READ {family} {template_name}",
                    frame,
                    "dispatch.knowledge",
                )
            if family:
                return self._dispatch_text_command(
                    f"UCODE TEMPLATE LIST {family}",
                    frame,
                    "dispatch.knowledge",
                )
            return self._dispatch_text_command(
                "UCODE TEMPLATE LIST",
                frame,
                "dispatch.knowledge",
            )

        if intent == "knowledge.duplicate":
            source_path = str(slots.get("source_path", "")).strip()
            target_path = str(slots.get("target_path", "")).strip()
            family, template_name = self._parse_template_reference(source_path)
            target_name = Path(target_path).name if target_path else ""
            if family and template_name and target_name:
                return self._dispatch_text_command(
                    f"UCODE TEMPLATE DUPLICATE {family} {template_name} {target_name}",
                    frame,
                    "dispatch.knowledge",
                )
            self._record_routing_event(frame, "dispatch.guidance")
            return self._with_route_metadata(
                self._route_to_operator(
                    f"Plan a template duplication for {source_path} into {target_path}"
                ),
                frame,
                "dispatch.guidance",
            )

        if intent == "knowledge.capture":
            return self._knowledge_text_command(
                "ENRICH", str(slots.get("text", "")).strip(), frame
            )
        if intent == "knowledge.research":
            return self._knowledge_text_command(
                "RESEARCH", str(slots.get("text", "")).strip(), frame
            )
        if intent == "knowledge.generate":
            return self._knowledge_text_command(
                "GENERATE", str(slots.get("text", "")).strip(), frame
            )

        self._record_routing_event(frame, "dispatch.guidance")
        return self._with_route_metadata(
            self._route_to_operator(str(slots.get("text", frame.intent))),
            frame,
            "dispatch.guidance",
        )

    def _route_guidance_frame(self, frame: IntentFrame) -> dict[str, Any]:
        prompt = str(frame.slots.get("text", "")).strip() or frame.intent
        self._record_routing_event(frame, "dispatch.guidance")
        return self._with_route_metadata(
            self._route_to_operator(prompt),
            frame,
            "dispatch.guidance",
        )

    def _route_frame(self, frame: IntentFrame) -> dict[str, Any]:
        outcome = frame.routing_outcome()
        if outcome.route == "dispatch.command":
            command_text = str(frame.slots.get("command_text", "")).strip()
            if not command_text:
                return {
                    "status": "error",
                    "message": "Command frame missing command text",
                    "routing": {
                        "route": "dispatch.reject",
                        "input_class": frame.input_class,
                        "intent": frame.intent,
                        "confidence": frame.confidence,
                        "source": frame.source,
                        "command_text": None,
                    },
                }
            cmd, confidence = self._match_ucode_command(command_text)
            if cmd and confidence >= 0.8:
                rest = ""
                parts = command_text.strip().split(None, 1)
                if len(parts) > 1:
                    rest = parts[1]
                self._record_routing_event(frame, outcome.route, command_text)
                result = self._execute_ucode_command(cmd, rest)
                return self._with_route_metadata(result, frame, outcome.route, command_text)
            return self._dispatch_text_command(command_text, frame, outcome.route)
        if outcome.route == "dispatch.workflow":
            return self._route_workflow_frame(frame)
        if outcome.route == "dispatch.knowledge":
            return self._route_knowledge_frame(frame)
        if outcome.route == "dispatch.guidance":
            return self._route_guidance_frame(frame)
        return {
            "status": "error",
            "message": "Unable to route input",
            "routing": {
                "route": "dispatch.reject",
                "input_class": frame.input_class,
                "intent": frame.intent,
                "confidence": frame.confidence,
                "source": frame.source,
                "command_text": None,
            },
        }

    def _route_input(self, user_input: str) -> dict[str, Any]:
        """Route input based on operator/dev prefixes or slash mode.

        Returns:
            Dict with status, message, and routed result
        """
        user_input = user_input.strip()
        if not user_input:
            return {"status": "error", "message": "Empty input"}

        # Mode 1: operator prompt shorthand
        if user_input.startswith("?"):
            prompt = user_input[1:].strip()
            if not prompt:
                return {"status": "error", "message": "Operator prompt required"}
            return self._route_to_operator(prompt)

        lowered = user_input.lower()
        if lowered == "operator" or lowered.startswith("operator "):
            return self._handle_operator_prefix(user_input)

        if lowered == "logic" or lowered.startswith("logic "):
            return self._handle_logic_prefix(user_input)

        # Mode 2: Slash mode
        if user_input.startswith("/"):
            return self._handle_slash_input(user_input)

        # Mode 3: v1.5 deterministic input contract
        frame = parse_primary_input(user_input)
        if frame and (frame.input_class != "guidance" or not self._dev_mode_active()):
            return self._route_frame(frame)

        # Mode 4: Dev extension routing / provider fallback
        return self._dispatch_with_vibe(user_input)

    def _dev_mode_active(self) -> bool:
        return resolve_runtime_mode() == RuntimeMode.DEV

    def _route_to_operator(self, prompt: str) -> dict[str, Any]:
        operator_service = get_operator_mode_service()
        plan = operator_service.plan(prompt)
        lines = [
            f"Operator intent: {plan.intent.label} ({plan.intent.confidence:.2f})",
            plan.summary,
        ]
        for action_item in plan.actions:
            lines.append(f"- {action_item.command}: {action_item.description}")
        return {
            "status": "operator_plan",
            "message": "Local operator guidance ready",
            "output": "\n".join(lines),
            "operator_plan": {
                "summary": plan.summary,
                "intent": {
                    "label": plan.intent.label,
                    "confidence": plan.intent.confidence,
                    "reason": plan.intent.reason,
                },
                "actions": [
                    {
                        "type": action_item.action_type,
                        "command": action_item.command,
                        "safe": action_item.safe,
                        "description": action_item.description,
                    }
                    for action_item in plan.actions
                ],
            },
        }

    def _handle_operator_prefix(self, user_input: str) -> dict[str, Any]:
        parts = user_input.split(None, 1)
        if len(parts) == 1:
            return self.dispatcher.dispatch(
                "UCODE OPERATOR STATUS", parser=self.prompt, game_state=self.state
            )
        normalized = parts[1].strip()
        if not normalized:
            return self.dispatcher.dispatch(
                "UCODE OPERATOR STATUS", parser=self.prompt, game_state=self.state
            )
        upper = normalized.upper()
        if upper.startswith(("STATUS", "QUEUE", "PLAN ")):
            return self.dispatcher.dispatch(
                f"UCODE OPERATOR {normalized}",
                parser=self.prompt,
                game_state=self.state,
            )
        return self._route_to_operator(normalized)

    def _legacy_dev_only_response(self, original: str) -> dict[str, Any]:
        return {
            "status": "warning",
            "message": "Legacy helper surface is Dev Mode only",
            "output": (
                f"`{original}` is reserved for Dev Mode.\n"
                "Standard runtime uses OPERATOR and UCODE OPERATOR.\n"
                "Use: OPERATOR <prompt>\n"
                "Or: UCODE OPERATOR STATUS\n"
                "Use the Wizard-managed /dev extension lane when you need contributor tooling."
            ),
        }

    def _handle_logic_prefix(self, user_input: str) -> dict[str, Any]:
        parts = user_input.split(None, 1)
        normalized = parts[1].strip() if len(parts) > 1 else ""
        prefix = parts[0].upper() if parts else "LOGIC"

        if not normalized:
            return (
                self._legacy_dev_only_response(prefix)
                if not self._dev_mode_active()
                else {"status": "error", "message": "Logic prompt required"}
            )

        logic_parts = normalized.split(None, 1)
        cmd_name = logic_parts[0].upper()
        args = logic_parts[1] if len(logic_parts) > 1 else ""

        if not self._dev_mode_active():
            if cmd_name in {"LOCAL", "ROUTE"}:
                return self._route_to_operator(args or normalized)
            if cmd_name == "SETUP":
                return {
                    "status": "warning",
                    "message": "Standard runtime setup is operator-first",
                    "output": (
                        "Legacy `LOGIC SETUP` shorthand is retired in standard runtime.\n"
                        "Use: SETUP\n"
                        "Then: UCODE PROFILE LIST\n"
                        "And: UCODE OPERATOR STATUS"
                    ),
                }
            return self._legacy_dev_only_response(f"{prefix} {cmd_name}")

        use_cloud = self._get_dev_mode_primary_provider() == "cloud"
        if cmd_name == "CLOUD":
            use_cloud = True
            normalized = args
            logic_parts = normalized.split(None, 1)
            cmd_name = logic_parts[0].upper() if logic_parts and logic_parts[0] else ""
            args = logic_parts[1] if len(logic_parts) > 1 else ""
        if cmd_name == "SETUP":
            self._run_dev_mode_setup()
            return {"status": "success", "command": "LOGIC SETUP"}
        if cmd_name in {"LOCAL", "EXPLAIN", "DIFF", "PATCH", "ROUTE"}:
            if use_cloud and cmd_name in {"EXPLAIN", "DIFF", "PATCH"} and "--cloud" not in args:
                args = f"{args} --cloud".strip()
            self.commands[cmd_name](args)
            return {"status": "success", "command": cmd_name}
        if cmd_name == "FALLBACK":
            self._cmd_logic_fallback(args)
            return {"status": "success", "command": cmd_name}
        self._run_logic_request(normalized, mode="LOCAL", use_cloud=use_cloud)
        return {"status": "success", "command": "LOGIC"}

    def _validate_shell_safety(self, command: str) -> bool:
        """Validate shell command safety (v1.4.6).

        Basic safety check for shell commands.
        Returns True if command appears safe to execute.
        """
        # Block obviously dangerous commands
        dangerous_patterns = [
            "rm -rf /",
            "mkfs",
            ":(){ :|:& };:",  # fork bomb
            "/dev/sd",  # direct disk access
        ]

        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return False

        return True

    def _execute_command_impl(self, command: str, args: str) -> tuple[bool, str, str]:
        """Execute ucode command (adapter for CommandEngine).

        Checks permissions for dangerous operations before execution.

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Check permissions for dangerous commands
            perm_result = self._check_command_permission(command, args)
            if not perm_result["allowed"]:
                return (False, "", perm_result["error"])

            if command in self.commands:
                # Route to existing command handler
                self.commands[command](args)
                return (True, "", "")
            else:
                return (False, "", f"Unknown command: {command}")
        except Exception as exc:
            return (False, "", str(exc))

    def _check_command_permission(self, command: str, args: str) -> dict[str, Any]:
        """Check if user has permission to execute command.

        Args:
            command: Command name
            args: Command arguments

        Returns:
            Dict with 'allowed' (bool) and 'error' (str) keys
        """
        try:
            handler = get_permission_handler()
            command_upper = command.upper()

            # Define dangerous commands requiring specific permissions
            dangerous_commands = {
                "DESTROY": Permission.DESTROY,
                "DELETE": Permission.DESTROY,
                "PURGE": Permission.DESTROY,
                "REPAIR": Permission.REPAIR,
                "RESTORE": Permission.REPAIR,
                "RESET": Permission.DESTROY,
            }

            # Check if command requires special permission
            if command_upper in dangerous_commands:
                required_perm = dangerous_commands[command_upper]

                # Check permission (testing mode returns True with warning)
                if handler.has_permission(required_perm):
                    # Log successful permission check
                    handler.log_check(
                        required_perm,
                        granted=True,
                        context={"command": command_upper, "args": args},
                    )
                    return {"allowed": True}
                else:
                    # Permission denied
                    handler.log_denied(
                        required_perm, context={"command": command_upper, "args": args}
                    )
                    return {
                        "allowed": False,
                        "error": f"Permission denied: {command_upper} requires {required_perm.value} permission",
                    }

            # Non-dangerous commands always allowed
            return {"allowed": True}

        except Exception as exc:
            # Log error but don't block execution (v1.4.x testing mode)
            self.logger.warning(f"Permission check error: {exc}")
            return {"allowed": True}

    def _route_to_provider(self, prompt: str) -> dict[str, Any]:
        """Route natural language input to the logic-assist provider lane.

        Uses ProviderRegistry for capability-based selection.
        Normalises response before any execution.

        Args:
            prompt: Natural language prompt

        Returns:
            Dict with status and response
        """
        import asyncio

        # Fallback to old system if new routing not available
        if not self.response_normaliser or not self.provider_registry:
            self.logger.warning(
                "[v1.5.1] Provider runtime not available, using legacy routing"
            )
            self._run_logic_request(
                prompt, mode="LOCAL", use_cloud=(self._get_dev_mode_primary_provider() == "cloud")
            )
            return {"status": "success", "command": "LOGIC"}

        # Determine task mode (code, conversation, etc.)
        mode = self._infer_task_mode(prompt)

        # Select provider
        try:
            provider_type, model = self.provider_registry.select_provider_for_task(
                mode=mode, prefer_local=True
            )
        except RuntimeError as exc:
            return {"status": "error", "message": f"No provider available: {exc}"}

        # Call provider
        self._ui_line(f"LOGIC → {provider_type.value} ({model})", level="info")

        from wizard.services.cloud_provider_executor import run_cloud_with_fallback_detail
        from wizard.services.provider_registry import ProviderStatus, ProviderType

        try:
            cloud_result = run_cloud_with_fallback_detail(prompt)
            result_provider = str(cloud_result.get("provider") or provider_type.value)
            result_model = str(cloud_result.get("model") or model)
            raw_response = str(cloud_result.get("response") or "")
            normalised = self.response_normaliser.normalise(raw_response)
            success = True
            error = None
            status = ProviderStatus.AVAILABLE
        except Exception as exc:
            result_provider = provider_type.value
            result_model = model
            normalised = self.response_normaliser.normalise("")
            success = False
            error = str(exc)
            status = ProviderStatus.ERROR

        # Record telemetry
        try:
            actual_provider = ProviderType(result_provider)
        except ValueError:
            actual_provider = provider_type
        self.provider_registry.record_call(
            actual_provider, success, 0.0, status
        )

        if not success:
            return {
                "status": "error",
                "message": error or "Provider call failed",
            }

        # Display response
        self.renderer.stream_text(normalised.text, prefix="logic> ")

        # Check for extracted ucode commands (but DO NOT auto-execute)
        if normalised.contains_ucode:
            self._ui_line(
                f"Response contains {len(normalised.ucode_commands)} ucode commands",
                level="warn",
            )
            # Future: Prompt user for confirmation before execution

        return {
            "status": "success",
            "command": "LOGIC",
            "response": normalised.text,
            "provider": result_provider,
            "model": result_model,
        }

    def _infer_task_mode(self, prompt: str) -> str:
        """Infer task mode from prompt (v1.4.6).

        Simple heuristics for now. Future: use the logic-assist model for classification.

        Args:
            prompt: User prompt

        Returns:
            Task mode string (code, conversation, etc.)
        """
        prompt_lower = prompt.lower()

        code_keywords = {
            "write",
            "code",
            "function",
            "class",
            "refactor",
            "debug",
            "implement",
        }
        if any(kw in prompt_lower for kw in code_keywords):
            return "code"

        return "conversation"

    def _handle_slash_input(self, user_input: str) -> dict[str, Any]:
        """Handle slash-prefixed input.

        If first token is a known slash command, route to uCODE.
        Otherwise, treat as shell command.
        """
        parsed = parse_slash_command(user_input)
        if not parsed or not parsed.first_token:
            return {"status": "error", "message": "Empty slash command"}

        if self._is_ucode_command(parsed.first_token):
            return self.dispatcher.dispatch(
                parsed.normalized_ucode_command,
                parser=self.prompt,
                game_state=self.state,
            )

        return self._execute_shell_command(parsed.body)

    def _execute_shell_command(self, shell_cmd: str) -> dict[str, Any]:
        """Execute a shell command safely.

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
                timeout=30,
            )

            output = result.stdout or result.stderr
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": output or "Command executed successfully",
                    "shell_output": output,
                }
            else:
                return {
                    "status": "error",
                    "message": output
                    or f"Command failed with exit code {result.returncode}",
                    "shell_output": output,
                }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out (30s limit)"}
        except Exception as e:
            return {"status": "error", "message": f"Shell execution failed: {e!s}"}

    def _handle_question_mode(self, user_input: str) -> dict[str, Any]:
        """Compatibility path for dispatch; delegates to canonical route."""
        return self._dispatch_with_vibe(user_input)

    def run(self) -> None:
        """Start uCODE TUI."""
        self.running = True
        self._run_startup_sequence()

        # Check if in ghost mode and prompt for setup
        self._check_ghost_mode()
        self._show_mode_policy_summary()
        self._show_first_run_ai_setup_hint()
        self._show_first_run_offline_hint()

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
                    # input phase: exclusive stdin ownership
                    with self._io_phase_scope(IOLifecyclePhase.INPUT):
                        self._show_status_bar()
                        user_input = self.prompt.ask_command(self._prompt_text())

                    if not user_input:
                        continue

                    # Route input based on operator/dev prefixes or slash mode
                    # This implements the uCODE Prompt Spec
                    corr_id = new_corr_id("C")
                    token = set_corr_id(corr_id)
                    try:
                        # render phase: exclusive stdout ownership
                        with self._io_phase_scope(IOLifecyclePhase.RENDER):
                            result = self._route_input(user_input)

                            # Check for EXIT before processing
                            normalized_input = user_input.strip().upper()
                            if normalized_input in (
                                "EXIT",
                                "?EXIT",
                                "? EXIT",
                                "LOGIC EXIT",
                                "OPERATOR EXIT",
                            ):
                                self.running = False
                                atomic_print("See you later!")
                                break

                            # Special handling for STORY and SETUP commands with forms
                            normalized_cmd = result.get("command", "").upper()
                            if normalized_cmd in ("STORY", "SETUP"):
                                # Check if this is a form-based story
                                if result.get("story_form"):
                                    collected_data = self._handle_story_form(
                                        result["story_form"]
                                    )

                                    # Save collected data if this came from SETUP command
                                    if normalized_cmd == "SETUP" and collected_data:
                                        self._save_user_profile(collected_data)

                                        # Reload Ghost Mode status after profile update
                                        old_ghost_mode = self.ghost_mode
                                        self.ghost_mode = self._is_ghost_user()

                                        # Notify user if they've exited Ghost Mode
                                        if old_ghost_mode and not self.ghost_mode:
                                            atomic_stdout_write("\n")
                                            self._ui_line(
                                                "Ghost Mode disabled - full access granted!",
                                                level="ok",
                                                mood="🎉",
                                            )

                                    atomic_stdout_write("\n")
                                    self._emit_lines([
                                        self._theme_text(
                                            OutputToolkit.line(
                                                "Setup form completed", level="ok"
                                            )
                                        ),
                                        self._theme_text(
                                            OutputToolkit.line(
                                                f"Collected {len(collected_data)} values",
                                                level="info",
                                            )
                                        ),
                                    ])
                                    if collected_data:
                                        self._emit_lines([
                                            "",
                                            self._theme_text(
                                                OutputToolkit.line(
                                                    "Data saved. Next steps:",
                                                    level="milestone",
                                                )
                                            ),
                                            self._theme_text(
                                                "  › SETUP --profile    - View your profile"
                                            ),
                                            self._theme_text(
                                                "  › CONFIG             - View variables"
                                            ),
                                        ])
                                else:
                                    # Show the result for non-form stories
                                    output = self.renderer.render(result)
                                    atomic_print(output)
                            else:
                                # Render normal command output
                                output = self.renderer.render(result)
                                atomic_print(output)

                        self.state.update_from_handler(result)
                        self.logger.info(
                            f"[COMMAND] {user_input} -> {result.get('status')}",
                            ctx={"corr_id": corr_id},
                        )
                        self.state.add_to_history(user_input)
                    finally:
                        reset_corr_id(token)

                except KeyboardInterrupt:
                    atomic_stdout_write("\n")
                    continue
                except Exception as e:
                    reset_corr_id(token)
                    self.logger.error(f"[ERROR] {e}", exc_info=True)
                    self._ui_line(str(e), level="error")

        except KeyboardInterrupt:
            atomic_stdout_write("\n")
            self._ui_line("Interrupt. Type EXIT to quit.", level="warn")
        except EOFError:
            self.running = False
        finally:
            self._cleanup()

    @staticmethod
    def _prompt_text() -> str:
        """Return the canonical single-entry uCODE prompt label."""
        return "▶ "

    def _print_task_progress(self, phase: str, label: str, percent: int) -> None:
        """Render a consistent phase progress bar."""
        if self.quiet:
            return
        pct = max(0, min(100, int(percent)))
        bar = ProgressBar(total=100, width=28).render(pct, label=phase.upper())
        atomic_print(
            self._theme_text(OutputToolkit.line(f"{bar}  {label}", level="progress"))
        )

    def _ui_line(
        self, message: str, level: str = "info", mood: str | None = None
    ) -> None:
        """Render a themed line with consistent symbols and spacing."""
        atomic_print(
            self._theme_text(OutputToolkit.line(message, level=level, mood=mood))
        )

    def _run_with_progress(
        self,
        phase: str,
        label: str,
        func: Callable[[], Any],
        *,
        spinner_label: str | None = None,
        mood: str = "busy",
    ) -> Any:
        """Run a long action with consistent progress-bar + spinner output."""
        self._print_task_progress(phase, label, 0)
        try:
            if self.quiet:
                result = func()
            else:
                result = self._run_with_spinner(
                    spinner_label or f"⏳ {label}", func, mood=mood
                )
        except Exception:
            self._print_task_progress(phase, f"{label} failed", 100)
            raise
        self._print_task_progress(phase, f"{label} complete", 100)
        return result

    def _run_startup_sequence(self) -> None:
        """Run startup steps with consistent progress bars + spinner feedback."""
        from core.services.unified_config_loader import get_bool_config

        clean_startup = get_bool_config("UDOS_TUI_CLEAN_STARTUP", default=True)
        startup_extras = get_bool_config("UDOS_TUI_STARTUP_EXTRAS", default=False)
        steps = [
            ("loading", "Rendering banner", self._show_banner, True),
            ("loading", "Detecting environment", self._autodetect_environment, True),
            ("loading", "Measuring viewport", self._refresh_viewport, True),
            ("installation", "Running startup scripts", self._run_startup_script, True),
            ("loading", "Computing health summary", self._show_health_summary, True),
            # Keep operator/dev surface checks in foreground so interactive prompts are clean.
            (
                "loading",
                "Checking operator surfaces",
                self._show_operator_startup_sequence,
                False,
            ),
        ]
        if startup_extras:
            steps.extend([
                ("loading", "Loading command hints", self._show_startup_hints, True),
                ("loading", "Rendering startup draw", self._run_startup_draw, True),
            ])
        total = len(steps)

        for idx, (phase, label, action, use_spinner) in enumerate(steps, start=1):
            done_pct = int((idx / total) * 100)
            try:
                if self.quiet:
                    result = action()
                elif clean_startup:
                    if label != "Rendering banner":
                        self._ui_line(f"{label}...", level="info")
                    result = action()
                elif use_spinner:
                    result = self._run_with_spinner(f"⏳ {label}", action)
                else:
                    print(self._theme_text(f"\n⏳ {label}"))
                    result = action()
            except Exception as exc:
                self.logger.warning(f"[STARTUP] Step failed ({label}): {exc}")
                result = None
            if label == "Checking operator surfaces":
                self._maybe_prompt_dev_setup(result)
            if not clean_startup:
                self._print_task_progress(phase, f"{label} complete", done_pct)

    def _maybe_prompt_dev_setup(self, ai_status: dict[str, Any] | None) -> None:
        """Prompt once for Dev extension setup when contributor tooling is unavailable."""
        from core.services.unified_config_loader import get_bool_config

        if self.quiet or get_bool_config("UDOS_AUTOMATION"):
            return
        if not self._dev_mode_active():
            return
        if not self._startup_dev_setup_prompt_enabled():
            return
        if self._get_dev_mode_primary_provider() == "cloud":
            return
        if not isinstance(ai_status, dict):
            return
        if ai_status.get("local_ready", False):
            return
        issue = ai_status.get("local_issue") or "setup required"
        choice = self._ask_confirm(
            question=f"Dev extension tooling unavailable ({issue}). Run SETUP now?",
            default=True,
            help_text="Yes = run now, No = continue startup, Skip = defer for this launch",
            variant="skip",
        )
        if choice == "yes":
            try:
                result = self.dispatcher.dispatch(
                    "SETUP dev", parser=self.prompt, game_state=self.state
                )
                output = (
                    self.renderer.render(result)
                    if isinstance(result, dict)
                    else str(result)
                )
                if output:
                    print(output)
            except Exception as exc:
                self._ui_line(f"SETUP dev failed: {exc}", level="error")
        elif choice == "skip":
            self._ui_line("Deferred Dev Mode setup for this launch.", level="info")

    def _open_command_selector(self) -> str | None:
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
                print(self._theme_text("\n  ⚠ Vault checks:"))
                for line in warnings:
                    print(self._theme_text(f"     - {line}"))
        except Exception:
            pass
        print(self._theme_text("\n  Tips: SETUP | HELP | TAB | OPERATOR <prompt>"))
        print(
            self._theme_text(
                "     Try: UCODE PROFILE LIST | UCODE OPERATOR STATUS | WIZARD start\n"
            )
        )

    def _run_startup_draw(self) -> None:
        """Render the default startup ASCII art."""
        if self.quiet:
            return
        try:
            result = self.dispatcher.dispatch(
                "DRAW ucodesmile-ascii.md --rainbow",
                parser=self.prompt,
                game_state=self.state,
            )
            if isinstance(result, dict):
                output = self.renderer.render(result)
                if output:
                    print(output)
        except Exception:
            pass

    def _refresh_viewport(self) -> None:
        """Measure and persist viewport size on startup."""
        try:
            ViewportService().refresh(source="startup")
        except Exception:
            pass

    def _autodetect_environment(self) -> None:
        """Auto-detect and persist system info to .env on startup."""
        try:
            from core.services.env_autodetect_service import get_autodetect_service

            service = get_autodetect_service()
            results = service.detect_all(force=False)

            # Show startup info if not quiet
            if not self.quiet:
                if results.get("os_type"):
                    os_type = results["os_type"]
                    tz = results.get("timezone", "UTC")
                    location = results.get("location")
                    grid_id = results.get("grid_id")
                    dt = f"{results.get('current_date', '')} {results.get('current_time', '')}".strip()

                    # Only show if values were auto-detected (not already set)
                    if any("OS_TYPE" in u for u in results.get("updated", [])):
                        self._ui_line(f"Detected OS: {os_type}", level="info")
                    if any("UDOS_TIMEZONE" in u for u in results.get("updated", [])):
                        self._ui_line(f"Timezone: {tz}", level="info")
                    if location and any(
                        "UDOS_LOCATION" in u for u in results.get("updated", [])
                    ):
                        display = f"{location} ({grid_id})" if grid_id else location
                        self._ui_line(f"Location: {display}", level="info")
                self.logger.info(
                    f"[AUTO-DETECT] Updated: {', '.join(results['updated'])}"
                )
            if results.get("errors"):
                for error in results["errors"]:
                    self.logger.warning(f"[AUTO-DETECT] {error}")
        except Exception as e:
            self.logger.warning(f"[AUTO-DETECT] Environment detection failed: {e}")

    def _show_status_bar(self) -> None:
        """Render status bar line for the current session."""
        from core.services.unified_config_loader import get_bool_config

        force_status = get_bool_config("UDOS_TUI_FORCE_STATUS")
        if self._get_io_phase() != IOLifecyclePhase.INPUT and not force_status:
            return
        if self.quiet and not force_status:
            return
        output_stream = sys.stdout
        if not sys.stdout.isatty() and not force_status:
            try:
                output_stream = open("/dev/tty", "w", buffering=1)
            except Exception:
                return
        user_role = "ghost"
        ghost_mode = False
        try:
            from core.services.user_service import get_user_manager, is_ghost_mode

            user = get_user_manager().current()
            user_role = user.role.value if user else "ghost"
            ghost_mode = is_ghost_mode()
        except Exception:
            pass
        try:
            status_line = self.status_bar.get_status_line(
                user_role=user_role, ghost_mode=ghost_mode
            )
            output_stream.write(self._theme_text(status_line) + "\n")
            output_stream.flush()
        except Exception:
            if force_status:
                try:
                    fallback = self.status_bar.get_status_line(
                        user_role=user_role, ghost_mode=ghost_mode
                    )
                    sys.stdout.write(fallback + "\n")
                    sys.stdout.flush()
                except Exception:
                    pass
        finally:
            if output_stream is not sys.stdout:
                try:
                    output_stream.close()
                except Exception:
                    pass

    def _show_first_run_ai_setup_hint(self) -> None:
        """Show a first-run hint for local operator/dev setup."""
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

        print(self._theme_text("\nFirst-Run: SETUP | UCODE PROFILE LIST | UCODE OPERATOR STATUS\n"))

    def _network_online(self) -> bool:
        """Return True when local loopback services are reachable."""
        for host, port in (("127.0.0.1", 8765), ("127.0.0.1", 11434)):
            try:
                with socket.create_connection((host, port), timeout=0.8):
                    return True
            except OSError:
                continue
        return False

    def _show_first_run_offline_hint(self) -> None:
        """Show first-run offline guidance when network is unavailable."""
        try:
            if self.quiet or self._network_online():
                return
            from core.services.config_sync_service import ConfigSyncManager

            identity = ConfigSyncManager().load_identity_from_env()
            if identity.get("user_username"):
                return
        except Exception:
            return

        self._emit_lines([
            "",
            "No network detected. Using offline mode.",
            "Try:",
            "  UCODE DEMO LIST",
            "  UCODE DOCS --query <text>",
            "  UCODE SYSTEM INFO",
            "  UCODE CAPABILITIES --filter <text>",
            "",
        ])

    def _show_mode_policy_summary(self) -> None:
        """Show active runtime mode policy summary."""
        if self.quiet:
            return
        summary = mode_summary()
        self._ui_line(
            f"{summary['label']}: {summary['purpose']} ({summary['policy']})",
            level="info",
        )

    def _show_banner(self) -> None:
        """Show startup banner."""
        if self.quiet:
            return
        from core.services.unified_config_loader import get_bool_config

        if get_bool_config("UDOS_LAUNCHER_BANNER"):
            return
        vibe_banner = self._get_vibe_banner()
        if vibe_banner:
            print(self._theme_text(vibe_banner))
        # Startup grid art removed (legacy uCODE banner)

    def _get_repo_display_version(self) -> str:
        """Get display version from repo version.json."""
        try:
            version_file = self.repo_root / "version.json"
            if version_file.exists():
                data = json.loads(version_file.read_text())
                return data.get("display") or data.get("version") or self.ucode_version
        except Exception:
            pass
        return self.ucode_version

    def _get_vibe_banner(self) -> str:
        """Return the Vibe-style ASCII startup banner."""
        lines = [
            "████████████████████████████████████████████████████████████",
            "██                                                        ██",
            "██   ██████████████████████████████████████████████████   ██",
            "██   ██  ████  ███      ███      ███       ███       ██   ██",
            "██   ██  ████  ██  ███████  ████  ██  ████  ██  ███████   ██",
            "██   ██  ████  ██  ███████  ████  ██  ████  ██      ███   ██",
            "██   ██  ████  ██  ███████  ████  ██  ████  ██  ███████   ██",
            "██   ███      ████      ███      ███       ███       ██   ██",
            "██   ██████████████████████████████████████████████████   ██",
            "██   ███████████████    ████████████    ███████████████   ██",
            "██   █████████████████                █████████████████   ██",
            "██   ██████████████████████████████████████████████████   ██",
            "██                                                        ██",
            "████████████████████████████████████████████████████████████",
        ]

        colors = [
            "\033[91m",
            "\033[93m",
            "\033[92m",
            "\033[96m",
            "\033[94m",
            "\033[95m",
        ]
        reset = "\033[0m"
        tinted = []
        for idx, line in enumerate(lines):
            color = colors[idx % len(colors)]
            tinted.append(f"{color}{line}{reset}")
        return "\n".join(tinted)

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

        summary_parts = []
        if self.self_heal_summary:
            success = self.self_heal_summary.get("success", False)
            status = "✓" if success else "!"
            issues = self.self_heal_summary.get("issues", 0)
            repaired = self.self_heal_summary.get("repaired", 0)
            remaining = self.self_heal_summary.get("remaining", 0)
            summary_parts.append(
                f"Self-Heal {status} (issues {issues}, repaired {repaired}, remaining {remaining})"
            )

        if self.hot_reload_stats:
            enabled = "on" if self.hot_reload_stats.get("enabled") else "off"
            running = "running" if self.hot_reload_stats.get("running") else "stopped"
            reloads = self.hot_reload_stats.get("reload_count", 0)
            summary_parts.append(f"Hot Reload {enabled}/{running} (reloads {reloads})")

        summary = (
            " | ".join(summary_parts) if summary_parts else "Health summary unavailable"
        )
        width = ViewportService().get_cols()
        print(OutputToolkit.invert_section(" Health ", width=width))
        print(f"Health: {summary}")
        try:
            mem_percent = int(psutil.virtual_memory().percent)
            cpu_percent = int(psutil.cpu_percent(interval=0.1))
            print(OutputToolkit.progress_block_full(mem_percent, 100, label="Memory"))
            print(OutputToolkit.progress_block_full(cpu_percent, 100, label="CPU"))
        except Exception:
            pass
        print(f"  Log: {self.health_log_path}")

        prev_remaining = (
            (self.previous_health_log or {}).get("self_heal", {}).get("remaining", 0)
        )
        if prev_remaining > 0:
            self._ui_line(
                f"Last health log recorded {prev_remaining} remaining issues; automation will rerun diagnostics on drift.",
                level="warn",
            )

        if self.self_heal_summary and self.self_heal_summary.get("remaining", 0) > 0:
            self._ui_line(
                "Automation will rerun REPAIR/HEALTH until remaining issues drop to zero.",
                level="warn",
            )

        if self.memory_test_summary:
            status = self.memory_test_summary.get("status", "idle")
            if status not in ("idle", "none"):
                pending = self.memory_test_summary.get("pending", 0)
                result = self.memory_test_summary.get("result") or "pending"
                print(
                    f"  Memory Tests: {status} | Result: {result} | Pending: {pending}"
                )
        print("")

        self._prompt_health_actions()

    def _prompt_health_actions(self) -> None:
        """Prompt for REPAIR/RESTORE/DESTROY when health checks report issues."""
        # Skip prompts for non-interactive or automation runs.
        from core.services.unified_config_loader import get_bool_config

        if self.quiet or get_bool_config("UDOS_AUTOMATION"):
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
            choice = (
                input(
                    "Health check issues detected. Choose: REPAIR | RESTORE | DESTROY | SKIP: "
                )
                .strip()
                .upper()
            )
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

    def _get_dev_mode_config_path(self) -> Path:
        """Return path to Dev Mode helper configuration."""
        return self.repo_root / "core" / "config" / "ok_modes.json"

    def _load_dev_mode_config(self) -> dict[str, Any]:
        """Load Dev Mode helper configuration (safe fallback)."""
        path = self._get_dev_mode_config_path()
        if not path.exists():
            return {"modes": {}}
        try:
            with open(path, encoding="utf-8") as handle:
                return json.load(handle)
        except Exception as exc:
            self.logger.warning("[OK] Failed to load ok_modes.json: %s", exc)
            return {"modes": {}}

    def _write_dev_mode_config(self, config: dict[str, Any]) -> None:
        """Persist Dev Mode helper configuration safely."""
        path = self._get_dev_mode_config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config, indent=2))

    def _get_dev_mode_default_model(self) -> str:
        """Return the default local model for Dev Mode helper requests."""
        mode = (self.dev_mode_config.get("modes") or {}).get("ofvibe", {})
        default_models = mode.get("default_models") or {}
        model = default_models.get("core") or default_models.get("dev")
        try:
            from core.services.dev_state import get_dev_active

            if get_dev_active():
                model = default_models.get("dev") or model
        except Exception:
            from core.services.unified_config_loader import get_bool_config

            if get_bool_config("UDOS_DEV_MODE"):
                model = default_models.get("dev") or model
        return model or "devstral-small-2"

    def _get_dev_mode_fallback_model(self) -> str | None:
        """Return the fallback model for Dev Mode helper requests when primary fails."""
        mode = (self.dev_mode_config.get("modes") or {}).get("ofvibe", {})
        default_models = mode.get("default_models") or {}
        return default_models.get("fallback")

    def _get_dev_mode_primary_provider(self) -> str:
        """Return normalized primary provider preference for Dev Mode helper requests."""
        env_value = self._env_value("VIBE_PRIMARY_PROVIDER").lower()
        if env_value in {"local", "cloud"}:
            return env_value
        mode = (self.dev_mode_config.get("modes") or {}).get("ofvibe", {})
        mode_value = str(mode.get("primary_provider", "")).strip().lower()
        if mode_value in {"local", "cloud"}:
            return mode_value
        return "local"

    def _provider_route_details(self) -> tuple[str, str]:
        """Return provider route and where that decision came from."""
        env_value = os.environ.get("VIBE_PRIMARY_PROVIDER", "").strip().lower()
        if env_value in {"local", "cloud"}:
            return env_value, "shell-env"

        from core.services.unified_config_loader import get_config_loader

        env_file_value = (
            get_config_loader().get_str("VIBE_PRIMARY_PROVIDER", "").strip().lower()
        )
        if env_file_value in {"local", "cloud"}:
            return env_file_value, ".env"

        return "local", "default"

    def _get_dev_mode_context_window(self) -> int:
        """Return the local Dev Mode context window size."""
        try:
            from core.services.provider_registry import (
                ProviderNotAvailableError,
                ProviderType,
                get_provider,
            )

            vibe_provider = get_provider(ProviderType.VIBE_SERVICE)
            if isinstance(vibe_provider, dict) and "context_window" in vibe_provider:
                return int(vibe_provider["context_window"])
            if hasattr(vibe_provider, "context_window"):
                return int(vibe_provider.context_window)
            if hasattr(vibe_provider, "get_context_window"):
                return int(vibe_provider.get_context_window())
            raise ProviderNotAvailableError("Vibe provider missing context_window")
        except Exception:
            return 8192

    def _dev_mode_auto_fallback_enabled(self) -> bool:
        """Return whether Dev Mode helper should auto-fallback between local and cloud."""
        from core.services.unified_config_loader import get_config_loader

        if raw_value := get_config_loader().get("UDOS_OK_AUTO_FALLBACK"):
            env_value = str(raw_value).strip().lower()
            if env_value in {"1", "true", "yes", "on"}:
                return True
            if env_value in {"0", "false", "no", "off"}:
                return False
        mode = (self.dev_mode_config.get("modes") or {}).get("ofvibe", {})
        return bool(mode.get("auto_fallback", False))

    def _dev_mode_cloud_sanity_check_enabled(self) -> bool:
        """Return whether low-confidence local responses should trigger cloud sanity checks."""
        from core.services.unified_config_loader import get_config_loader

        if raw_value := get_config_loader().get("UDOS_OK_CLOUD_SANITY_CHECK"):
            env_value = str(raw_value).strip().lower()
            if env_value in {"1", "true", "yes", "on"}:
                return True
            if env_value in {"0", "false", "no", "off"}:
                return False
        mode = (self.dev_mode_config.get("modes") or {}).get("ofvibe", {})
        return bool(mode.get("cloud_sanity_check", False))

    def _set_dev_mode_auto_fallback(self, enabled: bool) -> None:
        """Enable or disable Dev Mode helper auto-fallback between local/cloud."""
        config = self._load_dev_mode_config()
        modes = config.setdefault("modes", {})
        ofvibe = modes.setdefault("ofvibe", {})
        ofvibe["auto_fallback"] = bool(enabled)
        self._write_dev_mode_config(config)
        self.dev_mode_config = config

    def _wizard_base_url(self) -> str:
        """Wizard server base URL for brokered cloud access."""
        value = self._env_value("WIZARD_BASE_URL") or "http://127.0.0.1:8765"
        return self._resolve_loopback_url(
            value, fallback="http://127.0.0.1:8765", context="WIZARD_BASE_URL"
        )

    def _resolve_loopback_url(self, url: str, *, fallback: str, context: str) -> str:
        """Allow loopback URLs only; return fallback when policy is violated."""
        parsed = urlparse((url or "").strip())
        host = (parsed.hostname or "").strip().lower()
        if is_loopback_host(host):
            return url.rstrip("/")

        self.logger.warning(
            "[BoundaryPolicy] blocked non-loopback %s=%s; falling back to %s",
            context,
            url,
            fallback,
        )
        return fallback.rstrip("/")

    @staticmethod
    def _normalize_model_names(models: list[str]) -> list[str]:
        return [m.strip() for m in models if m and str(m).strip()]

    def _wizard_headers(self) -> dict[str, str]:
        """Authorization headers for Wizard API."""
        token = self._env_value("WIZARD_ADMIN_TOKEN")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def _env_value(self, key: str) -> str:
        """Read config value from process env first, then repo .env file."""
        from core.services.unified_config_loader import get_config_loader

        return get_config_loader().get_str(key, "").strip()

    def _startup_dev_setup_prompt_enabled(self) -> bool:
        """Return whether startup should prompt to run Dev Mode setup."""
        from core.services.unified_config_loader import get_bool_config

        return get_bool_config("UDOS_PROMPT_SETUP_DEV")

    def _init_operator_prompt_context(self) -> None:
        """Expose operator/dev helper status to the prompt toolbar."""
        try:
            if self._dev_mode_active():
                self.prompt.ok_model = self._get_dev_mode_default_model()
                self.prompt.ok_context_window = self._get_dev_mode_context_window()
            else:
                self.prompt.ok_model = "operator"
                self.prompt.ok_context_window = 0
        except Exception as exc:
            self.logger.debug(f"[LOGIC] Failed to set prompt context: {exc}")

    def _show_operator_startup_sequence(self) -> dict[str, Any]:
        """Show standard operator summary, with Dev extension status when active."""
        from core.services.ok_provider_handler import get_ok_provider_handler
        from core.services.provider_registry import CoreProviderRegistry

        CoreProviderRegistry.auto_register_vibe()
        if self.quiet:
            return {"local_ready": True, "cloud_ready": True}

        operator_status = get_operator_mode_service().status_payload()
        topology = operator_status["session"]["topology"]
        enabled_profiles = ", ".join(operator_status["session"]["enabled_profiles"]) or "(none)"
        print(self._theme_text("\nOperator"))
        self.renderer.stream_text(
            f"Topology: {topology}\nEnabled profiles: {enabled_profiles}\nQueued tasks: {operator_status['session']['queued_tasks']}",
            prefix="operator> ",
        )
        if not self._dev_mode_active():
            self.renderer.stream_text(
                "Standard runtime uses OPERATOR and UCODE OPERATOR.\nContributor tooling remains gated behind the active /dev extension lane.",
                prefix="operator> ",
            )
            print("")
            return {
                "local_ready": True,
                "local_issue": None,
                "cloud_ready": False,
                "cloud_skip": True,
                "cloud_direct": False,
            }

        # Use unified OK provider handler (replaces scattered status checks)
        handler = get_ok_provider_handler()
        local_status = handler.check_local_provider()
        cloud_status_obj = handler.check_cloud_provider()

        # Adapt new ProviderStatus to old dict format for compatibility
        logic_status = {
            "ready": local_status.is_available,
            "issue": local_status.issue,
            "model": local_status.default_model,
            "model_path": local_status.details.get("model_path"),
            "runtime": local_status.details.get("runtime", "gpt4all"),
        }
        cloud_status = {
            "ready": cloud_status_obj.is_available,
            "issue": cloud_status_obj.issue,
            "skip": not cloud_status_obj.is_configured,
        }

        model = logic_status.get("model") or self._get_dev_mode_default_model()
        fallback_model = self._get_dev_mode_fallback_model()
        ctx = self._get_dev_mode_context_window()
        local_issue = logic_status.get("issue") or None
        model_path = logic_status.get("model_path", "")
        runtime = logic_status.get("runtime", "gpt4all")

        lines = []
        if logic_status.get("ready"):
            lines.append(f"✅ Logic Assist local lane ready ({model}, ctx {ctx}, timeout 30s)")
            lines.append(f"   Local runtime: {runtime}")
            if model_path:
                lines.append(f"   Model path: {model_path}")
            if fallback_model:
                lines.append(f"   Fallback: {fallback_model} (lightweight open-source)")
        else:
            issue = local_issue or "setup required"
            lines.append(f"⚠️ Logic Assist contributor lane needs setup: {issue} ({model}, ctx {ctx})")
            if issue in {
                "setup required",
                "local runtime down",
                "missing model",
                "gpt4all package unavailable",
                "gpt4all model missing",
            }:
                lines.append("Tip: SETUP dev")
            if issue in {"missing model", "gpt4all model missing"}:
                lines.append("Tip: place the configured GPT4All model file in the logic-assist model directory")
            if issue == "port blocked":
                lines.append("Tip: REPAIR port (auto-fix config)")
            if issue == "model corrupted":
                lines.append("Tip: restore or replace the local model file")
            lines.append("Tip: RUN HEALTH/REPAIR to auto-fix all issues")
        if cloud_status.get("skip"):
            lines.append("Tip: WIZARD start")
        elif cloud_status.get("ready"):
            lines.append("✅ Mistral cloud ready (timeout 15s)")
        else:
            issue = cloud_status.get("issue") or "setup required"
            lines.append(f"⚠️ Mistral cloud needed: {issue}")
            lines.append(
                "Tip: REPAIR cloud (check API quota, switch key, use local, or auto-retry)"
            )
        lines.append("Tip: LOGIC EXPLAIN <file> | LOGIC LOCAL")

        print(self._theme_text("\nLogic Assist"))
        route, source = self._provider_route_details()
        self.renderer.stream_text(
            f"Provider route: {route} (source: {source})", prefix="dev> "
        )
        self.renderer.stream_text("\n".join(lines), prefix="dev> ")
        print("")
        return {
            "local_ready": bool(logic_status.get("ready")),
            "local_issue": local_issue,
            "cloud_ready": bool(cloud_status.get("ready")),
            "cloud_skip": bool(cloud_status.get("skip")),
            "cloud_direct": False,
        }

    def _format_ai_status_line(self, label: str, status: dict[str, Any]) -> str:
        """Format a single OK mode status line."""
        if status.get("ready"):
            return f"  ✅ {label}: ready"
        issues = status.get("issues") or []
        if issues:
            return f"  ⚠️ {label}: " + ", ".join(issues)
        return f"  ⚠️ {label}: setup required"

    def _setup_health_monitoring(self) -> None:
        """Initialize Self-Healer diagnostics + Hot Reload stats for automation."""
        self.previous_health_log = read_last_summary()
        self.self_heal_summary = self._run_self_healer()
        self.hot_reload_mgr = self._init_hot_reload_manager()
        self.hot_reload_stats = (
            self.hot_reload_mgr.stats() if self.hot_reload_mgr else None
        )
        self.memory_test_summary = self._schedule_memory_tests()
        self._log_health_training_summary()

    def _schedule_memory_tests(self) -> dict[str, Any]:
        """Run memory/tests automation if new or modified files exist."""
        tests_root = self.repo_root / "memory" / "tests"
        try:
            scheduler = MemoryTestScheduler(self.repo_root, logger=self.logger)
            self.memory_test_scheduler = scheduler
            return scheduler.schedule()
        except Exception as exc:
            log_path = tests_root.parent / "logs" / "memory-tests.log"
            self.logger.warning("[MemoryTests] Scheduler unavailable: %s", exc)
            return {
                "status": "error",
                "pending": 0,
                "last_run": None,
                "result": None,
                "log_path": str(log_path),
                "error": str(exc),
            }

    def _run_self_healer(self) -> dict[str, Any]:
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

    def _load_monitoring_summary(self, memory_root: Path) -> dict[str, Any]:
        summary_path = memory_root / "monitoring" / "monitoring-summary.json"
        if summary_path.exists():
            try:
                return json.loads(summary_path.read_text())
            except Exception as exc:
                self.logger.warning("[Monitoring] Failed to read summary: %s", exc)
        try:
            from core.services.provider_registry import (
                ProviderNotAvailableError,
                ProviderType,
                get_provider,
            )

            provider = get_provider(ProviderType.MONITORING_MANAGER)
            monitoring = (
                provider(data_dir=memory_root / "monitoring")
                if callable(provider)
                else provider
            )
            return monitoring.log_training_summary()
        except ProviderNotAvailableError:
            return {}
        except Exception as exc:
            self.logger.debug("[Monitoring] Provider unavailable: %s", exc)
            return {}

    def _check_and_build_ts_runtime(self) -> None:
        """Check if TS runtime is built, auto-build if missing (first-time setup)."""
        try:
            from core.services.ts_runtime_service import TSRuntimeService

            service = TSRuntimeService()

            # Check with auto_build=True to trigger automatic build if missing
            check_result = self._run_with_progress(
                "installation",
                "TypeScript runtime validation",
                lambda: service._check_runtime_entry(auto_build=True),
                spinner_label="⏳ TS runtime check",
            )

            if check_result and check_result.get("status") == "error":
                # Auto-build failed or runtime still missing
                if not self.quiet:
                    print("\n⚠️  TypeScript Runtime Issue:")
                    print(f"   {check_result.get('message')}")
                    if check_result.get("details"):
                        print(f"   Details: {check_result.get('details')}")
                    if check_result.get("suggestion"):
                        print(f"   -> {check_result.get('suggestion')}")
                    print()
        except Exception as exc:
            self.logger.warning(f"[STARTUP] TS runtime check failed: {exc}")

    def _read_notification_history(
        self, memory_root: Path, limit: int = 5
    ) -> list[dict[str, Any]]:
        try:
            from core.services.provider_registry import ProviderType, is_provider_available, get_provider
            if is_provider_available(ProviderType.NOTIFICATION_HISTORY):
                return get_provider(ProviderType.NOTIFICATION_HISTORY).get_recent(limit)
        except Exception as exc:
            self.logger.warning("[Notification] Protocol failed, falling back to JSONL: %s", exc)
        log_path = memory_root / "logs" / "notification-history.log"
        if not log_path.exists():
            return []
        try:
            lines = [
                line.strip()
                for line in log_path.read_text().splitlines()
                if line.strip()
            ]
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
        default_choice = normalize_default(default, variant)
        prompt_text = format_prompt(question, default_choice, variant)
        while True:
            response = input(prompt_text)
            if is_help_response(response):
                print(f"  ℹ Valid choices: {format_options(variant)}")
                print("  ℹ Shortcuts: 1=yes, 0=no, Enter=default")
                continue
            choice = parse_confirmation(response, default_choice, variant)
            if choice is not None:
                return choice
            print(format_error(variant))

    def _ask_yes_no(
        self,
        question: str,
        default: bool = True,
        help_text: str = None,
        context: str = None,
    ) -> bool:
        """Ask a standardized confirmation question.

        Prompt format with 2-line context display:
          ╭─ Context or current state
          ╰─ [Yes|No|Confirm]
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

    def _ask_menu_choice(
        self,
        prompt: str,
        num_options: int,
        allow_cancel: bool = True,
        help_text: str = None,
    ) -> int | None:
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
            context_lines = ["", f"  ╭─ Valid choices: {range_display}"]
            if help_text:
                context_lines.append(f"  ╰─ {help_text}")
            else:
                context_lines.append("  ╰─ Enter number and press Enter")
            self._emit_lines(context_lines)

        # Get choice using standard menu handler
        return self.prompt.ask_menu_choice(prompt, num_options, allow_zero=allow_cancel)

    def _handle_story_form(self, form_data: dict) -> dict:
        """Handle interactive story form - collect user responses for all sections.

        Args:
            form_data: Form structure with title and sections or fields

        Returns:
            Dictionary of collected field values from all sections
        """
        try:
            from core.tui.story_form_handler import get_form_handler
        except Exception as exc:
            self.logger.error(f"[STORY] Form handler unavailable: {exc}")
            return {}

        title = form_data.get("title", "Form")
        description = (form_data.get("text") or "").strip()

        fields: list[dict[str, Any]] = []
        sections = form_data.get("sections", [])
        if sections:
            for section in sections:
                section_title = section.get("title")
                for field in section.get("fields", []) or []:
                    if not isinstance(field, dict):
                        continue
                    field_copy = dict(field)
                    if section_title and field_copy.get("label"):
                        field_copy["label"] = f"{section_title}: {field_copy['label']}"
                    fields.append(field_copy)
        else:
            fields = [
                dict(f)
                for f in (form_data.get("fields", []) or [])
                if isinstance(f, dict)
            ]

        form_spec = {"title": title, "description": description, "fields": fields}

        # Inject dynamic defaults for known setup fields
        from core.services.unified_config_loader import get_config, get_path_config

        udos_root = str(get_path_config("UDOS_ROOT") or self.repo_root)
        vault_root = str(
            get_path_config("VAULT_ROOT")
            or (self.repo_root / "memory" / "vault").resolve()
        )
        for field in fields:
            if field.get("name") == "setup_udos_root":
                if not field.get("default"):
                    field["default"] = udos_root
                if not field.get("placeholder"):
                    field["placeholder"] = udos_root
            if field.get("name") == "setup_vault_md_root":
                if not field.get("default"):
                    field["default"] = vault_root
                if not field.get("placeholder"):
                    field["placeholder"] = vault_root
            # Also inject username default from .env if exists
            if field.get("name") == "user_username":
                env_username = get_config("USER_USERNAME", "")
                if env_username and not field.get("default"):
                    field["default"] = env_username

        env_udos_root = get_config("UDOS_ROOT", "")
        env_vault_root = get_config("VAULT_ROOT", "") or get_config("VAULT_MD_ROOT", "")
        if env_udos_root or env_vault_root:
            filtered = []
            for field in fields:
                name = field.get("name")
                if name == "setup_udos_root" and env_udos_root:
                    continue
                if name == "setup_vault_md_root" and env_vault_root:
                    continue
                filtered.append(field)
            form_spec["fields"] = filtered

        handler = get_form_handler()
        result = handler.process_story_form(form_spec)
        if result.get("status") == "success":
            return result.get("data", {})
        return {}

    def _save_user_profile(self, collected_data: dict) -> None:
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
            enriched_data = identity_enc.enrich_identity(
                collected_data, location=location
            )
            install_choice = str(
                collected_data.get(
                    "dev_mode_helper_install",
                    collected_data.get("ok_helper_install", ""),
                )
            ).strip().lower()
            dev_mode_setup_requested = install_choice in {"yes", "y", "true", "1", "ok"}
            if dev_mode_setup_requested:
                mistral_key = (collected_data.get("mistral_api_key") or "").strip()
                if not mistral_key:
                    try:
                        print("\nMistral API key required for Dev Mode helper setup.")
                        mistral_key = input(
                            "Mistral API key (leave blank to skip): "
                        ).strip()
                    except Exception:
                        mistral_key = ""
                if mistral_key:
                    collected_data["mistral_api_key"] = mistral_key
                    enriched_data["mistral_api_key"] = mistral_key
                else:
                    print("⚠️  Continuing without Mistral API key (can be added later).")

            # Step 2: Save identity fields + optional API keys to .env using ConfigSyncManager
            try:
                from core.services.config_sync_service import ConfigSyncManager

                sync_manager = ConfigSyncManager()

                # Validate and save identity to .env (7-field boundary enforced)
                if sync_manager.validate_identity(enriched_data):
                    sync_manager.save_identity_to_env(enriched_data)
                    self.logger.info("[SETUP] Identity saved to .env (7 fields)")
                    print("\n✅ Identity saved to .env file")
                    token = self._ensure_wizard_admin_token()
                    if token:
                        print("Wizard admin token ready")
                        print("   Token files: memory/private/wizard_admin_token.txt")
                        print(
                            "                memory/bank/private/wizard_admin_token.txt"
                        )
                    mistral_key = (collected_data.get("mistral_api_key") or "").strip()
                    if mistral_key:
                        self._sync_mistral_secret(mistral_key)
                    self._sync_local_user(enriched_data)
                    self.ghost_mode = self._is_ghost_user()
                    # Defer logic-assist setup until after Wizard sync/local save.
                    # Mistral key is now part of .env boundary (optional)
                    try:
                        from core.services.user_service import is_ghost_identity

                        if is_ghost_identity(
                            enriched_data.get("user_username"),
                            enriched_data.get("user_role"),
                        ):
                            print(
                                "Ghost Mode remains active (role or username is Ghost)."
                            )
                            print(
                                "   To exit Ghost Mode, change role to user/admin and set a non-Ghost username."
                            )
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
                # Get the token
                token = ""
                token_paths = [
                    self.repo_root / "memory" / "private" / "wizard_admin_token.txt",
                    self.repo_root
                    / "memory"
                    / "bank"
                    / "private"
                    / "wizard_admin_token.txt",
                ]
                for token_path in token_paths:
                    if token_path.exists():
                        token = token_path.read_text().strip()
                        if token:
                            break

                headers = {"Content-Type": "application/json"}
                if token:
                    headers["Authorization"] = f"Bearer {token}"

                base_url = self._wizard_base_url().rstrip("/")
                endpoint_candidates = [
                    f"{base_url}/api/setup/story/submit",
                    f"{base_url}/api/v1/setup/story/submit",
                ]
                wizard_reachable = False
                wizard_locked = False
                response = None
                for endpoint in endpoint_candidates:
                    status_code = 0
                    payload: dict[str, Any] = {}
                    try:
                        response = http_post(
                            endpoint,
                            headers=headers,
                            json_data={"answers": enriched_data},
                            timeout=10,
                        )
                        status_code = int(response.get("status_code") or 0)
                        payload = (
                            response.get("json")
                            if isinstance(response.get("json"), dict)
                            else {}
                        )
                    except HTTPError as exc:
                        status_code = exc.code
                        if exc.response_text:
                            try:
                                parsed = json.loads(exc.response_text)
                                if isinstance(parsed, dict):
                                    payload = parsed
                            except json.JSONDecodeError:
                                payload = {}
                    response = {"status_code": status_code, "json": payload}
                    if status_code != 404:
                        break

                if response is not None:
                    wizard_reachable = True
                    if response.get("status_code") == 200:
                        self.logger.info("[SETUP] Setup data synced to Wizard keystore")
                        print("✅ Data synced to Wizard keystore")

                        # Display UDOS Crypt identity
                        if enriched_data.get("_crypt_id"):
                            identity_enc.print_identity_summary(
                                enriched_data, location=location
                            )

                        self._maybe_run_dev_mode_setup(dev_mode_setup_requested)
                        return
                    elif response.get("status_code") == 503:
                        self.logger.warning("[SETUP] Wizard secret store locked")
                        wizard_locked = True
                        print("\n⚠️  Wizard secret store is locked.")
                        print(
                            "   ✅ Saved locally. Run WIZARD START after setting WIZARD_KEY to sync."
                        )
                    else:
                        try:
                            error_detail = (response.get("json") or {}).get(
                                "detail", f"HTTP {response.get('status_code')}"
                            )
                        except Exception:
                            error_detail = f"HTTP {response.get('status_code')}"
                        self.logger.warning(f"[SETUP] Wizard API error: {error_detail}")
                        print(f"\n⚠️  Could not sync to Wizard: {error_detail}")

            except HTTPError:
                self.logger.debug("Wizard server not running, trying direct save")
                print("⚠️  Wizard server not running - data saved locally.")
                print("   ▶ Run WIZARD START to sync this setup into the keystore.")
            except Exception as e:
                self.logger.debug(f"Wizard API submission failed: {e}")

            # Fallback: Try direct save via Wizard services (if Wizard is available but server isn't running)
            try:
                from core.services.provider_registry import (
                    ProviderNotAvailableError,
                    ProviderType,
                    get_provider,
                )

                providers = get_provider(ProviderType.SETUP_PROFILES)
                save_user_profile = (
                    providers.get("save_user_profile")
                    if isinstance(providers, dict)
                    else None
                )
                save_install_profile = (
                    providers.get("save_install_profile")
                    if isinstance(providers, dict)
                    else None
                )
                if not save_user_profile or not save_install_profile:
                    raise ProviderNotAvailableError(
                        "Setup profile providers not available"
                    )

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
                        "github_push": bool(
                            collected_data.get("capability_github_push")
                        ),
                        "icloud": bool(collected_data.get("capability_icloud")),
                        "plugin_repo": bool(
                            collected_data.get("capability_plugin_repo")
                        ),
                        "plugin_auto_update": bool(
                            collected_data.get("capability_plugin_auto_update")
                        ),
                    },
                }

                user_result = save_user_profile(user_profile)
                install_result = save_install_profile(install_profile)

                if user_result.data and install_result.data:
                    self.logger.info(
                        "[SETUP] Setup data saved via direct Wizard services"
                    )
                    print("\n✅ Setup data saved to Wizard keystore.")
                    self._maybe_run_dev_mode_setup(dev_mode_setup_requested)
                    self._maybe_run_dev_mode_setup(dev_mode_setup_requested)
                    return
                elif user_result.locked or install_result.locked:
                    error = user_result.error or install_result.error
                    self.logger.warning(f"[SETUP] Secret store locked: {error}")
                    wizard_locked = True
                    print(f"\n⚠️  Secret store is locked: {error}")
                    print(
                        "   ✅ Saved locally. Set WIZARD_KEY and run WIZARD START to sync."
                    )

            except Exception as e:
                self.logger.debug(f"Wizard direct save not available: {e}")

            # Final fallback: Save to local profile file in memory/
            if wizard_reachable and not wizard_locked:
                print("\nℹ️  Wizard is reachable; skipping local profile cache.")
                print("   ▶ Run WIZARD STATUS or retry SETUP to sync.")
                self._maybe_run_dev_mode_setup(dev_mode_setup_requested)
                return
            profile_dir = self.repo_root / "memory" / "user"
            profile_dir.mkdir(parents=True, exist_ok=True)
            profile_file = profile_dir / "profile.json"

            from datetime import datetime
            import json

            # Create profile structure with timestamp
            profile = {
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "data": collected_data,
            }

            with open(profile_file, "w") as f:
                json.dump(profile, f, indent=2)

            self.logger.info(
                f"[SETUP] User profile saved to local file: {profile_file}"
            )
            print(f"\nSetup data saved locally to {profile_file}")
            print("⚠️  Note: Run WIZARD START to sync this data to the keystore.")
            self._maybe_run_dev_mode_setup(dev_mode_setup_requested)

        except Exception as e:
            self.logger.error(
                f"[SETUP] Failed to save user profile: {e}", exc_info=True
            )
            print(f"\n⚠️  Warning: Could not save profile: {e}")

    def _ensure_wizard_admin_token(self) -> str | None:
        """Ensure WIZARD_ADMIN_TOKEN exists and is synced to token files."""
        env_path = self.repo_root / ".env"
        from core.services.unified_config_loader import get_config

        token = get_config("WIZARD_ADMIN_TOKEN", "").strip()

        if not token:
            token = self._fetch_or_generate_admin_token(env_path)
        if not token:
            return None

        os.environ["WIZARD_ADMIN_TOKEN"] = token
        self._write_env_var(env_path, "WIZARD_ADMIN_TOKEN", token)
        self._write_admin_token_files(token)
        return token

    def _fetch_or_generate_admin_token(self, env_path: Path) -> str:
        """Try Wizard API token generation; fallback to local token."""
        try:
            url = f"{self._wizard_base_url()}/api/admin-token/status"
            resp = http_get(url, timeout=2)
            if resp.get("status_code") == 200:
                payload = resp.get("json") if isinstance(resp.get("json"), dict) else {}
                env_data = payload.get("env") or {}
                existing = env_data.get("WIZARD_ADMIN_TOKEN", "").strip()
                if existing:
                    return existing
        except HTTPError:
            pass

        try:
            url = f"{self._wizard_base_url()}/api/admin-token/generate"
            resp = http_post(url, timeout=4)
            if resp.get("status_code") == 200:
                payload = resp.get("json") if isinstance(resp.get("json"), dict) else {}
                token = (payload.get("token") or "").strip()
                if token:
                    return token
        except HTTPError:
            pass

        token = secrets.token_urlsafe(32)
        self._write_env_var(env_path, "WIZARD_ADMIN_TOKEN", token)
        return token

    def _write_env_var(self, env_path: Path, key: str, value: str) -> None:
        """Write or update a single env var in .env."""
        env_path.parent.mkdir(parents=True, exist_ok=True)
        lines = env_path.read_text().splitlines() if env_path.exists() else []
        updated = False
        new_lines = []
        for line in lines:
            if not line or line.strip().startswith("#") or "=" not in line:
                new_lines.append(line)
                continue
            k, _ = line.split("=", 1)
            if k.strip() == key:
                new_lines.append(f'{key}="{value}"')
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f'{key}="{value}"')
        env_path.write_text("\n".join(new_lines) + "\n")

    def _write_admin_token_files(self, token: str) -> None:
        """Write admin token to canonical token file locations."""
        token_paths = [
            self.repo_root / "memory" / "private" / "wizard_admin_token.txt",
            self.repo_root / "memory" / "bank" / "private" / "wizard_admin_token.txt",
        ]
        for path in token_paths:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(token)
            except Exception as exc:
                self.logger.warning(
                    f"[SETUP] Failed to write admin token {path}: {exc}"
                )

    def _sync_mistral_secret(self, api_key: str) -> None:
        """Store Mistral API key in Wizard secret store (best effort)."""
        if not api_key:
            return
        from core.services.unified_config_loader import get_config

        token = get_config("WIZARD_ADMIN_TOKEN", "").strip()
        if not token:
            return
        base_url = self._wizard_base_url().rstrip("/")
        try:
            resp = http_post(
                f"{base_url}/api/settings-unified/secrets/mistral_api_key?value={quote(api_key)}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )
            if resp.get("status_code") == 200:
                print("✅ Mistral API key stored in Wizard secret store")
                return
            try:
                detail = (resp.get("json") or {}).get("detail")
            except Exception:
                detail = f"HTTP {resp.get('status_code')}"
            self.logger.warning(f"[SETUP] Failed to store Mistral key: {detail}")
        except HTTPError as exc:
            self.logger.debug(f"[SETUP] Wizard secret store API unavailable: {exc}")
        except Exception as exc:
            self.logger.debug(f"[SETUP] Wizard secret store API unavailable: {exc}")

        try:
            from core.services.provider_registry import (
                ProviderNotAvailableError,
                ProviderType,
                get_provider,
            )

            provider = get_provider(ProviderType.SECRET_STORE)
            store = provider() if callable(provider) else provider
            store.unlock()
            store.set_entry("mistral_api_key", api_key, provider="setup")
            print("✅ Mistral API key stored in Wizard secret store (local)")
        except ProviderNotAvailableError:
            self.logger.debug("[SETUP] Wizard secret store provider not available")
        except Exception as exc:
            self.logger.warning(f"[SETUP] Failed to store Mistral key locally: {exc}")

    def _sync_local_user(self, identity: dict[str, Any]) -> None:
        """Create/replace local user after setup to exit ghost mode.

        SETUP replaces the current user - there's only one user at a time.
        What's local is local and stays.
        """
        try:
            from core.services.user_service import UserRole, get_user_manager

            username = (identity.get("user_username") or "").strip().lower()
            role_raw = (identity.get("user_role") or "").strip().lower()
            if not username:
                return

            role = UserRole.USER
            if role_raw == "admin":
                role = UserRole.ADMIN
            elif role_raw == "ghost":
                role = UserRole.GUEST

            manager = get_user_manager()

            # SETUP replaces: delete all existing users except the new one
            current = manager.current()
            if current and current.username != username:
                # Delete old user, create new
                for old_username in list(manager.users.keys()):
                    if old_username != username:
                        try:
                            manager.delete_user(old_username)
                        except Exception:
                            pass

            # Create or update the user
            if username not in manager.users:
                success, msg = manager.create_user(username, role=role)
                if not success:
                    self.logger.error(f"[SETUP] Failed to create user: {msg}")
                    print(f"\n❌ Failed to create user: {msg}")
                    return
            else:
                # Update role if different
                manager.set_role(username, role)

            # Switch to the new user
            success, msg = manager.switch_user(username)
            if not success:
                self.logger.error(f"[SETUP] Failed to switch user: {msg}")
        except Exception as exc:
            self.logger.warning(f"[SETUP] Failed to sync local user: {exc}")

    def _collect_field_response(
        self, field: dict, previous_value: str | None = None
    ) -> str | None:
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
                suggestion = suggestions.get("timezone") or suggestions.get(
                    "user_timezone"
                )
            elif "time" in field_name:
                suggestion = suggestions.get("time") or suggestions.get(
                    "user_local_time"
                )
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
            self.logger.warning(
                f"[FORM] Advanced form handler failed, using fallback: {e}"
            )
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
                from core.services.provider_registry import (
                    ProviderNotAvailableError,
                    ProviderType,
                    get_provider,
                )

                providers = get_provider(ProviderType.SETUP_PROFILES)
                load_user_profile = (
                    providers.get("load_user_profile")
                    if isinstance(providers, dict)
                    else None
                )
                if not load_user_profile:
                    raise ProviderNotAvailableError(
                        "Setup profile provider not available"
                    )

                result = load_user_profile()

                # If we have user data, not a fresh install
                if result.data and not result.locked:
                    self.logger.debug("User profile exists, not a fresh install")
                    return

                # If locked due to no encryption key, still consider it fresh
                if result.locked and "not set" in str(result.error).lower():
                    self.logger.debug(
                        "Wizard not yet initialized, treating as fresh install"
                    )

            except Exception as e:
                self.logger.debug(f"Could not check user profile: {e}")
                return

            # Fresh install detected
            print("\n" + "=" * 60)
            print("⚙️  FRESH INSTALLATION DETECTED")
            print("=" * 60)
            print("\nNo user profile found. Let's set up your uDOS installation!")
            print("\nWe'll capture:")
            print("  • Your identity (username, role, timezone, location)")
            print("  • Installation settings (OS type, lifespan mode)")
            print("  • Capability preferences (cloud services, integrations)")
            print("\nThis data will be stored securely in the Wizard keystore.")
            print("-" * 60)

            # Check if TS runtime is built
            ts_runtime_path = (
                self.repo_root / "core" / "grid-runtime" / "dist" / "index.js"
            )
            if not ts_runtime_path.exists():
                print("\nBuilding TypeScript runtime (auto-heal)...")
                print("   This may take 30-60 seconds on first build...\n")

                # Verify Node.js and npm are available before attempting build
                try:
                    node_check = subprocess.run(
                        ["node", "--version"], capture_output=True, timeout=5, text=True
                    )
                    npm_check = subprocess.run(
                        ["npm", "--version"], capture_output=True, timeout=5, text=True
                    )

                    if node_check.returncode != 0 or npm_check.returncode != 0:
                        print("   Error: Node.js/npm not available.\n")
                        print("   The TypeScript runtime requires Node.js and npm.")
                        print("\n   Please install Node.js from: https://nodejs.org/")
                        print("   Then try again with:")
                        build_script = (
                            self.repo_root / "core" / "tools" / "build_ts_runtime.sh"
                        )
                        print(f"      bash {build_script}")
                        return

                except Exception as e:
                    print("   Warn: Could not verify Node.js/npm availability.\n")
                    print(f"   Error: {e}")
                    print("\n   Try manually building:")
                    build_script = (
                        self.repo_root / "core" / "tools" / "build_ts_runtime.sh"
                    )
                    print(f"      bash {build_script}")
                    return

                # Self-heal: automatically build the TS runtime
                build_script = self.repo_root / "core" / "tools" / "build_ts_runtime.sh"
                if build_script.exists():
                    try:
                        proc = self._run_with_progress(
                            "installation",
                            "TypeScript runtime build",
                            lambda: subprocess.run(
                                ["bash", str(build_script)],
                                cwd=str(self.repo_root),
                                capture_output=True,
                                text=True,
                            ),
                            spinner_label="⏳ Building TS runtime",
                        )
                        stdout, stderr = proc.stdout, proc.stderr

                        if proc.returncode == 0:
                            print("   TypeScript runtime built successfully.")
                            self.logger.info("[SETUP] TS runtime auto-built")
                            time.sleep(0.2)
                        else:
                            print("   Error: Build failed.\n")

                            # Combine stdout and stderr for complete error picture
                            output_text = (stdout or "") + (stderr or "")

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
                            log_path = (
                                self.repo_root / "core" / "grid-runtime" / "build.log"
                            )
                            print(f"      tail -100 {log_path}")
                            return
                    except Exception as e:
                        print(f"   Error: Build error: {e}\n")
                        print("   To fix manually, run:")
                        print(f"      bash {build_script}")
                        return
                else:
                    print(f"   Error: Build script not found: {build_script}")
                    return

            # TS runtime is available - run setup story automatically
            print()
            if self._ask_yes_no("Run setup story now"):
                print("\nLaunching setup story...\n")

                # Auto-execute the STORY tui-setup command
                result = self.dispatcher.dispatch(
                    "STORY tui-setup", game_state=self.state
                )

                # Check if this is a form-based story
                if result.get("story_form"):
                    collected_data = self._handle_story_form(result["story_form"])
                    print("\nSetup form completed.")
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
        """Apply simplified TUI message theme to the provided message."""
        themed = self.theme.format(text, map_level=self._infer_tui_map_level())
        width = ViewportService().get_cols()
        lines = themed.splitlines()
        clamped = [truncate_ansi_to_width(line, width) for line in lines]
        output = "\n".join(clamped)
        if themed.endswith("\n"):
            output += "\n"
        return output

    def _infer_tui_map_level(self) -> str | None:
        """Infer map-level theme bucket for TUI messaging."""
        from core.services.unified_config_loader import get_config

        env_level = get_config("UDOS_TUI_MAP_LEVEL", "").strip().lower()
        if env_level:
            return env_level

        loc = str(getattr(self.state, "current_location", "") or "").upper()
        if ":SUB:" in loc or ":D" in loc:
            return "dungeon"

        marker = "L"
        idx = loc.find(marker)
        if idx == -1 or idx + 4 > len(loc):
            return "foundation"

        layer_raw = loc[idx + 1 : idx + 4]
        if not layer_raw.isdigit():
            return "foundation"

        layer = int(layer_raw)
        if layer >= 700:
            return "galaxy"
        return "foundation"

    def _show_component_status(self) -> None:
        """Show detected components."""
        print("\nComponent Detection:\n")
        for comp_name, comp in self.components.items():
            status = "✅" if comp.state == ComponentState.AVAILABLE else "❌"
            version_str = f" ({comp.version})" if comp.version else ""
            line = f"  {status} {comp.name.upper():12} {comp.description}{version_str}"
            print(self._theme_text(line))
        print()

    def _record_logic_output(
        self,
        prompt: str,
        response: str,
        model: str,
        source: str,
        mode: str,
        file_path: str | None = None,
    ) -> dict[str, Any]:
        """Store logic-assist local output and emit a unified log entry."""
        self.logic_local_counter += 1
        entry = {
            "id": self.logic_local_counter,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
            "model": model,
            "source": source,
            "mode": mode,
            "file_path": file_path,
        }
        self.logic_local_outputs.append(entry)
        if len(self.logic_local_outputs) > self.logic_local_limit:
            self.logic_local_outputs = self.logic_local_outputs[-self.logic_local_limit :]

        try:
            logic_logger = get_logger("core", category="logic-local-output", name="ucode")
            preview = (response or "").strip().splitlines()
            logic_logger.event(
                "info",
                "logic.local.output",
                f"LOGIC {mode} output stored",
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

    def _format_logic_output_summary(self, entry: dict[str, Any]) -> str:
        """Return a collapsed summary line for a logic-assist output entry."""
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
            f"  Tip: LOGIC LOCAL SHOW {entry.get('id')}"
        )

    def _format_logic_output_full(self, entry: dict[str, Any]) -> str:
        """Return full output text for a logic-assist output entry."""
        header = [
            "═══ LOGIC LOCAL OUTPUT ═══",
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

    def _cmd_logic_local(self, args: str) -> None:
        """Show stored logic-assist local outputs."""
        tokens = args.strip().split()
        if not tokens:
            limit = 5
            entries = self.logic_local_outputs[-limit:]
        elif tokens[0].upper() in ("SHOW", "OPEN"):
            if len(tokens) < 2 or not tokens[1].isdigit():
                print(self._theme_text("Usage: LOGIC LOCAL SHOW <id>"))
                return
            entry_id = int(tokens[1])
            entry = next(
                (e for e in self.logic_local_outputs if e["id"] == entry_id), None
            )
            if not entry:
                print(self._theme_text(f"No logic output with id {entry_id}"))
                return
            print(self._theme_text(self._format_logic_output_full(entry)))
            return
        elif tokens[0].upper() == "CLEAR":
            self.logic_local_outputs = []
            print(self._theme_text("Logic local output log cleared."))
            return
        else:
            try:
                limit = int(tokens[0])
            except ValueError:
                print(
                    self._theme_text(
                        "Usage: LOGIC LOCAL [N] | LOGIC LOCAL SHOW <id> | LOGIC LOCAL CLEAR"
                    )
                )
                return
            entries = self.logic_local_outputs[-limit:]

        if not entries:
            print(self._theme_text("No logic local outputs yet."))
            return
        print(self._theme_text("\n═══ LOGIC LOCAL OUTPUTS ═══\n"))
        for entry in entries:
            print(self._theme_text(self._format_logic_output_summary(entry)))
            print(self._theme_text(""))

    def _cmd_logic_fallback(self, args: str) -> None:
        """Configure logic-assist auto-fallback mode."""
        token = args.strip().lower()
        if token in {"on", "true", "yes"}:
            self._set_dev_mode_auto_fallback(True)
            print(self._theme_text("Logic fallback set to auto (on)."))
            return
        if token in {"off", "false", "no"}:
            self._set_dev_mode_auto_fallback(False)
            print(self._theme_text("Logic fallback set to manual (off)."))
            return
        current = "on" if self._dev_mode_auto_fallback_enabled() else "off"
        print(self._theme_text("Usage: LOGIC FALLBACK on|off"))
        print(self._theme_text(f"Current: {current}"))

    def _parse_logic_file_args(self, args: str) -> dict[str, Any]:
        """Parse LOGIC command args for file + optional range + cloud flag."""
        tokens = args.strip().split()
        use_cloud = False
        clean_tokens: list[str] = []
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

        if (
            len(clean_tokens) >= 3
            and clean_tokens[1].isdigit()
            and clean_tokens[2].isdigit()
        ):
            line_start = int(clean_tokens[1])
            line_end = int(clean_tokens[2])
        elif len(clean_tokens) >= 2 and any(
            sep in clean_tokens[1] for sep in (":", "-", "..")
        ):
            parts = clean_tokens[1].replace("..", ":").replace("-", ":").split(":")
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

    def _run_logic_cloud(self, prompt: str) -> dict[str, Any]:
        """Run a logic-assist cloud request via Wizard server."""
        url = f"{self._wizard_base_url()}/api/ucode/logic/cloud"
        payload = {"prompt": prompt, "mode": "conversation", "workspace": "core"}
        quota_message = (
            "⚠️ Cloud quota exceeded (429 Too Many Requests). "
            "Try using local model, OpenRouter, or API manager. "
            "Cloud will auto-retry after quota resets."
        )
        wizard_quota = False
        try:
            response = http_post(
                url, headers=self._wizard_headers(), json_data=payload, timeout=15
            )
            if response.get("status_code") == 429:
                wizard_quota = True
            if response.get("status_code") == 200:
                data = (
                    response.get("json")
                    if isinstance(response.get("json"), dict)
                    else {}
                )
                return {
                    "response": data.get("response", ""),
                    "model": data.get("model", ""),
                }
        except HTTPError as exc:
            if exc.code == 429:
                wizard_quota = True
            if exc.code == 0:
                return {
                    "response": (
                        "❌ Wizard cloud route unavailable. "
                        "Web gate is closed in core. Run WIZARD START to manage networking."
                    ),
                    "model": "wizard-offline",
                }
        except Exception:
            return {
                "response": (
                    "❌ Wizard cloud route unavailable. "
                    "Web gate is closed in core. Run WIZARD START to manage networking."
                ),
                "model": "wizard-offline",
            }

        if wizard_quota:
            return {"response": quota_message, "model": "cloud-quota-exceeded"}

        return {
            "response": (
                "❌ Wizard cloud route failed. "
                "Use WIZARD START to manage networking and provider access."
            ),
            "model": "wizard-cloud-error",
        }

    def _run_ok_cloud(self, prompt: str) -> dict[str, Any]:
        """Compatibility alias for older ok-cloud callers."""
        return self._run_logic_cloud(prompt)

    def _run_logic_local(self, prompt: str, model: str | None = None) -> str:
        """Run the local logic-assist request through the contributor lane."""
        from core.services.provider_registry import (
            ProviderNotAvailableError,
            ProviderType,
            get_provider,
        )

        try:
            vibe_provider = get_provider(ProviderType.VIBE_SERVICE)
        except ProviderNotAvailableError as exc:
            raise RuntimeError("Local logic-assist provider not available") from exc

        target_model = model or self._get_dev_mode_default_model()

        import concurrent.futures

        def generate_with_timeout(vibe, prompt, timeout=30):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(vibe.generate, prompt, "markdown")
                try:
                    return future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    return f"❌ Model generation timed out after {timeout}s."

        # Try primary model
        try:
            if callable(vibe_provider):
                vibe = vibe_provider(model=target_model)
            elif hasattr(vibe_provider, "create"):
                vibe = vibe_provider.create(model=target_model)
            else:
                vibe = vibe_provider
            return generate_with_timeout(vibe, prompt, timeout=30)
        except Exception as exc:
            fallback_model = self._get_dev_mode_fallback_model()
            if fallback_model and fallback_model != target_model:
                self.logger.warning(
                    f"[LOGIC] Primary model {target_model} failed, trying fallback {fallback_model}: {exc}"
                )
                try:
                    if callable(vibe_provider):
                        vibe = vibe_provider(model=fallback_model)
                    elif hasattr(vibe_provider, "create"):
                        vibe = vibe_provider.create(model=fallback_model)
                    else:
                        vibe = vibe_provider
                    return generate_with_timeout(vibe, prompt, timeout=30)
                except Exception as fallback_exc:
                    self.logger.error(
                        f"[LOGIC] Fallback model {fallback_model} also failed: {fallback_exc}"
                    )
                    return f"❌ Both primary and fallback models failed: {exc} / {fallback_exc}"
            return f"❌ Model generation failed: {exc}"

    def _run_with_spinner(
        self, label: str, func: Callable[[], Any], mood: str = "busy"
    ) -> Any:
        """Run a long action with a lightweight spinner + elapsed seconds."""
        from core.tui.ui_elements import Spinner

        spinner = Spinner(label=label, show_elapsed=True)
        previous_mood = self.renderer.get_mood()
        self.renderer.set_mood(mood, pace=0.4, blink=True)

        stop = threading.Event()

        def spin() -> None:
            spinner.start()
            while not stop.is_set():
                if self._get_io_phase() == IOLifecyclePhase.INPUT:
                    time.sleep(spinner.interval)
                    continue
                spinner.tick()
                time.sleep(spinner.interval)
            spinner.stop(f"{label} done")

        thread = threading.Thread(target=spin, daemon=True)
        thread.start()
        try:
            with self._io_phase_scope(IOLifecyclePhase.BACKGROUND):
                result = func()
        except Exception:
            self.renderer.set_mood(previous_mood, pace=0.7, blink=True)
            stop.set()
            thread.join(timeout=2)
            raise
        stop.set()
        thread.join(timeout=2)
        self.renderer.set_mood(previous_mood, pace=0.7, blink=True)
        return result

    def _run_logic_request(
        self,
        prompt: str,
        mode: str,
        file_path: str | None = None,
        use_cloud: bool = False,
    ) -> None:
        """Execute a logic-assist request with optional cloud fallback."""
        model = self._get_dev_mode_default_model()
        source = "local"
        response = None
        auto_fallback = self._dev_mode_auto_fallback_enabled()
        from core.services.unified_config_loader import get_bool_config

        dev_mode = get_bool_config("UDOS_DEV_MODE")
        if dev_mode and not use_cloud:
            auto_fallback = False

        if use_cloud:
            try:
                print(self._theme_text("LOGIC → Cloud (Wizard)"))
                self._ui_line("Logic cloud request...", level="info")
                cloud_result = self._run_logic_cloud(prompt)
                response = cloud_result.get("response")
                model = cloud_result.get("model") or model
                source = "cloud"
            except Exception as exc:
                print(
                    self._theme_text(
                        f"⚠️  Cloud failed ({exc}). Falling back to local logic assist."
                    )
                )
                response = None

        if response is None:
            print(self._theme_text(f"LOGIC → Local ({model})"))
            try:
                self._ui_line("Logic local request...", level="info")
                response = self._run_logic_local(prompt, model=model)
            except Exception as exc:
                should_try_cloud = (
                    auto_fallback and not use_cloud
                ) or self._get_dev_mode_primary_provider() == "cloud"
                if should_try_cloud:
                    try:
                        print(
                            self._theme_text("⚠️  Local failed. Trying Wizard cloud review.")
                        )
                        self._ui_line("Logic fallback cloud request...", level="info")
                        cloud_result = self._run_logic_cloud(prompt)
                        response = cloud_result.get("response")
                        model = cloud_result.get("model") or model
                        source = "cloud"
                    except Exception as cloud_exc:
                        print(self._theme_text(f"❌ Logic local failed: {exc}"))
                        print(
                            self._theme_text(f"❌ Cloud fallback failed: {cloud_exc}")
                        )
                        return
                else:
                    print(self._theme_text(f"❌ Logic local failed: {exc}"))
                    return

        entry = self._record_logic_output(
            prompt=prompt,
            response=response,
            model=model,
            source=source,
            mode=mode,
            file_path=str(file_path) if file_path else None,
        )
        print(self._theme_text(""))
        self.renderer.stream_text(entry.get("response") or "", prefix="logic> ")

        if (
            not use_cloud
            and auto_fallback
            and not dev_mode
            and self._dev_mode_cloud_sanity_check_enabled()
        ):
            if self._needs_cloud_sanity_check(entry.get("response") or ""):
                try:
                    print(self._theme_text("\nLOGIC → Cloud sanity check"))
                    self._ui_line("Logic cloud sanity check...", level="info")
                    cloud_result = self._run_logic_cloud(prompt)
                    cloud_response = cloud_result.get("response") or ""
                    if cloud_response:
                        self.renderer.stream_text(cloud_response, prefix="logic-check> ")
                except Exception as exc:
                    print(self._theme_text(f"⚠️  Cloud sanity check failed: {exc}"))

    def _needs_cloud_sanity_check(self, response: str) -> bool:
        """Heuristic: request cloud sanity check when local confidence is low."""
        text = (response or "").strip()
        if not text:
            return False
        if len(text) < 160:
            return True
        lowered = text.lower()
        uncertain_phrases = [
            "i'm not sure",
            "i am not sure",
            "not sure",
            "unsure",
            "i think",
            "maybe",
            "might be",
            "cannot",
            "can't",
            "unable",
            "no access",
            "need more information",
            "not enough context",
            "as an ai",
        ]
        return any(phrase in lowered for phrase in uncertain_phrases)

    def _run_dev_mode_setup(self) -> None:
        """Install local Dev Mode helper stack for the logic-assist contributor lane."""
        print("")
        self._ui_line("SETUP: Installing Dev Mode helpers", level="milestone")
        gate_open = bool(gate_status().get("gate_open"))
        if not gate_open:
            allow_downloads = self._ask_yes_no(
                "Allow downloads for setup now",
                default=False,
                context="First-run bootstrap may need temporary web access",
                help_text="Gate opens only for setup and closes automatically",
            )
            if not allow_downloads:
                self._ui_line("Web gate closed. Setup skipped.", level="warn")
                self._ui_line(
                    "Run WIZARD START to manage networking when ready.", level="info"
                )
                print("")
                return
        try:
            from core.services.logic_assist_setup import run_logic_assist_setup

            with bootstrap_download_gate(opened_by="core.tui.logic_setup"):
                self._ui_line("Web gate open for setup downloads", level="info")
                result = self._run_with_progress(
                    "installation",
                    "Logic assist contributor installation",
                    lambda: run_logic_assist_setup(
                        self.repo_root, log=lambda msg: print(self._theme_text(msg))
                    ),
                    spinner_label="⏳ Installing Logic Assist contributor tooling",
                )
            self.dev_mode_config = self._load_dev_mode_config()
            for warning in result.get("warnings", []):
                self._ui_line(warning, level="warn")
        except Exception as exc:
            self._ui_line(f"SETUP failed: {exc}", level="error")
        finally:
            close_bootstrap_gate(reason="setup-complete")
            self._ui_line(
                "Web gate closed. WIZARD START to manage networking.", level="info"
            )
        self._ui_line("SETUP complete", level="ok")
        print("")

    def _maybe_run_dev_mode_setup(self, requested: bool) -> None:
        if not requested:
            return
        try:
            self._run_dev_mode_setup()
        except Exception as exc:
            print(self._theme_text(f"⚠️  Dev Mode setup skipped: {exc}"))

    def _cmd_logic_explain(self, args: str) -> None:
        """LOGIC EXPLAIN <file> [start end] [--cloud]."""
        parsed = self._parse_logic_file_args(args)
        if parsed.get("error"):
            print(self._theme_text("Usage: LOGIC EXPLAIN <file> [start end] [--cloud]"))
            return
        path = parsed["path"]
        if not path.exists():
            print(self._theme_text(f"File not found: {path}"))
            return
        content = path.read_text(encoding="utf-8", errors="ignore")
        if parsed.get("line_start") and parsed.get("line_end"):
            lines = content.splitlines()
            content = "\n".join(lines[parsed["line_start"] - 1 : parsed["line_end"]])
        prompt = (
            f"Explain this code from {path}:\n\n"
            f"```python\n{content}\n```\n\n"
            "Provide: 1) purpose, 2) key logic, 3) risks or follow-ups."
        )
        self._run_logic_request(
            prompt, mode="EXPLAIN", file_path=path, use_cloud=parsed.get("use_cloud")
        )

    def _cmd_logic_diff(self, args: str) -> None:
        """LOGIC DIFF <file> [start end] [--cloud]."""
        parsed = self._parse_logic_file_args(args)
        if parsed.get("error"):
            print(self._theme_text("Usage: LOGIC DIFF <file> [start end] [--cloud]"))
            return
        path = parsed["path"]
        if not path.exists():
            print(self._theme_text(f"File not found: {path}"))
            return
        content = path.read_text(encoding="utf-8", errors="ignore")
        if parsed.get("line_start") and parsed.get("line_end"):
            lines = content.splitlines()
            content = "\n".join(lines[parsed["line_start"] - 1 : parsed["line_end"]])
        prompt = (
            f"Propose a unified diff for improvements to {path}.\n\n"
            f"```python\n{content}\n```\n\n"
            "Return a unified diff only (no commentary)."
        )
        self._run_logic_request(
            prompt, mode="DIFF", file_path=path, use_cloud=parsed.get("use_cloud")
        )

    def _cmd_logic_patch(self, args: str) -> None:
        """LOGIC PATCH <file> [start end] [--cloud]."""
        parsed = self._parse_logic_file_args(args)
        if parsed.get("error"):
            print(self._theme_text("Usage: LOGIC PATCH <file> [start end] [--cloud]"))
            return
        path = parsed["path"]
        if not path.exists():
            print(self._theme_text(f"File not found: {path}"))
            return
        content = path.read_text(encoding="utf-8", errors="ignore")
        if parsed.get("line_start") and parsed.get("line_end"):
            lines = content.splitlines()
            content = "\n".join(lines[parsed["line_start"] - 1 : parsed["line_end"]])
        prompt = (
            f"Draft a patch (unified diff) for {path}. Keep the diff minimal.\n\n"
            f"```python\n{content}\n```\n\n"
            "Return a unified diff only."
        )
        self._run_logic_request(
            prompt, mode="PATCH", file_path=path, use_cloud=parsed.get("use_cloud")
        )

    def _cmd_logic_route(self, args: str) -> None:
        """LOGIC ROUTE <prompt> [--dry-run]."""
        from core.services.ok_router import plan_route

        raw = args.strip()
        if not raw:
            print(self._theme_text("Usage: LOGIC ROUTE <prompt> [--dry-run]"))
            return
        tokens = raw.split()
        dry_run = False
        cleaned: list[str] = []
        for token in tokens:
            if token.lower() == "--dry-run":
                dry_run = True
                continue
            cleaned.append(token)
        prompt = " ".join(cleaned).strip()
        if not prompt:
            print(self._theme_text("Usage: LOGIC ROUTE <prompt> [--dry-run]"))
            return

        plan = plan_route(prompt)
        plan_dict = plan.to_dict()

        lines = [
            "═══ LOGIC ROUTE PLAN ═══",
            f"Intent: {plan_dict.get('intent')}",
            f"Target: {plan_dict.get('target')}",
            f"Risk: {plan_dict.get('risk_level')}",
            f"Context: {', '.join(plan_dict.get('context_scope', []))}",
            "Commands:",
        ]
        for cmd in plan_dict.get("commands", []):
            lines.append(f"  - {cmd}")
        if plan_dict.get("notes"):
            lines.append("Notes:")
            for note in plan_dict.get("notes", []):
                lines.append(f"  - {note}")

        print(self._theme_text("\n" + "\n".join(lines) + "\n"))

        if dry_run:
            return

        # Execute mapped commands
        for cmd in plan_dict.get("commands", []):
            if not cmd:
                continue
            result = self.dispatcher.dispatch(
                cmd, parser=self.prompt, game_state=self.state
            )
            output = self.renderer.render(result)
            print(output)

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
            print("Usage: FKEYS [F1-F10]")
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
            wizard_base_url = self._wizard_base_url().rstrip("/")
            manager = get_wizard_process_manager()
            before = manager.status(base_url=wizard_base_url)
            status = self._run_with_progress(
                "loading",
                "Wizard startup",
                lambda: manager.ensure_running(
                    base_url=wizard_base_url, wait_seconds=45
                ),
                spinner_label="⏳ Starting Wizard",
            )
            if status.connected:
                self._ui_line(
                    "Wizard already running"
                    if before.connected
                    else "Wizard Server started",
                    level="ok",
                )
                if status.pid:
                    self._ui_line(f"PID: {status.pid}", level="info")
                sys.stdout.flush()
                return

            self._ui_line(f"Wizard unavailable ({status.message})", level="warn")
            self._ui_line(
                "Check memory/logs/wizard-daemon.log for startup logs", level="info"
            )
            sys.stdout.flush()

        except Exception as e:
            self.logger.error(f"Failed to start Wizard: {e}")
            self._ui_line(f"Error: {e}", level="error")
            sys.stdout.flush()

    def _wizard_stop(self) -> None:
        """Stop Wizard server."""
        try:
            wizard_base_url = self._wizard_base_url().rstrip("/")
            manager = get_wizard_process_manager()
            status = self._run_with_progress(
                "loading",
                "Wizard stop request",
                lambda: manager.stop(base_url=wizard_base_url, timeout_seconds=8),
                spinner_label="⏳ Stopping Wizard",
            )
            if status.connected or status.running:
                self._ui_line(
                    "Wizard Server still responding after stop command", level="warn"
                )
            else:
                self._ui_line("Wizard Server stopped", level="ok")

            sys.stdout.flush()

        except Exception as e:
            self.logger.error(f"Failed to stop Wizard: {e}")
            self._ui_line(f"Error: {e}", level="error")
            sys.stdout.flush()

    def _wizard_status(self) -> None:
        """Check Wizard status."""
        wizard_base_url = self._wizard_base_url().rstrip("/")
        try:
            resp = self._run_with_progress(
                "loading",
                "Wizard status check",
                lambda: http_get(f"{wizard_base_url}/health", timeout=2),
                spinner_label="⏳ Checking Wizard status",
            )
            if resp.get("status_code") == 200:
                self._ui_line(f"Wizard running on {wizard_base_url}", level="ok")
                data = resp.get("json") if isinstance(resp.get("json"), dict) else {}
                if "status" in data:
                    self._ui_line(f"Status: {data['status']}", level="info")
            else:
                self._ui_line("Wizard not responding", level="error")
        except HTTPError as exc:
            if exc.code == 0:
                self._ui_line("Wizard not running", level="error")
            else:
                self._ui_line(f"Error checking status: HTTP {exc.code}", level="warn")
        except Exception as e:
            self._ui_line(f"Error checking status: {e}", level="warn")

    def _wizard_console(self) -> None:
        """Enter Wizard interactive console."""
        try:
            print("  Launching Wizard interactive console...")
            env = dict(os.environ)
            env.setdefault("UV_PROJECT_ENVIRONMENT", ".venv")
            subprocess.run(
                ["uv", "run", "python", "wizard/wizard_tui.py"],
                cwd=str(self.repo_root),
                env=env,
                check=False,
            )

        except Exception as e:
            self.logger.error(f"Failed to launch Wizard console: {e}")
            print(f"  ❌ Error: {e}")

    def _wizard_page(self, page: str) -> None:
        """Show Wizard page via API."""
        wizard_base_url = self._wizard_base_url().rstrip("/")
        try:
            normalized_page = page.lower()
            if normalized_page == "ai":
                normalized_page = "logic"
            # Map page names to API endpoints
            page_map = {
                "status": "/health",
                "logic": "/api/logic/status",
                "services": "/api/status",
                "devices": "/api/devices",
                "quota": "/api/logic/status",
                "logs": "/api/logs",
            }

            endpoint = page_map.get(normalized_page)
            if not endpoint:
                self._ui_line(f"Unknown page: {page}", level="error")
                self._ui_line(f"Available: {', '.join(page_map.keys())}", level="info")
                return

            resp = self._run_with_progress(
                "loading",
                f"Wizard page fetch ({normalized_page})",
                lambda: http_get(f"{wizard_base_url}{endpoint}", timeout=5),
                spinner_label=f"⏳ Fetching Wizard page: {normalized_page}",
            )
            if resp.get("status_code") == 200:
                data = resp.get("json") if isinstance(resp.get("json"), dict) else {}
                print(json.dumps(data, indent=2))
            else:
                self._ui_line(
                    f"Request failed: {resp.get('status_code', 'unknown')}",
                    level="error",
                )

        except HTTPError as exc:
            if exc.code == 0:
                self._ui_line(
                    "Wizard not running. Start with: WIZARD start", level="error"
                )
            else:
                self._ui_line(f"Request failed: {exc.code}", level="error")
        except Exception as e:
            self._ui_line(f"Error: {e}", level="error")

    def _cmd_exit(self, args: str) -> None:
        """Exit uCODE."""
        self.running = False
        print("\nGoodbye!")

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
            self._emit_lines([
                "",
                "=" * 60,
                "Ghost Mode (Demo/Test Access)",
                "=" * 60,
                "",
                "You're currently in ghost mode with limited access.",
                "To set up your identity and unlock full features:",
                "",
                "  SETUP",
                "",
                "Or view this setup prompt later:",
                "  SETUP --profile",
                "",
                "=" * 60,
                "",
            ])


def main():
    """Compatibility shim for direct module execution."""
    from core.tui.ucode_entry import main as entry_main

    entry_main()


if __name__ == "__main__":
    main()
