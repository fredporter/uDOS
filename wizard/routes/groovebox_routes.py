"""
Groovebox playback + configuration routes for Round 10.
"""

from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Request
from wizard.services.library_manager_service import get_library_manager

router = APIRouter(prefix="/api/groovebox", tags=["groovebox"])


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
