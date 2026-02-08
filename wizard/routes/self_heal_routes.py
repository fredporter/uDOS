"""
Self-Heal Routes
================

Expose diagnostics and guided repair actions for Wizard setup.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from wizard.providers.nounproject_client import (
    NounProjectClient,
    NounProjectConfig,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
)
from wizard.services.path_utils import get_repo_root
from wizard.services.port_manager import get_port_manager


DEFAULT_CATEGORIES = {
    "ui": ["check", "close", "menu", "plus", "minus"],
    "nav": ["arrow left", "arrow right", "arrow up", "arrow down"],
    "system": ["settings", "warning", "info", "alert"],
    "media": ["play", "pause", "stop", "record"],
}


class SeedRequest(BaseModel):
    categories: Optional[Dict[str, List[str]]] = None
    per_term: int = 2


class PullRequest(BaseModel):
    model: str


def _nounproject_client() -> NounProjectClient:
    return NounProjectClient(NounProjectConfig(name="nounproject"))


def _diagrams_root() -> Path:
    return (
        get_repo_root()
        / "core"
        / "framework"
        / "seed"
        / "bank"
        / "graphics"
        / "diagrams"
        / "svg"
        / "icons"
        / "nounproject"
    )


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "icon"


def _ollama_get(path: str) -> Optional[dict]:
    import urllib.request

    url = f"http://127.0.0.1:11434{path}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _ollama_models() -> List[str]:
    data = _ollama_get("/api/tags")
    if not data:
        return []
    models = []
    for entry in data.get("models", []):
        name = entry.get("name", "")
        if name:
            models.append(name)
    return models


def _normalize_model_name(name: str) -> str:
    return name.split(":")[0]


def _ensure_ollama_running() -> Dict[str, Optional[str]]:
    """Ensure Ollama daemon is running; attempt to start if needed."""
    if _ollama_get("/api/version"):
        return {"started": False, "method": "already-running"}

    started = False
    method = None
    error = None

    try:
        # macOS app launch if available
        if os.path.exists("/Applications/Ollama.app"):
            subprocess.Popen(["open", "-a", "Ollama"])
            started = True
            method = "open-app"
        else:
            # Fallback to CLI daemon
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            started = True
            method = "ollama-serve"
    except Exception as exc:
        error = str(exc)

    # Wait briefly for daemon
    if started:
        for _ in range(10):
            if _ollama_get("/api/version"):
                return {"started": True, "method": method}
            time.sleep(0.5)

    return {"started": started, "method": method, "error": error}


def _handle_provider_error(exc: Exception):
    if isinstance(exc, AuthenticationError):
        raise HTTPException(status_code=401, detail=str(exc))
    if isinstance(exc, RateLimitError):
        raise HTTPException(status_code=429, detail=str(exc))
    if isinstance(exc, QuotaExceededError):
        raise HTTPException(status_code=402, detail=str(exc))
    if isinstance(exc, ProviderError):
        raise HTTPException(status_code=400, detail=str(exc))
    raise HTTPException(status_code=500, detail=str(exc))


def create_self_heal_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/self-heal", tags=["self-heal"], dependencies=dependencies
    )

    @router.get("/status")
    async def status():
        env_admin_token = os.getenv("WIZARD_ADMIN_TOKEN", "").strip()
        noun_key = os.getenv("NOUNPROJECT_API_KEY", "").strip()
        noun_secret = os.getenv("NOUNPROJECT_API_SECRET", "").strip()
        noun_configured = bool(noun_key and noun_secret)

        noun_auth_ok = None
        noun_error = None
        if noun_configured:
            try:
                client = _nounproject_client()
                await client.authenticate()
                noun_auth_ok = True
            except Exception as exc:
                noun_auth_ok = False
                noun_error = str(exc)

        pm = get_port_manager()
        ollama_port_open = pm.is_port_open(11434)
        ollama_version = _ollama_get("/api/version")
        ollama_running = bool(ollama_version)
        models = _ollama_models() if ollama_running else []
        normalized = {_normalize_model_name(m) for m in models}
        required = ["mistral", "devstral-small-2"]
        missing = [m for m in required if m not in normalized]
        vibe_cli = bool(shutil.which("vibe"))

        next_steps = []
        if not env_admin_token:
            next_steps.append("Set WIZARD_ADMIN_TOKEN in the Wizard server environment.")
        if not ollama_running:
            next_steps.append("Run `ollama serve` or open the Ollama app.")
        if missing:
            next_steps.append("Run `ollama pull mistral` and `ollama pull devstral-small-2`.")
        if not noun_configured:
            next_steps.append("Set NOUNPROJECT_API_KEY and NOUNPROJECT_API_SECRET.")
        if noun_auth_ok is False:
            next_steps.append("Verify Noun Project credentials; auth failed.")

        return {
            "admin_token_present": bool(env_admin_token),
            "ollama": {
                "running": ollama_running,
                "port_open": ollama_port_open,
                "version": ollama_version,
                "models": models,
                "missing_models": missing,
            },
            "vibe_cli": {"installed": vibe_cli},
            "nounproject": {
                "configured": noun_configured,
                "auth_ok": noun_auth_ok,
                "error": noun_error,
            },
            "next_steps": next_steps,
        }

    @router.post("/ollama/pull")
    async def pull_model(payload: PullRequest):
        startup = _ensure_ollama_running()
        try:
            result = subprocess.run(
                ["ollama", "pull", payload.model],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="ollama not installed")

        return {
            "model": payload.model,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "startup": startup,
        }

    @router.post("/ok-setup")
    async def run_ok_setup_endpoint():
        try:
            from core.services.ok_setup import run_ok_setup
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"OK setup import failed: {exc}")
        result = run_ok_setup(get_repo_root())
        return result

    @router.post("/nounproject/seed")
    async def seed_icons(payload: SeedRequest):
        categories = payload.categories or DEFAULT_CATEGORIES
        per_term = max(1, min(payload.per_term, 5))
        dest_root = _diagrams_root()
        dest_root.mkdir(parents=True, exist_ok=True)

        client = _nounproject_client()
        try:
            await client.authenticate()
        except Exception as exc:
            _handle_provider_error(exc)

        added = []
        skipped = []
        errors = []

        for category, terms in categories.items():
            cat_dir = dest_root / category
            cat_dir.mkdir(parents=True, exist_ok=True)
            for term in terms:
                try:
                    result = await client.search(term=term, limit=10)
                except Exception as exc:
                    errors.append(f"{category}:{term} search failed: {exc}")
                    continue
                icons = (result.get("icons") or [])[:per_term]
                for icon in icons:
                    icon_id = icon.get("id")
                    if not icon_id:
                        continue
                    try:
                        download = await client.download(icon_id=int(icon_id), format="svg")
                        src_path = Path(download.get("path", ""))
                        if not src_path.exists():
                            errors.append(f"{category}:{term} {icon_id} missing cache file")
                            continue
                        file_name = f"{_slugify(term)}-{icon_id}.svg"
                        dest_path = cat_dir / file_name
                        if dest_path.exists():
                            skipped.append(str(dest_path))
                            continue
                        shutil.copyfile(src_path, dest_path)
                        added.append(str(dest_path))
                    except Exception as exc:
                        errors.append(f"{category}:{term} {icon_id} download failed: {exc}")

        return {
            "added": added,
            "skipped": skipped,
            "errors": errors,
            "root": str(dest_root),
        }

    return router
