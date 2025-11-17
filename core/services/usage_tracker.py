"""
Usage Tracker Service for v1.0.12
Tracks command usage frequency, timestamps, and context for HELP RECENT feature.
"""

import json
import os
from datetime import datetime
from collections import defaultdict, deque
from pathlib import Path


class UsageTracker:
    """
    Track command usage patterns and provide usage statistics.

    Features:
    - Command frequency tracking
    - Recent command history with timestamps
    - Usage context (parameters, success/failure)
    - Session statistics
    - Persistent storage across sessions
    """

    def __init__(self, data_dir="knowledge/system", max_recent=100):
        """
        Initialize the usage tracker.

        Args:
            data_dir: Directory for storing usage data
            max_recent: Maximum number of recent commands to track
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.data_dir / "usage_tracker.json"

        self.max_recent = max_recent

        # Usage statistics
        self.command_counts = defaultdict(int)  # Command name -> count
        self.recent_commands = deque(maxlen=max_recent)  # Recent command entries
        self.session_commands = []  # Current session commands
        self.success_counts = defaultdict(int)  # Command name -> success count
        self.failure_counts = defaultdict(int)  # Command name -> failure count

        # Load existing data
        self._load_data()

    def track_command(self, command, params=None, success=True, context=None):
        """
        Track a command execution.

        Args:
            command: Command name (e.g., "HELP", "LIST")
            params: List of parameters passed to command
            success: Whether command executed successfully
            context: Additional context dict (optional)
        """
        entry = {
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "params": params or [],
            "success": success,
            "context": context or {}
        }

        # Update statistics
        self.command_counts[command] += 1
        if success:
            self.success_counts[command] += 1
        else:
            self.failure_counts[command] += 1

        # Add to recent commands
        self.recent_commands.append(entry)
        self.session_commands.append(entry)

        # Persist data periodically (every 10 commands)
        if len(self.session_commands) % 10 == 0:
            self._save_data()

    def get_recent_commands(self, limit=10, command_filter=None):
        """
        Get recent commands.

        Args:
            limit: Maximum number of commands to return
            command_filter: Filter by specific command name (optional)

        Returns:
            List of recent command entries
        """
        commands = list(self.recent_commands)

        # Filter by command if specified
        if command_filter:
            commands = [c for c in commands if c["command"].upper() == command_filter.upper()]

        # Return most recent first
        return list(reversed(commands))[:limit]

    def get_most_used(self, limit=10):
        """
        Get most frequently used commands.

        Args:
            limit: Maximum number of commands to return

        Returns:
            List of (command, count) tuples sorted by count
        """
        sorted_commands = sorted(
            self.command_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_commands[:limit]

    def get_command_stats(self, command):
        """
        Get detailed statistics for a specific command.

        Args:
            command: Command name

        Returns:
            Dictionary with command statistics
        """
        command = command.upper()
        total = self.command_counts.get(command, 0)
        successes = self.success_counts.get(command, 0)
        failures = self.failure_counts.get(command, 0)

        # Get recent usage
        recent = self.get_recent_commands(limit=5, command_filter=command)

        # Calculate success rate
        success_rate = (successes / total * 100) if total > 0 else 0

        return {
            "command": command,
            "total_uses": total,
            "successes": successes,
            "failures": failures,
            "success_rate": success_rate,
            "recent_usage": recent
        }

    def get_session_stats(self):
        """
        Get statistics for current session.

        Returns:
            Dictionary with session statistics
        """
        total = len(self.session_commands)
        if total == 0:
            return {
                "total_commands": 0,
                "unique_commands": 0,
                "most_used": [],
                "success_rate": 0
            }

        # Count unique commands
        unique = len(set(c["command"] for c in self.session_commands))

        # Count successes
        successes = sum(1 for c in self.session_commands if c["success"])
        success_rate = (successes / total * 100)

        # Get most used in session
        session_counts = defaultdict(int)
        for cmd in self.session_commands:
            session_counts[cmd["command"]] += 1

        most_used = sorted(
            session_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            "total_commands": total,
            "unique_commands": unique,
            "most_used": most_used,
            "success_rate": success_rate
        }

    def format_recent_commands(self, limit=10):
        """
        Format recent commands for display.

        Args:
            limit: Maximum number of commands to display

        Returns:
            Formatted string for display
        """
        recent = self.get_recent_commands(limit=limit)

        if not recent:
            return "📊 No recent command history available"

        output = ["╔══════════════════════════════════════════════════════════════╗"]
        output.append("║               📊 Recent Command History                      ║")
        output.append("╠══════════════════════════════════════════════════════════════╣")
        output.append("║                                                              ║")

        for i, entry in enumerate(recent, 1):
            # Parse timestamp
            try:
                ts = datetime.fromisoformat(entry["timestamp"])
                time_str = ts.strftime("%H:%M:%S")
            except:
                time_str = "??:??:??"

            # Format command
            cmd = entry["command"]
            params = " ".join(entry["params"]) if entry["params"] else ""
            status = "✓" if entry["success"] else "✗"

            # Build display line
            if params:
                line = f"  {i:2d}. [{time_str}] {status} {cmd} {params}"
            else:
                line = f"  {i:2d}. [{time_str}] {status} {cmd}"

            # Truncate if too long
            if len(line) > 62:
                line = line[:59] + "..."

            output.append(f"║ {line:<60} ║")

        output.append("║                                                              ║")
        output.append("╚══════════════════════════════════════════════════════════════╝")

        return "\n".join(output)

    def format_most_used(self, limit=10):
        """
        Format most used commands for display.

        Args:
            limit: Maximum number of commands to display

        Returns:
            Formatted string for display
        """
        most_used = self.get_most_used(limit=limit)

        if not most_used:
            return "📊 No command usage statistics available"

        output = ["╔══════════════════════════════════════════════════════════════╗"]
        output.append("║               📊 Most Used Commands                          ║")
        output.append("╠══════════════════════════════════════════════════════════════╣")
        output.append("║  Rank  Command             Uses    Success Rate             ║")
        output.append("╠══════════════════════════════════════════════════════════════╣")

        for i, (command, count) in enumerate(most_used, 1):
            stats = self.get_command_stats(command)
            success_rate = stats["success_rate"]

            # Format line
            line = f"  {i:2d}.   {command:<18} {count:>5}    {success_rate:>5.1f}%"
            output.append(f"║{line:<62}║")

        output.append("╚══════════════════════════════════════════════════════════════╝")

        return "\n".join(output)

    def format_session_stats(self):
        """
        Format session statistics for display.

        Returns:
            Formatted string for display
        """
        stats = self.get_session_stats()

        output = ["╔══════════════════════════════════════════════════════════════╗"]
        output.append("║               📊 Current Session Statistics                  ║")
        output.append("╠══════════════════════════════════════════════════════════════╣")
        output.append("║                                                              ║")
        output.append(f"║  Total Commands:     {stats['total_commands']:<40} ║")
        output.append(f"║  Unique Commands:    {stats['unique_commands']:<40} ║")
        output.append(f"║  Success Rate:       {stats['success_rate']:.1f}%{' ' * 36} ║")
        output.append("║                                                              ║")

        if stats["most_used"]:
            output.append("║  Top Commands This Session:                                  ║")
            for cmd, count in stats["most_used"]:
                output.append(f"║    • {cmd:<20} ({count} uses){' ' * (31 - len(str(count)))}║")

        output.append("║                                                              ║")
        output.append("╚══════════════════════════════════════════════════════════════╝")

        return "\n".join(output)

    def clear_session(self):
        """Clear current session commands."""
        self.session_commands = []

    def _load_data(self):
        """Load usage data from disk."""
        if not self.usage_file.exists():
            return

        try:
            with open(self.usage_file, 'r') as f:
                data = json.load(f)

            # Load command counts
            self.command_counts = defaultdict(int, data.get("command_counts", {}))
            self.success_counts = defaultdict(int, data.get("success_counts", {}))
            self.failure_counts = defaultdict(int, data.get("failure_counts", {}))

            # Load recent commands
            recent = data.get("recent_commands", [])
            self.recent_commands = deque(recent, maxlen=self.max_recent)

        except Exception as e:
            print(f"⚠️  Warning: Could not load usage data: {e}")

    def _save_data(self):
        """Save usage data to disk."""
        try:
            data = {
                "command_counts": dict(self.command_counts),
                "success_counts": dict(self.success_counts),
                "failure_counts": dict(self.failure_counts),
                "recent_commands": list(self.recent_commands),
                "last_updated": datetime.now().isoformat()
            }

            with open(self.usage_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"⚠️  Warning: Could not save usage data: {e}")

    def __del__(self):
        """Save data when object is destroyed."""
        try:
            self._save_data()
        except:
            pass
