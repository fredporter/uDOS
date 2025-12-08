"""
uDOS PEEK Command Handler

Data collection and parsing from URLs and documents.
Supports: .md, .json, .svg, HTML parsing

Commands:
- PEEK <url>                    # Fetch and parse content from URL
- PEEK <url> --format json      # Output as JSON
- PEEK <url> --save <filename>  # Save to file
- PEEK FILE <path>              # Parse local file

Version: 1.0.0
"""

import requests
from pathlib import Path
from typing import Optional, Dict, Any
import json
from urllib.parse import urlparse
from .base_handler import BaseCommandHandler


class PeekHandler(BaseCommandHandler):
    """Handles data collection and parsing from URLs and documents."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def handle(self, command, params, grid, parser=None):
        """
        Route PEEK commands.

        Args:
            command: Command name (PEEK)
            params: Command parameters
            grid: Grid instance
            parser: Parser instance (optional)

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        # Check if first param is a markdown file - auto-launch in Typo
        first_param = params[0]
        if first_param.endswith('.md') and not first_param.startswith('http'):
            # PEEK filename.md - Open in Typo viewer
            return self._peek_markdown_file(first_param, params[1:])

        # PEEK TYPO <file> - Explicit Typo command (legacy support)
        if first_param.upper() == 'TYPO':
            if len(params) < 2:
                return "❌ Usage: PEEK TYPO <file.md>"
            return self._peek_markdown_file(params[1], params[2:])

        # PEEK FILE <path>
        if first_param.upper() == 'FILE':
            if len(params) < 2:
                return "❌ Usage: PEEK FILE <path>"
            return self._peek_file(params[1:])

        # PEEK <url> [options]
        url = first_param
        options = self._parse_options(params[1:])
        return self._peek_url(url, options)

    def _show_help(self) -> str:
        """Show PEEK command help."""
        return """
╔════════════════════════════════════════════════════════════════════════════╗
║                          🔍 PEEK - Data Collection                         ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Markdown Viewer (Smart):                                                  ║
║    PEEK <file.md>                  # View markdown in Typo web viewer      ║
║    PEEK <file.md> --slides         # View as slideshow                     ║
║    PEEK <file.md> --preview        # Preview mode (read-only)              ║
║                                                                            ║
║  URL Fetching:                                                             ║
║    PEEK <url>                      # Fetch and display content             ║
║    PEEK <url> --format json        # Output as JSON                        ║
║    PEEK <url> --save <filename>    # Save to workspace                     ║
║                                                                            ║
║  File Parsing:                                                             ║
║    PEEK FILE <path>                # Parse local file                      ║
║    PEEK FILE <path> --extract      # Extract structured data               ║
║                                                                            ║
║  Supported Formats:                                                        ║
║    • Markdown (.md) → Typo viewer                                          ║
║    • JSON (.json)                                                          ║
║    • SVG (.svg)                                                            ║
║    • HTML (web pages)                                                      ║
║                                                                            ║
║  Examples:                                                                 ║
║    PEEK README.md                  # View in web browser (Typo)            ║
║    PEEK guide.md --slides          # Present as slideshow                  ║
║    PEEK https://example.com/data.json                                      ║
║    PEEK https://github.com/user/repo/README.md --save readme.md            ║
║    PEEK FILE knowledge/guide.md --extract                                  ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

    def _parse_options(self, params: list) -> Dict[str, Any]:
        """Parse command options."""
        options = {
            'format': 'text',
            'save': None,
            'extract': False
        }

        i = 0
        while i < len(params):
            if params[i] == '--format' and i + 1 < len(params):
                options['format'] = params[i + 1]
                i += 2
            elif params[i] == '--save' and i + 1 < len(params):
                options['save'] = params[i + 1]
                i += 2
            elif params[i] == '--extract':
                options['extract'] = True
                i += 1
            else:
                i += 1

        return options

    def _peek_url(self, url: str, options: Dict[str, Any]) -> str:
        """
        Fetch content from URL.

        Args:
            url: URL to fetch
            options: Parsing options

        Returns:
            Formatted content or error message
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return f"❌ Invalid URL: {url}"

            # Fetch content
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'uDOS-PEEK/1.0'
            })
            response.raise_for_status()

            content = response.text
            content_type = response.headers.get('content-type', '').lower()

            # Parse based on content type
            if 'json' in content_type or url.endswith('.json'):
                data = json.loads(content)
                if options['format'] == 'json':
                    formatted = json.dumps(data, indent=2)
                else:
                    formatted = self._format_json(data)
            elif 'markdown' in content_type or url.endswith('.md'):
                formatted = self._format_markdown(content)
            elif 'svg' in content_type or url.endswith('.svg'):
                formatted = self._format_svg(content)
            else:
                formatted = self._format_html(content)

            # Save if requested
            if options['save']:
                self._save_content(options['save'], formatted)
                return f"✅ Content saved to: {options['save']}\n\n{formatted[:500]}..."

            return formatted

        except requests.RequestException as e:
            return f"❌ Failed to fetch URL: {str(e)}"
        except json.JSONDecodeError:
            return f"❌ Invalid JSON content"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _peek_file(self, params: list) -> str:
        """
        Parse local file.

        Args:
            params: File path and options

        Returns:
            Parsed content or error message
        """
        if not params:
            return "❌ No file specified"

        filepath = Path(params[0])
        options = self._parse_options(params[1:])

        try:
            if not filepath.exists():
                return f"❌ File not found: {filepath}"

            content = filepath.read_text(encoding='utf-8')

            # Parse based on extension
            if filepath.suffix == '.json':
                data = json.loads(content)
                return self._format_json(data)
            elif filepath.suffix == '.md':
                return self._format_markdown(content)
            elif filepath.suffix == '.svg':
                return self._format_svg(content)
            else:
                return content

        except Exception as e:
            return f"❌ Error reading file: {str(e)}"

    def _format_json(self, data: Any) -> str:
        """Format JSON data for display."""
        formatted = json.dumps(data, indent=2)
        lines = formatted.split('\n')
        if len(lines) > 50:
            return '\n'.join(lines[:50]) + f"\n... ({len(lines) - 50} more lines)"
        return formatted

    def _format_markdown(self, content: str) -> str:
        """Format markdown content."""
        lines = content.split('\n')
        if len(lines) > 100:
            return '\n'.join(lines[:100]) + f"\n... ({len(lines) - 100} more lines)"
        return content

    def _format_svg(self, content: str) -> str:
        """Format SVG content."""
        lines = content.split('\n')
        return f"SVG Content ({len(content)} bytes)\n" + '\n'.join(lines[:20])

    def _format_html(self, content: str) -> str:
        """Format HTML content (basic)."""
        # Strip HTML tags for basic display
        import re
        text = re.sub(r'<[^>]+>', '', content)
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        if len(lines) > 50:
            return '\n'.join(lines[:50]) + f"\n... ({len(lines) - 50} more lines)"
        return '\n'.join(lines)

    def _save_content(self, filename: str, content: str) -> None:
        """Save content to file in sandbox."""
        sandbox = Path('memory/sandbox')
        sandbox.mkdir(exist_ok=True, parents=True)
        filepath = sandbox / filename
        filepath.write_text(content, encoding='utf-8')

    def _peek_markdown_file(self, filepath: str, options: list) -> str:
        """
        View markdown file in Typo web viewer.

        Args:
            filepath: Path to markdown file
            options: Additional options (--slides, --preview)

        Returns:
            Success message or error
        """
        from core.services.typo_manager import TypoManager

        # Initialize Typo manager
        config = getattr(self, 'config', None)
        typo = TypoManager(config)

        # Check if file exists
        file_path = Path(filepath)
        if not file_path.exists():
            return f"❌ File not found: {filepath}"

        # Determine mode from options
        mode = 'preview'  # Default to preview for PEEK (read-only)

        if '--slides' in options or '--slideshow' in options:
            mode = 'slides'
        elif '--edit' in options:
            mode = 'edit'

        # Open in Typo
        success, msg = typo.open_file(str(file_path), mode=mode, auto_start=True)

        if success:
            mode_emoji = {
                'preview': '👁️',
                'slides': '📊',
                'edit': '✏️'
            }.get(mode, '👁️')

            return f"{mode_emoji} {msg}"
        else:
            # Fallback to terminal display
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                preview = '\n'.join(lines[:50])

                if len(lines) > 50:
                    preview += f"\n\n... ({len(lines) - 50} more lines)"

                return (f"⚠️  Typo unavailable, showing preview:\n\n"
                       f"{preview}\n\n"
                       f"💡 Install Typo: ./extensions/setup/setup_typo.sh")
            except Exception as e:
                return f"❌ Error: {str(e)}"
