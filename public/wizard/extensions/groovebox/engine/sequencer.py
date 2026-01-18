"""
Sequencer - Pattern Playback Engine
===================================

Plays MML patterns with timing control, loop support,
and multi-track mixing.

Version: v1.0.0.0
"""

import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Callable, Any

from .mml_parser import MMLPattern, MMLNote


class SequencerState(Enum):
    """Sequencer playback states."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    RECORDING = "recording"


@dataclass
class Track:
    """Single sequencer track."""

    id: int
    name: str
    pattern: Optional[MMLPattern] = None
    volume: float = 1.0  # 0.0 - 1.0
    pan: float = 0.0  # -1.0 (left) to 1.0 (right)
    muted: bool = False
    solo: bool = False
    instrument: str = "default"

    def __repr__(self):
        status = "M" if self.muted else ("S" if self.solo else "-")
        return f"Track({self.id}: {self.name} [{status}])"


@dataclass
class SequencerConfig:
    """Sequencer configuration."""

    tempo: int = 120  # BPM
    time_signature: tuple = (4, 4)  # beats per bar, beat unit
    loop: bool = True  # Loop patterns
    loop_bars: int = 4  # Loop length in bars
    swing: float = 0.0  # Swing amount (0.0 - 1.0)
    metronome: bool = False  # Play metronome


class Sequencer:
    """
    Multi-track pattern sequencer.

    Features:
    - Multi-track playback
    - Tempo and time signature control
    - Loop support
    - Track mute/solo
    - Event callbacks for UI integration

    Example:
        seq = Sequencer()
        seq.set_pattern(0, drum_pattern)
        seq.set_pattern(1, bass_pattern)
        seq.play()
    """

    def __init__(self, num_tracks: int = 8):
        """
        Initialize sequencer.

        Args:
            num_tracks: Number of tracks (default 8)
        """
        self.config = SequencerConfig()
        self.state = SequencerState.STOPPED

        # Tracks
        self.tracks: List[Track] = [
            Track(id=i, name=f"Track {i+1}") for i in range(num_tracks)
        ]

        # Default track names
        default_names = ["Drums", "Bass", "Lead", "Pad", "FX1", "FX2", "FX3", "FX4"]
        for i, track in enumerate(self.tracks):
            if i < len(default_names):
                track.name = default_names[i]

        # Playback state
        self._position = 0  # Current tick position
        self._bar = 0  # Current bar
        self._beat = 0  # Current beat within bar
        self._start_time = 0.0  # Playback start time

        # Threading
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Callbacks
        self._callbacks: Dict[str, List[Callable]] = {
            "note_on": [],  # (track_id, note, velocity)
            "note_off": [],  # (track_id, note)
            "beat": [],  # (bar, beat)
            "bar": [],  # (bar)
            "stop": [],  # ()
            "position": [],  # (tick, bar, beat)
        }

    @property
    def tempo(self) -> int:
        """Get current tempo in BPM."""
        return self.config.tempo

    @tempo.setter
    def tempo(self, bpm: int):
        """Set tempo in BPM."""
        self.config.tempo = max(40, min(300, bpm))

    @property
    def is_playing(self) -> bool:
        """Check if sequencer is playing."""
        return self.state == SequencerState.PLAYING

    @property
    def position_info(self) -> Dict[str, Any]:
        """Get current position information."""
        return {
            "tick": self._position,
            "bar": self._bar,
            "beat": self._beat,
            "state": self.state.value,
        }

    def set_pattern(self, track_id: int, pattern: MMLPattern):
        """
        Set pattern for a track.

        Args:
            track_id: Track index (0-7)
            pattern: MMLPattern to assign
        """
        if 0 <= track_id < len(self.tracks):
            self.tracks[track_id].pattern = pattern

    def clear_pattern(self, track_id: int):
        """Clear pattern from a track."""
        if 0 <= track_id < len(self.tracks):
            self.tracks[track_id].pattern = None

    def set_track_volume(self, track_id: int, volume: float):
        """Set track volume (0.0 - 1.0)."""
        if 0 <= track_id < len(self.tracks):
            self.tracks[track_id].volume = max(0.0, min(1.0, volume))

    def set_track_pan(self, track_id: int, pan: float):
        """Set track pan (-1.0 left to 1.0 right)."""
        if 0 <= track_id < len(self.tracks):
            self.tracks[track_id].pan = max(-1.0, min(1.0, pan))

    def mute_track(self, track_id: int, muted: bool = True):
        """Mute/unmute a track."""
        if 0 <= track_id < len(self.tracks):
            self.tracks[track_id].muted = muted

    def solo_track(self, track_id: int, solo: bool = True):
        """Solo/unsolo a track."""
        if 0 <= track_id < len(self.tracks):
            self.tracks[track_id].solo = solo

    def on(self, event: str, callback: Callable):
        """
        Register event callback.

        Events:
            note_on: (track_id, note, velocity)
            note_off: (track_id, note)
            beat: (bar, beat)
            bar: (bar)
            stop: ()
            position: (tick, bar, beat)
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit(self, event: str, *args):
        """Emit event to callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args)
            except Exception as e:
                pass  # Don't let callback errors stop playback

    def play(self):
        """Start playback."""
        if self.state == SequencerState.PLAYING:
            return

        self._stop_event.clear()
        self.state = SequencerState.PLAYING
        self._start_time = time.time()

        self._playback_thread = threading.Thread(target=self._playback_loop)
        self._playback_thread.daemon = True
        self._playback_thread.start()

    def pause(self):
        """Pause playback."""
        if self.state == SequencerState.PLAYING:
            self.state = SequencerState.PAUSED
            self._stop_event.set()

    def stop(self):
        """Stop playback and reset position."""
        self._stop_event.set()
        self.state = SequencerState.STOPPED
        self._position = 0
        self._bar = 0
        self._beat = 0
        self._emit("stop")

    def rewind(self):
        """Rewind to beginning."""
        self._position = 0
        self._bar = 0
        self._beat = 0

    def _playback_loop(self):
        """Main playback loop (runs in thread)."""
        ticks_per_beat = 480
        beats_per_bar = self.config.time_signature[0]
        ticks_per_bar = ticks_per_beat * beats_per_bar

        # Build note schedule for all tracks
        schedules = self._build_schedules()

        last_beat = -1
        last_bar = -1

        while not self._stop_event.is_set():
            with self._lock:
                # Calculate current position based on time
                elapsed = time.time() - self._start_time
                ticks_per_second = (self.config.tempo / 60) * ticks_per_beat
                self._position = int(elapsed * ticks_per_second)

                # Loop handling
                if self.config.loop:
                    max_ticks = self.config.loop_bars * ticks_per_bar
                    if self._position >= max_ticks:
                        self._position = self._position % max_ticks
                        self._start_time = time.time() - (
                            self._position / ticks_per_second
                        )
                        schedules = self._build_schedules()  # Rebuild for loop

                # Calculate bar and beat
                self._bar = self._position // ticks_per_bar
                beat_in_bar = (self._position % ticks_per_bar) // ticks_per_beat
                self._beat = beat_in_bar

                # Emit beat/bar events
                if self._beat != last_beat:
                    self._emit("beat", self._bar, self._beat)
                    last_beat = self._beat

                if self._bar != last_bar:
                    self._emit("bar", self._bar)
                    last_bar = self._bar

                # Process note events
                for track_id, schedule in enumerate(schedules):
                    if self._should_play_track(track_id):
                        for note_event in schedule:
                            if (
                                note_event["tick"]
                                <= self._position
                                < note_event["tick"] + 10
                            ):
                                if not note_event.get("played"):
                                    note_event["played"] = True
                                    self._emit(
                                        "note_on",
                                        track_id,
                                        note_event["note"],
                                        note_event["velocity"],
                                    )

                # Emit position update
                self._emit("position", self._position, self._bar, self._beat)

            # Sleep for ~1ms resolution
            time.sleep(0.001)

    def _build_schedules(self) -> List[List[Dict]]:
        """Build note schedules for all tracks."""
        schedules = []

        for track in self.tracks:
            track_schedule = []

            if track.pattern:
                tick = 0
                for note in track.pattern.notes:
                    if note.pitch != "r":  # Skip rests
                        track_schedule.append(
                            {
                                "tick": tick,
                                "note": note.midi_note,
                                "velocity": int(note.velocity * track.volume),
                                "duration": note.duration_ticks,
                                "played": False,
                            }
                        )
                    tick += note.duration_ticks

            schedules.append(track_schedule)

        return schedules

    def _should_play_track(self, track_id: int) -> bool:
        """Check if track should play (considering mute/solo)."""
        track = self.tracks[track_id]

        # Check if any track is soloed
        any_solo = any(t.solo for t in self.tracks)

        if any_solo:
            return track.solo and not track.muted
        else:
            return not track.muted

    def get_pattern_grid(self, track_id: int, steps: int = 16) -> List[bool]:
        """
        Get pattern as step grid for UI display.

        Args:
            track_id: Track index
            steps: Number of steps (default 16)

        Returns:
            List of booleans indicating active steps
        """
        grid = [False] * steps

        if 0 <= track_id < len(self.tracks):
            track = self.tracks[track_id]
            if track.pattern:
                # Calculate ticks per step
                ticks_per_bar = 480 * 4  # Assuming 4/4
                ticks_per_step = ticks_per_bar // steps

                tick = 0
                for note in track.pattern.notes:
                    if note.pitch != "r":
                        step = tick // ticks_per_step
                        if 0 <= step < steps:
                            grid[step] = True
                    tick += note.duration_ticks

        return grid
