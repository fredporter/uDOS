"""
uDOS Configuration Package (v1.5.0+)

Provides unified configuration management across .env, user.json, and runtime state.
"""

from .config_manager import ConfigManager, get_config_manager, reset_config_manager

__all__ = ['ConfigManager', 'get_config_manager', 'reset_config_manager']
