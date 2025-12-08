"""
OK Context Manager - Workspace Awareness for OK Assistant
Tracks workspace state, location, recent commands, and errors

Features:
- Workspace state detection (current directory, active files)
- TILE location tracking
- Command history (last 10 commands)
- Error message capture
- Git status integration
- File context (current file, recent edits)

Version: 1.0.0 (v1.2.21)
Author: Fred Porter
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from core.config import Config


class OKContextManager:
    """Context manager for OK assistant workspace awareness"""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize context manager.

        Args:
            config: Config instance (auto-creates if None)
        """
        self.config = config or Config()
        self.project_root = self.config.project_root

        # Context state
        self.workspace_path: Optional[Path] = None
        self.current_file: Optional[Path] = None
        self.tile_location: Optional[str] = None
        self.command_history: List[Dict[str, Any]] = []
        self.error_messages: List[str] = []
        self.git_status: Optional[Dict[str, Any]] = None

    def update_workspace(self, path: Optional[Path] = None) -> None:
        """
        Update workspace path context.

        Args:
            path: Workspace path (uses cwd if None)
        """
        if path is None:
            path = Path.cwd()

        self.workspace_path = path

    def update_file(self, file_path: Optional[Path] = None) -> None:
        """
        Update current file context.

        Args:
            file_path: Current file path
        """
        self.current_file = file_path

    def update_tile_location(self, tile_code: Optional[str] = None) -> None:
        """
        Update TILE location context.

        Args:
            tile_code: TILE code (e.g., "AA340-100")
        """
        self.tile_location = tile_code

    def add_command(self, command: str, status: str = "success", output: Optional[str] = None) -> None:
        """
        Add command to history (keep last 10).

        Args:
            command: Command text
            status: success | error | warning
            output: Command output (optional)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "status": status,
            "output": output
        }

        self.command_history.append(entry)

        # Keep last 10 commands
        if len(self.command_history) > 10:
            self.command_history = self.command_history[-10:]

    def add_error(self, error_message: str) -> None:
        """
        Add error message to context (keep last 5).

        Args:
            error_message: Error message text
        """
        self.error_messages.append(error_message)

        # Keep last 5 errors
        if len(self.error_messages) > 5:
            self.error_messages = self.error_messages[-5:]

    def update_git_status(self) -> None:
        """Update git status for current workspace."""
        try:
            # Run git status --short
            result = subprocess.run(
                ['git', 'status', '--short'],
                cwd=self.workspace_path or self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse git status output
                lines = result.stdout.strip().split('\n')
                status = {
                    "modified": [],
                    "added": [],
                    "deleted": [],
                    "untracked": []
                }

                for line in lines:
                    if not line.strip():
                        continue

                    # Parse status format: "XY filename"
                    if len(line) >= 3:
                        code = line[:2]
                        filename = line[3:].strip()

                        if code.startswith('M'):
                            status["modified"].append(filename)
                        elif code.startswith('A'):
                            status["added"].append(filename)
                        elif code.startswith('D'):
                            status["deleted"].append(filename)
                        elif code.startswith('?'):
                            status["untracked"].append(filename)

                self.git_status = status
            else:
                self.git_status = None

        except Exception:
            # Not a git repo or git not available
            self.git_status = None

    def get_context(self) -> Dict[str, Any]:
        """
        Get complete context snapshot.

        Returns:
            Dictionary with all context data
        """
        # Update git status
        self.update_git_status()

        context = {
            "timestamp": datetime.now().isoformat(),
            "workspace": {
                "path": str(self.workspace_path) if self.workspace_path else None,
                "current_file": str(self.current_file) if self.current_file else None,
                "tile_location": self.tile_location
            },
            "history": {
                "commands": self.command_history[-5:],  # Last 5 commands
                "errors": self.error_messages
            },
            "git": self.git_status
        }

        return context

    def get_context_summary(self) -> str:
        """
        Get human-readable context summary.

        Returns:
            Formatted context string
        """
        context = self.get_context()
        lines = []

        # Workspace info
        if context["workspace"]["path"]:
            lines.append(f"📁 Workspace: {context['workspace']['path']}")

        if context["workspace"]["current_file"]:
            lines.append(f"📄 File: {context['workspace']['current_file']}")

        if context["workspace"]["tile_location"]:
            lines.append(f"📍 Location: {context['workspace']['tile_location']}")

        # Recent commands
        if context["history"]["commands"]:
            lines.append("\n📜 Recent commands:")
            for cmd in context["history"]["commands"]:
                status_icon = "✅" if cmd["status"] == "success" else "❌"
                lines.append(f"  {status_icon} {cmd['command']}")

        # Recent errors
        if context["history"]["errors"]:
            lines.append("\n⚠️  Recent errors:")
            for error in context["history"]["errors"]:
                lines.append(f"  • {error}")

        # Git status
        if context["git"]:
            git = context["git"]
            if any(git.values()):
                lines.append("\n🔧 Git status:")
                if git["modified"]:
                    lines.append(f"  M: {', '.join(git['modified'][:3])}")
                if git["added"]:
                    lines.append(f"  A: {', '.join(git['added'][:3])}")
                if git["untracked"]:
                    lines.append(f"  ?: {', '.join(git['untracked'][:3])}")

        return '\n'.join(lines) if lines else "No context available"


# Singleton instance
_context_manager: Optional[OKContextManager] = None


def get_ok_context_manager() -> OKContextManager:
    """
    Get singleton OK context manager instance.

    Returns:
        OKContextManager instance
    """
    global _context_manager
    if _context_manager is None:
        _context_manager = OKContextManager()
    return _context_manager
