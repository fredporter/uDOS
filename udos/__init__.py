"""
uDOS - Offline-first Operating System for Survival Knowledge

A text-based operating system for survival knowledge, mapping, and automation.
Supports offline-first operation with optional AI assistance.

Version: 1.1.9
Author: Fred Porter
License: See LICENSE.txt
"""

__version__ = "1.1.9"
__author__ = "Fred Porter"

# Core imports for convenient access
from core.config import Config

# Service imports
from core.services.asset_manager import AssetManager, get_asset_manager
from core.services.extension_manager import ExtensionManager

# Make commonly used classes available at package level
__all__ = [
    '__version__',
    '__author__',
    'Config',
    'AssetManager',
    'get_asset_manager',
    'ExtensionManager',
]


def get_version():
    """Return the current version of uDOS."""
    return __version__


def get_config():
    """Return a configured Config instance."""
    return Config()

