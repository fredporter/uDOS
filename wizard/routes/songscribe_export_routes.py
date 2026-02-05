"""
Songscribe export and synthesis routes.

API endpoints for:
- Pattern → MIDI export
- Pattern → WAV synthesis (via MIDI)
- Pattern → PDF/MusicXML generation
- Batch operations
"""

from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request

from wizard.services.library_manager_service import get_library_manager
from wizard.services.groovebox_service import get_groovebox_service
from wizard.services.path_utils import get_memory_dir
from library.songscribe.converters import MIDIConverter, GrooveboxConverter
from library.songscribe.schemas import dict_to_pattern

router = APIRouter(prefix="/api/songscribe/export", tags=["songscribe-export"])
groovebox_service = get_groovebox_service()


def _memory_export_dir() -> Path:
    """Get the export storage directory."""
    export_dir = get_memory_dir() / "groovebox" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


@router.post("/midi")
async def export_to_midi(payload: Dict[str, Any]):
    """
    Export pattern to MIDI file.

    Request body:
    {
        "pattern_id": "cosmic-dream",  # or pattern data directly
        "pattern": {...}  # if providing raw pattern
    }

    Response:
    {
        "status": "ok",
        "format": "midi",
        "file": "exports/pattern-name.mid",
        "url": "/api/files/exports/pattern-name.mid"
    }
    """
    pattern_id = payload.get("pattern_id")
    pattern_data = payload.get("pattern")

    # Load pattern if ID provided
    if pattern_id and not pattern_data:
        pattern_data = groovebox_service.get_pattern(str(pattern_id))
        if not pattern_data:
            raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' not found")

    if not pattern_data:
        raise HTTPException(status_code=400, detail="Missing pattern_id or pattern data")

    try:
        # Convert groovebox format to Songscribe pattern
        pattern = GrooveboxConverter.groovebox_to_pattern(pattern_data)

        # Export to MIDI
        export_dir = _memory_export_dir()
        midi_path = export_dir / f"{pattern.id}.mid"

        MIDIConverter.pattern_to_midi(pattern, midi_path)

        return {
            "status": "ok",
            "format": "midi",
            "file": f"exports/{pattern.id}.mid",
            "url": f"/api/files/exports/{pattern.id}.mid",
            "pattern_id": pattern.id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MIDI export failed: {str(e)}")


@router.post("/wav")
async def export_to_wav(payload: Dict[str, Any]):
    """
    Export pattern to WAV audio file.

    Requires: FluidSynth or external synthesizer installed.

    Request body:
    {
        "pattern_id": "cosmic-dream",
        "soundfont": "optional/path/to/soundfont.sf2",
        "sample_rate": 44100
    }

    Response:
    {
        "status": "pending|error",
        "message": "WAV synthesis requires external synthesizer..."
    }
    """
    pattern_id = payload.get("pattern_id")

    if not pattern_id:
        raise HTTPException(status_code=400, detail="Missing pattern_id")

    pattern_data = groovebox_service.get_pattern(str(pattern_id))
    if not pattern_data:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' not found")

    return {
        "status": "pending",
        "message": "WAV synthesis requires FluidSynth or external synthesizer. "
                   "Install: brew install fluidsynth (macOS) or apt-get install fluidsynth (Linux)",
        "pattern_id": pattern_id,
        "error": "NOT_IMPLEMENTED",
    }


@router.post("/pdf")
async def export_to_pdf(payload: Dict[str, Any]):
    """
    Export pattern to PDF sheet music.

    Requires: music21 or similar notation library.

    Request body:
    {
        "pattern_id": "cosmic-dream",
        "staff_type": "standard|guitar|drum"
    }

    Response:
    {
        "status": "pending|error",
        "message": "PDF generation requires music notation library..."
    }
    """
    pattern_id = payload.get("pattern_id")
    staff_type = payload.get("staff_type", "standard")

    if not pattern_id:
        raise HTTPException(status_code=400, detail="Missing pattern_id")

    return {
        "status": "pending",
        "message": "PDF sheet music generation requires music21. "
                   "Install: pip install music21",
        "pattern_id": pattern_id,
        "staff_type": staff_type,
        "error": "NOT_IMPLEMENTED",
    }


@router.post("/musicxml")
async def export_to_musicxml(payload: Dict[str, Any]):
    """
    Export pattern to MusicXML format.

    MusicXML is compatible with:
    - MuseScore
    - Finale
    - Sibelius
    - Dorico
    - Lilypond (via conversion)

    Request body:
    {
        "pattern_id": "cosmic-dream"
    }

    Response:
    {
        "status": "pending",
        "message": "MusicXML generation not yet implemented"
    }
    """
    pattern_id = payload.get("pattern_id")

    if not pattern_id:
        raise HTTPException(status_code=400, detail="Missing pattern_id")

    return {
        "status": "pending",
        "message": "MusicXML generation not yet implemented",
        "pattern_id": pattern_id,
        "error": "NOT_IMPLEMENTED",
    }


@router.get("/formats")
async def supported_formats(request: Request):
    """List supported export formats and their requirements."""
    return {
        "formats": [
            {
                "name": "MIDI",
                "extension": ".mid",
                "status": "ready",
                "requires": [],
                "description": "Standard MIDI 1.0 file format"
            },
            {
                "name": "WAV",
                "extension": ".wav",
                "status": "pending",
                "requires": ["fluidsynth"],
                "description": "Audio waveform (PCM)",
                "install_help": "brew install fluidsynth (macOS) or apt-get install fluidsynth (Linux)"
            },
            {
                "name": "PDF",
                "extension": ".pdf",
                "status": "pending",
                "requires": ["music21"],
                "description": "Sheet music notation",
                "install_help": "pip install music21"
            },
            {
                "name": "MusicXML",
                "extension": ".xml",
                "status": "pending",
                "requires": [],
                "description": "Universal music notation format"
            },
            {
                "name": "Groovebox Pattern",
                "extension": ".json",
                "status": "ready",
                "requires": [],
                "description": "Stored pattern format"
            },
        ]
    }


__all__ = ["router"]
