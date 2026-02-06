"""
Path Utilities for Wizard Server

Provides reliable repo root detection to prevent creating folders outside repo.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


def _home_root() -> Path:
    return Path.home() / "uDOS"


def _enforce_home_root(candidate: Path) -> Path:
    home_root = _home_root()
    if home_root.exists() or os.getenv("UDOS_HOME_ROOT_ENFORCE") == "1":
        try:
            resolved = candidate.resolve()
        except FileNotFoundError:
            resolved = candidate
        if not str(resolved).startswith(str(home_root)):
            if os.getenv("UDOS_HOME_ROOT_ALLOW_OUTSIDE") == "1":
                return candidate
            raise RuntimeError(
                "Repo root outside ~/uDOS. Move the repo under ~/uDOS or set "
                "UDOS_HOME_ROOT_ALLOW_OUTSIDE=1 to bypass."
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


def get_vault_md_root() -> Path:
    """Get vault-md root path (defaults to ~/Documents/uDOS Vault)."""
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    env_root = os.getenv("VAULT_MD_ROOT") or os.getenv("VAULT_ROOT")
    if env_root:
        return Path(env_root).expanduser()

    config_root = locations.get("vault_md_root")
    if config_root:
        return Path(config_root).expanduser()

    return Path.home() / "Documents" / "uDOS Vault"


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
    config_path = Path(__file__).parent.parent / "config" / "wizard.json"
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
