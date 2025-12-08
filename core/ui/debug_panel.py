"""
Debug Panel (v1.2.19)

Live log viewer with error highlighting, filtering, and export.
L-key access for debugging.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import re


class LogEntry:
    """Represents a single log entry"""
    
    def __init__(self, timestamp: str, level: str, module: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.module = module
        self.message = message
    
    def matches_filter(self, level_filter: Optional[str] = None, 
                      module_filter: Optional[str] = None,
                      search_term: Optional[str] = None) -> bool:
        """Check if entry matches filters"""
        if level_filter and self.level != level_filter:
            return False
        
        if module_filter and module_filter.lower() not in self.module.lower():
            return False
        
        if search_term and search_term.lower() not in self.message.lower():
            return False
        
        return True
    
    def format(self, highlight_errors: bool = True) -> str:
        """Format log entry for display"""
        # Level indicator
        level_icons = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️ ',
            'WARNING': '⚠️ ',
            'ERROR': '❌',
            'CRITICAL': '🔥'
        }
        icon = level_icons.get(self.level, '  ')
        
        # Timestamp (short format)
        time_str = self.timestamp[-12:-4] if len(self.timestamp) > 12 else self.timestamp
        
        # Module (truncate if long)
        module_str = self.module[:20] if len(self.module) > 20 else self.module
        
        # Highlight errors
        if highlight_errors and self.level in ['ERROR', 'CRITICAL']:
            return f"{icon} {time_str} [{module_str}] {self.message}"
        else:
            return f"{icon} {time_str} [{module_str}] {self.message}"


class DebugPanel:
    """
    TUI panel for live log viewing and debugging.
    
    Features:
    - Live log viewer (tail -f style)
    - Error highlighting
    - Filter by level/module
    - Search within logs
    - Export/save log sections
    """
    
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def __init__(self):
        """Initialize debug panel"""
        from core.utils.paths import PATHS
        self.logs_dir = PATHS.MEMORY / 'logs'
        
        # State
        self.log_entries: List[LogEntry] = []
        self.current_log_file = self.logs_dir / 'dev.log'
        self.level_filter: Optional[str] = None
        self.module_filter: Optional[str] = None
        self.search_term: Optional[str] = None
        self.auto_scroll = True
        self.scroll_offset = 0
        self.max_lines = 100  # Keep last N lines in memory
        
        # Load initial logs
        self._load_logs()
    
    def _load_logs(self):
        """Load logs from current log file"""
        if not self.current_log_file.exists():
            return
        
        try:
            # Read last N lines
            with open(self.current_log_file, 'r') as f:
                lines = f.readlines()[-self.max_lines:]
            
            # Parse log entries
            self.log_entries = []
            for line in lines:
                entry = self._parse_log_line(line)
                if entry:
                    self.log_entries.append(entry)
        except Exception:
            pass
    
    def _parse_log_line(self, line: str) -> Optional[LogEntry]:
        """Parse a log line into LogEntry"""
        # Expected format: TIMESTAMP [LEVEL] module: message
        # Example: 2025-12-07 14:30:45 [INFO] core.commands: Command executed
        
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+([^:]+):\s+(.+)'
        match = re.match(pattern, line.strip())
        
        if match:
            timestamp, level, module, message = match.groups()
            return LogEntry(timestamp, level, module, message)
        
        return None
    
    def refresh_logs(self):
        """Reload logs from file (for live updates)"""
        self._load_logs()
    
    def render(self) -> str:
        """Render debug panel"""
        output = []
        
        # Header
        output.append("╔══ DEBUG PANEL ══╗")
        output.append("")
        
        # Current log file
        output.append(f"Log File: {self.current_log_file.name}")
        
        # Filters status
        filters = []
        if self.level_filter:
            filters.append(f"Level: {self.level_filter}")
        if self.module_filter:
            filters.append(f"Module: {self.module_filter}")
        if self.search_term:
            filters.append(f"Search: {self.search_term}")
        
        if filters:
            output.append(f"Filters: {' | '.join(filters)}")
        
        output.append("=" * 70)
        output.append("")
        
        # Log entries
        output.extend(self._render_log_entries())
        
        # Footer
        output.append("")
        output.append(self._render_footer())
        
        return "\n".join(output)
    
    def _render_log_entries(self) -> List[str]:
        """Render filtered log entries"""
        output = []
        
        # Filter entries
        filtered = [
            entry for entry in self.log_entries
            if entry.matches_filter(self.level_filter, self.module_filter, self.search_term)
        ]
        
        if not filtered:
            output.append("  (no log entries match filters)")
            return output
        
        # Apply scroll offset
        visible_entries = filtered[self.scroll_offset:self.scroll_offset + 20]
        
        # Render entries
        for entry in visible_entries:
            output.append(entry.format(highlight_errors=True))
        
        # Scroll indicators
        if self.scroll_offset > 0:
            output.insert(0, "  ▲ (more above)")
        if self.scroll_offset + 20 < len(filtered):
            output.append("  ▼ (more below)")
        
        return output
    
    def _render_footer(self) -> str:
        """Render footer with controls"""
        total = len(self.log_entries)
        filtered = len([
            e for e in self.log_entries
            if e.matches_filter(self.level_filter, self.module_filter, self.search_term)
        ])
        
        controls = [
            f"{filtered}/{total} entries",
            "[R]efresh",
            "[F]ilter",
            "[C]lear Filters",
            "[E]xport",
            "↑↓ Scroll",
            "[ESC] Close"
        ]
        
        return "  ".join(controls)
    
    def scroll_up(self):
        """Scroll log view up"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            self.auto_scroll = False
    
    def scroll_down(self):
        """Scroll log view down"""
        filtered = [
            e for e in self.log_entries
            if e.matches_filter(self.level_filter, self.module_filter, self.search_term)
        ]
        if self.scroll_offset + 20 < len(filtered):
            self.scroll_offset += 1
    
    def set_level_filter(self, level: Optional[str]):
        """Set log level filter"""
        if level and level.upper() in self.LOG_LEVELS:
            self.level_filter = level.upper()
        else:
            self.level_filter = None
        
        self.scroll_offset = 0
    
    def set_module_filter(self, module: Optional[str]):
        """Set module filter"""
        self.module_filter = module if module else None
        self.scroll_offset = 0
    
    def set_search_term(self, term: Optional[str]):
        """Set search term"""
        self.search_term = term if term else None
        self.scroll_offset = 0
    
    def clear_filters(self):
        """Clear all filters"""
        self.level_filter = None
        self.module_filter = None
        self.search_term = None
        self.scroll_offset = 0
    
    def export_logs(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Export filtered logs to file"""
        if output_path is None:
            # Default export location
            from core.utils.paths import PATHS
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = PATHS.MEMORY_DOCS / f"debug_export_{timestamp}.log"
        
        try:
            # Get filtered entries
            filtered = [
                entry for entry in self.log_entries
                if entry.matches_filter(self.level_filter, self.module_filter, self.search_term)
            ]
            
            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(f"# Debug Log Export\n")
                f.write(f"# Exported: {datetime.now().isoformat()}\n")
                f.write(f"# Source: {self.current_log_file}\n")
                if self.level_filter:
                    f.write(f"# Level Filter: {self.level_filter}\n")
                if self.module_filter:
                    f.write(f"# Module Filter: {self.module_filter}\n")
                if self.search_term:
                    f.write(f"# Search: {self.search_term}\n")
                f.write("\n")
                
                for entry in filtered:
                    f.write(f"{entry.timestamp} [{entry.level}] {entry.module}: {entry.message}\n")
            
            return {
                'success': True,
                'path': str(output_path),
                'entries': len(filtered)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def switch_log_file(self, filename: str) -> Dict[str, Any]:
        """Switch to a different log file"""
        log_path = self.logs_dir / filename
        
        if not log_path.exists():
            return {'success': False, 'error': f'Log file not found: {filename}'}
        
        self.current_log_file = log_path
        self._load_logs()
        self.scroll_offset = 0
        
        return {'success': True, 'file': filename, 'entries': len(self.log_entries)}
    
    def get_available_log_files(self) -> List[str]:
        """Get list of available log files"""
        if not self.logs_dir.exists():
            return []
        
        return sorted([f.name for f in self.logs_dir.glob('*.log')])
    
    def get_error_count(self) -> Dict[str, int]:
        """Get count of errors by level"""
        counts = {level: 0 for level in self.LOG_LEVELS}
        
        for entry in self.log_entries:
            if entry.level in counts:
                counts[entry.level] += 1
        
        return counts
    
    def get_recent_errors(self, count: int = 10) -> List[LogEntry]:
        """Get most recent error/critical entries"""
        errors = [
            entry for entry in self.log_entries
            if entry.level in ['ERROR', 'CRITICAL']
        ]
        return errors[-count:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get debug panel summary"""
        error_counts = self.get_error_count()
        
        return {
            'log_file': str(self.current_log_file),
            'total_entries': len(self.log_entries),
            'error_counts': error_counts,
            'filters_active': bool(self.level_filter or self.module_filter or self.search_term),
            'auto_scroll': self.auto_scroll
        }


# Global instance
_debug_panel: Optional[DebugPanel] = None


def get_debug_panel() -> DebugPanel:
    """Get global DebugPanel instance"""
    global _debug_panel
    if _debug_panel is None:
        _debug_panel = DebugPanel()
    return _debug_panel
