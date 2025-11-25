"""
uDOS Server Manager Extension
Web-based extension server management (GUI/API)
Moved from core/network to extensions/core as it manages GUI/web servers
"""

from .server import ServerManager

__all__ = ['ServerManager']
