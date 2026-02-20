"""MUSIC command handler - Songscribe / Groovebox integration."""

from typing import Dict, List, Any, Optional
from pathlib import Path

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger, LogTags, get_repo_root
from core.services.error_contract import CommandError

logger = get_logger("command-music")


class MusicHandler(BaseCommandHandler):
    """Handler for MUSIC command - Songscribe/Groovebox workflows."""

    def __init__(self):
        super().__init__()
        self.groovebox_service = None
        self.songscribe_service = None
        self._init_services()

    def _init_services(self) -> None:
        """Lazy-initialize services."""
        try:
            from groovebox.wizard.services.groovebox_service import get_groovebox_service
            self.groovebox_service = get_groovebox_service()
        except (ImportError, Exception):
            pass

        try:
            from groovebox.wizard.services.songscribe_service import get_songscribe_service
            self.songscribe_service = get_songscribe_service()
        except (ImportError, Exception):
            pass

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle MUSIC commands.

        Extended implementation for Phase 2:

        Playback:
            MUSIC PLAY <pattern_id> [--loop N]
            MUSIC STOP
            MUSIC RECORD <pattern_id> [--length N]

        Transcription (scaffolded):
            MUSIC TRANSCRIBE <file.mp3> [--preset solo|duet|small_band|full_band]
            MUSIC SEPARATE <file.mp3> [--preset ...]
            MUSIC STEMS <file.mp3>

        Import/Export (ready):
            MUSIC IMPORT <file.mid> [AS pattern_id]
            MUSIC EXPORT <pattern_id> --format midi|wav|pdf
            MUSIC RENDER <pattern_id> [--format wav|pdf|musicxml]

        Pattern Management (ready):
            MUSIC LIST [--sort name|tempo|date]
            MUSIC SHOW <pattern_id> [--width 16|32]
            MUSIC SAVE <pattern_id>
            MUSIC DELETE <pattern_id>

        Synthesis (ready):
            MUSIC SYNTH <preset|config> [options...]
            MUSIC SCALE <root> <mode> [--octave N] [--length N]
            MUSIC SCORE <midi> [--staff standard|guitar|drum]

        Utility:
            MUSIC STATUS
            MUSIC HELP [command]
        """
        if not params:
            return self._help("Missing action.")

        action = params[0].upper()
        args = params[1:]

        # Route to handler
        handler_name = f"_handle_{action.lower()}"
        if hasattr(self, handler_name):
            try:
                handler = getattr(self, handler_name)
                result = handler(args, grid, parser)
                result.setdefault("status", "ok")
                return result
            except Exception as e:
                logger.error(f"{LogTags.LOCAL} MUSIC {action} failed: {e}")
                raise CommandError(
                    code="ERR_RUNTIME_UNEXPECTED",
                    message=f"Command failed: {str(e)}",
                    recovery_hint="Check Groovebox service",
                    level="ERROR",
                    cause=e,
                )
        else:
            return self._help(f"Unknown action: {action}")

    def _handle_help(self, args: List[str], grid=None, parser=None) -> Dict:
        """MUSIC HELP [command]"""
        from library.songscribe.cli import get_command, list_commands

        if args:
            cmd_name = args[0].upper()
            cmd = get_command(cmd_name)
            if cmd:
                return {
                    "status": "ok",
                    "data": {
                        "name": cmd.name,
                        "description": cmd.description,
                        "syntax": cmd.syntax,
                        "examples": cmd.examples,
                    },
                }
            else:
                return {"status": "ok", "message": f"Command not found: {cmd_name}"}
        else:
            commands = list_commands()
            return {
                "status": "ok",
                "data": {
                    "total": len(commands),
                    "commands": [
                        {"name": c.name, "description": c.description}
                        for c in commands
                    ],
                },
            }

    def _handle_status(self, args: List[str], grid=None, parser=None) -> Dict:
        """MUSIC STATUS"""
        try:
            from library.songscribe.synthesis import get_wav_synthesizer
            from library.songscribe.notation import get_pdf_notation_engine

            synth = get_wav_synthesizer().get_status()
            notation = get_pdf_notation_engine().get_status()

            patterns = []
            if self.groovebox_service:
                patterns = self.groovebox_service.list_patterns()

            return {
                "status": "ok",
                "data": {
                    "groovebox": {
                        "available": self.groovebox_service is not None,
                        "patterns": len(patterns),
                    },
                    "songscribe": {"available": self.songscribe_service is not None},
                    "synthesis": synth,
                    "notation": notation,
                },
            }
        except Exception as e:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(e),
                recovery_hint="Check Music services",
                level="ERROR",
                cause=e,
            )

    def _handle_list(self, args: List[str], grid=None, parser=None) -> Dict:
        """MUSIC LIST [--sort name|tempo|date]"""
        if not self.groovebox_service:
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message="Groovebox service not available",
                recovery_hint="Check Groovebox service installation",
                level="ERROR",
            )

        try:
            patterns = self.groovebox_service.list_patterns()
            sort_key = "name"

            if "--sort" in args:
                idx = args.index("--sort")
                if idx + 1 < len(args):
                    sort_key = args[idx + 1].lower()

            if sort_key == "tempo":
                patterns = sorted(patterns, key=lambda p: p.get("tempo", 0), reverse=True)
            elif sort_key == "date":
                patterns = sorted(patterns, key=lambda p: p.get("updated_at", ""), reverse=True)
            else:
                patterns = sorted(patterns, key=lambda p: p.get("name", "").lower())

            return {"status": "ok", "data": {"total": len(patterns), "patterns": patterns}}
        except Exception as e:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(e),
                recovery_hint="Check Groovebox service",
                level="ERROR",
                cause=e,
            )

    def _handle_show(self, args: List[str], grid=None, parser=None) -> Dict:
        """MUSIC SHOW <pattern_id> [--width 16|32]"""
        if not self.groovebox_service:
            return {"status": "error", "message": "Groovebox service not available"}

        if not args:
            return {"status": "error", "message": "Missing pattern_id"}

        try:
            pattern_id = args[0]
            width = 16

            if "--width" in args:
                idx = args.index("--width")
                if idx + 1 < len(args):
                    try:
                        width = int(args[idx + 1])
                    except ValueError:
                        pass

            pattern = self.groovebox_service.get_pattern(pattern_id)
            if not pattern:
                return {"status": "error", "message": f"Pattern not found: {pattern_id}"}

            # Render ASCII grid
            if self.songscribe_service:
                ascii_grid = self.songscribe_service.render_ascii(
                    self._pattern_to_songscribe(pattern), width=width
                )
            else:
                ascii_grid = "[ASCII rendering requires Songscribe service]"

            return {
                "status": "ok",
                "data": {"pattern_id": pattern_id, "ascii": ascii_grid, "width": width},
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_export(self, args: List[str], grid=None, parser=None) -> Dict:
        """MUSIC EXPORT <pattern_id> --format midi|wav|pdf"""
        if not self.groovebox_service:
            return {"status": "error", "message": "Groovebox service not available"}

        if not args:
            return {"status": "error", "message": "Missing pattern_id"}

        pattern_id = args[0]
        fmt = "midi"

        if "--format" in args:
            idx = args.index("--format")
            if idx + 1 < len(args):
                fmt = args[idx + 1].lower()

        try:
            from library.songscribe.converters import (
                MIDIConverter, WAVConverter, PDFConverter, GrooveboxConverter
            )
            from library.songscribe.schemas import dict_to_pattern

            pattern_data = self.groovebox_service.get_pattern(pattern_id)
            if not pattern_data:
                return {"status": "error", "message": f"Pattern not found: {pattern_id}"}

            pattern = dict_to_pattern(pattern_data)
            export_dir = self.groovebox_service.pattern_root.parent / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)

            if fmt == "midi":
                output = export_dir / f"{pattern_id}.mid"
                MIDIConverter.pattern_to_midi(pattern, output)
                return {
                    "status": "ok",
                    "message": f"Exported: {output}",
                    "data": {"file": str(output), "format": "midi"},
                }
            elif fmt == "wav":
                output = export_dir / f"{pattern_id}.wav"
                midi_tmp = export_dir / f".{pattern_id}.tmp.mid"
                MIDIConverter.pattern_to_midi(pattern, midi_tmp)
                WAVConverter.midi_to_wav(midi_tmp, output)
                midi_tmp.unlink()
                return {
                    "status": "ok",
                    "message": f"Exported: {output}",
                    "data": {"file": str(output), "format": "wav"},
                }
            elif fmt == "pdf":
                output = export_dir / f"{pattern_id}.pdf"
                PDFConverter.pattern_to_pdf(pattern, output)
                return {
                    "status": "ok",
                    "message": f"Exported: {output}",
                    "data": {"file": str(output), "format": "pdf"},
                }
            else:
                return {"status": "error", "message": f"Unknown format: {fmt}"}

        except Exception as e:
            logger.error(f"{LogTags.LOCAL} MUSIC EXPORT failed: {e}")
            return {"status": "error", "message": str(e)}

    def _handle_transcribe(self, args: List[str], grid=None, parser=None) -> Dict:
        """
        MUSIC TRANSCRIBE <file> [--preset solo|duet|small_band|full_band]

        Transcribe audio using ML backends:
        - demucs: instrument separation
        - basic-pitch: audio-to-MIDI
        - adtof: drum transcription
        """
        if not args:
            return {"status": "error", "message": "Missing audio file"}

        audio_file = Path(args[0])
        if not audio_file.exists():
            return {"status": "error", "message": f"Audio file not found: {audio_file}"}

        # Extract preset if provided
        preset = "full_band"
        if "--preset" in args:
            idx = args.index("--preset")
            if idx + 1 < len(args):
                preset = args[idx + 1]

        # Create output directory
        repo_root = get_repo_root()
        output_dir = repo_root / "memory" / "groovebox" / "transcriptions" / audio_file.stem

        try:
            from library.songscribe.transcription import get_transcription_engine

            engine = get_transcription_engine()
            result = engine.transcribe_audio(audio_file, output_dir, preset)

            logger.info(
                f"[TRANSCRIPTION] Completed: {audio_file.name}",
                tags=[LogTags.CLOUD]
            )

            return {
                "status": result.get("status", "error"),
                "message": result.get("message", "Transcription failed"),
                "audio_file": str(audio_file),
                "output_dir": str(output_dir),
                "preset": preset,
                "results": result.get("results", {}),
            }

        except ImportError:
            return {
                "status": "error",
                "message": "Transcription backend not available",
                "note": "Install: pip install demucs basic-pitch adtof",
                "audio_file": str(audio_file),
            }
        except Exception as e:
            logger.error(f"[TRANSCRIPTION] Error: {e}")
            return {
                "status": "error",
                "message": f"Transcription failed: {str(e)}",
                "audio_file": str(audio_file),
            }

    def _handle_play(self, args: List[str], grid=None, parser=None) -> Dict:
        """
        MUSIC PLAY <pattern_id> [--loop N]

        Play a stored Groovebox pattern.
        Requires: Audio playback engine (not yet wired to TUI)
        """
        if not args:
            return {"status": "error", "message": "Missing pattern_id"}

        pattern_id = args[0]
        loop_count = None

        # Extract loop count if provided
        if "--loop" in args:
            try:
                idx = args.index("--loop")
                if idx + 1 < len(args):
                    loop_count = int(args[idx + 1])
            except (IndexError, ValueError):
                pass

        # Check if pattern exists in Groovebox
        if self.groovebox_service:
            pattern = self.groovebox_service.get_pattern(pattern_id)
            if not pattern:
                return {
                    "status": "error",
                    "message": f"Pattern not found: {pattern_id}",
                }

        return {
            "status": "error",
            "message": "PLAY backend unavailable",
            "note": "Install/wire Groovebox playback service, or use MUSIC EXPORT <pattern_id> --format wav and play externally.",
            "pattern_id": pattern_id,
            "loop_count": loop_count,
        }

    def _help(self, message: str = None) -> Dict:
        """Return help text."""
        help_text = """MUSIC Command Structure:

