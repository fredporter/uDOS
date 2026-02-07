"""LOGS command handler - View and search v1.3 logs."""

from typing import List, Dict, Optional
from core.commands.base import BaseCommandHandler

try:
    from core.services.logging_api import get_logger, get_log_manager
    logger = get_logger("core", category="logs", name="logs-handler")
except ImportError:  # pragma: no cover - fallback for minimal runtime
    import logging
    logger = logging.getLogger("logs-handler")


class LogsHandler(BaseCommandHandler):
    """Handler for LOGS command - view and search system logs."""

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
            return self._show_logs(component="core", limit=50)

        elif subcommand == "--wizard":
            return self._show_logs(component="wizard", limit=50)

        elif subcommand == "--goblin":
            return self._show_logs(component="goblin", limit=50)

        elif subcommand == "--level":
            if len(params) < 2:
                return {"status": "error", "message": "Usage: LOGS --level DEBUG|INFO|WARN|ERROR|FATAL"}
            level_str = params[1].lower()
            if level_str not in {"trace", "debug", "info", "warn", "error", "fatal"}:
                return {"status": "error", "message": f"Invalid level: {params[1]}"}
            return self._show_logs(level=level_str, limit=50)

        elif subcommand == "--category":
            if len(params) < 2:
                return {"status": "error", "message": "Usage: LOGS --category CATEGORY"}
            category = params[1]
            return self._show_logs(category=category, limit=50)

        elif subcommand == "--stats":
            return self._show_stats()

        elif subcommand == "--ok":
            return self._show_ok_outputs(limit=50)

        elif subcommand == "--clear":
            return self._clear_logs()

        elif subcommand == "help":
            return {"status": "info", "output": self._help_text()}

        else:
            return {"status": "error", "message": f"Unknown LOGS subcommand: {subcommand}\nType: LOGS help"}

    def _show_logs(
        self,
        component: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 50,
    ) -> Dict:
        """Show filtered logs."""
        from core.tui.output import OutputToolkit

        entries = self._collect_entries(component=component, category=category, level=level, limit=limit)

        if not entries:
            return {
                "status": "info",
                "output": OutputToolkit.section("📋 LOGS", "No log entries found"),
            }

        lines = [
            OutputToolkit.banner("📋 LOGS"),
            f"Showing {len(entries)} entries\n",
        ]

        headers = ["TIME", "SOURCE", "LEVEL", "CATEGORY", "MESSAGE"]
        rows = []
        for entry in reversed(entries):
            ts = entry.get("ts", "")
            time_str = ts.split("T")[-1].split(".")[0] if "T" in ts else ts[:8]
            msg = entry.get("msg", "")
            msg = msg[:40] + "..." if len(msg) > 40 else msg
            rows.append(
                [
                    time_str,
                    entry.get("component", "-"),
                    entry.get("level", "-").upper(),
                    entry.get("category", "-"),
                    msg,
                ]
            )

        lines.append(OutputToolkit.table(headers, rows))

        filter_info = []
        if component:
            filter_info.append(f"component={component}")
        if category:
            filter_info.append(f"category={category}")
        if level:
            filter_info.append(f"level={level.upper()}")

        if filter_info:
            lines.append(f"\nFilters: {', '.join(filter_info)}")

        lines.append("\nTip: LOGS --last 100 | LOGS --wizard | LOGS --category command-routing")

        logger.event("info", "logs.display", "Displayed logs", ctx={"entries": len(entries)})

        return {
            "status": "success",
            "output": "\n".join(lines),
        }

    def _show_stats(self) -> Dict:
        """Show logging statistics."""
        from core.tui.output import OutputToolkit

        stats = self._stats()

        lines = [
            OutputToolkit.banner("📊 LOG STATISTICS"),
            f"Total entries: {stats['total_entries']}",
            "",
        ]

        if stats["by_component"]:
            lines.append("By Source:")
            for source, count in stats["by_component"].items():
                pct = (count / stats["total_entries"] * 100) if stats["total_entries"] > 0 else 0
                lines.append(f"  {source:12} {count:5} ({pct:5.1f}%)")
            lines.append("")

        if stats["by_level"]:
            lines.append("By Level:")
            for level, count in stats["by_level"].items():
                pct = (count / stats["total_entries"] * 100) if stats["total_entries"] > 0 else 0
                lines.append(f"  {level:12} {count:5} ({pct:5.1f}%)")

        command_entries = [
            entry for entry in stats["entries"]
            if entry.get("event") == "command.finish"
        ]

        if command_entries:
            total_commands = len(command_entries)
            success_count = sum(
                1 for entry in command_entries
                if entry.get("ctx", {}).get("status") == "success"
            )
            total_duration = sum(
                entry.get("ctx", {}).get("duration_seconds", 0) for entry in command_entries
            )
            avg_duration = total_duration / total_commands if total_commands else 0

            per_command: Dict[str, Dict[str, float]] = {}
            for entry in command_entries:
                ctx = entry.get("ctx", {})
                command_name = ctx.get("command", "UNKNOWN")
                duration = ctx.get("duration_seconds", 0)
                status = ctx.get("status", "unknown")
                data = per_command.setdefault(
                    command_name,
                    {"count": 0, "duration": 0.0, "success": 0},
                )
                data["count"] += 1
                data["duration"] += duration
                if status == "success":
                    data["success"] += 1

            slowest = sorted(
                per_command.items(),
                key=lambda item: (item[1]["duration"] / item[1]["count"]) if item[1]["count"] else 0,
                reverse=True,
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

        logger.event("info", "logs.stats", "Displayed log statistics")

        return {
            "status": "success",
            "output": "\n".join(lines),
        }

    def _clear_logs(self) -> Dict:
        """Clear in-memory logs (file logs are preserved)."""
        from core.tui.output import OutputToolkit

        count = self._clear_ring()

        logger.event("info", "logs.clear", "Cleared in-memory logs", ctx={"cleared": count})

        return {
            "status": "success",
            "output": OutputToolkit.section(
                "✓ LOGS CLEARED",
                f"Cleared {count} in-memory entries\nFile logs in memory/logs/ are preserved",
            ),
        }

    def _show_ok_outputs(self, limit: int = 50) -> Dict:
        """Show recent OK local output summaries."""
        from core.tui.output import OutputToolkit

        entries = self._collect_entries(category="ok-local-output", limit=limit)

        if not entries:
            return {
                "status": "info",
                "output": OutputToolkit.section(
                    "🧭 OK LOCAL OUTPUTS",
                    "No OK local outputs found yet.\nRun: OK EXPLAIN <file> or OK LOCAL",
                ),
            }

        lines = [
            OutputToolkit.banner("🧭 OK LOCAL OUTPUTS"),
            f"Showing {len(entries)} entries\n",
        ]

        headers = ["TIME", "MODE", "MODEL", "SOURCE", "FILE", "PREVIEW"]
        rows = []
        for entry in reversed(entries):
            ts = entry.get("ts", "")
            time_str = ts.split("T")[-1].split(".")[0] if "T" in ts else ts[:8]
            meta = entry.get("ctx", {}) or {}
            mode = meta.get("mode") or "LOCAL"
            model = meta.get("model") or "-"
            source = meta.get("source") or "-"
            file_path = meta.get("file_path") or ""
            file_short = file_path.split("/")[-1] if file_path else "-"
            preview = meta.get("response_preview") or ""
            preview = (preview[:50] + "...") if len(preview) > 50 else preview
            rows.append([time_str, mode, model, source, file_short, preview])

        lines.append(OutputToolkit.table(headers, rows))
        lines.append("\nTip: OK LOCAL SHOW <id> for full output")

        return {"status": "success", "output": "\n".join(lines)}

    def _help_text(self) -> str:
        """Help text for LOGS command."""
        return """
═════════════════════════════════════════════════════════════
LOGS - View Logs from All Systems
═════════════════════════════════════════════════════════════

USAGE:
  LOGS                          Show last 50 entries (all systems)
  LOGS --last N                 Show last N entries
  LOGS --core                   Only Core logs
  LOGS --wizard                 Only Wizard logs
  LOGS --goblin                 Only Goblin logs
  LOGS --ok                     Show OK local output summaries
  LOGS --level LEVEL            Filter by level (TRACE, DEBUG, INFO, WARN, ERROR, FATAL)
  LOGS --category CATEGORY      Filter by category
  LOGS --stats                  Statistics
  LOGS --clear                  Clear in-memory logs (files preserved)
  LOGS help                     Show this help

EXAMPLES:
  LOGS                          Last 50 entries
  LOGS --last 100               Last 100 entries
  LOGS --wizard                 Only Wizard logs
  LOGS --ok                     Recent OK local output summaries
  LOGS --level ERROR            Only errors
  LOGS --category command       Only command logs
  LOGS --stats                  Statistics

LOG FILES:
  Core:      memory/logs/udos/core/{name}-YYYY-MM-DD.jsonl
  Wizard:    memory/logs/udos/wizard/{name}-YYYY-MM-DD.jsonl
  Scripts:   memory/logs/udos/scripts/{name}-YYYY-MM-DD.jsonl

═════════════════════════════════════════════════════════════
"""

    def _collect_entries(
        self,
        component: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        manager = get_log_manager()
        entries = list(manager.ring())
        if component:
            entries = [entry for entry in entries if entry.get("component") == component]
        if category:
            entries = [entry for entry in entries if entry.get("category") == category]
        if level:
            entries = [entry for entry in entries if entry.get("level") == level]
        if limit:
            entries = entries[-limit:]
        return entries

    def _clear_ring(self) -> int:
        manager = get_log_manager()
        return manager.clear_ring()

    def _stats(self) -> Dict[str, Any]:
        manager = get_log_manager()
        entries = list(manager.ring())
        by_component: Dict[str, int] = {}
        by_level: Dict[str, int] = {}
        for entry in entries:
            comp = entry.get("component", "unknown")
            by_component[comp] = by_component.get(comp, 0) + 1
            level = entry.get("level", "unknown").upper()
            by_level[level] = by_level.get(level, 0) + 1
        return {
            "total_entries": len(entries),
            "by_component": by_component,
            "by_level": by_level,
            "entries": entries,
        }
