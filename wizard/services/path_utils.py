"""
Path Utilities for Wizard Server

Provides reliable repo root detection to prevent creating folders outside repo.
"""

from pathlib import Path
from typing import Optional


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
    
    # Search up directory tree for uDOS.py marker
    for parent in [start_path.parent] + list(start_path.parents):
        if (parent / "uDOS.py").exists():
            return parent
    
    # Fallback: assume wizard/ is one level below root
    # This maintains backward compatibility but should not normally be reached
    fallback = Path(__file__).parent.parent.resolve()
    if (fallback / "uDOS.py").exists():
        return fallback
    
    raise RuntimeError(
        f"Could not find uDOS repository root from {start_path}. "
        "Looking for uDOS.py marker file."
    )


def get_memory_dir() -> Path:
    """Get memory/ directory path (creates if doesn't exist)."""
    memory_dir = find_repo_root() / "memory"
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


# Cache repo root for performance
_REPO_ROOT: Optional[Path] = None


def get_repo_root() -> Path:
    """Get cached repo root (faster than find_repo_root on repeated calls)."""
    global _REPO_ROOT
    if _REPO_ROOT is None:
        _REPO_ROOT = find_repo_root()
    return _REPO_ROOT
