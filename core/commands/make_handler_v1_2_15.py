"""
uDOS v1.2.15 - MAKE Command Handler (Unified Graphics System)

5-Format Graphics System:
- ASCII: Template-based ASCII art with variable substitution
- Teletext: 8-color teletext pages with palette support
- SVG: AI-assisted SVG generation with style templates
- Sequence: Sequence diagrams using js-sequence syntax
- Flow: Flowcharts using flowchart.js syntax

Unified Syntax:
  MAKE --format <format> [options] <content>

Format-Specific Options:
  ASCII:     --template <name> [--data key=value] [--width N] [--border]
  Teletext:  --palette <name> [--width N] [--height N]
  SVG:       --style <name> [--width N] [--height N] "<description>"
  Sequence:  --template <name> | --source "<syntax>"
  Flow:      --template <name> | --source "<syntax>"

Common Options:
  --output <file>  Save to file (default: memory/drafts/<format>/)
  --list           List available templates/palettes/styles
  --help           Show format-specific help

Version: 1.2.15 (Graphics System Unification)
Author: uDOS Development Team
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from .base_handler import BaseCommandHandler
from core.services.graphics_service import get_graphics_service, GraphicsServiceError
from core.utils.paths import PATHS
from core.services.unified_logger import log_command, log_error


class MakeHandler(BaseCommandHandler):
    """
    Unified MAKE command handler for 5-format graphics system.
    
    Replaces old GENERATE/DIAGRAM commands with unified --format interface.
    Integrates with Node.js graphics renderer service on port 5555.
    """
    
    SUPPORTED_FORMATS = ['ascii', 'teletext', 'svg', 'sequence', 'flow']
    
    def __init__(self, **kwargs):
        """
        Initialize MAKE handler.
        
        Args:
            **kwargs: Standard handler dependencies
        """
        super().__init__(**kwargs)
        
        # Graphics service (Node.js renderer)
        self.graphics = get_graphics_service()
        
        # Output directories
        self.output_dirs = {
            'ascii': PATHS.MEMORY_DRAFTS_ASCII,
            'teletext': PATHS.MEMORY_DRAFTS_TELETEXT,
            'svg': PATHS.MEMORY_DRAFTS_SVG,
            'sequence': PATHS.MEMORY_DRAFTS_SVG,  # Sequence outputs SVG
            'flow': PATHS.MEMORY_DRAFTS_SVG       # Flow outputs SVG
        }
        
        # Ensure directories exist
        for dir_path in self.output_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Session statistics
        self.stats = {
            'total_renders': 0,
            'by_format': {fmt: 0 for fmt in self.SUPPORTED_FORMATS},
            'session_start': datetime.now()
        }
    
    def handle(self, command: str, params: List[str], grid=None) -> str:
        """
        Handle MAKE commands with unified format routing.
        
        Args:
            command: Command name (MAKE)
            params: Command parameters
            grid: Optional grid instance
            
        Returns:
            Command result message
        """
        if not params:
            return self._show_help()
        
        # Parse arguments
        args = self._parse_args(params)
        
        # Handle special commands
        if args.get('help'):
            return self._show_help(args.get('format'))
        
        if args.get('list'):
            return self._list_templates(args.get('format'))
        
        if args.get('status'):
            return self._show_status()
        
        # Validate format
        format_type = args.get('format')
        if not format_type:
            return "❌ Error: --format required. Supported: " + ", ".join(self.SUPPORTED_FORMATS)
        
        if format_type not in self.SUPPORTED_FORMATS:
            return f"❌ Error: Unsupported format '{format_type}'. Supported: {', '.join(self.SUPPORTED_FORMATS)}"
        
        # Check graphics service availability
        if not self.graphics.is_available():
            return (
                "❌ Graphics renderer service not available.\n"
                "Start service: cd extensions/core/graphics-renderer && npm start"
            )
        
        # Route to format-specific handler
        try:
            result = self._render_graphics(format_type, args)
            
            # Update statistics
            self.stats['total_renders'] += 1
            self.stats['by_format'][format_type] += 1
            
            log_command("MAKE", f"format={format_type}")
            
            return result
            
        except GraphicsServiceError as e:
            log_error("MAKE", str(e))
            return f"❌ Rendering error: {e}"
        except Exception as e:
            log_error("MAKE", str(e))
            return f"❌ Unexpected error: {e}"
    
    def _parse_args(self, params: List[str]) -> Dict[str, Any]:
        """
        Parse command arguments into structured dict.
        
        Args:
            params: Raw parameter list
            
        Returns:
            Parsed arguments dict
        """
        args = {
            'format': None,
            'template': None,
            'palette': None,
            'style': None,
            'source': None,
            'data': {},
            'options': {},
            'output': None,
            'content': [],
            'help': False,
            'list': False,
            'status': False
        }
        
        i = 0
        while i < len(params):
            param = params[i]
            
            # Flags
            if param == '--help':
                args['help'] = True
            elif param == '--list':
                args['list'] = True
            elif param == '--status':
                args['status'] = True
            
            # Format selection
            elif param == '--format' and i + 1 < len(params):
                args['format'] = params[i + 1].lower()
                i += 1
            
            # Template/palette/style
            elif param == '--template' and i + 1 < len(params):
                args['template'] = params[i + 1]
                i += 1
            elif param == '--palette' and i + 1 < len(params):
                args['palette'] = params[i + 1]
                i += 1
            elif param == '--style' and i + 1 < len(params):
                args['style'] = params[i + 1]
                i += 1
            
            # Source (raw syntax for sequence/flow)
            elif param == '--source' and i + 1 < len(params):
                args['source'] = params[i + 1]
                i += 1
            
            # Data (key=value pairs for ASCII templates)
            elif param == '--data' and i + 1 < len(params):
                pair = params[i + 1]
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    args['data'][key] = value
                i += 1
            
            # Options
            elif param == '--width' and i + 1 < len(params):
                args['options']['width'] = int(params[i + 1])
                i += 1
            elif param == '--height' and i + 1 < len(params):
                args['options']['height'] = int(params[i + 1])
                i += 1
            elif param == '--border':
                args['options']['border'] = True
            
            # Output file
            elif param == '--output' and i + 1 < len(params):
                args['output'] = params[i + 1]
                i += 1
            
            # Content (everything else)
            else:
                args['content'].append(param)
            
            i += 1
        
        return args
    
    def _render_graphics(self, format_type: str, args: Dict[str, Any]) -> str:
        """
        Render graphics using format-specific logic.
        
        Args:
            format_type: Graphics format
            args: Parsed arguments
            
        Returns:
            Success message with output location
        """
        if format_type == 'ascii':
            return self._render_ascii(args)
        elif format_type == 'teletext':
            return self._render_teletext(args)
        elif format_type == 'svg':
            return self._render_svg(args)
        elif format_type == 'sequence':
            return self._render_sequence(args)
        elif format_type == 'flow':
            return self._render_flow(args)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _render_ascii(self, args: Dict[str, Any]) -> str:
        """Render ASCII diagram from template."""
        template = args.get('template')
        if not template:
            return "❌ Error: --template required for ASCII format"
        
        # Render via graphics service
        output = self.graphics.render_ascii(
            template=template,
            data=args.get('data', {}),
            options=args.get('options', {})
        )
        
        # Save output
        output_file = self._save_output('ascii', template, output, args.get('output'))
        
        return f"✅ ASCII diagram rendered: {output_file}\n\n{output}"
    
    def _render_teletext(self, args: Dict[str, Any]) -> str:
        """Render teletext page with color palette."""
        content = ' '.join(args.get('content', []))
        if not content:
            return "❌ Error: Content required for teletext format"
        
        palette = args.get('palette', 'classic')
        
        # Render via graphics service
        output = self.graphics.render_teletext(
            content=content,
            palette=palette,
            options=args.get('options', {})
        )
        
        # Save output
        output_file = self._save_output('teletext', palette, output, args.get('output'))
        
        return f"✅ Teletext page rendered ({palette} palette): {output_file}\n\n{output}"
    
    def _render_svg(self, args: Dict[str, Any]) -> str:
        """Render SVG diagram (AI-assisted)."""
        description = ' '.join(args.get('content', []))
        if not description:
            return "❌ Error: Description required for SVG format"
        
        style = args.get('style', 'technical')
        
        # Render via graphics service
        output = self.graphics.render_svg(
            description=description,
            style=style,
            options=args.get('options', {})
        )
        
        # Save output
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"diagram_{timestamp}.svg"
        output_file = self._save_output('svg', filename, output, args.get('output'))
        
        return f"✅ SVG diagram rendered ({style} style): {output_file}"
    
    def _render_sequence(self, args: Dict[str, Any]) -> str:
        """Render sequence diagram."""
        source = args.get('source') or args.get('template')
        if not source:
            return "❌ Error: --template or --source required for sequence format"
        
        # Render via graphics service
        output = self.graphics.render_sequence(
            source=source,
            options=args.get('options', {})
        )
        
        # Save output
        name = args.get('template', 'sequence')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}.svg"
        output_file = self._save_output('sequence', filename, output, args.get('output'))
        
        return f"✅ Sequence diagram rendered: {output_file}"
    
    def _render_flow(self, args: Dict[str, Any]) -> str:
        """Render flowchart."""
        source = args.get('source') or args.get('template')
        if not source:
            return "❌ Error: --template or --source required for flow format"
        
        # Render via graphics service
        output = self.graphics.render_flow(
            source=source,
            options=args.get('options', {})
        )
        
        # Save output
        name = args.get('template', 'flowchart')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}.svg"
        output_file = self._save_output('flow', filename, output, args.get('output'))
        
        return f"✅ Flowchart rendered: {output_file}"
    
    def _save_output(self, format_type: str, name: str, content: str, 
                     custom_path: Optional[str] = None) -> Path:
        """
        Save rendered output to file.
        
        Args:
            format_type: Graphics format
            name: Base filename
            content: Rendered content
            custom_path: Optional custom output path
            
        Returns:
            Path to saved file
        """
        if custom_path:
            output_file = Path(custom_path)
        else:
            output_dir = self.output_dirs[format_type]
            # Add extension if not present
            if not name.endswith(('.txt', '.svg')):
                ext = '.txt' if format_type in ['ascii', 'teletext'] else '.svg'
                name = f"{name}{ext}"
            output_file = output_dir / name
        
        # Ensure parent directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        output_file.write_text(content, encoding='utf-8')
        
        return output_file
    
    def _list_templates(self, format_type: Optional[str] = None) -> str:
        """
        List available templates/palettes/styles.
        
        Args:
            format_type: Optional format filter
            
        Returns:
            Formatted list of templates
        """
        if format_type and format_type not in self.SUPPORTED_FORMATS:
            return f"❌ Error: Unknown format '{format_type}'"
        
        formats_to_list = [format_type] if format_type else self.SUPPORTED_FORMATS
        
        output = ["📋 Available Templates/Palettes/Styles:\n"]
        
        for fmt in formats_to_list:
            try:
                items = self.graphics.list_templates(fmt)
                output.append(f"  {fmt.upper()} ({len(items)}):")
                for item in sorted(items):
                    output.append(f"    - {item}")
                output.append("")
            except GraphicsServiceError:
                output.append(f"  {fmt.upper()}: Service unavailable")
                output.append("")
        
        return "\n".join(output)
    
    def _show_status(self) -> str:
        """Show session statistics."""
        uptime = datetime.now() - self.stats['session_start']
        
        output = [
            "📊 MAKE Command Statistics:",
            f"  Session uptime: {uptime}",
            f"  Total renders: {self.stats['total_renders']}",
            "",
            "  By format:"
        ]
        
        for fmt, count in self.stats['by_format'].items():
            output.append(f"    {fmt}: {count}")
        
        # Graphics service status
        output.append("")
        try:
            health = self.graphics.health_check()
            output.append(f"  Graphics service: ✅ {health['status']} (v{health['version']})")
            output.append(f"  Service uptime: {health['uptime']:.1f}s")
        except GraphicsServiceError:
            output.append("  Graphics service: ❌ Unavailable")
        
        return "\n".join(output)
    
    def _show_help(self, format_type: Optional[str] = None) -> str:
        """
        Show help for MAKE command.
        
        Args:
            format_type: Optional format-specific help
            
        Returns:
            Help text
        """
        if format_type == 'ascii':
            return self._help_ascii()
        elif format_type == 'teletext':
            return self._help_teletext()
        elif format_type == 'svg':
            return self._help_svg()
        elif format_type == 'sequence':
            return self._help_sequence()
        elif format_type == 'flow':
            return self._help_flow()
        else:
            return self._help_general()
    
    def _help_general(self) -> str:
        """General help for MAKE command."""
        return """
