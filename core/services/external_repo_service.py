"""External companion-repo discovery for Sonic and uHOME."""

from __future__ import annotations

import os
import sys
import importlib.util
from pathlib import Path

from core.services.path_service import get_repo_root


def _resolve_repo_root(repo_root: Path | None = None) -> Path:
    return Path(repo_root or get_repo_root()).resolve()


def _env_path(name: str) -> Path | None:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    return Path(raw).expanduser().resolve()


def resolve_sonic_repo_root(repo_root: Path | None = None) -> Path:
    root = _resolve_repo_root(repo_root)
    env = _env_path("UDOS_SONIC_ROOT")
    if env is not None:
        return env
    return root.parent / "uDOS-sonic"


def resolve_uhome_repo_root(repo_root: Path | None = None) -> Path:
    root = _resolve_repo_root(repo_root)
    env = _env_path("UDOS_UHOME_ROOT")
    if env is not None:
        return env
    return root.parent / "uHOME-server"


def sonic_repo_available(repo_root: Path | None = None) -> bool:
    return resolve_sonic_repo_root(repo_root).exists()


def uhome_repo_available(repo_root: Path | None = None) -> bool:
    return resolve_uhome_repo_root(repo_root).exists()


def ensure_sonic_python_paths(repo_root: Path | None = None) -> Path:
    sonic_root = resolve_sonic_repo_root(repo_root)
    for candidate in (sonic_root, sonic_root / "library"):
        if candidate.exists():
            raw = str(candidate)
            if raw not in sys.path:
                sys.path.insert(0, raw)
    _bind_external_sonic_core_modules(sonic_root)
    return sonic_root


def _bind_external_sonic_core_modules(sonic_root: Path) -> None:
    external_core = sonic_root / "core"
    if not external_core.exists():
        return
    for module_name in ("os_limits", "sonic_api", "sonic_mcp"):
        qualified = f"core.{module_name}"
        if qualified in sys.modules:
            continue
        path = external_core / f"{module_name}.py"
        if not path.exists():
            continue
        spec = importlib.util.spec_from_file_location(qualified, path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[qualified] = module
        spec.loader.exec_module(module)
