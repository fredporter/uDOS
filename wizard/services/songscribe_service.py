"""
Songscribe service wrapper for parsing Songscribe markdown, rendering Groovebox data, and audio transcription.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

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

    def transcribe_audio(
        self,
        audio_path: str | Path,
        output_dir: Optional[str | Path] = None,
        preset: str = "full_band",
        backends: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using ML backends.

        Args:
            audio_path: Path to audio file (mp3, wav, flac, ogg)
            output_dir: Output directory (default: memory/groovebox/transcriptions/{stem})
            preset: Transcription preset (solo, duet, small_band, full_band)
            backends: List of backends to use (demucs, basic-pitch, adtof)

        Returns:
            Transcription result dict with status, results from each backend
        """
        try:
            from library.songscribe.transcription import get_transcription_engine
            from core.services.logging_service import get_repo_root

            audio_path = Path(audio_path)

            if not output_dir:
                output_dir = get_repo_root() / "memory" / "groovebox" / "transcriptions" / audio_path.stem

            output_dir = Path(output_dir)

            engine = get_transcription_engine()
            result = engine.transcribe_audio(audio_path, output_dir, preset, backends)

            logger.info(f"[TRANSCRIPTION] Service: {audio_path.name} → {output_dir}")
            return result

        except ImportError as e:
            logger.error(f"[TRANSCRIPTION] Import error: {e}")
            return {
                "status": "error",
                "message": "Transcription backend not available",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"[TRANSCRIPTION] Error: {e}")
            return {
                "status": "error",
                "message": f"Transcription failed: {str(e)}",
                "error": str(e),
            }

    def transcription_status(self) -> Dict[str, Any]:
        """Get status of all transcription backends."""
        try:
            from library.songscribe.transcription import get_transcription_engine

            engine = get_transcription_engine()
            return engine.get_status()

        except ImportError:
            return {
                "status": "error",
                "message": "Transcription backend not available",
            }


def get_songscribe_service() -> SongscribeService:
    return SongscribeService()