MAKE - Unified Graphics Generation (v1.2.15)

USAGE:
  MAKE --format <format> [options] <content>

FORMATS:
  ascii      Template-based ASCII art
  teletext   8-color teletext pages
  svg        AI-assisted SVG diagrams
  sequence   Sequence diagrams (js-sequence)
  flow       Flowcharts (flowchart.js)

COMMON OPTIONS:
  --output <file>   Save to custom location
  --list            List available templates
  --status          Show session statistics
  --help            Show format-specific help

EXAMPLES:
  MAKE --format ascii --template flowchart_vertical --output my_flow.txt
  MAKE --format teletext --palette earth "Welcome to uDOS"
  MAKE --format svg --style technical "system architecture diagram"
  MAKE --format sequence --template api_request
  MAKE --format flow --template decision_flow

For format-specific help:
  MAKE --format <format> --help
  MAKE --list
"""
    
    def _help_ascii(self) -> str:
        """ASCII format help."""
        return """
ASCII Format Help

USAGE:
  MAKE --format ascii --template <name> [options]

OPTIONS:
  --template <name>   Template name (required)
  --data key=value    Variable substitution
  --width N           Max width in characters
  --border            Add border around output
  --output <file>     Save location

EXAMPLES:
  MAKE --format ascii --template flowchart_vertical
  MAKE --format ascii --template progress_bar --data progress=75
  MAKE --format ascii --template org_chart --border

