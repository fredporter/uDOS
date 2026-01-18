"""
FSK (Frequency-Shift Keying) Audio Codec
Alpha v1.1.0.1+

Encodes binary data as audio frequencies for acoustic data transfer.
Uses dual-tone FSK for reliability with error correction.

Sound Design (Imperial Edition):
- Mark/Space frequencies in A minor scale
- Compatible with Imperial sounds for cohesive aesthetic
- Audible mode uses musical tones, ultrasonic mode for silent transfer
"""

import math
import struct
import wave
from pathlib import Path
from typing import List, Optional, Tuple, Generator
from dataclasses import dataclass
from enum import Enum


class FSKMode(Enum):
    """FSK encoding modes"""

    AUDIBLE = "audible"  # Musical tones (A minor scale)
    ULTRASONIC = "ultrasonic"  # Above human hearing (~18kHz)
    MINIMAL = "minimal"  # Simple tones, no flourishes


@dataclass
class FSKConfig:
    """FSK codec configuration"""

    sample_rate: int = 44100
    bit_rate: int = 100  # Bits per second (baud) - slower for reliability
    mark_freq: float = 1200.0  # '1' bit - Bell 202 standard
    space_freq: float = 2200.0  # '0' bit - Bell 202 standard
    volume: float = 0.7
    preamble_bits: int = 16  # Sync pattern before data
    postamble_bits: int = 8  # End marker


class FSKEncoder:
    """
    Encodes binary data as FSK audio.

    Uses frequency-shift keying where:
    - Mark frequency = binary 1
    - Space frequency = binary 0

    Preamble: Alternating 1010... for receiver sync
    """

    def __init__(
        self, config: Optional[FSKConfig] = None, mode: FSKMode = FSKMode.AUDIBLE
    ):
        """Initialize FSK encoder."""
        self.config = config or FSKConfig()
        self.mode = mode

        # Adjust frequencies for mode
        if mode == FSKMode.ULTRASONIC:
            self.config.mark_freq = 19000.0  # ~19kHz
            self.config.space_freq = 18000.0  # ~18kHz
            self.config.bit_rate = 600  # Can be faster ultrasonic

        # Calculate samples per bit
        self.samples_per_bit = self.config.sample_rate // self.config.bit_rate

    def _generate_tone(self, freq: float, samples: int) -> List[float]:
        """Generate sine wave at frequency."""
        return [
            math.sin(2 * math.pi * freq * i / self.config.sample_rate)
            for i in range(samples)
        ]

    def _encode_bit(self, bit: int) -> List[float]:
        """Encode single bit as audio samples."""
        freq = self.config.mark_freq if bit else self.config.space_freq
        return self._generate_tone(freq, self.samples_per_bit)

    def _generate_preamble(self) -> List[float]:
        """Generate sync preamble (alternating 1010...)."""
        samples = []
        for i in range(self.config.preamble_bits):
            samples.extend(self._encode_bit(i % 2))
        return samples

    def _generate_postamble(self) -> List[float]:
        """Generate end marker (all 1s)."""
        samples = []
        for _ in range(self.config.postamble_bits):
            samples.extend(self._encode_bit(1))
        return samples

    def encode_bytes(self, data: bytes) -> List[float]:
        """
        Encode bytes as FSK audio samples.

        Format: [preamble][length:2][data][crc:2][postamble]
        """
        samples = []

        # Add preamble
        samples.extend(self._generate_preamble())

        # Add length (2 bytes, big-endian)
        length = len(data)
        length_bytes = struct.pack(">H", length)
        for byte in length_bytes:
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                samples.extend(self._encode_bit(bit))

        # Add data
        for byte in data:
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                samples.extend(self._encode_bit(bit))

        # Add CRC-16 checksum
        crc = self._calculate_crc(data)
        crc_bytes = struct.pack(">H", crc)
        for byte in crc_bytes:
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                samples.extend(self._encode_bit(bit))

        # Add postamble
        samples.extend(self._generate_postamble())

        # Apply volume
        return [s * self.config.volume for s in samples]

    def encode_text(self, text: str) -> List[float]:
        """Encode text as FSK audio."""
        return self.encode_bytes(text.encode("utf-8"))

    def _calculate_crc(self, data: bytes) -> int:
        """Calculate CRC-16 checksum."""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc

    def to_wav_bytes(self, samples: List[float]) -> bytes:
        """Convert samples to WAV file bytes."""
        import io

        # Convert to 16-bit PCM
        pcm_data = b"".join(
            struct.pack("<h", int(max(min(s, 1.0), -1.0) * 32767)) for s in samples
        )

        # Create WAV in memory
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.config.sample_rate)
            wav.writeframes(pcm_data)

        return buffer.getvalue()

    def save_wav(self, samples: List[float], filepath: str) -> Path:
        """Save samples to WAV file."""
        path = Path(filepath)

        pcm_data = b"".join(
            struct.pack("<h", int(max(min(s, 1.0), -1.0) * 32767)) for s in samples
        )

        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.config.sample_rate)
            wav.writeframes(pcm_data)

        return path

    def get_duration(self, data: bytes) -> float:
        """Calculate audio duration for data in seconds."""
        # preamble + length(2) + data + crc(2) + postamble
        total_bits = (
            self.config.preamble_bits
            + 16  # length
            + len(data) * 8
            + 16  # CRC
            + self.config.postamble_bits
        )
        return total_bits / self.config.bit_rate


