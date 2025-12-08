"""
POKE Online Extension v1.1.7

Cloud-based sharing and tunneling extension for uDOS.
Enables secure sharing of uDOS instances via ngrok or cloudflared.

Features:
- Tunnel management (POKE TUNNEL commands)
- File/folder sharing (POKE SHARE commands)
- Group collaboration (POKE GROUP commands)
- Security and permission controls
- Multiple tunnel provider support

Author: uDOS Core Team
License: MIT
Version: 1.1.7
"""

__version__ = "1.1.7"
__author__ = "uDOS Core Team"
__license__ = "MIT"

# Extension metadata
EXTENSION_INFO = {
    "name": "POKE Online",
    "version": "1.1.7",
    "description": "Cloud-based sharing and tunneling for uDOS",
    "requires": ["uDOS>=1.1.6"],
    "optional_dependencies": ["ngrok", "cloudflared"],
    "commands": ["TUNNEL", "SHARE", "GROUP"],
    "services": ["tunnel_manager"],
    "author": "uDOS Core Team",
    "license": "MIT"
}
