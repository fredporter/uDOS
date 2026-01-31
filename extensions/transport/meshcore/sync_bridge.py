"""
Mesh Sync Transport Bridge
==========================

Bridges the Wizard Server's MeshSyncService with the MeshCore transport layer.

Handles:
- Sync packet formatting
- Transport selection (MeshCore, Bluetooth, QR, NFC)
- Sync request/response handling
- Delta compression

Protocol:
1. SYNC_REQUEST: Device requests sync from Wizard
2. SYNC_DELTA: Wizard sends changes (delta) to device
3. SYNC_PUSH: Device pushes local changes to Wizard
4. SYNC_ACK: Acknowledgment with new version

Version: v1.0.0.0
Date: 2026-01-06
"""

import json
import zlib
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from core.services.logging_service import get_logger

logger = get_logger("mesh-sync-transport")

# Try to import transport modules
try:
    from extensions.transport.meshcore import MeshTransport, MeshPacket, PacketType

    MESHCORE_AVAILABLE = True
except ImportError:
    MESHCORE_AVAILABLE = False
    MeshTransport = None


class SyncPacketType(Enum):
    """Sync-specific packet types."""

    SYNC_REQUEST = "sync_request"  # Request sync from Wizard
    SYNC_DELTA = "sync_delta"  # Delta response from Wizard
    SYNC_PUSH = "sync_push"  # Push changes to Wizard
    SYNC_ACK = "sync_ack"  # Sync acknowledgment
    SYNC_CONFLICT = "sync_conflict"  # Conflict notification


@dataclass
class SyncRequest:
    """Sync request from device."""

    device_id: str
    device_version: int
    item_types: List[str]  # Types to sync
    transport: str = "meshcore"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_bytes(self) -> bytes:
        return json.dumps(self.to_dict()).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> "SyncRequest":
        return cls(**json.loads(data.decode()))


@dataclass
class SyncResponse:
    """Sync response to device."""

    from_version: int
    to_version: int
    items: List[Dict[str, Any]]
    deleted_ids: List[str]
    compressed: bool = False

    def to_bytes(self, compress: bool = True) -> bytes:
        data = json.dumps(asdict(self)).encode()

        if compress and len(data) > 1024:
            compressed = zlib.compress(data)
            if len(compressed) < len(data):
                return b"\x01" + compressed  # Prefix indicates compression

        return b"\x00" + data  # Prefix indicates uncompressed

    @classmethod
    def from_bytes(cls, data: bytes) -> "SyncResponse":
        if data[0] == 1:  # Compressed
            data = zlib.decompress(data[1:])
        else:
            data = data[1:]

        d = json.loads(data.decode())
        return cls(**d)


