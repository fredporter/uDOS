"""
uDOS v1.2.0 - Assistant Command Handler (DEPRECATED)

⚠️  DEPRECATION NOTICE:
    ASSISTANT commands are deprecated as of v1.2.0
    This handler routes to extensions/assistant (lazy loaded)
    Will be removed in v2.0.0

    Migration:
        ASSISTANT ASK <query> → GENERATE DO <query>
        OK ASK <query> → GENERATE DO <query>

    See: wiki/Migration-Guide-Assistant-to-Generate.md

Legacy commands (deprecated):
- ASSISTANT ASK: Ask Gemini AI (use GENERATE DO)
- ASSISTANT CLEAR: Clear conversation history
- ASSISTANT STATUS: Show status and usage
- OK ASK: Legacy command (use GENERATE DO)
- OK DEV: GitHub Copilot CLI (external tool)

Version: 1.2.0 (Deprecated)
Previous: 1.1.0 (Active)
"""

from typing import Optional, Dict
from .base_handler import BaseCommandHandler


class AssistantCommandHandler(BaseCommandHandler):
    """
    DEPRECATED: Handles ASSISTANT commands (routes to extensions/assistant).

    Deprecation Info:
        - Status: DEPRECATED as of v1.2.0
        - Removal: v2.0.0 (Q2 2025)
        - Replacement: GENERATE commands (offline-first)
        - Migration: wiki/Migration-Guide-Assistant-to-Generate.md

    This handler now acts as a compatibility shim that routes to
    extensions/assistant with deprecation warnings.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Lazy load extension handler
        self._extension_handler = None

        # Legacy properties (for backward compatibility)
        self.gemini = None  # Lazy initialization
        self._workspace_manager = None
        self._knowledge_manager = None
        self._audit_logger = None  # Lazy load
        self._session_analytics = None  # Lazy load

        # Role-based access control (v1.1.0)
        # Get role from config_manager (set via CONFIG ROLE wizard)
        self.user_role = self.config_manager.get('USER_ROLE', 'user') if hasattr(self, 'config_manager') and self.config_manager else "user"

    @property
    def extension_handler(self):
        """Lazy load assistant extension handler."""
        if self._extension_handler is None:
            try:
                from extensions.assistant.handler import get_assistant_handler
                self._extension_handler = get_assistant_handler(config_manager=self.config_manager)
            except ImportError as e:
                # Extension not available - return None
                # Commands will show helpful error message
                pass
        return self._extension_handler

    @property
    def workspace_manager(self):
        """Lazy load workspace manager."""
        if self._workspace_manager is None:
            from core.utils.files import WorkspaceManager
            self._workspace_manager = WorkspaceManager()
        return self._workspace_manager

    @property
    def knowledge_manager(self):
        """Lazy load knowledge manager."""
        if self._knowledge_manager is None:
            from core.knowledge import get_knowledge_manager
            self._knowledge_manager = get_knowledge_manager()
        return self._knowledge_manager

    @property
    def audit_logger(self):
        """Lazy load API audit logger."""
        if self._audit_logger is None:
            from core.services.api_audit import get_audit_logger
            self._audit_logger = get_audit_logger()
        return self._audit_logger

    @property
    def session_analytics(self):
        """Lazy load session analytics."""
        if self._session_analytics is None:
            from core.services.session_analytics import get_session_analytics
            self._session_analytics = get_session_analytics()
        return self._session_analytics

    def _initialize_gemini(self):
        """
        DEPRECATED: Initialize Gemini service (now in extension).

        Returns None for backward compatibility.
        Extension handler will manage Gemini initialization.
        """
        # No longer needed - extension handler manages Gemini
        return None

    def _check_api_access(self, operation: str) -> tuple[bool, Optional[str]]:
        """
        DEPRECATED: Check API access (kept for backward compatibility).

        All users can now access commands - extension handles permissions.
        """
        # Always allow - extension will handle permission checks
        return True, None

    def _log_api_usage(self, operation: str, query: str, tokens: int = None,
                      cost: float = None, duration_ms: float = None,
                      success: bool = True, error: str = None):
        """
        DEPRECATED: Log API usage (now handled by extension).

        Kept for backward compatibility but does nothing.
        """
        # Extension handler now manages API logging
        pass

    def handle(self, command, params, grid):
        """
        Route assistant commands to extension handler (with deprecation warnings).

        Args:
            command: Command name (ASSISTANT, OK)
            params: Command parameters
            grid: Grid instance

        Returns:
            Command result message with deprecation warning
        """
        # Show deprecation notice
        deprecation_warning = """⚠️  ASSISTANT commands are deprecated as of v1.2.0
    Use GENERATE commands instead (offline-first)

    Migration:
        ASSISTANT ASK <query> → GENERATE DO <query>
        OK ASK <query> → GENERATE DO <query>

    See: wiki/Migration-Guide-Assistant-to-Generate.md

