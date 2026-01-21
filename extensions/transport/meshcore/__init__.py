"""
MeshCore Transport Layer
Alpha v1.1.0.5+

Transport wrapper for MeshCore P2P mesh networking.
Provides unified packet interface for mesh communication.

Architecture: CODE CONTAINER
- Container Source: https://github.com/meshcore-dev/MeshCore
- Container Location: extensions/cloned/meshcore/
- Managed By: Wizard Server (clones, updates, packages)
- This Layer: uDOS transport wrapper (our code)

Features:
- Device discovery and pairing
- Encrypted P2P messaging
- Multi-hop packet relay
- Network topology management

Transport Policy: PRIVATE (commands + data allowed)
Realm: user_mesh
Max Packet: 64KB

See: CODE-CONTAINER.md for architecture details
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import time

# Container metadata
CONTAINER_INFO = {
    "id": "meshcore",
    "name": "MeshCore Mesh Networking",
    "source": "https://github.com/meshcore-dev/MeshCore",
    "container_path": "extensions/cloned/meshcore",
    "managed_by": "wizard_server",
    "transport_version": "1.1.0.5",
}

# Check if container is installed
CONTAINER_PATH = Path(__file__).parent.parent.parent / "cloned" / "meshcore"
CONTAINER_INSTALLED = CONTAINER_PATH.exists()

# Import MeshCore service (local transport modules)
try:
    from .meshcore_service import (
        MeshCoreService,
        get_mesh_service,
        ConnectionState,
        NetworkEvent,
        NetworkStats,
    )
    from .meshcore_protocol import (
        MeshMessage,
        MessageType,
        create_message,
        parse_message,
    )
    from .device_registry import (
        DeviceRegistry,
        Device,
        DeviceType,
        DeviceStatus,
        get_device_registry,
    )

    MESHCORE_AVAILABLE = True
except ImportError:
    MESHCORE_AVAILABLE = False


class PacketType(Enum):
    """MeshCore packet types for transport layer."""

    HANDSHAKE = "handshake"  # Device pairing
    DATA = "data"  # File/binary transfer
    COMMAND = "command"  # uDOS command relay
    MESSAGE = "message"  # Text message
    ACK = "ack"  # Acknowledgment
    PING = "ping"  # Connectivity check
    PONG = "pong"  # Ping response
    DISCOVERY = "discovery"  # Device discovery
    BROADCAST = "broadcast"  # Network-wide message


@dataclass
class MeshPacket:
    """Unified packet format for MeshCore transport."""

    packet_id: str
    packet_type: PacketType
    source_id: str
    target_id: str  # "*" for broadcast
    payload: bytes
    timestamp: float = field(default_factory=time.time)
    ttl: int = 8  # Max hops
    hop_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize packet to dictionary."""
        return {
            "packet_id": self.packet_id,
            "packet_type": self.packet_type.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "payload": self.payload.hex(),
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "hop_count": self.hop_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeshPacket":
        """Deserialize packet from dictionary."""
        return cls(
            packet_id=data["packet_id"],
            packet_type=PacketType(data["packet_type"]),
            source_id=data["source_id"],
            target_id=data["target_id"],
            payload=bytes.fromhex(data["payload"]),
            timestamp=data.get("timestamp", time.time()),
            ttl=data.get("ttl", 8),
            hop_count=data.get("hop_count", 0),
            metadata=data.get("metadata", {}),
        )

    def to_bytes(self) -> bytes:
        """Serialize packet to bytes for transmission."""
        return json.dumps(self.to_dict()).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> "MeshPacket":
        """Deserialize packet from bytes."""
        return cls.from_dict(json.loads(data.decode("utf-8")))


class MeshTransport:
    """
    MeshCore transport layer for uDOS.

    Wraps MeshCore service to provide unified packet interface
    for mesh networking operations.
    """

    MAX_PACKET_SIZE = 65536  # 64KB per policy

    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize MeshCore transport.

        Args:
            device_id: This device's unique identifier
        """
        if not MESHCORE_AVAILABLE:
            raise ImportError(
                "MeshCore service not available. "
                "Install play extension: extensions/play/"
            )

        self.service = get_mesh_service()
        self.device_id = device_id or self._generate_device_id()
        self._packet_handlers: Dict[PacketType, List[Callable]] = {}
        self._pending_acks: Dict[str, float] = {}

    def _generate_device_id(self) -> str:
        """Generate unique device ID."""
        import uuid

        return f"mesh-{uuid.uuid4().hex[:8]}"

    def is_available(self) -> bool:
        """Check if MeshCore is available and running."""
        return MESHCORE_AVAILABLE and self.service is not None

    def get_state(self) -> str:
        """Get current connection state."""
        if self.service:
            return self.service.state.value
        return "unavailable"

    def scan(self, timeout: float = 5.0) -> List[Dict[str, Any]]:
        """
        Scan for nearby devices.

        Args:
            timeout: Scan duration in seconds

        Returns:
            List of discovered devices
        """
        if not self.service:
            return []

        self.service.start_discovery(timeout)
        # Wait for scan to complete
        time.sleep(timeout + 0.5)

        devices = []
        for device in self.service.get_devices():
            devices.append(
                {
                    "device_id": device.id,
                    "name": device.name,
                    "type": (
                        device.type.value
                        if hasattr(device.type, "value")
                        else str(device.type)
                    ),
                    "status": (
                        device.status.value
                        if hasattr(device.status, "value")
                        else str(device.status)
                    ),
                    "signal_strength": getattr(device, "signal_strength", -50),
                }
            )

        return devices

    def pair(self, target_id: str) -> bool:
        """
        Pair with a device.

        Args:
            target_id: Target device ID

        Returns:
            True if pairing successful
        """
        if not self.service:
            return False

        # Create handshake packet
        packet = MeshPacket(
            packet_id=f"hs-{int(time.time()*1000)}",
            packet_type=PacketType.HANDSHAKE,
            source_id=self.device_id,
            target_id=target_id,
            payload=json.dumps({"action": "pair_request"}).encode(),
            metadata={"device_name": self.device_id},
        )

        return self.send_packet(packet)

    def unpair(self, target_id: str) -> bool:
        """
        Unpair from a device.

        Args:
            target_id: Target device ID

        Returns:
            True if unpairing successful
        """
        if not self.service:
            return False

        # Create unpair handshake
        packet = MeshPacket(
            packet_id=f"hs-{int(time.time()*1000)}",
            packet_type=PacketType.HANDSHAKE,
            source_id=self.device_id,
            target_id=target_id,
            payload=json.dumps({"action": "unpair_request"}).encode(),
        )

        return self.send_packet(packet)

    def send_data(
        self, target_id: str, data: bytes, metadata: Optional[Dict] = None
    ) -> bool:
        """
        Send binary data to a device.

        Args:
            target_id: Target device ID
            data: Binary data to send
            metadata: Optional metadata

        Returns:
            True if sent successfully
        """
        if len(data) > self.MAX_PACKET_SIZE:
            raise ValueError(
                f"Data exceeds max packet size ({len(data)} > {self.MAX_PACKET_SIZE})"
            )

        packet = MeshPacket(
            packet_id=f"data-{int(time.time()*1000)}",
            packet_type=PacketType.DATA,
            source_id=self.device_id,
            target_id=target_id,
            payload=data,
            metadata=metadata or {},
        )

        return self.send_packet(packet)

    def send_message(self, target_id: str, message: str) -> bool:
        """
        Send text message to a device.

        Args:
            target_id: Target device ID
            message: Text message

        Returns:
            True if sent successfully
        """
        packet = MeshPacket(
            packet_id=f"msg-{int(time.time()*1000)}",
            packet_type=PacketType.MESSAGE,
            source_id=self.device_id,
            target_id=target_id,
            payload=message.encode("utf-8"),
        )

        return self.send_packet(packet)

    def send_command(self, target_id: str, command: str) -> bool:
        """
        Send uDOS command to a remote device.

        Args:
            target_id: Target device ID
            command: uDOS command string

        Returns:
            True if sent successfully
        """
        packet = MeshPacket(
            packet_id=f"cmd-{int(time.time()*1000)}",
            packet_type=PacketType.COMMAND,
            source_id=self.device_id,
            target_id=target_id,
            payload=command.encode("utf-8"),
            metadata={"command_type": "ucode"},
        )

        return self.send_packet(packet)

    def broadcast(self, message: str) -> bool:
        """
        Broadcast message to all connected devices.

        Args:
            message: Text message

        Returns:
            True if broadcast initiated
        """
        packet = MeshPacket(
            packet_id=f"bc-{int(time.time()*1000)}",
            packet_type=PacketType.BROADCAST,
            source_id=self.device_id,
            target_id="*",  # Broadcast
            payload=message.encode("utf-8"),
        )

        return self.send_packet(packet)

    def ping(self, target_id: str) -> Optional[float]:
        """
        Ping a device and measure latency.

        Args:
            target_id: Target device ID

        Returns:
            Latency in milliseconds, or None if failed
        """
        packet = MeshPacket(
            packet_id=f"ping-{int(time.time()*1000)}",
            packet_type=PacketType.PING,
            source_id=self.device_id,
            target_id=target_id,
            payload=b"",
        )

        start_time = time.time()
        self._pending_acks[packet.packet_id] = start_time

        if self.send_packet(packet):
            # Wait for pong (with timeout)
            timeout = 5.0
            while time.time() - start_time < timeout:
                if packet.packet_id not in self._pending_acks:
                    # Got response
                    return (time.time() - start_time) * 1000
                time.sleep(0.1)

        # Timeout
        self._pending_acks.pop(packet.packet_id, None)
        return None

    def send_packet(self, packet: MeshPacket) -> bool:
        """
        Send a packet through MeshCore.

        Args:
            packet: MeshPacket to send

        Returns:
            True if sent successfully
        """
        if not self.service:
            return False

        try:
            # Convert to MeshCore message format
            mesh_msg = create_message(
                msg_type=self._map_packet_type(packet.packet_type),
                source=packet.source_id,
                target=packet.target_id,
                payload=packet.payload,
                ttl=packet.ttl,
            )

            # Send through service
            return self.service.send_message(packet.target_id, mesh_msg)

        except Exception as e:
            print(f"[MESH] Failed to send packet: {e}")
            return False

    def _map_packet_type(self, ptype: PacketType) -> "MessageType":
        """Map transport PacketType to MeshCore MessageType."""
        from extensions.transport.meshcore import MessageType

        mapping = {
            PacketType.HANDSHAKE: MessageType.HANDSHAKE,
            PacketType.DATA: MessageType.DATA,
            PacketType.COMMAND: MessageType.COMMAND,
            PacketType.MESSAGE: MessageType.TEXT,
            PacketType.ACK: MessageType.ACK,
            PacketType.PING: MessageType.PING,
            PacketType.PONG: MessageType.PONG,
            PacketType.DISCOVERY: MessageType.DISCOVERY,
            PacketType.BROADCAST: MessageType.BROADCAST,
        }
        return mapping.get(ptype, MessageType.DATA)

    def register_handler(
        self, packet_type: PacketType, handler: Callable[[MeshPacket], None]
    ):
        """
        Register a handler for incoming packets.

        Args:
            packet_type: Type of packets to handle
            handler: Callback function
        """
        if packet_type not in self._packet_handlers:
            self._packet_handlers[packet_type] = []
        self._packet_handlers[packet_type].append(handler)

    def get_stats(self) -> Dict[str, Any]:
        """Get network statistics."""
        if not self.service:
            return {"status": "unavailable"}

        stats = self.service.get_stats()
        return {
            "status": self.get_state(),
            "device_id": self.device_id,
            "messages_sent": stats.messages_sent,
            "messages_received": stats.messages_received,
            "bytes_sent": stats.bytes_sent,
            "bytes_received": stats.bytes_received,
            "devices_discovered": stats.devices_discovered,
            "uptime_seconds": stats.uptime_seconds,
        }

    def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of known devices."""
        if not self.service:
            return []

        return [
            {
                "device_id": d.id,
                "name": d.name,
                "type": d.type.value if hasattr(d.type, "value") else str(d.type),
                "status": (
                    d.status.value if hasattr(d.status, "value") else str(d.status)
                ),
                "signal_strength": getattr(d, "signal_strength", None),
            }
            for d in self.service.get_devices()
        ]

    def get_signal_strength(self, device_id: str) -> Optional[int]:
        """
        Get signal strength for a specific device.

        Args:
            device_id: Target device ID

        Returns:
            Signal strength in dBm (negative values), or None if unavailable
            Typical range: -30 (excellent) to -90 (poor)
        """
        if not self.service:
            return None

        for device in self.service.get_devices():
            if device.id == device_id:
                return getattr(device, "signal_strength", None)

        return None

    def get_signal_quality(self, device_id: str) -> Optional[str]:
        """
        Get human-readable signal quality for a device.

        Args:
            device_id: Target device ID

        Returns:
            Quality string: 'excellent', 'good', 'fair', 'poor', 'critical'
        """
        strength = self.get_signal_strength(device_id)
        if strength is None:
            return None

        if strength >= -50:
            return "excellent"
        elif strength >= -60:
            return "good"
        elif strength >= -70:
            return "fair"
        elif strength >= -80:
            return "poor"
        else:
            return "critical"

    def get_all_signal_strengths(self) -> Dict[str, Dict[str, Any]]:
        """
        Get signal strength monitoring data for all devices.

        Returns:
            Dictionary mapping device_id to signal info
        """
        if not self.service:
            return {}

        result = {}
        for device in self.service.get_devices():
            strength = getattr(device, "signal_strength", None)
            result[device.id] = {
                "name": device.name,
                "signal_dbm": strength,
                "quality": self._dbm_to_quality(strength) if strength else "unknown",
                "bars": self._dbm_to_bars(strength) if strength else 0,
                "status": (
                    device.status.value
                    if hasattr(device.status, "value")
                    else str(device.status)
                ),
            }
        return result

    def _dbm_to_quality(self, dbm: int) -> str:
        """Convert dBm to quality string."""
        if dbm >= -50:
            return "excellent"
        elif dbm >= -60:
            return "good"
        elif dbm >= -70:
            return "fair"
        elif dbm >= -80:
            return "poor"
        return "critical"

    def _dbm_to_bars(self, dbm: int) -> int:
        """Convert dBm to bar count (0-5)."""
        if dbm >= -50:
            return 5
        elif dbm >= -60:
            return 4
        elif dbm >= -70:
            return 3
        elif dbm >= -80:
            return 2
        elif dbm >= -90:
            return 1
        return 0

    def monitor_signal(
        self,
        device_id: str,
        duration: float = 10.0,
        interval: float = 1.0,
        callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Monitor signal strength over time.

        Args:
            device_id: Target device ID to monitor
            duration: Total monitoring duration in seconds
            interval: Sample interval in seconds
            callback: Optional callback(strength_dbm, quality) for each sample

        Returns:
            List of signal samples with timestamps
        """
        samples = []
        start_time = time.time()

        while time.time() - start_time < duration:
            strength = self.get_signal_strength(device_id)
            quality = self._dbm_to_quality(strength) if strength else "unknown"
            sample = {
                "timestamp": time.time(),
                "elapsed": time.time() - start_time,
                "signal_dbm": strength,
                "quality": quality,
                "bars": self._dbm_to_bars(strength) if strength else 0,
            }
            samples.append(sample)

            if callback and strength is not None:
                callback(strength, quality)

            time.sleep(interval)

        return samples

    def get_signal_stats(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics from signal samples.

        Args:
            samples: List of samples from monitor_signal()

        Returns:
            Statistics: min, max, avg, stability
        """
        strengths = [s["signal_dbm"] for s in samples if s["signal_dbm"] is not None]

        if not strengths:
            return {"error": "No valid samples"}

        avg_strength = sum(strengths) / len(strengths)
        variance = sum((s - avg_strength) ** 2 for s in strengths) / len(strengths)
        std_dev = variance**0.5

        return {
            "sample_count": len(strengths),
            "duration_seconds": samples[-1]["elapsed"] if samples else 0,
            "min_dbm": min(strengths),
            "max_dbm": max(strengths),
            "avg_dbm": round(avg_strength, 1),
            "std_dev": round(std_dev, 2),
            "stability": (
                "stable" if std_dev < 5 else "unstable" if std_dev < 10 else "volatile"
            ),
            "avg_quality": self._dbm_to_quality(int(avg_strength)),
            "avg_bars": self._dbm_to_bars(int(avg_strength)),
        }


# Container management functions
def get_container_status() -> Dict[str, Any]:
    """
    Get MeshCore code container status.

    Returns:
        Container status information
    """
    status = {
        "container": CONTAINER_INFO,
        "installed": CONTAINER_INSTALLED,
        "service_available": MESHCORE_AVAILABLE,
        "container_path": str(CONTAINER_PATH),
    }

    if CONTAINER_INSTALLED:
        # Check for git info
        git_dir = CONTAINER_PATH / ".git"
        if git_dir.exists():
            status["git_managed"] = True
            # Try to get current commit
            head_file = git_dir / "HEAD"
            if head_file.exists():
                status["git_head"] = head_file.read_text().strip()
        else:
            status["git_managed"] = False

        # Check for container manifest
        manifest_path = CONTAINER_PATH / "container.json"
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    status["manifest"] = json.load(f)
            except:
                pass

    return status


def check_container_update() -> Dict[str, Any]:
    """
    Check if container has updates available (Wizard Server only).

    Returns:
        Update status information
    """
    # This would be called by Wizard Server which has web access
    return {
        "check_available": False,
        "reason": "Update checks require Wizard Server (web access)",
        "instruction": "Use 'PLUGIN UPDATE meshcore' on Wizard Server",
    }


# Convenience function
def get_mesh_transport(device_id: Optional[str] = None) -> Optional[MeshTransport]:
    """
    Get MeshCore transport instance.

    Args:
        device_id: Optional device identifier

    Returns:
        MeshTransport instance or None if unavailable
    """
    try:
        return MeshTransport(device_id)
    except ImportError:
        return None


# Module exports
__all__ = [
    "MeshTransport",
    "MeshPacket",
    "PacketType",
    "get_mesh_transport",
    "get_container_status",
    "check_container_update",
    "MESHCORE_AVAILABLE",
    "CONTAINER_INSTALLED",
    "CONTAINER_INFO",
]
