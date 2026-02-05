"""API module initialization."""

from .rest import router as rest_router
from .rest import set_gateway_manager

__all__ = ["rest_router", "set_gateway_manager"]
