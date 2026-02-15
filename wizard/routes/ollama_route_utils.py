"""
Shared route helpers for Ollama-related API endpoints.
"""

from __future__ import annotations

import subprocess
from typing import Any, Dict, List

from fastapi import HTTPException

from wizard.services.ollama_service import ollama_api_request, ollama_host


def validate_model_name(model: str) -> None:
    """Validate model parameter for Ollama endpoints."""
    if not model or not isinstance(model, str):
        raise HTTPException(status_code=400, detail="model parameter required")
    if not all(c.isalnum() or c in "-_:." for c in model):
        raise HTTPException(status_code=400, detail="Invalid model name")


def _parse_ollama_list(stdout: str) -> List[Dict[str, Any]]:
    """Parse `ollama list` output into model payload rows."""
    lines = (stdout or "").strip().split("\n")
    if len(lines) < 2:
        return []

    models: List[Dict[str, Any]] = []
    for line in lines[1:]:  # Skip header row
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        models.append(
            {
                "name": parts[0],
                "id": parts[0],
                "size": parts[1] if len(parts) > 1 else "?",
                "modified": " ".join(parts[2:]) if len(parts) > 2 else "",
            }
        )
    return models


def get_installed_ollama_models_payload() -> Dict[str, Any]:
    """
    Return installed Ollama models, preferring CLI and falling back to API.
    Preserves existing response shape used by provider endpoints.
    """
    try:
        response = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        if response.returncode == 0:
            models = _parse_ollama_list(response.stdout)
            return {"success": True, "models": models, "count": len(models)}
        return {
            "success": False,
            "error": "Ollama not reachable. Is it running?",
            "help": "Start Ollama: ollama serve",
        }
    except FileNotFoundError:
        try:
            data = ollama_api_request("/api/tags")
            models = []
            for item in data.get("models", []):
                name = item.get("name") or ""
                models.append(
                    {
                        "name": name,
                        "id": name,
                        "size": item.get("size", "?"),
                        "modified": item.get("modified_at", ""),
                    }
                )
            return {"success": True, "models": models, "count": len(models)}
        except Exception as exc:
            return {
                "success": False,
                "error": "ollama CLI not found",
                "help": f"Install Ollama or set OLLAMA_HOST (current: {ollama_host()})",
                "detail": str(exc),
            }
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def remove_ollama_model_payload(model: str) -> Dict[str, Any]:
    """Remove an installed model and return API response payload."""
    validate_model_name(model)
    try:
        result = subprocess.run(
            ["ollama", "rm", model], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return {"success": True, "message": f"Removed {model}"}
        return {"success": False, "error": result.stderr}
    except FileNotFoundError:
        return {"success": False, "error": "ollama CLI not found"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}

