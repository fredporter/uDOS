"""
Service Registry for uDOS Core

Provides unified access to core services without direct imports.
Replaces verbose package imports with simple registry lookups.

BEFORE (verbose):
    from core.services.logging_service import get_logger
    from core.services.grid_config import load_grid_config
    from core.services.user_service import get_user_manager

AFTER (registry):
    from core.services.registry import get_service

    logger = get_service('logging').get_logger('category')
    grid_config = get_service('grid').load_config()
    user_mgr = get_service('user').get_manager()

Benefit: Lazy loading, better circular dependency handling, easier testing.
"""

from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Lazy-loaded services
_services: Dict[str, Any] = {}
_service_loaders = {
    'logging': lambda: __import__('core.services.logging_service', fromlist=['get_logging_manager']).get_logging_manager(),
    'grid': lambda: __import__('core.services.grid_config', fromlist=['load_grid_config']),
    'dataset': lambda: __import__('core.services.dataset_service', fromlist=['DatasetManager']).DatasetManager(),
    'user': lambda: __import__('core.services.user_service', fromlist=['get_user_manager']).get_user_manager(),
    'history': lambda: __import__('core.services.history_service', fromlist=['get_history_manager']).get_history_manager(),
}


def get_service(service_name: str) -> Any:
    """Get a service by name (lazy-loaded).

    Args:
        service_name: Service identifier (logging, grid, dataset, user, history)

    Returns:
        Service instance or module

    Raises:
        KeyError: If service not found

    Example:
        logger_mgr = get_service('logging')
        logger = logger_mgr.get_logger('my-category')
    """
    if service_name not in _services:
        if service_name not in _service_loaders:
            raise KeyError(f"Unknown service: {service_name}. Available: {list(_service_loaders.keys())}")

        try:
            _services[service_name] = _service_loaders[service_name]()
        except Exception as e:
            raise RuntimeError(f"Failed to load service '{service_name}': {e}")

    return _services[service_name]


def register_service(name: str, loader) -> None:
    """Register a new service loader.

    Args:
        name: Service identifier
        loader: Callable that returns service instance

    Example:
        register_service('myservice', lambda: MyService())
    """
    _service_loaders[name] = loader
    # Clear cache if already loaded
    if name in _services:
        del _services[name]


def list_services() -> list:
    """List all available services."""
    return list(_service_loaders.keys())


# Convenience imports for common pattern
def get_logger(category: str, source: Optional[str] = None):
    """Shortcut to logging service."""
    return get_service('logging').get_logger(category, source=source)
