"""
uDOS Core Services Package

This package contains foundational services for the Core TUI:
- Logging (logging_api.py)
- Configuration (grid_config.py, dataset_service.py)
- User management (user_service.py)
- History tracking (history_service.py)
- etc.

These services are NOT containerized — they're core infrastructure.

Import Pattern:
    # Direct import (recommended for core modules)
    from core.services.logging_api import get_logger

    # Or use registry pattern
    from core.services import ServiceRegistry
    logger = ServiceRegistry.get('logging').get_logger('category')

When to containerize modules:
- If it's self-contained and doesn't need cross-service communication
- If it could be deployed independently
- If it's > 2K LOC and growing
- If external projects might want it separately

Examples that SHOULD be containerized:
- Groovebox (music engine) ✓ Self-contained
- Empire (data enrichment) ✓ Self-contained
- Sonic (sound synthesis) ✓ Self-contained

Examples that SHOULD stay here:
- Logging ✓ Core infrastructure
- Grid config ✓ Core infrastructure
- User service ✓ Core infrastructure
- History/checkpoint ✓ Core infrastructure
"""

from core.services.logging_api import (
    get_logger,
    get_log_manager,
    LogManager,
    DevTrace,
    LogTags,
)

__all__ = [
    "get_logger",
    "get_log_manager",
    "LogManager",
    "DevTrace",
    "LogTags",
]