class MeshSyncTransport:
    """
    Transport bridge for mesh synchronization.

    Handles the transport-layer aspects of sync:
    - Packet formatting
    - Compression
    - Transport selection
    - Retries and acknowledgments
    """

    def __init__(self):
        self._handlers: Dict[SyncPacketType, Callable] = {}
        self._pending_syncs: Dict[str, SyncRequest] = {}

        # Transport layer reference
        self._mesh_transport: Optional[MeshTransport] = None

        if MESHCORE_AVAILABLE:
            self._mesh_transport = MeshTransport()
            self._register_handlers()

        logger.info("[MESH] SyncTransport initialized")

    def _register_handlers(self):
        """Register packet handlers with transport layer."""
        if self._mesh_transport:
            # Register for sync packets
            self._mesh_transport.register_handler(
                PacketType.DATA, self._handle_sync_packet
            )

    # =========================================================================
    # Outbound Sync (Wizard → Device)
    # =========================================================================

    async def send_delta(
        self,
        device_id: str,
        delta: Any,  # SyncDelta from wizard.services.mesh_sync
        transport: str = "meshcore",
    ) -> bool:
        """
        Send sync delta to a device.

        Args:
            device_id: Target device
            delta: Changes to send
            transport: Transport to use

        Returns:
            True if sent successfully
        """
        response = SyncResponse(
            from_version=delta.from_version,
            to_version=delta.to_version,
            items=[i.to_dict() for i in delta.items],
            deleted_ids=delta.deleted_ids,
        )

        payload = response.to_bytes(compress=True)

        if transport == "meshcore" and self._mesh_transport:
            packet = MeshPacket(
                packet_id=f"sync-{datetime.now().timestamp()}",
                packet_type=PacketType.DATA,
                source_id="wizard",
                target_id=device_id,
                payload=payload,
                metadata={"sync_type": SyncPacketType.SYNC_DELTA.value},
            )

            await self._mesh_transport.send(packet)
            logger.info(f"[MESH] Sent delta to {device_id}: {len(delta.items)} items")
            return True

        # Fallback: store for polling
        self._pending_syncs[device_id] = response
        return True

    async def broadcast_update(self, item_id: str, item_type: str):
        """
        Broadcast a content update notification to all devices.

        Devices will request full sync if needed.
        """
        if self._mesh_transport:
            payload = json.dumps(
                {
                    "type": "update_notification",
                    "item_id": item_id,
                    "item_type": item_type,
                    "timestamp": datetime.now().isoformat(),
                }
            ).encode()

            packet = MeshPacket(
                packet_id=f"notify-{datetime.now().timestamp()}",
                packet_type=PacketType.BROADCAST,
                source_id="wizard",
                target_id="*",
                payload=payload,
                metadata={"sync_type": "notification"},
            )

            await self._mesh_transport.broadcast(packet)
            logger.debug(f"[MESH] Broadcast update: {item_id}")

    # =========================================================================
    # Inbound Sync (Device → Wizard)
    # =========================================================================

    async def _handle_sync_packet(self, packet: "MeshPacket"):
        """Handle incoming sync packet from device."""
        sync_type = packet.metadata.get("sync_type")

        if sync_type == SyncPacketType.SYNC_REQUEST.value:
            await self._handle_sync_request(packet)
        elif sync_type == SyncPacketType.SYNC_PUSH.value:
            await self._handle_sync_push(packet)
        elif sync_type == SyncPacketType.SYNC_ACK.value:
            await self._handle_sync_ack(packet)

    async def _handle_sync_request(self, packet: "MeshPacket"):
        """Handle sync request from device."""
        request = SyncRequest.from_bytes(packet.payload)

        logger.info(
            f"[MESH] Sync request from {request.device_id} at version {request.device_version}"
        )

        # Get mesh sync service
        from wizard.services.mesh_sync import get_mesh_sync, SyncItemType

        sync = get_mesh_sync()

        # Calculate delta
        item_types = (
            [SyncItemType(t) for t in request.item_types]
            if request.item_types
            else None
        )
        delta = sync.get_delta(request.device_version, item_types)

        # Send response
        await self.send_delta(request.device_id, delta, request.transport)

    async def _handle_sync_push(self, packet: "MeshPacket"):
        """Handle sync push from device."""
        data = json.loads(packet.payload.decode())
        device_id = data.get("device_id")
        items = data.get("items", [])

        logger.info(f"[MESH] Sync push from {device_id}: {len(items)} items")

        # Apply to mesh sync service
        from wizard.services.mesh_sync import get_mesh_sync
        from wizard.services.device_auth import get_device_auth

        sync = get_mesh_sync()
        auth = get_device_auth()

        new_version = sync.apply_from_device(device_id, items)
        auth.update_device_sync(device_id, new_version)

        # Send acknowledgment
        if self._mesh_transport:
            ack_payload = json.dumps(
                {"status": "success", "new_version": new_version, "applied": len(items)}
            ).encode()

            ack_packet = MeshPacket(
                packet_id=f"ack-{datetime.now().timestamp()}",
                packet_type=PacketType.ACK,
                source_id="wizard",
                target_id=device_id,
                payload=ack_payload,
                metadata={"sync_type": SyncPacketType.SYNC_ACK.value},
            )

            await self._mesh_transport.send(ack_packet)

    async def _handle_sync_ack(self, packet: "MeshPacket"):
        """Handle sync acknowledgment from device."""
        data = json.loads(packet.payload.decode())
        device_id = packet.source_id

        logger.info(
            f"[MESH] Sync ack from {device_id}: version {data.get('new_version')}"
        )

        # Update device sync version
        from wizard.services.device_auth import get_device_auth

        auth = get_device_auth()
        auth.update_device_sync(device_id, data.get("new_version", 0))

    # =========================================================================
    # Polling Interface (for devices without real-time transport)
    # =========================================================================

    def get_pending_sync(self, device_id: str) -> Optional[SyncResponse]:
        """Get pending sync data for device (polling mode)."""
        return self._pending_syncs.pop(device_id, None)


# Singleton
_sync_transport: Optional[MeshSyncTransport] = None


def get_sync_transport() -> MeshSyncTransport:
    """Get mesh sync transport instance."""
    global _sync_transport
    if _sync_transport is None:
        _sync_transport = MeshSyncTransport()
    return _sync_transport
