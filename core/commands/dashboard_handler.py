"""
uDOS v1.5.0 - Dashboard Handler

Handles dashboard, status, and system information display:
- System status monitoring
- Dashboard creation (CLI and web)
- Viewport and palette information
- Live status monitoring
- Unified configuration via ConfigManager (v1.5.0+)
"""

import os
import sys
import json
import time
import webbrowser
from pathlib import Path
from datetime import datetime
from .base_handler import BaseCommandHandler
from core.uDOS_main import get_config  # v1.5.0 Unified configuration


class DashboardHandler(BaseCommandHandler):
    """Handles dashboard, status, and system information operations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

        # User info - enhanced with location
        config = get_config()
        name = config.username or 'user'
        project = config.get('project_name', 'uDOS')
        location = config.location or 'Unknown'
        timezone = config.timezone or 'UTC'

        status += f"║ 👤 User: {name[:20]} ({project[:30]})" + " "*(68-len(f"User: {name[:20]} ({project[:30]})") -4) + "║\n"
        status += f"║ 📍 Location: {location}, {timezone}" + " "*(68-len(f"Location: {location}, {timezone}") -4) + "║\n"

        status += "╠" + "═"*68 + "╣\n"

        # Web Extension Servers with visual status bars
        status += "║ " + "🌐 WEB SERVERS".ljust(67) + "║\n"
        status += "║ " + "─"*67 + "║\n"

        # Import ServerManager if available
        try:
            from extensions.server_manager import ServerManager
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
                status += "║  ⭕ No servers running" + " "*44 + "║\n"
                status += "║     💡 Use: OUTPUT START teletext (or dashboard/typo)" + " "*7 + "║\n"
        except Exception as e:
            status += "║  📡 Web servers not configured" + " "*36 + "║\n"
            status += "║     💡 Available when extensions loaded" + " "*24 + "║\n"

        status += "╠" + "═"*68 + "╣\n"

        # System health and resources
        status += "║ " + "🏥 SYSTEM HEALTH".ljust(67) + "║\n"
        status += "║ " + "─"*67 + "║\n"

        try:
            from core.services.uDOS_startup import check_python_version, check_dependencies
            py_ok = check_python_version()
            dep_result = check_dependencies()
            dep_ok = dep_result.status == "success"

            status += f"║  Python: {'✅ ' + sys.version.split()[0] if py_ok else '⚠️  WARNING'}" + " "*(68-len(f"Python: {'✅ ' + sys.version.split()[0] if py_ok else '⚠️  WARNING'}") -3) + "║\n"
            status += f"║  Dependencies: {'✅ All installed' if dep_ok else '⚠️  Issues detected'}" + " "*(68-len(f"Dependencies: {'✅ All installed' if dep_ok else '⚠️  Issues detected'}") -3) + "║\n"

            # Add system resources
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory().percent
                disk = psutil.disk_usage('.').percent

                cpu_emoji = '✅' if cpu < 70 else '⚠️' if cpu < 90 else '🔴'
                mem_emoji = '✅' if mem < 70 else '⚠️' if mem < 90 else '🔴'
                disk_emoji = '✅' if disk < 80 else '⚠️' if disk < 95 else '🔴'

                status += f"║  CPU: {cpu_emoji} {cpu:.1f}%  Memory: {mem_emoji} {mem:.1f}%  Disk: {disk_emoji} {disk:.1f}%" + " "*(68-len(f"CPU: {cpu_emoji} {cpu:.1f}%  Memory: {mem_emoji} {mem:.1f}%  Disk: {disk_emoji} {disk:.1f}%") -3) + "║\n"
            except ImportError:
                status += "║  Resources: 💡 Install psutil for monitoring" + " "*21 + "║\n"
        except Exception as e:
            status += "║  Health check: ⚠️  Unable to verify" + " "*30 + "║\n"

        # History stats if available
        if self.history:
            undo_count = len(self.history.undo_stack)
            redo_count = len(self.history.redo_stack)
            history_str = f"History: {undo_count} undo / {redo_count} redo available"
            status += f"║  {history_str}" + " "*(68-len(history_str) -3) + "║\n"

        # API Quotas (if resource manager available)
        try:
            from core.services.resource_manager import get_resource_manager
            rm = get_resource_manager()

            status += "╠" + "═"*68 + "╣\n"
            status += "║ " + "🔑 API QUOTAS".ljust(67) + "║\n"
            status += "║ " + "─"*67 + "║\n"

            for provider in ['gemini', 'github']:
                quota_info = rm.check_api_quota(provider)
                if 'error' not in quota_info:
                    percent = quota_info['percent']
                    emoji = "✅" if percent < 50 else "⚠️" if percent < 80 else "🔴"
                    quota_str = f"{provider.upper()}: {emoji} {quota_info['used']}/{quota_info['limit']} ({percent}%)"
                    status += f"║  {quota_str}" + " "*(68-len(quota_str) -3) + "║\n"
        except Exception:
            pass  # Skip quota section if not available

        status += "╚" + "═"*68 + "╝\n"
        status += "\n💡 Tips: STATUS --live (monitoring) | RESOURCE STATUS (detailed quotas)\n"

        return status

    def _status_live_mode(self):
        """Display live-updating status (updates every 3 seconds)."""
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
        display = "╔" + "═"*78 + "╗\n"
        display += "║" + f" 🔮 uDOS LIVE STATUS - {datetime.now().strftime('%H:%M:%S')}".ljust(78) + "║\n"
        display += "╠" + "═"*78 + "╣\n"

        # Server status with visual indicators
        display += "║ " + "SERVER STATUS".ljust(77) + "║\n"
        display += "║ " + "─"*77 + "║\n"

        servers = {
            'typo': {'name': 'Typo Editor', 'port': 5173},
            'dashboard': {'name': 'Dashboard', 'port': 8888},
            'terminal': {'name': 'Web Terminal', 'port': 8889},
            'teletext': {'name': 'Teletext Interface', 'port': 9002},
            'desktop': {'name': 'System Desktop', 'port': 8892},
            'font-editor': {'name': 'Character Editor', 'port': 8891},
            'markdown': {'name': 'Markdown Viewer (Typo)', 'port': 5173}
        }

        try:
            from core.uDOS_server import ServerManager
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

    def handle_dashboard(self, params, grid, parser):
        """
        DEPRECATED: Use STATUS for text dashboard or POKE DASHBOARD for web.

        This command is deprecated in v1.1.12. Use:
        - STATUS - Text-based system dashboard (TUI)
        - POKE DASHBOARD - Web-based dashboard
        """
        return ("⚠️  DASH command deprecated in v1.1.12\n\n"
               "Use instead:\n"
               "  STATUS - Text-based system dashboard\n"
               "  POKE DASHBOARD - Web-based NES dashboard\n\n"
               "Redirecting to STATUS...\n\n" +
               self._status_snapshot())

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
        try:
            # Load palette data from font-system.json
            palette_path = Path('core/data/font-system.json')
            with open(palette_path, 'r') as f:
                font_system = json.load(f)

            palette = font_system['font_system']['color_palette']
            colors = palette['colors']

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
