"""
uDOS QR Decoder
Alpha v1.0.1.0+

Decodes QR codes back into data/commands with CRC validation.
"""

import base64
from typing import Optional, List
from pathlib import Path

try:
    from PIL import Image
    from pyzbar import pyzbar

    DECODER_AVAILABLE = True
except ImportError:
    DECODER_AVAILABLE = False

try:
    from .packet import QRPacket, PacketAssembler
except ImportError:
    from packet import QRPacket, PacketAssembler


class QRDecoder:
    """
    QR code decoder for uDOS transport.

    Features:
    - Automatic chunk assembly
    - CRC32 validation
    - PNG/camera input
    - Progress tracking
    """

    def __init__(self):
        """Initialize QR decoder"""
        if not DECODER_AVAILABLE:
            raise ImportError(
                "pyzbar/PIL not available. " "Install with: pip install pyzbar pillow"
            )

        self.assembler = PacketAssembler()

    def decode_image(self, image_path: Path) -> Optional[QRPacket]:
        """
        Decode QR code from image file.

        Args:
            image_path: Path to QR code image

        Returns:
            QRPacket or None if no QR found
        """
        img = Image.open(image_path)
        decoded_objects = pyzbar.decode(img)

        if not decoded_objects:
            return None

        # Get first QR code
        qr_data = decoded_objects[0].data.decode("utf-8")

        # Parse as QR packet
        try:
            packet = QRPacket.from_json(qr_data)
            return packet
        except Exception as e:
            print(f"⚠️  Failed to parse QR packet: {e}")
            return None

    def decode_images(self, image_paths: List[Path]) -> List[QRPacket]:
        """
        Decode multiple QR code images.

        Args:
            image_paths: List of image paths

        Returns:
            List of decoded packets
        """
        packets = []
        for path in image_paths:
            packet = self.decode_image(path)
            if packet:
                packets.append(packet)

        return packets

    def add_packet(self, packet: QRPacket) -> bool:
        """
        Add packet to assembler.

        Args:
            packet: Decoded QR packet

        Returns:
            True if packet set is complete
        """
        return self.assembler.add_chunk(packet)

    def get_assembled_data(self, packet_id: str) -> Optional[bytes]:
        """
        Get assembled data for packet set.

        Args:
            packet_id: Packet ID

        Returns:
            Assembled data bytes or None if incomplete
        """
        return self.assembler.get_assembled_data(packet_id)

    def get_missing_chunks(self, packet_id: str) -> List[int]:
        """
        Get list of missing chunk numbers.

        Args:
            packet_id: Packet ID

        Returns:
            List of missing chunk numbers
        """
        return self.assembler.get_missing_chunks(packet_id)

    def verify_crc(self, packet: QRPacket) -> bool:
        """
        Verify CRC32 checksum for packet.

        Args:
            packet: QR packet

        Returns:
            True if CRC is valid
        """
        # Decode base64 data
        data = base64.b64decode(packet.data)
        return packet.verify_crc(data)

    def decode_and_assemble(
        self, image_paths: List[Path], verify_crc: bool = True
    ) -> Optional[bytes]:
        """
        Decode images and assemble into complete data.

        Args:
            image_paths: List of QR code images
            verify_crc: Whether to verify CRC (default: True)

        Returns:
            Assembled data or None if incomplete/invalid
        """
        # Decode all images
        packets = self.decode_images(image_paths)

        if not packets:
            return None

        # Verify CRC if requested
        if verify_crc:
            for packet in packets:
                if not self.verify_crc(packet):
                    print(
                        f"⚠️  CRC validation failed for packet {packet.packet_id} "
                        f"chunk {packet.chunk_num}"
                    )
                    return None

        # Add all packets to assembler
        packet_id = packets[0].packet_id
        complete = False

        for packet in packets:
            complete = self.add_packet(packet)

        if not complete:
            missing = self.get_missing_chunks(packet_id)
            print(f"⚠️  Incomplete packet set. Missing chunks: {missing}")
            return None

        # Get assembled data
        return self.get_assembled_data(packet_id)


# Example usage
if __name__ == "__main__":
    print("📱 uDOS QR Decoder Test\n")

    if not DECODER_AVAILABLE:
        print("⚠️  pyzbar/PIL not available")
        print("Install with: pip install pyzbar pillow")
        exit(1)

    # This test requires QR images to exist
    # Run encoder.py first to generate test QR codes

    test_dir = Path("memory/.tmp/qr-test")

    if not test_dir.exists():
        print(f"⚠️  Test directory not found: {test_dir}")
        print("Run encoder.py first to generate test QR codes")
        exit(1)

    # Find all QR images
    qr_images = sorted(test_dir.glob("qr_*.png"))

    if not qr_images:
        print(f"⚠️  No QR images found in {test_dir}")
        exit(1)

    print(f"Found {len(qr_images)} QR code image(s)")

    # Decode images
    decoder = QRDecoder()

    print("\n--- Decoding QR codes ---")
    for img_path in qr_images:
        packet = decoder.decode_image(img_path)
        if packet:
            print(
                f"  {img_path.name}: "
                f"Packet {packet.packet_id} "
                f"chunk {packet.chunk_num}/{packet.total_chunks} "
                f"(CRC: {packet.crc})"
            )

            # Verify CRC
            if decoder.verify_crc(packet):
                print(f"    ✅ CRC valid")
            else:
                print(f"    ❌ CRC invalid!")

    # Assemble data
    print("\n--- Assembling packets ---")
    assembled_data = decoder.decode_and_assemble(qr_images, verify_crc=True)

    if assembled_data:
        print(f"✅ Successfully assembled {len(assembled_data)} bytes")

        # Try to decode as JSON (if it's a command)
        try:
            import json

            data_json = json.loads(assembled_data.decode("utf-8"))
            print(f"  Command: {data_json.get('command')}")
            print(f"  Params: {data_json.get('params')}")
        except:
            # Not JSON, show as text
            try:
                print(f"  Data: {assembled_data.decode('utf-8')[:100]}...")
            except:
                print(f"  Data: {len(assembled_data)} bytes (binary)")
    else:
        print("❌ Failed to assemble data")

    print("\n✅ QR Decoder test complete")
