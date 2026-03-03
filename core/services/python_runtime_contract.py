"""Canonical Python runtime contract for uDOS v1.5."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

from core.services.path_service import get_repo_root as resolve_repo_root


CANONICAL_ENV_DIRNAME = ".venv"
CANONICAL_PYTHON_VERSION = "3.12"
CANONICAL_ENV_MANAGER = "uv"

def canonical_env_path(repo_root: Path | None = None) -> Path:
    root = repo_root or resolve_repo_root()
    return root / CANONICAL_ENV_DIRNAME


def canonical_python_path(repo_root: Path | None = None) -> Path:
    return canonical_env_path(repo_root) / "bin" / "python"


def canonical_uv_path(repo_root: Path | None = None) -> Path:
    return canonical_env_path(repo_root) / "bin" / "uv"


@dataclass(frozen=True)
class PythonRuntimeStatus:
    executable: str
    repo_root: str
    canonical_env: str
    canonical_python: str
    uv_available: bool
    uv_path: str | None
    using_canonical_env: bool
    core_boundary_ok: bool
    wizard_dependency_groups_declared: bool
    wizard_runtime_available: bool
    problems: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "executable": self.executable,
            "repo_root": self.repo_root,
            "canonical_env": self.canonical_env,
            "canonical_python": self.canonical_python,
            "uv_available": self.uv_available,
            "uv_path": self.uv_path,
            "using_canonical_env": self.using_canonical_env,
            "core_boundary_ok": self.core_boundary_ok,
            "wizard_dependency_groups_declared": self.wizard_dependency_groups_declared,
            "wizard_runtime_available": self.wizard_runtime_available,
            "problems": list(self.problems),
        }


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _python_inside_env(executable: Path, env_path: Path) -> bool:
    try:
        executable_resolved = executable.resolve()
    except FileNotFoundError:
        executable_resolved = executable
    try:
        env_resolved = env_path.resolve()
    except FileNotFoundError:
        env_resolved = env_path
    return env_resolved == executable_resolved.parent.parent


def _core_boundary_ok(root: Path) -> bool:
    audit_script = root / "scripts" / "check_core_stdlib_contract.py"
    if not audit_script.exists():
        return False
    result = subprocess.run(
        [sys.executable, str(audit_script)],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _wizard_dependency_groups_declared(root: Path) -> bool:
    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.exists():
        return False
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    optional = payload.get("project", {}).get("optional-dependencies", {})
    return "udos" in optional and "udos-wizard" in optional


def detect_python_runtime_status(repo_root: Path | None = None) -> PythonRuntimeStatus:
    root = repo_root or resolve_repo_root()
    env_path = canonical_env_path(root)
    python_path = canonical_python_path(root)
    uv_bin = shutil.which(CANONICAL_ENV_MANAGER)
    uv_env_bin = canonical_uv_path(root)
    uv_path = uv_bin or (str(uv_env_bin) if uv_env_bin.exists() else None)
    using_canonical_env = _python_inside_env(Path(sys.executable), env_path)
    wizard_dependency_groups_declared = _wizard_dependency_groups_declared(root)
    wizard_runtime_available = _module_available("fastapi")
    core_boundary_ok = _core_boundary_ok(root)

    problems: list[str] = []
    if not uv_path:
        problems.append("uv missing")
    if not env_path.exists():
        problems.append("canonical env missing")
    if env_path.exists() and not python_path.exists():
        problems.append("canonical python missing")
    if not using_canonical_env:
        problems.append("python executable outside canonical env")
    if not core_boundary_ok:
        problems.append("core stdlib contract check failed")
    if not wizard_runtime_available:
        problems.append("wizard runtime dependencies unavailable")
    if not wizard_dependency_groups_declared:
        problems.append("wizard dependency groups missing from pyproject")

    return PythonRuntimeStatus(
        executable=sys.executable,
        repo_root=str(root),
        canonical_env=str(env_path),
        canonical_python=str(python_path),
        uv_available=bool(uv_path),
        uv_path=uv_path,
        using_canonical_env=using_canonical_env,
        core_boundary_ok=core_boundary_ok,
        wizard_dependency_groups_declared=wizard_dependency_groups_declared,
        wizard_runtime_available=wizard_runtime_available,
        problems=tuple(problems),
    )
