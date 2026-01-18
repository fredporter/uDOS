"""
Imperial Groovebox - MML-Style Pattern Engine
Alpha v1.1.0.2+

Text-based music pattern generator for Imperial Data Transport sounds.
Combines TR-808 style drums with dark synth aesthetic for data transfer cues.

Pattern Language (simplified MML):
    Notes:     C D E F G A B (with # for sharp, - for flat)
    Octaves:   o0-o8 (o4 is middle)
    Length:    l1 l2 l4 l8 l16 l32 (whole, half, quarter, 8th, 16th, 32nd)
    Rest:      r
    Volume:    v0-v15
    Tempo:     t60-t240
    Loop:      [pattern]N (repeat N times)

Imperial Sound Mapping:
    Drums (o2):  C=kick, D=snare, E=low_tom, F=mid_tom, G=hi_tom, A=hat_c, B=hat_o
    Bass (o2-3): Resonant saw/square, 303-style
    Lead (o4-5): FM/analog synth, dark minor melodies
    FX (o6+):    Data bleeps, status tones, error sounds
"""

import math
import struct
import re
from typing import List, Dict, Optional, Tuple, Generator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SoundBank(Enum):
    """Available sound banks for groovebox"""

    IMPERIAL_808 = "imperial_808"  # Dark 808 drums
    SYNTH_BASS = "synth_bass"  # 303-style acid bass
    FM_LEAD = "fm_lead"  # DX7-style leads
    ANALOG_PAD = "analog_pad"  # Juno-style pads
    DATA_FX = "data_fx"  # Data transfer bleeps
    GAME_SFX = "game_sfx"  # Retro game sounds


@dataclass
class GrooveConfig:
    """Groovebox configuration"""

    sample_rate: int = 44100
    tempo: int = 125  # BPM (Imperial default)
    default_length: int = 8  # 8th notes
    default_octave: int = 4
    default_volume: float = 0.7
    swing: float = 0.0  # 0.0 = straight, 0.5 = heavy swing


@dataclass
class Note:
    """Single note in a pattern"""

    pitch: int  # MIDI note number (0-127)
    length: float  # Duration in beats
    velocity: float  # 0.0-1.0
    is_rest: bool = False

    def duration_samples(self, sample_rate: int, tempo: int) -> int:
        """Calculate sample duration"""
        beat_duration = 60.0 / tempo
        return int(self.length * beat_duration * sample_rate)


@dataclass
class Pattern:
    """A sequence of notes forming a musical pattern"""

    name: str
    notes: List[Note] = field(default_factory=list)
    bank: SoundBank = SoundBank.IMPERIAL_808
    loop_count: int = 1

    def total_beats(self) -> float:
        """Total pattern length in beats"""
        return sum(n.length for n in self.notes)


