"""
Server Panel UI Component (v1.2.17)

S-key panel for real-time server monitoring, extension status, and system health.
Integrates with ServerMonitor and ExtensionMonitor services.
"""

from typing import Dict, List, Optional
from core.services.server_monitor import get_server_monitor
from core.services.extension_monitor import get_extension_monitor
from core.utils.column_formatter import ColumnFormatter, ColumnConfig


class ServerPanel:
    """
    TUI panel for server and system monitoring.
    
    Features:
    - Real-time server status display
    - Extension monitoring
    - System health metrics
    - Process management controls
    - Log tail viewer (future)
    """
    
    def __init__(self):
        """Initialize server panel"""
        self.server_monitor = get_server_monitor()
        self.extension_monitor = get_extension_monitor()
        self.current_view = 'servers'  # servers, extensions, health
        self.selected_index = 0
        self.formatter = ColumnFormatter(ColumnConfig(width=70))
        
    def render(self) -> str:
        """
        Render the complete server panel.
        
        Returns:
            Formatted panel content for display
        """
        output = []
        
        # Header
        output.append(self._render_header())
        output.append("")
        
        # Content based on current view
        if self.current_view == 'servers':
            output.extend(self._render_servers())
        elif self.current_view == 'extensions':
            output.extend(self._render_extensions())
        elif self.current_view == 'health':
            output.extend(self._render_health())
        
        # Footer with controls
        output.append("")
        output.append(self._render_footer())
        
        return "\n".join(output)
    
    def _render_header(self) -> str:
        """Render panel header with tabs"""
        tabs = []
        
        # Tab indicators
        tabs.append("[S] Servers" if self.current_view == 'servers' else " S  Servers")
        tabs.append("[E] Extensions" if self.current_view == 'extensions' else " E  Extensions")
        tabs.append("[H] Health" if self.current_view == 'health' else " H  Health")
        
        tab_bar = "  |  ".join(tabs)
        
        lines = []
        lines.append(self.formatter.box_top("uDOS Server Panel"))
        lines.append(self.formatter.box_line(tab_bar, align="left"))
        lines.append(self.formatter.box_separator())
        return "\n".join(lines)
    
    def _render_servers(self) -> List[str]:
        """Render server status view"""
        output = []
        
        # Get server summary
        summary = self.server_monitor.get_summary()
        counts = summary['counts']
        
        # Summary line
        output.append(f"Total: {counts['total']} | Running: {counts['running']} | "
                     f"Stopped: {counts['stopped']} | Core: {counts['core']}")
        output.append("")
        
        # Running servers
        if summary['running']:
            output.append("🟢 RUNNING SERVERS")
            output.append("-" * 70)
            for server in summary['running']:
                status_line = f"  ✓ {server['name']:<20} Port {server['port']:<5} [{server['server']}]"
                output.append(status_line)
            output.append("")
        
        # Stopped servers
        if summary['stopped']:
            output.append("🔴 STOPPED SERVERS")
            output.append("-" * 70)
            for server in summary['stopped'][:5]:  # Limit to 5
                status_line = f"  ✗ {server['name']:<20} Port {server['port']:<5} [{server['server']}]"
                output.append(status_line)
            
            if len(summary['stopped']) > 5:
                output.append(f"  ... and {len(summary['stopped']) - 5} more")
        
        return output
    
    def _render_extensions(self) -> List[str]:
        """Render extension status view"""
        output = []
        
        # Get extension summary
        summary = self.extension_monitor.get_summary()
        counts = summary['counts']
        
        # Summary line
        output.append(f"Total: {counts['total']} | Active: {counts['active']} | "
                     f"Inactive: {counts['inactive']} | Core: {counts['core']}")
        output.append("")
        
        # Active extensions
        if summary['active']:
            output.append("🟢 ACTIVE EXTENSIONS")
            output.append("-" * 70)
            for ext in summary['active']:
                ext_line = f"  ✓ {ext['name']:<30} v{ext['version']:<10} [{ext['id']}]"
                output.append(ext_line)
            output.append("")
        
        # Inactive extensions
        if summary['inactive']:
            output.append("🔴 INACTIVE EXTENSIONS")
            output.append("-" * 70)
            for ext in summary['inactive']:
                ext_line = f"  ✗ {ext['name']:<30} v{ext['version']:<10} [{ext['id']}]"
                output.append(ext_line)
        
        return output
    
    def _render_health(self) -> List[str]:
        """Render system health view"""
        output = []
        
        # Get system health
        health = self.server_monitor.get_system_health()
        
        # Overall status
        status_icon = "🟢" if health['overall'] == 'healthy' else "🟡" if health['overall'] == 'warning' else "🔴"
        output.append(f"{status_icon} OVERALL SYSTEM HEALTH: {health['overall'].upper()}")
        output.append("=" * 70)
        output.append("")
        
        # Memory
        mem = health['memory']
        mem_icon = self._get_status_icon(mem['status'])
        output.append(f"{mem_icon} MEMORY")
        output.append(f"  Total: {mem['total_mb']} MB")
        output.append(f"  Used: {mem['used_mb']} MB ({mem['percent']}%)")
        output.append(f"  Available: {mem['available_mb']} MB")
        output.append(f"  Status: {mem['status']}")
        output.append("")
        
        # Disk
        disk = health['disk']
        disk_icon = self._get_status_icon(disk['status'])
        output.append(f"{disk_icon} DISK SPACE")
        output.append(f"  Total: {disk['total_gb']} GB")
        output.append(f"  Used: {disk['used_gb']} GB ({disk['percent']}%)")
        output.append(f"  Free: {disk['free_gb']} GB")
        output.append(f"  Status: {disk['status']}")
        output.append("")
        
        # Logs
        logs = health['logs']
        logs_icon = self._get_status_icon(logs['status'])
        output.append(f"{logs_icon} LOG FILES")
        output.append(f"  Total size: {logs['total_size_mb']} MB")
        output.append(f"  File count: {logs['file_count']}")
        if logs['largest_file']:
            output.append(f"  Largest: {logs['largest_file']['name']} ({logs['largest_file']['size_mb']} MB)")
        output.append(f"  Status: {logs['status']}")
        output.append("")
        
        # Archive
        archive = health['archive']
        archive_icon = self._get_status_icon(archive['status'])
        output.append(f"{archive_icon} ARCHIVE FOLDERS")
        output.append(f"  Archive count: {archive['archive_count']}")
        output.append(f"  Total size: {archive['total_size_mb']} MB")
        output.append(f"  File count: {archive['file_count']}")
        output.append(f"  Status: {archive['status']}")
        
        return output
    
    def _get_status_icon(self, status: str) -> str:
        """Get emoji icon for status"""
        if status == 'healthy':
            return "🟢"
        elif status == 'warning':
            return "🟡"
        else:
            return "🔴"
    
    def _render_footer(self) -> str:
        """Render panel footer with controls"""
        controls = [
            "[S]ervers",
            "[E]xtensions",
            "[H]ealth",
            "[R]efresh",
            "[ESC] Close"
        ]
        
        return "  ".join(controls)
    
    def switch_view(self, view: str):
        """Switch to a different panel view"""
        if view in ['servers', 'extensions', 'health']:
            self.current_view = view
            self.selected_index = 0
    
    def refresh(self):
        """Refresh all data (rescan extensions, check servers)"""
        self.extension_monitor.scan_extensions()
        # Server monitor checks are real-time, no caching
    
    def handle_key(self, key: str) -> Optional[str]:
        """
        Handle keypress in panel.
        
        Args:
            key: Key pressed
            
        Returns:
            'close' if panel should close, None otherwise
        """
        key_lower = key.lower()
        
        if key_lower == 's':
            self.switch_view('servers')
        elif key_lower == 'e':
            self.switch_view('extensions')
        elif key_lower == 'h':
            self.switch_view('health')
        elif key_lower == 'r':
            self.refresh()
        elif key == '\x1b':  # ESC
            return 'close'
        
        return None


# Global instance
_server_panel_instance: Optional[ServerPanel] = None


def get_server_panel() -> ServerPanel:
    """Get global ServerPanel instance"""
    global _server_panel_instance
    if _server_panel_instance is None:
        _server_panel_instance = ServerPanel()
    return _server_panel_instance
