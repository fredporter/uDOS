"""
TB-303 Bass Synthesizer Engine
==============================

Pure Python implementation of a TB-303-style acid bass synthesizer.
Generates characteristic acid basslines with:
- Sawtooth/square oscillator
- 24dB/oct resonant low-pass filter
- Accent (volume + filter boost)
- Slide/portamento between notes
- Envelope modulation

Part of uDOS Groovebox Extension v1.0.0.35+

Audio: 16-bit PCM, 44100 Hz mono
"""

import math
import struct
import wave
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from pathlib import Path
from enum import Enum

from core.services.logging_service import get_logger

logger = get_logger("groovebox-303")


class Waveform(Enum):
    """303 oscillator waveforms."""

    SAWTOOTH = "saw"
    SQUARE = "square"


@dataclass
class Note303:
    """A single 303 note/step."""

    pitch: int = 36  # MIDI note (36 = C2)
    gate: bool = True  # Note on/off
    accent: bool = False  # Accent flag
    slide: bool = False  # Slide to next note
    octave_up: bool = False  # Octave transpose
    octave_down: bool = False


@dataclass
class Pattern303:
    """A 303 pattern (16 steps)."""

    steps: List[Note303] = field(default_factory=lambda: [Note303() for _ in range(16)])
    tempo: int = 120
    waveform: Waveform = Waveform.SAWTOOTH
    cutoff: float = 0.5  # Filter cutoff (0-1)
    resonance: float = 0.7  # Filter resonance (0-1)
    env_mod: float = 0.6  # Envelope modulation depth
    decay: float = 0.3  # Envelope decay (0-1)
    accent_level: float = 0.8  # Accent intensity


class Filter303:
    """
    24dB/oct resonant low-pass filter (4-pole ladder).

    Simplified digital model of the 303's distinctive filter.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.cutoff = 1000.0  # Hz
        self.resonance = 0.0  # 0-1 (0.97 = self-oscillation)

        # Filter state (4 poles)
        self.s = [0.0, 0.0, 0.0, 0.0]

    def set_cutoff(self, freq: float):
        """Set cutoff frequency in Hz."""
        # Clamp to valid range
        self.cutoff = max(20.0, min(freq, self.sample_rate * 0.45))

    def set_resonance(self, res: float):
        """Set resonance (0-1)."""
        self.resonance = max(0.0, min(res, 0.97))

    def process(self, sample: float) -> float:
        """Process a single sample through the filter."""
        # Calculate filter coefficient
        f = 2.0 * math.sin(math.pi * self.cutoff / self.sample_rate)

        # Feedback amount from resonance
        fb = self.resonance + self.resonance / (1.0 - f + 0.001)

        # 4-pole cascade
        inp = sample - fb * self.s[3]

        self.s[0] += f * (inp - self.s[0])
        self.s[1] += f * (self.s[0] - self.s[1])
        self.s[2] += f * (self.s[1] - self.s[2])
        self.s[3] += f * (self.s[2] - self.s[3])

        return self.s[3]

    def reset(self):
        """Reset filter state."""
        self.s = [0.0, 0.0, 0.0, 0.0]


class Envelope303:
    """
    303-style decay envelope.

    Controls both VCA (volume) and VCF (filter cutoff).
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.decay_time = 0.3  # seconds
        self.accent_decay = 0.1  # shorter for accented notes

        # State
        self.level = 0.0
        self.gate = False
        self.accent = False
        self.decay_rate = 0.0

    def set_decay(self, decay: float):
        """Set decay time (0-1 maps to 0.05-1.0 seconds)."""
        self.decay_time = 0.05 + decay * 0.95

    def trigger(self, accent: bool = False):
        """Trigger envelope."""
        self.level = 1.0
        self.accent = accent

        # Accent has faster decay
        decay = self.accent_decay if accent else self.decay_time
        # Calculate exponential decay rate
        self.decay_rate = 1.0 / (decay * self.sample_rate)

    def process(self) -> float:
        """Get next envelope value."""
        if self.level > 0.001:
            self.level *= 1.0 - self.decay_rate
        else:
            self.level = 0.0

        return self.level


