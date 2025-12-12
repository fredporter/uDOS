"""
uDOS v2.0.2 - MAKE Command Handler (Unified Content Generation)

Consolidated generation system with offline-first AI:
- DO: Offline-first Q&A using knowledge bank → Gemini fallback
- REDO: Retry last generation with optional modifications
- GUIDE: Generate knowledge bank guides
- SVG: Generate vector diagrams (Nano Banana)
- ASCII: Generate ASCII art
- TELETEXT: Generate BBC-style teletext graphics
- STATUS: Show generation statistics
- CLEAR: Clear generation history
- VALIDATE: Validate system performance criteria

Architecture:
- Offline Engine (90%+ queries) → Gemini Extension (fallback) → Banana (images)
- Cost tracking, rate limiting, priority queues
- Workflow variable support ($MAKE.*, $PROMPT.*, $API.*)

Version: 2.0.2 (Renamed from GENERATE for clarity)
Author: uDOS Development Team
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import time
import json

from .base_handler import BaseCommandHandler
from core.utils.filename_generator import generate_session
from core.services.api_monitor import get_api_monitor, APIRequest
from core.services.priority_queue import get_priority_queue, Priority as QueuePriority
from core.services.performance_monitor import get_performance_monitor
from core.services.unified_logger import log_performance, log_api, log_error, log_command
from core.utils.paths import PATHS


class MakeHandler(BaseCommandHandler):
    """
    Unified MAKE command handler with offline-first AI.

    Replaces old GENERATE command (renamed for clarity in v2.0.2).
    Consolidates all content generation: guides, diagrams, ASCII art, teletext.
    """

    def __init__(self, **kwargs):
        """
        Initialize unified MAKE handler.

        Args:
            **kwargs: Standard handler dependencies (theme, viewport, logger, etc.)
        """
        super().__init__(**kwargs)

        # Lazy load services
        self._offline_engine = None
        self._gemini_service = None
        self._gemini_generator = None  # For SVG/image generation
        self._vectorizer = None
        self._ascii_generator = None
        self._knowledge_manager = None

        # API monitoring and throttling
        self.api_monitor = get_api_monitor()
        self.priority_queue = get_priority_queue()

        # Performance monitoring (v1.2.1)
        self.performance_monitor = get_performance_monitor()

        # Generation history (for REDO)
        self.generation_history: List[Dict[str, Any]] = []
        self.max_history = 100

        # Session statistics
        self.stats = {
            'total_requests': 0,
            'offline_requests': 0,
            'online_requests': 0,
            'total_cost': 0.0,
            'session_start': datetime.now()
        }

        # Output directories
        self.svg_output = PATHS.MEMORY_DRAFTS_SVG
        self.ascii_output = PATHS.MEMORY_DRAFTS_ASCII
        self.teletext_output = PATHS.MEMORY_DRAFTS_TELETEXT
        self.guide_output = Path("knowledge")  # For GENERATE GUIDE

        # Ensure directories exist
        for dir_path in [self.svg_output, self.ascii_output, self.teletext_output]:
            dir_path.mkdir(parents=True, exist_ok=True)

    # ========== Lazy Loading Properties ==========

    @property
    def offline_engine(self):
        """Lazy load offline AI engine (always available)."""
        if self._offline_engine is None:
            from core.interpreters.offline import OfflineEngine
            self._offline_engine = OfflineEngine()
            if self.logger:
                self.logger.info("Offline AI engine loaded")
        return self._offline_engine

    @property
    def gemini_service(self):
        """Lazy load Gemini service (optional extension)."""
        if self._gemini_service is None:
            try:
                from extensions.assistant.gemini_service import get_gemini_service
                self._gemini_service = get_gemini_service(config_manager=None)
                if self.logger and self._gemini_service.is_available:
                    self.logger.info("Gemini service loaded")
            except ImportError:
                # Extension not available - that's okay
                if self.logger:
                    self.logger.debug("Gemini extension not available (optional)")
        return self._gemini_service

    @property
    def gemini_generator(self):
        """Lazy load Gemini generator for image/SVG generation."""
        if self._gemini_generator is None:
            try:
                from core.services.gemini_generator import GeminiGenerator
                self._gemini_generator = GeminiGenerator()
                if self.logger:
                    self.logger.info("Gemini generator loaded (for images/SVG)")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to load Gemini generator: {e}")
                # Will raise error when trying to use SVG generation
        return self._gemini_generator

    @property
    def knowledge_manager(self):
        """Lazy load knowledge manager."""
        if self._knowledge_manager is None:
            from core.knowledge import get_knowledge_manager
            self._knowledge_manager = get_knowledge_manager()
            if self.logger:
                self.logger.info("Knowledge manager loaded")
        return self._knowledge_manager

    @property
    def vectorizer(self):
        """Lazy load vectorizer service for SVG generation."""
        if self._vectorizer is None:
            try:
                from core.services.vectorizer import get_vectorizer_service
                self._vectorizer = get_vectorizer_service()
                if self.logger:
                    self.logger.info("Vectorizer loaded")
            except ImportError as e:
                if self.logger:
                    self.logger.error(f"Failed to load vectorizer: {e}")
                raise ImportError(
                    "Vectorizer not available. "
                    "Install: brew install potrace OR pip install vtracer"
                ) from e
        return self._vectorizer

    @property
    def ascii_generator(self):
        """Lazy load ASCII generator service."""
        if self._ascii_generator is None:
            try:
                from core.services.ascii_generator import get_ascii_generator
                self._ascii_generator = get_ascii_generator(style="unicode")
                if self.logger:
                    self.logger.info("ASCII generator loaded (Unicode style)")
            except ImportError as e:
                if self.logger:
                    self.logger.error(f"Failed to load ASCII generator: {e}")
                raise ImportError("ASCII generator not available") from e
        return self._ascii_generator

    # ========== Main Command Router ==========

    def handle(self, command: str, params: List[str], grid=None) -> str:
        """
        Handle GENERATE commands with unified routing.

        Args:
            command: Command name (GENERATE)
            params: Command parameters [subcommand, args...]
            grid: Optional grid instance for context

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        subcommand = params[0].upper()
        sub_params = params[1:] if len(params) > 1 else []

        # Route to appropriate handler
        if subcommand == "DO":
            return self._handle_do(sub_params, grid)
        elif subcommand == "REDO":
            return self._handle_redo(sub_params, grid)
        elif subcommand == "GUIDE":
            return self._handle_guide(sub_params)
        elif subcommand in ["SVG", "DIAGRAM"]:
            return self._handle_svg(sub_params)
        elif subcommand == "ASCII":
            return self._handle_ascii(sub_params)
        elif subcommand == "TELETEXT":
            return self._handle_teletext(sub_params)
        elif subcommand == "SEQUENCE":
            return self._handle_sequence(sub_params)
        elif subcommand == "FLOW":
            return self._handle_flow(sub_params)
        elif subcommand == "STATUS":
            return self._handle_status()
        elif subcommand == "VALIDATE":
            return self._handle_validate()
        elif subcommand == "CLEAR":
            return self._handle_clear()
        elif subcommand == "HELP":
            return self._show_help()
        else:
            return f"❌ Unknown GENERATE subcommand: {subcommand}\n\n{self._show_help()}"

    # For backward compatibility with old routing
    def handle_command(self, params: List[str]) -> str:
        """
        Legacy routing method for backward compatibility.

        Args:
            params: Command parameters (same as handle())

        Returns:
            Command result
        """
        return self.handle("GENERATE", params, grid=None)

    # ========== DO Command (Offline-First Q&A) ==========

    def _handle_do(self, params: List[str], grid=None) -> str:
        """
        Handle GENERATE DO - Offline-first Q&A.

        Process:
        1. Try offline engine first (knowledge bank + FAQ)
        2. If confidence < 50%, try Gemini extension
        3. Track usage statistics
        4. Store in generation history

        Args:
            params: Query words
            grid: Optional grid for context

        Returns:
            AI response (offline or online)
        """
        if not params:
            return """❌ Usage: GENERATE DO <question>

Examples:
  GENERATE DO how do I purify water?
  GENERATE DO what's the best shelter for desert?
  GENERATE DO explain grid system

💡 This uses offline-first AI:
   - Searches 166+ survival guides
   - Checks FAQ database (40+ questions)
   - Falls back to Gemini if needed
   - 90%+ queries answered offline!
"""

        query = " ".join(params)
        start_time = time.time()

        # Build context
        context = {
            'workspace': 'memory',  # Default workspace
            'grid': grid
        }

        # Step 1: Try offline engine first
        if self.logger:
            self.logger.debug(f"GENERATE DO: Trying offline engine for '{query}'")

        offline_response = self.offline_engine.generate(query, context)
        duration_ms = (time.time() - start_time) * 1000

        # Check if offline response is sufficient
        if offline_response.confidence >= 0.5:
            # Offline answer good enough
            self.stats['total_requests'] += 1
            self.stats['offline_requests'] += 1

            # Track performance (v1.2.1)
            duration = duration_ms / 1000.0
            self.performance_monitor.track_query(
                query_type='DO',
                mode='offline',
                duration=duration,
                cost=0.0,
                confidence=offline_response.confidence * 100,
                success=True
            )

            # Log to unified logger
            log_performance('DO', duration, offline=True,
                          confidence=offline_response.confidence * 100,
                          method=offline_response.method)

            # Store in history
            self._add_to_history({
                'timestamp': datetime.now().isoformat(),
                'command': 'DO',
                'query': query,
                'method': offline_response.method,
                'confidence': offline_response.confidence,
                'sources': offline_response.sources,
                'duration_ms': duration_ms,
                'cost': 0.0
            })

            # Format response
            confidence_emoji = "✅" if offline_response.confidence >= 0.7 else "⚠️"
            method_label = {
                'faq': 'FAQ',
                'knowledge_bank': 'Knowledge Bank',
                'synthesis': 'Knowledge Synthesis',
                'pattern': 'Pattern Matching'
            }.get(offline_response.method, 'Offline')

            response_parts = [
                f"{confidence_emoji} {method_label} (Offline - No API Cost)",
                f"Confidence: {offline_response.confidence:.0%}",
                "",
                offline_response.content
            ]

            if offline_response.sources:
                response_parts.append("")
                response_parts.append(f"📚 Sources ({len(offline_response.sources)}):")
                for source in offline_response.sources[:3]:  # Top 3
                    response_parts.append(f"  • {source}")

            if offline_response.suggestions:
                response_parts.append("")
                response_parts.append("💡 Related:")
                for suggestion in offline_response.suggestions[:3]:
                    response_parts.append(f"  • {suggestion}")

            return "\n".join(response_parts)

        # Step 2: Offline confidence too low - try Gemini if available
        if self.gemini_service and self.gemini_service.is_available:
            if self.logger:
                self.logger.debug(f"GENERATE DO: Offline confidence {offline_response.confidence:.0%}, trying Gemini")

            # Check rate limit
            rate_check = self.api_monitor.check_rate_limit(priority=APIPriority.HIGH)
            if not rate_check['allowed']:
                return f"""⚠️ Rate Limit Reached (Offline Answer)
Confidence: {offline_response.confidence:.0%}

{offline_response.content}

🚫 Rate Limit: {rate_check['message']}
   Wait {rate_check.get('wait_seconds', 0):.1f}s or use offline answer

💡 Offline answers have no rate limits!
"""

            # Estimate cost and check budget
            estimated_cost = 0.0001  # Typical small query cost (~100 tokens)
            budget_check = self.api_monitor.check_budget(
                estimated_cost=estimated_cost,
                priority=APIPriority.HIGH
            )
            if not budget_check['allowed']:
                return f"""⚠️ Budget Limit Reached (Offline Answer)
Confidence: {offline_response.confidence:.0%}

{offline_response.content}

🚫 Budget: {budget_check['message']}
   Daily usage: ${budget_check.get('daily_cost', 0):.4f} / ${budget_check.get('daily_budget', 1.0):.2f}

💡 Offline answers are free!
"""

            try:
                # Add offline results to context for Gemini
                gemini_context = {
                    **context,
                    'local_knowledge': {
                        'results': [],  # Could enhance with offline results
                        'confidence': offline_response.confidence,
                        'method': offline_response.method
                    }
                }

                gemini_start = time.time()
                gemini_response = self.gemini_service.ask(query, context=gemini_context)
                gemini_duration = (time.time() - gemini_start) * 1000

                # Get actual cost estimate (if available)
                cost = 0.0001  # Default estimate
                status = self.gemini_service.get_status()
                if status.get('total_cost_usd'):
                    # Calculate incremental cost (rough estimate)
                    cost = 0.0001  # Typical small query cost

                # Record API request
                self.api_monitor.record_request(APIRequest(
                    timestamp=time.time(),
                    api_type='gemini',
                    operation='DO',
                    tokens_input=len(query.split()) * 1.3,  # Rough estimate
                    tokens_output=len(gemini_response.split()) * 1.3,
                    cost=cost,
                    duration_ms=gemini_duration,
                    success=True,
                    error=None,
                    priority=APIPriority.HIGH.value
                ))

                self.stats['total_requests'] += 1
                self.stats['online_requests'] += 1
                self.stats['total_cost'] += cost

                # Track performance (v1.2.1)
                duration = gemini_duration / 1000.0
                self.performance_monitor.track_query(
                    query_type='DO',
                    mode='gemini',
                    duration=duration,
                    cost=cost,
                    tokens=int((len(query.split()) + len(gemini_response.split())) * 1.3),
                    success=True
                )

                # Log to unified logger
                log_performance('DO', duration, offline=False, mode='gemini', cost=cost)
                log_api('gemini', duration, cost, success=True, operation='DO')

                # Store in history
                self._add_to_history({
                    'timestamp': datetime.now().isoformat(),
                    'command': 'DO',
                    'query': query,
                    'method': 'gemini',
                    'confidence': 0.95,  # Gemini assumed high confidence
                    'sources': ['Gemini AI'],
                    'duration_ms': duration_ms,
                    'cost': cost
                })

                return f"""🤖 Gemini AI (Online)
Cost: ${cost:.4f} | Duration: {duration_ms:.0f}ms

{gemini_response}

💡 Offline confidence was {offline_response.confidence:.0%}
   Try rephrasing for better offline results
"""

            except Exception as e:
                # Gemini failed - record and fall back to offline response
                if self.logger:
                    self.logger.error(f"GENERATE DO: Gemini error: {e}")

                # Record failed API request
                self.api_monitor.record_request(APIRequest(
                    timestamp=time.time(),
                    api_type='gemini',
                    operation='DO',
                    tokens_input=len(query.split()) * 1.3,
                    tokens_output=0,
                    cost=0.0,
                    duration_ms=(time.time() - start_time) * 1000,
                    success=False,
                    error=str(e),
                    priority=APIPriority.HIGH.value
                ))

                return f"""⚠️ Offline Response (Gemini unavailable)
Confidence: {offline_response.confidence:.0%}

{offline_response.content}

❌ Gemini Error: {str(e)}

💡 This offline answer may be incomplete.
   Try: HELP SEARCH or GUIDE <topic>
"""

        # Step 3: No Gemini available - return offline response with disclaimer
        self.stats['total_requests'] += 1
        self.stats['offline_requests'] += 1

        self._add_to_history({
            'timestamp': datetime.now().isoformat(),
            'command': 'DO',
            'query': query,
            'method': offline_response.method,
            'confidence': offline_response.confidence,
            'sources': offline_response.sources,
            'duration_ms': duration_ms,
            'cost': 0.0
        })

        return f"""📚 Offline Response (Gemini not configured)
Confidence: {offline_response.confidence:.0%}

{offline_response.content}

💡 Gemini Extension Not Available:
   To enable online AI fallback:
   1. Get API key: https://makersuite.google.com/app/apikey
   2. Add to .env: GEMINI_API_KEY=your_key_here

   Or improve offline results:
   - Use more specific keywords
   - Try GUIDE <topic> for detailed guides
   - Use HELP SEARCH for command help
"""

    # ========== REDO Command (Retry Last Generation) ==========

    def _handle_redo(self, params: List[str], grid=None) -> str:
        """
        Handle GENERATE REDO - Retry last generation.

        Args:
            params: Optional modifications to last query
            grid: Optional grid for context

        Returns:
            Regenerated response
        """
        if not self.generation_history:
            return """❌ No previous generation to redo

Use GENERATE DO first, then GENERATE REDO to retry.

Example:
  GENERATE DO how do I purify water?
  GENERATE REDO  # Retry same query
  GENERATE REDO with boiling  # Add constraint
"""

        # Get last generation
        last_gen = self.generation_history[-1]

        # Build new query
        if params:
            # Modify query with additional params
            original_query = last_gen['query']
            modification = " ".join(params)
            new_query = f"{original_query} {modification}"
        else:
            # Same query
            new_query = last_gen['query']

        # Re-run DO command
        return f"🔄 Retrying: {new_query}\n\n" + self._handle_do(new_query.split(), grid)

    # ========== GUIDE Command (Generate Knowledge Guides) ==========

    def _handle_guide(self, params: List[str]) -> str:
        """
        Handle GENERATE GUIDE - Generate knowledge bank guides.

        Uses offline engine + Gemini to create comprehensive survival guides.

        Args:
            params: [topic, --category, --save]

        Returns:
            Generated guide content or save confirmation
        """
        if not params:
            return """❌ Usage: GENERATE GUIDE <topic> [--category CATEGORY] [--save]

Examples:
  GENERATE GUIDE water purification --category water --save
  GENERATE GUIDE fire starting methods --category fire
  GENERATE GUIDE emergency shelter --save

Categories: water, fire, shelter, food, navigation, medical

💡 This command is part of the knowledge expansion workflow.
   Requires Gemini API key for guide generation.
"""

        # Parse params
        topic_parts = []
        category = None
        save = False

        i = 0
        while i < len(params):
            param = params[i]

            if param == "--category":
                if i + 1 < len(params):
                    category = params[i + 1]
                    i += 2
                else:
                    return "❌ --category requires a value"
            elif param == "--save":
                save = True
                i += 1
            else:
                topic_parts.append(param)
                i += 1

        if not topic_parts:
            return "❌ Topic required"

        topic = " ".join(topic_parts)

        # Check if Gemini available
        if not self.gemini_service or not self.gemini_service.is_available:
            return """❌ GENERATE GUIDE requires Gemini API

Setup:
1. Get API key: https://makersuite.google.com/app/apikey
2. Add to .env: GEMINI_API_KEY=your_key_here
3. Retry command

💡 For existing guides, use: GUIDE <topic>
"""

        # Generate guide using Gemini with knowledge bank context
        try:
            start_time = time.time()

            # Search knowledge bank for related content
            kb_results = self.knowledge_manager.search(topic, limit=5, category=category)

            # Build context for Gemini
            context = {
                'topic': topic,
                'category': category or 'general',
                'existing_guides': kb_results,
                'format': 'markdown',
                'style': 'survival_guide'
            }

            # Use guide creation prompt
            prompt = f"""Create a comprehensive survival guide about: {topic}

Category: {category or 'general'}

Format as a practical survival guide with:
1. Overview (2-3 sentences)
2. Materials Needed (bulleted list)
3. Step-by-Step Instructions (numbered)
4. Safety Warnings (if applicable)
5. Tips & Tricks
6. Common Mistakes

Existing related guides: {len(kb_results)}

Write in clear, concise language for field use.
Use markdown formatting."""

            response = self.gemini_service.ask(prompt, context=context)
            duration_ms = (time.time() - start_time) * 1000

            # Add metadata header
            guide_content = f"""# {topic.title()}

**Category:** {category or 'General'}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Source:** AI-Generated (Gemini)

---

{response}

---

*This guide was AI-generated. Always verify information and use common sense in survival situations.*
"""

            # Save if requested
            if save:
                # Determine filename
                filename = topic.lower().replace(' ', '-') + '.md'
                if category:
                    save_path = self.guide_output / category / filename
                else:
                    save_path = self.guide_output / 'generated' / filename

                save_path.parent.mkdir(parents=True, exist_ok=True)

                with open(save_path, 'w') as f:
                    f.write(guide_content)

                return f"""✅ Guide Generated and Saved

Topic: {topic}
Category: {category or 'general'}
File: {save_path}
Duration: {duration_ms:.0f}ms

Preview:
{guide_content[:500]}...

💡 View full guide: GUIDE {topic}
"""

            else:
                return f"""✅ Guide Generated (Not Saved)

{guide_content}

💡 To save: Add --save flag
   GENERATE GUIDE {topic} --save
"""

        except Exception as e:
            return f"❌ Guide generation failed: {str(e)}"

    # ========== SVG Command (Delegate to Old Handler) ==========

    def _handle_svg(self, params: List[str]) -> str:
        """
        Handle GENERATE SVG - Generate vector diagrams.

        This delegates to the existing SVG generation logic.

        Args:
            params: SVG generation parameters

        Returns:
            SVG generation result
        """
        # Import and use old generate_handler logic
        # This maintains backward compatibility
        try:
            from core.commands.generate_handler import GenerateHandler as OldHandler
            old_handler = OldHandler(viewport=self.viewport, logger=self.logger)
            return old_handler._generate_svg(params)
        except Exception as e:
            return f"❌ SVG generation failed: {str(e)}\n\nSee: GENERATE HELP"

    # ========== ASCII Command (Delegate to Old Handler) ==========

    def _handle_ascii(self, params: List[str]) -> str:
        """
        Handle GENERATE ASCII - Generate ASCII art.

        Args:
            params: ASCII generation parameters

        Returns:
            ASCII generation result
        """
        try:
            from core.commands.generate_handler import GenerateHandler as OldHandler
            old_handler = OldHandler(viewport=self.viewport, logger=self.logger)
            return old_handler._generate_ascii(params)
        except Exception as e:
            return f"❌ ASCII generation failed: {str(e)}\n\nSee: GENERATE HELP"

    # ========== TELETEXT Command (Delegate to Old Handler) ==========

    def _handle_teletext(self, params: List[str]) -> str:
        """
        Handle GENERATE TELETEXT - Generate teletext graphics.

        Args:
            params: Teletext generation parameters

        Returns:
            Teletext generation result
        """
        try:
            from core.commands.generate_handler import GenerateHandler as OldHandler
            old_handler = OldHandler(viewport=self.viewport, logger=self.logger)
            return old_handler._generate_teletext(params)
        except Exception as e:
            return f"❌ Teletext generation failed: {str(e)}\n\nSee: GENERATE HELP"

    # ========== SEQUENCE Command (v1.2.17) ==========

    def _handle_sequence(self, params: List[str]) -> str:
        """
        Handle GENERATE SEQUENCE - Generate sequence diagrams.

        Uses templates from core/data/diagrams/sequence/.

        Args:
            params: Sequence parameters [template_name or --list]

        Returns:
            Sequence diagram or template list
        """
        diagrams_path = PATHS.ROOT / 'core' / 'data' / 'diagrams' / 'sequence'
        
        # List templates
        if params and params[0] == '--list':
            try:
                templates = list(diagrams_path.glob('*.txt'))
                if not templates:
                    return "❌ No sequence diagram templates found"
                
                output = "📋 Available Sequence Diagram Templates:\n\n"
                for template in sorted(templates):
                    name = template.stem
                    output += f"  • {name}\n"
                output += "\n💡 Usage: GENERATE SEQUENCE <template_name>"
                return output
            except Exception as e:
                return f"❌ Failed to list templates: {str(e)}"
        
        # Generate from template
        if not params:
            return """❌ Usage: GENERATE SEQUENCE <template_name>

Examples:
  GENERATE SEQUENCE api_request
  GENERATE SEQUENCE --list

Available templates in core/data/diagrams/sequence/
"""
        
        template_name = params[0]
        template_file = diagrams_path / f"{template_name}.txt"
        
        if not template_file.exists():
            return f"""❌ Template '{template_name}' not found

Use: GENERATE SEQUENCE --list
"""
        
        try:
            content = template_file.read_text()
            
            # Save to drafts with ISO 8601 timestamp
            output_dir = PATHS.MEMORY_DRAFTS / 'sequence'
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = generate_session(template_name, ".txt")
            output_file = output_dir / filename
            output_file.write_text(content)
            
            return f"""✅ Sequence Diagram Generated

Template: {template_name}
Output: {output_file.relative_to(PATHS.ROOT)}

{content}

💡 Saved to {output_file.relative_to(PATHS.ROOT)}
"""
        except Exception as e:
            return f"❌ Failed to generate sequence diagram: {str(e)}"

    # ========== FLOW Command (v1.2.17) ==========

    def _handle_flow(self, params: List[str]) -> str:
        """
        Handle GENERATE FLOW - Generate flowchart diagrams.

        Uses templates from core/data/diagrams/flow/.

        Args:
            params: Flow parameters [template_name or --list]

        Returns:
            Flowchart diagram or template list
        """
        diagrams_path = PATHS.ROOT / 'core' / 'data' / 'diagrams' / 'flow'
        
        # List templates
        if params and params[0] == '--list':
            try:
                templates = list(diagrams_path.glob('*.txt'))
                if not templates:
                    return "❌ No flowchart templates found"
                
                output = "📋 Available Flowchart Templates:\n\n"
                for template in sorted(templates):
                    name = template.stem
                    output += f"  • {name}\n"
                output += "\n💡 Usage: GENERATE FLOW <template_name>"
                return output
            except Exception as e:
                return f"❌ Failed to list templates: {str(e)}"
        
        # Generate from template
        if not params:
            return """❌ Usage: GENERATE FLOW <template_name>

Examples:
  GENERATE FLOW login_process
  GENERATE FLOW --list

Available templates in core/data/diagrams/flow/
"""
        
        template_name = params[0]
        template_file = diagrams_path / f"{template_name}.txt"
        
        if not template_file.exists():
            return f"""❌ Template '{template_name}' not found

Use: GENERATE FLOW --list
"""
        
        try:
            content = template_file.read_text()
            
            # Save to drafts with ISO 8601 timestamp
            output_dir = PATHS.MEMORY_DRAFTS / 'flow'
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = generate_session(template_name, ".txt")
            output_file = output_dir / filename
            output_file.write_text(content)
            
            return f"""✅ Flowchart Generated

Template: {template_name}
Output: {output_file.relative_to(PATHS.ROOT)}

{content}

💡 Saved to {output_file.relative_to(PATHS.ROOT)}
"""
        except Exception as e:
            return f"❌ Failed to generate flowchart: {str(e)}"

    # ========== STATUS Command ==========

    def _handle_status(self) -> str:
        """Show GENERATE command statistics."""
        uptime = (datetime.now() - self.stats['session_start']).total_seconds()
        uptime_str = f"{uptime / 3600:.1f}h" if uptime >= 3600 else f"{uptime:.0f}s"

        offline_pct = (self.stats['offline_requests'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0
        online_pct = (self.stats['online_requests'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0

        avg_cost = (self.stats['total_cost'] / self.stats['total_requests']) if self.stats['total_requests'] > 0 else 0

        # Check service availability
        offline_status = "✅ Active"
        gemini_status = "❌ Not Available"
        if self.gemini_service and self.gemini_service.is_available:
            gemini_status = "✅ Active"

        # Get API monitor stats
        api_stats = self.api_monitor.get_stats()
        live_stats = self.api_monitor.get_live_stats()

        # Get any alerts
        alerts = self.api_monitor.get_alerts()
        alerts_display = ""
        if alerts:
            alerts_display = "\n\n🚨 Active Alerts:\n"
            for alert in alerts[-3:]:  # Last 3 alerts
                icon = "⚠️" if alert['level'] == 'warning' else "❌"
                alerts_display += f"  {icon} {alert['message']} ({alert['timestamp']})\n"

        return f"""📊 GENERATE System Status

Uptime: {uptime_str}

Services:
  Offline Engine: {offline_status}
  Gemini Extension: {gemini_status}

Usage Statistics:
  Total Requests: {self.stats['total_requests']}
  Offline Requests: {self.stats['offline_requests']} ({offline_pct:.0f}%)
  Online Requests: {self.stats['online_requests']} ({online_pct:.0f}%)
  Total Cost: ${self.stats['total_cost']:.4f}
  Avg Cost/Request: ${avg_cost:.4f}

History:
  Generation History: {len(self.generation_history)} items
  Max History: {self.max_history}

{live_stats}{alerts_display}

💡 Use GENERATE CLEAR to clear history
"""

    # ========== VALIDATE Command (v1.2.1) ==========

    def _handle_validate(self) -> str:
        """
        Validate v1.2.0 success criteria.

        Checks:
        1. Offline query rate ≥90%
        2. Cost reduction ≥99%
        3. Average response time <500ms
        4. P95 response time <500ms

        Returns:
            Validation report with success criteria status
        """
        # Get validation results
        validation = self.performance_monitor.validate_success_criteria()

        # Build report
        report = "📊 GENERATE System Validation (v1.2.0 Success Criteria)\n\n"

        # Overall status
        all_passed = validation['all_passed']
        status = "✅ ALL CRITERIA MET" if all_passed else "❌ CRITERIA NOT MET"
        report += f"{status}\n\n"

        # Individual criteria
        report += "Criteria:\n"
        criteria = validation['criteria']

        for name, details in criteria.items():
            icon = "✅" if details['passed'] else "❌"
            desc = details['description']
            actual = details['actual']
            target = details['target']

            # Format based on type
            if 'rate' in name:
                actual_str = f"{actual*100:.1f}%"
                target_str = f"{target*100:.0f}%"
            elif 'cost' in name:
                actual_str = f"{actual:.1f}%"
                target_str = f"{target:.0f}%"
            else:  # response time
                actual_str = f"{actual*1000:.0f}ms"
                target_str = f"{target*1000:.0f}ms"

            report += f"  {icon} {desc}: {actual_str} (target: {target_str})\n"

        # Session summary
        stats = validation['session_stats']
        report += f"\nSession Summary:\n"
        report += f"  Total Queries: {stats.get('total_queries', 0)}\n"
        report += f"  Offline Queries: {stats.get('offline_queries', 0)}\n"
        report += f"  Online Queries: {stats.get('online_queries', 0)}\n"
        report += f"  Total Cost: ${stats.get('total_cost', 0):.4f}\n"
        report += f"  Cost Savings: ${stats.get('cost_savings', 0):.4f}\n"

        # Performance report
        report += f"\n{self.performance_monitor.generate_report()}"

        # Log validation
        log_performance('VALIDATE', 0.0, offline=True,
                       validation=all_passed, criteria_met=sum(1 for c in criteria.values() if c['passed']))

        return report    # ========== CLEAR Command ==========

    def _handle_clear(self) -> str:
        """Clear generation history."""
        count = len(self.generation_history)
        self.generation_history.clear()

        # Also clear Gemini history if available
        if self.gemini_service and self.gemini_service.is_available:
            self.gemini_service.clear_history()

        return f"✅ Cleared {count} generation history items"

    # ========== Helper Methods ==========

    def _add_to_history(self, entry: Dict[str, Any]) -> None:
        """
        Add entry to generation history.

        Args:
            entry: History entry dict
        """
        self.generation_history.append(entry)

        # Trim history if needed
        if len(self.generation_history) > self.max_history:
            self.generation_history = self.generation_history[-self.max_history:]

    def _show_help(self) -> str:
        """Display GENERATE command help."""
        return """🤖 GENERATE Command - Unified AI & Generation System

OFFLINE-FIRST COMMANDS (No API Key Required):
  GENERATE DO <question>              - Offline-first Q&A (knowledge bank + FAQ)
  GENERATE REDO [modification]        - Retry last generation
  GENERATE STATUS                     - Show usage statistics
  GENERATE VALIDATE                   - Validate v1.2.0 success criteria
  GENERATE CLEAR                      - Clear history

ONLINE COMMANDS (Require Gemini API Key):
  GENERATE GUIDE <topic> [--save]     - Generate knowledge guides
  GENERATE SVG <description>          - Generate vector diagrams
  GENERATE ASCII <description>        - Generate ASCII art
  GENERATE TELETEXT <description>     - Generate teletext graphics

Examples:
  GENERATE DO how do I purify water?
  GENERATE REDO with boiling method
  GENERATE GUIDE fire starting --category fire --save
  GENERATE SVG water filter diagram --style technical
  GENERATE STATUS

Architecture:
  1. Offline Engine (90%+ queries) - FREE
     - 166+ survival guides in knowledge bank
     - 40+ FAQ entries
     - Intelligent synthesis

  2. Gemini Extension (fallback) - ~$0.0001/query
     - Used when offline confidence < 50%
     - Enhanced with local knowledge
     - Optional (uDOS works fully offline)

  3. Banana Image Generation - ~$0.001/image
     - For SVG/diagram generation only
     - Explicit --pro flag for higher quality

Migration from ASSISTANT:
  OLD: ASSISTANT ASK how do I purify water?
  NEW: GENERATE DO how do I purify water?

Setup Gemini (Optional):
  1. Get API key: https://makersuite.google.com/app/apikey
  2. Add to .env: GEMINI_API_KEY=your_key_here
  3. Test with: GENERATE STATUS

💡 Try GENERATE DO first - 90% of queries work offline!
"""