Patterns:
  MUSIC LIST              - List all patterns
  MUSIC SHOW <id>         - Display pattern
  MUSIC SAVE <id>         - Save pattern
  MUSIC EXPORT <id> --format midi|wav|pdf

Playback (pending):
  MUSIC PLAY <id>         - Play pattern
  MUSIC STOP              - Stop playback

Transcription (pending):
  MUSIC TRANSCRIBE <file> - Transcribe audio

Utility:
  MUSIC STATUS            - Check status
  MUSIC HELP [cmd]        - Show help

Use:  MUSIC HELP <command>  for detailed syntax
"""
        return {
            "status": "ok",
            "message": message or help_text,
        }

    def _help(self, message: str = None) -> Dict:
        """Return help text."""
        help_text = """MUSIC Command Structure:

Patterns:
  MUSIC LIST              - List all patterns
  MUSIC SHOW <id>         - Display pattern
  MUSIC SAVE <id>         - Save pattern
  MUSIC EXPORT <id> --format midi|wav|pdf

Playback (pending):
  MUSIC PLAY <id>         - Play pattern
  MUSIC STOP              - Stop playback

Transcription (pending):
  MUSIC TRANSCRIBE <file> - Transcribe audio

Utility:
  MUSIC STATUS            - Check status
  MUSIC HELP [cmd]        - Show help

Use:  MUSIC HELP <command>  for detailed syntax
"""
        return {
            "status": "ok",
            "message": message or help_text,
        }

    def _pattern_to_songscribe(self, pattern_data: Dict) -> str:
        """Convert stored pattern to Songscribe markdown."""
        lines = [
            f"Title: {pattern_data.get('name', 'Untitled')}",
            f"Tempo: {pattern_data.get('tempo', 120)}",
        ]

        for track in pattern_data.get("tracks", []):
            lines.append(f"\nTrack: {track.get('name', 'unknown')}")
            steps = []
            for step in track.get("steps", []):
                if isinstance(step, dict):
                    velocity = step.get("velocity", 100)
                    accent = 0x80 if step.get("accent") else 0x00
                    steps.append(f"{velocity:02x}{accent:02x}")
                else:
                    steps.append("0000")
            lines.append(f"Steps: {' '.join(steps)}")

        return "\n".join(lines)

    def _extension_available(self) -> bool:
        repo_root = get_repo_root()
        candidates = [
            repo_root / "groovebox",
            repo_root / "extensions" / "groovebox",
        ]
        return any(path.exists() for path in candidates)
