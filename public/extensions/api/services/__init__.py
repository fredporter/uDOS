"""
API Services Layer
==================

Shared services for uDOS API routes and WebSocket handlers.
"""

from .executor import (
    execute_command,
    init_udos_systems,
    get_api_logger,
    get_project_root,
    get_services,
    UDOS_AVAILABLE,
    STREAMING_AVAILABLE,
)

__all__ = [
    "execute_command",
    "init_udos_systems",
    "get_api_logger",
    "get_project_root",
    "get_services",
    "UDOS_AVAILABLE",
    "STREAMING_AVAILABLE",
]
