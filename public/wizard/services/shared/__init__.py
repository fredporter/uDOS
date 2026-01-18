"""
Shared utilities for both Wizard Server and Dev Server.

This module contains common functionality:
- Logging
- Authentication
- Rate limiting
- Configuration management
"""

from pathlib import Path

WIZARD_DATA_PATH = Path(__file__).parent.parent.parent.parent / "memory" / "wizard"
WIZARD_CONFIG_PATH = Path(__file__).parent.parent / "config"

# Ensure directories exist
WIZARD_DATA_PATH.mkdir(parents=True, exist_ok=True)
WIZARD_CONFIG_PATH.mkdir(parents=True, exist_ok=True)

__all__ = ["WIZARD_DATA_PATH", "WIZARD_CONFIG_PATH"]
