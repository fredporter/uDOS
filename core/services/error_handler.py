"""
uDOS Error Handler - Boundary Violation Detection

Detects and handles data architecture boundary violations.

Author: uDOS Development Team
Version: 1.1.0
Feature: 1.1.0.14
"""

from typing import Optional
from core.utils.path_validator import is_writable_path, detect_boundary_violation


class ErrorHandler:
    """Error handling with data boundary validation"""

    def validate_write_operation(self, path: str, command: str = None, root: str = None) -> Optional[str]:
        """
        Validate a write operation respects data boundaries.

        Args:
            path: Path to write to
            command: Command attempting the write
            root: Project root

        Returns:
            Error message if invalid, None if valid
        """
        if not is_writable_path(path, root):
            error = f"Cannot write to read-only system directory"
            if command:
                error = f"{command}: {error}"
            return error

        return None

    def check_boundary_violation(self, source: str, dest: str, root: str = None) -> Optional[str]:
        """
        Check for cross-boundary violations.

        Args:
            source: Source path
            dest: Destination path
            root: Project root

        Returns:
            Error message if violation detected, None if valid
        """
        return detect_boundary_violation(source, dest, root)
