"""Optional private extension loader (soft-fail when unavailable)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

from wizard.services.logging_api import get_logger


def load_empire() -> Dict[str, Optional[Any]]:
    """Attempt to load the private extension without hard failure."""
    logger = get_logger("wizard-private-extension")
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    try:
        import empire  # type: ignore
        return {
            "available": True,
            "module": empire,
            "message": None,
        }
    except Exception:
        message = (
            "Optional private extension not available. "
            "Install the private extension to enable this module."
        )
        logger.info(message)
        return {
            "available": False,
            "module": None,
            "message": message,
        }