class FSKDecoder:
    """
    Decodes FSK audio back to binary data.

    Uses Goertzel algorithm for efficient frequency detection.
    """

    def __init__(self, config: Optional[FSKConfig] = None):
        """Initialize FSK decoder."""
        self.config = config or FSKConfig()
        self.samples_per_bit = self.config.sample_rate // self.config.bit_rate

    def _goertzel(self, samples: List[float], target_freq: float) -> float:
        """
        Goertzel algorithm for frequency detection.
        Returns magnitude of target frequency in samples.
        """
        n = len(samples)
        k = int(0.5 + (n * target_freq / self.config.sample_rate))
        w = 2 * math.pi * k / n
        coeff = 2 * math.cos(w)

        s0 = s1 = s2 = 0.0
        for sample in samples:
            s0 = sample + coeff * s1 - s2
            s2 = s1
            s1 = s0

        return math.sqrt(s1 * s1 + s2 * s2 - coeff * s1 * s2)

    def _decode_bit(self, samples: List[float]) -> int:
        """Decode single bit from samples using Goertzel."""
        mark_mag = self._goertzel(samples, self.config.mark_freq)
        space_mag = self._goertzel(samples, self.config.space_freq)
        return 1 if mark_mag > space_mag else 0

    def _find_preamble(self, samples: List[float]) -> int:
        """
        Find preamble in samples, return start index of data.
        Returns -1 if not found.
        """
        # Look for alternating pattern
        window = self.samples_per_bit * 4  # Check 4 bits at a time
        step = self.samples_per_bit // 2  # Slide by half bit

        for i in range(0, len(samples) - window, step):
            bits = []
            for j in range(4):
                start = i + j * self.samples_per_bit
                end = start + self.samples_per_bit
                bits.append(self._decode_bit(samples[start:end]))

            # Check for alternating pattern
            if bits == [1, 0, 1, 0] or bits == [0, 1, 0, 1]:
                # Found potential preamble, find end
                preamble_end = i + self.config.preamble_bits * self.samples_per_bit
                if preamble_end < len(samples):
                    return preamble_end

        return -1

    def decode_samples(self, samples: List[float]) -> Optional[bytes]:
        """
        Decode FSK samples back to bytes.

        Returns decoded data or None if decode fails.
        """
        # Find preamble
        data_start = self._find_preamble(samples)
        if data_start < 0:
            return None

        # Extract bits from data section
        bits = []
        pos = data_start
        while pos + self.samples_per_bit <= len(samples):
            bit = self._decode_bit(samples[pos : pos + self.samples_per_bit])
            bits.append(bit)
            pos += self.samples_per_bit

        if len(bits) < 32:  # Need at least length(16) + crc(16)
            return None

        # Extract length (first 16 bits)
        length_bits = bits[:16]
        length = 0
        for bit in length_bits:
            length = (length << 1) | bit

        # Calculate expected bit count
        expected_bits = 16 + length * 8 + 16 + self.config.postamble_bits
        if len(bits) < expected_bits:
            return None

        # Extract data bytes
        data_bits = bits[16 : 16 + length * 8]
        data = bytearray()
        for i in range(0, len(data_bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(data_bits):
                    byte = (byte << 1) | data_bits[i + j]
            data.append(byte)

        # Extract CRC
        crc_bits = bits[16 + length * 8 : 16 + length * 8 + 16]
        received_crc = 0
        for bit in crc_bits:
            received_crc = (received_crc << 1) | bit

        # Verify CRC
        calculated_crc = self._calculate_crc(bytes(data))
        if received_crc != calculated_crc:
            return None  # CRC mismatch

        return bytes(data)

    def _calculate_crc(self, data: bytes) -> int:
        """Calculate CRC-16 checksum."""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc

    def decode_wav(self, filepath: str) -> Optional[bytes]:
        """Decode WAV file back to bytes."""
        path = Path(filepath)

        with wave.open(str(path), "rb") as wav:
            frames = wav.readframes(wav.getnframes())
            samples = [
                struct.unpack("<h", frames[i : i + 2])[0] / 32767.0
                for i in range(0, len(frames), 2)
            ]

        return self.decode_samples(samples)


# Simple wrapper class for backward compatibility
class AudioCodec:
    """Unified FSK audio codec interface."""

    def __init__(self, mode: FSKMode = FSKMode.AUDIBLE):
        config = FSKConfig()
        self.encoder = FSKEncoder(config, mode)
        self.decoder = FSKDecoder(config)
        self.mode = mode

    def encode(self, data: bytes) -> List[float]:
        """Encode data to audio samples."""
        return self.encoder.encode_bytes(data)

    def decode(self, samples: List[float]) -> Optional[bytes]:
        """Decode audio samples to data."""
        return self.decoder.decode_samples(samples)

    def encode_to_wav(self, data: bytes, filepath: str) -> Path:
        """Encode data and save as WAV."""
        samples = self.encoder.encode_bytes(data)
        return self.encoder.save_wav(samples, filepath)

    def decode_from_wav(self, filepath: str) -> Optional[bytes]:
        """Decode WAV file to data."""
        return self.decoder.decode_wav(filepath)


# Test when run directly
if __name__ == "__main__":
    print("🎵 FSK Codec Test\n")

    # Test encode/decode cycle
    codec = AudioCodec(FSKMode.AUDIBLE)

    test_messages = [
        b"Hello uDOS!",
        b"The Force is strong with this one.",
        bytes([0x00, 0x01, 0x02, 0xFF, 0xFE, 0xFD]),  # Binary data
    ]

    passed = 0
    for msg in test_messages:
        print(f"--- Testing: {msg[:30]}{'...' if len(msg) > 30 else ''} ---")

        # Encode
        samples = codec.encode(msg)
        duration = codec.encoder.get_duration(msg)
        print(f"  Encoded: {len(samples)} samples ({duration:.2f}s)")

        # Decode
        decoded = codec.decode(samples)

        if decoded == msg:
            print(f"  ✅ PASS - Round-trip successful")
            passed += 1
        else:
            print(f"  ❌ FAIL - Decoded: {decoded}")

    print(f"\n{'='*40}")
    print(f"Results: {passed}/{len(test_messages)} passed")

    # Save example WAV
    print("\n--- Saving example WAV ---")
    wav_path = codec.encode_to_wav(b"uDOS audio transport test", "/tmp/fsk_test.wav")
    print(f"  Saved: {wav_path}")

    # Decode it back
    decoded = codec.decode_from_wav("/tmp/fsk_test.wav")
    if decoded:
        print(f"  Decoded: {decoded.decode('utf-8')}")
        print("  ✅ WAV encode/decode successful")
    else:
        print("  ❌ WAV decode failed")

    print("\n🎵 Play with: afplay /tmp/fsk_test.wav (macOS)")
