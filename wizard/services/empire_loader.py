"""Official Empire extension loader (soft-fail when unavailable)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

from wizard.services.logging_api import get_logger


def load_empire() -> Dict[str, Optional[Any]]:
    """Attempt to load the official Empire extension without hard failure."""
    logger = get_logger("wizard-private-extension")
    repo_root = Path(__file__).resolve().parents[2]
    extensions_root = repo_root / "extensions"
    if str(extensions_root) not in sys.path:
        sys.path.insert(0, str(extensions_root))

    try:
        import empire  # type: ignore
        return {
            "available": True,
            "module": empire,
            "message": None,
        }
    except Exception:
        message = (
            "Official Empire extension not available. "
            "Install or restore extensions/empire to enable this module."
        )
        logger.info(message)
        return {
            "available": False,
            "module": None,
            "message": message,
        }
