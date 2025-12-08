"""
LOGS Command Handler v1.1.6

Provides command-line interface for managing the flat directory logging system.

Commands:
- LOGS STATUS - Show logging statistics
- LOGS CLEANUP [--dry-run] - Clean up old logs per retention policy
- LOGS SEARCH <pattern> [--category] [--days] - Search logs
- LOGS ARCHIVE [month] - Archive logs to compressed file
- LOGS HELP - Show help

Author: uDOS Core Team
License: MIT
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from core.services.logging_manager import get_logging_manager


class LogsHandler:
    """Handler for LOGS command family."""

    def __init__(self):
        """Initialize logs handler."""
        self.manager = get_logging_manager()

    def handle(self, command: str, params: List[str]) -> str:
        """
        Handle LOGS command.

        Args:
            command: Full command string
            params: Command parameters

        Returns:
            Command output
        """
        if not params:
            return self._help()

        subcommand = params[0].upper()

        if subcommand == "STATUS":
            return self._status()
        elif subcommand == "CLEANUP":
            return self._cleanup(params[1:])
        elif subcommand == "SEARCH":
            return self._search(params[1:])
        elif subcommand == "ARCHIVE":
            return self._archive(params[1:])
        elif subcommand == "HELP":
            return self._help()
        else:
            return f"❌ Unknown LOGS command: {subcommand}\nUse LOGS HELP for available commands."

    def _status(self) -> str:
        """Show logging system status and statistics."""
        try:
            stats = self.manager.get_log_stats()

            output = ["📊 uDOS Logging System Status v1.1.6", ""]

            # Overall stats
            output.append(f"📁 Total Files: {stats['total_files']}")
            output.append(f"💾 Total Size: {stats['total_size_mb']} MB")
            output.append(f"📅 Date Range: {stats['oldest_log']} → {stats['newest_log']}")
            output.append("")

            # Category breakdown
            output.append("📋 By Category:")
            for category, cat_stats in sorted(stats['by_category'].items()):
                output.append(f"  {category}: {cat_stats['count']} files, {cat_stats['size_mb']} MB")

            output.append("")
            output.append("🛠️  Use LOGS CLEANUP to remove old files")
            output.append("🔍 Use LOGS SEARCH <pattern> to find entries")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error getting log status: {e}"

    def _cleanup(self, params: List[str]) -> str:
        """Clean up old logs based on retention policies."""
        try:
            # Check for dry-run flag
            dry_run = "--dry-run" in params

            if dry_run:
                deleted = self.manager.enforce_retention_policy(dry_run=True)

                if not deleted:
                    return "✅ No logs need cleanup (all within retention policies)"

                output = ["🔍 DRY RUN - Files that would be deleted:", ""]
                total = 0
                for category, count in deleted.items():
                    output.append(f"  {category}: {count} files")
                    total += count

                output.append("")
                output.append(f"Total: {total} files would be deleted")
                output.append("Run LOGS CLEANUP (without --dry-run) to actually delete")

            else:
                deleted = self.manager.enforce_retention_policy(dry_run=False)

                if not deleted:
                    return "✅ No logs needed cleanup (all within retention policies)"

                output = ["🗑️  Log cleanup completed:", ""]
                total = 0
                for category, count in deleted.items():
                    output.append(f"  {category}: {count} files deleted")
                    total += count

                output.append("")
                output.append(f"✅ Total: {total} files deleted")

                # Show updated stats
                stats = self.manager.get_log_stats()
                output.append(f"💾 Remaining: {stats['total_files']} files, {stats['total_size_mb']} MB")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error during cleanup: {e}"

    def _search(self, params: List[str]) -> str:
        """Search logs for pattern."""
        if not params:
            return "❌ LOGS SEARCH requires a pattern\nUsage: LOGS SEARCH <pattern> [--category cat] [--days N]"

        try:
            pattern = params[0]
            category = None
            days = 7  # Default search window

            # Parse optional parameters
            i = 1
            while i < len(params):
                if params[i] == "--category" and i + 1 < len(params):
                    category = params[i + 1]
                    i += 2
                elif params[i] == "--days" and i + 1 < len(params):
                    try:
                        days = int(params[i + 1])
                    except ValueError:
                        return f"❌ Invalid days value: {params[i + 1]}"
                    i += 2
                else:
                    i += 1

            # Perform search
            matches = self.manager.search_logs(pattern, category=category, days=days)

            if not matches:
                search_desc = f"'{pattern}'"
                if category:
                    search_desc += f" in {category} logs"
                search_desc += f" (last {days} days)"
                return f"🔍 No matches found for {search_desc}"

            # Format results
            output = [f"🔍 Search Results for '{pattern}'"]
            if category:
                output[0] += f" in {category} logs"
            output[0] += f" (last {days} days):"
            output.append("")

            # Group by file for better readability
            by_file = {}
            for match in matches:
                file = match['file']
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(match)

            for file, file_matches in sorted(by_file.items()):
                output.append(f"📄 {file} ({len(file_matches)} matches):")
                for match in file_matches[:5]:  # Limit to 5 matches per file
                    line_preview = match['line'][:100] + "..." if len(match['line']) > 100 else match['line']
                    output.append(f"  L{match['line_num']}: {line_preview}")

                if len(file_matches) > 5:
                    output.append(f"  ... and {len(file_matches) - 5} more matches")
                output.append("")

            total_matches = len(matches)
            total_files = len(by_file)
            output.append(f"✅ Found {total_matches} matches in {total_files} files")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error during search: {e}"

    def _archive(self, params: List[str]) -> str:
        """Archive logs for specific month."""
        try:
            # Parse month parameter
            if params:
                month = params[0]
                # Validate format YYYY-MM
                try:
                    datetime.strptime(month + "-01", "%Y-%m-%d")
                except ValueError:
                    return f"❌ Invalid month format: {month}\nUse YYYY-MM format (e.g., 2025-11)"
            else:
                # Default to last month
                last_month = datetime.now().replace(day=1) - timedelta(days=1)
                month = last_month.strftime('%Y-%m')

            # Perform archiving
            archive_path = self.manager.archive_logs(month)

            if archive_path is None:
                return f"📦 No logs found for {month} to archive"

            # Get archive info
            import os
            archive_size = os.path.getsize(archive_path) / (1024 * 1024)

            output = [f"📦 Log Archive Created for {month}"]
            output.append("")
            output.append(f"📄 Archive: {archive_path.name}")
            output.append(f"💾 Size: {archive_size:.2f} MB")
            output.append(f"📁 Location: {archive_path.parent}")
            output.append("")
            output.append("✅ Original log files have been deleted")
            output.append("💡 Archives are kept for 6 months, then auto-deleted")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error during archiving: {e}"

    def _help(self) -> str:
        """Show LOGS command help."""
        help_text = """