"""

        # Try to route to extension handler
        if self.extension_handler:
            # Build context for extension
            context = {
                'workspace': self.workspace_manager.current_workspace if self.workspace_manager else 'sandbox',
                'grid': grid,
                'user_role': self.user_role
            }

            # Route to extension (it will show its own deprecation notice)
            return self.extension_handler.handle(command, params, context)

        # Extension not available - show helpful message
        if command == "ASSISTANT" or command == "OK":
            if not params:
                return deprecation_warning + self._handle_ok_help()

            subcommand = params[0].upper()

            if subcommand == "ASK":
                return f"""{deprecation_warning}❌ Assistant extension not available

The ASSISTANT extension has been moved to extensions/assistant
and is now optional (uDOS works fully offline without it).

💡 Offline Alternative (No API Key Required):
   GENERATE DO <your question>

   This uses uDOS's built-in offline AI engine with:
   - 166+ survival guides from knowledge bank
   - FAQ database (40+ common questions)
   - User memory and context tracking
   - 70-90% confidence on most queries
   - No API costs!

💡 To Enable Gemini (Optional):
   1. Get API key: https://makersuite.google.com/app/apikey
   2. Add to .env: GEMINI_API_KEY=your_key_here
   3. Extension will load automatically

💡 Migration Guide:
   wiki/Migration-Guide-Assistant-to-Generate.md
"""
            elif subcommand == "DEV":
                # DEV command is special - routes to GitHub Copilot CLI (external)
                return self._handle_dev(params[1:])
            elif subcommand == "STATUS" or command == "STATUS":
                return f"""{deprecation_warning}❌ Assistant extension not available

Extension Status: Not loaded
Location: extensions/assistant/
Required: GEMINI_API_KEY in .env

💡 Use GENERATE STATUS instead (works offline)
"""

        # Other commands
        if command == "ANALYZE":
            return f"{deprecation_warning}Use GENERATE DO to analyze content"
        elif command == "CLEAR":
            return f"{deprecation_warning}Use GENERATE CLEAR to clear history"
        else:
            return self.get_message("ERROR_UNKNOWN_ASSISTANT_COMMAND", command=command)

    def _handle_status(self):
        """
        DEPRECATED: Display assistant status (routes to extension).
        """
        deprecation_notice = """⚠️  ASSISTANT commands are deprecated as of v1.2.0
    Use GENERATE commands instead

"""
        if self.extension_handler:
            return self.extension_handler.handle('ASSISTANT', ['STATUS'])

        return f"""{deprecation_notice}❌ Assistant extension not available

Extension moved to: extensions/assistant/
Status: Optional (uDOS works fully offline)

💡 Use GENERATE STATUS instead (works offline)
"""

    def _handle_ok_help(self):
        """Display OK command help with deprecation notice."""
        return """⚠️  OK commands are deprecated as of v1.2.0

DEPRECATED Commands:
  OK ASK <question>     - Use GENERATE DO instead
  OK DEV <task>         - Still works (GitHub Copilot CLI)

Replacement Commands:
  GENERATE DO <query>   - Offline-first AI (no API key needed)
  GENERATE GUIDE <topic> - Generate survival guides
  GENERATE SVG <desc>   - Generate diagrams (requires API)

Examples:
  OLD: OK ASK how do I purify water?
  NEW: GENERATE DO how do I purify water?

Migration: wiki/Migration-Guide-Assistant-to-Generate.md
"""

    def _handle_ask(self, params, grid):
        """
        DEPRECATED: Routes to extension handler or shows migration message.
        """
        if self.extension_handler:
            context = {
                'workspace': self.workspace_manager.current_workspace if self.workspace_manager else 'sandbox',
                'grid': grid
            }
            return self.extension_handler._handle_ask(params, context)

        return """❌ Assistant extension not available

💡 Use GENERATE DO instead (offline-first, no API key):
   GENERATE DO <your question>

Example:
   GENERATE DO how do I purify water?
