"""
Songscribe routes for parsing and rendering Songscribe markdown.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request

from wizard.services.library_manager_service import get_library_manager
from wizard.services.songscribe_service import get_songscribe_service

router = APIRouter(prefix="/api/songscribe", tags=["songscribe"])
service = get_songscribe_service()


def _require_text(payload: Dict[str, Any]) -> str:
    text = payload.get("text") or payload.get("songscribe") or payload.get("content")
    if not text or not str(text).strip():
        raise HTTPException(status_code=400, detail="Missing Songscribe text")
    return str(text)


@router.get("/health")
async def songscribe_health(request: Request):
    manager = get_library_manager()
    integration = manager.get_integration("songscribe")
    if not integration:
        return {"available": False, "installed": False, "enabled": False}
    return {
        "available": True,
        "name": integration.name,
        "version": integration.version,
        "path": str(integration.path),
        "installed": integration.installed,
        "enabled": integration.enabled,
        "last_checked": None,
    }


@router.post("/parse")
async def parse_songscribe(payload: Dict[str, Any]):
    text = _require_text(payload)
    return {
        "status": "ok",
        "document": service.parse(text),
    }


@router.post("/render")
async def render_songscribe(payload: Dict[str, Any]):
    text = _require_text(payload)
    fmt = str(payload.get("format") or "ascii").lower()
    try:
        width = int(payload.get("width") or 16)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid width")

    if fmt in {"ascii", "grid"}:
        output = service.render_ascii(text, width=width)
    elif fmt == "pattern":
        output = service.to_pattern(text)
    elif fmt == "document":
        output = service.parse(text)
    else:
        raise HTTPException(status_code=400, detail="Unsupported render format")

    return {
        "status": "ok",
        "format": fmt,
        "output": output,
    }


@router.post("/pattern")
async def songscribe_pattern(payload: Dict[str, Any]):
    text = _require_text(payload)
    return {
        "status": "ok",
        "pattern": service.to_pattern(text),
    }
