"""
Assistant Extension Handler
Provides ASSISTANT command interface (deprecated - use GENERATE)

Version: 1.0.0
Moved from core to extensions in v1.2.0

Deprecation Notice:
    ASSISTANT commands are deprecated as of v1.2.0
    Use GENERATE commands instead:
        ASSISTANT ASK → GENERATE DO
        OK ASK → GENERATE DO
"""

from typing import Optional
from .gemini_service import get_gemini_service


class AssistantHandler:
    """
    Handles ASSISTANT commands (deprecated).

    Commands:
        ASSISTANT ASK <query>    - Ask Gemini AI (deprecated - use GENERATE DO)
        ASSISTANT CLEAR          - Clear conversation history
        ASSISTANT STATUS         - Show status and usage stats
    """

    def __init__(self, config_manager=None):
        """
        Initialize assistant handler.

        Args:
            config_manager: ConfigManager instance for settings
        """
        self.config_manager = config_manager
        self._gemini = None  # Lazy loading

    @property
    def gemini(self):
        """Lazy load Gemini service."""
        if self._gemini is None:
            self._gemini = get_gemini_service(config_manager=self.config_manager)
        return self._gemini

    def handle(self, command: str, params: list, context: Optional[dict] = None) -> str:
        """
        Handle ASSISTANT commands.

        Args:
            command: Command name (ASSISTANT, OK)
            params: Command parameters
            context: Optional context dict (workspace, files, grid, etc.)

        Returns:
            Command result message
        """
        # Show deprecation notice for all commands
        deprecation_notice = "⚠️  ASSISTANT commands are deprecated. Use GENERATE DO instead.\n\n"

        if command == "ASSISTANT":
            if not params:
                return self._handle_help(deprecation_notice)

            subcommand = params[0].upper()
            sub_params = params[1:] if len(params) > 1 else []

            if subcommand == "ASK":
                return deprecation_notice + self._handle_ask(sub_params, context)
            elif subcommand == "CLEAR":
                return self._handle_clear()
            elif subcommand == "STATUS":
                return self._handle_status()
            else:
                return f"❌ Unknown ASSISTANT subcommand: {subcommand}\n\nUse: ASSISTANT ASK, CLEAR, or STATUS"

        elif command == "OK":
            # Legacy OK command support
            if not params:
                return self._handle_help(deprecation_notice)

            subcommand = params[0].upper()
            sub_params = params[1:] if len(params) > 1 else []

            if subcommand == "ASK":
                return deprecation_notice + self._handle_ask(sub_params, context)
            else:
                return f"❌ Unknown OK subcommand: {subcommand}\n\nUse: OK ASK (deprecated - use GENERATE DO)"

        return f"❌ Unknown command: {command}"

    def _handle_help(self, deprecation_notice: str = "") -> str:
        """Display ASSISTANT command help."""
        return f"""{deprecation_notice}🤖 ASSISTANT Commands (Deprecated)

⚠️  These commands will be removed in v2.0.0
    Use GENERATE commands instead

Usage:
  ASSISTANT ASK <question>    - Ask Gemini AI (use GENERATE DO)
  ASSISTANT CLEAR             - Clear conversation history
  ASSISTANT STATUS            - Show status and usage

Examples:
  ASSISTANT ASK how do I purify water?
  → Use instead: GENERATE DO how do I purify water?

  ASSISTANT ASK what's the best shelter?
  → Use instead: GENERATE DO what's the best shelter?

Migration:
  See: wiki/Migration-Guide-Assistant-to-Generate.md
"""

    def _handle_ask(self, params: list, context: Optional[dict] = None) -> str:
        """
        Ask Gemini AI a question.

        Args:
            params: Question words
            context: Optional context dict

        Returns:
            AI response or error message
        """
        if not params:
            return "❌ Usage: ASSISTANT ASK <question>\n\nExample: ASSISTANT ASK how do I purify water?"

        # Check if service is available
        if not self.gemini.is_available:
            error = self.gemini.error_message
            return f"""❌ Gemini service not available: {error}

💡 Setup Instructions:
1. Get API key from: https://makersuite.google.com/app/apikey
2. Add to .env: GEMINI_API_KEY=your_key_here
3. Test with: ASSISTANT STATUS

💡 Offline Alternative:
   uDOS works fully offline without Gemini.
   Use GENERATE DO for offline-first AI using knowledge bank.
"""

        question = " ".join(params)

        # Build context for Gemini
        gemini_context = context or {}

        # Call Gemini service
        try:
            response = self.gemini.ask(question, context=gemini_context)

            # Add context note if knowledge bank results were included
            kb_note = ""
            if gemini_context.get('local_knowledge', {}).get('results'):
                kb_count = len(gemini_context['local_knowledge']['results'])
                kb_note = f"\n\n📚 Enhanced with {kb_count} knowledge bank items"

            return f"🤖 Gemini AI:{kb_note}\n\n{response}"

        except Exception as e:
            return f"❌ Error: {str(e)}\n\nTry GENERATE DO for offline-first alternative."

    def _handle_clear(self) -> str:
        """Clear conversation history."""
        if not self.gemini.is_available:
            return "❌ Gemini service not available"

        try:
            self.gemini.clear_history()
            return "✅ Conversation history cleared"
        except Exception as e:
            return f"❌ Error clearing history: {str(e)}"

    def _handle_status(self) -> str:
        """Show assistant status and usage statistics."""
        status = self.gemini.get_status()

        if not status['available']:
            return f"""❌ Gemini Assistant - Not Available

Error: {status['error']}

💡 Setup Instructions:
1. Get API key: https://makersuite.google.com/app/apikey
2. Add to .env: GEMINI_API_KEY=your_key_here
3. Test with: ASSISTANT STATUS

💡 Offline Alternative:
   Use GENERATE DO for offline-first AI
   No API key required!
"""

        # Format uptime
        uptime_hours = status['uptime_seconds'] / 3600
        uptime_str = f"{uptime_hours:.1f}h" if uptime_hours >= 1 else f"{status['uptime_seconds']:.0f}s"

        # Cost per request
        cost_per_request = status['total_cost_usd'] / status['total_requests'] if status['total_requests'] > 0 else 0

        return f"""✅ Gemini Assistant - Active

Model: {status['model']}
Uptime: {uptime_str}

Usage Statistics:
  Total Requests: {status['total_requests']}
  Input Tokens: {status['total_input_tokens']:,}
  Output Tokens: {status['total_output_tokens']:,}
  Total Cost: ${status['total_cost_usd']:.4f}
  Cost per Request: ${cost_per_request:.4f}

Conversation:
  History Size: {status['conversation_history_size']} messages

⚠️  Deprecation Notice:
    ASSISTANT commands will be removed in v2.0.0
    Use GENERATE commands instead (offline-first)

Migration: wiki/Migration-Guide-Assistant-to-Generate.md
"""


# Factory function for easy import
def get_assistant_handler(config_manager=None) -> AssistantHandler:
    """
    Get AssistantHandler instance.

    Args:
        config_manager: Optional ConfigManager instance

    Returns:
        AssistantHandler instance
    """
    return AssistantHandler(config_manager=config_manager)
