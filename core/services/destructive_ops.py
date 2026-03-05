"""Shared destructive operation helpers for handlers/routes."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import shutil

from core.services.unified_config_loader import get_process_env


def resolve_vault_root(repo_root: Path) -> Path:
    if vault_root := get_process_env("VAULT_ROOT"):
        candidate = Path(vault_root).expanduser()
        return candidate if candidate.is_absolute() else (repo_root / candidate).resolve()
    if memory_root := get_process_env("UDOS_MEMORY_ROOT"):
        candidate = Path(memory_root).expanduser()
        resolved = candidate if candidate.is_absolute() else (repo_root / candidate).resolve()
        return resolved / "vault"
    return (repo_root / "memory" / "vault").resolve()


def remove_path(path: Path) -> bool:
    """Remove a file/symlink/directory path if present. Returns True when removed."""
    if not path.exists():
        return False
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()
    return True


def scrub_directory(path: Path, recreate: bool = True) -> None:
    remove_path(path)
    if recreate:
        path.mkdir(parents=True, exist_ok=True)


def ensure_memory_layout(memory_root: Path, subdirs: Iterable[str] | None = None) -> None:
    memory_root.mkdir(parents=True, exist_ok=True)
    for sub in subdirs or ("logs", "bank", "private", "wizard"):
        (memory_root / sub).mkdir(parents=True, exist_ok=True)


def wipe_json_config_dir(config_path: Path, keep_files: set[str] | None = None) -> int:
    keep = keep_files or set()
    removed = 0
    if not config_path.exists():
        return removed
    for config_file in config_path.glob("*.json"):
        if config_file.name in keep:
            continue
        try:
            config_file.unlink()
            removed += 1
        except Exception:
            pass
    return removed