class Bass303:
    """
    TB-303 Bass Synthesizer.

    Generates acid basslines with characteristic filter sweeps.

    Usage:
        bass = Bass303()
        pattern = Pattern303()
        pattern.steps[0] = Note303(pitch=36, accent=True)
        pattern.steps[4] = Note303(pitch=38, slide=True)

        samples = bass.render_pattern(pattern)
    """

    SAMPLE_RATE = 44100

    def __init__(self):
        self.filter = Filter303(self.SAMPLE_RATE)
        self.envelope = Envelope303(self.SAMPLE_RATE)

        # Oscillator state
        self.phase = 0.0
        self.frequency = 110.0  # A2
        self.target_frequency = 110.0
        self.slide_rate = 0.0

        # Current settings
        self.waveform = Waveform.SAWTOOTH
        self.base_cutoff = 500.0
        self.env_mod = 3000.0  # Hz range for envelope
        self.accent_boost = 2000.0  # Extra cutoff for accent

        logger.info("[LOCAL] Bass303 synthesizer initialized")

    def midi_to_freq(self, midi_note: int) -> float:
        """Convert MIDI note to frequency."""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    def set_note(self, midi_note: int, slide: bool = False):
        """Set oscillator frequency from MIDI note."""
        self.target_frequency = self.midi_to_freq(midi_note)

        if slide:
            # Calculate slide rate (portamento over ~50ms)
            slide_samples = int(0.05 * self.SAMPLE_RATE)
            self.slide_rate = (self.target_frequency - self.frequency) / slide_samples
        else:
            self.frequency = self.target_frequency
            self.slide_rate = 0.0

    def oscillator(self) -> float:
        """Generate oscillator sample."""
        # Update frequency (slide)
        if self.slide_rate != 0.0:
            self.frequency += self.slide_rate
            if (self.slide_rate > 0 and self.frequency >= self.target_frequency) or (
                self.slide_rate < 0 and self.frequency <= self.target_frequency
            ):
                self.frequency = self.target_frequency
                self.slide_rate = 0.0

        # Advance phase
        self.phase += self.frequency / self.SAMPLE_RATE
        if self.phase >= 1.0:
            self.phase -= 1.0

        # Generate waveform
        if self.waveform == Waveform.SAWTOOTH:
            return 2.0 * self.phase - 1.0
        else:  # SQUARE
            return 1.0 if self.phase < 0.5 else -1.0

    def render_step(
        self, note: Note303, samples_per_step: int, accent_level: float = 0.8
    ) -> List[float]:
        """Render a single step."""
        output = []

        if note.gate:
            # Calculate pitch with octave shifts
            pitch = note.pitch
            if note.octave_up:
                pitch += 12
            if note.octave_down:
                pitch -= 12

            # Set note (with slide if flagged)
            self.set_note(pitch, note.slide)

            # Trigger envelope
            self.envelope.trigger(note.accent)

        for i in range(samples_per_step):
            # Get oscillator
            osc = self.oscillator()

            # Get envelope
            env = self.envelope.process()

            # Calculate filter cutoff
            cutoff = self.base_cutoff + env * self.env_mod
            if note.accent:
                cutoff += self.accent_boost * env

            self.filter.set_cutoff(cutoff)

            # Filter the oscillator
            filtered = self.filter.process(osc)

            # Apply VCA envelope
            volume = 0.3 + env * 0.7  # Don't fully close VCA
            if note.accent:
                volume *= 1.0 + accent_level * 0.5

            sample = filtered * volume * 0.7  # Master volume

            output.append(sample)

        return output

    def render_pattern(self, pattern: Pattern303) -> List[float]:
        """
        Render a complete 303 pattern.

        Args:
            pattern: Pattern303 with 16 steps

        Returns:
            List of audio samples (float, -1 to 1)
        """
        # Apply pattern settings
        self.waveform = pattern.waveform
        self.base_cutoff = 200.0 + pattern.cutoff * 2000.0
        self.env_mod = pattern.env_mod * 5000.0
        self.envelope.set_decay(pattern.decay)
        self.filter.set_resonance(pattern.resonance)

        # Calculate samples per step
        step_duration = 60.0 / pattern.tempo / 4  # 16th notes
        samples_per_step = int(step_duration * self.SAMPLE_RATE)

        output = []

        for i, step in enumerate(pattern.steps):
            # Check if next step has slide
            next_idx = (i + 1) % len(pattern.steps)
            step_with_slide = Note303(
                pitch=step.pitch,
                gate=step.gate,
                accent=step.accent,
                slide=pattern.steps[next_idx].slide if next_idx != 0 else False,
                octave_up=step.octave_up,
                octave_down=step.octave_down,
            )

            step_samples = self.render_step(
                step_with_slide, samples_per_step, pattern.accent_level
            )
            output.extend(step_samples)

        logger.info(f"[LOCAL] Rendered 303 pattern: {len(output)} samples")
        return output

    def to_wav(self, samples: List[float], output_path: Path) -> Path:
        """
        Export samples to WAV file.

        Args:
            samples: Audio samples (-1 to 1)
            output_path: Output file path

        Returns:
            Path to created file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(output_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(self.SAMPLE_RATE)

            # Convert to 16-bit PCM
            for sample in samples:
                clamped = max(-1.0, min(1.0, sample))
                pcm = int(clamped * 32767)
                wav.writeframes(struct.pack("<h", pcm))

        logger.info(f"[LOCAL] Exported 303 to {output_path}")
        return output_path


# === Preset Patterns ===


def create_acid_pattern() -> Pattern303:
    """Classic acid house pattern."""
    pattern = Pattern303(
        tempo=130,
        waveform=Waveform.SAWTOOTH,
        cutoff=0.3,
        resonance=0.85,
        env_mod=0.8,
        decay=0.2,
        accent_level=0.9,
    )

    # Classic acid pattern: C-C-C-E-G-G-C-C (with accents and slides)
    notes = [
        Note303(pitch=36, gate=True, accent=True),  # 1 - C2 accent
        Note303(pitch=36, gate=True),  # 2 - C2
        Note303(pitch=36, gate=True, slide=True),  # 3 - C2 slide
        Note303(pitch=40, gate=True, accent=True),  # 4 - E2 accent
        Note303(pitch=43, gate=True),  # 5 - G2
        Note303(pitch=43, gate=True, slide=True),  # 6 - G2 slide
        Note303(pitch=48, gate=True, accent=True),  # 7 - C3 accent
        Note303(pitch=48, gate=True),  # 8 - C3
        Note303(pitch=36, gate=True),  # 9 - C2
        Note303(pitch=36, gate=False),  # 10 - rest
        Note303(pitch=40, gate=True, slide=True),  # 11 - E2 slide
        Note303(pitch=43, gate=True, accent=True),  # 12 - G2 accent
        Note303(pitch=43, gate=True),  # 13 - G2
        Note303(pitch=36, gate=True, slide=True),  # 14 - C2 slide
        Note303(pitch=36, gate=True, accent=True),  # 15 - C2 accent
        Note303(pitch=36, gate=False),  # 16 - rest
    ]
    pattern.steps = notes

    return pattern


def create_techno_pattern() -> Pattern303:
    """Dark techno bassline."""
    pattern = Pattern303(
        tempo=138,
        waveform=Waveform.SQUARE,
        cutoff=0.2,
        resonance=0.75,
        env_mod=0.6,
        decay=0.15,
        accent_level=0.7,
    )

    # Minimal techno: mostly root with occasional jumps
    notes = [
        Note303(pitch=33, gate=True, accent=True),  # 1 - A1 accent
        Note303(pitch=33, gate=False),  # 2 - rest
        Note303(pitch=33, gate=True),  # 3 - A1
        Note303(pitch=33, gate=False),  # 4 - rest
        Note303(pitch=33, gate=True, accent=True),  # 5 - A1 accent
        Note303(pitch=33, gate=True, slide=True),  # 6 - A1 slide
        Note303(pitch=45, gate=True),  # 7 - A2
        Note303(pitch=33, gate=False),  # 8 - rest
        Note303(pitch=33, gate=True),  # 9 - A1
        Note303(pitch=33, gate=True, accent=True),  # 10 - A1 accent
        Note303(pitch=33, gate=False),  # 11 - rest
        Note303(pitch=33, gate=True),  # 12 - A1
        Note303(pitch=33, gate=True, slide=True),  # 13 - A1 slide
        Note303(pitch=40, gate=True, accent=True),  # 14 - E2 accent
        Note303(pitch=33, gate=True),  # 15 - A1
        Note303(pitch=33, gate=False),  # 16 - rest
    ]
    pattern.steps = notes

    return pattern


# === MML Integration ===


def parse_bass_mml(mml: str) -> Pattern303:
    """
    Parse MML notation for 303 bass.

    Format: NOTE[OCTAVE][+/-][*][~]
    - NOTE: c, c#, d, d#, e, f, f#, g, g#, a, a#, b, r (rest)
    - OCTAVE: 1-5 (default 2)
    - +: octave up
    - -: octave down
    - *: accent
    - ~: slide to next

    Example: "c2* c c~ e* g g~ c3* c"
    """
    pattern = Pattern303()

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
        "r": -1,
    }

    tokens = mml.lower().split()
    steps = []

    for token in tokens[:16]:  # Max 16 steps
        note = Note303()

        # Parse note name
        if token.startswith("r"):
            note.gate = False
            steps.append(note)
            continue

        # Find note
        note_name = token[0]
        idx = 1
        if len(token) > 1 and token[1] == "#":
            note_name += "#"
            idx = 2

        if note_name not in note_map:
            continue

        base_pitch = note_map[note_name]

        # Parse octave
        octave = 2
        if idx < len(token) and token[idx].isdigit():
            octave = int(token[idx])
            idx += 1

        note.pitch = 12 + octave * 12 + base_pitch  # MIDI note

        # Parse modifiers
        while idx < len(token):
            if token[idx] == "*":
                note.accent = True
            elif token[idx] == "~":
                note.slide = True
            elif token[idx] == "+":
                note.octave_up = True
            elif token[idx] == "-":
                note.octave_down = True
            idx += 1

        steps.append(note)

    # Pad to 16 steps
    while len(steps) < 16:
        steps.append(Note303(gate=False))

    pattern.steps = steps[:16]
    return pattern


if __name__ == "__main__":
    # Demo
    bass = Bass303()

    # Render acid pattern
    pattern = create_acid_pattern()
    samples = bass.render_pattern(pattern)

    # Export
    output = Path("/tmp/303_acid.wav")
    bass.to_wav(samples, output)
    print(f"Created: {output} ({len(samples)} samples)")

    # MML test
    mml_pattern = parse_bass_mml("c2* c c~ e* g g~ c3* c c2 r e~ g* g c2~ c2* r")
    samples2 = bass.render_pattern(mml_pattern)
    output2 = Path("/tmp/303_mml.wav")
    bass.to_wav(samples2, output2)
    print(f"Created: {output2}")
