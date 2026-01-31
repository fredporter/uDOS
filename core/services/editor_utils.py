"""
Editor Utilities for Core TUI

Default editor: /library/micro (micro) with nano fallback.
Default workspace: /memory
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from core.services.logging_service import get_repo_root


def get_memory_root() -> Path:
    return get_repo_root() / "memory"


def _is_executable(path: Path) -> bool:
    return path.exists() and os.access(path, os.X_OK) and path.is_file()


def find_micro_binary() -> Optional[Path]:
    repo_root = get_repo_root()
    candidates = [
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
    memory_root = get_memory_root()

    if not value:
        relative = default_name
    else:
        relative = value.strip()

    if not relative:
        relative = default_name

    if not Path(relative).suffix:
        relative = f"{relative}.md"

    # Normalize path separators
    relative = relative.replace("\\", "/")

    candidate = Path(relative)
    if candidate.is_absolute():
        resolved = candidate
    else:
        resolved = memory_root / candidate

    resolved = resolved.resolve()
    memory_root = memory_root.resolve()
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
