"""
Songscribe service wrapper for parsing Songscribe markdown and rendering Groovebox data.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.services.songscribe_parser import (
    SongscribeDocument,
    parse_songscribe,
    steps_to_events,
    to_ascii_grid,
    to_groovebox_pattern,
)
from wizard.services.logging_manager import get_logger

logger = get_logger("songscribe-service")


class SongscribeService:
    """Parse Songscribe markdown and expose rendering helpers."""

    def parse_document(self, text: Optional[str]) -> SongscribeDocument:
        if text is None:
            text = ""
        return parse_songscribe(text)

    def serialize_document(self, doc: SongscribeDocument) -> Dict[str, Any]:
        tracks = []
        for track in doc.tracks:
            tracks.append(
                {
                    "name": track.name,
                    "steps": track.steps,
                    "annotations": track.annotations,
                    "events": steps_to_events(track.steps),
                }
            )
        return {
            "meta": doc.meta,
            "tracks": tracks,
            "track_count": len(tracks),
        }

    def parse(self, text: Optional[str]) -> Dict[str, Any]:
        doc = self.parse_document(text)
        return self.serialize_document(doc)

    def render_ascii(self, text: Optional[str], width: int = 16) -> str:
        doc = self.parse_document(text)
        return to_ascii_grid(doc, width=width)

    def to_pattern(self, text: Optional[str]) -> Dict[str, Any]:
        doc = self.parse_document(text)
        return to_groovebox_pattern(doc)

    def parse_with_pattern(self, text: Optional[str], width: int = 16) -> Dict[str, Any]:
        doc = self.parse_document(text)
        payload = self.serialize_document(doc)
        payload["pattern"] = to_groovebox_pattern(doc)
        payload["ascii"] = to_ascii_grid(doc, width=width)
        return payload


def get_songscribe_service() -> SongscribeService:
    return SongscribeService()
