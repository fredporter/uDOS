"""
MIDI Exporter - Export Patterns to MIDI Files
=============================================

Exports MML patterns to standard MIDI files for use
in external DAWs and hardware.

Version: v1.0.0.0
"""

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, BinaryIO

from .mml_parser import MMLPattern, MMLNote


@dataclass
class MidiEvent:
    """Single MIDI event."""

    tick: int  # Absolute tick position
    type: str  # 'note_on', 'note_off', 'tempo', 'end'
    channel: int = 0  # MIDI channel (0-15)
    note: int = 60  # MIDI note number
    velocity: int = 100  # Note velocity
    tempo: int = 500000  # Tempo in microseconds per beat (for tempo events)


class MidiExporter:
    """
    Export MML patterns to Standard MIDI Files (SMF).

    Supports:
    - Type 0 (single track) and Type 1 (multi-track) MIDI
    - Variable tempo
    - Multiple channels for drum mapping
    - GM-compatible drum channel (10)

    Example:
        exporter = MidiExporter()
        exporter.add_pattern(drum_pattern, channel=9)  # Drums on channel 10
        exporter.add_pattern(bass_pattern, channel=0)
        exporter.export("output.mid")
    """

    # MIDI timing
    TICKS_PER_BEAT = 480

    # GM Drum channel (channel 10 = index 9)
    DRUM_CHANNEL = 9

    def __init__(self):
        self.patterns: List[tuple] = []  # (pattern, channel, name)
        self.tempo = 120  # Default BPM

    def add_pattern(self, pattern: MMLPattern, channel: int = 0, name: str = ""):
        """
        Add pattern to export.

        Args:
            pattern: MMLPattern to add
            channel: MIDI channel (0-15, use 9 for drums)
            name: Track name
        """
        self.patterns.append((pattern, channel, name or pattern.name))
        # Use pattern tempo if set
        if pattern.tempo:
            self.tempo = pattern.tempo

    def clear(self):
        """Clear all patterns."""
        self.patterns = []

    def export(self, filepath: str) -> bool:
        """
        Export patterns to MIDI file.

        Args:
            filepath: Output file path (.mid)

        Returns:
            True if successful
        """
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "wb") as f:
                self._write_midi_file(f)

            return True
        except Exception as e:
            print(f"MIDI export error: {e}")
            return False

    def export_bytes(self) -> bytes:
        """
        Export patterns to MIDI bytes.

        Returns:
            MIDI file as bytes
        """
        import io

        buffer = io.BytesIO()
        self._write_midi_file(buffer)
        return buffer.getvalue()

    def _write_midi_file(self, f: BinaryIO):
        """Write complete MIDI file."""
        # Build tracks
        tracks = self._build_tracks()

        # Write header
        self._write_header(f, len(tracks))

        # Write tracks
        for track_data in tracks:
            self._write_track(f, track_data)

    def _write_header(self, f: BinaryIO, num_tracks: int):
        """Write MIDI file header."""
        # MThd chunk
        f.write(b"MThd")
        f.write(struct.pack(">I", 6))  # Chunk length = 6

        # Format type (0 = single track, 1 = multi-track)
        format_type = 0 if num_tracks == 1 else 1
        f.write(struct.pack(">H", format_type))

        # Number of tracks
        f.write(struct.pack(">H", num_tracks))

        # Ticks per beat (PPQ)
        f.write(struct.pack(">H", self.TICKS_PER_BEAT))

    def _write_track(self, f: BinaryIO, events: List[MidiEvent]):
        """Write single MIDI track."""
        # Build track data
        track_data = bytearray()

        last_tick = 0
        for event in events:
            # Delta time (variable length)
            delta = event.tick - last_tick
            track_data.extend(self._encode_variable_length(delta))
            last_tick = event.tick

            # Event data
            if event.type == "note_on":
                track_data.append(0x90 | event.channel)  # Note on
                track_data.append(event.note)
                track_data.append(event.velocity)

            elif event.type == "note_off":
                track_data.append(0x80 | event.channel)  # Note off
                track_data.append(event.note)
                track_data.append(0)  # Release velocity

            elif event.type == "tempo":
                # Meta event: tempo
                track_data.append(0xFF)
                track_data.append(0x51)  # Tempo
                track_data.append(0x03)  # Length = 3
                # Microseconds per beat (3 bytes, big endian)
                track_data.append((event.tempo >> 16) & 0xFF)
                track_data.append((event.tempo >> 8) & 0xFF)
                track_data.append(event.tempo & 0xFF)

            elif event.type == "track_name":
                # Meta event: track name
                name_bytes = event.note if isinstance(event.note, bytes) else b""
                track_data.append(0xFF)
                track_data.append(0x03)  # Track name
                track_data.extend(self._encode_variable_length(len(name_bytes)))
                track_data.extend(name_bytes)

            elif event.type == "end":
                # Meta event: end of track
                track_data.append(0xFF)
                track_data.append(0x2F)
                track_data.append(0x00)

        # MTrk chunk
        f.write(b"MTrk")
        f.write(struct.pack(">I", len(track_data)))
        f.write(track_data)

    def _build_tracks(self) -> List[List[MidiEvent]]:
        """Build MIDI events for all tracks."""
        if not self.patterns:
            # Return empty track with just end marker
            return [[MidiEvent(tick=0, type="end")]]

        all_tracks = []

        for pattern, channel, name in self.patterns:
            events = []

            # Track name
            if name:
                events.append(
                    MidiEvent(
                        tick=0,
                        type="track_name",
                        note=name.encode("utf-8")[:127],  # Truncate to 127 bytes
                    )
                )

            # Tempo event (only on first track)
            if not all_tracks:
                # Convert BPM to microseconds per beat
                tempo_us = int(60_000_000 / self.tempo)
                events.append(MidiEvent(tick=0, type="tempo", tempo=tempo_us))

            # Convert notes to MIDI events
            tick = 0
            for note in pattern.notes:
                if note.pitch != "r":  # Not a rest
                    midi_note = note.midi_note

                    # Note on
                    events.append(
                        MidiEvent(
                            tick=tick,
                            type="note_on",
                            channel=channel,
                            note=midi_note,
                            velocity=note.velocity,
                        )
                    )

                    # Note off (at end of note duration)
                    note_end = (
                        tick + note.duration_ticks - 1
                    )  # Slightly before next note
                    events.append(
                        MidiEvent(
                            tick=note_end,
                            type="note_off",
                            channel=channel,
                            note=midi_note,
                        )
                    )

                tick += note.duration_ticks

            # Sort events by tick
            events.sort(key=lambda e: (e.tick, 0 if e.type == "note_on" else 1))

            # End of track
            end_tick = tick if tick > 0 else 0
            events.append(MidiEvent(tick=end_tick, type="end"))

            all_tracks.append(events)

        return all_tracks

    def _encode_variable_length(self, value: int) -> bytes:
        """Encode integer as MIDI variable-length quantity."""
        if value < 0:
            value = 0

        result = []
        result.append(value & 0x7F)
        value >>= 7

        while value:
            result.append((value & 0x7F) | 0x80)
            value >>= 7

        return bytes(reversed(result))


def export_pattern_to_midi(
    pattern: MMLPattern, filepath: str, channel: int = 0
) -> bool:
    """
    Convenience function to export a single pattern to MIDI.

    Args:
        pattern: MMLPattern to export
        filepath: Output file path
        channel: MIDI channel (0-15)

    Returns:
        True if successful
    """
    exporter = MidiExporter()
    exporter.add_pattern(pattern, channel)
    return exporter.export(filepath)


def export_drum_pattern(pattern: MMLPattern, filepath: str) -> bool:
    """
    Export drum pattern to MIDI using GM drum channel.

    Args:
        pattern: Drum pattern (notes mapped to GM drums)
        filepath: Output file path

    Returns:
        True if successful
    """
    exporter = MidiExporter()
    exporter.add_pattern(pattern, channel=MidiExporter.DRUM_CHANNEL, name="Drums")
    return exporter.export(filepath)