List templates:
  MAKE --format ascii --list
"""
    
    def _help_teletext(self) -> str:
        """Teletext format help."""
        return """
Teletext Format Help

USAGE:
  MAKE --format teletext --palette <name> "<content>"

OPTIONS:
  --palette <name>    Color palette (default: classic)
  --width N           Page width (default: 40)
  --height N          Page height (default: 24)
  --output <file>     Save location

PALETTES:
  classic    High-contrast primary colors
  earth      Warm earthy tones
  terminal   Green phosphor CRT
  amber      Vintage amber CRT

COLOR TAGS:
  {red}text{/red}      Red text
  {green}text{/green}  Green text
  (Also: yellow, blue, magenta, cyan, white, black)

EXAMPLES:
  MAKE --format teletext --palette earth "{green}Status: OK{/green}"
  MAKE --format teletext --palette terminal "System Ready"
"""
    
    def _help_svg(self) -> str:
        """SVG format help."""
        return """
SVG Format Help

USAGE:
  MAKE --format svg --style <name> "<description>"

OPTIONS:
  --style <name>      Style template (default: technical)
  --width N           SVG width (default: 800)
  --height N          SVG height (default: 600)
  --output <file>     Save location

STYLES:
  technical    Clean technical diagrams
  simple       Minimalist black/white
  detailed     Rich colors with gradients

