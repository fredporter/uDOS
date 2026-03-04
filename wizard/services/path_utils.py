from __future__ import annotations

from pathlib import Path
from typing import Any

from core.services.path_service import (
    find_repo_root as _find_repo_root,
    get_repo_root as _get_repo_root,
)
from core.services.unified_config_loader import get_config
from wizard.services.wizard_config import load_wizard_config_data


def find_repo_root(start_path: Path | None = None) -> Path:
    return _find_repo_root(start_path=start_path, marker="uDOS.py")


def get_memory_dir() -> Path:
    """Return the memory/ directory path, creating it if it doesn't exist."""
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    configured = get_config("UDOS_MEMORY_ROOT") or locations.get("memory_root")
    memory_dir = _resolve_repo_path(configured) if configured else (get_repo_root() / "memory")
    memory_dir.mkdir(parents=True, exist_ok=True)
    return memory_dir


def get_vault_dir() -> Path:
    """Return the vault directory path, creating it if it doesn't exist."""
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    configured = get_config("VAULT_ROOT") or locations.get("vault_root")
    if configured:
        vault_dir = _resolve_repo_path(configured)
    else:
        vault_dir = get_memory_dir() / "vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir


def get_distribution_dir() -> Path:
    """Return the distribution/ directory path, creating it if it doesn't exist."""
    dist_dir = find_repo_root() / "distribution"
    dist_dir.mkdir(parents=True, exist_ok=True)
    return dist_dir


def get_logs_dir() -> Path:
    """Return the memory/logs/ directory path, creating it if it doesn't exist."""
    logs_dir = get_memory_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_artifacts_dir() -> Path:
    """Return the .artifacts/ directory path, creating it if it doesn't exist."""
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    configured = (
        get_config("UDOS_ARTIFACTS_ROOT")
        or locations.get("artifacts_root")
        or ".artifacts"
    )
    artifacts_dir = _resolve_repo_path(configured)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return artifacts_dir


def get_test_runs_dir() -> Path:
    """Return the test-runs artifacts directory path, creating it if it doesn't exist."""
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    configured = (
        get_config("UDOS_TEST_RUNS_ROOT")
        or locations.get("test_runs_root")
        or str(Path(".artifacts") / "test-runs")
    )
    test_runs_dir = _resolve_repo_path(configured)
    test_runs_dir.mkdir(parents=True, exist_ok=True)
    return test_runs_dir


# ---------------------------------------------------------------------------
# ensure_* aliases — identical to get_* but named to signal explicit intent
# that directory creation is desired.  Prefer these in new code.
# ---------------------------------------------------------------------------

def ensure_memory_dir() -> Path:
    """Ensure the memory/ directory exists and return its path."""
    return get_memory_dir()


def ensure_vault_dir() -> Path:
    """Ensure the vault directory exists and return its path."""
    return get_vault_dir()


def ensure_distribution_dir() -> Path:
    """Ensure the distribution/ directory exists and return its path."""
    return get_distribution_dir()


def ensure_logs_dir() -> Path:
    """Ensure the memory/logs/ directory exists and return its path."""
    return get_logs_dir()


def ensure_artifacts_dir() -> Path:
    """Ensure the .artifacts/ directory exists and return its path."""
    return get_artifacts_dir()


def ensure_test_runs_dir() -> Path:
    """Ensure the test-runs artifacts directory exists and return its path."""
    return get_test_runs_dir()


def _resolve_venv_path(raw_path: str) -> Path:
    """Resolve Python runtime path from env/user input, allowing relative paths."""
    return _resolve_repo_path(raw_path)


def _resolve_repo_path(raw_path: str) -> Path:
    """Resolve path from env/config input, allowing relative repo paths."""
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = get_repo_root() / candidate
    return candidate


def get_wizard_venv_dir() -> Path:
    """Return the Wizard Python runtime path.

    Priority:
    1. WIZARD_VENV_PATH env (absolute or repo-relative)
    2. Default repo path: .venv
    """
    env_venv = get_config("WIZARD_VENV_PATH", "").strip()
    if env_venv:
        return _resolve_venv_path(env_venv)

    return get_repo_root() / ".venv"


def get_repo_root() -> Path:
    """Get cached repo root using canonical path service."""
    return _get_repo_root(marker="uDOS.py")


def _load_wizard_config() -> dict[str, Any]:
    """Load wizard.json config if available."""
    return load_wizard_config_data()
