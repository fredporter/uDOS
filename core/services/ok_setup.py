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
import time
import threading
import urllib.request
from pathlib import Path
from typing import Callable, List, Dict

from core.tui.ui_elements import Spinner

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

    def ollama_running() -> bool:
        try:
            with urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=2):
                return True
        except Exception:
            return False

    def ensure_ollama_started() -> None:
        if ollama_running():
            return
        if sys.platform == "darwin" and os.path.exists("/Applications/Ollama.app"):
            run_cmd(["open", "-a", "Ollama"], "Start Ollama app")
        else:
            run_cmd(["ollama", "serve"], "Start Ollama daemon")
        # Allow the daemon to boot
        stop = threading.Event()
        spinner = Spinner(label="Waiting for Ollama", show_elapsed=True)
        thread = spinner.start_background(stop)
        for _ in range(10):
            if ollama_running():
                stop.set()
                thread.join(timeout=1)
                spinner.stop("Ollama ready")
                return
            time.sleep(0.5)
        stop.set()
        thread.join(timeout=1)
        spinner.stop("Ollama start timed out")

    if shutil.which("ollama"):
        ensure_ollama_started()
        models = [
            "mistral",
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
            ("mistral", ["core"]),
            ("devstral-small-2", ["dev"]),
        ]:
            if name not in names:
                models.append({"name": name, "availability": availability})
        config_path.write_text(json.dumps(config, indent=2))
        steps.append("Updated ok_modes.json")
    except Exception as exc:
        warnings.append(f"Could not update ok_modes.json: {exc}")

    return {"steps": steps, "warnings": warnings}
