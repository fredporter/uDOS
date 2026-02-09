"""
Audio Receiver - Real-time Microphone Capture
Alpha v1.1.0.9+

Captures audio from microphone and decodes FSK data.
Uses pyaudio for cross-platform audio input.

Dependencies:
    pip install pyaudio
    # macOS: brew install portaudio
    # Linux: sudo apt-get install python3-pyaudio
"""

import struct
import threading
import time
from pathlib import Path
from typing import Optional, List, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import deque

from core.services.logging_api import get_logger

logger = get_logger("audio-receiver")


class ReceiveState(Enum):
    """Receiver states"""

    IDLE = "idle"
    LISTENING = "listening"
    RECEIVING = "receiving"  # Detected signal
    DECODING = "decoding"
    ERROR = "error"


@dataclass
class ReceiveConfig:
    """Receiver configuration"""

    sample_rate: int = 44100
    channels: int = 1
    chunk_size: int = 1024  # Samples per buffer
    buffer_seconds: int = 30  # Max recording buffer
    noise_threshold: float = 0.02  # Minimum amplitude to detect signal
    silence_timeout_ms: int = 1000  # Silence before end-of-transmission
    auto_gain: bool = True  # Automatic gain control


class AudioReceiver:
    """
    Real-time audio receiver for FSK data.

    Uses pyaudio to capture audio from microphone.
    Detects FSK signal and decodes data.
    """

    def __init__(self, config: Optional[ReceiveConfig] = None):
        """Initialize receiver."""
        self.config = config or ReceiveConfig()
        self.state = ReceiveState.IDLE
        self._pyaudio = None
        self._stream = None
        self._thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._data_callback: Optional[Callable] = None
        self._status_callback: Optional[Callable] = None

        # Recording buffer
        self._buffer: deque = deque(
            maxlen=int(self.config.sample_rate * self.config.buffer_seconds)
        )

        # Signal detection
        self._signal_detected = False
        self._silence_samples = 0

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
        """Initialize pyaudio input stream."""
        if not self._pyaudio_available:
            return False

        try:
            import pyaudio

            self._pyaudio = pyaudio.PyAudio()
            self._stream = self._pyaudio.open(
                format=pyaudio.paFloat32,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                frames_per_buffer=self.config.chunk_size,
            )
            return True
        except Exception as e:
            logger.error(f"[AUD] Failed to initialize audio input: {e}")
            self.state = ReceiveState.ERROR
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

    def _bytes_to_samples(self, data: bytes) -> List[float]:
        """Convert pyaudio bytes to float samples."""
        n_samples = len(data) // 4  # float32
        return list(struct.unpack(f"{n_samples}f", data))

    def _detect_signal(self, samples: List[float]) -> bool:
        """Detect if samples contain FSK signal (not just noise)."""
        if not samples:
            return False

        # Calculate RMS amplitude
        rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
        return rms > self.config.noise_threshold

    def _apply_auto_gain(self, samples: List[float]) -> List[float]:
        """Apply automatic gain control."""
        if not samples or not self.config.auto_gain:
            return samples

        peak = max(abs(s) for s in samples)
        if peak > 0.1:  # Only boost if there's actual signal
            target = 0.8
            gain = min(target / peak, 5.0)  # Limit gain to 5x
            return [s * gain for s in samples]
        return samples

    def listen_and_decode(
        self,
        timeout_seconds: float = 30.0,
        data_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None,
    ) -> Optional[bytes]:
        """
        Listen for FSK signal and decode data.

        Args:
            timeout_seconds: Max time to listen
            data_callback: Called with decoded bytes when complete
            status_callback: Called with (state, message)

        Returns:
            Decoded bytes or None if timeout/error
        """
        if not self._pyaudio_available:
            logger.error("[AUD] pyaudio not available")
            return None

        if self.state == ReceiveState.LISTENING:
            logger.warning("[AUD] Already listening")
            return None

        self._data_callback = data_callback
        self._status_callback = status_callback

        try:
            if not self._init_audio():
                return None

            self.state = ReceiveState.LISTENING
            self._stop_flag.clear()
            self._buffer.clear()
            self._signal_detected = False
            self._silence_samples = 0

            silence_threshold = int(
                self.config.sample_rate * self.config.silence_timeout_ms / 1000
            )

            start_time = time.time()
            logger.info(f"[AUD] Listening for FSK signal (timeout: {timeout_seconds}s)")

            if status_callback:
                status_callback(self.state, "Listening for signal...")

            while not self._stop_flag.is_set():
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    logger.info("[AUD] Listen timeout")
                    if status_callback:
                        status_callback(self.state, "Timeout")
                    break

                # Read audio chunk
                try:
                    audio_data = self._stream.read(
                        self.config.chunk_size, exception_on_overflow=False
                    )
                except Exception as e:
                    logger.warning(f"[AUD] Read error: {e}")
                    continue

                samples = self._bytes_to_samples(audio_data)
                samples = self._apply_auto_gain(samples)

                # Check for signal
                has_signal = self._detect_signal(samples)

                if has_signal:
                    if not self._signal_detected:
                        self._signal_detected = True
                        self.state = ReceiveState.RECEIVING
                        logger.info("[AUD] Signal detected, recording...")
                        if status_callback:
                            status_callback(self.state, "Signal detected")

                    self._silence_samples = 0
                    self._buffer.extend(samples)

                elif self._signal_detected:
                    # Signal was detected, now silent
                    self._silence_samples += len(samples)
                    self._buffer.extend(samples)  # Include trailing silence

                    if self._silence_samples >= silence_threshold:
                        # End of transmission
                        logger.info(
                            f"[AUD] End of transmission ({len(self._buffer)} samples)"
                        )
                        break

            # Decode captured audio
            if self._signal_detected and len(self._buffer) > 0:
                self.state = ReceiveState.DECODING
                if status_callback:
                    status_callback(self.state, "Decoding...")

                samples_list = list(self._buffer)
                decoded = self._decode_samples(samples_list)

                if decoded:
                    logger.info(f"[AUD] Decoded {len(decoded)} bytes")
                    if data_callback:
                        data_callback(decoded)
                    return decoded
                else:
                    logger.warning("[AUD] Failed to decode signal")
                    if status_callback:
                        status_callback(ReceiveState.ERROR, "Decode failed")

            return None

        except Exception as e:
            logger.error(f"[AUD] Receive error: {e}")
            self.state = ReceiveState.ERROR
            return None

        finally:
            self._cleanup_audio()
            self.state = ReceiveState.IDLE

    def _decode_samples(self, samples: List[float]) -> Optional[bytes]:
        """Decode FSK samples to bytes."""
        try:
            from extensions.transport.audio import AudioCodec, FSKMode

            codec = AudioCodec(FSKMode.AUDIBLE)
            return codec.decode(samples)

        except ImportError as e:
            logger.error(f"[AUD] Audio codec not available: {e}")
            return None
        except Exception as e:
            logger.error(f"[AUD] Decode error: {e}")
            return None

    def listen_async(
        self,
        timeout_seconds: float = 30.0,
        data_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None,
    ):
        """
        Listen in background thread.

        Args:
            timeout_seconds: Max listen time
            data_callback: Called with decoded bytes
            status_callback: Called with (state, message)
        """

        def _listen_thread():
            self.listen_and_decode(timeout_seconds, data_callback, status_callback)

        self._thread = threading.Thread(target=_listen_thread, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop listening."""
        self._stop_flag.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def save_recording(self, filepath: str) -> bool:
        """Save captured audio to WAV file."""
        if not self._buffer:
            logger.warning("[AUD] No audio in buffer")
            return False

        try:
            import wave

            samples = list(self._buffer)
            # Convert to 16-bit PCM
            int_samples = [int(s * 32767) for s in samples]
            int_samples = [max(-32768, min(32767, s)) for s in int_samples]

            with wave.open(filepath, "wb") as wf:
                wf.setnchannels(self.config.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.config.sample_rate)
                wf.writeframes(struct.pack(f"{len(int_samples)}h", *int_samples))

            logger.info(f"[AUD] Saved recording: {filepath}")
            return True

        except Exception as e:
            logger.error(f"[AUD] Error saving recording: {e}")
            return False

    def is_available(self) -> bool:
        """Check if receiver is available."""
        return self._pyaudio_available

    def get_devices(self) -> List[dict]:
        """Get available input devices."""
        if not self._pyaudio_available:
            return []

        try:
            import pyaudio

            pa = pyaudio.PyAudio()
            devices = []

            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if info["maxInputChannels"] > 0:
                    devices.append(
                        {
                            "index": i,
                            "name": info["name"],
                            "channels": info["maxInputChannels"],
                            "sample_rate": int(info["defaultSampleRate"]),
                        }
                    )

            pa.terminate()
            return devices

        except Exception as e:
            logger.error(f"[AUD] Error listing devices: {e}")
            return []

    def get_input_level(self, duration_ms: int = 100) -> float:
        """
        Get current input level (for VU meter display).

        Returns:
            RMS level 0.0 to 1.0
        """
        if not self._pyaudio_available:
            return 0.0

        try:
            if not self._init_audio():
                return 0.0

            samples_needed = int(self.config.sample_rate * duration_ms / 1000)
            all_samples = []

            while len(all_samples) < samples_needed:
                audio_data = self._stream.read(
                    self.config.chunk_size, exception_on_overflow=False
                )
                all_samples.extend(self._bytes_to_samples(audio_data))

            # Calculate RMS
            rms = (sum(s * s for s in all_samples) / len(all_samples)) ** 0.5
            return min(1.0, rms * 3)  # Scale for display

        except Exception as e:
            return 0.0

        finally:
            self._cleanup_audio()


# Test when run directly
if __name__ == "__main__":
    print("🎤 Audio Receiver Test\n")

    rx = AudioReceiver()

    if not rx.is_available():
        print("❌ pyaudio not available")
        print("Install with: pip install pyaudio")
        print("macOS: brew install portaudio")
        exit(1)

    print("✅ pyaudio available")
    print("\nInput devices:")
    for dev in rx.get_devices():
        print(f"  [{dev['index']}] {dev['name']}")

    # Test input level
    print("\n📊 Testing input level (speak into mic)...")
    for i in range(10):
        level = rx.get_input_level(100)
        bar = "█" * int(level * 40) + "░" * (40 - int(level * 40))
        print(f"\r  Level: [{bar}] {level:.2f}", end="")
        time.sleep(0.2)
    print()

    # Test listening
    print("\n🎧 Listening for FSK signal (10 seconds)...")
    print("   (Run transmitter.py test in another terminal)")

    def status_cb(state, msg):
        print(f"\r  Status: [{state.value}] {msg}          ", end="")

    def data_cb(data):
        print(f"\n  ✅ Received: {data}")

    result = rx.listen_and_decode(
        timeout_seconds=10, data_callback=data_cb, status_callback=status_cb
    )

    print(f"\n  Result: {'✅ Data received' if result else '⏱️ Timeout (no signal)'}")
