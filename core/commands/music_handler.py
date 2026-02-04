"""MUSIC command handler - Songscribe / Groovebox scaffolding."""

from typing import Dict, List
from pathlib import Path

from core.commands.base import BaseCommandHandler
from core.services.logging_service import get_logger, LogTags, get_repo_root

logger = get_logger("command-music")


class MusicHandler(BaseCommandHandler):
    """Handler for MUSIC command - Songscribe/Groovebox workflows."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle MUSIC commands.

        Syntax:
            MUSIC TRANSCRIBE <file.mp3>
            MUSIC TRANSCRIBE <youtube_url>
            MUSIC SEPARATE <file.mp3> --preset full_band
            MUSIC STEMS <file.mp3>
            MUSIC SCORE <file.mid>
            MUSIC IMPORT <file.mid>
        """
        if not self._extension_available():
            return {
                "status": "error",
                "message": "Groovebox/Songscribe extension not installed.",
                "suggestion": "Install the groovebox submodule or extension package, then retry.",
            }
        if not params:
            return self._help("Missing action.")

        action = params[0].lower()
        if action in {"help", "list"}:
            return self._help()

        if action in {"transcribe", "separate", "stems", "score", "import", "play"}:
            logger.info(f"{LogTags.LOCAL} MUSIC: Requested {action} {' '.join(params[1:])}")
            return {
                "status": "error",
                "message": (
                    "Songscribe container actions are not wired in the TUI yet. "
                    "Use Wizard endpoints (/api/songscribe/*, /api/groovebox/songscribe/parse) "
                    "or install/run the Songscribe container UI." 
                ),
                "requested": action,
                "params": params[1:],
            }

        return {
            "status": "error",
            "message": f"Unknown MUSIC action '{params[0]}'. Use MUSIC HELP for options.",
        }

    def _help(self, message: str = "") -> Dict:
        payload = {
            "status": "ok",
            "message": message or "MUSIC command help.",
            "syntax": [
                "MUSIC TRANSCRIBE <file.mp3>",
                "MUSIC TRANSCRIBE <youtube_url>",
                "MUSIC SEPARATE <file.mp3> --preset full_band",
                "MUSIC STEMS <file.mp3>",
                "MUSIC SCORE <file.mid>",
                "MUSIC IMPORT <file.mid>",
            ],
            "note": "Songscribe container wiring is pending in the TUI.",
        }
        if not message:
            payload.pop("message", None)
        return payload

    def _extension_available(self) -> bool:
        repo_root = get_repo_root()
        candidates = [
            repo_root / "groovebox",
            repo_root / "extensions" / "groovebox",
        ]
        return any(path.exists() for path in candidates)
