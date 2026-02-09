"""
Audio Transmitter - Real-time Speaker Output
Alpha v1.1.0.9+

Plays FSK-encoded audio through the system speaker for acoustic data transfer.
Uses pyaudio for cross-platform audio output.

Dependencies:
    pip install pyaudio
    # macOS: brew install portaudio
    # Linux: sudo apt-get install python3-pyaudio
"""

import math
import struct
import threading
import time
from pathlib import Path
from typing import Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

from core.services.logging_api import get_logger

logger = get_logger("audio-transmitter")


class TransmitState(Enum):
    """Transmitter states"""

    IDLE = "idle"
    TRANSMITTING = "transmitting"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class TransmitConfig:
    """Transmitter configuration"""

    sample_rate: int = 44100
    channels: int = 1
    chunk_size: int = 1024  # Samples per buffer
    volume: float = 0.8
    pre_tone_ms: int = 500  # Lead-in tone
    post_tone_ms: int = 200  # Lead-out tone
    inter_packet_ms: int = 100  # Gap between packets


class AudioTransmitter:
    """
    Real-time audio transmitter for FSK data.

    Uses pyaudio to output encoded audio through speakers.
    Supports callback for progress updates.
    """

    def __init__(self, config: Optional[TransmitConfig] = None):
        """Initialize transmitter."""
        self.config = config or TransmitConfig()
        self.state = TransmitState.IDLE
        self._pyaudio = None
        self._stream = None
        self._thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._progress_callback: Optional[Callable] = None

        # Check pyaudio availability
        self._pyaudio_available = self._check_pyaudio()

    def _check_pyaudio(self) -> bool:
        """Check if pyaudio is available."""
        try:
            import pyaudio

            self._pyaudio_module = pyaudio
            return True
        except ImportError:
            logger.warning(
                "[AUD] pyaudio not installed. Install with: pip install pyaudio"
            )
            return False

    def _init_audio(self) -> bool:
        """Initialize pyaudio stream."""
        if not self._pyaudio_available:
            return False

        try:
            import pyaudio

            self._pyaudio = pyaudio.PyAudio()
            self._stream = self._pyaudio.open(
                format=pyaudio.paFloat32,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                output=True,
                frames_per_buffer=self.config.chunk_size,
            )
            return True
        except Exception as e:
            logger.error(f"[AUD] Failed to initialize audio output: {e}")
            self.state = TransmitState.ERROR
            return False

    def _cleanup_audio(self):
        """Clean up audio resources."""
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except:
                pass
            self._stream = None

        if self._pyaudio:
            try:
                self._pyaudio.terminate()
            except:
                pass
            self._pyaudio = None

    def _samples_to_bytes(self, samples: List[float]) -> bytes:
        """Convert float samples to bytes for pyaudio."""
        # Apply volume and convert to float32 bytes
        scaled = [s * self.config.volume for s in samples]
        return struct.pack(f"{len(scaled)}f", *scaled)

    def _generate_tone(self, freq: float, duration_ms: int) -> List[float]:
        """Generate a tone at given frequency."""
        num_samples = int(self.config.sample_rate * duration_ms / 1000)
        return [
            math.sin(2 * math.pi * freq * i / self.config.sample_rate)
            for i in range(num_samples)
        ]

    def transmit_samples(
        self, samples: List[float], progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Transmit audio samples through speaker.

        Args:
            samples: Audio samples (float, -1 to 1)
            progress_callback: Optional callback(percent, state)

        Returns:
            True if transmission completed successfully
        """
        if not self._pyaudio_available:
            logger.error("[AUD] pyaudio not available")
            return False

        if self.state == TransmitState.TRANSMITTING:
            logger.warning("[AUD] Already transmitting")
            return False

        self._progress_callback = progress_callback

        try:
            if not self._init_audio():
                return False

            self.state = TransmitState.TRANSMITTING
            self._stop_flag.clear()

            # Add lead-in tone (helps receiver sync)
            lead_in = self._generate_tone(1000, self.config.pre_tone_ms)
            samples = lead_in + samples

            # Add lead-out tone
            lead_out = self._generate_tone(1000, self.config.post_tone_ms)
            samples = samples + lead_out

            total_samples = len(samples)
            chunk_size = self.config.chunk_size

            logger.info(
                f"[AUD] Transmitting {total_samples} samples ({total_samples/self.config.sample_rate:.2f}s)"
            )

            # Stream in chunks
            for i in range(0, total_samples, chunk_size):
                if self._stop_flag.is_set():
                    logger.info("[AUD] Transmission stopped")
                    break

                chunk = samples[i : i + chunk_size]
                audio_bytes = self._samples_to_bytes(chunk)
                self._stream.write(audio_bytes)

                # Progress update
                if self._progress_callback:
                    percent = min(100, int((i + chunk_size) * 100 / total_samples))
                    self._progress_callback(percent, self.state)

            self.state = TransmitState.IDLE
            return not self._stop_flag.is_set()

        except Exception as e:
            logger.error(f"[AUD] Transmission error: {e}")
            self.state = TransmitState.ERROR
            return False

        finally:
            self._cleanup_audio()

    def transmit_wav(
        self, wav_path: str, progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Transmit a WAV file through speaker.

        Args:
            wav_path: Path to WAV file
            progress_callback: Optional callback(percent, state)

        Returns:
            True if transmission completed
        """
        import wave

        path = Path(wav_path)
        if not path.exists():
            logger.error(f"[AUD] WAV file not found: {wav_path}")
            return False

        try:
            with wave.open(str(path), "rb") as wf:
                # Read WAV data
                n_frames = wf.getnframes()
                sample_width = wf.getsampwidth()
                raw_data = wf.readframes(n_frames)

                # Convert to float samples
                if sample_width == 2:  # 16-bit
                    samples = list(struct.unpack(f"{n_frames}h", raw_data))
                    samples = [s / 32768.0 for s in samples]
                elif sample_width == 4:  # 32-bit float
                    samples = list(struct.unpack(f"{n_frames}f", raw_data))
                else:
                    logger.error(f"[AUD] Unsupported sample width: {sample_width}")
                    return False

                return self.transmit_samples(samples, progress_callback)

        except Exception as e:
            logger.error(f"[AUD] Error reading WAV: {e}")
            return False

    def transmit_data(
        self, data: bytes, progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Encode and transmit data as FSK audio.

        Args:
            data: Binary data to transmit
            progress_callback: Optional callback

        Returns:
            True if transmission completed
        """
        try:
            from .codec import AudioCodec, FSKMode

            codec = AudioCodec(FSKMode.AUDIBLE)
            samples = codec.encode(data)

            logger.info(f"[AUD] Encoded {len(data)} bytes to {len(samples)} samples")
            return self.transmit_samples(samples, progress_callback)

        except ImportError as e:
            logger.error(f"[AUD] Audio codec not available: {e}")
            return False

    def transmit_async(
        self,
        samples: List[float],
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None,
    ):
        """
        Transmit audio in background thread.

        Args:
            samples: Audio samples
            progress_callback: Called with (percent, state)
            completion_callback: Called with (success) when done
        """

        def _transmit_thread():
            success = self.transmit_samples(samples, progress_callback)
            if completion_callback:
                completion_callback(success)

        self._thread = threading.Thread(target=_transmit_thread, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop current transmission."""
        self._stop_flag.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def is_available(self) -> bool:
        """Check if transmitter is available."""
        return self._pyaudio_available

    def get_devices(self) -> List[dict]:
        """Get available output devices."""
        if not self._pyaudio_available:
            return []

        try:
            import pyaudio

            pa = pyaudio.PyAudio()
            devices = []

            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if info["maxOutputChannels"] > 0:
                    devices.append(
                        {
                            "index": i,
                            "name": info["name"],
                            "channels": info["maxOutputChannels"],
                            "sample_rate": int(info["defaultSampleRate"]),
                        }
                    )

            pa.terminate()
            return devices

        except Exception as e:
            logger.error(f"[AUD] Error listing devices: {e}")
            return []


# Test when run directly
if __name__ == "__main__":
    print("🔊 Audio Transmitter Test\n")

    tx = AudioTransmitter()

    if not tx.is_available():
        print("❌ pyaudio not available")
        print("Install with: pip install pyaudio")
        print("macOS: brew install portaudio")
        exit(1)

    print("✅ pyaudio available")
    print("\nOutput devices:")
    for dev in tx.get_devices():
        print(f"  [{dev['index']}] {dev['name']}")

    # Test tone transmission
    print("\n🎵 Transmitting test tone (1 second)...")
    samples = tx._generate_tone(440, 1000)  # A4 note

    def progress(pct, state):
        print(f"\r  Progress: {pct}% [{state.value}]", end="")

    success = tx.transmit_samples(samples, progress)
    print(f"\n  Result: {'✅ Success' if success else '❌ Failed'}")

    # Test data transmission
    print("\n📡 Transmitting test data...")
    success = tx.transmit_data(b"Hello uDOS!", progress)
    print(f"\n  Result: {'✅ Success' if success else '❌ Failed'}")
