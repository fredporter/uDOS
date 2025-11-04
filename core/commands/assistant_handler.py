"""
uDOS v1.0.0 - Assist Command Handler

Handles all assist-related commands:
- ASK: Ask the assist system a question
- READ: Read panel content
- EXPLAIN: Explain a command
- GENERATE: Generate script from description
- DEBUG: Help debug an error
- CLEAR: Clear conversation history

Version: 1.0.0
"""

from .base_handler import BaseCommandHandler


class AssistantCommandHandler(BaseCommandHandler):
    """Handles OK Assisted Task (Gemini-powered) commands with knowledge integration."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini = None  # Lazy initialization
        self._workspace_manager = None
        self._knowledge_manager = None

    @property
    def workspace_manager(self):
        """Lazy load workspace manager."""
        if self._workspace_manager is None:
            from core.uDOS_files import WorkspaceManager
            self._workspace_manager = WorkspaceManager()
        return self._workspace_manager

    @property
    def knowledge_manager(self):
        """Lazy load knowledge manager."""
        if self._knowledge_manager is None:
            from core.services.knowledge_manager import get_knowledge_manager
            self._knowledge_manager = get_knowledge_manager()
        return self._knowledge_manager

    def _initialize_gemini(self):
        """Initialize Gemini service for OK Assisted Task on first use."""
        if self.gemini is None:
            try:
                from core.uDOS_gemini import get_gemini
                self.gemini = get_gemini()
            except Exception as e:
                return f"⚠️  Failed to initialize assist system: {str(e)}"
        return None

    def handle(self, command, params, grid):
        """
        Route assist commands to appropriate handlers.

        Args:
            command: Command name (OK with subcommand, READ, etc.)
            params: Command parameters
            grid: Grid instance

        Returns:
            Command result message
        """
        # Handle OK with subcommands
        if command == "OK":
            if not params:
                return self._handle_ok_help()

            subcommand = params[0].upper()
            sub_params = params[1:] if len(params) > 1 else []

            if subcommand == "ASK":
                # Initialize Gemini for ASK
                init_error = self._initialize_gemini()
                if init_error:
                    return init_error
                return self._handle_ask(sub_params, grid)
            elif subcommand == "DEV":
                return self._handle_dev(sub_params)
            else:
                return f"❌ Unknown OK subcommand: {subcommand}\n\nUse: OK ASK or OK DEV"

        # Legacy direct commands (for backward compatibility)
        elif command == "ASK":
            init_error = self._initialize_gemini()
            if init_error:
                return init_error
            return self._handle_ask(params, grid)
        elif command == "READ":
            return self._handle_read(params, grid)
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

    def _handle_ok_help(self):
        """Display OK command help."""
        return """✅ OK Command - AI Assistance

Usage:
  OK ASK <question>     - Ask Gemini AI a question
  OK DEV <task>         - Get GitHub Copilot CLI development help

Examples:
  OK ASK how do I implement UNDO?
  OK ASK what files handle navigation?
  OK DEV create a grid command handler
  OK DEV explain this git error

Available:
  • OK ASK - Gemini-powered general assistance
  • OK DEV - GitHub Copilot CLI for development tasks
"""

    def _handle_ask(self, params, grid):
        """
        Ask the assist system a question with local knowledge integration.

        Args:
            params: [question, optional_panel]
        """
        if not params:
            return "❌ Usage: ASK <question> [panel]\n\nExample: ASK What is uDOS?"

        question = params[0]
        panel_name = params[1] if len(params) > 1 else None

        # Search local knowledge base first
        knowledge_context = self._search_local_knowledge(question)

        # Build context
        context = {
            'workspace': self.workspace_manager.current_workspace if self.workspace_manager else 'sandbox',
            'files': [],
            'local_knowledge': knowledge_context
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
            # If we have local knowledge, provide enhanced context
            if knowledge_context['results']:
                context_note = f"\n\n📚 **Local Knowledge Found** ({len(knowledge_context['results'])} items):\n"
                for result in knowledge_context['results'][:3]:
                    context_note += f"• {result['title']} ({result['category']})\n"

                response = self.gemini.ask(question, context=context)
                return f"✅ OK System{context_note}\n{response}"
            else:
                response = self.gemini.ask(question, context=context)
                return f"✅ OK System:\n\n{response}"
        except Exception as e:
            # Fallback to local knowledge if assist fails
            if knowledge_context['results']:
                fallback_response = self._generate_fallback_response(question, knowledge_context)
                return f"📚 Local Knowledge (OK System unavailable):\n\n{fallback_response}"
            return f"⚠️  OK System error: {str(e)}\n\nPlease check your connection and API key."

    def _handle_read(self, params, grid):
        """
        Read and analyze panel content.

        Args:
            params: [panel_name]
        """
        if not params:
            return "❌ Usage: READ <panel>\n\nExample: READ docs"

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

    def _handle_dev(self, params):
        """
        Handle development tasks using GitHub Copilot CLI.

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

