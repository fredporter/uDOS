"""
TR-808 Drum Machine
===================

Classic TR-808 style drum machine with 6 core sounds.
Provides MIDI note mapping and pattern generation helpers.

Sounds:
  - Kick (bass drum) - Long, subby 808 kick
  - Snare - Snappy 808 snare
  - Closed Hi-Hat - Tight closed hat
  - Open Hi-Hat - Open hat with decay
  - Clap - Hand clap
  - Cowbell - Classic 808 cowbell

MML Note Mapping (octave 4):
  C = Kick (36)
  D = Snare (38)
  E = Low Tom (41)
  F = Mid Tom (43)
  G = High Tom / Rim (45)
  A = Closed Hat (42)
  B = Open Hat (46)

GM Drum Mapping (Channel 10):
  36 = Bass Drum 1
  38 = Acoustic Snare
  42 = Closed Hi-Hat
  46 = Open Hi-Hat
  39 = Hand Clap
  56 = Cowbell

Version: v1.0.0.0
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from ..engine.mml_parser import MMLPattern, MMLNote, parse_mml


class DrumSound(Enum):
    """808 drum sounds."""

    KICK = "kick"
    SNARE = "snare"
    CLOSED_HAT = "closed_hat"
    OPEN_HAT = "open_hat"
    CLAP = "clap"
    COWBELL = "cowbell"
    LOW_TOM = "low_tom"
    MID_TOM = "mid_tom"
    HIGH_TOM = "high_tom"
    RIMSHOT = "rimshot"


# GM Drum Map (MIDI note numbers)
GM_DRUM_MAP: Dict[DrumSound, int] = {
    DrumSound.KICK: 36,
    DrumSound.SNARE: 38,
    DrumSound.CLOSED_HAT: 42,
    DrumSound.OPEN_HAT: 46,
    DrumSound.CLAP: 39,
    DrumSound.COWBELL: 56,
    DrumSound.LOW_TOM: 41,
    DrumSound.MID_TOM: 43,
    DrumSound.HIGH_TOM: 45,
    DrumSound.RIMSHOT: 37,
}

# MML to Drum Sound mapping (based on note pitch at octave 4)
MML_DRUM_MAP: Dict[str, DrumSound] = {
    "c": DrumSound.KICK,
    "d": DrumSound.SNARE,
    "e": DrumSound.LOW_TOM,
    "f": DrumSound.MID_TOM,
    "g": DrumSound.HIGH_TOM,
    "a": DrumSound.CLOSED_HAT,
    "b": DrumSound.OPEN_HAT,
}


@dataclass
class DrumHit:
    """Single drum hit."""

    sound: DrumSound
    velocity: int = 100  # 0-127
    tick: int = 0  # Position in ticks

    @property
    def midi_note(self) -> int:
        """Get GM drum note number."""
        return GM_DRUM_MAP.get(self.sound, 36)


class Drum808:
    """
    TR-808 style drum machine.

    Provides:
    - Drum pattern parsing from MML
    - Step sequencer grid interface
    - Preset patterns (house, techno, electro, hip-hop)
    - MIDI note mapping for GM drums

    Example:
        drum = Drum808()
        pattern = drum.parse_pattern("t120 l16 o4 [c a a d a a c a]4")
        grid = drum.pattern_to_grid(pattern, steps=16)
    """

    # Preset patterns (MML format)
    PRESETS = {
        "basic_4x4": "t120 l16 o4 [c a a a d a a a c a a a d a a a]2",
        "house_basic": """
            t125 l16 o4 v14
            ; Four-on-the-floor with hats
            [c--- a-a- d--- a-a- c--- a-a- d--- a-a-]4
        """,
        "techno_kick": """
            t130 l16 o4 v15
            ; Hard kick pattern
            [c-c- ---- d--- ---- c--- c--- d--- ----]4
        """,
        "electro_beat": """
            t125 l16 o4 v14
            ; Electro with claps
            [c--- a-a- d-c- a-a- c--- a-b- d--- a-a-]4
        """,
        "hip_hop": """
            t90 l16 o4 v12
            ; Boom bap style
            [c--- a-a- ---- a-d- ---- c-a- d--- a-a-]4
        """,
        "breakbeat": """
            t135 l16 o4 v14
            ; Broken beat pattern
            [c--- a-d- ---- a-c- d--- a--- c-d- a-a-]4
        """,
    }

    def __init__(self):
        """Initialize 808 drum machine."""
        self.tempo = 120
        self.swing = 0.0  # 0.0 - 1.0

    def parse_pattern(self, mml_text: str) -> MMLPattern:
        """
        Parse MML drum pattern.

        Args:
            mml_text: MML notation for drums

        Returns:
            MMLPattern with drum notes
        """
        return parse_mml(mml_text, name="drums")

    def get_preset(self, name: str) -> Optional[MMLPattern]:
        """
        Get preset drum pattern.

        Args:
            name: Preset name (basic_4x4, house_basic, etc.)

        Returns:
            MMLPattern or None if not found
        """
        if name in self.PRESETS:
            return self.parse_pattern(self.PRESETS[name])
        return None

    def list_presets(self) -> List[str]:
        """List available preset names."""
        return list(self.PRESETS.keys())

    def pattern_to_grid(
        self, pattern: MMLPattern, steps: int = 16
    ) -> Dict[DrumSound, List[int]]:
        """
        Convert pattern to step sequencer grid.

        Args:
            pattern: Drum pattern
            steps: Number of steps (16 for one bar)

        Returns:
            Dict mapping drum sounds to list of velocities per step
        """
        # Initialize grid
        grid: Dict[DrumSound, List[int]] = {sound: [0] * steps for sound in DrumSound}

        # Calculate ticks per step
        ticks_per_bar = 480 * 4  # Quarter note = 480, 4 beats per bar
        ticks_per_step = ticks_per_bar // steps

        tick = 0
        for note in pattern.notes:
            if note.pitch != "r":
                # Map MML note to drum sound
                sound = MML_DRUM_MAP.get(note.pitch, DrumSound.KICK)

                # Calculate step position
                step = tick // ticks_per_step
                if 0 <= step < steps:
                    grid[sound][step] = note.velocity

            tick += note.duration_ticks

        return grid

    def grid_to_mml(self, grid: Dict[DrumSound, List[int]], tempo: int = 120) -> str:
        """
        Convert step grid to MML notation.

        Args:
            grid: Step grid (sound -> velocity per step)
            tempo: BPM

        Returns:
            MML string
        """
        steps = 16  # Assume 16 steps

        # Reverse map: DrumSound -> MML note
        sound_to_note = {v: k for k, v in MML_DRUM_MAP.items()}

        mml_parts = [f"t{tempo}", "l16", "o4", "v14"]

        pattern = []
        for step in range(steps):
            step_notes = []
            for sound in [
                DrumSound.KICK,
                DrumSound.SNARE,
                DrumSound.CLOSED_HAT,
                DrumSound.OPEN_HAT,
                DrumSound.CLAP,
            ]:
                if grid.get(sound, [0] * steps)[step] > 0:
                    note = sound_to_note.get(sound, "c")
                    step_notes.append(note)

            if step_notes:
                pattern.append("".join(step_notes))
            else:
                pattern.append("-")

        # Build MML with 4 steps per group
        mml_pattern = []
        for i in range(0, len(pattern), 4):
            group = pattern[i : i + 4]
            mml_pattern.append("".join(group))

        mml_parts.append("[" + " ".join(mml_pattern) + "]")

        return "\n".join(mml_parts)

    def create_basic_beat(self, style: str = "house") -> MMLPattern:
        """
        Create a basic beat pattern.

        Args:
            style: Beat style ('house', 'techno', 'electro', 'hip_hop')

        Returns:
            MMLPattern
        """
        preset_map = {
            "house": "house_basic",
            "techno": "techno_kick",
            "electro": "electro_beat",
            "hip_hop": "hip_hop",
            "breakbeat": "breakbeat",
        }

        preset_name = preset_map.get(style, "basic_4x4")
        return self.get_preset(preset_name) or self.get_preset("basic_4x4")


# Convenience functions


def create_drum_pattern(mml: str) -> MMLPattern:
    """Create drum pattern from MML."""
    drum = Drum808()
    return drum.parse_pattern(mml)


def get_preset_pattern(name: str) -> Optional[MMLPattern]:
    """Get preset drum pattern by name."""
    drum = Drum808()
    return drum.get_preset(name)
