"""
OK Setup Helper - Install local AI stack for Vibe.

Installs:
  - mistral-vibe (Vibe CLI)
  - Ollama (if missing)
  - Recommended models: mistral-small2, mistral-large2, devstral-small-2  - Fallback model: qwen2.5:0.5b (lightweight open-source, 500MB)
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
from urllib.error import URLError, HTTPError
from pathlib import Path
from typing import Callable, List, Dict

from core.tui.ui_elements import Spinner

def _default_logger(message: str) -> None:
    print(message)


def _load_ok_modes_config_for_setup(config_path: Path) -> tuple[Dict[str, object], List[str]]:
    """Load ok_modes config with self-heal for empty/corrupt JSON."""
    warnings: List[str] = []
    config: Dict[str, object] = {"modes": {}}
    if not config_path.exists():
        return config, warnings

    try:
        loaded = json.loads(config_path.read_text())
        if isinstance(loaded, dict):
            return loaded, warnings
        warnings.append("ok_modes.json was non-object; reset to defaults")
        return config, warnings
    except Exception as exc:
        try:
            backup = config_path.with_suffix(f".invalid-{int(time.time())}.json")
            backup.write_text(config_path.read_text())
            warnings.append(
                f"Recovered invalid ok_modes.json; backup saved to {backup.name}"
            )
        except Exception:
            warnings.append("Recovered invalid ok_modes.json (backup unavailable)")
        warnings.append(f"ok_modes.json parse failed: {exc}")
        return config, warnings

def _format_bytes(num: int) -> str:
    if num <= 0:
        return "0B"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num)
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    return f"{size:.1f}{units[idx]}"


def _format_eta(seconds: float) -> str:
    if seconds <= 0:
        return "0s"
    secs = int(seconds)
    mins, sec = divmod(secs, 60)
    hrs, mins = divmod(mins, 60)
    if hrs > 0:
        return f"{hrs}h{mins:02d}m"
    if mins > 0:
        return f"{mins}m{sec:02d}s"
    return f"{sec}s"


def _lookup_installed_model_size(*names: str) -> int:
    """Return installed model size in bytes from Ollama /api/tags."""
    candidates = set()
    for name in names:
        if not name:
            continue
        norm = str(name).strip()
        if not norm:
            continue
        candidates.add(norm)
        if ":" not in norm:
            candidates.add(f"{norm}:latest")

    if not candidates:
        return 0

    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        models = payload.get("models") or []
        for model in models:
            if not isinstance(model, dict):
                continue
            model_name = str(model.get("name") or "").strip()
            if model_name in candidates:
                return int(model.get("size") or 0)
    except Exception:
        return 0
    return 0


def pull_ollama_model(
    model: str,
    log: Callable[[str], None],
    display_name: str | None = None,
    aliases: List[str] | None = None,
    stream_progress: bool = True,
) -> Dict[str, str]:
    """
    Pull an Ollama model via the local HTTP API with progress.

    Returns:
        {"success": "true|false", "name": used_name, "error": msg}
    """
    display = display_name or model
    candidates: List[str] = []
    for name in [model] + (aliases or []):
        if name and name not in candidates:
            candidates.append(name)

    def _pull(name: str) -> Dict[str, str]:
        start = time.time()
        progress_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame_idx = 0
        last_total = 0
        last_done = 0
        last_status = ""
        stream = bool(stream_progress and sys.stdout.isatty())

        def update_line(line: str) -> None:
            if not stream:
                return
            # ANSI clear avoids width-mismatch artifacts when terminal size
            # changes or Unicode widths are ambiguous across environments.
            sys.stdout.write("\r\033[2K" + line)
            sys.stdout.flush()

        def clear_line() -> None:
            if not stream:
                return
            sys.stdout.write("\r\033[2K")
            sys.stdout.flush()

        payload = json.dumps({"name": name, "stream": True}).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/pull",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                while True:
                    line = resp.readline()
                    if not line:
                        break
                    try:
                        data = json.loads(line.decode("utf-8").strip())
                    except Exception:
                        continue
                    if data.get("error"):
                        clear_line()
                        return {"success": "false", "name": name, "error": str(data["error"])}
                    status = data.get("status") or ""
                    total = int(data.get("total") or 0)
                    completed = int(data.get("completed") or 0)
                    last_total = total or last_total
                    last_done = completed or last_done
                    last_status = status or last_status
                    if stream:
                        frame = progress_frames[frame_idx % len(progress_frames)]
                        frame_idx += 1
                        elapsed = max(0.1, time.time() - start)
                        eta = ""
                        size = ""
                        pct = ""
                        if last_total:
                            pct = f"{int((last_done / last_total) * 100):d}%"
                            size = f"{_format_bytes(last_done)}/{_format_bytes(last_total)}"
                            rate = last_done / elapsed if last_done else 0
                            if rate > 0:
                                eta = f"ETA {_format_eta((last_total - last_done) / rate)}"
                        elif last_done:
                            size = f"{_format_bytes(last_done)}"
                        parts = [f"Ollama pull {display}", frame]
                        if pct:
                            parts.append(pct)
                        if size:
                            parts.append(size)
                        if eta:
                            parts.append(eta)
                        if not pct and last_status:
                            parts.append(last_status)
                        update_line(" ".join(parts))
        except (URLError, HTTPError) as exc:
            clear_line()
            return {"success": "false", "name": name, "error": str(exc)}
        except Exception as exc:
            clear_line()
            return {"success": "false", "name": name, "error": str(exc)}

        clear_line()
        elapsed = time.time() - start
        installed_size = _lookup_installed_model_size(display, name, model, *(aliases or []))
        size_bytes = installed_size or last_total
        size = _format_bytes(size_bytes) if size_bytes else "unknown size"
        log(f"✅ Ollama pull {display} ({size}, {_format_eta(elapsed)})")
        return {"success": "true", "name": name}

    for candidate in candidates:
        result = _pull(candidate)
        if result.get("success") == "true":
            return result
        err = result.get("error", "unknown error")
        log(f"  ⚠️  Ollama pull {display} failed using {candidate}: {err}")
    return {"success": "false", "name": model, "error": f"All pull candidates failed for {display}"}


def run_ok_setup(
    repo_root: Path,
    log: Callable[[str], None] | None = None,
    models: List[str] | None = None,
) -> Dict[str, List[str]]:
    if log is None:
        log = _default_logger
    interactive_output = log is _default_logger

    steps: List[str] = []
    warnings: List[str] = []
    if models is None:
        models = [
            {"name": "mistral-small2", "pull": "mistral-small", "aliases": ["mistral-small2", "mistral-small:latest"]},
            {"name": "mistral-large2", "pull": "mistral-large", "aliases": ["mistral-large2", "mistral-large:latest"]},
            {"name": "devstral-small-2", "pull": "devstral-small-2", "aliases": ["devstral-small-2"]},
            {"name": "qwen2.5:0.5b", "pull": "qwen2.5:0.5b", "aliases": ["qwen2.5:0.5b"]},
        ]

    def run_cmd(cmd: List[str], label: str, quiet: bool = True, use_spinner: bool = True) -> bool:
        spinner = None
        stop = threading.Event()
        thread = None
        success = False
        spinner_active = bool(use_spinner and interactive_output and sys.stdout.isatty())
        if spinner_active:
            spinner = Spinner(label=label, show_elapsed=True)
            thread = spinner.start_background(stop)
        try:
            if not spinner_active:
                log(f"  • {label}")
            proc = subprocess.run(
                cmd,
                check=False,
                stdout=subprocess.PIPE if quiet else None,
                stderr=subprocess.PIPE if quiet else None,
                text=True,
            )
            if proc.returncode != 0:
                err = (proc.stderr or proc.stdout or "").strip()
                warnings.append(f"{label} failed{': ' + err if err else ''}")
                return False
            steps.append(label)
            success = True
            return True
        except Exception as exc:
            warnings.append(f"{label} failed: {exc}")
            return False
        finally:
            if spinner:
                stop.set()
                if thread:
                    thread.join(timeout=1)
                status = "✅" if success else "⚠️"
                spinner.stop(f"{status} {label}")

    venv_python = repo_root / "venv" / "bin" / "python"
    pip_cmd = [str(venv_python), "-m", "pip"] if venv_python.exists() else [sys.executable, "-m", "pip"]

    run_cmd(pip_cmd + ["install", "-q", "mistral-vibe"], "Install Vibe CLI (mistral-vibe)")

    if not shutil.which("ollama"):
        if sys.platform == "darwin" and shutil.which("brew"):
            run_cmd(["brew", "install", "ollama", "--quiet"], "Install Ollama via Homebrew")
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
            run_cmd(["open", "-a", "Ollama"], "Start Ollama app", quiet=True)
        else:
            try:
                log("  • Start Ollama daemon")
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                steps.append("Start Ollama daemon")
            except Exception as exc:
                warnings.append(f"Start Ollama daemon failed: {exc}")
        # Allow the daemon to boot
        spinner = None
        stop = threading.Event()
        thread = None
        if interactive_output and sys.stdout.isatty():
            spinner = Spinner(label="Waiting for Ollama", show_elapsed=True)
            thread = spinner.start_background(stop)
        else:
            log("  • Waiting for Ollama")
        for _ in range(10):
            if ollama_running():
                stop.set()
                if thread:
                    thread.join(timeout=1)
                if spinner:
                    spinner.stop("Ollama ready")
                else:
                    log("  ✓ Ollama ready")
                return
            time.sleep(0.5)
        stop.set()
        if thread:
            thread.join(timeout=1)
        if spinner:
            spinner.stop("Ollama start timed out")
        else:
            log("  ⚠️  Ollama start timed out")

    pulled_names: List[str] = []
    if shutil.which("ollama"):
        ensure_ollama_started()
        for model in models:
            if isinstance(model, dict):
                display = model.get("name") or ""
                pull_name = model.get("pull") or display
                aliases = model.get("aliases") or []
            else:
                display = str(model)
                pull_name = display
                aliases = []
            if not pull_name:
                continue
            result = pull_ollama_model(
                pull_name,
                log=log,
                display_name=display,
                aliases=[name for name in aliases if name != pull_name],
                stream_progress=interactive_output,
            )
            if result.get("success") == "true":
                steps.append(f"Ollama pull {display}")
                pulled_names.append(result.get("name") or pull_name)
            else:
                warnings.append(result.get("error", f"Ollama pull {display} failed"))
    else:
        warnings.append("Skipping model pulls (Ollama not installed).")

    # Update ok_modes.json
    try:
        config_path = repo_root / "core" / "config" / "ok_modes.json"
        config, load_warnings = _load_ok_modes_config_for_setup(config_path)
        warnings.extend(load_warnings)
        modes = config.setdefault("modes", {})
        ofvibe = modes.setdefault("ofvibe", {})
        models = ofvibe.setdefault("models", [])
        default_models = ofvibe.setdefault("default_models", {})
        names = {m.get("name") for m in models if isinstance(m, dict)}
        if pulled_names:
            for pulled in pulled_names:
                if pulled and pulled not in names:
                    models.append({"name": pulled, "availability": ["core"]})
        else:
            for name, availability in [
                ("mistral-small2", ["core"]),
                ("mistral-large2", ["core"]),
                ("devstral-small-2", ["dev"]),
                ("qwen2.5:0.5b", ["core", "fallback"]),
            ]:
                if name not in names:
                    models.append({"name": name, "availability": availability})
        default_models.setdefault("core", "mistral-small2")
        default_models.setdefault("dev", "devstral-small-2")
        default_models.setdefault("fallback", "qwen2.5:0.5b")
        config_path.write_text(json.dumps(config, indent=2))
        steps.append("Updated ok_modes.json")
    except Exception as exc:
        warnings.append(f"Could not update ok_modes.json: {exc}")

    return {"steps": steps, "warnings": warnings}
