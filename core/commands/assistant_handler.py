"""
uDOS v1.0.0 - Assistant Command Handler

Handles all assistant-related commands (formerly AI commands):
- ASK: Ask the assistant a question
- ANALYZE: Analyze panel content
- EXPLAIN: Explain a command
- GENERATE: Generate script from description
- DEBUG: Help debug an error
- CLEAR: Clear conversation history

Version: 1.0.0
"""

from .base_handler import BaseCommandHandler


class AssistantCommandHandler(BaseCommandHandler):
    """Handles assistant (Gemini-powered) commands."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini = None  # Lazy initialization
        self._workspace_manager = None

    @property
    def workspace_manager(self):
        """Lazy load workspace manager."""
        if self._workspace_manager is None:
            from core.uDOS_files import WorkspaceManager
            self._workspace_manager = WorkspaceManager()
        return self._workspace_manager

    def _initialize_gemini(self):
        """Initialize Gemini service on first use."""
        if self.gemini is None:
            try:
                from core.uDOS_gemini import get_gemini
                self.gemini = get_gemini()
            except Exception as e:
                return f"⚠️  Failed to initialize assistant: {str(e)}"
        return None

    def handle(self, command, params, grid):
        """
        Route assistant commands to appropriate handlers.

        Args:
            command: Command name (ASK, ANALYZE, etc.)
            params: Command parameters
            grid: Grid instance

        Returns:
            Command result message
        """
        # Initialize Gemini on first use
        init_error = self._initialize_gemini()
        if init_error:
            return init_error

        if command == "ASK":
            return self._handle_ask(params, grid)
        elif command == "ANALYZE":
            return self._handle_analyze(params, grid)
        elif command == "EXPLAIN":
            return self._handle_explain(params)
        elif command == "GENERATE":
            return self._handle_generate(params)
        elif command == "DEBUG":
            return self._handle_debug(params)
        elif command == "CLEAR":
            return self._handle_clear()
        else:
            return self.get_message("ERROR_UNKNOWN_ASSISTANT_COMMAND", command=command)

    def _handle_ask(self, params, grid):
        """
        Ask the assistant a question.

        Args:
            params: [question, optional_panel]
        """
        if not params:
            return "❌ Usage: ASK <question> [panel]\n\nExample: ASK What is uDOS?"

        question = params[0]
        panel_name = params[1] if len(params) > 1 else None

        # Build context
        context = {
            'workspace': self.workspace_manager.current_workspace if self.workspace_manager else 'sandbox',
            'files': []
        }

        # Add panel content if specified
        if panel_name:
            panel_content = grid.get_panel(panel_name)
            if panel_content is None:
                return f"❌ Panel '{panel_name}' not found"
            context['panel'] = {
                'name': panel_name,
                'content': panel_content
            }

        try:
            response = self.gemini.ask(question, context=context)
            return f"🤖 Assistant:\n\n{response}"
        except Exception as e:
            return f"⚠️  Assistant error: {str(e)}\n\nPlease check your connection and API key."

    def _handle_analyze(self, params, grid):
        """
        Analyze panel content.

        Args:
            params: [panel_name]
        """
        if not params:
            return "❌ Usage: ANALYZE <panel>\n\nExample: ANALYZE docs"

        panel_name = params[0]
        panel_content = grid.get_panel(panel_name)
        if panel_content is None:
            return f"❌ Panel '{panel_name}' not found"

        try:
            response = self.gemini.analyze(panel_content)
            return f"📊 Analysis:\n\n{response}"
        except Exception as e:
            return f"⚠️  Analysis failed: {str(e)}"

    def _handle_explain(self, params):
        """
        Explain a command.

        Args:
            params: [command, ...]
        """
        if not params:
            return "❌ Usage: EXPLAIN <command>\n\nExample: EXPLAIN TREE"

        cmd = ' '.join(params)
        try:
            response = self.gemini.explain_command(cmd)
            return f"📖 Explanation:\n\n{response}"
        except Exception as e:
            return f"⚠️  Explanation failed: {str(e)}"

    def _handle_generate(self, params):
        """
        Generate script from description.

        Args:
            params: [description, ...]
        """
        if not params:
            return "❌ Usage: GENERATE <description>\n\nExample: GENERATE Create a test script"

        description = ' '.join(params)
        try:
            response = self.gemini.generate_script(description)
            return f"📝 Generated Script:\n\n{response}"
        except Exception as e:
            return f"⚠️  Generation failed: {str(e)}"

    def _handle_debug(self, params):
        """
        Help debug an error.

        Args:
            params: [error_message, ...]
        """
        if not params:
            return "❌ Usage: DEBUG <error>\n\nExample: DEBUG ImportError: module not found"

        error_msg = ' '.join(params)
        try:
            response = self.gemini.debug_error(error_msg)
            return f"🔧 Debug Help:\n\n{response}"
        except Exception as e:
            return f"⚠️  Debug failed: {str(e)}"

    def _handle_clear(self):
        """Clear conversation history."""
        try:
            self.gemini.clear_history()
            return "✅ Assistant conversation history cleared"
        except Exception as e:
            return f"⚠️  Clear failed: {str(e)}"
