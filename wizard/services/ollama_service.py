"""
Ollama Service
==============

Shared Ollama helpers for API communication, model management, and pull operations.
Used by both provider route factories.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import urllib.request
from typing import Any, Dict, List, Optional


# ════════════════════════════════════════════════════════════════════════════
# Ollama Host & API
# ════════════════════════════════════════════════════════════════════════════


def ollama_host() -> str:
    """Return Ollama API host from env or default."""
    return (os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")


def ollama_api_request(
    path: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 10
) -> Dict[str, Any]:
    """Make a request to the Ollama API."""
    url = f"{ollama_host()}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        method="POST" if data is not None else "GET",
        data=data,
        headers={"Content-Type": "application/json"} if data is not None else {},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def ollama_reachable() -> bool:
    """Check if Ollama API is reachable."""
    try:
        ollama_api_request("/api/tags")
        return True
    except Exception:
        return False


def list_local_models() -> List[str]:
    """List locally installed Ollama models."""
    try:
        resp = ollama_api_request("/api/tags")
        return [m.get("name") for m in resp.get("models", []) if m.get("name")]
    except Exception:
        return []


# ════════════════════════════════════════════════════════════════════════════
# Popular Models Catalog
# ════════════════════════════════════════════════════════════════════════════


POPULAR_MODELS: List[Dict[str, Any]] = [
    {
        "name": "mistral",
        "description": "Fast general purpose 7B model from Mistral AI",
        "size": "4.1GB",
        "category": "general",
    },
    {
        "name": "devstral-small-2",
        "description": "Mistral's lightweight coding assistant (10.7B)",
        "size": "8.7GB",
        "category": "coding",
    },
    {
        "name": "llama3.2",
        "description": "Meta's compact 3B instruction-tuned model",
        "size": "2.0GB",
        "category": "general",
    },
    {
        "name": "qwen3",
        "description": "Alibaba's multilingual reasoning model",
        "size": "4.7GB",
        "category": "general",
    },
    {
        "name": "codellama",
        "description": "Meta's code-specialized LLaMA model",
        "size": "3.8GB",
        "category": "coding",
    },
    {
        "name": "phi3",
        "description": "Microsoft's small but capable model (3.8B)",
        "size": "2.2GB",
        "category": "general",
    },
    {
        "name": "gemma2",
        "description": "Google's lightweight open model (2B)",
        "size": "1.6GB",
        "category": "general",
    },
    {
        "name": "deepseek-coder",
        "description": "DeepSeek's 6.7B code model",
        "size": "3.8GB",
        "category": "coding",
    },
]


def get_popular_models(include_installed: bool = True) -> List[Dict[str, Any]]:
    """Get list of popular Ollama models with optional install status."""
    models = [m.copy() for m in POPULAR_MODELS]
    if include_installed:
        installed = set(list_local_models())
        for m in models:
            m["installed"] = m["name"] in installed
    return models


# ════════════════════════════════════════════════════════════════════════════
# Pull Status Tracking
# ════════════════════════════════════════════════════════════════════════════


class PullStatusTracker:
    """Thread-safe pull status tracker for model downloads."""

    def __init__(self):
        self._status: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def set(self, model: str, **fields: Any) -> None:
        """Update pull status for a model."""
        with self._lock:
            current = self._status.get(model, {"model": model})
            current.update(fields)
            self._status[model] = current

    def get(self, model: str) -> Optional[Dict[str, Any]]:
        """Get pull status for a model."""
        with self._lock:
            return self._status.get(model)

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all pull statuses."""
        with self._lock:
            return dict(self._status)

    def clear(self, model: str) -> None:
        """Clear pull status for a model."""
        with self._lock:
            self._status.pop(model, None)


# Global tracker instance
_pull_tracker = PullStatusTracker()


def get_pull_tracker() -> PullStatusTracker:
    """Get the global pull status tracker."""
    return _pull_tracker


# ════════════════════════════════════════════════════════════════════════════
# Pull Operations
# ════════════════════════════════════════════════════════════════════════════


def pull_via_api(model: str, tracker: Optional[PullStatusTracker] = None) -> None:
    """Pull a model via Ollama API (streaming progress)."""
    tracker = tracker or _pull_tracker
    tracker.set(model, state="connecting", percent=0)
    try:
        url = f"{ollama_host()}/api/pull"
        data = json.dumps({"name": model}).encode("utf-8")
        req = urllib.request.Request(
            url,
            method="POST",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            for raw in resp:
                line = raw.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                if payload.get("error"):
                    tracker.set(model, state="error", error=payload.get("error"))
                    return
                total = payload.get("total")
                completed = payload.get("completed")
                percent = None
                if isinstance(total, (int, float)) and total:
                    percent = int((completed or 0) / total * 100)
                tracker.set(
                    model,
                    state="pulling",
                    status=payload.get("status"),
                    total=total,
                    completed=completed,
                    percent=percent,
                )
        tracker.set(model, state="done", percent=100, status="complete")
    except Exception as exc:
        tracker.set(model, state="error", error=str(exc))


def pull_via_cli(model: str, tracker: Optional[PullStatusTracker] = None) -> None:
    """Pull a model via Ollama CLI (fallback)."""
    tracker = tracker or _pull_tracker
    tracker.set(model, state="pulling", percent=None)
    percent_re = re.compile(r"(\d{1,3})%")
    try:
        process = subprocess.Popen(
            ["ollama", "pull", model],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for stream in (process.stdout, process.stderr):
            if not stream:
                continue
            for line in stream:
                match = percent_re.search(line)
                if match:
                    pct = min(max(int(match.group(1)), 0), 100)
                    tracker.set(model, percent=pct, status=line.strip())
        code = process.wait()
        if code == 0:
            tracker.set(model, state="done", percent=100, status="complete")
        else:
            tracker.set(model, state="error", error=f"ollama pull exited {code}")
    except Exception as exc:
        tracker.set(model, state="error", error=str(exc))


def start_pull(model: str, tracker: Optional[PullStatusTracker] = None) -> None:
    """Start pulling a model in a background thread.

    Prefers API for progress tracking; falls back to CLI if API unreachable.
    """
    tracker = tracker or _pull_tracker
    try:
        ollama_api_request("/api/tags")
        thread = threading.Thread(target=pull_via_api, args=(model, tracker), daemon=True)
    except Exception:
        if shutil.which("ollama"):
            thread = threading.Thread(target=pull_via_cli, args=(model, tracker), daemon=True)
        else:
            tracker.set(
                model,
                state="error",
                error="ollama CLI not found and Ollama API unreachable",
            )
            return
    thread.start()
