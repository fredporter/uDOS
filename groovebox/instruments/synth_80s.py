"""
80s Synthesizer Engine
======================

Pure Python implementation of classic 80s synthesizer sounds:
- Juno-style warm pads (PWM, chorus)
- DX7-style FM synthesis (2-op simplified)
- Prophet-style polyphonic leads

Part of uDOS Groovebox Extension v1.0.0.35+

Audio: 16-bit PCM, 44100 Hz mono
"""

import math
import struct
import wave
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Callable
from pathlib import Path
from enum import Enum

from core.services.logging_service import get_logger

logger = get_logger("groovebox-80s-synth")


class SynthType(Enum):
    """80s synthesizer types."""

    JUNO_PAD = "juno"  # Warm analog pads
    DX7_FM = "dx7"  # FM electric piano / bells
    PROPHET_LEAD = "prophet"  # Polyphonic lead


@dataclass
class SynthNote:
    """A synthesizer note event."""

    pitch: int = 60  # MIDI note
    velocity: float = 0.8  # 0-1
    duration: float = 0.5  # seconds
    start_time: float = 0.0  # seconds


@dataclass
class SynthPatch:
    """Synthesizer patch parameters."""

    name: str = "Init"
    synth_type: SynthType = SynthType.JUNO_PAD

    # Oscillator
    detune: float = 0.0  # cents (-100 to 100)
    pulse_width: float = 0.5  # PWM (0.1-0.9)
    pwm_depth: float = 0.0  # PWM LFO depth
    pwm_rate: float = 0.5  # PWM LFO rate Hz

    # FM (DX7)
    fm_ratio: float = 2.0  # Modulator frequency ratio
    fm_index: float = 2.0  # Modulation index
    fm_decay: float = 0.5  # Index envelope decay

    # Filter (Juno/Prophet)
    cutoff: float = 0.7  # 0-1
    resonance: float = 0.3  # 0-1
    env_amount: float = 0.3  # Filter envelope depth

    # Envelope (ADSR)
    attack: float = 0.01  # seconds
    decay: float = 0.2  # seconds
    sustain: float = 0.7  # level 0-1
    release: float = 0.3  # seconds

    # Effects
    chorus_depth: float = 0.3  # 0-1
    chorus_rate: float = 0.8  # Hz


class ADSR:
    """ADSR envelope generator."""

    def __init__(
        self,
        attack: float = 0.01,
        decay: float = 0.2,
        sustain: float = 0.7,
        release: float = 0.3,
        sample_rate: int = 44100,
    ):
        self.attack = max(0.001, attack)
        self.decay = max(0.001, decay)
        self.sustain = sustain
        self.release = max(0.001, release)
        self.sample_rate = sample_rate

        # State
        self.level = 0.0
        self.stage = "idle"  # idle, attack, decay, sustain, release
        self.gate = False

    def trigger(self):
        """Start envelope."""
        self.gate = True
        self.stage = "attack"
        self.level = 0.0

    def release_note(self):
        """Release envelope."""
        self.gate = False
        self.stage = "release"

    def process(self) -> float:
        """Get next envelope value."""
        if self.stage == "idle":
            return 0.0

        if self.stage == "attack":
            rate = 1.0 / (self.attack * self.sample_rate)
            self.level += rate
            if self.level >= 1.0:
                self.level = 1.0
                self.stage = "decay"

        elif self.stage == "decay":
            rate = (1.0 - self.sustain) / (self.decay * self.sample_rate)
            self.level -= rate
            if self.level <= self.sustain:
                self.level = self.sustain
                self.stage = "sustain"

        elif self.stage == "sustain":
            if not self.gate:
                self.stage = "release"

        elif self.stage == "release":
            rate = self.sustain / (self.release * self.sample_rate)
            self.level -= rate
            if self.level <= 0.0:
                self.level = 0.0
                self.stage = "idle"

        return self.level


class LFO:
    """Low Frequency Oscillator."""

    def __init__(self, rate: float = 1.0, sample_rate: int = 44100):
        self.rate = rate
        self.sample_rate = sample_rate
        self.phase = 0.0

    def process(self) -> float:
        """Get next LFO value (-1 to 1)."""
        self.phase += self.rate / self.sample_rate
        if self.phase >= 1.0:
            self.phase -= 1.0
        return math.sin(2.0 * math.pi * self.phase)


