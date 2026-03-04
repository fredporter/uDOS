"""
uDOS Wizard Server
==================

The Wizard Server is an always-on component that provides:
- Web access for user devices (proxy)
- Plugin repository hosting and distribution
- GitHub repo cloning and packaging
- OK/LLM gateway
- Heavy processing tasks

Architecture
------------
Wizard Server is the ONLY component with web access. User devices
communicate with Wizard via private transports only (mesh/QR/audio).

Components
----------
- server.py: Main FastAPI server
- plugin_factory.py: TCZ package builder
- web_proxy.py: Web content fetching for user devices
- logic-assist routes: local and cloud OK Provider routing

Security
--------
- Wizard runs on dedicated always-on machine
- No direct web exposure to user devices
- All requests authenticated via device tokens
- Rate limiting and cost tracking
"""

from pathlib import Path
import json

# Load version
VERSION_FILE = Path(__file__).parent / "version.json"
if VERSION_FILE.exists():
    with open(VERSION_FILE) as f:
        _version_data = json.load(f)
    __version__ = _version_data.get("version", "1.0.0.0")
else:
    __version__ = "1.0.0.0"

__all__ = [
    "__version__",
    "WizardServer",
    "PluginFactory",
    "PluginRepository",
    "WebProxy",
]


# Lazy imports
def get_wizard_server():
    """Get Wizard Server instance."""
    from .server import WizardServer

    return WizardServer()


def get_plugin_factory():
    """Get Plugin Factory instance."""
    from .services.plugin_factory import PluginFactory

    return PluginFactory()


def get_plugin_repository():
    """Get Plugin Repository instance."""
    from .services.plugin_repository import get_repository

    return get_repository()


def get_web_proxy():
    """Get Web Proxy instance."""
    from .tools.web_proxy import WebProxy

    return WebProxy()

def get_web_service():
    """Legacy web service is retired; FastAPI server is the canonical surface."""
    return None
