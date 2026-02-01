"""
Multi-Track Song Renderer
=========================

Combines drums, bass, and synth tracks into complete songs.
Supports MML notation for all track types.

Part of uDOS Groovebox Extension v1.0.0.36+

Song Format:
```mml
#SONG "My Song"
#TEMPO 120
#BARS 4

#DRUMS
x-x-|x-x-|x-x-|x-x-  ; hi-hat
--o-|--o-|--o-|--o-  ; snare
o---|o---|o---|o---  ; kick

#BASS <303>
c2* c c~ e* | g g~ c3* c | c2 r e~ g* | g c2~ c2* r

#SYNTH <juno-pad>
[c4 e4 g4]1 | [c4 e4 g4]1 | [f4 a4 c5]1 | [g4 b4 d5]1
```
"""

import struct
import wave
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from enum import Enum

from core.services.logging_service import get_logger

from ..instruments.drum_808 import Drum808, DrumSound
from ..instruments.bass_303 import Bass303, Pattern303, parse_bass_mml
from ..instruments.synth_80s import Synth80s, get_preset, SynthPatch, create_juno_pad

logger = get_logger("groovebox-multitrack")


class TrackType(Enum):
    """Track types."""

    DRUMS = "drums"
    BASS = "bass"
    SYNTH = "synth"


@dataclass
class DrumTrack:
    """Drum track data."""

    pattern: List[List[bool]]  # [instrument][step] = hit?
    sounds: List[DrumSound] = field(default_factory=list)


@dataclass
class BassTrack:
    """Bass track data."""

    pattern: Pattern303
    preset: str = "acid"


@dataclass
class SynthTrack:
    """Synth track data."""

    notes: List[Tuple[int, float, float]]  # (midi_note, start_time, duration)
    patch: SynthPatch = field(default_factory=create_juno_pad)
    preset: str = "juno-pad"


@dataclass
class Song:
    """Complete multi-track song."""

    name: str = "Untitled"
    tempo: int = 120
    bars: int = 4

    drums: Optional[DrumTrack] = None
    bass: Optional[BassTrack] = None
    synth: Optional[SynthTrack] = None

    # Mixing
    drum_volume: float = 0.8
    bass_volume: float = 0.7
    synth_volume: float = 0.6


