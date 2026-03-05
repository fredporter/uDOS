"""Canonical repository path resolution helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Final

DEFAULT_REPO_MARKER: Final[str] = "uDOS.py"
_REPO_ROOT_CACHE: dict[str, Path] = {}


def _home_root() -> Path:
    return Path.home() / "uDOS"


def _enforce_home_root(candidate: Path) -> Path:
    from core.services.unified_config_loader import get_bool_config

    if not get_bool_config("UDOS_HOME_ROOT_ENFORCE"):
        return candidate

    home_root = _home_root()
    try:
        resolved = candidate.resolve()
    except FileNotFoundError:
        resolved = candidate

    if str(resolved).startswith(str(home_root)):
        return candidate

    raise RuntimeError(
        "Repo root outside ~/uDOS. Move the repo under ~/uDOS or "
        "unset UDOS_HOME_ROOT_ENFORCE to allow other locations."
    )


def _normalize_start_path(start_path: Path | None) -> Path:
    candidate = start_path or Path(__file__).resolve()
    candidate = candidate.resolve()
    if candidate.is_dir():
        return candidate
    return candidate.parent


def _strict_root_required() -> bool:
    from core.services.unified_config_loader import get_config

    value = str(get_config("UDOS_ROOT_REQUIRED", "1")).strip().lower()
    return value not in {"0", "false", "no", "off"}


def find_repo_root(start_path: Path | None = None, marker: str = DEFAULT_REPO_MARKER) -> Path:
    """Find repository root.

    Resolution order:
      1. explicit ``start_path`` ancestry (when provided)
      2. ``UDOS_ROOT`` env override (when valid)
      3. module/cwd ancestry fallback
    """
    if start_path is not None:
        current = _normalize_start_path(start_path)
        for parent in [current] + list(current.parents):
            if (parent / marker).exists():
                return _enforce_home_root(parent)

    from core.services.unified_config_loader import get_config

    env_root = get_config("UDOS_ROOT", "")
    strict_required = _strict_root_required()
    if env_root:
        env_path = Path(env_root).expanduser()
        if not env_path.is_absolute():
            env_path = (Path.cwd() / env_path).resolve()
        if (env_path / marker).exists():
            return _enforce_home_root(env_path)
        if strict_required:
            raise RuntimeError(
                f"UDOS_ROOT is set to {env_path} but marker {marker} was not found."
            )
    elif strict_required:
        raise RuntimeError(
            "UDOS_ROOT is required but not set. "
            "Export UDOS_ROOT to the repository root before running uDOS."
        )

    current = _normalize_start_path(start_path)
    for parent in [current] + list(current.parents):
        if (parent / marker).exists():
            return _enforce_home_root(parent)

    raise RuntimeError(
        f"Could not find repository root from {current}. "
        f"Looking for {marker} marker file."
    )


def get_repo_root(marker: str = DEFAULT_REPO_MARKER) -> Path:
    """Return cached repository root for the requested marker."""
    cached = _REPO_ROOT_CACHE.get(marker)
    if cached is not None:
        return cached

    resolved = find_repo_root(marker=marker)
    _REPO_ROOT_CACHE[marker] = resolved
    return resolved


def clear_repo_root_cache(marker: str | None = None) -> None:
    """Clear root cache for tests/runtime refresh."""
    if marker is None:
        _REPO_ROOT_CACHE.clear()
        return
    _REPO_ROOT_CACHE.pop(marker, None)


def get_memory_root(marker: str = DEFAULT_REPO_MARKER) -> Path:
    return get_repo_root(marker=marker) / "memory"


def resolve_repo_path(raw_path: str, marker: str = DEFAULT_REPO_MARKER) -> Path:
    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate
    return get_repo_root(marker=marker) / candidate
