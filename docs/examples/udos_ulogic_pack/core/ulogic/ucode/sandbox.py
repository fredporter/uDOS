from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess

class SandboxError(RuntimeError): pass

@dataclass
class ScriptSandbox:
    project_root: Path

    def run_script(self, path: str, timeout_seconds: int = 60) -> str:
        p = (self.project_root / path).resolve()
        if not p.exists():
            raise SandboxError(f"Script not found: {p}")
        if p.suffix == ".py":
            cmd = ["python", str(p)]
        elif p.suffix in (".sh", ".bash"):
            cmd = ["bash", str(p)]
        else:
            raise SandboxError(f"Unsupported script type: {p.suffix}")
        try:
            proc = subprocess.run(cmd, cwd=str(self.project_root), capture_output=True, text=True, timeout=timeout_seconds)
        except subprocess.TimeoutExpired as e:
            return f"[SANDBOX TIMEOUT] {e}\n"
        return f"[SANDBOX EXIT {proc.returncode}]\n\nSTDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}\n"