class SongParser:
    """
    Parse multi-track song format.
    """

    def __init__(self):
        self.song = Song()

    def parse(self, text: str) -> Song:
        """Parse song text into Song object."""
        self.song = Song()

        lines = text.strip().split("\n")
        current_section = None
        section_content = []
        section_preset = None

        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith(";"):
                continue

            # Metadata
            if line.startswith("#SONG"):
                match = line.split('"')
                if len(match) >= 2:
                    self.song.name = match[1]
                continue

            if line.startswith("#TEMPO"):
                parts = line.split()
                if len(parts) >= 2:
                    self.song.tempo = int(parts[1])
                continue

            if line.startswith("#BARS"):
                parts = line.split()
                if len(parts) >= 2:
                    self.song.bars = int(parts[1])
                continue

            # Section headers
            if line.startswith("#DRUMS"):
                if current_section and section_content:
                    self._process_section(
                        current_section, section_content, section_preset
                    )
                current_section = TrackType.DRUMS
                section_content = []
                section_preset = None
                continue

            if line.startswith("#BASS"):
                if current_section and section_content:
                    self._process_section(
                        current_section, section_content, section_preset
                    )
                current_section = TrackType.BASS
                section_content = []
                # Extract preset: #BASS <303> or #BASS <techno>
                if "<" in line:
                    section_preset = line.split("<")[1].split(">")[0]
                continue

            if line.startswith("#SYNTH"):
                if current_section and section_content:
                    self._process_section(
                        current_section, section_content, section_preset
                    )
                current_section = TrackType.SYNTH
                section_content = []
                if "<" in line:
                    section_preset = line.split("<")[1].split(">")[0]
                continue

            # Section content
            if current_section:
                # Remove inline comments
                if ";" in line:
                    line = line.split(";")[0].strip()
                if line:
                    section_content.append(line)

        # Process final section
        if current_section and section_content:
            self._process_section(current_section, section_content, section_preset)

        return self.song

    def _process_section(
        self, track_type: TrackType, content: List[str], preset: Optional[str]
    ):
        """Process a section into track data."""
        if track_type == TrackType.DRUMS:
            self._parse_drums(content)
        elif track_type == TrackType.BASS:
            self._parse_bass(content, preset)
        elif track_type == TrackType.SYNTH:
            self._parse_synth(content, preset)

    def _parse_drums(self, lines: List[str]):
        """Parse drum grid notation."""
        # Format: x-x-|x-x- where x=hit, -=rest, |=bar line
        patterns = []
        sounds = [DrumSound.HIHAT_CLOSED, DrumSound.SNARE, DrumSound.KICK]

        for i, line in enumerate(lines[:8]):  # Max 8 drum tracks
            steps = []
            for char in line:
                if char in "xXoO":
                    steps.append(True)
                elif char == "-":
                    steps.append(False)
                # Skip bar lines |

            # Pad to 16 steps per bar
            steps_per_bar = 16
            total_steps = self.song.bars * steps_per_bar
            while len(steps) < total_steps:
                steps.append(False)

            patterns.append(steps[:total_steps])

        self.song.drums = DrumTrack(pattern=patterns, sounds=sounds[: len(patterns)])

    def _parse_bass(self, lines: List[str], preset: Optional[str]):
        """Parse bass MML notation."""
        # Join lines and remove bar markers
        mml = " ".join(lines).replace("|", " ")

        pattern = parse_bass_mml(mml)
        pattern.tempo = self.song.tempo

        self.song.bass = BassTrack(pattern=pattern, preset=preset or "acid")

    def _parse_synth(self, lines: List[str], preset: Optional[str]):
        """Parse synth chord notation."""
        # Format: [c4 e4 g4]1 = C major chord for 1 beat
        content = " ".join(lines).replace("|", " ")

        notes = []
        time = 0.0
        beat_duration = 60.0 / self.song.tempo

        i = 0
        while i < len(content):
            if content[i] == "[":
                # Find matching ]
                end = content.find("]", i)
                if end == -1:
                    break

                chord_str = content[i + 1 : end]

                # Parse chord notes
                chord_notes = []
                for note_str in chord_str.split():
                    midi = self._parse_note_to_midi(note_str)
                    if midi >= 0:
                        chord_notes.append(midi)

                # Duration after ]
                duration_str = ""
                j = end + 1
                while j < len(content) and content[j].isdigit():
                    duration_str += content[j]
                    j += 1

                duration_beats = float(duration_str) if duration_str else 1.0
                duration = duration_beats * beat_duration

                # Add all chord notes
                for midi in chord_notes:
                    notes.append((midi, time, duration))

                time += duration
                i = j
            else:
                i += 1

        # Get patch
        patch = get_preset(preset) if preset else create_juno_pad()

        self.song.synth = SynthTrack(
            notes=notes, patch=patch, preset=preset or "juno-pad"
        )

    def _parse_note_to_midi(self, note_str: str) -> int:
        """Parse note string to MIDI number."""
        note_map = {
            "c": 0,
            "c#": 1,
            "d": 2,
            "d#": 3,
            "e": 4,
            "f": 5,
            "f#": 6,
            "g": 7,
            "g#": 8,
            "a": 9,
            "a#": 10,
            "b": 11,
        }

        note_str = note_str.lower().strip()
        if not note_str:
            return -1

        # Parse note name
        note_name = note_str[0]
        idx = 1
        if len(note_str) > 1 and note_str[1] == "#":
            note_name += "#"
            idx = 2

        if note_name not in note_map:
            return -1

        # Parse octave
        octave = 4
        if idx < len(note_str) and note_str[idx].isdigit():
            octave = int(note_str[idx])

        return 12 + octave * 12 + note_map[note_name]


