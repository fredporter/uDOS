"""
uDOS Wizard Server
==================

The Wizard Server is an always-on component that provides:
- Web access for user devices (proxy)
- Plugin repository hosting and distribution
- GitHub repo cloning and packaging
- Gmail relay integration
- AI/LLM gateway
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
- gmail_relay.py: Gmail OAuth integration
- ai_gateway.py: LLM API routing
- scraper.py: Web content extraction

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
    "GmailRelay",
    "AIGateway",
    "WebService",
    "BizIntel",
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


def get_gmail_relay():
    """Get Gmail Relay instance."""
    from .services.gmail_relay import get_gmail_relay as _get_relay

    return _get_relay()


def get_ai_gateway():
    """Get AI Gateway instance."""
    from .services.ai_gateway import get_ai_gateway as _get_gateway

    return _get_gateway()


def get_web_service():
    """Get Web Service instance for Wizard GUI."""
    from .web.web_service import WebService

    return WebService()


def get_empire():
    """Get Empire CRM instance."""
    from extensions.empire.empire import Empire

    return Empire()
