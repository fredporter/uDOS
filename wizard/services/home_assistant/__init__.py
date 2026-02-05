"""
Home Assistant Container Gateway Service
=========================================

REST/WebSocket gateway for Home Assistant device integration.
Provides unified interface for device discovery, control, and monitoring.
"""

from .service import HomeAssistantService
from .gateway.manager import GatewayManager

__all__ = ["HomeAssistantService", "GatewayManager"]
