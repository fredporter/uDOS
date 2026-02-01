"""
Groovebox Engine Tests
======================

Unit tests for MML parser, sequencer, and MIDI export.
Tests use the ServiceRegistry pattern to load containerized groovebox module.
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add repo root to path for conftest
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import via registry (containerized module pattern)
from core.services.registry import get_service

# Load groovebox engine
groovebox = get_service('groovebox')

# Extract components for tests
MMLParser = groovebox.MMLParser
Sequencer = groovebox.Sequencer
MidiExporter = groovebox.MidiExporter
mml_parser = groovebox.mml_parser
sequencer = groovebox.sequencer
midi_export = groovebox.midi_export
drum_808 = groovebox.instruments.drum_808

# Import specific types for test assertions
parse_mml = mml_parser.parse_mml
MMLPattern = mml_parser.MMLPattern
MMLNote = mml_parser.MMLNote
TokenType = mml_parser.TokenType
SequencerState = sequencer.SequencerState
Track = sequencer.Track
Drum808 = drum_808.Drum808
DrumSound = drum_808.DrumSound
GM_DRUM_MAP = drum_808.GM_DRUM_MAP
create_drum_pattern = drum_808.create_drum_pattern
export_pattern_to_midi = midi_export.export_pattern_to_midi


class TestMMLParser:
    """Tests for MML parser."""

    def test_parse_simple_notes(self):
        """Test parsing simple note sequence."""
        pattern = parse_mml("c d e f g a b")
        assert len(pattern.notes) == 7
        assert pattern.notes[0].pitch == "c"
        assert pattern.notes[6].pitch == "b"

    def test_parse_tempo(self):
        """Test tempo parsing."""
        pattern = parse_mml("t140 c d e")
        assert pattern.tempo == 140

    def test_parse_octave(self):
        """Test octave commands."""
        pattern = parse_mml("o3 c o5 d")
        assert pattern.notes[0].octave == 3
        assert pattern.notes[1].octave == 5

    def test_parse_octave_up_down(self):
        """Test octave shift operators."""
        pattern = parse_mml("o4 c > d < e")
        assert pattern.notes[0].octave == 4
        assert pattern.notes[1].octave == 5
        assert pattern.notes[2].octave == 4

    def test_parse_note_length(self):
        """Test note length parsing."""
        pattern = parse_mml("c4 d8 e16")
        assert pattern.notes[0].length == 4
        assert pattern.notes[1].length == 8
        assert pattern.notes[2].length == 16

    def test_parse_default_length(self):
        """Test default length command."""
        pattern = parse_mml("l8 c d e")
        assert pattern.notes[0].length == 8
        assert pattern.notes[1].length == 8

    def test_parse_sharps_flats(self):
        """Test sharp and flat parsing."""
        pattern = parse_mml("c+ d- e# f")
        assert pattern.notes[0].sharp == True
        assert pattern.notes[1].flat == True
        assert pattern.notes[2].sharp == True
        assert pattern.notes[3].sharp == False

    def test_parse_rest(self):
        """Test rest parsing."""
        pattern = parse_mml("c r d")
        assert len(pattern.notes) == 3
        assert pattern.notes[1].pitch == "r"

    def test_parse_dots(self):
        """Test dotted note parsing."""
        pattern = parse_mml("c4. d8..")
        assert pattern.notes[0].dots == 1
        assert pattern.notes[1].dots == 2

    def test_parse_loop(self):
        """Test loop parsing."""
        pattern = parse_mml("[c d]3")
        assert len(pattern.notes) == 6  # c d repeated 3 times

    def test_parse_comments(self):
        """Test comment handling."""
        pattern = parse_mml("c d ; this is a comment\ne f")
        assert len(pattern.notes) == 4

    def test_parse_volume(self):
        """Test volume parsing."""
        pattern = parse_mml("v15 c v8 d")
        assert pattern.notes[0].velocity == 127  # v15 = max velocity
        assert pattern.notes[1].velocity < 127

    def test_midi_note_conversion(self):
        """Test MIDI note number conversion."""
        pattern = parse_mml("o4 c")
        assert pattern.notes[0].midi_note == 60  # Middle C

        pattern = parse_mml("o4 c+")
        assert pattern.notes[0].midi_note == 61  # C#

    def test_duration_ticks(self):
        """Test duration calculation."""
        pattern = parse_mml("c4 c8 c4.")
        assert pattern.notes[0].duration_ticks == 480  # Quarter note
        assert pattern.notes[1].duration_ticks == 240  # Eighth note
        assert pattern.notes[2].duration_ticks == 720  # Dotted quarter

    def test_drum_pattern(self):
        """Test 808 drum pattern parsing."""
        mml = "t120 l16 o4 c a d a c a d a"
        pattern = parse_mml(mml)
        assert pattern.tempo == 120
        assert len(pattern.notes) == 8


class TestSequencer:
    """Tests for sequencer."""

    def test_sequencer_init(self):
        """Test sequencer initialization."""
        seq = Sequencer(num_tracks=8)
        assert len(seq.tracks) == 8
        assert seq.state == SequencerState.STOPPED

    def test_set_pattern(self):
        """Test setting pattern on track."""
        seq = Sequencer()
        pattern = parse_mml("c d e f")
        seq.set_pattern(0, pattern)
        assert seq.tracks[0].pattern == pattern

    def test_track_mute(self):
        """Test track mute/unmute."""
        seq = Sequencer()
        seq.mute_track(0, True)
        assert seq.tracks[0].muted == True
        seq.mute_track(0, False)
        assert seq.tracks[0].muted == False

    def test_track_solo(self):
        """Test track solo."""
        seq = Sequencer()
        seq.solo_track(1, True)
        assert seq.tracks[1].solo == True

    def test_tempo_property(self):
        """Test tempo getter/setter."""
        seq = Sequencer()
        seq.tempo = 140
        assert seq.tempo == 140

        # Test bounds
        seq.tempo = 500  # Should clamp to 300
        assert seq.tempo == 300

    def test_pattern_grid(self):
        """Test converting pattern to step grid."""
        seq = Sequencer()
        pattern = parse_mml("l16 c r c r c r c r c r c r c r c r")
        seq.set_pattern(0, pattern)
        grid = seq.get_pattern_grid(0, steps=16)

        # Every other step should be active
        assert grid[0] == True
        assert grid[1] == False


class TestMidiExporter:
    """Tests for MIDI exporter."""

    def test_exporter_init(self):
        """Test exporter initialization."""
        exporter = MidiExporter()
        assert len(exporter.patterns) == 0

    def test_add_pattern(self):
        """Test adding pattern."""
        exporter = MidiExporter()
        pattern = parse_mml("c d e f")
        exporter.add_pattern(pattern, channel=0)
        assert len(exporter.patterns) == 1

    def test_export_bytes(self):
        """Test exporting to bytes."""
        exporter = MidiExporter()
        pattern = parse_mml("t120 c d e f")
        exporter.add_pattern(pattern, channel=0)

        midi_bytes = exporter.export_bytes()

        # Check MIDI header
        assert midi_bytes[:4] == b"MThd"
        assert b"MTrk" in midi_bytes

    def test_export_file(self):
        """Test exporting to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.mid"

            pattern = parse_mml("t120 c d e f g")
            success = export_pattern_to_midi(pattern, str(filepath))

            assert success == True
            assert filepath.exists()
            assert filepath.stat().st_size > 0

    def test_export_drum_channel(self):
        """Test exporting drums on GM drum channel."""
        exporter = MidiExporter()
        pattern = parse_mml("t120 l16 o4 c a d a")
        exporter.add_pattern(pattern, channel=9, name="Drums")

        midi_bytes = exporter.export_bytes()

        # Should have MIDI data
        assert len(midi_bytes) > 50


