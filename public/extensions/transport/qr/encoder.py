"""
uDOS QR Encoder
Alpha v1.0.1.0+

Encodes data/commands into QR codes with chunking and CRC validation.
"""

import base64
import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    import qrcode

    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from .packet import QRPacket, PacketType, PacketBuilder
except ImportError:
    from packet import QRPacket, PacketType, PacketBuilder


class QREncoder:
    """
    QR code encoder for uDOS transport.

    Features:
    - Automatic chunking for large data
    - CRC32 validation
    - PNG/ASCII output
    - Configurable QR code size and error correction
    """

    # Maximum data size per QR code (in bytes, before encoding)
    # QR code Version 40 with High error correction can hold ~1,800 bytes
    # We use 256 bytes to be safe and account for JSON overhead
    MAX_CHUNK_SIZE = 256

    def __init__(
        self,
        chunk_size: int = MAX_CHUNK_SIZE,
        version: Optional[int] = None,
        error_correction: str = "H",
        box_size: int = 10,
        border: int = 4,
    ):
        """
        Initialize QR encoder.

        Args:
            chunk_size: Maximum bytes per chunk (default: 256)
            version: QR code version (1-40, None = auto)
            error_correction: Error correction level (L, M, Q, H)
            box_size: Size of each QR code box in pixels
            border: Border size in boxes
        """
        if not QRCODE_AVAILABLE:
            raise ImportError(
                "qrcode library not available. " "Install with: pip install qrcode[pil]"
            )

        self.chunk_size = min(chunk_size, self.MAX_CHUNK_SIZE)
        self.version = version
        self.box_size = box_size
        self.border = border

        # Map error correction level
        error_levels = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }
        self.error_correction = error_levels.get(
            error_correction, qrcode.constants.ERROR_CORRECT_H
        )

        self.builder = PacketBuilder()

    def encode_data(
        self,
        data: bytes,
        packet_type: PacketType = PacketType.DATA,
        metadata: Dict[str, Any] = None,
    ) -> List[QRPacket]:
        """
        Encode data into QR packets.

        Args:
            data: Raw data bytes
            packet_type: Type of packet
            metadata: Optional metadata

        Returns:
            List of QR packets
        """
        packet_id = str(uuid.uuid4())[:8]  # Short ID

        # Calculate number of chunks needed
        total_chunks = (len(data) + self.chunk_size - 1) // self.chunk_size

        packets = []
        for i in range(total_chunks):
            start = i * self.chunk_size
            end = min(start + self.chunk_size, len(data))
            chunk_data = data[start:end]

            packet = self.builder.create_packet(
                packet_type=packet_type,
                packet_id=packet_id,
                chunk_num=i + 1,
                total_chunks=total_chunks,
                data=chunk_data,
                metadata=metadata,
            )
            packets.append(packet)

        return packets

    def encode_text(
        self,
        text: str,
        packet_type: PacketType = PacketType.DATA,
        metadata: Dict[str, Any] = None,
    ) -> List[QRPacket]:
        """
        Encode text into QR packets.

        Args:
            text: Text to encode
            packet_type: Type of packet
            metadata: Optional metadata

        Returns:
            List of QR packets
        """
        data = text.encode("utf-8")
        return self.encode_data(data, packet_type, metadata)

    def encode_command(
        self, command: str, params: List[str] = None, metadata: Dict[str, Any] = None
    ) -> List[QRPacket]:
        """
        Encode uDOS command into QR packets.

        Args:
            command: Command name
            params: Command parameters
            metadata: Optional metadata

        Returns:
            List of QR packets
        """
        import json

        command_data = {"command": command, "params": params or [], "format": "ucode"}

        data = json.dumps(command_data).encode("utf-8")
        return self.encode_data(data, PacketType.COMMAND, metadata)

    def packet_to_qr(self, packet: QRPacket) -> "qrcode.QRCode":
        """
        Convert packet to QR code object.

        Args:
            packet: QR packet

        Returns:
            QRCode object
        """
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )

        # Add packet JSON to QR code
        qr.add_data(packet.to_json())
        qr.make(fit=True)

        return qr

    def save_packet_qr(
        self,
        packet: QRPacket,
        output_path: Path,
        fill_color: str = "black",
        back_color: str = "white",
    ):
        """
        Save packet as QR code image.

        Args:
            packet: QR packet
            output_path: Output file path
            fill_color: QR code color
            back_color: Background color
        """
        qr = self.packet_to_qr(packet)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.save(output_path)

    def save_packets_qr(
        self, packets: List[QRPacket], output_dir: Path, prefix: str = "qr"
    ):
        """
        Save all packets as QR code images.

        Args:
            packets: List of QR packets
            output_dir: Output directory
            prefix: Filename prefix
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for packet in packets:
            filename = f"{prefix}_{packet.packet_id}_chunk{packet.chunk_num}of{packet.total_chunks}.png"
            output_path = output_dir / filename
            self.save_packet_qr(packet, output_path)

    def packet_to_ascii(self, packet: QRPacket) -> str:
        """
        Convert packet to ASCII QR code.

        Args:
            packet: QR packet

        Returns:
            ASCII representation of QR code
        """
        qr = self.packet_to_qr(packet)

        # Get QR code matrix
        matrix = qr.get_matrix()

        # Convert to ASCII art (█ for black, space for white)
        ascii_lines = []
        for row in matrix:
            line = "".join("█" if cell else " " for cell in row)
            ascii_lines.append(line)

        return "\n".join(ascii_lines)

    def print_packet_qr(self, packet: QRPacket):
        """
        Print packet as ASCII QR code to console.

        Args:
            packet: QR packet
        """
        print(
            f"\n📱 QR Code for packet {packet.packet_id} "
            f"(chunk {packet.chunk_num}/{packet.total_chunks})"
        )
        print("=" * 60)
        print(self.packet_to_ascii(packet))
        print("=" * 60)
        print(f"Type: {packet.packet_type.value}")
        print(f"CRC: {packet.crc}")
        print(f"Data size: {len(packet.data)} bytes (base64)")


# Example usage
if __name__ == "__main__":
    print("📱 uDOS QR Encoder Test\n")

    if not QRCODE_AVAILABLE:
        print("⚠️  qrcode library not available")
        print("Install with: pip install qrcode[pil]")
        exit(1)

    encoder = QREncoder(chunk_size=100)

    # Test 1: Small text (single QR)
    print("--- Test 1: Small text (single QR) ---")
    text = "Hello, uDOS QR Transport!"
    packets = encoder.encode_text(text)
    print(f"Encoded '{text}' into {len(packets)} QR code(s)")

    # Print ASCII QR code
    encoder.print_packet_qr(packets[0])
    print()

    # Test 2: Large text (multiple QRs)
    print("--- Test 2: Large text (multiple QRs) ---")
    large_text = "A" * 250  # Will need multiple chunks
    packets = encoder.encode_text(large_text)
    print(f"Encoded {len(large_text)} bytes into {len(packets)} QR code(s)")
    for packet in packets:
        print(
            f"  Chunk {packet.chunk_num}/{packet.total_chunks}: "
            f"{len(packet.to_json())} bytes (JSON)"
        )
    print()

    # Test 3: Command encoding
    print("--- Test 3: Command encoding ---")
    packets = encoder.encode_command("FILE", ["SHOW", "README.MD"])
    print(f"Encoded command into {len(packets)} QR code(s)")
    print(f"  Type: {packets[0].packet_type.value}")
    print()

    # Test 4: Save QR codes to files
    print("--- Test 4: Save QR codes ---")
    output_dir = Path("memory/.tmp/qr-test")
    encoder.save_packets_qr(packets, output_dir)
    print(f"✅ Saved {len(packets)} QR code(s) to {output_dir}/")

    print("\n✅ QR Encoder test complete")
