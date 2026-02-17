"""
Dev Recovery Health Diagnostics
--------------------------------

Runs local-first diagnostics to identify common issues with the
Wizard Server and Core runtime, and suggests safe repair actions.

This module is designed for the Dev Mode Recovery TUI to execute
on startup before user interaction.
"""

from __future__ import annotations

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_wizard_venv_dir

logger = get_logger("wizard", category="dev-recovery", name="dev-recovery")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _wizard_venv_dir() -> Path:
    return get_wizard_venv_dir()


def _wizard_requirements() -> Path:
    repo = _repo_root()
    primary = repo / "wizard" / "requirements.txt"
    if primary.exists():
        return primary
    return repo / "requirements.txt"


def _wizard_python() -> str:
    py = _wizard_venv_dir() / "bin" / "python"
    if py.exists():
        return str(py)
    return sys.executable


def _run_cmd(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> Tuple[int, str, str]:
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out.decode("utf-8", errors="ignore"), err.decode("utf-8", errors="ignore")
    except Exception as e:
        return 1, "", str(e)


def check_venv() -> Dict[str, Any]:
    """Detect active Python venv even if VIRTUAL_ENV is unset.

    Healthy if either:
    - VIRTUAL_ENV points to an existing directory, or
    - Current Python executable is inside the resolved Wizard venv
    """
    venv_env = os.environ.get("VIRTUAL_ENV")
    venv_dir = _wizard_venv_dir()
    exe = Path(sys.executable)

    env_ok = bool(venv_env and Path(venv_env).exists())
    path_ok = venv_dir.exists() and venv_dir in exe.parents

    ok = env_ok or path_ok
    if ok:
        if env_ok:
            msg = f"VENV active via env: {venv_env}"
        else:
            msg = f"VENV active via python: {exe}"
    else:
        msg = "Python virtualenv not active"

    return {
        "name": "python_venv",
        "status": "healthy" if ok else "unhealthy",
        "message": msg,
    }


def check_requirements() -> Dict[str, Any]:
    root = _repo_root()
    req = _wizard_requirements()
    if not req.exists():
        return {
            "name": "python_requirements",
            "status": "degraded",
            "message": f"{req.name} missing",
        }
    code, out, err = _run_cmd(
        [_wizard_python(), "-m", "pip", "install", "-r", str(req), "--quiet"],
        cwd=root,
        timeout=300,
    )
    ok = code == 0
    return {
        "name": "python_requirements",
        "status": "healthy" if ok else "unhealthy",
        "message": "Dependencies installed" if ok else f"pip install failed: {err.strip()[:120]}",
    }


def check_fastapi() -> Dict[str, Any]:
    """Verify FastAPI and uvicorn are installed (required for Wizard Server)."""
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        return {
            "name": "fastapi",
            "status": "healthy",
            "message": "FastAPI + uvicorn installed",
        }
    except ImportError as e:
        return {
            "name": "fastapi",
            "status": "unhealthy",
            "message": f"FastAPI/uvicorn missing: {str(e)}. Run: pip install -r wizard/requirements.txt",
        }


def check_wizard_config() -> Dict[str, Any]:
    cfg = _repo_root() / "wizard" / "config" / "wizard.json"
    if not cfg.exists():
        return {"name": "wizard_config", "status": "unhealthy", "message": "wizard/config/wizard.json missing"}
    try:
        data = json.loads(cfg.read_text())
        if "ok_gateway_enabled" not in data and "ai_gateway_enabled" in data:
            data["ok_gateway_enabled"] = data.get("ai_gateway_enabled")
        # minimal required keys
        required = ["host", "port", "ok_gateway_enabled"]
        missing = [k for k in required if k not in data]
        if missing:
            return {
                "name": "wizard_config",
                "status": "degraded",
                "message": f"Missing keys: {', '.join(missing)}",
            }
        return {"name": "wizard_config", "status": "healthy", "message": "Wizard config OK"}
    except Exception as e:
        return {"name": "wizard_config", "status": "unhealthy", "message": f"Invalid JSON: {e}"}


def check_core_versions() -> Dict[str, Any]:
    root = _repo_root()
    code, out, err = _run_cmd([sys.executable, "-m", "core.version", "check"], cwd=root, timeout=120)
    ok = code == 0
    return {
        "name": "core_versions",
        "status": "healthy" if ok else "degraded",
        "message": "Versions OK" if ok else (err.strip() or out.strip())[:160],
    }


def check_git_status() -> Dict[str, Any]:
    root = _repo_root()
    code, out, err = _run_cmd(["git", "status", "--porcelain"], cwd=root)
    ok = code == 0
    dirty = bool(out.strip())
    return {
        "name": "git_status",
        "status": "healthy" if ok and not dirty else ("degraded" if ok and dirty else "unhealthy"),
        "message": "Repo clean" if ok and not dirty else ("Uncommitted changes present" if ok else f"git error: {err.strip()[:120]}"),
    }


def check_wizard_port(host: str = "127.0.0.1", port: int = 8765) -> Dict[str, Any]:
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect((host, port))
        s.close()
        return {"name": "wizard_port", "status": "degraded", "message": f"Port {port} occupied"}
    except Exception:
        return {"name": "wizard_port", "status": "healthy", "message": f"Port {port} available"}


def run_all() -> Dict[str, Any]:
    """Run all diagnostics and return a summary dict."""
    checks = [
        check_venv(),
        check_requirements(),
        check_fastapi(),
        check_wizard_config(),
        check_core_versions(),
        check_git_status(),
        check_wizard_port(),
    ]

    healthy = sum(1 for c in checks if c["status"] == "healthy")
    degraded = sum(1 for c in checks if c["status"] == "degraded")
    unhealthy = sum(1 for c in checks if c["status"] == "unhealthy")

    overall = "healthy"
    if unhealthy > 0:
        overall = "unhealthy"
    elif degraded > 0:
        overall = "degraded"

    summary = {
        "overall": overall,
        "healthy": healthy,
        "degraded": degraded,
        "unhealthy": unhealthy,
        "checks": checks,
    }

    # Log concise summary
    logger.info(
        f"[WIZ] Dev Recovery diagnostics: overall={overall} healthy={healthy} degraded={degraded} unhealthy={unhealthy}"
    )
    return summary


def attempt_safe_repair() -> Dict[str, Any]:
    """
    Perform safe, offline-first repair actions:
    - Ensure venv packages are installed
    - Update/initialize git submodules
    Returns a dict with action results.
    """
    root = _repo_root()
    results: Dict[str, Any] = {}

    # pip install
    code, _, err = _run_cmd(
        [_wizard_python(), "-m", "pip", "install", "-r", str(_wizard_requirements())],
        cwd=root,
        timeout=600,
    )
    results["pip_install"] = {"ok": code == 0, "error": err.strip()[:160]}

    # git submodule update
    code2, _, err2 = _run_cmd(["git", "submodule", "update", "--init", "--recursive"], cwd=root, timeout=300)
    results["submodule_update"] = {"ok": code2 == 0, "error": err2.strip()[:160]}

    logger.info(
        f"[WIZ] Dev Recovery repair done: pip_ok={results['pip_install']['ok']} submodule_ok={results['submodule_update']['ok']}"
    )
    return results