EXAMPLES:
  MAKE --format svg --style technical "3-tier web architecture"
  MAKE --format svg --style simple "user login flowchart"
  MAKE --format svg --style detailed "data processing pipeline"
"""
    
    def _help_sequence(self) -> str:
        """Sequence diagram help."""
        return """
Sequence Diagram Help

USAGE:
  MAKE --format sequence --template <name>
  MAKE --format sequence --source "<syntax>"

OPTIONS:
  --template <name>   Use template from library
  --source "<text>"   Raw js-sequence syntax
  --output <file>     Save location

SYNTAX:
  Title: Diagram Title
  Actor1->Actor2: Message
  Actor2-->Actor1: Response
  Note right of Actor1: Comment

EXAMPLES:
  MAKE --format sequence --template api_request
  MAKE --format sequence --source "User->Server: Login\\nServer-->User: Token"

List templates:
  MAKE --format sequence --list
"""
    
    def _help_flow(self) -> str:
        """Flowchart help."""
        return """
Flowchart Help

USAGE:
  MAKE --format flow --template <name>
  MAKE --format flow --source "<syntax>"

OPTIONS:
  --template <name>   Use template from library
  --source "<text>"   Raw flowchart.js syntax
  --output <file>     Save location

SYNTAX:
  st=>start: Start
  op=>operation: Process
  cond=>condition: Decision?
  e=>end: End
  
  st->op->cond
  cond(yes)->e
  cond(no)->op

EXAMPLES:
  MAKE --format flow --template decision_flow
  MAKE --format flow --template login_process

List templates:
  MAKE --format flow --list
"""


def get_make_handler(**kwargs):
    """Get MakeHandler instance."""
    return MakeHandler(**kwargs)
