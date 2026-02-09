"""
Transcription service scaffold for Songscribe container integration.

This is a lightweight wrapper that keeps the service path referenced by
library/songscribe/container.json valid while the full ML pipeline is
implemented in the Songscribe container.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from wizard.services.logging_api import get_logger
from wizard.services.library_manager_service import get_library_manager
from groovebox.wizard.services.songscribe_service import get_songscribe_service

logger = get_logger("transcription-service")


class TranscriptionService:
    """Scaffold for Songscribe transcription operations."""

    def __init__(self) -> None:
        self.songscribe = get_songscribe_service()

    def health(self) -> Dict[str, Any]:
        manager = get_library_manager()
        integration = manager.get_integration("songscribe")
        if not integration:
            return {"available": False, "installed": False, "enabled": False}
        return {
            "available": True,
            "name": integration.name,
            "version": integration.version,
            "installed": integration.installed,
            "enabled": integration.enabled,
            "path": str(integration.path),
        }

    def parse_songscribe(self, text: Optional[str]) -> Dict[str, Any]:
        return self.songscribe.parse(text)

    def render_songscribe(self, text: Optional[str], width: int = 16) -> Dict[str, Any]:
        return {
            "format": "ascii",
            "output": self.songscribe.render_ascii(text, width=width),
        }

    def to_pattern(self, text: Optional[str]) -> Dict[str, Any]:
        return self.songscribe.to_pattern(text)

    def transcribe(self, source: str, preset: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "message": "Songscribe ML transcription pipeline not wired yet.",
            "source": source,
            "preset": preset,
        }

    def separate(self, source: str, preset: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "message": "Songscribe stem separation not wired yet.",
            "source": source,
            "preset": preset,
        }

    def stems(self, source: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "message": "Songscribe stems export not wired yet.",
            "source": source,
        }

    def score(self, source: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "message": "Songscribe score export not wired yet.",
            "source": source,
        }


def get_transcription_service() -> TranscriptionService:
    return TranscriptionService()