Note: Requires GitHub Copilot CLI (gh copilot)
Install: https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line
"""

        task = " ".join(params)

        # Check if gh copilot is available
        import subprocess
        import shutil

        if not shutil.which('gh'):
            return """❌ GitHub CLI not found

GitHub Copilot CLI requires the GitHub CLI to be installed.

Install GitHub CLI:
  macOS:   brew install gh
  Linux:   See https://github.com/cli/cli#installation
  Windows: See https://github.com/cli/cli#installation

Then install Copilot extension:
  gh extension install github/gh-copilot
"""

        try:
            # Check if copilot extension is installed
            result = subprocess.run(
                ['gh', 'copilot', 'suggest', task],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                if 'not installed' in result.stderr.lower() or 'unknown command' in result.stderr.lower():
                    return """❌ GitHub Copilot CLI extension not found

Install the extension:
  gh extension install github/gh-copilot

Then authenticate:
  gh auth login
"""
                return f"❌ Copilot CLI error:\n{result.stderr}"

            return f"🤖 GitHub Copilot DEV:\n\n{result.stdout}"

        except subprocess.TimeoutExpired:
            return "⚠️  Request timeout. Please try again."
        except FileNotFoundError:
            return "❌ GitHub CLI (gh) not found in PATH"
        except Exception as e:
            return f"⚠️  Error calling Copilot CLI: {str(e)}"

    def _search_local_knowledge(self, question):
        """Search local knowledge base for relevant content."""
        try:
            # Search for relevant knowledge
            results = self.knowledge_manager.search(question, limit=5)

            # Build context from results
            context = {
                'query': question,
                'results': results,
                'content_snippets': []
            }

            # Extract content snippets for context
            for result in results[:3]:  # Top 3 results
                content = self.knowledge_manager.get_content(result['file_path'])
                if content:
                    # Extract a relevant section (first 500 chars)
                    snippet = content[:500] + "..." if len(content) > 500 else content
                    context['content_snippets'].append({
                        'title': result['title'],
                        'content': snippet,
                        'category': result['category']
                    })

            return context

        except Exception as e:
            # Return empty context if knowledge search fails
            return {
                'query': question,
                'results': [],
                'content_snippets': [],
                'error': str(e)
            }

    def _generate_fallback_response(self, question, knowledge_context):
        """Generate a response using only local knowledge when OK Assisted Task is unavailable."""
        if not knowledge_context['results']:
            return "No local knowledge found for this question. Please check your internet connection for OK System support."

        response = []
        response.append(f"Based on local knowledge for '{question}':\n")

        for i, result in enumerate(knowledge_context['results'][:3], 1):
            response.append(f"**{i}. {result['title']}** ({result['category']})")
            response.append(f"📝 {result['word_count']} words")

            # Show snippet
            snippet = result['snippet'].strip()
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            response.append(f"💡 {snippet}\n")

        if len(knowledge_context['results']) > 3:
            response.append(f"... and {len(knowledge_context['results']) - 3} more results.")

        response.append("\n💡 Use `KNOWLEDGE SHOW <title>` to view full content")
        response.append("💡 Use `KNOWLEDGE SEARCH <query>` for more detailed search")

        return "\n".join(response)
