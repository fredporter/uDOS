"""
uDOS v1.1.6 - GENERATE Command Handler

Unified generation system for SVG, diagrams, ASCII, and teletext using Nano Banana.

Commands:
- GENERATE SVG: Generate vector diagrams via Gemini 2.5 Flash Image → PNG → SVG pipeline
- GENERATE DIAGRAM: Alias for SVG generation
- GENERATE ASCII: Generate ASCII art diagrams
- GENERATE TELETEXT: Generate BBC-style teletext graphics

Pipeline: Style Guide → Nano Banana (PNG) → Vectorize → Validate → Save SVG

Author: uDOS Development Team
Version: 1.1.6
"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import time


class GenerateHandler:
    """Handle all GENERATE commands with unified pipeline."""

    def __init__(self, viewport=None, logger=None):
        """
        Initialize GENERATE handler.

        Args:
            viewport: Viewport instance for output display
            logger: Logger instance for logging
        """
        self.viewport = viewport
        self.logger = logger

        # Lazy load services
        self._gemini_generator = None
        self._vectorizer = None
        self._ascii_generator = None

        # Output directories
        self.svg_output = Path("sandbox/drafts/svg")
        self.ascii_output = Path("sandbox/drafts/ascii")
        self.teletext_output = Path("sandbox/drafts/teletext")

        # Ensure directories exist
        self.svg_output.mkdir(parents=True, exist_ok=True)
        self.ascii_output.mkdir(parents=True, exist_ok=True)
        self.teletext_output.mkdir(parents=True, exist_ok=True)

    @property
    def gemini_generator(self):
        """Lazy load Gemini generator."""
        if self._gemini_generator is None:
            try:
                from core.services.gemini_generator import GeminiGenerator
                self._gemini_generator = GeminiGenerator()
                if self.logger:
                    self.logger.info("Gemini generator loaded")
            except ImportError as e:
                if self.logger:
                    self.logger.error(f"Failed to load Gemini generator: {e}")
                raise ImportError(
                    "Gemini generator not available. "
                    "Requires GEMINI_API_KEY in .env"
                ) from e
        return self._gemini_generator

    @property
    def vectorizer(self):
        """Lazy load vectorizer service."""
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

    def handle_command(self, params):
        """
        Handle GENERATE command routing.

        Args:
            params: Command parameters [subcommand, description, options...]

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        # Check for --survival-help flag anywhere
        if "--survival-help" in params:
            return self._show_survival_help()

        subcommand = params[0].upper()
        remaining_params = params[1:]

        if subcommand in ["SVG", "DIAGRAM"]:
            return self._generate_svg(remaining_params)
        elif subcommand == "ASCII":
            return self._generate_ascii(remaining_params)
        elif subcommand == "TELETEXT":
            return self._generate_teletext(remaining_params)
        elif subcommand == "HELP":
            return self._show_help()
        elif subcommand == "--SURVIVAL-HELP":  # Direct command
            return self._show_survival_help()
        else:
            return f"❌ Unknown GENERATE subcommand: {subcommand}\n\n" + self._show_help()

    def _generate_svg(self, params):
        """
        Generate SVG diagram via Nano Banana pipeline.

        Pipeline: Load Style Guide → Generate PNG → Vectorize → Validate → Save SVG

        Args:
            params: [description, --style, --type, --save, --no-preview, --survival, etc.]

        Returns:
            Result message with saved file path
        """
        # Parse parameters
        description_parts = []
        style = "technical-kinetic"
        diagram_type = "flowchart"
        save_path = None
        preview = True
        use_pro = False
        strict = False
        survival_category = None  # v1.1.15: Survival-specific templates
        survival_prompt = None    # v1.1.15: Specific prompt key

        i = 0
        while i < len(params):
            param = params[i]

            if param == "--style":
                if i + 1 < len(params):
                    style = params[i + 1]
                    i += 2
                else:
                    return "❌ --style requires a value\n\n" + self._show_help()

            elif param == "--type":
                if i + 1 < len(params):
                    diagram_type = params[i + 1]
                    i += 2
                else:
                    return "❌ --type requires a value\n\n" + self._show_help()

            elif param == "--save":
                if i + 1 < len(params):
                    save_path = params[i + 1]
                    i += 2
                else:
                    return "❌ --save requires a filename\n\n" + self._show_help()

            elif param == "--survival":
                # v1.1.15: Use survival-specific templates
                if i + 1 < len(params):
                    survival_spec = params[i + 1]
                    if '/' in survival_spec:
                        survival_category, survival_prompt = survival_spec.split('/', 1)
                    else:
                        survival_category = survival_spec
                        survival_prompt = None
                    i += 2
                else:
                    return "❌ --survival requires category or category/prompt\n\n" + self._show_survival_help()

            elif param == "--no-preview":
                preview = False
                i += 1

            elif param == "--pro":
                use_pro = True
                i += 1

            elif param == "--strict":
                strict = True
                i += 1

            else:
                description_parts.append(param)
                i += 1

        # Build description
        description = " ".join(description_parts)

        if not description:
            return "❌ No description provided\n\n" + self._show_help()

        # Validate style
        valid_styles = ["technical-kinetic", "hand-illustrative", "hybrid"]
        if style not in valid_styles:
            return (
                f"❌ Invalid style: {style}\n"
                f"Valid styles: {', '.join(valid_styles)}\n\n"
                + self._show_help()
            )

        # Validate diagram type
        valid_types = ["flowchart", "architecture", "kinetic-flow", "hatching-pattern",
                      "typography", "curved-conduits", "gears-cogs", "schematic"]
        if diagram_type not in valid_types:
            return (
                f"❌ Invalid diagram type: {diagram_type}\n"
                f"Valid types: {', '.join(valid_types)}\n\n"
                + self._show_help()
            )

        # Start generation
        try:
            if self.logger:
                log_msg = f"Generating SVG: {description} (style: {style}, type: {diagram_type}, pro: {use_pro}"
                if survival_category:
                    log_msg += f", survival: {survival_category}/{survival_prompt or 'auto'}"
                log_msg += ")"
                self.logger.info(log_msg)

            start_time = time.time()

            # Step 1: Generate PNG via Nano Banana
            if self.viewport:
                mode = "Survival Template" if survival_category else "Standard"
                self.viewport.write(f"⏳ Generating PNG via Nano Banana ({mode})...")

            # v1.1.15: Use survival-specific templates if specified
            if survival_category:
                if not survival_prompt:
                    # Auto-select first prompt from category
                    try:
                        cat_prompts = self.gemini_generator.prompts['prompts']['survival']['categories'][survival_category]['prompts']
                        survival_prompt = list(cat_prompts.keys())[0]
                        if self.viewport:
                            self.viewport.write(f"   Auto-selected prompt: {survival_prompt}")
                    except (KeyError, IndexError) as e:
                        return f"❌ Failed to auto-select prompt for category '{survival_category}': {e}"

                png_bytes, metadata = self.gemini_generator.generate_survival_diagram(
                    category=survival_category,
                    prompt_key=survival_prompt,
                    use_pro=use_pro
                )

                # Get vectorization preset for this survival category
                vec_params = self.gemini_generator.get_vectorization_preset(survival_category, survival_prompt)
                stroke_width = vec_params.get('stroke_width', 2.5)
            else:
                # Standard generation
                png_bytes, metadata = self.gemini_generator.generate_image_svg(
                    subject=description,
                    diagram_type=diagram_type,
                    style=style,
                    use_pro=use_pro
                )
                stroke_width = 2.5  # Default

            if not png_bytes:
                return "❌ Failed to generate PNG from Nano Banana"

            if self.viewport:
                self.viewport.write(f"✅ PNG generated ({len(png_bytes)} bytes)")

            # Step 2: Vectorize PNG → SVG
            if self.viewport:
                self.viewport.write("⏳ Vectorizing PNG to SVG...")

            vectorize_result = self.vectorizer.vectorize(
                png_bytes,
                stroke_width=stroke_width,  # Use optimized stroke width
                simplify=True,
                validate_compliance=strict
            )

            if not vectorize_result.svg_content:
                return "❌ Failed to vectorize PNG to SVG"

            if self.viewport:
                self.viewport.write(
                    f"✅ Vectorized using {vectorize_result.method} "
                    f"({vectorize_result.metadata.get('path_count', 0)} paths)"
                )

            # Step 3: Validate compliance
            validation = vectorize_result.validation
            if strict and not validation.get("compliant", False):
                errors = validation.get("errors", [])
                warnings = validation.get("warnings", [])
                return (
                    f"❌ SVG validation failed (strict mode):\n"
                    f"   Errors: {', '.join(errors) if errors else 'None'}\n"
                    f"   Warnings: {', '.join(warnings) if warnings else 'None'}\n"
                    f"💡 Retry without --strict flag to accept with warnings"
                )

            # Step 4: Save SVG
            if not save_path:
                # Auto-generate filename
                safe_desc = description.replace(' ', '-').replace('/', '-')[:30]
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                save_path = f"{safe_desc}-{style}-{timestamp}.svg"

            # Ensure .svg extension
            if not save_path.endswith('.svg'):
                save_path += '.svg'

            # Save to sandbox/drafts/svg/
            output_path = self.svg_output / save_path
            output_path.write_text(vectorize_result.svg_content, encoding='utf-8')

            generation_time = time.time() - start_time

            if self.logger:
                self.logger.info(f"SVG generated: {output_path} ({generation_time:.1f}s)")

            # Build success response
            response = f"✅ SVG diagram generated: {description}\n"
            response += f"   Style: {style}\n"
            response += f"   Type: {diagram_type}\n"
            response += f"   Vectorizer: {vectorize_result.method}\n"
            response += f"   Time: {generation_time:.1f}s\n"
            response += f"   Saved: {output_path}\n"

            # Show validation status
            if validation.get("compliant"):
                response += "   Validation: ✅ Technical-Kinetic compliant\n"
            elif validation.get("warnings"):
                response += f"   Validation: ⚠️ {len(validation['warnings'])} warnings\n"

            # Show preview if requested
            if preview:
                response += "\n💡 Preview:\n"
                response += f"   - Open in browser: open {output_path}\n"
                response += f"   - View metadata: cat {output_path} | head -20\n"

            # Show next steps
            response += "\n🔧 Next Steps:\n"
            response += f"   - Edit: open -a 'Inkscape' {output_path}\n"
            response += "   - Regenerate: GENERATE SVG {description} --style {other-style}\n"
            response += "   - Refine: GENERATE SVG {description} --pro --strict\n"

            return response

        except ImportError as e:
            return (
                f"❌ Generation system not available: {e}\n\n"
                "This feature requires:\n"
                "  - Gemini API key (GEMINI_API_KEY in .env)\n"
                "  - potrace or vtracer (vectorization)\n\n"
                "Install: brew install potrace"
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"SVG generation error: {e}", exc_info=True)
            return f"❌ Error generating SVG: {e}"

    def _generate_ascii(self, params):
        """
        Generate ASCII art diagram with Unicode box-drawing.

        Args:
            params: [type, description, --style, --width, --save, etc.]

        Returns:
            ASCII art diagram

        Supported types:
        - box: Simple box with title/content
        - table: Data table with headers
        - flowchart: Vertical flowchart
        - panel: Panel header (block/plain style)
        - progress: Progress bar
        - banner: Centered banner text
        - list: Bulleted/numbered/checkbox list
        """
        # Parse parameters
        diagram_type = None
        description_parts = []
        width = 60
        height = 10
        style = "unicode"
        save_path = None

        # Additional params for specific diagram types
        headers = []
        rows = []
        items = []
        percentage = 0

        i = 0
        while i < len(params):
            param = params[i]

            if param.lower() in ["box", "table", "flowchart", "panel", "progress", "banner", "list", "tree"]:
                diagram_type = param.lower()
                i += 1
            elif param == "--width":
                if i + 1 < len(params):
                    try:
                        width = int(params[i + 1])
                        i += 2
                    except ValueError:
                        return "❌ --width requires an integer\n"
                else:
                    return "❌ --width requires a value\n"
            elif param == "--height":
                if i + 1 < len(params):
                    try:
                        height = int(params[i + 1])
                        i += 2
                    except ValueError:
                        return "❌ --height requires an integer\n"
                else:
                    return "❌ --height requires a value\n"
            elif param == "--style":
                if i + 1 < len(params):
                    style = params[i + 1]
                    i += 2
                else:
                    return "❌ --style requires a value (unicode/plain/blocks)\n"
            elif param == "--save":
                if i + 1 < len(params):
                    save_path = params[i + 1]
                    i += 2
                else:
                    return "❌ --save requires a filename\n"
            elif param == "--percent":
                if i + 1 < len(params):
                    try:
                        percentage = int(params[i + 1])
                        i += 2
                    except ValueError:
                        return "❌ --percent requires an integer (0-100)\n"
                else:
                    return "❌ --percent requires a value\n"
            else:
                description_parts.append(param)
                i += 1

        description = " ".join(description_parts)

        if not description and diagram_type not in ["table", "list"]:
            return self._ascii_help()

        try:
            # Get ASCII generator with requested style
            from core.services.ascii_generator import get_ascii_generator
            generator = get_ascii_generator(style=style)

            # Generate based on type
            if diagram_type == "box":
                ascii_art = generator.generate_box(
                    width=width,
                    height=height,
                    title=description,
                    style="single" if style != "double" else "double"
                )
            elif diagram_type == "panel":
                panel_style = "blocks" if style == "blocks" else "plain"
                ascii_art = generator.generate_panel(
                    width=width,
                    title=description,
                    style=panel_style
                )
            elif diagram_type == "banner":
                banner_style = "blocks" if style == "blocks" else ("double" if style == "unicode" else "single")
                ascii_art = generator.generate_banner(
                    text=description,
                    width=width,
                    style=banner_style
                )
            elif diagram_type == "progress":
                ascii_art = generator.generate_progress_bar(
                    label=description,
                    percentage=percentage,
                    width=width,
                    style="blocks" if style == "blocks" else "chars"
                )
            elif diagram_type == "list":
                # Parse items from description (semicolon-separated)
                items = [item.strip() for item in description.split(';')]
                list_style = "bullet"  # Default
                if "--numbered" in params:
                    list_style = "number"
                elif "--checkbox" in params:
                    list_style = "checkbox"

                ascii_art = generator.generate_list(items, style=list_style)
            elif diagram_type == "table":
                # Simple example table (would need more sophisticated parsing)
                headers = ["Column 1", "Column 2", "Column 3"]
                rows = [
                    ["Data 1", "Data 2", "Data 3"],
                    ["Row 2", "Value", "More"]
                ]
                ascii_art = generator.generate_table(headers, rows)
            else:
                # Default: simple box with description
                ascii_art = generator.generate_box(
                    width=width,
                    height=8,
                    title=description or "ASCII Diagram",
                    content=[
                        "Use GENERATE ASCII with a type:",
                        "",
                        "  box, panel, banner, table,",
                        "  progress, list, flowchart",
                    ],
                    style="single"
                )

            # Save if requested
            if save_path:
                from pathlib import Path
                output_path = generator.save(ascii_art, save_path, Path("memory/drafts/ascii"))
                return f"✅ ASCII diagram saved: {output_path}\n\n{ascii_art}\n"
            else:
                return f"✅ ASCII diagram:\n\n{ascii_art}\n"

        except Exception as e:
            if self.logger:
                self.logger.error(f"ASCII generation error: {e}", exc_info=True)
            return f"❌ Error generating ASCII: {e}\n"

    def _ascii_help(self):
        """Show ASCII generation help."""
        return """
┌──────────────────────────────────────────────────────────────────┐
│  GENERATE ASCII - Unicode Box-Drawing Diagrams                   │
└──────────────────────────────────────────────────────────────────┘

USAGE:
  GENERATE ASCII <type> <description> [options]

TYPES:
  box         Simple box with title and content
  panel       Panel header (block or plain style)
  banner      Centered banner text
  table       Data table with headers and rows
  progress    Progress bar with percentage
  list        Bulleted, numbered, or checkbox list
  flowchart   Vertical flowchart (basic)
  tree        Tree structure

OPTIONS:
  --width <n>      Diagram width (default: 60)
  --height <n>     Diagram height (default: 10)
  --style <s>      unicode | plain | blocks
  --percent <n>    Progress percentage (0-100)
  --save <file>    Save to file
  --numbered       Use numbered list
  --checkbox       Use checkbox list

STYLES:
  unicode    ┌─┐ │ └─┘ (refined box-drawing)
  plain      +--+ | (maximum compatibility)
  blocks     █▓▒░ (visual hierarchy)

EXAMPLES:
  GENERATE ASCII box System Status --width 40 --style unicode
  GENERATE ASCII panel Mission Control --width 60 --style blocks
  GENERATE ASCII progress "Water Purification" --percent 75
  GENERATE ASCII banner "uDOS v1.1.15" --width 50 --style blocks
  GENERATE ASCII list "Water;Fire;Shelter;Food" --checkbox

See: core/data/diagrams/ for 50 pre-built examples
"""

    def _generate_teletext(self, params):
        """
        Generate teletext-style diagram.

        Args:
            params: [description, --save, etc.]

        Returns:
            Teletext diagram
        """
        description = " ".join(params)
        if not description:
            return "❌ No description provided\n"

        return (
            "⚠️ GENERATE TELETEXT is not yet implemented\n"
            "💡 Use DRAW command for ASCII diagrams:\n"
            f"   DRAW {description}"
        )



    def _show_help(self):
        """Show comprehensive GENERATE command help."""
        return """
╔══════════════════════════════════════════════════════════════════════╗
║  GENERATE - Unified Generation System (Nano Banana Pipeline)         ║
╚══════════════════════════════════════════════════════════════════════╝

USAGE:
  GENERATE SVG <description> [options]
  GENERATE DIAGRAM <description> [options]  (alias for SVG)
  GENERATE ASCII <description> [options]
  GENERATE TELETEXT <description> [options]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SVG/DIAGRAM OPTIONS:
  <description>          Subject to illustrate (required)
  --style <style>        Visual style (default: technical-kinetic)
  --type <type>          Diagram type (default: flowchart)
  --survival <cat/key>   Use survival templates (v1.1.15) - see below
  --save <file>          Save to specific file (optional)
  --no-preview           Skip preview hints (optional)
  --pro                  Use Nano Banana Pro for refinement (slower)
  --strict               Enforce strict Technical-Kinetic validation

STYLES:
  technical-kinetic      MCM geometry, 2-3px strokes, monochrome (default)
  hand-illustrative      Hand-drawn aesthetic, organic lines
  hybrid                 Mix of technical precision + hand-drawn feel

DIAGRAM TYPES:
  flowchart              Process flows, decision trees (default)
  architecture           System architecture, MCM structures
  kinetic-flow           Mechanical flows, gears, motion
  schematic              Technical schematics, wiring diagrams
  hatching-pattern       Shading and texture patterns
  typography             Text layout and font demonstrations
  curved-conduits        Pipe flows, conduits, connections
  gears-cogs             Mechanical components, interlocking parts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ASCII OPTIONS:
  <description>          Subject to illustrate (required)
  --width <chars>        Character width (default: 80)
  --save <file>          Save to file (optional)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLES:

  GENERATE SVG water purification filter
    → Technical-Kinetic flowchart of water filter

  GENERATE SVG fire triangle --style hand-illustrative
    → Hand-drawn fire triangle diagram

  GENERATE SVG shelter construction --type architecture --pro
    → Precise MCM architecture with Pro refinement

  GENERATE SVG --survival water/purification_flow --pro
    → Optimized water purification flowchart using survival template (v1.1.15)

  GENERATE SVG --survival fire/fire_triangle --strict
    → Fire triangle using survival-specific prompt and validation

  GENERATE DIAGRAM gear mechanism --type kinetic-flow --strict
    → Kinetic flow diagram with strict validation

  GENERATE ASCII water cycle --width 100
    → ASCII art water cycle diagram

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PIPELINE (SVG/DIAGRAM):
  1. Load Style Guide     → 0-14 reference images cached
  2. Generate PNG         → Gemini 2.5 Flash Image (Nano Banana)
  3. Vectorize            → potrace (primary) or vtracer (fallback)
  4. Validate             → Technical-Kinetic compliance check
  5. Save SVG             → Editable vector file

OUTPUT:
  SVG files:     sandbox/drafts/svg/
  ASCII files:   sandbox/drafts/ascii/
  Teletext:      sandbox/drafts/teletext/

REQUIREMENTS:
  - Gemini API key (GEMINI_API_KEY in .env)
  - potrace (brew install potrace) OR vtracer (pip install vtracer)
  - Pillow (pip install Pillow>=10.0.0)

PERFORMANCE:
  Standard:  15-30 seconds per SVG
  --pro:     30-60 seconds (multi-turn refinement)
  ASCII:     Instant (offline)

SEE ALSO:
  DRAW       - Offline ASCII diagram library
  DIAGRAM    - Browse ASCII art templates
  SVG        - Legacy SVG command (deprecated, use GENERATE SVG)
  ASSIST     - AI assistance for content generation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPS:
  • Use --pro for critical diagrams requiring precision
  • Use --strict to enforce monochrome-only output
  • Use --survival for optimized survival category templates (v1.1.15)
  • Batch generation: Use uCODE loops with GENERATE commands
  • Edit SVGs in Inkscape or any vector editor
  • Technical-Kinetic style best for knowledge base diagrams
  • For survival help: GENERATE --survival-help

uCODE EXAMPLE:
  for topic in water fire shelter food
    [GENERATE|svg|$topic/overview|style=technical-kinetic|type=flowchart]
  done
"""

    def _show_survival_help(self):
        """Show survival-specific template help (v1.1.15)."""
        return """
╔══════════════════════════════════════════════════════════════════════╗
║  GENERATE --survival - Survival Diagram Templates (v1.1.15)          ║
╚══════════════════════════════════════════════════════════════════════╝

USAGE:
  GENERATE SVG --survival <category>/<prompt_key> [options]
  GENERATE SVG --survival <category> [options]  (auto-selects first prompt)

SURVIVAL CATEGORIES:

┌──────────────────────────────────────────────────────────────────────┐
│ WATER - Water systems and purification                               │
├──────────────────────────────────────────────────────────────────────┤
│  water/purification_flow     - Complete purification process         │
│  water/collection_system     - Rainwater catchment schematic         │
│  water/filtration_detail     - Multi-stage filter cross-section      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ FIRE - Fire systems and management                                   │
├──────────────────────────────────────────────────────────────────────┤
│  fire/fire_triangle          - Fire triangle with interdependencies  │
│  fire/fire_lay_types         - 4 fire lay configurations (2×2 grid)  │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ SHELTER - Shelter construction and insulation                        │
├──────────────────────────────────────────────────────────────────────┤
│  shelter/a_frame_construction - A-frame with dimensions & callouts   │
│  shelter/insulation_layers    - Layering system cross-section        │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ FOOD - Foraging and preservation                                     │
├──────────────────────────────────────────────────────────────────────┤
│  food/edible_plant_anatomy   - Plant identification (organic style)  │
│  food/food_preservation_flow - Preservation method decision tree     │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ NAVIGATION - Direction finding and orientation                       │
├──────────────────────────────────────────────────────────────────────┤
│  navigation/compass_rose_detailed - 16-point compass with degrees    │
│  navigation/sun_navigation       - Shadow stick method steps         │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ MEDICAL - First aid and wound care                                   │
├──────────────────────────────────────────────────────────────────────┤
│  medical/wound_care_flow     - Wound treatment procedure             │
│  medical/human_anatomy_reference - Anatomical zones for first aid    │
└──────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FEATURES (v1.1.15):
  ✅ Survival-specific prompts with domain terminology
  ✅ Category-optimized vectorization parameters
  ✅ Auto-selected style (technical-kinetic, hand-illustrative, hybrid)
  ✅ Pre-configured stroke width and pattern density per category

STYLES BY CATEGORY:
  water, fire, shelter, navigation, medical → technical_kinetic
  food                                      → hand_illustrative
  (Technical diagrams use MCM geometry, organic subjects use flowing lines)

VECTORIZATION PRESETS:
  technical  - For flowcharts, schematics (majority policy, low tolerance)
  organic    - For plants, natural forms (white policy, high tolerance)
  hybrid     - For mixed technical/organic (balanced settings)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLES:

  GENERATE SVG --survival water/purification_flow --pro
    → Water purification flowchart with optimized parameters

  GENERATE SVG --survival fire
    → Auto-selects fire/fire_triangle (first prompt in category)

  GENERATE SVG --survival food/edible_plant_anatomy --strict
    → Plant illustration with hand-illustrative style + strict validation

  GENERATE SVG --survival navigation/compass_rose_detailed --save compass.svg
    → 16-point compass rose saved to specified file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BENEFITS:
  • Consistent terminology across survival categories
  • Pre-tested prompts with proven results
  • Optimized vectorization for technical vs organic subjects
  • Faster iteration (no manual prompt engineering)
  • Style guide compliance built-in

SEE ALSO:
  GUIDE water    - Knowledge base for water systems
  GUIDE fire     - Knowledge base for fire management
  DRAW           - Offline ASCII diagram library
"""


def handle_generate_command(params, viewport=None, logger=None):
    """
    Helper function for GENERATE command.

    Args:
        params: Command parameters
        viewport: Viewport instance
        logger: Logger instance

    Returns:
        Command result message
    """
    handler = GenerateHandler(viewport=viewport, logger=logger)
    return handler.handle_command(params)


# Command metadata for uDOS command system
COMMAND_INFO = {
    'name': 'GENERATE',
    'version': '1.1.6',
    'category': 'graphics',
    'description': 'Unified generation system (SVG, ASCII, Teletext) via Nano Banana',
    'requires': ['Gemini API key', 'potrace or vtracer', 'Pillow'],
    'examples': [
        'GENERATE SVG water filter',
        'GENERATE SVG fire triangle --style hand-illustrative',
        'GENERATE DIAGRAM shelter --type architecture --pro --strict',
        'GENERATE ASCII water cycle --width 100'
    ],
    'see_also': ['DRAW', 'DIAGRAM', 'ASSIST'],
    'replaces': ['SVG (v1.1.5)']
}
