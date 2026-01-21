"""
Wizard Server Web Interface
Alpha v1.0.0.32

Web-based GUI for Wizard Server administration and services.
Replaces Tauri requirement with browser-based access.

Components:
- web_service.py: Flask/FastAPI web server
- poke_commands.py: POKE web server commands
- tunnel_manager.py: Secure tunnel for remote access
- static/: Web UI assets (HTML, CSS, JS)

Features:
- Wizard Server dashboard (browser GUI)
- POKE web server for file/page hosting
- Webhook receiver for external integrations
- Real-time log streaming via WebSocket
- Plugin management UI
- Device/mesh monitoring

Transport Policy: WIZARD (web access allowed)
"""

# Conditional imports to avoid breaking standalone scripts
try:
    from .web_service import WebService
except ImportError:
    WebService = None

try:
    from .poke_commands import POKECommandHandler as PokeCommands
except ImportError:
    PokeCommands = None

try:
    from .tunnel_manager import TunnelManager
except ImportError:
    TunnelManager = None

__all__ = ["WebService", "PokeCommands", "TunnelManager"]
