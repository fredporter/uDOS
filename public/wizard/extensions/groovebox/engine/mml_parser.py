"""
MML Parser - Music Macro Language Parser
========================================

Parses MML (Music Macro Language) notation into structured pattern data.

MML Syntax Reference:
  Notes:     c d e f g a b (lowercase = natural)
  Sharps:    c+ d+ f+ g+ a+ (or c# etc.)
  Flats:     d- e- b-
  Rests:     r
  Octave:    o4 (set octave 0-8)
  Octave +/- > (up one octave), < (down)
  Length:    l8 (default note length: 8 = eighth note)
  Note len:  c4 (quarter note C), d16 (16th note D)
  Tempo:     t120 (BPM)
  Volume:    v12 (0-15)
  Dots:      c4. (dotted quarter = 1.5x length)
  Ties:      c4&c4 (tied notes)
  Loops:     [c d e f]4 (repeat 4 times)

Drum Mapping (o4 by default):
  C = kick, D = snare, E = low tom, F = mid tom,
  G = high tom/rim, A = closed hat, B = open hat/clap

Version: v1.0.0.0
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any


class TokenType(Enum):
    """MML token types."""

    NOTE = "note"  # c, d, e, f, g, a, b
    REST = "rest"  # r
    OCTAVE = "octave"  # o0-o8
    OCTAVE_UP = "octave_up"  # >
    OCTAVE_DOWN = "octave_down"  # <
    LENGTH = "length"  # l1-l64
    TEMPO = "tempo"  # t40-t300
    VOLUME = "volume"  # v0-v15
    LOOP_START = "loop_start"  # [
    LOOP_END = "loop_end"  # ]N (N = repeat count)
    TIE = "tie"  # &
    DOT = "dot"  # .
    SHARP = "sharp"  # + or #
    FLAT = "flat"  # -
    COMMENT = "comment"  # ; to end of line
    WHITESPACE = "whitespace"
    NEWLINE = "newline"
    NUMBER = "number"


@dataclass
class MMLToken:
    """Single MML token."""

    type: TokenType
    value: Any
    line: int = 0
    column: int = 0

    def __repr__(self):
        return f"Token({self.type.value}, {self.value!r})"


@dataclass
class MMLNote:
    """Parsed note with all attributes."""

    pitch: str  # c, d, e, f, g, a, b, r (rest)
    octave: int = 4  # 0-8
    length: int = 4  # 1=whole, 2=half, 4=quarter, 8=eighth, 16=sixteenth
    dots: int = 0  # Number of dots (each adds 50% duration)
    sharp: bool = False  # Is sharp?
    flat: bool = False  # Is flat?
    velocity: int = 100  # MIDI velocity (0-127)
    tied: bool = False  # Tied to next note?

    @property
    def midi_note(self) -> int:
        """Convert to MIDI note number (0-127)."""
        if self.pitch == "r":
            return -1  # Rest

        # C4 = MIDI 60
        note_map = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}
        midi = 12 * (self.octave + 1) + note_map.get(self.pitch, 0)

        if self.sharp:
            midi += 1
        elif self.flat:
            midi -= 1

        return max(0, min(127, midi))

    @property
    def duration_ticks(self) -> int:
        """Get duration in MIDI ticks (480 ticks per quarter note)."""
        # Quarter note = 480 ticks
        ticks = 480 * 4 // self.length  # Base duration

        # Apply dots
        dot_ticks = ticks
        for _ in range(self.dots):
            dot_ticks //= 2
            ticks += dot_ticks

        return ticks


@dataclass
class MMLPattern:
    """Parsed MML pattern."""

    name: str = ""
    notes: List[MMLNote] = field(default_factory=list)
    tempo: int = 120
    default_length: int = 4
    default_octave: int = 4
    default_volume: int = 12
    bars: int = 0  # Number of bars (calculated)

    def __len__(self):
        return len(self.notes)

    @property
    def total_ticks(self) -> int:
        """Total duration in MIDI ticks."""
        return sum(n.duration_ticks for n in self.notes)

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds based on tempo."""
        ticks_per_beat = 480
        beats = self.total_ticks / ticks_per_beat
        return beats * 60 / self.tempo


