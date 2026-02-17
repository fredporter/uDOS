"""
Path Utilities for Wizard Server

Provides reliable repo root detection to prevent creating folders outside repo.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from wizard.services.wizard_config import load_wizard_config_data


def _home_root() -> Path:
    return Path.home() / "uDOS"


def _enforce_home_root(candidate: Path) -> Path:
    # Only enforce ~/uDOS location if explicitly requested
    if os.getenv("UDOS_HOME_ROOT_ENFORCE") == "1":
        home_root = _home_root()
        try:
            resolved = candidate.resolve()
        except FileNotFoundError:
            resolved = candidate
        if not str(resolved).startswith(str(home_root)):
            raise RuntimeError(
                "Repo root outside ~/uDOS. Move the repo under ~/uDOS or "
                "unset UDOS_HOME_ROOT_ENFORCE to allow other locations."
            )
    return candidate


def find_repo_root(start_path: Optional[Path] = None) -> Path:
    """
    Find uDOS repository root by looking for uDOS.py marker file.

    This prevents creating memory/ and distribution/ folders outside the repo
    when modules are imported from different working directories.

    Args:
        start_path: Starting path (defaults to this file's location)

    Returns:
        Absolute path to repository root

    Raises:
        RuntimeError: If repo root cannot be found
    """
    if start_path is None:
        start_path = Path(__file__).resolve()
    else:
        start_path = start_path.resolve()

    # Honor UDOS_ROOT if it points at a repo
    env_root = os.getenv("UDOS_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser()
        if (env_path / "uDOS.py").exists():
            return _enforce_home_root(env_path)

    # Search up directory tree for uDOS.py marker
    for parent in [start_path.parent] + list(start_path.parents):
        if (parent / "uDOS.py").exists():
            return _enforce_home_root(parent)

    # Fallback: assume wizard/ is one level below root
    # This maintains backward compatibility but should not normally be reached
    fallback = Path(__file__).parent.parent.resolve()
    if (fallback / "uDOS.py").exists():
        return _enforce_home_root(fallback)

    raise RuntimeError(
        f"Could not find uDOS repository root from {start_path}. "
        "Looking for uDOS.py marker file."
    )


def get_memory_dir() -> Path:
    """Get memory/ directory path (creates if doesn't exist)."""
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    memory_root = locations.get("memory_root", "memory")
    memory_dir = Path(memory_root)
    if not memory_dir.is_absolute():
        memory_dir = find_repo_root() / memory_dir
    memory_dir.mkdir(parents=True, exist_ok=True)
    return memory_dir


def get_vault_dir() -> Path:
    """Get vault directory path (creates if doesn't exist)."""
    env_root = os.getenv("VAULT_ROOT")
    if env_root:
        vault_dir = Path(env_root).expanduser()
        if not vault_dir.is_absolute():
            vault_dir = get_repo_root() / vault_dir
    else:
        vault_dir = get_repo_root() / "memory" / "vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir


def get_distribution_dir() -> Path:
    """Get distribution/ directory path (creates if doesn't exist)."""
    dist_dir = find_repo_root() / "distribution"
    dist_dir.mkdir(parents=True, exist_ok=True)
    return dist_dir


def get_logs_dir() -> Path:
    """Get memory/logs/ directory path (creates if doesn't exist)."""
    logs_dir = get_memory_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def _resolve_venv_path(raw_path: str) -> Path:
    """Resolve venv path from env/user input, allowing relative paths."""
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = get_repo_root() / candidate
    return candidate


def get_wizard_venv_dir() -> Path:
    """Return Wizard runtime venv path.

    Priority:
    1. WIZARD_VENV_PATH env (absolute or repo-relative)
    2. Default repo path: venv
    """
    env_venv = os.getenv("WIZARD_VENV_PATH", "").strip()
    if env_venv:
        return _resolve_venv_path(env_venv)

    return get_repo_root() / "venv"


# Cache repo root for performance
_REPO_ROOT: Optional[Path] = None


def get_repo_root() -> Path:
    """Get cached repo root (faster than find_repo_root on repeated calls)."""
    global _REPO_ROOT
    if _REPO_ROOT is None:
        _REPO_ROOT = find_repo_root()
    return _REPO_ROOT


def _load_wizard_config() -> Dict[str, Any]:
    """Load wizard.json config if available."""
    return load_wizard_config_data()
