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

    def _load_workflow_state(self):
        """Load current workflow state from memory/workflows/state/current.json."""
        try:
            state_file = PATHS.WORKFLOW_STATE
            if state_file.exists():
                with open(state_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _get_mission_emoji(self, status):
        """Get emoji for mission status."""
        emoji_map = {
            'DRAFT': '📝',
            'ACTIVE': '⚡',
            'PAUSED': '⏸️',
            'COMPLETED': '✅',
            'FAILED': '❌',
            'ARCHIVED': '📦',
            'IDLE': '💤'
        }
        return emoji_map.get(status.upper(), '❓')

    def _format_elapsed_time(self, seconds):
        """Format elapsed time in human-readable format."""
        if not seconds or seconds == 0:
            return "00:00:00"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _build_lifecycle_bar(self, steps, current_step):
        """Build visual lifecycle progress bar."""
        # Find current step index
        try:
            current_idx = steps.index(current_step)
        except ValueError:
            current_idx = -1

        bar = ""
        for i, step in enumerate(steps):
            if i < current_idx:
                bar += "✅ "  # Completed
            elif i == current_idx:
                bar += "⚡ "  # Current
            else:
                bar += "⭕ "  # Pending

            # Add step name (abbreviated)
            bar += step[:3] + " "

        return bar.strip()


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
        """Display a single snapshot of system status with enhanced ASCII dashboard."""
        # Get configuration
        config = get_config()

        # Load workflow state
        workflow_state = self._load_workflow_state()

        # Build comprehensive dashboard
        status = "╔" + "═"*78 + "╗\n"
        status += "║" + "📊 uDOS SYSTEM DASHBOARD".center(78) + "║\n"
        status += "╠" + "═"*78 + "╣\n"

        # User & Location Information
        status += "║ " + "👤 USER PROFILE".ljust(77) + "║\n"
        status += "║ " + "─"*77 + "║\n"

        username = config.username or 'user'
        location = config.location or 'Unknown'
        timezone = config.timezone or 'UTC'

        # Get current time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")

        # Get planet/galaxy info from config or defaults
        planet = config.get('planet', 'Earth')
        galaxy = config.get('galaxy', 'Milky Way')

        status += f"║  Name: {username[:30].ljust(30)} Timezone: {timezone[:30].ljust(30)}  ║\n"
        status += f"║  Location: {location[:66].ljust(66)}  ║\n"
        status += f"║  Planet: {planet[:30].ljust(30)} Galaxy: {galaxy[:30].ljust(30)}  ║\n"
        status += f"║  Time: {current_time.ljust(20)} Date: {current_date.ljust(30)}  ║\n"

        status += "╠" + "═"*78 + "╣\n"

        # Mission & Workflow Status
        status += "║ " + "🚀 MISSION CONTROL".ljust(77) + "║\n"
        status += "║ " + "─"*77 + "║\n"

        if workflow_state and workflow_state.get('current_mission'):
            mission = workflow_state['current_mission']
            mission_status = workflow_state.get('status', 'UNKNOWN')

            # Mission name and status
            mission_name = mission.get('name', 'Unknown')[:40]
            status_emoji = self._get_mission_emoji(mission_status)
            status += f"║  Active: {mission_name.ljust(40)} {status_emoji} {mission_status.ljust(10)} ║\n"

            # Progress bar
            progress = mission.get('progress', 0)
            if isinstance(progress, str) and '/' in progress:
                # Parse "45/55" format
                try:
                    current, total = map(int, progress.split('/'))
                    percent = int((current / total) * 100) if total > 0 else 0
                except:
                    percent = 0
            else:
                percent = int(progress) if isinstance(progress, (int, float)) else 0

            # Visual progress bar
            bar_length = 30
            filled = int((percent / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            status += f"║  Progress: [{bar}] {percent}%".ljust(78) + " ║\n"

            # Mission details
            if 'phase' in mission:
                phase = mission['phase'][:20]
                elapsed = mission.get('elapsed_time', 0)
                elapsed_str = self._format_elapsed_time(elapsed)
                status += f"║  Phase: {phase.ljust(20)} Runtime: {elapsed_str.ljust(20)} ║\n"

            # Lifecycle steps
            lifecycle_steps = ['INIT', 'SETUP', 'EXECUTE', 'MONITOR', 'COMPLETE']
            current_phase = mission.get('phase', 'UNKNOWN').upper()
            lifecycle_bar = self._build_lifecycle_bar(lifecycle_steps, current_phase)
            status += f"║  Lifecycle: {lifecycle_bar.ljust(64)} ║\n"

            # Checkpoint info
            checkpoints_saved = workflow_state.get('checkpoints_saved', 0)
            last_checkpoint = mission.get('last_checkpoint', 'None')
            status += f"║  Checkpoints: {checkpoints_saved} saved".ljust(40)
            status += f"Last: {str(last_checkpoint)[:20].ljust(20)}  ║\n"

        else:
            # No active mission
            status += "║  Status: 💤 No active mission".ljust(78) + " ║\n"

            # Stats
            total = workflow_state.get('missions_total', 0) if workflow_state else 0
            completed = workflow_state.get('missions_completed', 0) if workflow_state else 0
            failed = workflow_state.get('missions_failed', 0) if workflow_state else 0

            if total > 0:
                status += f"║  History: {completed} completed / {failed} failed / {total} total".ljust(78) + " ║\n"

                # Perfect streak
                streak = workflow_state.get('perfect_streak', 0) if workflow_state else 0
                if streak > 0:
                    status += f"║  🔥 Perfect streak: {streak} missions".ljust(78) + " ║\n"

                # XP earned
                xp = workflow_state.get('total_xp_earned', 0) if workflow_state else 0
                if xp > 0:
                    status += f"║  ⭐ Total XP: {xp}".ljust(78) + " ║\n"
            else:
                status += "║  💡 Start a mission: ucode memory/workflows/missions/<mission>.upy".ljust(78) + " ║\n"

        status += "╠" + "═"*78 + "╣\n"

        # Connection & Display Status
        status += "║ " + "🔌 SYSTEM STATUS".ljust(77) + "║\n"
        status += "║ " + "─"*77 + "║\n"

        # Connection status with color-coded indicator
        if self.connection:
            mode = self.connection.get_mode()
            if "ONLINE" in mode:
                conn_icon = "🟢"
                conn_status = "ONLINE"
            else:
                conn_icon = "🔴"
                conn_status = "OFFLINE"
            status += f"║  Connectivity: {conn_icon} {conn_status.ljust(61)} ║\n"

        # Viewport info
        if self.viewport:
            specs = self.viewport.get_grid_specs()
            status += f"║  Display: 📐 {specs['terminal_width']}×{specs['terminal_height']} chars".ljust(78) + " ║\n"
            status += f"║  Device: {specs['device_type'].ljust(68)} ║\n"

        status += "╠" + "═"*78 + "╣\n"

        # Web Extension Servers with visual status bars
        status += "║ " + "🌐 WEB SERVERS".ljust(77) + "║\n"
        status += "║ " + "─"*77 + "║\n"

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

                    status_line = f"  ✅ {srv_name[:16].ljust(16)} {bar} {uptime_str.rjust(8)}"
                    status += f"║{status_line.ljust(78)}║\n"
                    status += f"║     {url.ljust(73)}║\n"

            if not any_running:
                status += "║  ⭕ No servers running" + " "*54 + "║\n"
                status += "║     💡 Use: OUTPUT START teletext (or dashboard/typora)" + " "*17 + "║\n"
        except Exception as e:
            status += "║  📡 Web servers not configured" + " "*46 + "║\n"
            status += "║     💡 Available when extensions loaded" + " "*34 + "║\n"

        status += "╠" + "═"*78 + "╣\n"

        # System health and resources
        status += "║ " + "🏥 SYSTEM HEALTH".ljust(77) + "║\n"
        status += "║ " + "─"*77 + "║\n"

        try:
            from core.services.uDOS_startup import check_python_version, check_dependencies
            py_ok = check_python_version()
            dep_result = check_dependencies()
            dep_ok = dep_result.status == "success"

            py_status = f"✅ {sys.version.split()[0]}" if py_ok else "⚠️  WARNING"
            status += f"║  Python: {py_status.ljust(68)} ║\n"

            dep_status = "✅ All installed" if dep_ok else "⚠️  Issues detected"
            status += f"║  Dependencies: {dep_status.ljust(63)} ║\n"

            # Add system resources
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory().percent
                disk = psutil.disk_usage('.').percent

                cpu_emoji = '✅' if cpu < 70 else '⚠️' if cpu < 90 else '🔴'
                mem_emoji = '✅' if mem < 70 else '⚠️' if mem < 90 else '🔴'
                disk_emoji = '✅' if disk < 80 else '⚠️' if disk < 95 else '🔴'

                status += f"║  CPU: {cpu_emoji} {cpu:5.1f}%  Memory: {mem_emoji} {mem:5.1f}%  Disk: {disk_emoji} {disk:5.1f}%".ljust(78) + " ║\n"
            except ImportError:
                status += "║  Resources: 💡 Install psutil for monitoring" + " "*31 + "║\n"
        except Exception as e:
            status += "║  Health check: ⚠️  Unable to verify" + " "*40 + "║\n"

        # History stats if available
        if self.history:
            undo_count = len(self.history.undo_stack)
            redo_count = len(self.history.redo_stack)
            history_str = f"History: {undo_count} undo / {redo_count} redo available"
            status += f"║  {history_str}".ljust(78) + " ║\n"

        # API Quotas (if resource manager available)
        try:
            from core.services.resource_manager import get_resource_manager
            rm = get_resource_manager()

            status += "╠" + "═"*78 + "╣\n"
            status += "║ " + "🔑 API QUOTAS".ljust(77) + "║\n"
            status += "║ " + "─"*77 + "║\n"

            for provider in ['gemini', 'github']:
                quota_info = rm.check_api_quota(provider)
                if 'error' not in quota_info:
                    percent = quota_info['percent']
                    emoji = "✅" if percent < 50 else "⚠️" if percent < 80 else "🔴"
                    quota_str = f"{provider.upper()}: {emoji} {quota_info['used']}/{quota_info['limit']} ({percent}%)"
                    status += f"║  {quota_str}".ljust(78) + " ║\n"
        except Exception:
            pass  # Skip quota section if not available

        # Archive System Health (v1.1.16)
        try:
            from core.utils.archive_manager import ArchiveManager
            archive_mgr = ArchiveManager()
            health = archive_mgr.get_health_metrics()

            status += "╠" + "═"*78 + "╣\n"
            status += "║ " + "📦 ARCHIVE SYSTEM".ljust(77) + "║\n"
            status += "║ " + "─"*77 + "║\n"

            # Total stats
            total_size_mb = round(health['total_size'] / (1024 * 1024), 2)
            emoji = "✅" if total_size_mb < 100 else "⚠️" if total_size_mb < 500 else "🔴"

            archive_stats = f"Archives: {health['total_archives']}  Files: {health['total_files']}  Size: {emoji} {total_size_mb} MB"
            status += f"║  {archive_stats}".ljust(78) + " ║\n"

            # Warnings
            if health['warnings']:
                for warning in health['warnings'][:2]:  # Show max 2 warnings
                    warn_text = warning[:70]  # Truncate long warnings
                    status += f"║  ⚠️  {warn_text}".ljust(78) + " ║\n"
        except Exception:
            pass  # Skip archive section if not available

        status += "╚" + "═"*78 + "╝\n"
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
            from core.utils.paths import PATHS
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
        Display system dashboard (alias for STATUS command).

        DASH is now an alias for STATUS, showing enhanced ASCII dashboard
        with user info, location, planet, galaxy, time, and system metrics.
        """
        return self._status_snapshot()

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
