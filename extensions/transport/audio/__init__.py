"""
Audio Transport - Imperial Edition

Dark synth sounds + FSK codec + MML groovebox for acoustic data transfer.
Real-time transmitter/receiver for acoustic data transfer.

Status: 100% (sounds + codec + groovebox + transmitter + receiver)
"""

from .sounds import ImperialSounds, RetroSounds, SoundType, AudioConfig
from .codec import FSKEncoder, FSKDecoder, FSKConfig, FSKMode, AudioCodec
from .groovebox import (
    ImperialGroovebox,
    MMLParser,
    GrooveConfig,
    SoundBank,
    Pattern,
    Note,
    IMPERIAL_PATTERNS,
)
from .transmitter import AudioTransmitter, TransmitConfig, TransmitState
from .receiver import AudioReceiver, ReceiveConfig, ReceiveState

__all__ = [
    # Sounds
    "ImperialSounds",
    "RetroSounds",
    "SoundType",
    "AudioConfig",
    # Codec
    "FSKEncoder",
    "FSKDecoder",
    "FSKConfig",
    "FSKMode",
    "AudioCodec",
    # Groovebox
    "ImperialGroovebox",
    "MMLParser",
    "GrooveConfig",
    "SoundBank",
    "Pattern",
    "Note",
    "IMPERIAL_PATTERNS",
    # Real-time I/O
    "AudioTransmitter",
    "TransmitConfig",
    "TransmitState",
    "AudioReceiver",
    "ReceiveConfig",
    "ReceiveState",
]

__version__ = "1.1.0.9"
