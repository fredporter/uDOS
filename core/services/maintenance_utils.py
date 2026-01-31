"""
Maintenance utilities for Core TUI.

Implements BACKUP/RESTORE/TIDY/CLEAN/COMPOST helpers with uDOS conventions.
"""

from __future__ import annotations

import fnmatch
import json
import os
import shutil
import tarfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from core.services.logging_service import get_repo_root


DEFAULT_EXCLUDES = [
    ".git/*",
    ".venv/*",
    "node_modules/*",
    "dist/*",
    "build/*",
    ".tmp/*",
    ".cache/*",
    "__pycache__/*",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
]

JUNK_PATTERNS = [
    "*.tmp",
    "*.temp",
    "*~",
    "*.bak",
    "*.backup",
    "*-backup.*",
    "*-old.*",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
]


def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def get_memory_root() -> Path:
    return get_repo_root() / "memory"


def get_compost_root() -> Path:
    compost_root = get_repo_root() / ".compost"
    compost_root.mkdir(parents=True, exist_ok=True)
    return compost_root


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _matches_any(path: Path, root: Path, patterns: Iterable[str]) -> bool:
    rel = path.relative_to(root).as_posix()
    for pattern in patterns:
        if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(path.name, pattern):
            return True
    return False


def _safe_move(src: Path, dest_dir: Path) -> Path:
    _ensure_dir(dest_dir)
    dest = dest_dir / src.name
    if dest.exists():
        dest = dest_dir / f"{src.name}.{_now_stamp()}"
    shutil.move(str(src), str(dest))
    return dest


def _backup_root_for(target_root: Path) -> Path:
    backup_root = target_root / ".backup"
    _ensure_dir(backup_root)
    return backup_root


def list_backups(target_root: Path) -> List[Path]:
    backup_root = _backup_root_for(target_root)
    return sorted(backup_root.glob("*.tar.gz"), reverse=True)


