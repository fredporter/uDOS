"""
uDOS Shared Extensions Framework
Common utilities and base classes for web extensions
"""

from .port_manager import PortManager, get_port_manager
from .base_server import BaseExtensionServer, BaseExtensionHandler

__all__ = [
    'PortManager',
    'get_port_manager',
    'BaseExtensionServer',
    'BaseExtensionHandler'
]
