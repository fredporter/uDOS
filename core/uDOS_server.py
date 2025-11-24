"""
uDOS Server Module - Compatibility Re-export

This module re-exports ServerManager from its actual location in core.network.server.
Provides backward compatibility for imports that reference core.uDOS_server.

Author: uDOS Development Team
Version: 1.1.0
"""

from core.network.server import ServerManager

__all__ = ['ServerManager']
