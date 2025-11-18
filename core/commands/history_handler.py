"""
History Command Handler for uDOS

Manages command history tracking, display, and analysis.
"""

from typing import List


class HistoryCommandHandler:
    """Handler for HISTORY command - displays and manages command history."""

    def __init__(self, logger=None):
        """
        Initialize history handler.

        Args:
            logger: Optional logger instance for accessing session history
        """
        self.logger = logger
        self.history = []

    def handle(self, command: str, args: List[str]) -> str:
        """
        Handle HISTORY command.

        Args:
            command: The subcommand (if any)
            args: Additional arguments

        Returns:
            String output to display
        """
        if not command or command == "LIST":
            return self._show_history()
        elif command == "CLEAR":
            return self._clear_history()
        elif command == "SEARCH":
            query = args[0] if args else ""
            return self._search_history(query)
        elif command == "STATS":
            return self._show_stats()
        else:
            return f"Unknown history command: {command}"

    def _show_history(self) -> str:
        """Display command history."""
        if not self.history:
            return "📜 No command history yet"

        output = ["📜 COMMAND HISTORY", "=" * 50]
        for i, cmd in enumerate(self.history[-20:], 1):  # Last 20 commands
            output.append(f"{i:3d}. {cmd}")

        return "\n".join(output)

    def _clear_history(self) -> str:
        """Clear command history."""
        count = len(self.history)
        self.history.clear()
        return f"✅ Cleared {count} commands from history"

    def _search_history(self, query: str) -> str:
        """Search command history."""
        if not query:
            return "⚠️  Please provide a search query"

        matches = [cmd for cmd in self.history if query.lower() in cmd.lower()]

        if not matches:
            return f"🔍 No matches found for '{query}'"

        output = [f"🔍 SEARCH RESULTS: '{query}'", "=" * 50]
        for i, cmd in enumerate(matches, 1):
            output.append(f"{i:3d}. {cmd}")

        return "\n".join(output)

    def _show_stats(self) -> str:
        """Show history statistics."""
        if not self.history:
            return "📊 No history data"

        total = len(self.history)
        unique = len(set(self.history))

        # Count command frequency
        freq = {}
        for cmd in self.history:
            first_word = cmd.split()[0] if cmd else ""
            freq[first_word] = freq.get(first_word, 0) + 1

        # Top 5 commands
        top_cmds = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]

        output = [
            "📊 HISTORY STATISTICS",
            "=" * 50,
            f"Total commands: {total}",
            f"Unique commands: {unique}",
            f"Repetition rate: {(1 - unique/total)*100:.1f}%",
            "",
            "Top 5 commands:"
        ]

        for cmd, count in top_cmds:
            output.append(f"  {cmd}: {count}x")

        return "\n".join(output)

    def add_to_history(self, command: str):
        """Add a command to history."""
        self.history.append(command)
