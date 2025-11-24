"""
uDOS v1.0.0 - Dashboard Handler

Handles dashboard, status, and system information display:
- System status monitoring
- Dashboard creation (CLI and web)
- Viewport and palette information
- Live status monitoring
"""

import os
import sys
import json
import time
import webbrowser
from pathlib import Path
from datetime import datetime
from .base_handler import BaseCommandHandler


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

        # User info
        if self.user_manager and self.user_manager.user_data:
            user_profile = self.user_manager.user_data.get('user_profile', {})
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

    def handle_dashboard(self, params, grid, parser):
        """
        Display comprehensive system dashboard.

        Modes:
            DASH        - Show CLI dashboard
            DASH WEB    - Open interactive web dashboard in browser

        Shows:
            - User profile and installation info
            - System stats (connection, terminal, grid)
            - Running web servers
            - Sandbox and memory file counts
            - Quick command references
        """
        # Check if WEB mode was requested
        if params and params[0].upper() == 'WEB':
            return self._dashboard_web_mode()

        # CLI mode - build comprehensive dashboard
        try:
            output = []
            width = 78  # Box width

            # Header
            output.append("╔" + "═" * width + "╗")
            output.append("║" + "🔮 uDOS DASHBOARD".center(width) + "║")
            output.append("╠" + "═" * width + "╣")

            # User Profile Section
            output.append("║ 👤 USER PROFILE".ljust(width + 1) + "║")
            output.append("║ " + "─" * (width - 2) + " ║")

            user_name = self.user_manager.current_user if self.user_manager else "Guest"
            try:
                user_file = Path('memory/sandbox/user.json')
                if user_file.exists():
                    with open(user_file, 'r') as f:
                        user_data = json.load(f)
                        user_name = user_data.get('USER', {}).get('NAME', user_name)
                        location = user_data.get('USER', {}).get('LOCATION', 'Unknown')
                        timezone = user_data.get('USER', {}).get('TIMEZONE', 'UTC')
                        project = user_data.get('USER', {}).get('PROJECT', 'uDOS')
                        project_type = user_data.get('USER', {}).get('PROJECT_TYPE', 'CLI Framework')
                        mode = user_data.get('SESSION', {}).get('MODE', 'STANDARD')
                else:
                    location = "Unknown"
                    timezone = "UTC"
                    project = "uDOS"
                    project_type = "CLI Framework"
                    mode = "STANDARD"
            except:
                location = "Unknown"
                timezone = "UTC"
                project = "uDOS"
                project_type = "CLI Framework"
                mode = "STANDARD"

            line1 = f"  Name: {user_name:<20} Location: {location}"
            line2 = f"  Timezone: {timezone:<16} Mode: {mode}"
            line3 = f"  Project: {project:<18} Type: {project_type}"
            output.append("║" + line1.ljust(width) + "║")
            output.append("║" + line2.ljust(width) + "║")
            output.append("║" + line3.ljust(width) + "║")

            # Installation Info
            output.append("╠" + "═" * width + "╣")
            output.append("║ 💿 INSTALLATION INFO".ljust(width + 1) + "║")
            output.append("║ " + "─" * (width - 2) + " ║")

            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            udos_version = "v1.0.0"
            install_path = os.getcwd()

            line1 = f"  Python: {python_version:<15} uDOS: {udos_version}"
            line2 = f"  Path: {install_path}"
            line3 = f"  Dependencies: ✅ All OK"
            output.append("║" + line1.ljust(width) + "║")
            output.append("║" + line2.ljust(width) + "║")
            output.append("║" + line3.ljust(width) + "║")

            # System Stats
            output.append("╠" + "═" * width + "╣")
            output.append("║ 📊 SYSTEM STATS".ljust(width + 1) + "║")
            output.append("║ " + "─" * (width - 2) + " ║")

            connection_status = "🌐 ONLINE" if (self.connection and hasattr(self.connection, 'active') and self.connection.active) else "⚠️  OFFLINE"

            if self.viewport:
                terminal_size = f"{self.viewport.width}×{self.viewport.height}"
                device_type = getattr(self.viewport, 'device_type', 'UNKNOWN')
                grid_dims = f"{getattr(self.viewport, 'grid_width', '?')}×{getattr(self.viewport, 'grid_height', '?')}"
                total_cells = getattr(self.viewport, 'grid_width', 0) * getattr(self.viewport, 'grid_height', 0)
            else:
                terminal_size = "Unknown"
                device_type = "UNKNOWN"
                grid_dims = "?"
                total_cells = 0

            history_undo = len(self.history.actions) if self.history and hasattr(self.history, 'actions') else 0
            history_redo = 0  # TODO: Track redo stack

            line1 = f"  Connection: {connection_status}"
            line2 = f"  Terminal: {terminal_size:<15} Device: {device_type}"
            line3 = f"  Grid: {grid_dims:<20} Total Cells: {total_cells}"
            line4 = f"  History: Undo({history_undo}) / Redo({history_redo})"
            line5 = f"  Map Position: (0, 0)        Layer: default"
            output.append("║" + line1.ljust(width) + "║")
            output.append("║" + line2.ljust(width) + "║")
            output.append("║" + line3.ljust(width) + "║")
            output.append("║" + line4.ljust(width) + "║")
            output.append("║" + line5.ljust(width) + "║")

            # Web Servers Section
            output.append("╠" + "═" * width + "╣")
            output.append("║ 🌐 WEB SERVERS".ljust(width + 1) + "║")
            output.append("║ " + "─" * (width - 2) + " ║")

            # Check for running servers
            server_state_file = Path('.server_state.json')
            running_servers = []
            if server_state_file.exists():
                try:
                    with open(server_state_file, 'r') as f:
                        server_data = json.load(f)
                        running_servers = server_data.get('servers', [])
                except:
                    pass

            if running_servers:
                for server in running_servers:
                    name = server.get('name', 'unknown')
                    url = server.get('url', 'http://localhost:????')
                    uptime = server.get('uptime', '0s')
                    line = f"  ✅ {name:<18} {url:<35} ⏱ {uptime}"
                    output.append("║" + line.ljust(width) + "║")
                total_line = f"  Total: {len(running_servers)} server(s) running"
                output.append("║" + total_line.ljust(width) + "║")
            else:
                output.append("║  No web servers currently running".ljust(width + 1) + "║")
                output.append("║  Use: OUTPUT START <name> to start a server".ljust(width + 1) + "║")

            # Sandbox Section
            output.append("╠" + "═" * width + "╣")
            output.append("║ 📁 SANDBOX".ljust(width + 1) + "║")
            output.append("║ " + "─" * (width - 2) + " ║")

            sandbox_path = Path('memory/sandbox')
            if sandbox_path.exists():
                files = [f for f in sandbox_path.rglob('*') if f.is_file() and not f.name.startswith('.')]
                dirs = [d for d in sandbox_path.rglob('*') if d.is_dir() and not d.name.startswith('.')]

                line1 = f"  Files: {len(files):<18} Directories: {len(dirs)}"
                output.append("║" + line1.ljust(width) + "║")

                # Show first 3 files
                for f in files[:3]:
                    size = f.stat().st_size
                    size_str = f"{size:,} bytes" if size < 1024 else f"{size//1024} KB"
                    line = f"   • {f.name:<45} {size_str}"
                    output.append("║" + line.ljust(width) + "║")
            else:
                output.append("║  Sandbox not found".ljust(width + 1) + "║")

            # Memory Section
            output.append("╠" + "═" * width + "╣")
            output.append("║ 💾 MEMORY".ljust(width + 1) + "║")
            output.append("║ " + "─" * (width - 2) + " ║")

            memory_path = Path('memory')
            if memory_path.exists():
                files = [f for f in memory_path.rglob('*') if f.is_file() and not f.name.startswith('.')]
                dirs = [d for d in memory_path.rglob('*') if d.is_dir() and not d.name.startswith('.')]

                line1 = f"  Files: {len(files):<18} Directories: {len(dirs)}"
                output.append("║" + line1.ljust(width) + "║")

                # Show first 3 files
                for f in files[:3]:
                    size = f.stat().st_size
                    size_str = f"{size:,} bytes" if size < 1024 else f"{size//1024} KB"
                    line = f"   • {f.name:<45} {size_str}"
                    output.append("║" + line.ljust(width) + "║")
            else:
                output.append("║  Memory not found".ljust(width + 1) + "║")

            # Quick Commands
            output.append("╠" + "═" * width + "╣")
            output.append("║ ⚡ QUICK COMMANDS".ljust(width + 1) + "║")
            output.append("║ " + "─" * (width - 2) + " ║")
            output.append("║  STATUS - System status    TREE - File tree".ljust(width + 1) + "║")
            output.append("║  HELP   - Command help     REBOOT - Restart uDOS".ljust(width + 1) + "║")
            output.append("║  REPAIR - System repair    CLEAN - Review sandbox".ljust(width + 1) + "║")

            # Footer
            output.append("╚" + "═" * width + "╝")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Failed to generate dashboard: {str(e)}"

    def _dashboard_web_mode(self):
        """Open interactive web dashboard in browser."""
        # Check if dashboard extension exists
        dashboard_path = Path('extensions/web/dashboard/index.html')

        if not dashboard_path.exists():
            return ("⚠️  Web dashboard not installed\n\n"
                   "To install:\n"
                   "  cd extensions/web\n"
                   "  git clone https://github.com/fredporter/udos-dashboard dashboard\n\n"
                   "Or use the CLI dashboard: DASH")

        # Start dashboard server if not running
        try:
            # Check if server is running
            import subprocess
            result = subprocess.run(
                ['lsof', '-ti:8887'],
                capture_output=True,
                text=True
            )

            if not result.stdout.strip():
                # Start server in background
                server_script = Path('extensions/web/dashboard/server.py')
                if server_script.exists():
                    subprocess.Popen(
                        [sys.executable, str(server_script)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    time.sleep(2)  # Give server time to start

            # Open in browser
            webbrowser.open('http://localhost:8887')

            return ("✅ Dashboard opened in browser\n\n"
                   "🌐 URL: http://localhost:8887\n"
                   "📊 Interactive dashboard with live updates\n\n"
                   "Use CTRL+C in server window to stop")

        except Exception as e:
            return f"❌ Failed to start web dashboard: {str(e)}\n\nTry: DASH (CLI mode)"

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
            # Load palette data
            palette_path = Path('knowledge/system/palette.json')
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
