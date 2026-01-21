"""
uDOS Packet Format for QR Transport
Alpha v1.0.1.0+

Defines the packet structure for QR code data transfer.
Includes chunking, CRC validation, and metadata.
"""

import json
import zlib
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class PacketType(Enum):
    """Types of QR packets"""

    DATA = "data"  # Regular data packet
    COMMAND = "command"  # uDOS command
    FILE = "file"  # File transfer
    HANDSHAKE = "handshake"  # Connection initiation
    ACK = "ack"  # Acknowledgment
    ERROR = "error"  # Error notification


@dataclass
class QRPacket:
    """
    uDOS QR Packet structure.

    Format:
    {
        "v": "1.0.1.0",           # Protocol version
        "type": "data",           # Packet type
        "id": "abc123",           # Packet ID (UUID)
        "chunk": 1,               # Current chunk number (1-based)
        "total": 5,               # Total chunks
        "data": "...",            # Payload (base64 encoded)
        "crc": 12345678,          # CRC32 checksum
        "meta": {...}             # Metadata (optional)
    }
    """

    version: str  # Protocol version
    packet_type: PacketType  # Type of packet
    packet_id: str  # Unique packet ID
    chunk_num: int  # Current chunk (1-based)
    total_chunks: int  # Total number of chunks
    data: str  # Payload data (base64 encoded)
    crc: int  # CRC32 checksum
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata

    @property
    def is_single_chunk(self) -> bool:
        """Check if this is a single-chunk packet"""
        return self.total_chunks == 1

    @property
    def is_first_chunk(self) -> bool:
        """Check if this is the first chunk"""
        return self.chunk_num == 1

    @property
    def is_last_chunk(self) -> bool:
        """Check if this is the last chunk"""
        return self.chunk_num == self.total_chunks

    def to_dict(self) -> Dict[str, Any]:
        """Convert packet to dictionary for JSON serialization"""
        return {
            "v": self.version,
            "type": self.packet_type.value,
            "id": self.packet_id,
            "chunk": self.chunk_num,
            "total": self.total_chunks,
            "data": self.data,
            "crc": self.crc,
            "meta": self.metadata or {},
        }

    def to_json(self) -> str:
        """Serialize packet to JSON string"""
        return json.dumps(self.to_dict(), separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QRPacket":
        """Create packet from dictionary"""
        return cls(
            version=data.get("v", "1.0.1.0"),
            packet_type=PacketType(data["type"]),
            packet_id=data["id"],
            chunk_num=data["chunk"],
            total_chunks=data["total"],
            data=data["data"],
            crc=data["crc"],
            metadata=data.get("meta"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "QRPacket":
        """Deserialize packet from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def verify_crc(self, original_data: bytes) -> bool:
        """
        Verify CRC32 checksum against original data.

        Args:
            original_data: Original data bytes (before base64 encoding)

        Returns:
            True if CRC matches
        """
        computed_crc = zlib.crc32(original_data) & 0xFFFFFFFF
        return computed_crc == self.crc

    def compute_crc(self, data: bytes) -> int:
        """
        Compute CRC32 checksum for data.

        Args:
            data: Data bytes to checksum

        Returns:
            CRC32 value
        """
        return zlib.crc32(data) & 0xFFFFFFFF


class PacketBuilder:
    """Helper class for building QR packets"""

    def __init__(self, version: str = "1.0.1.0"):
        """
        Initialize packet builder.

        Args:
            version: Protocol version
        """
        self.version = version

    def create_packet(
        self,
        packet_type: PacketType,
        packet_id: str,
        chunk_num: int,
        total_chunks: int,
        data: bytes,
        metadata: Dict[str, Any] = None,
    ) -> QRPacket:
        """
        Create a QR packet with CRC validation.

        Args:
            packet_type: Type of packet
            packet_id: Unique packet ID
            chunk_num: Current chunk number (1-based)
            total_chunks: Total number of chunks
            data: Raw data bytes
            metadata: Optional metadata

        Returns:
            QRPacket instance
        """
        import base64

        # Encode data as base64
        encoded_data = base64.b64encode(data).decode("ascii")

        # Compute CRC32 for original data
        crc = zlib.crc32(data) & 0xFFFFFFFF

        # Create packet
        packet = QRPacket(
            version=self.version,
            packet_type=packet_type,
            packet_id=packet_id,
            chunk_num=chunk_num,
            total_chunks=total_chunks,
            data=encoded_data,
            crc=crc,
            metadata=metadata,
        )

        return packet

    def create_handshake(
        self, packet_id: str, device_id: str, device_name: str
    ) -> QRPacket:
        """
        Create a handshake packet.

        Args:
            packet_id: Unique packet ID
            device_id: Device identifier
            device_name: Human-readable device name

        Returns:
            Handshake packet
        """
        import base64

        handshake_data = {
            "device_id": device_id,
            "device_name": device_name,
            "timestamp": datetime.now().isoformat(),
            "protocol": self.version,
        }

        data_bytes = json.dumps(handshake_data).encode("utf-8")

        return self.create_packet(
            packet_type=PacketType.HANDSHAKE,
            packet_id=packet_id,
            chunk_num=1,
            total_chunks=1,
            data=data_bytes,
            metadata={"device_name": device_name},
        )

    def create_ack(
        self, packet_id: str, ack_for: str, success: bool = True, message: str = None
    ) -> QRPacket:
        """
        Create an acknowledgment packet.

        Args:
            packet_id: Unique packet ID for this ACK
            ack_for: Packet ID being acknowledged
            success: Whether operation was successful
            message: Optional message

        Returns:
            ACK packet
        """
        ack_data = {
            "ack_for": ack_for,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

        data_bytes = json.dumps(ack_data).encode("utf-8")

        return self.create_packet(
            packet_type=PacketType.ACK,
            packet_id=packet_id,
            chunk_num=1,
            total_chunks=1,
            data=data_bytes,
            metadata={"ack_for": ack_for},
        )

    def create_error(
        self,
        packet_id: str,
        error_code: str,
        error_message: str,
        failed_packet: str = None,
    ) -> QRPacket:
        """
        Create an error packet.

        Args:
            packet_id: Unique packet ID
            error_code: Error code
            error_message: Human-readable error
            failed_packet: ID of packet that failed (if applicable)

        Returns:
            Error packet
        """
        error_data = {
            "code": error_code,
            "message": error_message,
            "failed_packet": failed_packet,
            "timestamp": datetime.now().isoformat(),
        }

        data_bytes = json.dumps(error_data).encode("utf-8")

        return self.create_packet(
            packet_type=PacketType.ERROR,
            packet_id=packet_id,
            chunk_num=1,
            total_chunks=1,
            data=data_bytes,
            metadata={"error_code": error_code},
        )


class PacketAssembler:
    """Assembles multi-chunk packets"""

    def __init__(self):
        """Initialize packet assembler"""
        self.chunks: Dict[str, List[Optional[QRPacket]]] = {}
        self.expected_totals: Dict[str, int] = {}

    def add_chunk(self, packet: QRPacket) -> bool:
        """
        Add a chunk to the assembler.

        Args:
            packet: QR packet chunk

        Returns:
            True if packet set is complete
        """
        packet_id = packet.packet_id

        # Initialize chunk list if needed
        if packet_id not in self.chunks:
            self.chunks[packet_id] = [None] * packet.total_chunks
            self.expected_totals[packet_id] = packet.total_chunks

        # Verify total chunks matches
        if self.expected_totals[packet_id] != packet.total_chunks:
            raise ValueError(
                f"Chunk total mismatch: expected {self.expected_totals[packet_id]}, "
                f"got {packet.total_chunks}"
            )

        # Add chunk (convert to 0-based index)
        chunk_index = packet.chunk_num - 1
        self.chunks[packet_id][chunk_index] = packet

        # Check if complete
        return all(c is not None for c in self.chunks[packet_id])

    def get_assembled_data(self, packet_id: str) -> Optional[bytes]:
        """
        Get assembled data for a complete packet set.

        Args:
            packet_id: Packet ID to assemble

        Returns:
            Assembled data bytes or None if incomplete
        """
        if packet_id not in self.chunks:
            return None

        chunks = self.chunks[packet_id]

        # Check if complete
        if not all(c is not None for c in chunks):
            return None

        # Decode and concatenate chunks
        import base64

        assembled = b""
        for chunk in chunks:
            decoded = base64.b64decode(chunk.data)
            assembled += decoded

        return assembled

    def get_missing_chunks(self, packet_id: str) -> List[int]:
        """
        Get list of missing chunk numbers for a packet.

        Args:
            packet_id: Packet ID

        Returns:
            List of missing chunk numbers (1-based)
        """
        if packet_id not in self.chunks:
            return []

        missing = []
        for i, chunk in enumerate(self.chunks[packet_id]):
            if chunk is None:
                missing.append(i + 1)  # Convert to 1-based

        return missing

    def clear(self, packet_id: str):
        """Clear chunks for a packet ID"""
        if packet_id in self.chunks:
            del self.chunks[packet_id]
        if packet_id in self.expected_totals:
            del self.expected_totals[packet_id]


# Example usage
if __name__ == "__main__":
    print("📦 uDOS QR Packet Format Test\n")

    # Create packet builder
    builder = PacketBuilder()

    # Test 1: Single-chunk data packet
    print("--- Test 1: Single-chunk data packet ---")
    data = b"Hello, uDOS QR Transport!"
    packet = builder.create_packet(
        packet_type=PacketType.DATA,
        packet_id="test-001",
        chunk_num=1,
        total_chunks=1,
        data=data,
        metadata={"test": True},
    )

    print(f"Packet ID: {packet.packet_id}")
    print(f"Type: {packet.packet_type.value}")
    print(f"Chunks: {packet.chunk_num}/{packet.total_chunks}")
    print(f"CRC: {packet.crc}")
    print(f"JSON size: {len(packet.to_json())} bytes")
    print(f"Is single chunk: {packet.is_single_chunk}")
    print()

    # Test 2: Multi-chunk packet assembly
    print("--- Test 2: Multi-chunk packet assembly ---")
    large_data = b"A" * 500 + b"B" * 500 + b"C" * 500
    chunk_size = 500

    # Split into chunks
    chunks = []
    packet_id = "test-002"
    total_chunks = (len(large_data) + chunk_size - 1) // chunk_size

    for i in range(total_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, len(large_data))
        chunk_data = large_data[start:end]

        chunk_packet = builder.create_packet(
            packet_type=PacketType.DATA,
            packet_id=packet_id,
            chunk_num=i + 1,
            total_chunks=total_chunks,
            data=chunk_data,
        )
        chunks.append(chunk_packet)

    print(f"Created {len(chunks)} chunks for {len(large_data)} bytes")

    # Assemble chunks
    assembler = PacketAssembler()
    for chunk in chunks:
        complete = assembler.add_chunk(chunk)
        print(
            f"  Added chunk {chunk.chunk_num}/{chunk.total_chunks}: Complete={complete}"
        )

    assembled_data = assembler.get_assembled_data(packet_id)
    print(f"Assembled data matches: {assembled_data == large_data}")
    print()

    # Test 3: Handshake packet
    print("--- Test 3: Handshake packet ---")
    handshake = builder.create_handshake(
        packet_id="test-003", device_id="device-12345", device_name="Fred's Laptop"
    )
    print(f"Handshake from: {handshake.metadata.get('device_name')}")
    print(f"Packet type: {handshake.packet_type.value}")
    print()

    # Test 4: ACK packet
    print("--- Test 4: ACK packet ---")
    ack = builder.create_ack(
        packet_id="test-004",
        ack_for="test-001",
        success=True,
        message="Data received successfully",
    )
    print(f"ACK for: {ack.metadata.get('ack_for')}")
    print(f"Packet type: {ack.packet_type.value}")
    print()

    print("✅ QR Packet Format test complete")
