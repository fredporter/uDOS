"""
uDOS QR Transport
Alpha v1.0.1.0+

Visual data transfer using QR codes with chunked packets and error correction.
Part of the private transport framework.

Features:
- Chunked packet encoding (up to 2KB per QR code)
- CRC32 validation
- uDOS Packet Format compliance
- Offline-capable
- Visual confirmation
"""

__version__ = "1.0.1.0"
__author__ = "uDOS Core Team"

from .encoder import QREncoder
from .decoder import QRDecoder
from .packet import QRPacket, PacketType

__all__ = ["QREncoder", "QRDecoder", "QRPacket", "PacketType"]
