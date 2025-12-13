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
from core.utils.filename_generator import FilenameGenerator


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
        
        # v1.2.23: FilenameGenerator for AI-generated content
        config = kwargs.get('config')
        self.filename_gen = FilenameGenerator(config=config)

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
        """Lazy load Gemini service with first-time setup."""
        if self._gemini is None:
            try:
                from extensions.assistant.gemini_service import GeminiService
                from core.config import Config
                config = Config()
                
                # Check if API key is set (v1.3 - first-time setup)
                api_key = config.get_env('GEMINI_API_KEY', '')
                if not api_key:
                    # Prompt for setup on first use
                    return self._prompt_gemini_setup(config)
                
                self._gemini = GeminiService(config_manager=config)
            except ImportError:
                # Cloud extension not installed
                return None
            except Exception as e:
                # Other Gemini initialization error
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
        elif subcommand == "FIX":
            return self._handle_fix(params[1:])
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
                "Workflows:\n"
                "  OK MAKE WORKFLOW <desc>   - Generate uPY workflow script\n"
                "  OK MAKE MISSION <cat> <tile> - Generate mission script\n"
                "  OK MAKE TEST <file>       - Generate unit tests\n"
                "  OK MAKE DOC <topic>       - Generate documentation\n\n"
                "Graphics (Typora/GitHub standards):\n"
                "  OK MAKE SEQUENCE <desc>   - js-sequence diagram (interactions)\n"
                "  OK MAKE FLOWCHART <desc>  - flowchart.js diagram (processes)\n"
                "  OK MAKE SVG <desc>        - Custom vector graphics\n"
                "  OK MAKE ASCII <desc>      - Text-based art\n"
                "  OK MAKE TELETEXT <desc>   - Retro terminal graphics\n\n"
                "Examples:\n"
                "  OK MAKE SEQUENCE \"user login process\"\n"
                "  OK MAKE FLOWCHART \"water purification steps\"\n"
                "  OK MAKE SVG \"water filter components\"\n"
                "  OK MAKE TEST core/services/ok_config.py\n"
            )

        make_type = params[0].upper()
        make_params = params[1:]

        if make_type == "WORKFLOW":
            return self._make_workflow(make_params)
        elif make_type == "SEQUENCE":
            return self._make_diagram(make_params, "sequence")
        elif make_type == "FLOWCHART" or make_type == "FLOW":
            return self._make_diagram(make_params, "flowchart")
        elif make_type == "SVG":
            return self._make_svg(make_params)
        elif make_type == "ASCII":
            return self._make_diagram(make_params, "ascii")
        elif make_type == "TELETEXT":
            return self._make_diagram(make_params, "teletext")
        elif make_type == "DOC":
            return self._make_doc(make_params)
        elif make_type == "TEST":
            return self._make_test(make_params)
        elif make_type == "MISSION":
            return self._make_mission(make_params)
        else:
            return f"❌ Unknown MAKE type: {make_type}\n\nSupported: SEQUENCE, FLOWCHART, SVG, ASCII, TELETEXT, WORKFLOW, DOC, TEST, MISSION"

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

    def _make_diagram(self, params: List[str], diagram_type: str) -> str:
        """Generate Typora-compatible diagram code (sequence/flowchart/ascii/teletext)."""
        if not params:
            type_examples = {
                'sequence': 'Alice->Bob: Hello Bob!',
                'flowchart': 'st=>start: Start\\nop=>operation: Process',
                'ascii': 'water filtration system',
                'teletext': 'survival guide header'
            }
            example = type_examples.get(diagram_type, 'description')
            return f"❌ Usage: OK MAKE {diagram_type.upper()} <description>\n\nExample: OK MAKE {diagram_type.upper()} \"{example}\""

        description = ' '.join(params)

        if not self.gemini or not self.gemini.is_available:
            return "❌ Gemini API not available. Set GEMINI_API_KEY in .env"

        # Build diagram-specific prompt
        prompt = self._build_diagram_prompt(description, diagram_type)

        try:
            response = self.gemini.ask(prompt)

            if response.get('success'):
                diagram_code = self._extract_code(response['response'])

                # Save to appropriate directory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{diagram_type}_{timestamp}.md"
                
                # Determine output directory
                if diagram_type in ['sequence', 'flowchart']:
                    output_dir = Path("memory/drafts/diagrams")
                elif diagram_type == 'ascii':
                    output_dir = Path("memory/drafts/ascii")
                elif diagram_type == 'teletext':
                    output_dir = Path("memory/drafts/teletext")
                else:
                    output_dir = Path("memory/drafts")
                
                output_dir.mkdir(parents=True, exist_ok=True)
                filepath = output_dir / filename

                # Wrap in Typora/GitHub markdown fence
                if diagram_type in ['sequence', 'flowchart']:
                    fence_type = 'sequence' if diagram_type == 'sequence' else 'flow'
                    wrapped_code = f"```{fence_type}\n{diagram_code}\n```\n"
                else:
                    wrapped_code = diagram_code

                with open(filepath, 'w') as f:
                    f.write(wrapped_code)

                self._update_stats(diagram_type, response.get('tokens_used', 0))

                return (
                    f"✅ {diagram_type.upper()} diagram generated: {filepath}\n\n"
                    f"Format: Typora/GitHub compatible\n"
                    f"Preview:\n{diagram_code[:150]}...\n\n"
                    f"View with: SHOW {filepath}"
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

    def _handle_fix(self, params: List[str]) -> str:
        """Handle OK FIX command - suggest fixes for errors using AI + learned patterns."""
        from core.services.pattern_learner import get_pattern_learner
        from core.services.error_interceptor import get_error_context_manager
        
        learner = get_pattern_learner()
        error_manager = get_error_context_manager()
        
        # Get error context (signature or latest)
        if params and params[0].startswith('#'):
            # Specific error by signature
            signature = params[0][1:]  # Remove # prefix
            error_ctx = error_manager.get_context(signature)
            if not error_ctx:
                return f"❌ Error not found: #{signature}\n\nUse: ERROR HISTORY to see available errors"
        else:
            # Use latest error
            error_ctx = error_manager.get_latest()
            if not error_ctx:
                return "❌ No recent errors found\n\nUse OK FIX after an error occurs"
        
        # Build output
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════╗")
        lines.append("║               OK FIX - Error Analysis                    ║")
        lines.append("╚══════════════════════════════════════════════════════════╝")
        lines.append("")
        
        # Show error summary
        lines.append(f"🔍 Error: {error_ctx['error_type']}")
        lines.append(f"   Message: {error_ctx['message']}")
        lines.append(f"   Signature: #{error_ctx['signature']}")
        lines.append(f"   Timestamp: {error_ctx['timestamp']}")
        lines.append("")
        
        # Get learned patterns
        suggestions = learner.suggest_fix(
            error_ctx['error_type'],
            error_ctx['message'],
            error_ctx.get('stack_trace', '')
        )
        
        if suggestions:
            lines.append("📚 Learned Fixes (from previous occurrences):")
            for i, sugg in enumerate(suggestions[:3], 1):  # Top 3
                success_rate = sugg.get('success_rate', 0)
                if success_rate > 0:
                    lines.append(f"   {i}. {sugg['fix']} (✅ {success_rate:.0%} success rate)")
                else:
                    lines.append(f"   {i}. {sugg['fix']}")
            lines.append("")
        
        # Get AI analysis (if available)
        if self.gemini and self.gemini.is_available:
            lines.append("🤖 AI Analysis (via Gemini)...")
            lines.append("")
            
            try:
                # Build error analysis prompt
                prompt = self._build_error_analysis_prompt(error_ctx, suggestions)
                
                # Query Gemini
                response = self.gemini.ask(prompt)
                
                if response.get('success'):
                    lines.append(response['response'])
                    self._update_stats('fix', response.get('tokens_used', 0))
                else:
                    lines.append(f"⚠️  AI analysis failed: {response.get('error', 'Unknown error')}")
            
            except Exception as e:
                lines.append(f"⚠️  AI analysis error: {e}")
        else:
            lines.append("ℹ️  AI analysis unavailable (set GEMINI_API_KEY in .env)")
        
        lines.append("")
        lines.append("Next Steps:")
        lines.append("  • Try suggested fix and use: OK FIX WORKED (or FAILED)")
        lines.append("  • View full error: ERROR SHOW #{signature}")
        lines.append("  • Enter debug mode: DEV MODE")
        
        return '\n'.join(lines)
    
    def _build_error_analysis_prompt(self, error_ctx: Dict[str, Any], learned_suggestions: List[Dict]) -> str:
        """Build prompt for Gemini error analysis."""
        prompt_parts = []
        
        prompt_parts.append("You are an expert debugging assistant for uDOS (an offline-first terminal OS).")
        prompt_parts.append("")
        prompt_parts.append("Analyze this error and provide:")
        prompt_parts.append("1. Root cause analysis")
        prompt_parts.append("2. Step-by-step fix instructions")
        prompt_parts.append("3. Prevention tips")
        prompt_parts.append("")
        prompt_parts.append(f"ERROR TYPE: {error_ctx['error_type']}")
        prompt_parts.append(f"MESSAGE: {error_ctx['message']}")
        
        if error_ctx.get('command'):
            prompt_parts.append(f"COMMAND: {error_ctx['command']}")
        
        if error_ctx.get('stack_trace'):
            # Truncate stack trace to avoid token limits
            stack = error_ctx['stack_trace'][:1000]
            prompt_parts.append("")
            prompt_parts.append("STACK TRACE:")
            prompt_parts.append(stack)
        
        if learned_suggestions:
            prompt_parts.append("")
            prompt_parts.append("PREVIOUSLY SUCCESSFUL FIXES:")
            for sugg in learned_suggestions[:3]:
                success_rate = sugg.get('success_rate', 0)
                prompt_parts.append(f"  • {sugg['fix']} ({success_rate:.0%} success rate)")
        
        prompt_parts.append("")
        prompt_parts.append("Provide concise, actionable advice (max 200 words).")
        
        return '\n'.join(prompt_parts)

    def _build_diagram_prompt(self, description: str, diagram_type: str) -> str:
        """Build AI prompt for diagram generation."""
        type_specs = {
            'sequence': {
                'format': 'js-sequence-diagrams syntax',
                'example': 'Alice->Bob: Hello\\nNote right of Bob: Bob thinks\\nBob-->Alice: Hi!',
                'rules': [
                    'Use -> for solid lines, --> for dashed lines',
                    'Format: Actor->Actor: Message',
                    'Use "Note left/right of Actor: text" for notes',
                    'Use "Title: text" for diagram title'
                ]
            },
            'flowchart': {
                'format': 'flowchart.js syntax',
                'example': 'st=>start: Start\\nop=>operation: Process\\ne=>end\\nst->op->e',
                'rules': [
                    'Define nodes: id=>type: label',
                    'Types: start, end, operation, condition, inputoutput, subroutine',
                    'Connect with arrows: node1->node2',
                    'Conditions: cond(yes)->node1, cond(no)->node2'
                ]
            },
            'ascii': {
                'format': 'ASCII art',
                'example': '+---+\\n| A |\\n+---+',
                'rules': [
                    'Use box drawing: + - | for borders',
                    'Use arrows: -> <- => <= for connections',
                    'Keep it simple and readable in monospace'
                ]
            },
            'teletext': {
                'format': 'Teletext/ANSI art',
                'example': '█▀▀▀█\\n█   █\\n█▄▄▄█',
                'rules': [
                    'Use block chars: █ ▀ ▄ ░ ▒ ▓',
                    'Create retro terminal aesthetic',
                    'Use simple geometric shapes'
                ]
            }
        }

        spec = type_specs.get(diagram_type, type_specs['sequence'])

        prompt = f"""Generate a {diagram_type} diagram for: {description}

OUTPUT FORMAT: {spec['format']}

EXAMPLE:
{spec['example']}

RULES:
"""
        for rule in spec['rules']:
            prompt += f"  • {rule}\n"

        prompt += f"""
REQUIREMENTS:
  • Output ONLY the diagram code (no markdown fences, no explanations)
  • Follow {spec['format']} syntax exactly
  • Keep it concise and clear
  • Test the syntax mentally before outputting

Generate the diagram code now:"""

        return prompt

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

    def _prompt_gemini_setup(self, config) -> Optional[Any]:
        """
        Prompt user for GEMINI_API_KEY setup on first use.
        
        Args:
            config: Config instance
            
        Returns:
            Initialized GeminiService or None if setup failed/skipped
        """
        from pathlib import Path
        
        # Check if cloud extension is installed
        gemini_service_path = Path('extensions/assistant/gemini_service.py')
        if not gemini_service_path.exists():
            print("\n❌ Cloud extension not installed")
            print("OK commands require the AI assistant extension")
            print("\nInstallation:")
            print("  1. Ensure extensions/assistant/ directory exists")
            print("  2. Install dependencies: pip install google-generativeai")
            print("  3. Restart uDOS")
            return None
        
        print("\n💡 First-time OK Assistant setup")
        print("GEMINI_API_KEY required for AI-powered features")
        print("Get API key: https://makersuite.google.com/app/apikey")
        print("\nFeatures enabled:")
        print("  • OK MAKE WORKFLOW/SVG/DOC/TEST/MISSION")
        print("  • OK ASK <question>")
        print("  • OK FIX (AI error analysis)")
        
        try:
            api_key = input("\nEnter Gemini API Key (starts with AIza...): ").strip()
            
            if not api_key:
                print("⚠️  Setup skipped - OK commands will not be available")
                return None
            
            # Validate format
            if not api_key.startswith('AIza'):
                print("❌ Invalid API key format (should start with 'AIza')")
                print("⚠️  Setup skipped - Please try again later")
                return None
            
            # Save to .env
            config.set_env('GEMINI_API_KEY', api_key)
            print("✅ API key saved to .env")
            
            # Initialize GeminiService
            try:
                from extensions.assistant.gemini_service import GeminiService
                self._gemini = GeminiService(config_manager=config)
                print("✅ OK Assistant initialized successfully")
                return self._gemini
            except Exception as e:
                print(f"❌ Failed to initialize Gemini service: {e}")
                print("⚠️  API key saved but service unavailable")
                return None
                
        except KeyboardInterrupt:
            print("\n⚠️  Setup cancelled")
            return None
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return None

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
            "Workflows:\n"
            "  OK MAKE WORKFLOW <desc>  - Generate uPY workflow script\n"
            "  OK MAKE MISSION <cat> <tile> - Generate mission script\n"
            "  OK MAKE TEST <file>      - Generate unit tests\n"
            "  OK MAKE DOC <topic>      - Generate documentation\n\n"
            "Graphics (Typora/GitHub standards):\n"
            "  OK MAKE SEQUENCE <desc>  - js-sequence diagram (interactions)\n"
            "  OK MAKE FLOWCHART <desc> - flowchart.js diagram (processes)\n"
            "  OK MAKE SVG <desc>       - Custom vector graphics\n"
            "  OK MAKE ASCII <desc>     - Text-based art\n"
            "  OK MAKE TELETEXT <desc>  - Retro terminal graphics\n\n"
            "Assistant:\n"
            "  OK ASK <question>        - Ask AI assistant\n"
            "  OK FIX [#signature]      - Analyze error and suggest fixes\n"
            "  OK CLEAR                 - Clear conversation history\n"
            "  OK STATUS                - Show usage statistics\n\n"
            "Examples:\n"
            "  OK MAKE SEQUENCE \"user login process\"\n"
            "  OK MAKE FLOWCHART \"water purification steps\"\n"
            "  OK MAKE SVG \"fire triangle diagram\"\n"
            "  OK ASK \"How do I use the TILE system?\"\n"
            "  OK FIX                   - Fix latest error\n\n"
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
