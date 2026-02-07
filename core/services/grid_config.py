"""
Grid Configuration (Core)
"""

import json
from pathlib import Path
from typing import Dict, Any

from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("core.grid_config")


def load_grid_config() -> Dict[str, Any]:
    config_path = get_repo_root() / "core" / "config" / "grid.json"
    if not config_path.exists():
        return {"viewports": {"standard": {"cols": 80, "rows": 30}}}
    try:
        return json.loads(config_path.read_text())
    except json.JSONDecodeError:
        logger.warning("[LOCAL] Invalid grid config JSON")
        return {"viewports": {"standard": {"cols": 80, "rows": 30}}}
