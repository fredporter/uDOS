"""Simple wrapper to reuse Core's logging manager from Wizard services."""

from core.services.logging_service import get_logger as core_get_logger


def get_logger(category: str, source: str = "wizard", **kwargs):
    """Return a Core logger pinned to the Wizard source."""
    return core_get_logger(category, source=source, **kwargs)