class SongRenderer:
    """
    Render multi-track songs to audio.
    """

    SAMPLE_RATE = 44100

    def __init__(self):
        self.drum_engine = Drum808()
        self.bass_engine = Bass303()
        self.synth_engine = Synth80s()

    def render(self, song: Song) -> List[float]:
        """
        Render complete song to audio samples.

        Args:
            song: Song object with tracks

        Returns:
            Mixed audio samples
        """
        # Calculate total duration
        step_duration = 60.0 / song.tempo / 4  # 16th notes
        steps_per_bar = 16
        total_steps = song.bars * steps_per_bar
        total_duration = total_steps * step_duration
        total_samples = int(total_duration * self.SAMPLE_RATE)

        # Initialize mix buffer
        mix = [0.0] * total_samples

        # Render drums
        if song.drums:
            drum_samples = self._render_drums(song.drums, song.tempo, song.bars)
            self._mix_into(mix, drum_samples, song.drum_volume)
            logger.info(f"[LOCAL] Rendered drums: {len(drum_samples)} samples")

        # Render bass
        if song.bass:
            bass_samples = self._render_bass(song.bass, song.tempo)
            self._mix_into(mix, bass_samples, song.bass_volume)
            logger.info(f"[LOCAL] Rendered bass: {len(bass_samples)} samples")

        # Render synth
        if song.synth:
            synth_samples = self._render_synth(song.synth, total_duration)
            self._mix_into(mix, synth_samples, song.synth_volume)
            logger.info(f"[LOCAL] Rendered synth: {len(synth_samples)} samples")

        # Normalize to prevent clipping
        max_val = max(abs(s) for s in mix) if mix else 1.0
        if max_val > 1.0:
            mix = [s / max_val for s in mix]

        logger.info(f"[LOCAL] Song rendered: {len(mix)} samples, {total_duration:.1f}s")
        return mix

    def _render_drums(self, track: DrumTrack, tempo: int, bars: int) -> List[float]:
        """Render drum track."""
        step_duration = 60.0 / tempo / 4
        samples_per_step = int(step_duration * self.SAMPLE_RATE)
        total_steps = bars * 16

        output = [0.0] * (total_steps * samples_per_step)

        for inst_idx, (pattern, sound) in enumerate(zip(track.pattern, track.sounds)):
            for step_idx, hit in enumerate(pattern[:total_steps]):
                if hit:
                    # Generate drum sound
                    drum_samples = self.drum_engine.generate_sound(sound)

                    # Mix at step position
                    start = step_idx * samples_per_step
                    for i, s in enumerate(drum_samples):
                        if start + i < len(output):
                            output[start + i] += s

        return output

    def _render_bass(self, track: BassTrack, tempo: int) -> List[float]:
        """Render bass track."""
        track.pattern.tempo = tempo
        return self.bass_engine.render_pattern(track.pattern)

    def _render_synth(self, track: SynthTrack, duration: float) -> List[float]:
        """Render synth track."""
        total_samples = int(duration * self.SAMPLE_RATE)
        output = [0.0] * total_samples

        for midi_note, start_time, note_duration in track.notes:
            # Render note
            note_samples = self.synth_engine.render_note(
                track.patch, midi_note, note_duration
            )

            # Mix at position
            start_sample = int(start_time * self.SAMPLE_RATE)
            for i, s in enumerate(note_samples):
                if start_sample + i < len(output):
                    output[start_sample + i] += s

        return output

    def _mix_into(self, target: List[float], source: List[float], volume: float):
        """Mix source into target buffer."""
        for i, s in enumerate(source):
            if i < len(target):
                target[i] += s * volume

    def to_wav(self, samples: List[float], output_path: Path) -> Path:
        """Export to WAV file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(output_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.SAMPLE_RATE)

            for sample in samples:
                clamped = max(-1.0, min(1.0, sample))
                pcm = int(clamped * 32767)
                wav.writeframes(struct.pack("<h", pcm))

        logger.info(f"[LOCAL] Exported song to {output_path}")
        return output_path


def parse_song(text: str) -> Song:
    """Parse song text into Song object."""
    parser = SongParser()
    return parser.parse(text)


def render_song(song: Song) -> List[float]:
    """Render song to audio samples."""
    renderer = SongRenderer()
    return renderer.render(song)


def render_song_to_wav(text: str, output_path: Path) -> Path:
    """
    Parse and render song text to WAV file.

    Args:
        text: Song text in multi-track format
        output_path: Output WAV path

    Returns:
        Path to created file
    """
    song = parse_song(text)
    renderer = SongRenderer()
    samples = renderer.render(song)
    return renderer.to_wav(samples, output_path)


# === Example Songs ===

DEMO_SONG = """
#SONG "Acid Demo"
#TEMPO 128
#BARS 4

#DRUMS
x-x-x-x-|x-x-x-x-|x-x-x-x-|x-x-x-x-
----o---|----o---|----o---|----o---
o-------|o--o----|o-------|o--o----

#BASS <303>
c2* c c~ e* g g~ c3* c c2 r e~ g* g c2~ c2* r

#SYNTH <juno-pad>
[c4 e4 g4]2 [c4 e4 g4]2 [f4 a4 c5]2 [g4 b4 d5]2
"""


if __name__ == "__main__":
    # Demo
    song = parse_song(DEMO_SONG)
    print(f"Song: {song.name}")
    print(f"Tempo: {song.tempo} BPM")
    print(f"Bars: {song.bars}")
    print(f"Has drums: {song.drums is not None}")
    print(f"Has bass: {song.bass is not None}")
    print(f"Has synth: {song.synth is not None}")

    # Render
    output = Path("/tmp/demo_song.wav")
    render_song_to_wav(DEMO_SONG, output)
    print(f"Created: {output}")
