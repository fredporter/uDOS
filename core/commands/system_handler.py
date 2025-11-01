"""
uDOS v1.0.0 - System Command Handler

Handles all system-related commands:
- REPAIR, STATUS, REBOOT, DESTROY
- HELP, VIEWPORT, PALETTE, DASH
- CONFIG, SETTINGS, SETUP
- TREE, CLEAN, WORKSPACE
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from .base_handler import BaseCommandHandler


class SystemCommandHandler(BaseCommandHandler):
    """Handles system administration and configuration commands."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Import services only when needed (lazy loading)
        self._startup_module = None
        self._settings_manager = None
        self._workspace_manager = None
        self._config_manager = None

    @property
    def startup(self):
        """Lazy load startup module."""
        if self._startup_module is None:
            from core import uDOS_startup
            self._startup_module = uDOS_startup
        return self._startup_module

    @property
    def settings_manager(self):
        """Lazy load settings manager."""
        if self._settings_manager is None:
            from core.services.settings_manager import SettingsManager
            self._settings_manager = SettingsManager()
        return self._settings_manager

    @property
    def workspace_manager(self):
        """Lazy load workspace manager."""
        if self._workspace_manager is None:
            from core.services.workspace_manager import WorkspaceManager
            self._workspace_manager = WorkspaceManager()
        return self._workspace_manager

    @property
    def config_manager(self):
        """Lazy load config manager."""
        if self._config_manager is None:
            from core.services.config_manager import ConfigManager
            self._config_manager = ConfigManager()
        return self._config_manager

    def handle(self, command, params, grid, parser):
        """
        Route system commands to appropriate handlers.

        Args:
            command: Command name (e.g., 'REPAIR', 'STATUS')
            params: List of command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result string
        """
        # Map commands to handler methods
        handlers = {
            'BLANK': self.handle_blank,
            'HELP': self.handle_help,
            'STATUS': self.handle_status,
            'REPAIR': self.handle_repair,
            'REBOOT': self.handle_reboot,
            'DESTROY': self.handle_destroy,
            'VIEWPORT': self.handle_viewport,
            'PALETTE': self.handle_palette,
            'DASH': self.handle_dashboard,
            'DASHBOARD': self.handle_dashboard,
            'TREE': self.handle_tree,
            'CLEAN': self.handle_clean,
            'CONFIG': self.handle_config,
            'SETTINGS': self.handle_settings,
            'SETUP': self.handle_setup,
            'WORKSPACE': self.handle_workspace,
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)
        else:
            return self.get_message("ERROR_UNKNOWN_SYSTEM_COMMAND", command=command)

    def handle_blank(self, params, grid, parser):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        return self.get_message("ACTION_SUCCESS_SCREEN_CLEARED")

    def handle_help(self, params, grid, parser):
        """
        Display help information for all commands or a specific command.

        Args:
            params: List with optional command name to get help for
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted help text
        """
        # Load commands data
        commands_file = 'data/system/commands.json'
        try:
            with open(commands_file, 'r') as f:
                commands_data = json.load(f)['COMMANDS']
        except Exception as e:
            return f"❌ Error loading commands: {e}"

        if not params or params[0] == 'ALL':
            # Display organized command list dynamically from COMMANDS.UDO
            help_text = "╔" + "═"*78 + "╗\n"
            help_text += "║" + " "*26 + "📚 uDOS COMMAND REFERENCE" + " "*27 + "║\n"
            help_text += "╠" + "═"*78 + "╣\n"

            # Auto-categorize commands based on their properties
            categories = {
                "📊 System & Info": [],
                "🤖 Assistant & Analysis": [],
                "🔧 System Control": [],
                "📝 File Operations": [],
                "🗺️  Navigation & Mapping": [],
                "🌐 Web Output": [],
                "🎨 Customization": [],
                "⚡ Other": []
            }

            # Build command lookup and auto-categorize
            cmd_lookup = {}
            for cmd_data in commands_data:
                cmd_name = cmd_data.get('NAME', '')
                cmd_lookup[cmd_name] = {
                    'syntax': cmd_data.get('SYNTAX', ''),
                    'desc': cmd_data.get('DESCRIPTION', '')
                }

                # Auto-categorize based on name and uCODE template
                ucode = cmd_data.get('UCODE_TEMPLATE', '')
                if cmd_name in ['STATUS', 'DASH', 'DASHBOARD', 'VIEWPORT', 'PALETTE', 'HELP', 'TREE', 'SETUP']:
                    categories["📊 System & Info"].append(cmd_name)
                elif 'ASSISTANT|' in ucode or cmd_name in ['ASK', 'ANALYZE', 'EXPLAIN', 'GENERATE', 'DEBUG', 'CLEAR']:
                    categories["🤖 Assistant & Analysis"].append(cmd_name)
                elif cmd_name in ['BLANK', 'REBOOT', 'RESTART', 'REPAIR', 'DESTROY', 'UNDO', 'REDO', 'RESTORE', 'CLEAN']:
                    categories["🔧 System Control"].append(cmd_name)
                elif 'FILE|' in ucode or cmd_name in ['EDIT', 'SHOW', 'RUN', 'NEW', 'DELETE', 'COPY', 'MOVE', 'RENAME']:
                    categories["📝 File Operations"].append(cmd_name)
                elif 'MAP' in cmd_name or cmd_name in ['GOTO', 'MOVE', 'LAYER', 'DESCEND', 'ASCEND', 'LOCATE', 'WHERE']:
                    categories["🗺️  Navigation & Mapping"].append(cmd_name)
                elif cmd_name in ['OUTPUT', 'SERVER', 'WEB']:
                    categories["🌐 Web Output"].append(cmd_name)
                elif cmd_name in ['FONT', 'THEME', 'CONFIG', 'SETTINGS']:
                    categories["🎨 Customization"].append(cmd_name)
                else:
                    categories["⚡ Other"].append(cmd_name)

            # Display by category (only show categories with commands)
            for category, commands in categories.items():
                if not commands:
                    continue

                help_text += "║ " + category.ljust(77) + "║\n"
                help_text += "║ " + "─"*77 + "║\n"

                for cmd_name in sorted(commands):
                    if cmd_name in cmd_lookup:
                        cmd_info = cmd_lookup[cmd_name]
                        # Truncate description to fit
                        desc = cmd_info['desc'][:56]
                        help_text += f"║  {cmd_name:<18} - {desc.ljust(56)}║\n"

                help_text += "║" + " "*78 + "║\n"

            # Footer
            help_text += "╠" + "═"*78 + "╣\n"
            help_text += "║  💡 HELP <command_name> for detailed information".ljust(79) + "║\n"
            help_text += "║  📖 Full docs: https://github.com/fredporter/uDOS/wiki".ljust(79) + "║\n"
            help_text += "╚" + "═"*78 + "╝\n"

            return help_text
        else:
            # Display help for a specific command
            cmd_name = params[0].upper()
            for cmd_data in commands_data:
                if cmd_data.get('NAME') == cmd_name:
                    help_text = "╔" + "═"*78 + "╗\n"
                    help_text += f"║  📖 {cmd_name}".ljust(79) + "║\n"
                    help_text += "╠" + "═"*78 + "╣\n"

                    # Description
                    desc = cmd_data.get('DESCRIPTION', 'No description')
                    help_text += "║  Description:".ljust(79) + "║\n"
                    # Word wrap description
                    words = desc.split()
                    line = "║    "
                    for word in words:
                        if len(line) + len(word) + 1 > 77:
                            help_text += line.ljust(79) + "║\n"
                            line = "║    " + word
                        else:
                            line += (" " if len(line) > 4 else "") + word
                    if len(line) > 4:
                        help_text += line.ljust(79) + "║\n"

                    help_text += "║".ljust(79) + "║\n"

                    # Syntax
                    syntax = cmd_data.get('SYNTAX', 'No syntax')
                    help_text += "║  Syntax:".ljust(79) + "║\n"
                    help_text += f"║    {syntax}".ljust(79) + "║\n"

                    # uCODE template if available
                    if 'UCODE_TEMPLATE' in cmd_data:
                        help_text += "║".ljust(79) + "║\n"
                        help_text += "║  uCODE Format:".ljust(79) + "║\n"
                        template = cmd_data.get('UCODE_TEMPLATE', '')
                        help_text += f"║    {template}".ljust(79) + "║\n"

                    help_text += "╚" + "═"*78 + "╝\n"
                    return help_text
            return self.get_message("ERROR_COMMAND_NOT_FOUND", command=cmd_name)

    def handle_status(self, params, grid, parser):
        """
        Display comprehensive system status.
        Supports --live flag for real-time monitoring.

        Args:
            params: Optional parameters including --live flag
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            System status display
        """
        # Check for --live flag
        live_mode = params and ('--live' in params or 'LIVE' in params)

        if live_mode:
            return self._status_live_mode()
        else:
            return self._status_snapshot()

    def _status_snapshot(self):
        """Display a single snapshot of system status."""
        status = "╔" + "═"*68 + "╗\n"
        status += "║" + "📊 uDOS SYSTEM STATUS".center(68) + "║\n"
        status += "╠" + "═"*68 + "╣\n"

        # Connection status with color-coded indicator
        if self.connection:
            mode = self.connection.get_mode()
            if "ONLINE" in mode:
                conn_icon = "🟢"
                conn_status = "ONLINE"
            else:
                conn_icon = "🔴"
                conn_status = "OFFLINE"
            status += f"║ {conn_icon} Connectivity: {conn_status.ljust(54)} ║\n"

        # Viewport info
        if self.viewport:
            specs = self.viewport.get_grid_specs()
            status += f"║ 📐 Display: {specs['terminal_width']}×{specs['terminal_height']} chars".ljust(68) + " ║\n"
            status += f"║    Device Type: {specs['device_type'].ljust(50)} ║\n"

        # User info
        if self.user_manager and self.user_manager.user_data:
            user_profile = self.user_manager.user_data.get('USER_PROFILE', {})
            name = user_profile.get('NAME', 'Unknown')
            status += f"║ 👤 User: {name[:50].ljust(56)} ║\n"

        status += "╠" + "═"*68 + "╣\n"

        # Web Extension Servers with visual status bars
        status += "║ " + "🌐 WEB SERVERS".ljust(67) + "║\n"
        status += "║ " + "─"*67 + "║\n"

        # Import ServerManager if available
        try:
            from core.services.connection_manager import ServerManager
            server_manager = ServerManager()

            any_running = False
            for srv_name, srv_info in server_manager.servers.items():
                if server_manager._is_process_running(srv_info.get('pid')):
                    any_running = True
                    url = srv_info.get('url', 'Unknown')
                    uptime = time.time() - srv_info.get('started_at', time.time())
                    uptime_str = server_manager._format_uptime(uptime)

                    # Create status bar based on uptime
                    bar_length = 10
                    filled = min(bar_length, int((uptime / 3600) * bar_length))  # 1 hour = full bar
                    bar = "█" * filled + "░" * (bar_length - filled)

                    status_line = f" ✅ {srv_name[:16].ljust(16)} {bar} {uptime_str.rjust(8)}"
                    status += f"║{status_line.ljust(68)}║\n"
                    status += f"║    {url.ljust(64)}║\n"

            if not any_running:
                status += "║  ⭕ No servers running".ljust(69) + "║\n"
                status += "║     Use: OUTPUT START <name> to launch".ljust(69) + "║\n"
        except Exception as e:
            status += "║  ⚠️  Server info unavailable".ljust(69) + "║\n"

        status += "╠" + "═"*68 + "╣\n"

        # System health
        status += "║ " + "🏥 SYSTEM HEALTH".ljust(67) + "║\n"
        status += "║ " + "─"*67 + "║\n"

        try:
            from core.uDOS_startup import check_python_version, check_dependencies
            py_ok = check_python_version()
            dep_result = check_dependencies()
            dep_ok = dep_result.status == "success"

            status += f"║  Python: {'✅ OK' if py_ok else '⚠️  WARNING'.ljust(58)} ║\n"
            status += f"║  Dependencies: {'✅ OK' if dep_ok else '⚠️  Issues detected'.ljust(52)} ║\n"
        except Exception:
            status += "║  Health check: ⚠️  Unable to verify".ljust(69) + "║\n"

        # History stats if available
        if self.history:
            undo_count = len(self.history.undo_stack)
            redo_count = len(self.history.redo_stack)
            status += f"║  History: {undo_count} undo / {redo_count} redo available".ljust(69) + "║\n"

        status += "╚" + "═"*68 + "╝\n"
        status += "\n💡 Tip: Use 'STATUS --live' for real-time monitoring\n"

        return status

    def _status_live_mode(self):
        """Display live-updating status (updates every 3 seconds)."""
        import sys
        from datetime import datetime

        try:
            status = "\n🔴 LIVE STATUS MODE (Press Ctrl+C to exit)\n\n"
            status += "Refreshing every 3 seconds...\n\n"
            status += self._get_live_status_display()
            status += "\n\n💡 Press Ctrl+C to return to command prompt\n"
            status += "\n⚠️  Note: Full live mode requires threading. This is a snapshot.\n"

            return status

        except KeyboardInterrupt:
            return "\n\n✅ Exited live status mode\n"

    def _get_live_status_display(self):
        """Get the current status display for live mode."""
        from datetime import datetime

        display = "╔" + "═"*78 + "╗\n"
        display += "║" + f" 🔮 uDOS LIVE STATUS - {datetime.now().strftime('%H:%M:%S')}".ljust(78) + "║\n"
        display += "╠" + "═"*78 + "╣\n"

        # Server status with visual indicators
        display += "║ " + "SERVER STATUS".ljust(77) + "║\n"
        display += "║ " + "─"*77 + "║\n"

        servers = {
            'dashboard': {'name': 'Dashboard', 'port': 8887},
            'font-editor': {'name': 'Font Editor', 'port': 8888},
            'markdown-viewer': {'name': 'Markdown Viewer', 'port': 8889},
            'typo': {'name': 'Typo Editor', 'port': 5173},
            'terminal': {'name': 'Web Terminal', 'port': 8890}
        }

        try:
            from core.services.connection_manager import ServerManager
            server_manager = ServerManager()

            for srv_id, srv_config in servers.items():
                if srv_id in server_manager.servers:
                    srv_info = server_manager.servers[srv_id]
                    if server_manager._is_process_running(srv_info.get('pid')):
                        uptime = time.time() - srv_info.get('started_at', time.time())
                        uptime_str = server_manager._format_uptime(uptime)
                        port = srv_info.get('port', srv_config['port'])

                        indicator = "●"
                        line = f"  {indicator} {srv_config['name'][:20].ljust(20)} [ONLINE]  :{port}  ⏱ {uptime_str}"
                        display += f"║{line.ljust(78)}║\n"
                    else:
                        line = f"  ○ {srv_config['name'][:20].ljust(20)} [OFFLINE] :{srv_config['port']}"
                        display += f"║{line.ljust(78)}║\n"
                else:
                    line = f"  ○ {srv_config['name'][:20].ljust(20)} [OFFLINE] :{srv_config['port']}"
                    display += f"║{line.ljust(78)}║\n"
        except Exception:
            display += "║  ⚠️  Server status unavailable".ljust(79) + "║\n"

        display += "╚" + "═"*78 + "╝"

        return display

    def handle_repair(self, params, grid, parser):
        """
        System health check and repair.
        Supports multiple modes: check, auto, report, pull, upgrade-pip.

        Args:
            params: List with optional component/mode flag
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Repair results or health report
        """
        from core.uDOS_startup import (
            check_system_health,
            repair_system,
            get_health_report,
            quick_health_check,
            repair_git_pull,
            repair_pip_upgrade
        )

        # Normalize component (remove -- prefix if present)
        component = params[0] if params else None
        if component and component.startswith('--'):
            component = component[2:]

        # Parse flags
        check_only = component in ("", "check", None)
        auto_repair = component == "auto"
        full_report = component == "report"
        git_pull = component == "pull"
        pip_upgrade = component == "upgrade-pip"

        # Handle special repair modes
        if git_pull:
            success, message = repair_git_pull(verbose=True)
            if success:
                return f"✅ {message}\n\n💡 Run REBOOT to apply changes"
            else:
                return f"❌ {message}"

        if pip_upgrade:
            success, message = repair_pip_upgrade(verbose=True)
            return f"{'✅' if success else '❌'} {message}"

        # Run full health check
        health = check_system_health(verbose=False)

        # Check-only mode
        if check_only:
            result = "╔" + "═"*58 + "╗\n"
            result += "║" + "🔧 SYSTEM HEALTH CHECK".center(58) + "║\n"
            result += "╚" + "═"*58 + "╝\n\n"

            if health.is_healthy():
                result += "✅ All systems operational\n"
            elif health.has_warnings():
                result += f"⚠️  {health.get_warnings_count()} warning(s) detected\n"
                result += f"💡 Run 'REPAIR --auto' to attempt fixes\n\n"
            else:
                result += f"❌ {health.get_issues_count()} critical issue(s) detected\n"
                result += f"💡 Run 'REPAIR --auto' to attempt fixes\n\n"

            # Show quick summary
            for check in health.checks:
                status_icon = "✅" if check.is_healthy() else ("⚠️ " if check.passed else "❌")
                result += f"{status_icon} {check.name}\n"

                # Show first issue or warning if any
                if check.issues and len(check.issues) > 0:
                    result += f"   └─ {check.issues[0]}\n"
                elif check.warnings and len(check.warnings) > 0:
                    result += f"   └─ {check.warnings[0]}\n"

            return result

        # Full report mode
        if full_report:
            return get_health_report(health, include_warnings=True)

        # Auto-repair mode (default)
        if auto_repair or component == "ALL" or component is None:
            result = "╔" + "═"*58 + "╗\n"
            result += "║" + "🔧 SYSTEM AUTO-REPAIR".center(58) + "║\n"
            result += "╚" + "═"*58 + "╝\n\n"

            # Attempt repairs
            repaired_health = repair_system(health, verbose=False)

            if repaired_health.repaired_issues:
                result += "✅ Repairs applied:\n"
                for repair in repaired_health.repaired_issues:
                    result += f"  • {repair}\n"
                result += "\n"

            # Re-check health
            if repaired_health.is_healthy():
                result += "✅ System health restored\n"
            elif repaired_health.has_warnings():
                result += f"⚠️  {repaired_health.get_warnings_count()} warning(s) remain\n"
                result += "💡 Run 'REPAIR --report' for details\n"
            else:
                result += f"❌ {repaired_health.get_issues_count()} issue(s) remain\n"
                result += "💡 Run 'REPAIR --report' for full diagnostic\n"

            return result

        # Unknown component
        return f"❌ Unknown repair mode: {component}\n\nAvailable modes:\n  REPAIR (auto-fix)\n  REPAIR --check (health check)\n  REPAIR --report (full report)\n  REPAIR --pull (git pull)\n  REPAIR --upgrade-pip (upgrade pip)"

    def handle_reboot(self, params, grid, parser):
        """
        Reboot the uDOS system with pre-flight checks.

        Args:
            params: List (unused)
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Reboot confirmation message
        """
        # Run pre-flight health check
        from core.uDOS_startup import quick_health_check

        result = "╔" + "═"*58 + "╗\n"
        result += "║" + "🔄 REBOOT PRE-FLIGHT CHECK".center(58) + "║\n"
        result += "╚" + "═"*58 + "╝\n\n"

        is_healthy, message = quick_health_check()

        # Check user profile
        if self.user_manager and self.user_manager.user_data:
            user_profile = self.user_manager.user_data.get('USER_PROFILE', {})
            name = user_profile.get('NAME', 'Unknown')
            result += f"✅ User profile OK ({name})\n"
        else:
            result += "⚠️  User profile not loaded\n"

        # Check system health
        if is_healthy and "warning" not in message.lower():
            result += "✅ System health OK\n"
        elif is_healthy:
            result += f"⚠️  {message}\n"
        else:
            result += f"❌ {message}\n"

        # Check viewport
        if self.viewport:
            result += f"✅ Viewport detected ({self.viewport.width}×{self.viewport.height})\n"
        else:
            result += "⚠️  Viewport not detected\n"

        result += "\n🔄 Restarting uDOS...\n"
        result += "💡 All state will be reloaded from disk\n"

        # Set reboot flag
        self.reboot_requested = True

        return result

    def handle_destroy(self, params, grid, parser):
        """
        Destructive reset command with safety confirmations.
        Supports: --all, --env, --reset flags

        Args:
            params: List with optional flags (--all, --env, --reset)
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Destruction confirmation or cancellation message
        """
        import shutil

        # Parse flags
        clear_all = '--all' in params if params else False
        clear_env = '--env' in params if params else False
        reset_git = '--reset' in params if params else False

        # Safety confirmation
        result = "╔" + "═"*58 + "╗\n"
        result += "║" + "⚠️  DESTRUCTIVE OPERATION WARNING".center(58) + "║\n"
        result += "╚" + "═"*58 + "╝\n\n"

        result += "This will DELETE:\n"
        result += "  • sandbox/* (all temporary files)\n"

        if clear_all:
            result += "  • memory/logs/* (all session logs)\n"
            result += "  • output/* (all generated files)\n"

        if clear_env:
            result += "  • .env (API keys and secrets)\n"

        if reset_git:
            result += "  • Complete git reset + fresh clone\n"
            result += "  • ALL uncommitted changes LOST\n"

        result += "\n❌ THIS CANNOT BE UNDONE\n\n"
        result += "To confirm, you must run this command interactively.\n"
        result += "Non-interactive mode does not support DESTROY.\n"

        # In production, this would prompt for confirmation
        # For now, just show what would happen
        result += "\n💡 To execute: Run interactively and confirm\n"

        # Don't actually destroy in this implementation
        # The actual destruction would happen after user confirmation

        return result

    def handle_viewport(self, params, grid, parser):
        """Display viewport visualization."""
        if self.viewport:
            return self.viewport.draw_viewport_map()
        else:
            return "Viewport information not available. Try: REBOOT"

    def handle_palette(self, params, grid, parser):
        """
        Display color palette with visual tests and reference.

        Shows the Polaroid color system with:
        - Color blocks visualization
        - Hex codes and tput numbers
        - Usage descriptions
        - Grayscale gradient
        """
        import json
        from pathlib import Path

        try:
            # Load palette data
            palette_path = Path('data/system/palette.json')
            with open(palette_path, 'r') as f:
                palette_data = json.load(f)

            palette = palette_data['PALETTE']
            colors = palette['COLORS']

            # Build output
            output = []
            output.append("🎨 " + palette['NAME'].upper() + " COLOR PALETTE")
            output.append("=" * 60)
            output.append(f"Name: {palette['NAME']}")
            output.append(f"Version: {palette['VERSION']}")
            output.append(f"Description: {palette['DESCRIPTION']}")
            output.append("")

            # Primary colors section
            output.append("📋 PRIMARY COLORS:")
            output.append("-" * 60)
            for color_id, color_data in colors['PRIMARY'].items():
                # Color block (unicode filled block)
                ansi_code = color_data['ansi'].replace('\\033', '\033')
                reset = '\033[0m'
                block = f"{ansi_code}███{reset}"

                name = color_data['name'].ljust(20)
                tput_hex = f"(tput:{color_data['tput']}) {color_data['hex']}".ljust(20)
                usage = color_data['usage']

                output.append(f"  {block} {name} {tput_hex} - {usage}")

            output.append("")

            # Monochrome section
            output.append("📋 MONOCHROME:")
            output.append("-" * 60)
            for color_id, color_data in colors['MONOCHROME'].items():
                ansi_code = color_data['ansi'].replace('\\033', '\033')
                reset = '\033[0m'
                block = f"{ansi_code}███{reset}"

                name = color_data['name'].ljust(20)
                tput_hex = f"(tput:{color_data['tput']}) {color_data['hex']}".ljust(20)
                usage = color_data['usage']

                output.append(f"  {block} {name} {tput_hex} - {usage}")

            output.append("")

            # Grayscale gradient
            output.append("📋 GRAYSCALE GRADIENT:")
            output.append("-" * 60)
            gradient_line = "  "
            for color_id, color_data in colors['GRAYSCALE'].items():
                ansi_code = color_data['ansi'].replace('\\033', '\033')
                reset = '\033[0m'
                gradient_line += f"{ansi_code}████{reset}"
            output.append(gradient_line)
            output.append("  Black → Darkest → Dark → Medium → Light → Lightest → White")
            output.append("")

            # Visual test blocks
            output.append("🎨 COLOR COMBINATION TESTS:")
            output.append("-" * 60)
            test_line = "  "
            for color_id in ['red', 'green', 'yellow', 'blue', 'purple', 'cyan']:
                color_data = colors['PRIMARY'][color_id]
                ansi_code = color_data['ansi'].replace('\\033', '\033')
                reset = '\033[0m'
                test_line += f"{ansi_code}██{reset} "
            output.append(test_line)
            output.append("")

            output.append("=" * 60)
            output.append("💡 Use: VIEWPORT for terminal capabilities test")
            output.append("💡 Use: REBOOT to see full splash screen with color tests")
            output.append("=" * 60)

            return "\n".join(output)

        except Exception as e:
            return f"❌ Failed to load palette: {str(e)}"

    def handle_dashboard(self, params, grid, parser):
        """
        Display system dashboard.

        TODO: Move this logic from uDOS_commands.py
        This is one of the largest blocks (~400+ lines)
        """
        return "DASHBOARD command - to be refactored"

    def handle_tree(self, params, grid, parser):
        """
        Generate repository tree structure.

        Syntax:
            TREE                 - Full repository tree
            TREE <folder>        - Specific folder (sandbox, memory, knowledge, etc.)
            TREE --depth=N       - Limit depth to N levels

        Returns:
            Tree structure string and saves to structure.txt
        """
        from core.uDOS_tree import generate_repository_tree
        import re

        try:
            # Parse parameters
            target_folder = None
            max_depth = 5

            for param in params:
                if param.startswith('--depth='):
                    try:
                        max_depth = int(param.split('=')[1])
                    except (ValueError, IndexError):
                        return "❌ Invalid depth value. Use: TREE --depth=3"
                elif param.upper() in ['SANDBOX', 'MEMORY', 'KNOWLEDGE', 'HISTORY',
                                       'CORE', 'WIKI', 'EXTENSIONS', 'EXAMPLES']:
                    target_folder = param.lower()

            # Generate tree
            tree_string, tree_path = generate_repository_tree(
                root_path=".",
                output_file="structure.txt",
                target_folder=target_folder,
                max_depth=max_depth
            )

            # Build result message
            output = []
            output.append("🌳 REPOSITORY STRUCTURE")
            output.append("=" * 60)
            if target_folder:
                output.append(f"📁 Folder: {target_folder}/")
            else:
                output.append("📁 Full Repository")
            output.append(f"📏 Max Depth: {max_depth}")
            output.append(f"💾 Saved: {tree_path}")
            output.append("")
            output.append(tree_string)
            output.append("")
            output.append("=" * 60)
            output.append("💡 Use: TREE <folder> to show specific folder")
            output.append("💡 Use: TREE --depth=2 to limit depth")
            output.append("=" * 60)

            return "\n".join(output)

        except Exception as e:
            return f"❌ Failed to generate tree: {str(e)}"

    def handle_clean(self, params, grid, parser):
        """
        Review and clean sandbox files.

        TODO: Move this logic from uDOS_commands.py
        """
        return "CLEAN command - to be refactored"

    def handle_config(self, params, grid, parser):
        """
        Manage .env configuration.

        TODO: Move this logic from uDOS_commands.py
        """
        return "CONFIG command - to be refactored"

    def handle_settings(self, params, grid, parser):
        """
        Manage user settings.

        TODO: Move this logic from uDOS_commands.py
        """
        return "SETTINGS command - to be refactored"

    def handle_setup(self, params, grid, parser):
        """
        Run user setup script.

        TODO: Move this logic from uDOS_commands.py
        """
        return "SETUP command - to be refactored"

    def handle_workspace(self, params, grid, parser):
        """
        Manage workspaces.

        TODO: Move this logic from uDOS_commands.py
        """
        return "WORKSPACE command - to be refactored"
