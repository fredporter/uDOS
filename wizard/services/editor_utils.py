"""
Editor utilities for Wizard TUIs.

Default editor: /library/micro (micro) with nano fallback.
Default workspace: /memory
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from wizard.services.path_utils import get_repo_root, get_memory_dir
from wizard.services.logging_manager import get_logger

logger = get_logger("wizard.editor")


def _is_executable(path: Path) -> bool:
    return path.exists() and os.access(path, os.X_OK) and path.is_file()


def _read_container_repo_path(container_id: str) -> Optional[Path]:
    repo_root = get_repo_root()
    container_json = repo_root / "library" / container_id / "container.json"
    if not container_json.exists():
        return None

    try:
        data = json.loads(container_json.read_text())
        repo_path = data.get("repo_path")
    except Exception:
        return None

    if not repo_path:
        return None

    repo_path = Path(repo_path)
    if repo_path.is_absolute():
        return repo_path

    return (repo_root / repo_path).resolve()


def micro_path() -> Path:
    repo_root = get_repo_root()
    repo_path = _read_container_repo_path("micro")
    if repo_path:
        return repo_path

    return get_memory_dir().resolve() / "library" / "containers" / "micro"


def ensure_micro_repo() -> None:
    repo_root = get_repo_root()
    target = micro_path()
    if target.exists():
        return

    git = shutil.which("git")
    if not git:
        logger.warning("[WIZ] git not found; cannot clone micro")
        return

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [git, "clone", "https://github.com/zyedidia/micro", str(target)],
            check=True,
            cwd=str(repo_root),
        )
        logger.info(f"[WIZ] Cloned micro to {target}")
    except Exception as exc:
        logger.warning(f"[WIZ] Failed to clone micro: {exc}")


def find_micro_binary() -> Optional[Path]:
    repo_root = get_repo_root()
    micro_root = micro_path()
    candidates = [
        micro_root / "micro",
        micro_root / "bin" / "micro",
        repo_root / "library" / "micro" / "micro",
        repo_root / "library" / "micro" / "bin" / "micro",
    ]
    for candidate in candidates:
        if _is_executable(candidate):
            return candidate

    from_path = shutil.which("micro")
    return Path(from_path) if from_path else None


def find_nano_binary() -> Optional[Path]:
    from_path = shutil.which("nano")
    return Path(from_path) if from_path else None


def pick_editor() -> Tuple[str, Optional[Path]]:
    micro = find_micro_binary()
    if micro:
        return "micro", micro

    nano = find_nano_binary()
    if nano:
        return "nano", nano

    return "", None


def resolve_workspace_path(value: str, default_name: str = "untitled.md") -> Path:
    memory_root = get_memory_dir().resolve()

    if not value:
        relative = default_name
    else:
        relative = value.strip()

    if not relative:
        relative = default_name

    if not Path(relative).suffix:
        relative = f"{relative}.md"

    relative = relative.replace("\\", "/")

    candidate = Path(relative)
    if candidate.is_absolute():
        resolved = candidate
    else:
        resolved = memory_root / candidate

    resolved = resolved.resolve()
    if not str(resolved).startswith(str(memory_root)):
        raise ValueError("Path must be within /memory")

    return resolved


def open_in_editor(path: Path) -> Tuple[bool, str]:
    editor_name, editor_path = pick_editor()
    if not editor_path:
        return False, "No editor available (micro/nano not found)"

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([str(editor_path), str(path)], check=True)
    except subprocess.CalledProcessError as exc:
        return False, f"Editor failed: {exc}"

    return True, editor_name
