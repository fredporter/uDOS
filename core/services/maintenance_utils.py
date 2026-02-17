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
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Tuple

from core.services.logging_api import get_repo_root


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


def _day_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_memory_root() -> Path:
    return get_repo_root() / "memory"


def get_compost_root() -> Path:
    compost_root = get_repo_root() / ".compost"
    compost_root.mkdir(parents=True, exist_ok=True)
    return compost_root


def _scope_key(target_root: Path) -> str:
    repo_root = get_repo_root().resolve()
    target = target_root.resolve()
    try:
        rel = target.relative_to(repo_root)
        label = rel.as_posix() or "repo-root"
    except Exception:
        label = target.as_posix().replace(":", "")
    label = label.replace("/", "__")
    return label.strip("_") or "repo-root"


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


def _path_size_bytes(path: Path) -> int:
    """Best-effort byte size for files/directories."""
    try:
        if path.is_file():
            return path.stat().st_size
        if path.is_dir():
            total = 0
            for root, _dirs, files in os.walk(path):
                root_path = Path(root)
                for name in files:
                    try:
                        total += (root_path / name).stat().st_size
                    except OSError:
                        continue
            return total
    except OSError:
        return 0
    return 0


def _dedupe_move_candidates(candidates: List[Path]) -> List[Path]:
    """Remove nested children when a parent is already scheduled for move."""
    ordered = sorted({p.resolve() for p in candidates}, key=lambda p: len(p.parts))
    chosen: List[Path] = []
    for candidate in ordered:
        if any(parent in candidate.parents for parent in chosen):
            continue
        chosen.append(candidate)
    return chosen


def _compost_total_bytes(compost_root: Path) -> int:
    return _path_size_bytes(compost_root)


def _compost_type_root(compost_type: str) -> Path:
    root = get_compost_root() / _day_stamp() / compost_type
    _ensure_dir(root)
    return root


def _iter_compost_type_roots(compost_root: Path, compost_type: str) -> List[Path]:
    roots: List[Path] = []

    direct = compost_root / compost_type
    if direct.exists() and direct.is_dir():
        roots.append(direct)

    for day_dir in compost_root.iterdir():
        if not day_dir.is_dir():
            continue
        typed = day_dir / compost_type
        if typed.exists() and typed.is_dir():
            roots.append(typed)

    return roots


def _prune_compost_by_priority(
    compost_root: Path,
    bytes_needed: int,
) -> Tuple[int, int]:
    """Prune compost until at least bytes_needed reclaimed, ordered by priority."""
    if bytes_needed <= 0:
        return 0, 0

    reclaimed = 0
    removed = 0
    tier_order = ["archive", "trash", "backups"]

    for tier_name in tier_order:
        tier_roots = _iter_compost_type_roots(compost_root, tier_name)
        if not tier_roots:
            continue
        tier_entries: List[Path] = []
        for tier in tier_roots:
            tier_entries.extend(tier.rglob("*"))

        entries = sorted(
            [p for p in tier_entries if p.exists()],
            key=lambda p: p.stat().st_mtime if p.exists() else float("inf"),
        )
        # Oldest first, files first (allows gradual cleanup in backups tier).
        entries = sorted(entries, key=lambda p: (p.is_dir(), p.stat().st_mtime if p.exists() else float("inf")))

        for entry in entries:
            if not entry.exists():
                continue
            # Delete files as soon as possible; delete dirs only when empty.
            if entry.is_dir():
                try:
                    next(entry.iterdir())
                    continue
                except StopIteration:
                    size = 0
                except OSError:
                    continue
                try:
                    entry.rmdir()
                    removed += 1
                except OSError:
                    continue
            else:
                size = _path_size_bytes(entry)
                try:
                    entry.unlink()
                    reclaimed += size
                    removed += 1
                except OSError:
                    continue

            if reclaimed >= bytes_needed:
                return reclaimed, removed

        # After file cleanup, try removing now-empty dirs for this type.
        for tier in tier_roots:
            for dir_path in sorted([p for p in tier.rglob("*") if p.is_dir()], key=lambda p: len(p.parts), reverse=True):
                try:
                    next(dir_path.iterdir())
                    continue
                except StopIteration:
                    pass
                except OSError:
                    continue
                try:
                    dir_path.rmdir()
                    removed += 1
                except OSError:
                    continue
            try:
                next(tier.iterdir())
            except StopIteration:
                try:
                    tier.rmdir()
                    removed += 1
                except OSError:
                    pass
            except OSError:
                pass

    return reclaimed, removed