📋 LOGS Commands v1.1.6

🔍 Information:
  LOGS STATUS              Show logging system statistics
  LOGS SEARCH <pattern>    Search logs for pattern
    --category <cat>       Limit to category (e.g., system, web, ai)
    --days <N>            Search last N days (default: 7)

🗑️ Maintenance:
  LOGS CLEANUP             Clean up old logs per retention policy
    --dry-run             Show what would be deleted (don't delete)

  LOGS ARCHIVE [month]     Archive logs for month (YYYY-MM)
                           Default: last month

📚 Examples:
  LOGS STATUS
  LOGS SEARCH "error" --category system --days 3
  LOGS CLEANUP --dry-run
  LOGS ARCHIVE 2025-10

📁 Log Categories:
  system-*     System startup, health, errors, audit
  ucode-*      uCODE script execution
  command-*    User command history
  web-*        Web API, dashboard, extensions, WebSocket
  ai-*         AI/Gemini requests and batch generation
  workflow-*   Workflow automation
  mission-*    Mission progress (never auto-deleted)
  extension-*  Third-party extensions
  debug-*      Development/debugging

🛠️ Retention Policies:
  Daily logs: 30 days     Mission logs: Never deleted
  Error logs: 90 days     Debug logs: 7 days
  AI logs: 14 days        Audit logs: 90 days

💡 All logs use flat naming: category-YYYY-MM-DD.log
"""
        return help_text.strip()


def create_logs_handler() -> LogsHandler:
    """Create LOGS command handler."""
    return LogsHandler()


# For testing
if __name__ == "__main__":
    handler = LogsHandler()

    # Test commands
    print("=== LOGS STATUS ===")
    print(handler.handle("LOGS STATUS", ["STATUS"]))

    print("\n=== LOGS HELP ===")
    print(handler.handle("LOGS HELP", ["HELP"]))