class MMLParser:
    """
    Parses simplified MML (Music Macro Language) into patterns.

    Syntax:
        t125          - Set tempo to 125 BPM
        l8            - Set default length to 8th notes
        o4            - Set octave to 4
        v12           - Set volume to 12 (0-15)
        c d e f g a b - Notes (lowercase)
        c# d- e#      - Sharps and flats
        r             - Rest
        c4            - Quarter note C
        c8.           - Dotted 8th note
        [cdefg]4      - Loop pattern 4 times
        ;             - Comment to end of line
    """

    # Note name to semitone offset from C
    NOTE_MAP = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}

    def __init__(self, config: Optional[GrooveConfig] = None):
        self.config = config or GrooveConfig()
        self.reset()

    def reset(self):
        """Reset parser state"""
        self.tempo = self.config.tempo
        self.octave = self.config.default_octave
        self.length = self.config.default_length
        self.volume = self.config.default_volume

    def parse(
        self, mml: str, name: str = "pattern", bank: SoundBank = SoundBank.IMPERIAL_808
    ) -> Pattern:
        """Parse MML string into a Pattern"""
        self.reset()
        notes = []

        # Remove comments
        mml = re.sub(r";.*$", "", mml, flags=re.MULTILINE)
        mml = mml.lower().replace("\n", " ").replace("\r", "")

        i = 0
        while i < len(mml):
            char = mml[i]

            # Skip whitespace
            if char in " \t":
                i += 1
                continue

            # Tempo
            if char == "t":
                num, i = self._read_number(mml, i + 1)
                if num:
                    self.tempo = max(30, min(300, num))
                continue

            # Octave
            if char == "o":
                num, i = self._read_number(mml, i + 1)
                if num is not None:
                    self.octave = max(0, min(8, num))
                continue

            # Length
            if char == "l":
                num, i = self._read_number(mml, i + 1)
                if num:
                    self.length = num
                continue

            # Volume
            if char == "v":
                num, i = self._read_number(mml, i + 1)
                if num is not None:
                    self.volume = max(0, min(15, num)) / 15.0
                continue

            # Rest
            if char == "r":
                note_len, i = self._read_note_length(mml, i + 1)
                notes.append(
                    Note(
                        pitch=0,
                        length=4.0 / note_len,  # Convert to beats
                        velocity=0,
                        is_rest=True,
                    )
                )
                continue

            # Notes
            if char in self.NOTE_MAP:
                pitch = self.NOTE_MAP[char]
                i += 1

                # Check for sharp/flat
                if i < len(mml):
                    if mml[i] == "#" or mml[i] == "+":
                        pitch += 1
                        i += 1
                    elif mml[i] == "-":
                        pitch -= 1
                        i += 1

                # Calculate MIDI note
                midi_note = (self.octave + 1) * 12 + pitch

                # Get note length
                note_len, i = self._read_note_length(mml, i)

                notes.append(
                    Note(pitch=midi_note, length=4.0 / note_len, velocity=self.volume)
                )
                continue

            # Loop brackets
            if char == "[":
                # Find matching ]
                depth = 1
                start = i + 1
                i += 1
                while i < len(mml) and depth > 0:
                    if mml[i] == "[":
                        depth += 1
                    elif mml[i] == "]":
                        depth -= 1
                    i += 1

                # Get loop count
                loop_count, i = self._read_number(mml, i)
                if not loop_count:
                    loop_count = 2

                # Parse inner pattern and repeat
                inner_mml = mml[start : i - 1 - (1 if loop_count else 0)]
                inner_pattern = self.parse(inner_mml, f"{name}_inner", bank)
                for _ in range(loop_count):
                    notes.extend(inner_pattern.notes)
                continue

            # Skip unknown characters
            i += 1

        return Pattern(name=name, notes=notes, bank=bank)

    def _read_number(self, mml: str, pos: int) -> Tuple[Optional[int], int]:
        """Read a number from MML string"""
        start = pos
        while pos < len(mml) and mml[pos].isdigit():
            pos += 1
        if pos > start:
            return int(mml[start:pos]), pos
        return None, pos

    def _read_note_length(self, mml: str, pos: int) -> Tuple[int, int]:
        """Read note length (with optional dot)"""
        num, pos = self._read_number(mml, pos)
        length = num if num else self.length

        # Check for dot (1.5x length)
        if pos < len(mml) and mml[pos] == ".":
            length = int(length * 2 / 3)  # Dotted = 1.5x
            pos += 1

        return length, pos


