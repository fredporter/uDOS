"""
Imperial Data Transport - Electro Melodic Edition

Darth Vader meets dialup. Dark synth vibes for acoustic data transfer.
All sounds generated mathematically - no external audio files needed.

Sound Design:
- Deep bass pulses (Vader breathing)
- Filtered sweeps (Imperial scanners)
- Arpeggiated data tones (droid communication)
- Vocoder-style modulation
- Minor key melodies (ominous but musical)
"""

import math
import struct
import wave
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class SoundType(Enum):
    """Types of transport sounds"""

    BOOT = "boot"  # System startup
    DIAL = "dial"  # Initiating connection
    HANDSHAKE = "handshake"  # Establishing link
    CARRIER = "carrier"  # Steady connection
    DATA = "data"  # Data transfer
    SUCCESS = "success"  # Transfer complete
    ERROR = "error"  # Transfer failed
    DISCONNECT = "disconnect"  # Connection closed


@dataclass
class AudioConfig:
    """Audio generation configuration"""

    sample_rate: int = 44100
    bit_depth: int = 16
    channels: int = 1
    volume: float = 0.7


class ImperialSounds:
    """
    Generates dark synth sounds for data transport.

    Aesthetic: Darth Vader's meditation chamber meets 80s synth

    Features:
    - Deep bass pulses (breathing rhythm)
    - Filtered saw/square waves
    - Minor key arpeggios
    - Vocoder-style data encoding
    - Reverb tails for atmosphere
    """

    # Minor pentatonic scale frequencies (A minor - dark and ominous)
    SCALE = {
        "A2": 110.00,
        "C3": 130.81,
        "D3": 146.83,
        "E3": 164.81,
        "G3": 196.00,
        "A3": 220.00,
        "C4": 261.63,
        "D4": 293.66,
        "E4": 329.63,
        "G4": 392.00,
        "A4": 440.00,
        "C5": 523.25,
        "D5": 587.33,
        "E5": 659.26,
        "G5": 783.99,
    }

    # Imperial March inspired intervals (minor 2nd, perfect 5th, tritone)
    DARK_INTERVALS = [1.0, 1.059, 1.335, 1.414, 1.498, 1.682, 2.0]

    def __init__(self, config: Optional[AudioConfig] = None):
        """Initialize sound generator."""
        self.config = config or AudioConfig()

    def _generate_samples(self, duration: float) -> List[float]:
        """Create empty sample buffer."""
        return [0.0] * int(self.config.sample_rate * duration)

    def _sine(self, freq: float, t: float) -> float:
        """Pure sine wave."""
        return math.sin(2 * math.pi * freq * t)

    def _saw(self, freq: float, t: float) -> float:
        """Sawtooth wave (buzzy, aggressive)."""
        period = 1.0 / freq
        phase = (t % period) / period
        return 2.0 * phase - 1.0

    def _square(self, freq: float, t: float, duty: float = 0.5) -> float:
        """Square wave with adjustable duty cycle."""
        period = 1.0 / freq
        phase = (t % period) / period
        return 1.0 if phase < duty else -1.0

    def _triangle(self, freq: float, t: float) -> float:
        """Triangle wave (softer than square)."""
        period = 1.0 / freq
        phase = (t % period) / period
        return 4.0 * abs(phase - 0.5) - 1.0

    def _lowpass(self, samples: List[float], cutoff: float = 0.1) -> List[float]:
        """Simple lowpass filter for warmth."""
        filtered = []
        prev = 0.0
        alpha = cutoff
        for s in samples:
            prev = alpha * s + (1 - alpha) * prev
            filtered.append(prev)
        return filtered

    def _reverb(
        self, samples: List[float], decay: float = 0.3, delay_ms: float = 50
    ) -> List[float]:
        """Simple reverb for atmosphere."""
        delay_samples = int(self.config.sample_rate * delay_ms / 1000)
        output = samples.copy()

        for i in range(delay_samples, len(samples)):
            output[i] += samples[i - delay_samples] * decay

        return output

    def _envelope_adsr(
        self,
        samples: List[float],
        attack: float = 0.1,
        decay: float = 0.1,
        sustain: float = 0.7,
        release: float = 0.2,
    ) -> List[float]:
        """ADSR envelope for musical shaping."""
        n = len(samples)
        sr = self.config.sample_rate

        a_samples = int(attack * sr)
        d_samples = int(decay * sr)
        r_samples = int(release * sr)
        s_samples = n - a_samples - d_samples - r_samples

        output = []
        for i, s in enumerate(samples):
            if i < a_samples:
                # Attack
                env = i / a_samples if a_samples > 0 else 1.0
            elif i < a_samples + d_samples:
                # Decay
                progress = (i - a_samples) / d_samples if d_samples > 0 else 0
                env = 1.0 - progress * (1.0 - sustain)
            elif i < a_samples + d_samples + s_samples:
                # Sustain
                env = sustain
            else:
                # Release
                progress = (
                    (i - a_samples - d_samples - s_samples) / r_samples
                    if r_samples > 0
                    else 1
                )
                env = sustain * (1.0 - progress)

            output.append(s * max(0, env))

        return output

    def _samples_to_bytes(self, samples: List[float]) -> bytes:
        """Convert float samples to 16-bit PCM bytes."""
        max_val = 32767
        return b"".join(
            struct.pack(
                "<h", int(max(min(s * self.config.volume, 1.0), -1.0) * max_val)
            )
            for s in samples
        )

    # ═══════════════════════════════════════════════════════════════
    # VADER BREATHING - Deep rhythmic pulses
    # ═══════════════════════════════════════════════════════════════

    def vader_breath(self, cycles: int = 3) -> bytes:
        """
        Deep rhythmic breathing like Vader's respirator.

        The signature inhale-exhale with filtered bass.
        """
        samples = []
        sr = self.config.sample_rate

        import random

        for cycle in range(cycles):
            # INHALE - rising filtered noise + bass
            inhale_duration = 0.8
            for i in range(int(sr * inhale_duration)):
                t = i / sr
                progress = i / (sr * inhale_duration)

                # Deep bass pulse
                bass = self._sine(55, t) * 0.6  # A1

                # Filtered noise (breath sound)
                noise = random.uniform(-1, 1) * 0.2

                # Rising filter
                cutoff = 0.05 + progress * 0.15

                # Combine with envelope
                env = math.sin(math.pi * progress * 0.5)  # Rise
                sample = (bass + noise * cutoff) * env
                samples.append(sample)

            # Brief pause
            samples.extend([0.0] * int(sr * 0.1))

            # EXHALE - falling filtered noise + bass
            exhale_duration = 1.0
            for i in range(int(sr * exhale_duration)):
                t = i / sr
                progress = i / (sr * exhale_duration)

                # Descending bass
                bass_freq = 55 * (1.0 - progress * 0.3)
                bass = self._sine(bass_freq, t) * 0.6

                # Filtered noise
                noise = random.uniform(-1, 1) * 0.15

                # Falling filter
                cutoff = 0.2 - progress * 0.15

                # Envelope
                env = math.cos(math.pi * progress * 0.5)  # Fall
                sample = (bass + noise * cutoff) * env
                samples.append(sample)

            # Pause between breaths
            samples.extend([0.0] * int(sr * 0.3))

        return self._samples_to_bytes(self._lowpass(samples, 0.15))

    # ═══════════════════════════════════════════════════════════════
    # IMPERIAL BOOT - System startup sequence
    # ═══════════════════════════════════════════════════════════════

    def boot_sequence(self) -> bytes:
        """
        Dark synth startup sequence.

        Like powering up Imperial systems.
        """
        samples = []
        sr = self.config.sample_rate

        # Deep bass hit
        for i in range(int(sr * 0.3)):
            t = i / sr
            progress = i / (sr * 0.3)
            bass = self._sine(55, t) + self._sine(110, t) * 0.5
            env = math.exp(-progress * 5)
            samples.append(bass * env * 0.8)

        # Ascending arpeggio (minor)
        notes = ["A2", "C3", "E3", "A3", "C4", "E4"]
        for note in notes:
            freq = self.SCALE[note]
            for i in range(int(sr * 0.12)):
                t = i / sr
                progress = i / (sr * 0.12)

                # Filtered square wave
                wave = self._square(freq, t, 0.3) * 0.3
                wave += self._sine(freq, t) * 0.4

                env = 1.0 - progress * 0.5
                samples.append(wave * env)

        # Final chord (Am)
        chord_freqs = [self.SCALE["A3"], self.SCALE["C4"], self.SCALE["E4"]]
        for i in range(int(sr * 0.8)):
            t = i / sr
            progress = i / (sr * 0.8)

            chord = sum(self._sine(f, t) for f in chord_freqs) / 3
            chord += self._saw(110, t) * 0.2  # Bass

            env = math.exp(-progress * 2)
            samples.append(chord * env * 0.6)

        return self._samples_to_bytes(self._reverb(samples, 0.4, 80))

    # ═══════════════════════════════════════════════════════════════
    # HANDSHAKE - Two systems connecting
    # ═══════════════════════════════════════════════════════════════

    def handshake(self, is_initiator: bool = True) -> bytes:
        """
        Melodic handshake sequence.

        Call and response between two systems.
        """
        samples = []
        sr = self.config.sample_rate

        # Different melodic phrases for each side
        if is_initiator:
            # Initiator: Imperial theme inspired phrase
            notes = ["E4", "E4", "E4", "C4", "G4", "E4", "C4"]
            durations = [0.15, 0.15, 0.15, 0.1, 0.3, 0.15, 0.4]
        else:
            # Responder: Ascending acknowledgment
            notes = ["A3", "C4", "E4", "G4", "A4"]
            durations = [0.12, 0.12, 0.12, 0.12, 0.4]

        for note, dur in zip(notes, durations):
            freq = self.SCALE[note]
            note_samples = []

            for i in range(int(sr * dur)):
                t = i / sr

                # Layered synth sound
                wave = self._sine(freq, t) * 0.5
                wave += self._triangle(freq, t) * 0.3
                wave += self._sine(freq * 2, t) * 0.15  # Octave

                note_samples.append(wave)

            # ADSR envelope
            note_samples = self._envelope_adsr(note_samples, 0.02, 0.1, 0.6, 0.15)
            samples.extend(note_samples)

        return self._samples_to_bytes(self._reverb(samples, 0.3, 60))

    # ═══════════════════════════════════════════════════════════════
    # DATA TRANSFER - Arpeggiated data stream
    # ═══════════════════════════════════════════════════════════════

    def data_stream(self, duration: float = 3.0, intensity: float = 0.7) -> bytes:
        """
        Melodic data transfer sound.

        Arpeggiated notes representing data flow - like R2-D2
        communicating, but darker and more rhythmic.
        """
        samples = []
        sr = self.config.sample_rate

        import random

        # Arpeggio pattern (Am7 chord)
        arp_notes = ["A3", "C4", "E4", "G4", "E4", "C4"]
        arp_freqs = [self.SCALE[n] for n in arp_notes]

        note_duration = 0.08  # Fast arpeggio
        note_samples = int(sr * note_duration)

        current_sample = 0
        total_samples = int(sr * duration)
        note_index = 0

        # Steady bass pulse underneath
        bass_freq = self.SCALE["A2"]

        while current_sample < total_samples:
            freq = arp_freqs[note_index % len(arp_freqs)]

            # Add some variation based on "data"
            if random.random() > 0.7:
                # Occasional octave jump
                freq *= 2

            for i in range(note_samples):
                if current_sample >= total_samples:
                    break

                t = current_sample / sr
                progress = i / note_samples

                # Main arpeggio note
                wave = self._sine(freq, t) * 0.4
                wave += self._triangle(freq, t) * 0.2

                # Steady bass
                wave += self._sine(bass_freq, t) * 0.25

                # Quick envelope per note
                env = math.sin(math.pi * progress) * intensity

                samples.append(wave * env)
                current_sample += 1

            note_index += 1

        # Add subtle filter sweep
        return self._samples_to_bytes(self._lowpass(samples, 0.2))

    # ═══════════════════════════════════════════════════════════════
    # CARRIER TONE - Steady connection indicator
    # ═══════════════════════════════════════════════════════════════

    def carrier(self, duration: float = 1.0) -> bytes:
        """
        Warm carrier tone with subtle movement.

        Indicates active connection - like a held synth pad.
        """
        samples = []
        sr = self.config.sample_rate

        base_freq = self.SCALE["A3"]  # 220 Hz

        for i in range(int(sr * duration)):
            t = i / sr

            # Base tone with subtle vibrato
            vibrato = 1.0 + math.sin(2 * math.pi * 4 * t) * 0.005
            freq = base_freq * vibrato

            # Warm layered sound
            wave = self._sine(freq, t) * 0.5
            wave += self._triangle(freq, t) * 0.3
            wave += self._sine(freq * 0.5, t) * 0.2  # Sub bass

            samples.append(wave * 0.6)

        return self._samples_to_bytes(samples)

    # ═══════════════════════════════════════════════════════════════
    # SUCCESS - Transfer complete
    # ═══════════════════════════════════════════════════════════════

    def success(self) -> bytes:
        """
        Triumphant success fanfare.

        Short but satisfying - like a level-up sound.
        """
        samples = []
        sr = self.config.sample_rate

        # Rising perfect fifth (powerful, resolved)
        notes = [("A3", 0.15), ("E4", 0.15), ("A4", 0.4)]

        for note, dur in notes:
            freq = self.SCALE[note]
            note_samples = []

            for i in range(int(sr * dur)):
                t = i / sr

                wave = self._sine(freq, t) * 0.5
                wave += self._triangle(freq * 2, t) * 0.2
                wave += self._sine(freq * 0.5, t) * 0.3

                note_samples.append(wave)

            note_samples = self._envelope_adsr(note_samples, 0.02, 0.05, 0.8, 0.2)
            samples.extend(note_samples)

        return self._samples_to_bytes(self._reverb(samples, 0.5, 100))

    # ═══════════════════════════════════════════════════════════════
    # ERROR - Something went wrong
    # ═══════════════════════════════════════════════════════════════

    def error(self) -> bytes:
        """
        Ominous error sound.

        Descending minor - something's not right.
        """
        samples = []
        sr = self.config.sample_rate

        # Descending tritone (the devil's interval)
        notes = [("E4", 0.2), ("A3", 0.4)]  # Down a fifth

        for note, dur in notes:
            freq = self.SCALE[note]
            note_samples = []

            for i in range(int(sr * dur)):
                t = i / sr

                # Harsh square wave
                wave = self._square(freq, t, 0.4) * 0.3
                wave += self._sine(freq, t) * 0.4

                note_samples.append(wave)

            note_samples = self._envelope_adsr(note_samples, 0.01, 0.1, 0.5, 0.3)
            samples.extend(note_samples)

        # Add dissonant low rumble
        rumble = []
        for i in range(int(sr * 0.3)):
            t = i / sr
            progress = i / (sr * 0.3)
            r = self._sine(55, t) * math.exp(-progress * 3) * 0.4
            rumble.append(r)

        samples.extend(rumble)

        return self._samples_to_bytes(self._lowpass(samples, 0.2))

    # ═══════════════════════════════════════════════════════════════
    # DISCONNECT - Connection closing
    # ═══════════════════════════════════════════════════════════════

    def disconnect(self) -> bytes:
        """
        Fade-out disconnection sound.

        Like powering down - graceful ending.
        """
        samples = []
        sr = self.config.sample_rate
        duration = 0.8

        base_freq = self.SCALE["A3"]

        for i in range(int(sr * duration)):
            t = i / sr
            progress = i / (sr * duration)

            # Descending pitch
            freq = base_freq * (1.0 - progress * 0.5)

            # Fading sound
            wave = self._sine(freq, t) * 0.5
            wave += self._triangle(freq, t) * 0.3

            # Exponential decay
            env = math.exp(-progress * 4)
            samples.append(wave * env)

        return self._samples_to_bytes(samples)

    # ═══════════════════════════════════════════════════════════════
    # FULL SEQUENCE - Complete transfer experience
    # ═══════════════════════════════════════════════════════════════

    def full_transfer_sequence(self, data_duration: float = 2.0) -> bytes:
        """
        Complete data transfer sequence.

        Boot → Handshake → Data → Success
        """
        sequence = b""

        # Boot up
        sequence += self.boot_sequence()
        sequence += self._samples_to_bytes([0.0] * int(self.config.sample_rate * 0.3))

        # Vader breath (connection establishing)
        sequence += self.vader_breath(1)

        # Handshake exchange
        sequence += self.handshake(True)
        sequence += self._samples_to_bytes([0.0] * int(self.config.sample_rate * 0.2))
        sequence += self.handshake(False)

        # Data transfer
        sequence += self._samples_to_bytes([0.0] * int(self.config.sample_rate * 0.2))
        sequence += self.data_stream(data_duration)

        # Success
        sequence += self._samples_to_bytes([0.0] * int(self.config.sample_rate * 0.2))
        sequence += self.success()

        return sequence

    def save_wav(self, audio_data: bytes, filepath: str) -> Path:
        """Save audio data to WAV file."""
        path = Path(filepath)

        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(self.config.channels)
            wav.setsampwidth(self.config.bit_depth // 8)
            wav.setframerate(self.config.sample_rate)
            wav.writeframes(audio_data)

        return path


# Alias for backward compatibility
RetroSounds = ImperialSounds


# Quick test
if __name__ == "__main__":
    print("🌑 Generating Imperial Data Transport sounds...")

    sounds = ImperialSounds()

    print("  🫁 Vader breathing...")
    breath = sounds.vader_breath(2)
    sounds.save_wav(breath, "/tmp/vader_breath.wav")

    print("  ⚡ Boot sequence...")
    boot = sounds.boot_sequence()
    sounds.save_wav(boot, "/tmp/boot.wav")

    print("  🤝 Handshake...")
    hs1 = sounds.handshake(True)
    sounds.save_wav(hs1, "/tmp/handshake_init.wav")
    hs2 = sounds.handshake(False)
    sounds.save_wav(hs2, "/tmp/handshake_resp.wav")

    print("  📡 Data stream...")
    data = sounds.data_stream(3.0)
    sounds.save_wav(data, "/tmp/data_stream.wav")

    print("  ✅ Success...")
    success = sounds.success()
    sounds.save_wav(success, "/tmp/success.wav")

    print("  ❌ Error...")
    error = sounds.error()
    sounds.save_wav(error, "/tmp/error.wav")

    print("  🎵 Full sequence...")
    full = sounds.full_transfer_sequence(2.0)
    sounds.save_wav(full, "/tmp/imperial_transfer.wav")

    print("\n✅ All sounds saved to /tmp/")
    print("   Play with: afplay /tmp/imperial_transfer.wav (macOS)")
    print("\n   🌑 The Dark Side of Data Transfer 🌑")
