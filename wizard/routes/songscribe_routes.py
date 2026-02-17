"""
Songscribe routes for parsing and rendering Songscribe markdown.
"""

from typing import Any, Dict
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request

from wizard.services.library_manager_service import get_library_manager
from wizard.services.path_utils import get_memory_dir
from groovebox.wizard.services.songscribe_service import get_songscribe_service
from groovebox.transport.audio.groovebox import ImperialGroovebox

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


@router.post("/transport/bridge")
async def songscribe_transport_bridge(payload: Dict[str, Any]):
    text = _require_text(payload)
    cue = str(payload.get("cue") or "data").strip().lower()
    save_wav = bool(payload.get("save_wav", False))
    duration = float(payload.get("duration") or 2.0)

    engine = ImperialGroovebox()
    if cue == "handshake":
        samples = engine.handshake(is_initiator=bool(payload.get("is_initiator", True)))
    elif cue == "success":
        samples = engine.success()
    elif cue == "error":
        samples = engine.error()
    else:
        samples = engine.data_stream(duration=max(0.1, min(duration, 10.0)))

    pattern = service.to_pattern(text)
    output_wav = None
    if save_wav:
        out_dir = get_memory_dir() / "groovebox" / "transport"
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        out_path = out_dir / f"songscribe-{cue}-{stamp}.wav"
        output_wav = str(engine.save_wav(samples, str(out_path)))

    return {
        "status": "ok",
        "cue": cue,
        "sample_count": len(samples),
        "pattern": pattern,
        "wav_path": output_wav,
    }