class TestDrum808:
    """Tests for 808 drum machine."""

    def test_drum_init(self):
        """Test drum machine initialization."""
        drum = Drum808()
        assert drum.tempo == 120

    def test_list_presets(self):
        """Test listing presets."""
        drum = Drum808()
        presets = drum.list_presets()
        assert len(presets) > 0
        assert "house_basic" in presets

    def test_get_preset(self):
        """Test getting preset pattern."""
        drum = Drum808()
        pattern = drum.get_preset("house_basic")
        assert pattern is not None
        assert len(pattern.notes) > 0

    def test_pattern_to_grid(self):
        """Test converting pattern to step grid."""
        drum = Drum808()
        pattern = drum.parse_pattern("t120 l16 o4 c a a a d a a a")
        grid = drum.pattern_to_grid(pattern, steps=16)

        # Check kick on step 0
        assert DrumSound.KICK in grid
        assert grid[DrumSound.KICK][0] > 0

        # Check snare on step 4
        assert grid[DrumSound.SNARE][4] > 0

    def test_create_basic_beat(self):
        """Test creating basic beat."""
        drum = Drum808()

        for style in ["house", "techno", "electro", "hip_hop"]:
            pattern = drum.create_basic_beat(style)
            assert pattern is not None
            assert len(pattern.notes) > 0

    def test_gm_drum_map(self):
        """Test GM drum note mapping."""
        assert GM_DRUM_MAP[DrumSound.KICK] == 36
        assert GM_DRUM_MAP[DrumSound.SNARE] == 38
        assert GM_DRUM_MAP[DrumSound.CLOSED_HAT] == 42
        assert GM_DRUM_MAP[DrumSound.OPEN_HAT] == 46


class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self):
        """Test complete workflow: MML -> Pattern -> MIDI."""
        # 1. Parse drum pattern
        mml = """
        t125 l16 o4 v14
        [c--- a-a- d--- a-a- c--- a-b- d--- a-a-]2
        """
        pattern = parse_mml(mml, name="house_beat")

        assert pattern.tempo == 125
        assert len(pattern.notes) > 0

        # 2. Create sequencer and add pattern
        seq = Sequencer()
        seq.set_pattern(0, pattern)
        seq.tempo = pattern.tempo

        assert seq.tracks[0].pattern == pattern

        # 3. Export to MIDI
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "house_beat.mid"

            exporter = MidiExporter()
            exporter.add_pattern(pattern, channel=9, name="Drums")
            success = exporter.export(str(filepath))

            assert success == True
            assert filepath.exists()

    def test_808_to_midi(self):
        """Test 808 preset to MIDI export."""
        drum = Drum808()
        pattern = drum.get_preset("techno_kick")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "techno.mid"

            from extensions.groovebox.engine.midi_export import export_drum_pattern

            success = export_drum_pattern(pattern, str(filepath))

            assert success == True
            assert filepath.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
