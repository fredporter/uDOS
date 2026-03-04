"""Legacy OK setup adapter for the v1.5 logic-assist runtime."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable


def _default_logger(message: str) -> None:
    print(message)


def _load_ok_modes_config_for_setup(config_path: Path) -> tuple[dict[str, object], list[str]]:
    """Load ok_modes config with recovery for empty or invalid JSON."""
    warnings: list[str] = []
    config: dict[str, object] = {"modes": {}}
    if not config_path.exists():
        return config, warnings

    try:
        loaded = json.loads(config_path.read_text())
        if isinstance(loaded, dict):
            return loaded, warnings
        warnings.append("ok_modes.json was non-object; reset to defaults")
        return config, warnings
    except Exception as exc:
        try:
            backup = config_path.with_suffix(f".invalid-{int(time.time())}.json")
            backup.write_text(config_path.read_text())
            warnings.append(
                f"Recovered invalid ok_modes.json; backup saved to {backup.name}"
            )
        except Exception:
            warnings.append("Recovered invalid ok_modes.json (backup unavailable)")
        warnings.append(f"ok_modes.json parse failed: {exc}")
        return config, warnings


def run_ok_setup(
    repo_root: Path,
    log: Callable[[str], None] | None = None,
    models: list[str] | None = None,
) -> dict[str, list[str]]:
    """Run the canonical v1.5 logic-assist setup helper.

    The legacy OK setup entry point is retained only as an adapter so older
    callers converge on the same GPT4All-based contributor setup path.
    """
    del models
    from core.services.logic_assist_setup import run_logic_assist_setup

    logger = log or _default_logger
    return run_logic_assist_setup(repo_root=repo_root, log=logger)
