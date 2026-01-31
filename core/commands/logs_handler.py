"""LOGS command handler - View and search unified logs from all systems."""

from typing import List, Dict, Optional
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.services.unified_logging import get_unified_logger, LogSource, LogLevel

try:
    from core.services.logging_service import get_logger
    logger = get_logger("logs-handler")
except ImportError:
    import logging
    logger = logging.getLogger("logs-handler")


class LogsHandler(BaseCommandHandler):
    """Handler for LOGS command - view and search unified system logs."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle LOGS command.

        Args:
            command: Command name (LOGS)
            params: Subcommand and options
                - LOGS                      Show last 50 entries (all sources)
                - LOGS [--last N]           Show last N entries
                - LOGS --core               Show Core logs only
                - LOGS --wizard             Show Wizard logs only
                - LOGS --goblin             Show Goblin logs only
                - LOGS --level ERROR        Show entries at ERROR level
                - LOGS --category CATEGORY  Show specific category
                - LOGS --stats              Show statistics
                - LOGS --clear              Clear in-memory logs
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with log display
        """
        if not params:
            return self._show_logs(limit=50)
        
        subcommand = params[0].lower()
        
        if subcommand == "--last":
            if len(params) < 2:
                return {"status": "error", "message": "Usage: LOGS --last N"}
            try:
                limit = int(params[1])
                return self._show_logs(limit=limit)
            except ValueError:
                return {"status": "error", "message": f"Invalid number: {params[1]}"}
        
        elif subcommand == "--core":
            return self._show_logs(source=LogSource.CORE, limit=50)
        
        elif subcommand == "--wizard":
            return self._show_logs(source=LogSource.WIZARD, limit=50)
        
        elif subcommand == "--goblin":
            return self._show_logs(source=LogSource.GOBLIN, limit=50)
        
        elif subcommand == "--level":
            if len(params) < 2:
                return {"status": "error", "message": "Usage: LOGS --level DEBUG|INFO|WARNING|ERROR|CRITICAL"}
            level_str = params[1].upper()
            try:
                level = LogLevel[level_str]
                return self._show_logs(level=level, limit=50)
            except KeyError:
                return {"status": "error", "message": f"Invalid level: {level_str}"}
        
        elif subcommand == "--category":
            if len(params) < 2:
                return {"status": "error", "message": "Usage: LOGS --category CATEGORY"}
            category = params[1]
            return self._show_logs(category=category, limit=50)
        
        elif subcommand == "--stats":
            return self._show_stats()
        
        elif subcommand == "--clear":
            return self._clear_logs()
        
        elif subcommand == "help":
            return {"status": "info", "output": self._help_text()}
        
        else:
            return {"status": "error", "message": f"Unknown LOGS subcommand: {subcommand}\nType: LOGS help"}

    def _show_logs(
        self,
        source: Optional[LogSource] = None,
        category: Optional[str] = None,
        level: Optional[LogLevel] = None,
        limit: int = 50
    ) -> Dict:
        """Show filtered logs."""
        from core.tui.output import OutputToolkit

        unified = get_unified_logger()
        entries = unified.filter(source=source, category=category, level=level, limit=limit)
        
        if not entries:
            return {
                "status": "info",
                "output": OutputToolkit.section("📋 LOGS", "No log entries found")
            }
        
        # Format as table
        lines = [
            OutputToolkit.banner("📋 UNIFIED LOGS"),
            f"Showing {len(entries)} of {len(unified.entries)} entries\n"
        ]
        
        # Build table
        headers = ["TIME", "SOURCE", "LEVEL", "CATEGORY", "MESSAGE"]
        rows = []
        for entry in reversed(entries):
            time_str = entry.timestamp.strftime("%H:%M:%S")
            msg = entry.message[:40] + "..." if len(entry.message) > 40 else entry.message
            rows.append([
                time_str,
                entry.source.value,
                entry.level.value,
                entry.category,
                msg
            ])
        
        lines.append(OutputToolkit.table(headers, rows))
        
        # Add filter info
        filter_info = []
        if source:
            filter_info.append(f"source={source.value}")
        if category:
            filter_info.append(f"category={category}")
        if level:
            filter_info.append(f"level={level.value}")
        
        if filter_info:
            lines.append(f"\nFilters: {', '.join(filter_info)}")
        
        lines.append(f"\nTip: LOGS --last 100 | LOGS --wizard | LOGS --category command-dispatch")
        
        logger.info("[LOCAL] Displayed unified logs", extra={"entries": len(entries)})
        
        return {
            "status": "success",
            "output": "\n".join(lines)
        }

    def _show_stats(self) -> Dict:
        """Show logging statistics."""
        from core.tui.output import OutputToolkit

        unified = get_unified_logger()
        stats = unified.stats()
        
        lines = [
            OutputToolkit.banner("📊 LOG STATISTICS"),
            f"Total entries: {stats['total_entries']}",
            f"Uptime: {stats['uptime']:.1f}s",
            ""
        ]
        
        # By source
        if stats['by_source']:
            lines.append("By Source:")
            for source, count in stats['by_source'].items():
                pct = (count / stats['total_entries'] * 100) if stats['total_entries'] > 0 else 0
                lines.append(f"  {source:12} {count:5} ({pct:5.1f}%)")
            lines.append("")
        
        # By level
        if stats['by_level']:
            lines.append("By Level:")
            for level, count in stats['by_level'].items():
                pct = (count / stats['total_entries'] * 100) if stats['total_entries'] > 0 else 0
                lines.append(f"  {level:12} {count:5} ({pct:5.1f}%)")
        
        # Command performance summary
        command_entries = [
            entry for entry in unified.entries
            if entry.category.startswith("command_finish_")
        ]

        if command_entries:
            total_commands = len(command_entries)
            success_count = sum(
                1 for entry in command_entries
                if entry.metadata.get("status") == "success"
            )
            total_duration = sum(
                entry.metadata.get("duration_seconds", 0) for entry in command_entries
            )
            avg_duration = total_duration / total_commands if total_commands else 0

            # Aggregate per command
            per_command = {}
            for entry in command_entries:
                command_name = entry.metadata.get("command", "UNKNOWN")
                duration = entry.metadata.get("duration_seconds", 0)
                status = entry.metadata.get("status", "unknown")
                data = per_command.setdefault(
                    command_name,
                    {"count": 0, "duration": 0.0, "success": 0}
                )
                data["count"] += 1
                data["duration"] += duration
                if status == "success":
                    data["success"] += 1

            # Top slow commands by average duration
            slowest = sorted(
                per_command.items(),
                key=lambda item: (item[1]["duration"] / item[1]["count"]) if item[1]["count"] else 0,
                reverse=True
            )[:5]

            lines.extend(
                [
                    "",
                    "Command Execution Summary:",
                    f"  Total Commands: {total_commands}",
                    f"  Success Rate: {(success_count / total_commands * 100):.1f}%" if total_commands else "  Success Rate: 0.0%",
                    f"  Avg Duration: {avg_duration:.3f}s",
                ]
            )

            if slowest:
                lines.append("")
                lines.append("Top 5 Slowest Commands:")
                for idx, (cmd, data) in enumerate(slowest, start=1):
                    avg = (data["duration"] / data["count"]) if data["count"] else 0
                    lines.append(f"  {idx}. {cmd} ({avg:.3f}s avg, {data['count']} runs)")

        logger.info("[LOCAL] Displayed log statistics")
        
        return {
            "status": "success",
            "output": "\n".join(lines)
        }

    def _clear_logs(self) -> Dict:
        """Clear in-memory logs (file logs are preserved)."""
        from core.tui.output import OutputToolkit

        unified = get_unified_logger()
        count = len(unified.entries)
        unified.entries.clear()
        
        logger.info("[LOCAL] Cleared in-memory logs", extra={"cleared": count})
        
        return {
            "status": "success",
            "output": OutputToolkit.section(
                "✓ LOGS CLEARED",
                f"Cleared {count} in-memory entries\nFile logs in memory/logs/ are preserved"
            )
        }

    def _help_text(self) -> str:
        """Help text for LOGS command."""
        return """
═════════════════════════════════════════════════════════════
LOGS - View Unified Logs from All Systems
═════════════════════════════════════════════════════════════

USAGE:
  LOGS                          Show last 50 entries (all systems)
  LOGS --last N                 Show last N entries
  LOGS --core                   Show Core TUI logs only
  LOGS --wizard                 Show Wizard Server logs only
  LOGS --goblin                 Show Goblin Dev Server logs only
  LOGS --level LEVEL            Filter by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  LOGS --category CATEGORY      Filter by category
  LOGS --stats                  Show log statistics (counts by source/level)
  LOGS --clear                  Clear in-memory logs (files preserved)
  LOGS help                     Show this help

EXAMPLES:
  LOGS                          Last 50 entries
  LOGS --last 100               Last 100 entries
  LOGS --wizard                 Only Wizard logs
  LOGS --level ERROR            Only errors
  LOGS --category ai-routing    Only AI routing logs
  LOGS --stats                  Statistics

LOG FILES:
  Core:      memory/logs/core-{category}-YYYY-MM-DD.log
  Wizard:    memory/logs/unified-wizard-YYYY-MM-DD.log
  Goblin:    memory/logs/unified-goblin-YYYY-MM-DD.log
  Unified:   memory/logs/unified-summary-YYYY-MM-DD.json
  Dev Trace: memory/logs/dev-trace-{category}-YYYY-MM-DD.log

═════════════════════════════════════════════════════════════
"""
