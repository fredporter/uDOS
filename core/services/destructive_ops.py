"""Shared destructive operation helpers for handlers/routes."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterable


def resolve_vault_root(repo_root: Path) -> Path:
    env_vault = os.environ.get("VAULT_ROOT")
    if env_vault:
        return Path(env_vault).expanduser()
    return repo_root / "memory" / "vault"


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