class MMLParser:
    """
    MML (Music Macro Language) parser.

    Converts text-based MML notation into structured pattern data.

    Example:
        parser = MMLParser()
        pattern = parser.parse("t120 l8 o4 c d e f g a b > c")
        print(pattern.notes)  # List of MMLNote objects
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset parser state."""
        self.tokens: List[MMLToken] = []
        self.pos = 0
        self.line = 1
        self.column = 1

        # Current state
        self.current_octave = 4
        self.current_length = 4
        self.current_volume = 12
        self.current_tempo = 120

    def parse(self, mml_text: str, name: str = "") -> MMLPattern:
        """
        Parse MML text into a pattern.

        Args:
            mml_text: MML notation string
            name: Optional pattern name

        Returns:
            MMLPattern with parsed notes
        """
        self.reset()
        self.tokens = self._tokenize(mml_text)
        self.pos = 0

        pattern = MMLPattern(
            name=name,
            tempo=self.current_tempo,
            default_length=self.current_length,
            default_octave=self.current_octave,
            default_volume=self.current_volume,
        )

        pattern.notes = self._parse_tokens()
        pattern.tempo = self.current_tempo

        # Calculate bars (assuming 4/4 time, 480 ticks per beat, 4 beats per bar)
        ticks_per_bar = 480 * 4
        pattern.bars = (pattern.total_ticks + ticks_per_bar - 1) // ticks_per_bar

        return pattern

    def _tokenize(self, text: str) -> List[MMLToken]:
        """Tokenize MML text."""
        tokens = []
        i = 0
        line = 1
        column = 1

        while i < len(text):
            char = text[i]

            # Whitespace
            if char in " \t":
                i += 1
                column += 1
                continue

            # Newline
            if char == "\n":
                i += 1
                line += 1
                column = 1
                continue

            # Comment
            if char == ";":
                # Skip to end of line
                while i < len(text) and text[i] != "\n":
                    i += 1
                continue

            # Notes
            if char.lower() in "cdefgab":
                tokens.append(MMLToken(TokenType.NOTE, char.lower(), line, column))
                i += 1
                column += 1
                continue

            # Rest
            if char.lower() == "r":
                tokens.append(MMLToken(TokenType.REST, "r", line, column))
                i += 1
                column += 1
                continue

            # Octave command (oN)
            if char.lower() == "o":
                i += 1
                column += 1
                # Parse number
                num_str = ""
                while i < len(text) and text[i].isdigit():
                    num_str += text[i]
                    i += 1
                    column += 1
                if num_str:
                    tokens.append(
                        MMLToken(TokenType.OCTAVE, int(num_str), line, column)
                    )
                continue

            # Octave up/down
            if char == ">":
                tokens.append(MMLToken(TokenType.OCTAVE_UP, ">", line, column))
                i += 1
                column += 1
                continue
            if char == "<":
                tokens.append(MMLToken(TokenType.OCTAVE_DOWN, "<", line, column))
                i += 1
                column += 1
                continue

            # Length command (lN)
            if char.lower() == "l":
                i += 1
                column += 1
                num_str = ""
                while i < len(text) and text[i].isdigit():
                    num_str += text[i]
                    i += 1
                    column += 1
                if num_str:
                    tokens.append(
                        MMLToken(TokenType.LENGTH, int(num_str), line, column)
                    )
                continue

            # Tempo command (tN)
            if char.lower() == "t":
                i += 1
                column += 1
                num_str = ""
                while i < len(text) and text[i].isdigit():
                    num_str += text[i]
                    i += 1
                    column += 1
                if num_str:
                    tokens.append(MMLToken(TokenType.TEMPO, int(num_str), line, column))
                continue

            # Volume command (vN)
            if char.lower() == "v":
                i += 1
                column += 1
                num_str = ""
                while i < len(text) and text[i].isdigit():
                    num_str += text[i]
                    i += 1
                    column += 1
                if num_str:
                    tokens.append(
                        MMLToken(TokenType.VOLUME, int(num_str), line, column)
                    )
                continue

            # Sharp
            if char in "+#":
                tokens.append(MMLToken(TokenType.SHARP, char, line, column))
                i += 1
                column += 1
                continue

            # Flat
            if char == "-":
                # Could be flat or negative number - check context
                # For now, treat as flat after a note
                tokens.append(MMLToken(TokenType.FLAT, char, line, column))
                i += 1
                column += 1
                continue

            # Dot (dotted note)
            if char == ".":
                tokens.append(MMLToken(TokenType.DOT, ".", line, column))
                i += 1
                column += 1
                continue

            # Tie
            if char == "&":
                tokens.append(MMLToken(TokenType.TIE, "&", line, column))
                i += 1
                column += 1
                continue

            # Loop start
            if char == "[":
                tokens.append(MMLToken(TokenType.LOOP_START, "[", line, column))
                i += 1
                column += 1
                continue

            # Loop end
            if char == "]":
                i += 1
                column += 1
                # Parse repeat count
                num_str = ""
                while i < len(text) and text[i].isdigit():
                    num_str += text[i]
                    i += 1
                    column += 1
                repeat_count = int(num_str) if num_str else 2
                tokens.append(MMLToken(TokenType.LOOP_END, repeat_count, line, column))
                continue

            # Number (note length modifier)
            if char.isdigit():
                num_str = ""
                while i < len(text) and text[i].isdigit():
                    num_str += text[i]
                    i += 1
                    column += 1
                tokens.append(MMLToken(TokenType.NUMBER, int(num_str), line, column))
                continue

            # Unknown character - skip
            i += 1
            column += 1

        return tokens

    def _parse_tokens(self) -> List[MMLNote]:
        """Parse tokens into notes."""
        notes = []
        loop_stack = []  # Stack of (start_index, notes_before_loop)

        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            # Tempo
            if token.type == TokenType.TEMPO:
                self.current_tempo = token.value
                self.pos += 1
                continue

            # Octave
            if token.type == TokenType.OCTAVE:
                self.current_octave = max(0, min(8, token.value))
                self.pos += 1
                continue

            # Octave up/down
            if token.type == TokenType.OCTAVE_UP:
                self.current_octave = min(8, self.current_octave + 1)
                self.pos += 1
                continue
            if token.type == TokenType.OCTAVE_DOWN:
                self.current_octave = max(0, self.current_octave - 1)
                self.pos += 1
                continue

            # Default length
            if token.type == TokenType.LENGTH:
                self.current_length = token.value
                self.pos += 1
                continue

            # Volume
            if token.type == TokenType.VOLUME:
                # Convert MML volume (0-15) to MIDI velocity (0-127)
                self.current_volume = min(15, max(0, token.value))
                self.pos += 1
                continue

            # Loop start
            if token.type == TokenType.LOOP_START:
                loop_stack.append((len(notes), self.pos))
                self.pos += 1
                continue

            # Loop end
            if token.type == TokenType.LOOP_END:
                if loop_stack:
                    start_note_idx, _ = loop_stack.pop()
                    repeat_count = token.value
                    # Get notes inside loop
                    loop_notes = notes[start_note_idx:]
                    # Repeat them
                    for _ in range(repeat_count - 1):
                        notes.extend(
                            [
                                MMLNote(
                                    pitch=n.pitch,
                                    octave=n.octave,
                                    length=n.length,
                                    dots=n.dots,
                                    sharp=n.sharp,
                                    flat=n.flat,
                                    velocity=n.velocity,
                                    tied=n.tied,
                                )
                                for n in loop_notes
                            ]
                        )
                self.pos += 1
                continue

            # Note or rest
            if token.type in (TokenType.NOTE, TokenType.REST):
                note = self._parse_note()
                notes.append(note)
                continue

            # Skip unknown tokens
            self.pos += 1

        return notes

    def _parse_note(self) -> MMLNote:
        """Parse a single note with its modifiers."""
        token = self.tokens[self.pos]

        note = MMLNote(
            pitch=token.value,
            octave=self.current_octave,
            length=self.current_length,
            velocity=int(self.current_volume * 127 / 15),  # Convert to MIDI velocity
        )

        self.pos += 1

        # Look for modifiers after the note
        while self.pos < len(self.tokens):
            next_token = self.tokens[self.pos]

            # Sharp
            if next_token.type == TokenType.SHARP:
                note.sharp = True
                self.pos += 1
                continue

            # Flat
            if next_token.type == TokenType.FLAT:
                note.flat = True
                self.pos += 1
                continue

            # Note length
            if next_token.type == TokenType.NUMBER:
                note.length = next_token.value
                self.pos += 1
                continue

            # Dot
            if next_token.type == TokenType.DOT:
                note.dots += 1
                self.pos += 1
                continue

            # Tie
            if next_token.type == TokenType.TIE:
                note.tied = True
                self.pos += 1
                continue

            # Not a modifier - stop
            break

        return note


def parse_mml(mml_text: str, name: str = "") -> MMLPattern:
    """
    Convenience function to parse MML text.

    Args:
        mml_text: MML notation string
        name: Optional pattern name

    Returns:
        MMLPattern with parsed notes
    """
    parser = MMLParser()
    return parser.parse(mml_text, name)
