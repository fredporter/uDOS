"""
Contextual Command Prompt (v1.0.0)
===================================

Enhanced command prompt with:
- Command registry (metadata for all commands)
- Dynamic suggestions as user types
- 2-line help context (suggestions + help text)
- Autocomplete with SmartPrompt
- Integration with command dispatcher

Part of TUI Enhancement Phase 1: Input Helper Lines

Author: uDOS Engineering
Date: 2026-01-30
Version: v1.0.0
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
import os
import shutil
from core.utils.tty import interactive_tty_status
from .enhanced_prompt import EnhancedPrompt
from core.services.logging_api import get_logger
from core.services.dev_state import get_dev_state_label


def _get_safe_logger():
    """Best-effort logger init (avoid import-time failures in tests)."""
    try:
        return get_logger("core", category="command-prompt", name="command-prompt")
    except Exception:
        import logging

        return logging.getLogger("command-prompt")


logger = _get_safe_logger()


@dataclass
class CommandMetadata:
    """Metadata for a command."""
    name: str
    help_text: str
    options: List[str] = None
    syntax: str = ""
    examples: List[str] = None
    icon: str = "⚙️"
    category: str = "General"

    def __post_init__(self):
        if self.options is None:
            self.options = []
        if self.examples is None:
            self.examples = []
        if not self.syntax:
            self.syntax = self.name


class CommandRegistry:
    """Registry of all available commands with metadata."""

    def __init__(self):
        """Initialize command registry."""
        self.commands: Dict[str, CommandMetadata] = {}
        try:
            self.logger = get_logger("core", category="command-registry", name="command-prompt")
        except Exception:
            import logging

            self.logger = logging.getLogger("command-registry")

    def register(
        self,
        name: str,
        help_text: str,
        options: Optional[List[str]] = None,
        syntax: Optional[str] = None,
        examples: Optional[List[str]] = None,
        icon: str = "⚙️",
        category: str = "General",
    ) -> None:
        """
        Register a command with metadata.

        Args:
            name: Command name (will be uppercased)
            help_text: Short help description (one line)
            options: List of command options
            syntax: Command syntax (e.g., "COMMAND [args...]")
            examples: List of usage examples
            icon: Emoji icon for display
            category: Command category (General, System, Data, Navigation, etc.)
        """
        name_upper = name.upper()
        self.commands[name_upper] = CommandMetadata(
            name=name_upper,
            help_text=help_text,
            options=options or [],
            syntax=syntax or name_upper,
            examples=examples or [],
            icon=icon,
            category=category,
        )
        self.logger.debug(f"Registered command: {name_upper} ({category})")

    def get_suggestions(self, prefix: str, limit: int = 10) -> List[CommandMetadata]:
        """
        Get command suggestions matching prefix.

        Args:
            prefix: Command prefix to match
            limit: Maximum suggestions to return

        Returns:
            List of matching CommandMetadata objects
        """
        prefix_upper = prefix.upper().strip()

        if not prefix_upper:
            # Return all commands, sorted by category then name
            sorted_cmds = sorted(
                self.commands.values(),
                key=lambda x: (x.category, x.name)
            )
            return sorted_cmds[:limit]

        # Fuzzy match: prefix or substring match
        matches = []
        for cmd in self.commands.values():
            if cmd.name.startswith(prefix_upper):
                matches.append(cmd)
            elif prefix_upper in cmd.name:
                matches.append(cmd)

        # Sort by relevance (prefix match first, then substring)
        prefix_matches = [c for c in matches if c.name.startswith(prefix_upper)]
        substring_matches = [c for c in matches if not c.name.startswith(prefix_upper)]

        return (prefix_matches + substring_matches)[:limit]

    def get_command(self, name: str) -> Optional[CommandMetadata]:
        """Get command metadata by name."""
        return self.commands.get(name.upper())

    def list_all(self) -> List[CommandMetadata]:
        """Get all registered commands."""
        return sorted(
            self.commands.values(),
            key=lambda x: (x.category, x.name)
        )


class ContextualCommandPrompt(EnhancedPrompt):
    """
    Enhanced command prompt with contextual help and suggestions.

    Features:
    - Command registry integration
    - Dynamic suggestions as user types
    - 2-line context display:
      Line 1: Matching suggestions or current input
      Line 2: Help text for first matching command
    - Autocomplete with SmartPrompt
    """

    def __init__(self, registry: Optional[CommandRegistry] = None):
        """
        Initialize contextual command prompt.

        Args:
            registry: CommandRegistry instance (uses default if None)
        """
        try:
            self.logger = get_logger("core", category="contextual-prompt", name="command-prompt")
        except Exception:
            import logging

            self.logger = logging.getLogger("contextual-prompt")
        self.registry = registry or CommandRegistry()
        super().__init__(registry=self.registry)
        self.toolbar_fixed_lines = True
        self.set_bottom_toolbar_provider(self._build_command_toolbar)

    def ask_command(self, prompt_text: str = "▶ ") -> str:
        """
        Ask for command with contextual help and suggestions.

        Shows:
          ▶ [user typing...]
          ╭─ Suggestions: CMD1, CMD2, CMD3 (+N more)
          ╰─ Help: Brief command description

        Args:
            prompt_text: Prompt prefix

        Returns:
            User's command input
        """
        self.logger.debug("Asking for command with contextual help")

        # Display context lines only in fallback mode; prompt_toolkit renders live toolbar.
        if self.use_fallback:
            self._display_context_for_command("")

        # Use SmartPrompt directly - don't duplicate context printing
        # Hints are shown once at startup via _show_startup_hints()
        user_input = self.ask(prompt_text, default="")
        return user_input.strip()

    def _display_context_for_command(self, prefix: str) -> None:
        """
        Display 2-line context for command input.

        Args:
            prefix: Current user input prefix
        """
        if not self.show_context:
            return

        # Get suggestions
        suggestions = self.registry.get_suggestions(prefix, limit=5)

        # Line 1: Suggestions
        if suggestions:
            suggestion_names = [s.name for s in suggestions[:3]]
            suggestion_text = ", ".join(suggestion_names)
            if len(suggestions) > 3:
                suggestion_text += f" (+{len(suggestions) - 3} more)"
            print(f"  ╭─ Suggestions: {suggestion_text}")
        else:
            print(f"  ╭─ No matching commands")

        # Line 2: Help text for first suggestion
        if suggestions:
            first_cmd = suggestions[0]
            print(f"  ╰─ {first_cmd.icon} {first_cmd.help_text}")
        else:
            print(f"  ╰─ Type a command name to see suggestions")

    def _build_command_toolbar(self, text: str):
        """
        Build a dynamic, 2-line toolbar for prompt_toolkit.

        Line 1: Suggestions/options bar
        Line 2: Help/syntax bar
        """
        if not self.show_context:
            return ""
        raw = text or ""
        stripped = raw.strip()
        tokens = stripped.split()
        term_width = shutil.get_terminal_size(fallback=(120, 24)).columns
        ok_model = getattr(self, "ok_model", "devstral-small-2")
        ok_ctx = getattr(self, "ok_context_window", 8192)

        def _format_line(line: str) -> str:
            if not self.toolbar_fixed_lines:
                if len(line) <= term_width:
                    return line
                return line[: max(0, term_width - 1)] + "…"
            if len(line) > term_width:
                return line[: max(0, term_width - 1)] + "…"
            return line.ljust(term_width)

        def _prefix_symbol() -> str:
            if raw.startswith(":"):
                return ":"
            if raw.startswith("/"):
                return "/"
            return ""

        prefix_symbol = _prefix_symbol()
        dev_state = get_dev_state_label()

        # No input yet: show general suggestions + a rotating tip
        if not tokens:
            suggestions = self.registry.get_suggestions("", limit=5)
            line1 = self._format_suggestions_line(suggestions, prefix_symbol, label="Commands")
            line2 = f"  ↳ DEV: {dev_state}  |  Tip: Use '?' or 'OK' for AI, '/' for commands"
            return [_format_line(line1), _format_line(line2)]

        cmd_token = tokens[0].lstrip(":/")
        cmd_key = cmd_token.upper()
        cmd_meta = self.registry.get_command(cmd_key)

        # If user is still typing the command name
        if len(tokens) == 1 and not raw.endswith(" "):
            suggestions = self.registry.get_suggestions(cmd_key, limit=5)
            line1 = self._format_suggestions_line(suggestions, prefix_symbol)
            if cmd_meta:
                syntax = f"{prefix_symbol}{cmd_meta.syntax}" if prefix_symbol else cmd_meta.syntax
                line2 = f"  ↳ {cmd_meta.icon} {cmd_meta.help_text}  |  {syntax}"
            else:
                line2 = self._format_tip_line(stripped)
            return [_format_line(line1), _format_line(line2)]

        if cmd_key == "OK":
            options = ["LOCAL", "EXPLAIN", "DIFF", "PATCH", "VIBE"]
            opt_preview = ", ".join(options[:4])
            if len(options) > 4:
                opt_preview += f" (+{len(options) - 4} more)"
            line1 = f"  ⎔ OK: {opt_preview}"
            line2 = f"  ↳ 🧭 Local Vibe ({ok_model}, ctx {ok_ctx})"
            return [_format_line(line1), _format_line(line2)]

        # Otherwise, show options/next hints for the chosen command
        options = self._collect_option_hints(cmd_key, cmd_meta)

        if options:
            opt_preview = ", ".join(options[:4])
            if len(options) > 4:
                opt_preview += f" (+{len(options) - 4} more)"
            line1 = f"  ⎔ Options: {opt_preview}"
        else:
            line1 = "  ⎔ Options: (none)"

        if cmd_meta and cmd_meta.examples:
            line2 = f"  ↳ Example: {cmd_meta.examples[0]}"
        elif cmd_meta:
            line2 = f"  ↳ {cmd_meta.icon} {cmd_meta.help_text}  |  Try: HELP {cmd_meta.name}"
        else:
            line2 = self._format_tip_line(stripped)

        return [_format_line(line1), _format_line(line2)]

    def _format_suggestions_line(
        self, suggestions: List[CommandMetadata], prefix_symbol: str = "", label: str = "Suggestions"
    ) -> str:
        """Format suggestions line for toolbar."""
        if suggestions:
            names = [f"{prefix_symbol}{s.name}" for s in suggestions[:3]]
            suggestion_text = ", ".join(names)
            if len(suggestions) > 3:
                suggestion_text += f" (+{len(suggestions) - 3} more)"
            return f"  ⎔ {label}: {suggestion_text}"
        return f"  ⎔ {label}: (none)"

    def _format_tip_line(self, prefix: str) -> str:
        """Return a rotating tip/help line for variety."""
        tips = [
            "  ↳ Tip: Use ↑/↓ for history, → to accept suggestions",
            "  ↳ Tip: Press Tab to open the command selector",
            "  ↳ Tip: Add --help to see command options",
            "  ↳ Tip: Prefix OK for local Vibe (e.g., OK EXPLAIN)",
            "  ↳ Tip: Try HELP <command> for full docs",
        ]
        idx = (len(prefix) + sum(ord(c) for c in prefix)) % len(tips) if prefix else 0
        return tips[idx]

    def set_toolbar_fixed_lines(self, enabled: bool = True) -> None:
        """Enable or disable fixed-width toolbar lines to prevent wrapping."""
        self.toolbar_fixed_lines = enabled

    def _collect_option_hints(
        self, cmd_key: str, cmd_meta: Optional[CommandMetadata]
    ) -> List[str]:
        """
        Combine options from registry, autocomplete, and recent history.
        """
        merged: List[str] = []

        def _add(values: List[str]) -> None:
            for value in values:
                if value and value not in merged:
                    merged.append(value)

        if cmd_meta and cmd_meta.options:
            _add(cmd_meta.options)

        # Recent history/logs-derived options
        _add(self._extract_recent_options(cmd_key))

        # Autocomplete options
        if hasattr(self, "autocomplete_service"):
            try:
                _add(self.autocomplete_service.get_options(cmd_key))
            except Exception:
                pass

        return merged

    def _extract_recent_options(self, cmd_key: str) -> List[str]:
        """Extract recently used options/args from input history."""
        history: List[str] = []
        if hasattr(self, "input_history") and self.input_history:
            history = list(self.input_history)
        elif hasattr(self, "history") and hasattr(self.history, "get_strings"):
            try:
                history = list(self.history.get_strings())
            except Exception:
                history = []

        recent = history[-100:]
        options: List[str] = []
        args: List[str] = []

        for line in recent:
            if not line:
                continue
            parts = line.strip().split()
            if not parts:
                continue
            token = parts[0].lstrip(":/").upper()
            if token != cmd_key:
                continue

            for part in parts[1:]:
                if part.startswith("--") or part.startswith("-"):
                    if part not in options:
                        options.append(part)
                else:
                    if part not in args:
                        args.append(part)

        merged = options[:6]
        # Include a couple of frequent args as soft hints
        merged.extend([arg for arg in args[:3] if arg not in merged])
        return merged

    def ask_command_interactive(
        self,
        prompt_text: str = "▶ ",
        show_help: bool = True
    ) -> str:
        """
        Ask for command with real-time suggestion display.

        This version shows suggestions and help as user types.
        Note: Requires terminal that supports ANSI escape codes.

        Args:
            prompt_text: Prompt prefix
            show_help: Whether to show help lines

        Returns:
            User's command input
        """
        if not show_help:
            return self.ask(prompt_text, default="")

        # For now, we'll use basic version (full SmartPrompt integration
        # with real-time updates would require more complex terminal handling)
        # This is a placeholder that shows the structure

        self.logger.debug("Interactive command prompt (with context)")
        return self.ask_command(prompt_text)

    def _is_interactive(self) -> bool:
        """Check if running in interactive terminal."""
        interactive, reason = interactive_tty_status()
        if not interactive and reason:
            log = getattr(self, "logger", logger)
            log.debug("[LOCAL] Interactive check failed: %s", reason)
        return interactive


def create_default_registry() -> CommandRegistry:
    """
    Create and populate default command registry.

    This should be called during uCODE initialization to register all
    available commands with their metadata.

    Returns:
        Populated CommandRegistry instance
    """
    registry = CommandRegistry()

    # System Commands
    registry.register(
        name="STATUS",
        help_text="Show system health and component status",
        syntax="STATUS [--detailed|--quick]",
        options=["--detailed: Show all metrics", "--quick: Show summary only"],
        examples=["STATUS", "STATUS --detailed"],
        icon="📊",
        category="System",
    )

    registry.register(
        name="HELP",
        help_text="Show available commands and help",
        syntax="HELP [command]",
        options=["command: Get help for specific command"],
        examples=["HELP", "HELP WIZARD"],
        icon="❓",
        category="System",
    )

    registry.register(
        name="EXIT",
        help_text="Exit uCODE",
        syntax="EXIT",
        examples=["EXIT"],
        icon="🚪",
        category="System",
    )

    # Management Commands
    registry.register(
        name="SETUP",
        help_text="Run setup story (default) or view profile",
        syntax="SETUP [--profile|--story|--wizard]",
        examples=["SETUP", "SETUP --profile"],
        icon="⚙️",
        category="Management",
    )

    registry.register(
        name="CONFIG",
        help_text="Manage configuration variables",
        syntax="CONFIG [variable] [value]",
        examples=["CONFIG", "CONFIG seed 12345"],
        icon="🔧",
        category="Management",
    )

    registry.register(
        name="INTEGRATION",
        help_text="Show GitHub and Mistral/Ollama wiring details",
        syntax="INTEGRATION [status|github|mistral|ollama]",
        examples=["INTEGRATION status", "INTEGRATION mistral"],
        icon="🔗",
        category="System",
    )

    registry.register(
        name="OK",
        help_text="Local Vibe helpers (EXPLAIN, DIFF, PATCH, LOCAL)",
        syntax="OK <LOCAL|EXPLAIN|DIFF|PATCH|VIBE|FALLBACK> [args]",
        options=[
            "LOCAL: Show recent local outputs",
            "EXPLAIN: Summarize code in a file",
            "DIFF: Propose a diff for a file",
            "PATCH: Draft a patch with preview",
            "VIBE: Alias for LOCAL",
            "FALLBACK: Toggle auto-fallback (on|off)",
        ],
        examples=["OK EXPLAIN core/tui/ucode.py", "OK LOCAL 5", "OK FALLBACK on"],
        icon="🧭",
        category="AI",
    )

    registry.register(
        name="SHAKEDOWN",
        help_text="Full system validation and health check",
        syntax="SHAKEDOWN [--detailed] [--fresh] [--destroy-verify] [--cycle]",
        options=[
            "--detailed: Show detailed results",
            "--fresh: Validate fresh install",
            "--destroy-verify: Verify DESTROY command works",
            "--cycle: Dry-run command cycle",
        ],
        examples=["SHAKEDOWN", "SHAKEDOWN --cycle"],
        icon="✅",
        category="Management",
    )

    # Wizard Commands
    registry.register(
        name="WIZARD",
        help_text="Wizard server management (start/stop/status)",
        syntax="WIZARD [start|stop|status|logs|console|rebuild]",
        options=[
            "start: Start Wizard server",
            "stop: Stop Wizard server",
            "status: Check server status",
            "logs: View server logs",
            "console: Enter interactive console",
            "rebuild: Rebuild Wizard dashboard artifacts",
        ],
        examples=["WIZARD start", "WIZARD status", "WIZARD logs --tail", "WIZARD rebuild"],
        icon="🧙",
        category="Server",
    )

    registry.register(
        name="DEV",
        help_text="Toggle dev mode (Wizard)",
        syntax="DEV [on|off|status|restart]",
        examples=["DEV status", "DEV on", "DEV off"],
        icon="🛠️",
        category="System",
    )

    # Data Commands
    registry.register(
        name="BINDER",
        help_text="Multi-chapter project management",
        syntax="BINDER [open|create|list]",
        examples=["BINDER open", "BINDER list"],
        icon="📚",
        category="Data",
    )

    registry.register(
        name="SONIC",
        help_text="Sonic Screwdriver USB builder + device catalog",
        syntax="SONIC [status|plan|run] [options]",
        examples=[
            "SONIC STATUS",
            "SONIC PLAN --dry-run",
            "SONIC RUN --manifest config/sonic-manifest.json --dry-run",
        ],
        icon="🛠️",
        category="System",
    )

    registry.register(
        name="FILE",
        help_text="Interactive workspace and file browser",
        syntax="FILE [BROWSE|LIST|SHOW] [path]",
        options=[
            "FILE: Open workspace picker → file browser",
            "LIST [workspace]: List files in workspace",
            "SHOW <file>: Display file content",
            "HELP: Show FILE command help",
        ],
        examples=[
            "FILE",
            "FILE LIST @sandbox",
            "FILE SHOW @sandbox/readme.md",
        ],
        icon="📁",
        category="Data",
    )

    registry.register(
        name="STORY",
        help_text="Run interactive story files",
        syntax="STORY <name>",
        examples=["STORY tui-setup", "STORY onboarding"],
        icon="📖",
        category="Data",
    )

    registry.register(
        name="RUN",
        help_text="Execute TypeScript scripts (embedded in .md files)",
        syntax="RUN <file>",
        examples=["RUN script.py", "RUN automation-script.md"],
        icon="▶️",
        category="Data",
    )

    registry.register(
        name="MUSIC",
        help_text="Songscribe transcription + Groovebox import",
        syntax="MUSIC <transcribe|separate|stems|score|import> <file or url>",
        examples=[
            "MUSIC TRANSCRIBE song.mp3",
            "MUSIC SEPARATE song.mp3 --preset full_band",
            "MUSIC SCORE track.mid",
        ],
        icon="🎵",
        category="Media",
    )

    # Navigation Commands
    registry.register(
        name="MAP",
        help_text="Show spatial map",
        syntax="MAP [--zoom N]",
        examples=["MAP", "MAP --zoom 5"],
        icon="🗺️",
        category="Navigation",
    )

    registry.register(
        name="GRID",
        help_text="Render UGRID canvas (calendar/table/schedule/map/dashboard)",
        syntax="GRID <mode> [--input file.json] [--loc LOCID]",
        examples=[
            "GRID MAP --loc EARTH:SUR:L305-DA11",
            "GRID CALENDAR --input memory/events.json",
        ],
        icon="🧱",
        category="Navigation",
    )

    registry.register(
        name="ANCHOR",
        help_text="List gameplay anchors or show anchor details",
        syntax="ANCHOR [LIST] | ANCHOR SHOW <id> | ANCHOR REGISTER <id> <title>",
        examples=[
            "ANCHOR",
            "ANCHOR SHOW EARTH",
            "ANCHOR REGISTER GAME:NETHACK NetHack",
        ],
        icon="⚓",
        category="Navigation",
    )

    registry.register(
        name="GOTO",
        help_text="Travel to location",
        syntax="GOTO <location>",
        examples=["GOTO home", "GOTO market"],
        icon="🧭",
        category="Navigation",
    )

    return registry
