# Integration module marker
"""
uDOS uCORE Integration Package
Provides integration between uNETWORK, uSCRIPT, and uCORE protocols
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ucore_protocols import create_ucore_integration, uCOREProtocols

__version__ = "1.3.3"
__all__ = ["create_ucore_integration", "uCOREProtocols"]