"""

    def _handle_read(self, params, grid):
        """DEPRECATED: Read panel content."""
        return "❌ READ command deprecated. Use GENERATE DO to analyze content."

    def _handle_explain(self, params):
        """DEPRECATED: Explain command."""
        return "❌ EXPLAIN command deprecated. Use GENERATE DO <explain command>."

    def _handle_generate(self, params):
        """DEPRECATED: Generate script."""
        return "❌ Old GENERATE deprecated. Use: GENERATE DO <description> or GENERATE GUIDE <topic>."

    def _handle_debug(self, params):
        """DEPRECATED: Debug error."""
        return "❌ DEBUG command deprecated. Use GENERATE DO <debug error message>."

    def _handle_clear(self):
        """
        DEPRECATED: Clear conversation history.
        """
        if self.extension_handler:
            return self.extension_handler._handle_clear()

        return "❌ Assistant extension not available. Use GENERATE CLEAR instead."

    def _handle_dev(self, params):
        """
        Handle development tasks using GitHub Copilot CLI with context awareness.

        Args:
            params: [task_description]
        """
        if not params:
            return """❌ Usage: OK DEV <task>

Examples:
  OK DEV explain this error message
  OK DEV how do I fix merge conflicts
  OK DEV create a new command handler
  OK DEV optimize this function

Note: Requires GitHub Copilot CLI
Install: https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli
"""

        task = " ".join(params)

        # Check if copilot CLI is available
        import subprocess
        import shutil
        import os

        # Try new copilot CLI first, then fall back to gh copilot extension
        copilot_cmd = shutil.which('copilot')
        use_gh_extension = False

        if not copilot_cmd:
            # Fall back to gh copilot extension
            gh_cmd = shutil.which('gh')
            if gh_cmd:
                use_gh_extension = True
            else:
                return """❌ GitHub Copilot CLI not found

Install the new Copilot CLI:
  See: https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli

Or use the legacy gh extension:
  brew install gh
  gh extension install github/gh-copilot
  gh auth login
"""

        # Gather context for better suggestions
        context_info = self._gather_dev_context()

        # Enhance task with context if relevant
        enhanced_task = task
        if context_info:
            enhanced_task = f"{task}\n\nContext: {context_info}"

        try:
            if use_gh_extension:
                # Use legacy gh copilot extension
                result = subprocess.run(
                    ['gh', 'copilot', 'suggest', enhanced_task],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.getcwd()
                )
            else:
                # Use new Copilot CLI (programmatic mode)
                result = subprocess.run(
                    ['copilot', '-p', enhanced_task, '--allow-tool', 'shell'],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.getcwd()
                )

            if result.returncode != 0:
                if use_gh_extension:
                    if 'not installed' in result.stderr.lower() or 'unknown command' in result.stderr.lower():
                        return """❌ GitHub Copilot CLI extension not found

Install the new standalone Copilot CLI (recommended):
  https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli

Or install the legacy gh extension:
  gh extension install github/gh-copilot
  gh auth login
"""
                else:
                    if 'not authenticated' in result.stderr.lower():
                        return """❌ Copilot CLI not authenticated

Run: copilot auth login
"""
                return f"❌ Copilot CLI error:\n{result.stderr}"

            # Add context note if we provided extra info
            context_note = ""
            if context_info:
                context_note = f"\n📍 Context: {context_info}\n"

            cli_type = "legacy gh extension" if use_gh_extension else "CLI"
            return f"🤖 GitHub Copilot DEV ({cli_type}):{context_note}\n{result.stdout}"

        except subprocess.TimeoutExpired:
            return "⚠️  Request timeout. Please try again."
        except FileNotFoundError:
            return "❌ Copilot CLI not found in PATH"
        except Exception as e:
            return f"⚠️  Error calling Copilot CLI: {str(e)}"

    def _gather_dev_context(self):
        """Gather development context for Copilot CLI suggestions."""
        import subprocess
        import os

        context_parts = []

        # Get current directory
        cwd = os.getcwd()
        if '/uDOS' in cwd:
            context_parts.append("Working in uDOS project")

        # Try to get git branch
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                context_parts.append(f"Git branch: {branch}")
        except:
            pass

        # Get Python version if in Python project
        if os.path.exists('requirements.txt') or os.path.exists('setup.py'):
            import sys
            py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            context_parts.append(f"Python {py_version}")

        return ", ".join(context_parts) if context_parts else None

    def _search_local_knowledge(self, question):
        """
        DEPRECATED: Search local knowledge base (now in offline engine).

        Kept for backward compatibility but returns empty results.
        """
        return {
            'query': question,
            'results': [],
            'content_snippets': [],
            'note': 'Use offline AI engine or GENERATE DO command'
        }

    def _generate_fallback_response(self, question, knowledge_context):
        """
        DEPRECATED: Generate fallback response (now in offline engine).

        Returns migration message.
        """
        return "Use GENERATE DO for offline-first AI responses."

    def _extract_token_usage(self, response: str) -> Optional[Dict[str, int]]:
        """DEPRECATED: Token extraction (now in extension)."""
        return None

    def _calculate_cost(self, tokens: Optional[Dict[str, int]]) -> Optional[float]:
        """DEPRECATED: Cost calculation (now in extension)."""
        return None
