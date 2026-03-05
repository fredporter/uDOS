"""Bounded local script runner for offline runtime actions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


class SandboxError(RuntimeError):
    """Raised when a script cannot be executed safely."""


@dataclass
class ScriptSandbox:
    project_root: Path

    def run_script(self, path: str, timeout_seconds: int = 60) -> str:
        script_path = (self.project_root / path).resolve()
        if not script_path.exists():
            raise SandboxError(f"Script not found: {script_path}")
        if not str(script_path).startswith(str(self.project_root.resolve())):
            raise SandboxError(f"Script escapes project root: {script_path}")
        if script_path.suffix == ".py":
            cmd = [sys.executable, str(script_path)]
        elif script_path.suffix in {".sh", ".bash"}:
            cmd = ["bash", str(script_path)]
        else:
            raise SandboxError(f"Unsupported script type: {script_path.suffix}")

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            return f"[SANDBOX TIMEOUT] {exc}"
        return (
            f"[SANDBOX EXIT {proc.returncode}]\n\n"
            f"STDOUT:\n{proc.stdout}\n\n"
            f"STDERR:\n{proc.stderr}"
        )
