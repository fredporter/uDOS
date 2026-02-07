"""
OK Setup Helper - Install local AI stack for Vibe.

Installs:
  - mistral-vibe (Vibe CLI)
  - Ollama (if missing)
  - Recommended models: mistral-small2, mistral-large2, devstral-small-2

Updates core/config/ok_modes.json with recommended models.
"""

from __future__ import annotations

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Callable, List, Dict


def _default_logger(message: str) -> None:
    print(message)


def run_ok_setup(repo_root: Path, log: Callable[[str], None] | None = None) -> Dict[str, List[str]]:
    if log is None:
        log = _default_logger

    steps: List[str] = []
    warnings: List[str] = []

    def run_cmd(cmd: List[str], label: str) -> None:
        try:
            log(f"  • {label}")
            subprocess.run(cmd, check=False)
            steps.append(label)
        except Exception as exc:
            warnings.append(f"{label} failed: {exc}")

    venv_python = repo_root / ".venv" / "bin" / "python"
    pip_cmd = [str(venv_python), "-m", "pip"] if venv_python.exists() else [sys.executable, "-m", "pip"]

    run_cmd(pip_cmd + ["install", "mistral-vibe"], "Install Vibe CLI (mistral-vibe)")

    if not shutil.which("ollama"):
        if sys.platform == "darwin" and shutil.which("brew"):
            run_cmd(["brew", "install", "ollama"], "Install Ollama via Homebrew")
        else:
            warnings.append("Ollama not found. Install manually: https://ollama.com")

    if shutil.which("ollama"):
        models = [
            "mistral-small2",
            "mistral-large2",
            "devstral-small-2",
        ]
        for model in models:
            run_cmd(["ollama", "pull", model], f"Ollama pull {model}")
    else:
        warnings.append("Skipping model pulls (Ollama not installed).")

    # Update ok_modes.json
    try:
        config_path = repo_root / "core" / "config" / "ok_modes.json"
        config = {"modes": {}}
        if config_path.exists():
            config = json.loads(config_path.read_text())
        modes = config.setdefault("modes", {})
        ofvibe = modes.setdefault("ofvibe", {})
        models = ofvibe.setdefault("models", [])
        names = {m.get("name") for m in models if isinstance(m, dict)}
        for name, availability in [
            ("mistral-small2", ["core"]),
            ("mistral-large2", ["core"]),
            ("devstral-small-2", ["dev"]),
        ]:
            if name not in names:
                models.append({"name": name, "availability": availability})
        config_path.write_text(json.dumps(config, indent=2))
        steps.append("Updated ok_modes.json")
    except Exception as exc:
        warnings.append(f"Could not update ok_modes.json: {exc}")

    return {"steps": steps, "warnings": warnings}
