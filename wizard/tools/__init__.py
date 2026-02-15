"""
Wizard Tools - Image conversion, proxy, device provisioning
"""
from .web_proxy import WebProxy
try:
    from .image_teletext import ImageToTeletext
except ImportError:
    ImageToTeletext = None  # Optional tool may be archived/missing in slim installs

# Optional tools (may have extra dependencies)
try:
    from .screwdriver import FlashPackManager, ScrewdriverProvisioner

    SCREWDRIVER_AVAILABLE = True
except ImportError:
    SCREWDRIVER_AVAILABLE = False

try:
    from .toybox_setup import main as toybox_setup_main
except ImportError:
    toybox_setup_main = None

__all__ = ["WebProxy", "ImageToTeletext", "toybox_setup_main"]