class ImperialGroovebox:
    """
    Groovebox engine for Imperial Data Transport sounds.

    Generates musical patterns for:
    - Boot sequence (dark synth arpeggio)
    - Connection (Vader breathing rhythm)
    - Handshake (Imperial theme call/response)
    - Data transfer (arpeggiated stream)
    - Success/Error (fanfares)
    """

    # A minor scale frequencies (dark, ominous)
    SCALE_A_MINOR = {
        "A2": 110.00,
        "B2": 123.47,
        "C3": 130.81,
        "D3": 146.83,
        "E3": 164.81,
        "F3": 174.61,
        "G3": 196.00,
        "A3": 220.00,
        "B3": 246.94,
        "C4": 261.63,
        "D4": 293.66,
        "E4": 329.63,
        "F4": 349.23,
        "G4": 392.00,
        "A4": 440.00,
        "C5": 523.25,
        "E5": 659.26,
        "A5": 880.00,
    }

    # Drum kit mapping (TR-808 style)
    DRUM_KIT = {
        "kick": 55.0,  # Deep 808 kick
        "snare": 200.0,  # Snappy snare
        "hat_c": 8000.0,  # Closed hat
        "hat_o": 6000.0,  # Open hat
        "clap": 1500.0,  # Handclap
        "tom_l": 80.0,  # Low tom
        "tom_m": 120.0,  # Mid tom
        "tom_h": 180.0,  # High tom
        "rim": 800.0,  # Rimshot
        "cowbell": 560.0,  # Cowbell
    }

    def __init__(self, config: Optional[GrooveConfig] = None):
        self.config = config or GrooveConfig()
        self.parser = MMLParser(self.config)

    def _generate_samples(self, duration: float) -> List[float]:
        """Create empty sample buffer"""
        return [0.0] * int(self.config.sample_rate * duration)

    def _sine(self, freq: float, t: float) -> float:
        """Pure sine wave"""
        return math.sin(2 * math.pi * freq * t)

    def _saw(self, freq: float, t: float) -> float:
        """Sawtooth wave"""
        period = 1.0 / freq if freq > 0 else 1.0
        phase = (t % period) / period
        return 2.0 * phase - 1.0

    def _square(self, freq: float, t: float, duty: float = 0.5) -> float:
        """Square wave with duty cycle"""
        period = 1.0 / freq if freq > 0 else 1.0
        phase = (t % period) / period
        return 1.0 if phase < duty else -1.0

    def _envelope_adsr(
        self,
        samples: List[float],
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.7,
        release: float = 0.2,
    ) -> List[float]:
        """Apply ADSR envelope"""
        n = len(samples)
        sr = self.config.sample_rate

        a_samples = int(attack * sr)
        d_samples = int(decay * sr)
        r_samples = int(release * sr)
        s_samples = max(0, n - a_samples - d_samples - r_samples)

        output = []
        for i, s in enumerate(samples):
            if i < a_samples:
                env = i / a_samples if a_samples > 0 else 1.0
            elif i < a_samples + d_samples:
                progress = (i - a_samples) / d_samples if d_samples > 0 else 0
                env = 1.0 - progress * (1.0 - sustain)
            elif i < a_samples + d_samples + s_samples:
                env = sustain
            else:
                progress = (
                    (i - a_samples - d_samples - s_samples) / r_samples
                    if r_samples > 0
                    else 1
                )
                env = sustain * (1.0 - progress)
            output.append(s * max(0, env))

        return output

    def _render_note(self, note: Note, bank: SoundBank) -> List[float]:
        """Render a single note to samples"""
        if note.is_rest:
            return [0.0] * note.duration_samples(
                self.config.sample_rate, self.config.tempo
            )

        duration = note.duration_samples(self.config.sample_rate, self.config.tempo)
        freq = 440.0 * (2 ** ((note.pitch - 69) / 12.0))  # MIDI to freq
        samples = []

        sr = self.config.sample_rate

        for i in range(duration):
            t = i / sr

            if bank == SoundBank.IMPERIAL_808:
                # 808-style drums - use note pitch to select drum sound
                drum_idx = note.pitch % 12
                if drum_idx == 0:  # C = kick
                    # Pitch-decaying sine for punchy kick
                    kick_freq = 55 * (1 + 2 * math.exp(-t * 30))
                    sample = self._sine(kick_freq, t) * math.exp(-t * 8)
                elif drum_idx == 2:  # D = snare
                    sample = (
                        self._sine(200, t) * 0.5
                        + (hash(str(i)) % 1000 / 1000 - 0.5) * 0.5
                    ) * math.exp(-t * 15)
                elif drum_idx == 4:  # E = low tom
                    sample = self._sine(80, t) * math.exp(-t * 10)
                elif drum_idx == 5:  # F = mid tom
                    sample = self._sine(120, t) * math.exp(-t * 10)
                elif drum_idx == 7:  # G = hi tom
                    sample = self._sine(180, t) * math.exp(-t * 10)
                elif drum_idx == 9:  # A = closed hat
                    sample = (hash(str(i)) % 1000 / 1000 - 0.5) * math.exp(-t * 40)
                elif drum_idx == 11:  # B = open hat
                    sample = (hash(str(i)) % 1000 / 1000 - 0.5) * math.exp(-t * 10)
                else:
                    sample = self._sine(freq, t) * math.exp(-t * 10)

            elif bank == SoundBank.SYNTH_BASS:
                # 303-style acid bass
                sample = self._saw(freq, t) * 0.6 + self._square(freq, t, 0.3) * 0.4

            elif bank == SoundBank.FM_LEAD:
                # FM synthesis (simple 2-op)
                mod_ratio = 2.0
                mod_index = 3.0 * math.exp(-t * 2)
                modulator = self._sine(freq * mod_ratio, t) * mod_index
                sample = self._sine(freq + modulator * freq, t)

            elif bank == SoundBank.ANALOG_PAD:
                # Warm detuned pad
                sample = (
                    self._saw(freq * 0.995, t) * 0.3
                    + self._saw(freq * 1.005, t) * 0.3
                    + self._sine(freq * 0.5, t) * 0.4
                )

            elif bank == SoundBank.DATA_FX:
                # Digital data bleeps
                sample = self._square(freq, t, 0.5) * 0.5
                if t > 0.05:  # Quick decay
                    sample *= math.exp(-(t - 0.05) * 20)

            elif bank == SoundBank.GAME_SFX:
                # Retro game sounds (square wave with pitch bend)
                bend = 1.0 + 0.5 * math.exp(-t * 10)
                sample = self._square(freq * bend, t, 0.5) * 0.6

            else:
                sample = self._sine(freq, t)

            samples.append(sample * note.velocity)

        # Apply envelope
        if bank in [SoundBank.SYNTH_BASS, SoundBank.FM_LEAD]:
            samples = self._envelope_adsr(samples, 0.01, 0.1, 0.6, 0.3)
        elif bank == SoundBank.ANALOG_PAD:
            samples = self._envelope_adsr(samples, 0.2, 0.3, 0.8, 0.5)

        return samples

    def render_pattern(self, pattern: Pattern) -> List[float]:
        """Render a pattern to audio samples"""
        samples = []
        for note in pattern.notes:
            samples.extend(self._render_note(note, pattern.bank))
        return samples

    def render_mml(
        self, mml: str, name: str = "pattern", bank: SoundBank = SoundBank.IMPERIAL_808
    ) -> List[float]:
        """Parse and render MML to audio"""
        pattern = self.parser.parse(mml, name, bank)
        return self.render_pattern(pattern)

    # ═══════════════════════════════════════════════════════════════
    # IMPERIAL TRANSPORT PATTERNS
    # ═══════════════════════════════════════════════════════════════

    def boot_sequence(self) -> List[float]:
        """Imperial boot sequence - dark arpeggio rising"""
        mml = """
        t125 l16 o2 v12
        ; Deep bass hit
        c4 r8
        ; Rising arpeggio (A minor)
        o3 a c e a o4 c e
        ; Final chord swell
        l2 o3 a
        """
        bass = self.render_mml(mml, "boot_bass", SoundBank.SYNTH_BASS)

        # Add pad underneath
        pad_mml = "t125 l1 o3 v8 a"
        pad = self.render_mml(pad_mml, "boot_pad", SoundBank.ANALOG_PAD)

        # Mix (extend shorter to match)
        max_len = max(len(bass), len(pad))
        bass.extend([0.0] * (max_len - len(bass)))
        pad.extend([0.0] * (max_len - len(pad)))

        return [b * 0.7 + p * 0.3 for b, p in zip(bass, pad)]

    def vader_breath(self, cycles: int = 2) -> List[float]:
        """Rhythmic breathing pattern using drums"""
        # Using 808 kit: kick for inhale, noise burst for exhale
        mml = f"""
        t60 l4 o2 v14
        ; Inhale-exhale pattern
        [c r d r]{ cycles }
        """
        drums = self.render_mml(mml, "breath_drums", SoundBank.IMPERIAL_808)

        # Add low drone
        drone_mml = f"t60 l1 o2 v6 [a]{ cycles }"
        drone = self.render_mml(drone_mml, "breath_drone", SoundBank.SYNTH_BASS)

        max_len = max(len(drums), len(drone))
        drums.extend([0.0] * (max_len - len(drums)))
        drone.extend([0.0] * (max_len - len(drone)))

        return [d * 0.6 + dr * 0.4 for d, dr in zip(drums, drone)]

    def handshake(self, is_initiator: bool = True) -> List[float]:
        """Imperial theme inspired handshake melody"""
        if is_initiator:
            # Call pattern (Imperial March rhythm)
            mml = "t125 l8 o4 v12 e e e c g e c"
        else:
            # Response pattern (rising acknowledgment)
            mml = "t125 l8 o4 v12 a c e g a"

        return self.render_mml(mml, "handshake", SoundBank.FM_LEAD)

    def data_stream(self, duration: float = 2.0) -> List[float]:
        """Arpeggiated data transfer sound"""
        # Calculate how many bars we need
        bars = max(1, int(duration / 2))

        mml = f"""
        t140 l16 o4 v10
        ; Fast Am7 arpeggio stream
        [a c e g e c]{ bars * 4 }
        """

        lead = self.render_mml(mml, "data_lead", SoundBank.DATA_FX)

        # Add bass pulse
        bass_mml = f"t140 l4 o2 v8 [a r]{ bars * 2 }"
        bass = self.render_mml(bass_mml, "data_bass", SoundBank.SYNTH_BASS)

        max_len = max(len(lead), len(bass))
        lead.extend([0.0] * (max_len - len(lead)))
        bass.extend([0.0] * (max_len - len(bass)))

        return [l * 0.6 + b * 0.4 for l, b in zip(lead, bass)]

    def success(self) -> List[float]:
        """Rising perfect fifth fanfare"""
        mml = """
        t125 l8 o4 v14
        ; Rising triumph
        a4 e a o5 e2
        """
        lead = self.render_mml(mml, "success_lead", SoundBank.FM_LEAD)

        # Add pad
        pad_mml = "t125 l1 o3 v10 a"
        pad = self.render_mml(pad_mml, "success_pad", SoundBank.ANALOG_PAD)

        max_len = max(len(lead), len(pad))
        lead.extend([0.0] * (max_len - len(lead)))
        pad.extend([0.0] * (max_len - len(pad)))

        return [l * 0.6 + p * 0.4 for l, p in zip(lead, pad)]

    def error(self) -> List[float]:
        """Descending tritone error sound"""
        mml = """
        t125 l8 o4 v14
        ; Ominous descent
        e d# r d c# r c b r
        o3 a#2
        """
        return self.render_mml(mml, "error", SoundBank.FM_LEAD)

    def disconnect(self) -> List[float]:
        """Fade out disconnection"""
        mml = "t100 l2 o4 v10 a g f e d c"
        return self.render_mml(mml, "disconnect", SoundBank.ANALOG_PAD)

    # ═══════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════

    def samples_to_bytes(self, samples: List[float]) -> bytes:
        """Convert float samples to 16-bit PCM bytes"""
        return b"".join(
            struct.pack(
                "<h", int(max(min(s * self.config.default_volume, 1.0), -1.0) * 32767)
            )
            for s in samples
        )

    def save_wav(self, samples: List[float], filepath: str) -> Path:
        """Save samples to WAV file"""
        import wave

        path = Path(filepath)
        pcm_data = self.samples_to_bytes(samples)

        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.config.sample_rate)
            wav.writeframes(pcm_data)

        return path


