"""
uDOS Transport Layer
Alpha v1.0.0.32

Modular transport system for offline-first P2P communication.
All transports are optional - core can run without them.

Available Transports:
- meshcore: P2P mesh networking (primary)
- bluetooth: Paired device communication
- nfc: Near-field contact data
- qr: Visual data transfer via QR codes
- audio: Acoustic data relay

Transport Policy: See policy.yaml for rules.
All transports follow the Two-Realm model:
- PRIVATE transports: Commands + data allowed
- PUBLIC signals: Beacon/presence only, no data

Usage:
    from extensions.transport import get_transport

    mesh = get_transport('meshcore')  # Returns None if unavailable
    if mesh:
        mesh.send_message(...)
"""

from typing import Optional, Dict, Any
from pathlib import Path
import importlib

__version__ = "1.0.0.32"

# Transport availability flags
TRANSPORTS_AVAILABLE: Dict[str, bool] = {}


def _check_transport(name: str) -> bool:
    """Check if a transport module is available."""
    try:
        if name == "audio":
            importlib.import_module("groovebox.transport.audio")
        else:
            importlib.import_module(f".{name}", package=__name__)
        return True
    except ImportError:
        return False


def get_transport(name: str) -> Optional[Any]:
    """
    Get a transport module by name.

    Returns None if transport is not available (missing dependencies).
    This allows core to function without any transports installed.

    Args:
        name: Transport name ('meshcore', 'bluetooth', 'nfc', 'qr', 'audio')

    Returns:
        Transport module or None
    """
    if name not in TRANSPORTS_AVAILABLE:
        TRANSPORTS_AVAILABLE[name] = _check_transport(name)

    if TRANSPORTS_AVAILABLE[name]:
        if name == "audio":
            return importlib.import_module("groovebox.transport.audio")
        return importlib.import_module(f".{name}", package=__name__)
    return None


def list_transports() -> Dict[str, bool]:
    """
    List all transports and their availability.

    Returns:
        Dict of transport name -> available (bool)
    """
    transport_names = ["meshcore", "bluetooth", "nfc", "qr", "audio"]

    for name in transport_names:
        if name not in TRANSPORTS_AVAILABLE:
            TRANSPORTS_AVAILABLE[name] = _check_transport(name)

    return TRANSPORTS_AVAILABLE.copy()


def get_policy() -> Dict[str, Any]:
    """Load transport policy from YAML."""
    import yaml

    policy_file = Path(__file__).parent / "policy.yaml"
    if policy_file.exists():
        return yaml.safe_load(policy_file.read_text())
    return {}


# Check core transports on import
try:
    from . import meshcore

    TRANSPORTS_AVAILABLE["meshcore"] = True
except ImportError:
    TRANSPORTS_AVAILABLE["meshcore"] = False

try:
    importlib.import_module("groovebox.transport.audio")
    TRANSPORTS_AVAILABLE["audio"] = True
except ImportError:
    TRANSPORTS_AVAILABLE["audio"] = False

try:
    from . import qr

    TRANSPORTS_AVAILABLE["qr"] = True
except ImportError:
    TRANSPORTS_AVAILABLE["qr"] = False