def _ensure_compost_capacity(incoming_bytes: int = 0) -> None:
    """Elastic-trash policy:
    - Keep a free-space reserve on local storage.
    - Optionally cap total /.compost size.
    - Reclaim from /.compost in priority order when required.
    """
    compost_root = get_compost_root()
    repo_root = get_repo_root()

    reserve_mb_raw = os.getenv("UDOS_COMPOST_RESERVE_MB", "512").strip()
    max_mb_raw = os.getenv("UDOS_COMPOST_MAX_MB", "").strip()
    max_bytes_raw = os.getenv("UDOS_COMPOST_MAX_BYTES", "").strip()

    try:
        reserve_bytes = max(0, int(float(reserve_mb_raw) * 1024 * 1024))
    except ValueError:
        reserve_bytes = 512 * 1024 * 1024

    max_bytes = None
    if max_bytes_raw:
        try:
            max_bytes = max(0, int(max_bytes_raw))
        except ValueError:
            max_bytes = None
    elif max_mb_raw:
        try:
            max_bytes = max(0, int(float(max_mb_raw) * 1024 * 1024))
        except ValueError:
            max_bytes = None

    # Rule 1: keep compost within max size when configured.
    if max_bytes is not None:
        current_compost = _compost_total_bytes(compost_root)
        overflow = max(0, current_compost - max_bytes)
        if overflow > 0:
            _prune_compost_by_priority(compost_root, overflow)

    # Rule 2: keep enough local free space for incoming move + reserve.
    try:
        free_now = shutil.disk_usage(repo_root).free
    except OSError:
        return
    required = max(0, incoming_bytes) + reserve_bytes
    deficit = required - free_now
    if deficit > 0:
        _prune_compost_by_priority(compost_root, deficit)


def _backup_root_for(target_root: Path) -> Path:
    backup_root = _compost_type_root("backups") / _scope_key(target_root)
    _ensure_dir(backup_root)
    return backup_root


def list_backups(target_root: Path) -> List[Path]:
    compost_root = get_compost_root()
    scope = _scope_key(target_root)
    archives: List[Path] = []
    for root in _iter_compost_type_roots(compost_root, "backups"):
        backup_root = root / scope
        if not backup_root.exists():
            continue
        archives.extend(backup_root.glob("*.tar.gz"))
    return sorted(archives, reverse=True)