# ═══════════════════════════════════════════════════════════════
# IMPERIAL PATTERNS (MML format for customization)
# ═══════════════════════════════════════════════════════════════

IMPERIAL_PATTERNS = {
    "boot": """
        t125 l16 o2 v12
        c4 r8
        o3 a c e a o4 c e
        l2 o3 a
    """,
    "breath": """
        t60 l4 o2 v14
        [c r d r]2
    """,
    "handshake_call": """
        t125 l8 o4 v12
        e e e c g e c
    """,
    "handshake_response": """
        t125 l8 o4 v12
        a c e g a
    """,
    "data_stream": """
        t140 l16 o4 v10
        [a c e g e c]8
    """,
    "success": """
        t125 l8 o4 v14
        a4 e a o5 e2
    """,
    "error": """
        t125 l8 o4 v14
        e d# r d c# r c b r
        o3 a#2
    """,
    "disconnect": """
        t100 l2 o4 v10
        a g f e d c
    """,
    # 808 drum patterns
    "drums_main": """
        t125 l16 o2 v14
        ; Bar 1-2: Four on floor
        c4 a8 a8 d4 a8 a8 c4 a8 a8 d4 a8 a8
        ; Bar 3-4: With clap
        c4 a8 a8 d4 b4 c4 a8 a8 d4 b4
    """,
    "drums_break": """
        t125 l16 o2 v12
        a8 a a a a a a a r4 d4 r4 d4
    """,
}


