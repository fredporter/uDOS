"""
Groovebox playback + configuration routes for the v1.3 audio tooling lane.
"""

from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request
from wizard.services.library_manager_service import get_library_manager
from wizard.services.groovebox_service import get_groovebox_service
from wizard.services.songscribe_service import get_songscribe_service

router = APIRouter(prefix="/api/groovebox", tags=["groovebox"])
groovebox_service = get_groovebox_service()
songscribe_service = get_songscribe_service()


def _sample_playlists() -> List[Dict[str, str]]:
    return [
        {"name": "Synth Dawn", "tempo": "110", "mode": "minor", "duration": "2:18"},
        {"name": "Hyperlane Pulse", "tempo": "138", "mode": "Lydian", "duration": "3:04"},
        {"name": "Forest Circuit", "tempo": "96", "mode": "Aeolian", "duration": "2:45"},
    ]


def _sample_sequences() -> List[Dict[str, object]]:
    return [
        {
            "title": "Chord Bloom",
            "type": "pattern",
            "length": 8,
            "tracks": ["bass", "lead", "pad"],
            "last_updated": datetime.utcnow().isoformat(),
        },
        {
            "title": "Percussion Loop",
            "type": "sequence",
            "length": 16,
            "tracks": ["kick", "snare", "hats"],
            "last_updated": datetime.utcnow().isoformat(),
        },
    ]


@router.get("/playback")
async def playback_preview(request: Request):
    """
    Return playback preview data (waveform + current sample metadata).
    """
    return {
        "now_playing": {
            "title": "Groovebox Channel",
            "tempo": "120 BPM",
            "key": "C minor",
            "loop": "Arcade Strings",
            "waveform": "https://cdn.fredporter.com/groovebox/waveform.svg",
        },
        "playlists": _sample_playlists(),
        "sequences": _sample_sequences(),
    }


@router.get("/presets")
async def groovebox_presets(request: Request):
    """Return configuration presets for channels/sfx."""
    return {
        "presets": [
            {"name": "Arcade Mode", "colors": ["#ff3b30", "#ff9500", "#34c759"], "description": "Bright, punchy leads and percussive snap."},
            {"name": "Nebula Drift", "colors": ["#5e5ce6", "#0a84ff", "#64d2ff"], "description": "Ethereal pads with slow bloom."},
            {"name": "Analog Noir", "colors": ["#1c1c1e", "#8e8e93", "#ff2d55"], "description": "Moody synth waves and VHS grime."},
        ],
        "license": "Creative Commons Attribution 4.0",
    }


@router.get("/config")
async def groovebox_config(request: Request):
    """Return Groovebox config/settings used by the playback UI."""
    return {
        "master_volume": 0.78,
        "midi_export_enabled": True,
        "default_format": "wav",
        "monitoring": {
            "latency_ms": 14,
            "last_sync": datetime.utcnow().isoformat(),
        },
        "hotkeys": ["F1: Play", "F2: Stop", "F3: Record", "F4: Render"],
    }


@router.get("/songscribe")
async def songscribe_status(request: Request):
    """Expose Songscribe plugin status/integration info for Groovebox."""
    manager = get_library_manager()
    integration = manager.get_integration("songscribe")
    if not integration:
        return {"available": False}
    return {
        "available": True,
        "name": integration.name,
        "version": integration.version,
        "path": str(integration.path),
        "installed": integration.installed,
        "enabled": integration.enabled,
        "last_checked": None,
    }


@router.get("/patterns")
async def list_patterns(request: Request):
    """List stored Groovebox patterns."""
    return {"patterns": groovebox_service.list_patterns()}


@router.get("/patterns/{pattern_id}")
async def get_pattern(request: Request, pattern_id: str):
    """Return a single Groovebox pattern."""
    pattern = groovebox_service.get_pattern(pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return {"pattern": pattern}


@router.post("/pattern")
async def save_pattern(payload: Dict[str, Any]):
    """Save a Groovebox pattern payload to memory."""
    pattern = payload.get("pattern") if isinstance(payload, dict) else None
    if pattern is None:
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Invalid pattern payload")
        pattern = payload
    pattern_id = payload.get("pattern_id") or payload.get("id")
    source = payload.get("source")
    try:
        saved = groovebox_service.save_pattern(pattern, pattern_id=pattern_id, source=source)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "ok", "pattern": saved}


@router.post("/songscribe/parse")
async def songscribe_parse(payload: Dict[str, Any]):
    """Parse Songscribe markdown into Groovebox pattern + ASCII grid."""
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    text = payload.get("text") or payload.get("songscribe") or payload.get("content")
    if not text or not str(text).strip():
        raise HTTPException(status_code=400, detail="Missing Songscribe text")

    try:
        width = int(payload.get("width") or 16)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid width")

    save_flag = payload.get("save")
    if isinstance(save_flag, bool):
        save_pattern = save_flag
    elif save_flag is None:
        save_pattern = False
    else:
        save_pattern = str(save_flag).strip().lower() in {"1", "true", "yes", "y"}
    name_override = payload.get("name")
    pattern_id = payload.get("pattern_id")

    document = songscribe_service.parse(text)
    pattern = songscribe_service.to_pattern(text)
    if name_override:
        pattern["name"] = str(name_override)

    response: Dict[str, Any] = {
        "status": "ok",
        "document": document,
        "pattern": pattern,
        "ascii": songscribe_service.render_ascii(text, width=width),
    }

    if save_pattern:
        saved = groovebox_service.save_pattern(pattern, pattern_id=pattern_id, source="songscribe")
        response["pattern"] = saved
        response["saved"] = True
        response["pattern_id"] = saved.get("id")

    return response
