"""
OK Command Handler - AI-Assisted Workflow Generation
Handles OK MAKE commands for workflow, SVG, documentation, and test generation

Commands:
- OK MAKE WORKFLOW <description> - Generate uPY workflow script
- OK MAKE SVG <description> - Generate SVG graphic
- OK MAKE DOC <topic> - Generate documentation
- OK MAKE TEST <file> - Generate unit tests
- OK MAKE MISSION <category> <tile> - Generate mission script
- OK ASK <question> - Ask AI assistant
- OK CLEAR - Clear conversation history
- OK STATUS - Show usage statistics

Integration:
- Uses Gemini service from extensions/assistant
- Context-aware via ok_context_manager
- Prompt augmentation via context_builder
- Settings via ok_config

Version: 1.0.0 (v1.2.21)
Author: Fred Porter
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base_handler import BaseCommandHandler
from core.services.ok_context_manager import get_ok_context_manager
from core.services.ok_config import get_ok_config
from extensions.assistant.context_builder import get_context_builder


class OKHandler(BaseCommandHandler):
    """OK command handler for AI-assisted generation"""

    def __init__(self, **kwargs):
        """
        Initialize OK handler.

        Args:
            **kwargs: Standard handler dependencies
        """
        super().__init__(**kwargs)

        # Context and configuration
        self.context_manager = get_ok_context_manager()
        self.context_builder = get_context_builder()
        self.ok_config = get_ok_config()

        # Gemini service (lazy load)
        self._gemini = None

        # Output directories
        self.output_dirs = {
            'workflow': Path('memory/workflows/missions'),
            'svg': Path('memory/drafts/svg'),
            'doc': Path('memory/docs'),
            'test': Path('memory/ucode/tests'),
            'mission': Path('memory/workflows/missions')
        }

        # Ensure directories exist
        for dir_path in self.output_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            'total_requests': 0,
            'by_command': {},
            'total_tokens': 0,
            'session_start': datetime.now()
        }

    @property
    def gemini(self):
        """Lazy load Gemini service."""
        if self._gemini is None:
            try:
                from extensions.assistant.gemini_service import GeminiService
                from core.config import Config
                config = Config()
                self._gemini = GeminiService(config_manager=config)
            except Exception as e:
                # Gemini not available
                return None
        return self._gemini

    def handle(self, command: str, params: List[str], grid=None) -> str:
        """
        Handle OK commands.

        Args:
            command: Command name (OK)
            params: Command parameters
            grid: Optional grid instance

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        subcommand = params[0].upper()

        # Route to subcommand handlers
        if subcommand == "MAKE":
            return self._handle_make(params[1:])
        elif subcommand == "ASK":
            return self._handle_ask(params[1:])
        elif subcommand == "CLEAR":
            return self._handle_clear()
        elif subcommand == "STATUS":
            return self._handle_status()
        else:
            return f"❌ Unknown OK command: {subcommand}\n\nUse: OK --help"

    def _handle_make(self, params: List[str]) -> str:
        """Handle OK MAKE subcommands."""
        if not params:
            return (
                "OK MAKE - AI-Assisted Generation\n\n"
                "Commands:\n"
                "  OK MAKE WORKFLOW <description> - Generate uPY workflow\n"
                "  OK MAKE SVG <description>      - Generate SVG graphic\n"
                "  OK MAKE DOC <topic>             - Generate documentation\n"
                "  OK MAKE TEST <file>             - Generate unit tests\n"
                "  OK MAKE MISSION <cat> <tile>    - Generate mission script\n\n"
                "Examples:\n"
                "  OK MAKE WORKFLOW \"water purification checklist\"\n"
                "  OK MAKE SVG \"water filter diagram\"\n"
                "  OK MAKE DOC \"grid system overview\"\n"
                "  OK MAKE TEST core/services/ok_config.py\n"
            )

        make_type = params[0].upper()
        make_params = params[1:]

        if make_type == "WORKFLOW":
            return self._make_workflow(make_params)
        elif make_type == "SVG":
            return self._make_svg(make_params)
        elif make_type == "DOC":
            return self._make_doc(make_params)
        elif make_type == "TEST":
            return self._make_test(make_params)
        elif make_type == "MISSION":
            return self._make_mission(make_params)
        else:
            return f"❌ Unknown MAKE type: {make_type}\n\nUse: OK MAKE --help"

    def _make_workflow(self, params: List[str]) -> str:
        """Generate uPY workflow script."""
        if not params:
            return "❌ Usage: OK MAKE WORKFLOW <description>"

        description = ' '.join(params)

        # Check Gemini availability
        if not self.gemini or not self.gemini.is_available:
            return "❌ Gemini API not available. Set GEMINI_API_KEY in .env"

        # Build context-aware prompt
        prompt = self.context_builder.build_workflow_prompt("automation", description)

        # Generate with Gemini
        try:
            response = self.gemini.ask(prompt)

            if response.get('success'):
                # Extract code from response
                code = self._extract_code(response['response'])

                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"workflow_{timestamp}.upy"
                filepath = self.output_dirs['workflow'] / filename

                with open(filepath, 'w') as f:
                    f.write(code)

                # Update stats
                self._update_stats('workflow', response.get('tokens_used', 0))

                return (
                    f"✅ Workflow generated: {filepath}\n\n"
                    f"Preview:\n{code[:200]}...\n\n"
                    f"Run with: RUN {filepath}"
                )
            else:
                return f"❌ Generation failed: {response.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error: {e}"

    def _make_svg(self, params: List[str]) -> str:
        """Generate SVG graphic."""
        if not params:
            return "❌ Usage: OK MAKE SVG <description>"

        description = ' '.join(params)

        if not self.gemini or not self.gemini.is_available:
            return "❌ Gemini API not available. Set GEMINI_API_KEY in .env"

        # Build SVG-specific prompt
        prompt = self.context_builder.build_svg_prompt(description)

        try:
            response = self.gemini.ask(prompt)

            if response.get('success'):
                svg_code = self._extract_code(response['response'])

                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"graphic_{timestamp}.svg"
                filepath = self.output_dirs['svg'] / filename

                with open(filepath, 'w') as f:
                    f.write(svg_code)

                self._update_stats('svg', response.get('tokens_used', 0))

                return (
                    f"✅ SVG generated: {filepath}\n\n"
                    f"Size: {len(svg_code)} bytes\n"
                    f"Preview in browser or: SHOW {filepath}"
                )
            else:
                return f"❌ Generation failed: {response.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error: {e}"

    def _make_doc(self, params: List[str]) -> str:
        """Generate documentation."""
        if not params:
            return "❌ Usage: OK MAKE DOC <topic>"

        topic = ' '.join(params)

        if not self.gemini or not self.gemini.is_available:
            return "❌ Gemini API not available. Set GEMINI_API_KEY in .env"

        prompt = self.context_builder.build_doc_prompt(topic)

        try:
            response = self.gemini.ask(prompt)

            if response.get('success'):
                doc_content = response['response']

                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_topic = topic.replace(' ', '_')[:30]
                filename = f"{safe_topic}_{timestamp}.md"
                filepath = self.output_dirs['doc'] / filename

                with open(filepath, 'w') as f:
                    f.write(doc_content)

                self._update_stats('doc', response.get('tokens_used', 0))

                return (
                    f"✅ Documentation generated: {filepath}\n\n"
                    f"Length: {len(doc_content)} characters\n"
                    f"View with: SHOW {filepath}"
                )
            else:
                return f"❌ Generation failed: {response.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error: {e}"

    def _make_test(self, params: List[str]) -> str:
        """Generate unit tests."""
        if not params:
            return "❌ Usage: OK MAKE TEST <file_path>"

        file_path = params[0]

        if not self.gemini or not self.gemini.is_available:
            return "❌ Gemini API not available. Set GEMINI_API_KEY in .env"

        prompt = self.context_builder.build_test_prompt(file_path)

        try:
            response = self.gemini.ask(prompt)

            if response.get('success'):
                test_code = self._extract_code(response['response'])

                # Save to file
                base_name = Path(file_path).stem
                filename = f"test_{base_name}.py"
                filepath = self.output_dirs['test'] / filename

                with open(filepath, 'w') as f:
                    f.write(test_code)

                self._update_stats('test', response.get('tokens_used', 0))

                return (
                    f"✅ Tests generated: {filepath}\n\n"
                    f"Run with: pytest {filepath}"
                )
            else:
                return f"❌ Generation failed: {response.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error: {e}"

    def _make_mission(self, params: List[str]) -> str:
        """Generate mission script."""
        if len(params) < 2:
            return "❌ Usage: OK MAKE MISSION <category> <tile>"

        category = params[0]
        tile = params[1]

        if not self.gemini or not self.gemini.is_available:
            return "❌ Gemini API not available. Set GEMINI_API_KEY in .env"

        prompt = f"Generate a uPY mission script for category '{category}' at TILE {tile}"

        try:
            response = self.gemini.ask(prompt)

            if response.get('success'):
                mission_code = self._extract_code(response['response'])

                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"mission_{category}_{tile}_{timestamp}.upy"
                filepath = self.output_dirs['mission'] / filename

                with open(filepath, 'w') as f:
                    f.write(mission_code)

                self._update_stats('mission', response.get('tokens_used', 0))

                return (
                    f"✅ Mission generated: {filepath}\n\n"
                    f"Run with: RUN {filepath}"
                )
            else:
                return f"❌ Generation failed: {response.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error: {e}"

    def _handle_ask(self, params: List[str]) -> str:
        """Handle OK ASK command."""
        if not params:
            return "❌ Usage: OK ASK <question>"

        question = ' '.join(params)

        if not self.gemini or not self.gemini.is_available:
            return "❌ Gemini API not available. Set GEMINI_API_KEY in .env"

        # Build context-aware prompt
        prompt = self.context_builder.build_prompt(question, context_type="general")

        try:
            response = self.gemini.ask(prompt)

            if response.get('success'):
                self._update_stats('ask', response.get('tokens_used', 0))
                return response['response']
            else:
                return f"❌ Error: {response.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error: {e}"

    def _handle_clear(self) -> str:
        """Clear conversation history."""
        if self.gemini and self.gemini.is_available:
            self.gemini.clear_conversation()
            return "✅ Conversation history cleared"
        else:
            return "⚠️  No active conversation to clear"

    def _handle_status(self) -> str:
        """Show OK assistant status."""
        lines = []

        # Gemini status
        if self.gemini and self.gemini.is_available:
            lines.append("🤖 OK Assistant Status: ACTIVE")
            lines.append("")
            lines.append(f"Model: {self.ok_config.get('model')}")
            lines.append(f"Temperature: {self.ok_config.get('temperature')}")
            lines.append(f"Max Tokens: {self.ok_config.get('max_tokens'):,}")
        else:
            lines.append("🤖 OK Assistant Status: INACTIVE")
            lines.append("")
            lines.append("⚠️  Gemini API not available")
            lines.append("Set GEMINI_API_KEY in .env to enable")
            return '\n'.join(lines)

        # Session statistics
        lines.append("")
        lines.append("📊 Session Statistics:")
        lines.append(f"Total Requests: {self.stats['total_requests']}")
        lines.append(f"Total Tokens: {self.stats['total_tokens']:,}")

        if self.stats['by_command']:
            lines.append("")
            lines.append("By Command:")
            for cmd, count in self.stats['by_command'].items():
                lines.append(f"  {cmd}: {count}")

        # Context status
        context = self.context_manager.get_context()
        if context['workspace']['tile_location']:
            lines.append("")
            lines.append(f"📍 Location: {context['workspace']['tile_location']}")

        return '\n'.join(lines)

    def _extract_code(self, response: str) -> str:
        """Extract code block from response."""
        # Look for code blocks
        if '```' in response:
            parts = response.split('```')
            if len(parts) >= 3:
                # Get code between first ```
                code = parts[1]
                # Remove language identifier if present
                if '\n' in code:
                    lines = code.split('\n')
                    if lines[0].strip() in ['python', 'upy', 'svg', 'xml']:
                        code = '\n'.join(lines[1:])
                return code.strip()

        # No code blocks - return full response
        return response.strip()

    def _update_stats(self, command: str, tokens: int) -> None:
        """Update usage statistics."""
        self.stats['total_requests'] += 1
        self.stats['total_tokens'] += tokens
        self.stats['by_command'][command] = self.stats['by_command'].get(command, 0) + 1

        # Update context manager
        self.context_manager.add_command(f"OK MAKE {command.upper()}", "success")

    def _show_help(self) -> str:
        """Show OK command help."""
        return (
            "╔══════════════════════════════════════════════════════════╗\n"
            "║               OK Assistant - AI Workflows                ║\n"
            "╚══════════════════════════════════════════════════════════╝\n\n"
            "Commands:\n"
            "  OK MAKE WORKFLOW <desc>  - Generate uPY workflow script\n"
            "  OK MAKE SVG <desc>       - Generate SVG graphic\n"
            "  OK MAKE DOC <topic>      - Generate documentation\n"
            "  OK MAKE TEST <file>      - Generate unit tests\n"
            "  OK MAKE MISSION <cat> <tile> - Generate mission script\n\n"
            "  OK ASK <question>        - Ask AI assistant\n"
            "  OK CLEAR                 - Clear conversation history\n"
            "  OK STATUS                - Show usage statistics\n\n"
            "Examples:\n"
            "  OK MAKE WORKFLOW \"water purification checklist\"\n"
            "  OK MAKE SVG \"water filter diagram\"\n"
            "  OK MAKE DOC \"grid system overview\"\n"
            "  OK ASK \"How do I use the TILE system?\"\n\n"
            "TUI:\n"
            "  Press O-key to open OK assistant panel\n\n"
            "Configuration:\n"
            "  Set GEMINI_API_KEY in .env\n"
            "  Configure via: CONFIG (C-key) → [OK] tab\n"
        )


# Factory function for handler creation
def create_ok_handler(**kwargs) -> OKHandler:
    """
    Create OK handler instance.

    Args:
        **kwargs: Handler dependencies

    Returns:
        OKHandler instance
    """
    return OKHandler(**kwargs)