# Test when run directly
if __name__ == "__main__":
    print("🎛️ Imperial Groovebox Test\n")

    groovebox = ImperialGroovebox()

    # Test MML parsing
    print("--- Testing MML Parser ---")
    test_mml = "t120 l8 o4 c d e f g a b o5 c"
    pattern = groovebox.parser.parse(test_mml, "test_scale")
    print(f"  Parsed {len(pattern.notes)} notes")
    print(f"  Total beats: {pattern.total_beats():.1f}")

    # Test sound rendering
    print("\n--- Testing Sound Rendering ---")
    samples = groovebox.render_pattern(pattern)
    print(f"  Rendered {len(samples)} samples ({len(samples)/44100:.2f}s)")

    # Test Imperial patterns
    print("\n--- Testing Imperial Patterns ---")

    sounds = {
        "boot": groovebox.boot_sequence(),
        "breath": groovebox.vader_breath(1),
        "handshake": groovebox.handshake(True),
        "data": groovebox.data_stream(1.0),
        "success": groovebox.success(),
        "error": groovebox.error(),
    }

    for name, samples in sounds.items():
        duration = len(samples) / 44100
        print(f"  {name}: {len(samples)} samples ({duration:.2f}s)")

    # Save test files
    print("\n--- Saving Test WAVs ---")
    output_dir = Path("/tmp/imperial_groovebox")
    output_dir.mkdir(exist_ok=True)

    for name, samples in sounds.items():
        path = groovebox.save_wav(samples, output_dir / f"{name}.wav")
        print(f"  Saved: {path.name}")

    # Full sequence
    print("\n--- Full Transfer Sequence ---")
    full = []
    full.extend(sounds["boot"])
    full.extend([0.0] * 22050)  # 0.5s pause
    full.extend(sounds["breath"])
    full.extend([0.0] * 11025)
    full.extend(sounds["handshake"])
    full.extend([0.0] * 11025)
    full.extend(sounds["data"])
    full.extend([0.0] * 11025)
    full.extend(sounds["success"])

    path = groovebox.save_wav(full, output_dir / "full_sequence.wav")
    print(f"  Saved full sequence: {path}")

    print("\n✅ Imperial Groovebox test complete")
    print(f"   Play with: afplay {output_dir}/full_sequence.wav (macOS)")