def create_backup(
    target_root: Path,
    label: str,
    excludes: Optional[List[str]] = None,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
) -> Tuple[Path, Path]:
    """Create a tar.gz backup in /.compost/<date>/backups and return (archive, manifest)."""
    excludes = excludes or []
    backup_root = _backup_root_for(target_root)
    stamp = _now_stamp()
    safe_label = label.replace(" ", "-").lower()
    archive_path = backup_root / f"{stamp}-{safe_label}.tar.gz"
    manifest_path = backup_root / f"{stamp}-{safe_label}.json"

    def _include(path: Path) -> bool:
        if _matches_any(path, target_root, DEFAULT_EXCLUDES + excludes):
            return False
        if ".compost" in path.parts:
            return False
        return True

    files_to_add: List[Path] = []
    for root, dirs, files in os.walk(target_root):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if _include(root_path / d)]
        for file in files:
            file_path = root_path / file
            if not _include(file_path):
                continue
            files_to_add.append(file_path)

    total_files = len(files_to_add)
    if on_progress:
        on_progress(0, total_files, "collecting")

    with tarfile.open(archive_path, "w:gz") as tar:
        for idx, file_path in enumerate(files_to_add, 1):
            rel = file_path.relative_to(target_root)
            tar.add(file_path, arcname=str(rel))
            if on_progress:
                on_progress(idx, total_files, str(rel))

    manifest = {
        "label": label,
        "created_at": stamp,
        "target_root": str(target_root),
        "archive": str(archive_path),
        "excludes": excludes,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    if on_progress:
        on_progress(total_files, total_files, "manifest")
    return archive_path, manifest_path


def restore_backup(
    archive_path: Path,
    target_root: Path,
    force: bool = False,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
) -> str:
    if not archive_path.exists():
        raise FileNotFoundError(f"Backup not found: {archive_path}")
    _ensure_dir(target_root)
    with tarfile.open(archive_path, "r:gz") as tar:
        members = tar.getmembers()
        total_members = len(members)
        if on_progress:
            on_progress(0, total_members, "checking")
        if not force:
            for member in members:
                dest = target_root / member.name
                if dest.exists():
                    raise FileExistsError(f"Restore conflict: {dest}")
        for idx, member in enumerate(members, 1):
            tar.extract(member, path=target_root)
            if on_progress:
                on_progress(idx, total_members, member.name)
    return f"Restored {archive_path.name} to {target_root}"


def tidy(
    scope_root: Path,
    recursive: bool = True,
    archive_name: str = ".compost",
) -> Tuple[int, Path]:
    """Move junk patterns into /.compost/<date>/trash."""
    archive_root = _compost_type_root("trash") / _now_stamp() / _scope_key(scope_root)
    candidates: List[Path] = []
    for root, dirs, files in os.walk(scope_root):
        root_path = Path(root)
        if ".compost" in root_path.parts:
            continue
        if not recursive and root_path != scope_root:
            continue
        for entry in list(dirs) + list(files):
            candidate = root_path / entry
            if _matches_any(candidate, scope_root, JUNK_PATTERNS):
                candidates.append(candidate)

    candidates = _dedupe_move_candidates(candidates)
    incoming_bytes = sum(_path_size_bytes(path) for path in candidates)
    _ensure_compost_capacity(incoming_bytes)

    moved = 0
    for candidate in candidates:
        if not candidate.exists():
            continue
        _safe_move(candidate, archive_root)
        moved += 1
    return moved, archive_root


def clean(
    scope_root: Path,
    allowed_entries: Optional[List[str]] = None,
    recursive: bool = False,
    archive_name: str = ".compost",
) -> Tuple[int, Path]:
    """
    Reset scope_root by moving non-allowed entries to /.compost/<date>/trash.
    """
    archive_root = _compost_type_root("trash") / _now_stamp() / _scope_key(scope_root)
    candidates: List[Path] = []
    allowed = set(allowed_entries or [])
    allowed.update({archive_name, ".compost"})

    if recursive:
        for root, dirs, files in os.walk(scope_root):
            root_path = Path(root)
            if ".compost" in root_path.parts:
                continue
            for entry in list(dirs) + list(files):
                candidate = root_path / entry
                if candidate.name in allowed:
                    continue
                candidates.append(candidate)
        candidates = _dedupe_move_candidates(candidates)
        incoming_bytes = sum(_path_size_bytes(path) for path in candidates)
        _ensure_compost_capacity(incoming_bytes)
        moved = 0
        for candidate in candidates:
            if not candidate.exists():
                continue
            _safe_move(candidate, archive_root)
            moved += 1
        return moved, archive_root

    moved = 0
    candidates = []
    for entry in scope_root.iterdir():
        if entry.name in allowed:
            continue
        candidates.append(entry)
    candidates = _dedupe_move_candidates(candidates)
    incoming_bytes = sum(_path_size_bytes(path) for path in candidates)
    _ensure_compost_capacity(incoming_bytes)
    for candidate in candidates:
        if not candidate.exists():
            continue
        _safe_move(candidate, archive_root)
        moved += 1
    return moved, archive_root


def compost(scope_root: Path, recursive: bool = True) -> Tuple[int, Path]:
    """Move local runtime archive dirs into /.compost/<date>/archive."""
    compost_root = _compost_type_root("archive") / _now_stamp() / _scope_key(scope_root)
    _ensure_dir(compost_root)
    moved = 0
    targets = {".archive", ".backup", ".tmp", ".temp"}

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
        "requirements.txt",
        "README.md",
        "AGENTS.md",
        "uDOS.py",
        "pyproject.toml",
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
        ".compost",
    ]