def create_backup(
    target_root: Path,
    label: str,
    excludes: Optional[List[str]] = None,
) -> Tuple[Path, Path]:
    """Create a tar.gz backup in target_root/.backup and return (archive, manifest)."""
    excludes = excludes or []
    backup_root = _backup_root_for(target_root)
    stamp = _now_stamp()
    safe_label = label.replace(" ", "-").lower()
    archive_path = backup_root / f"{stamp}-{safe_label}.tar.gz"
    manifest_path = backup_root / f"{stamp}-{safe_label}.json"

    def _include(path: Path) -> bool:
        if _matches_any(path, target_root, DEFAULT_EXCLUDES + excludes):
            return False
        if ".backup" in path.parts:
            return False
        return True

    with tarfile.open(archive_path, "w:gz") as tar:
        for root, dirs, files in os.walk(target_root):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if _include(root_path / d)]
            for file in files:
                file_path = root_path / file
                if not _include(file_path):
                    continue
                rel = file_path.relative_to(target_root)
                tar.add(file_path, arcname=str(rel))

    manifest = {
        "label": label,
        "created_at": stamp,
        "target_root": str(target_root),
        "archive": str(archive_path),
        "excludes": excludes,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return archive_path, manifest_path


def restore_backup(archive_path: Path, target_root: Path, force: bool = False) -> str:
    if not archive_path.exists():
        raise FileNotFoundError(f"Backup not found: {archive_path}")
    _ensure_dir(target_root)
    with tarfile.open(archive_path, "r:gz") as tar:
        if not force:
            for member in tar.getmembers():
                dest = target_root / member.name
                if dest.exists():
                    raise FileExistsError(f"Restore conflict: {dest}")
        tar.extractall(path=target_root)
    return f"Restored {archive_path.name} to {target_root}"


def tidy(
    scope_root: Path,
    recursive: bool = True,
    archive_name: str = ".archive",
) -> Tuple[int, Path]:
    """Move junk patterns into .archive."""
    archive_root = scope_root / archive_name
    moved = 0
    for root, dirs, files in os.walk(scope_root):
        root_path = Path(root)
        if archive_name in root_path.parts:
            continue
        if not recursive and root_path != scope_root:
            continue
        for entry in list(dirs) + list(files):
            candidate = root_path / entry
            if _matches_any(candidate, scope_root, JUNK_PATTERNS):
                _safe_move(candidate, archive_root)
                moved += 1
    return moved, archive_root


def clean(
    scope_root: Path,
    allowed_entries: Optional[List[str]] = None,
    recursive: bool = False,
    archive_name: str = ".archive",
) -> Tuple[int, Path]:
    """
    Reset scope_root to default state by moving non-allowed entries to .archive.
    """
    archive_root = scope_root / archive_name
    moved = 0
    allowed = set(allowed_entries or [])
    allowed.update({archive_name, ".backup", ".compost"})

    if recursive:
        for root, dirs, files in os.walk(scope_root):
            root_path = Path(root)
            if archive_name in root_path.parts:
                continue
            for entry in list(dirs) + list(files):
                candidate = root_path / entry
                if candidate.name in allowed:
                    continue
                _safe_move(candidate, archive_root)
                moved += 1
        return moved, archive_root

    for entry in scope_root.iterdir():
        if entry.name in allowed:
            continue
        _safe_move(entry, archive_root)
        moved += 1
    return moved, archive_root


def compost(scope_root: Path, recursive: bool = True) -> Tuple[int, Path]:
    """Move .archive/.backup/.tmp/.dev/.cache folders into /.compost."""
    compost_root = get_compost_root() / f"{_now_stamp()}"
    _ensure_dir(compost_root)
    moved = 0
    targets = {".archive", ".backup", ".tmp", ".dev", ".cache"}

    for root, dirs, _files in os.walk(scope_root):
        root_path = Path(root)
        if not recursive and root_path != scope_root:
            continue
        for entry in list(dirs):
            if entry in targets:
                candidate = root_path / entry
                rel_parent = root_path.relative_to(scope_root)
                dest_parent = compost_root / rel_parent
                _safe_move(candidate, dest_parent)
                moved += 1
                dirs.remove(entry)

    return moved, compost_root


def compost_stats() -> dict:
    """Return basic stats about /.compost."""
    compost_root = get_compost_root()
    total_bytes = 0
    entries = 0
    newest_mtime = None

    for root, _dirs, files in os.walk(compost_root):
        root_path = Path(root)
        for name in files:
            path = root_path / name
            try:
                stat = path.stat()
            except OSError:
                continue
            total_bytes += stat.st_size
            entries += 1
            if newest_mtime is None or stat.st_mtime > newest_mtime:
                newest_mtime = stat.st_mtime

    newest_iso = None
    if newest_mtime is not None:
        newest_iso = datetime.fromtimestamp(newest_mtime).isoformat()

    return {
        "path": str(compost_root),
        "entries": entries,
        "total_bytes": total_bytes,
        "latest_update": newest_iso,
    }


def compost_cleanup(days: int = 30, dry_run: bool = True) -> dict:
    """Delete compost entries older than N days."""
    compost_root = get_compost_root()
    if days <= 0:
        days = 30
    cutoff = datetime.now().timestamp() - (days * 86400)

    deleted = 0
    deleted_bytes = 0

    for entry in compost_root.iterdir():
        try:
            stat = entry.stat()
        except OSError:
            continue
        if stat.st_mtime > cutoff:
            continue

        if entry.is_dir():
            size = 0
            for root, _dirs, files in os.walk(entry):
                for name in files:
                    try:
                        size += (Path(root) / name).stat().st_size
                    except OSError:
                        pass
            if not dry_run:
                shutil.rmtree(entry)
            deleted += 1
            deleted_bytes += size
        else:
            if not dry_run:
                entry.unlink()
            deleted += 1
            deleted_bytes += stat.st_size

    return {
        "path": str(compost_root),
        "deleted_entries": deleted,
        "deleted_bytes": deleted_bytes,
        "days": days,
        "dry_run": dry_run,
    }


def default_repo_allowlist() -> List[str]:
    return [
        "core",
        "wizard",
        "extensions",
        "docs",
        "knowledge",
        "library",
        "distribution",
        "sonic",
        "packages",
        "app",
        "bin",
        "memory",
        "dev",
        ".git",
        ".venv",
        ".compost",
        ".archive",
        ".backup",
        ".tmp",
        "requirements.txt",
        "README.md",
        "AGENTS.md",
        "uDOS.py",
        "setup.py",
        "LICENSE.txt",
        "package.json",
        "package-lock.json",
        "uDOS.code-workspace",
    ]


def default_memory_allowlist() -> List[str]:
    return [
        "logs",
        "system",
        "user",
        "public",
        "private",
        "groups",
        "shared",
        "planet",
        "ucode",
        "workflows",
        "bank",
        "drafts",
        "tmp",
        ".backup",
        ".archive",
        ".compost",
    ]
