"""
TYPO Command Handler
Manages Typo markdown editor server.

Commands:
- TYPO START: Start Typo server
- TYPO STOP: Stop Typo server
- TYPO STATUS: Check server status
- TYPO OPEN: Open Typo editor
- TYPO SLIDES: Open in slideshow mode
"""

from .base_handler import BaseCommandHandler


class TypoCommandHandler(BaseCommandHandler):
    """Handle TYPO command for managing Typo editor server."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._typo_manager = None

    @property
    def typo_manager(self):
        """Lazy load Typo manager."""
        if self._typo_manager is None:
            from core.services.typo_manager import TypoManager
            from core.commands.handler_utils import HandlerUtils
            self._typo_manager = TypoManager(HandlerUtils.get_config())
        return self._typo_manager

    def handle(self, command, params, grid, parser=None):
        """
        Handle TYPO command.

        Args:
            command: Command name (TYPO)
            params: Subcommand and parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        subcommand = params[0].upper()

        if subcommand == "START":
            return self._handle_start(params[1:])
        elif subcommand == "STOP":
            return self._handle_stop()
        elif subcommand == "STATUS":
            return self._handle_status()
        elif subcommand in ["OPEN", "LAUNCH"]:
            return self._handle_open(params[1:])
        elif subcommand == "SLIDES":
            return self._handle_slides()
        elif subcommand == "PREVIEW":
            return self._handle_preview()
        elif subcommand == "HELP":
            return self._show_help()
        else:
            return f"❌ Unknown TYPO subcommand: {subcommand}\n\n" + self._show_help()

    def _handle_start(self, params):
        """Start Typo server."""
        auto_open = '--open' in params or '--browser' in params

        success, msg = self.typo_manager.start_server(
            background=True,
            auto_open=auto_open
        )

        return msg

    def _handle_stop(self):
        """Stop Typo server."""
        success, msg = self.typo_manager.stop_server()
        return msg

    def _handle_status(self):
        """Show Typo server status."""
        status = self.typo_manager.get_status()

        output = "📊 Typo Server Status\n\n"

        if status['installed']:
            output += "✅ Typo: Installed\n"
        else:
            output += "❌ Typo: Not installed\n"
            output += "   Install: ./extensions/setup/setup_typo.sh\n\n"
            return output

        if status['running']:
            output += f"✅ Server: Running\n"
            output += f"🌐 URL: {status['url']}\n"
            output += f"🔌 Port: {status['port']}\n\n"
            output += "💡 Commands:\n"
            output += "   TYPO STOP           - Stop server\n"
            output += "   TYPO OPEN           - Open editor\n"
            output += "   EDIT <file.md>      - Edit markdown file\n"
        else:
            output += "⏸️  Server: Not running\n"
            output += f"🔌 Port: {status['port']} (configured)\n\n"
            output += "💡 Commands:\n"
            output += "   TYPO START          - Start server\n"
            output += "   TYPO START --open   - Start and open browser\n"

        output += f"\n📁 Path: {status['path']}"

        return output

    def _handle_open(self, params):
        """Open Typo editor."""
        mode = 'edit'
        if '--slides' in params:
            mode = 'slides'
        elif '--preview' in params:
            mode = 'preview'

        success, msg = self.typo_manager.open_editor(mode=mode)
        return msg

    def _handle_slides(self):
        """Open Typo in slideshow mode."""
        success, msg = self.typo_manager.open_editor(mode='slides')
        return msg

    def _handle_preview(self):
        """Open Typo in preview mode."""
        success, msg = self.typo_manager.open_editor(mode='preview')
        return msg

    def _show_help(self):
        """Show TYPO command help."""
        return """
📝 TYPO - Markdown Editor Management

COMMANDS:
  TYPO START              Start Typo server
  TYPO START --open       Start and open browser
  TYPO STOP               Stop Typo server
  TYPO STATUS             Check server status
  TYPO OPEN               Open Typo editor
  TYPO SLIDES             Open in slideshow mode
  TYPO PREVIEW            Open in preview mode

EDITOR INTEGRATION:
  EDIT <file.md>          Auto-opens in Typo (if installed)
  EDIT <file.md> --typo   Explicitly use Typo
  EDIT <file.md> --tui    Force terminal editor
  EDIT <file.md> --slides Open in slideshow mode

  VIEW <file.md>          Preview in Typo
  VIEW <file.md> --slides Slideshow mode
  VIEW <file.md> --terminal Terminal view

CONFIGURATION:
  CONFIG SET editor.markdown_default typo
  CONFIG SET editor.web_editor_enabled true
  CONFIG SET editor.typo_port 9000

FEATURES:
  • Live markdown preview
  • Auto-save with File System API
  • Slideshow mode (use --- to create slides)
  • Code execution (JS/TS blocks)
  • Offline-first (local server)

INSTALLATION:
  ./extensions/setup/setup_typo.sh

For more info: https://typo.robino.dev
"""


def register_command():
    """Register TYPO command (for backward compatibility)."""
    handler = TypoCommandHandler()
    return handler.handle
