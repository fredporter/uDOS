from __future__ import annotations

from pathlib import Path

from core.services.python_runtime_contract import (
    CANONICAL_ENV_DIRNAME,
    CANONICAL_ENV_MANAGER,
    CANONICAL_PYTHON_VERSION,
    canonical_env_path,
    canonical_python_path,
)
from tools.ci.check_core_stdlib_boundary import main as run_ci_stdlib_boundary


def test_python_runtime_contract_constants(tmp_path: Path) -> None:
    assert CANONICAL_ENV_DIRNAME == ".venv"
    assert CANONICAL_ENV_MANAGER == "uv"
    assert CANONICAL_PYTHON_VERSION == "3.12"
    assert canonical_env_path(tmp_path) == tmp_path / ".venv"
    assert canonical_python_path(tmp_path) == tmp_path / ".venv" / "bin" / "python"


def test_ci_stdlib_boundary_matches_active_contract() -> None:
    assert run_ci_stdlib_boundary() == 0