class Chorus:
    """Simple stereo chorus effect."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.depth = 0.003  # 3ms max delay
        self.rate = 0.8  # Hz

        # Delay buffer (max 20ms)
        max_delay = int(0.02 * sample_rate)
        self.buffer = [0.0] * max_delay
        self.write_pos = 0

        self.lfo = LFO(self.rate, sample_rate)

    def process(self, sample: float) -> float:
        """Process sample through chorus."""
        # Write to buffer
        self.buffer[self.write_pos] = sample

        # Calculate modulated delay
        lfo_val = self.lfo.process()
        delay_samples = int(
            (0.01 + self.depth * (lfo_val + 1) * 0.5) * self.sample_rate
        )

        # Read from buffer
        read_pos = (self.write_pos - delay_samples) % len(self.buffer)
        delayed = self.buffer[read_pos]

        # Advance write position
        self.write_pos = (self.write_pos + 1) % len(self.buffer)

        # Mix dry and wet
        return sample * 0.7 + delayed * 0.3


class Synth80s:
    """
    80s Synthesizer Engine.

    Generates classic synth sounds from the Juno, DX7, and Prophet.

    Usage:
        synth = Synth80s()
        patch = create_juno_pad()
        samples = synth.render_note(patch, 60, 1.0)  # Middle C, 1 second
    """

    SAMPLE_RATE = 44100

    def __init__(self):
        logger.info("[LOCAL] Synth80s engine initialized")

    def midi_to_freq(self, midi_note: int) -> float:
        """Convert MIDI note to frequency."""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    def render_juno(
        self, patch: SynthPatch, freq: float, duration: float, velocity: float
    ) -> List[float]:
        """
        Render Juno-style warm pad.

        Features:
        - Dual detuned oscillators (saw + PWM pulse)
        - Simple low-pass filter
        - Chorus effect
        """
        samples = int(duration * self.SAMPLE_RATE)
        output = []

        # Components
        env = ADSR(patch.attack, patch.decay, patch.sustain, patch.release)
        filter_env = ADSR(0.01, 0.3, 0.5, 0.5)
        pwm_lfo = LFO(patch.pwm_rate, self.SAMPLE_RATE)
        chorus = Chorus(self.SAMPLE_RATE)
        chorus.depth = patch.chorus_depth * 0.005
        chorus.lfo.rate = patch.chorus_rate

        # Trigger envelopes
        env.trigger()
        filter_env.trigger()

        # Oscillator phases
        phase1 = 0.0  # Saw
        phase2 = 0.0  # Pulse

        # Detune second oscillator
        freq2 = freq * (2.0 ** (patch.detune / 1200.0))

        # Release point
        release_sample = int((duration - patch.release) * self.SAMPLE_RATE)

        for i in range(samples):
            # Release envelope near end
            if i == release_sample:
                env.release_note()
                filter_env.release_note()

            # Get envelope
            amp_env = env.process()
            filt_env = filter_env.process()

            # Saw oscillator 1
            phase1 += freq / self.SAMPLE_RATE
            if phase1 >= 1.0:
                phase1 -= 1.0
            saw = 2.0 * phase1 - 1.0

            # Pulse oscillator 2 with PWM
            phase2 += freq2 / self.SAMPLE_RATE
            if phase2 >= 1.0:
                phase2 -= 1.0

            pwm = patch.pulse_width + patch.pwm_depth * pwm_lfo.process() * 0.3
            pwm = max(0.1, min(0.9, pwm))
            pulse = 1.0 if phase2 < pwm else -1.0

            # Mix oscillators
            osc_mix = (saw + pulse * 0.8) * 0.5

            # Simple low-pass filter (1-pole)
            cutoff_freq = 200 + patch.cutoff * 4000 + filt_env * patch.env_amount * 3000
            fc = cutoff_freq / self.SAMPLE_RATE
            fc = max(0.001, min(0.49, fc))

            if i == 0:
                filtered = osc_mix
            else:
                filtered = output[-1] + fc * (osc_mix - output[-1])

            # Apply VCA
            sample = filtered * amp_env * velocity * 0.6

            # Chorus
            if patch.chorus_depth > 0:
                sample = chorus.process(sample)

            output.append(sample)

        return output

    def render_dx7(
        self, patch: SynthPatch, freq: float, duration: float, velocity: float
    ) -> List[float]:
        """
        Render DX7-style FM synthesis.

        Simplified 2-operator FM:
        - Carrier at note frequency
        - Modulator at ratio * frequency
        - Index envelope for brightness decay
        """
        samples = int(duration * self.SAMPLE_RATE)
        output = []

        # Envelopes
        amp_env = ADSR(patch.attack, patch.decay, patch.sustain, patch.release)
        index_env = ADSR(0.001, patch.fm_decay, 0.2, 0.1)

        amp_env.trigger()
        index_env.trigger()

        # Operator phases
        carrier_phase = 0.0
        mod_phase = 0.0

        mod_freq = freq * patch.fm_ratio

        release_sample = int((duration - patch.release) * self.SAMPLE_RATE)

        for i in range(samples):
            if i == release_sample:
                amp_env.release_note()
                index_env.release_note()

            # Envelopes
            amp = amp_env.process()
            idx = index_env.process()

            # Modulator
            mod_phase += mod_freq / self.SAMPLE_RATE
            if mod_phase >= 1.0:
                mod_phase -= 1.0
            modulator = math.sin(2.0 * math.pi * mod_phase)

            # FM index (modulation depth)
            fm_amount = modulator * patch.fm_index * idx

            # Carrier with FM
            carrier_phase += (freq + freq * fm_amount * 0.1) / self.SAMPLE_RATE
            if carrier_phase >= 1.0:
                carrier_phase -= 1.0
            carrier = math.sin(2.0 * math.pi * carrier_phase)

            sample = carrier * amp * velocity * 0.7
            output.append(sample)

        return output

    def render_prophet(
        self, patch: SynthPatch, freq: float, duration: float, velocity: float
    ) -> List[float]:
        """
        Render Prophet-style polyphonic lead.

        Features:
        - Dual saw oscillators with detune
        - Resonant low-pass filter
        - Punchy envelope
        """
        samples = int(duration * self.SAMPLE_RATE)
        output = []

        # Envelopes
        amp_env = ADSR(patch.attack, patch.decay, patch.sustain, patch.release)
        filter_env = ADSR(0.005, 0.15, 0.4, 0.2)

        amp_env.trigger()
        filter_env.trigger()

        # Oscillators
        phase1 = 0.0
        phase2 = 0.0
        freq2 = freq * (2.0 ** (patch.detune / 1200.0))

        # Filter state
        filter_state = 0.0
        filter_state2 = 0.0

        release_sample = int((duration - patch.release) * self.SAMPLE_RATE)

        for i in range(samples):
            if i == release_sample:
                amp_env.release_note()
                filter_env.release_note()

            amp = amp_env.process()
            filt = filter_env.process()

            # Dual saws
            phase1 += freq / self.SAMPLE_RATE
            if phase1 >= 1.0:
                phase1 -= 1.0

            phase2 += freq2 / self.SAMPLE_RATE
            if phase2 >= 1.0:
                phase2 -= 1.0

            saw1 = 2.0 * phase1 - 1.0
            saw2 = 2.0 * phase2 - 1.0
            osc_mix = (saw1 + saw2) * 0.5

            # Resonant filter (2-pole)
            cutoff = 300 + patch.cutoff * 5000 + filt * patch.env_amount * 4000
            fc = 2.0 * math.sin(math.pi * cutoff / self.SAMPLE_RATE)
            fc = max(0.01, min(0.99, fc))

            fb = patch.resonance * 3.5

            hp = osc_mix - filter_state - fb * filter_state2
            bp = fc * hp + filter_state
            lp = fc * bp + filter_state2

            filter_state = bp
            filter_state2 = lp

            sample = lp * amp * velocity * 0.6
            output.append(sample)

        return output

    def render_note(
        self, patch: SynthPatch, midi_note: int, duration: float, velocity: float = 0.8
    ) -> List[float]:
        """
        Render a single note with the specified patch.

        Args:
            patch: Synth patch settings
            midi_note: MIDI note number
            duration: Note duration in seconds
            velocity: Note velocity (0-1)

        Returns:
            List of audio samples
        """
        freq = self.midi_to_freq(midi_note)

        if patch.synth_type == SynthType.JUNO_PAD:
            return self.render_juno(patch, freq, duration, velocity)
        elif patch.synth_type == SynthType.DX7_FM:
            return self.render_dx7(patch, freq, duration, velocity)
        elif patch.synth_type == SynthType.PROPHET_LEAD:
            return self.render_prophet(patch, freq, duration, velocity)

        return []

    def render_chord(
        self,
        patch: SynthPatch,
        midi_notes: List[int],
        duration: float,
        velocity: float = 0.8,
    ) -> List[float]:
        """
        Render a chord (multiple simultaneous notes).

        Args:
            patch: Synth patch
            midi_notes: List of MIDI notes
            duration: Duration in seconds
            velocity: Velocity (0-1)

        Returns:
            Mixed audio samples
        """
        if not midi_notes:
            return []

        # Render each note
        note_samples = []
        for note in midi_notes:
            samples = self.render_note(patch, note, duration, velocity)
            note_samples.append(samples)

        # Mix (find max length)
        max_len = max(len(s) for s in note_samples)
        mixed = [0.0] * max_len

        for samples in note_samples:
            for i, s in enumerate(samples):
                mixed[i] += s

        # Normalize to prevent clipping
        scale = 1.0 / len(midi_notes)
        return [s * scale for s in mixed]

    def to_wav(self, samples: List[float], output_path: Path) -> Path:
        """Export samples to WAV file."""
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

        logger.info(f"[LOCAL] Exported 80s synth to {output_path}")
        return output_path


# === Preset Patches ===


def create_juno_pad() -> SynthPatch:
    """Warm Juno-60 style pad."""
    return SynthPatch(
        name="Warm Pad",
        synth_type=SynthType.JUNO_PAD,
        detune=8.0,  # Slight detune
        pulse_width=0.5,
        pwm_depth=0.4,  # PWM movement
        pwm_rate=0.3,
        cutoff=0.6,
        resonance=0.2,
        env_amount=0.3,
        attack=0.15,
        decay=0.5,
        sustain=0.8,
        release=0.8,
        chorus_depth=0.4,
        chorus_rate=0.6,
    )


def create_dx7_epiano() -> SynthPatch:
    """DX7 electric piano (Rhodes-like)."""
    return SynthPatch(
        name="E.Piano 1",
        synth_type=SynthType.DX7_FM,
        fm_ratio=1.0,  # 1:1 ratio
        fm_index=3.5,  # Moderate brightness
        fm_decay=0.4,  # Bell-like decay
        attack=0.005,
        decay=0.8,
        sustain=0.3,
        release=0.5,
    )


def create_dx7_bells() -> SynthPatch:
    """DX7 tubular bells."""
    return SynthPatch(
        name="Tubular Bells",
        synth_type=SynthType.DX7_FM,
        fm_ratio=3.5,  # Inharmonic ratio
        fm_index=5.0,  # Bright attack
        fm_decay=0.2,  # Fast decay for bell
        attack=0.001,
        decay=2.0,
        sustain=0.1,
        release=1.0,
    )


def create_prophet_lead() -> SynthPatch:
    """Prophet-5 style lead."""
    return SynthPatch(
        name="Prophet Lead",
        synth_type=SynthType.PROPHET_LEAD,
        detune=12.0,  # Fat detune
        cutoff=0.7,
        resonance=0.5,
        env_amount=0.5,
        attack=0.01,
        decay=0.2,
        sustain=0.6,
        release=0.3,
    )


def create_prophet_brass() -> SynthPatch:
    """Prophet brass ensemble."""
    return SynthPatch(
        name="Poly Brass",
        synth_type=SynthType.PROPHET_LEAD,
        detune=6.0,
        cutoff=0.5,
        resonance=0.3,
        env_amount=0.6,
        attack=0.08,  # Slower attack for brass
        decay=0.3,
        sustain=0.7,
        release=0.4,
    )


# === Preset Library ===

PRESETS: Dict[str, Callable[[], SynthPatch]] = {
    "juno-pad": create_juno_pad,
    "dx7-epiano": create_dx7_epiano,
    "dx7-bells": create_dx7_bells,
    "prophet-lead": create_prophet_lead,
    "prophet-brass": create_prophet_brass,
}


def get_preset(name: str) -> Optional[SynthPatch]:
    """Get preset patch by name."""
    if name in PRESETS:
        return PRESETS[name]()
    return None


def list_presets() -> List[str]:
    """List available preset names."""
    return list(PRESETS.keys())


if __name__ == "__main__":
    # Demo
    synth = Synth80s()

    # Juno pad chord
    pad = create_juno_pad()
    chord = synth.render_chord(pad, [60, 64, 67, 72], 3.0)  # Cmaj7
    synth.to_wav(chord, Path("/tmp/juno_pad.wav"))
    print("Created: /tmp/juno_pad.wav")

    # DX7 E.Piano
    epiano = create_dx7_epiano()
    ep_samples = synth.render_note(epiano, 60, 2.0)
    synth.to_wav(ep_samples, Path("/tmp/dx7_epiano.wav"))
    print("Created: /tmp/dx7_epiano.wav")

    # Prophet lead
    lead = create_prophet_lead()
    lead_samples = synth.render_note(lead, 72, 1.5)
    synth.to_wav(lead_samples, Path("/tmp/prophet_lead.wav"))
    print("Created: /tmp/prophet_lead.wav")
