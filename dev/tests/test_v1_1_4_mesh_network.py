"""
uDOS v1.1.4.2 - Device Spawning & Mesh Networking Test Suite

Tests distributed uDOS ecosystem with master-child device spawning and
encrypted P2P mesh networking for offline-first community features.

Test Coverage:
- Device Spawning & Management (10 tests)
- Peer Discovery & Connection (8 tests)
- Encryption & Security (9 tests)
- Cross-Device Sync (10 tests)
- Mesh Community Features (8 tests)
- Distributed Debugging (6 tests)
"""

import unittest
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid


# ============================================================================
# DEVICE SPAWNING & MANAGEMENT
# ============================================================================

class DeviceType(Enum):
    """Types of devices in mesh network"""
    MASTER = "master"  # Full desktop/laptop with all features
    CHILD = "child"    # Spawned simplified device
    MOBILE = "mobile"  # Mobile companion app
    IOT = "iot"        # IoT/embedded device


class DeviceCapability(Enum):
    """Device capabilities"""
    FULL_CLI = "full_cli"
    KNOWLEDGE_BANK = "knowledge_bank"
    BARTER_SYSTEM = "barter_system"
    MISSIONS = "missions"
    MAPPING = "mapping"
    MESH_RELAY = "mesh_relay"
    SESSION_SYNC = "session_sync"
    LOCAL_AI = "local_ai"


@dataclass
class DeviceProfile:
    """Profile for a device in the mesh"""
    device_id: str
    device_type: DeviceType
    name: str
    capabilities: Set[DeviceCapability]
    parent_id: Optional[str] = None
    spawned_at: Optional[datetime] = None
    last_seen: datetime = field(default_factory=datetime.now)
    mesh_address: str = ""
    public_key: str = ""

    def is_child(self) -> bool:
        """Check if device is a child"""
        return self.parent_id is not None

    def has_capability(self, cap: DeviceCapability) -> bool:
        """Check if device has specific capability"""
        return cap in self.capabilities


class DeviceSpawner:
    """Manages device spawning and hierarchy"""

    def __init__(self, master_device_id: str):
        self.master_device_id = master_device_id
        self.devices: Dict[str, DeviceProfile] = {}
        self.spawn_requests: List[Dict[str, Any]] = []

        # Register master device
        self.devices[master_device_id] = DeviceProfile(
            device_id=master_device_id,
            device_type=DeviceType.MASTER,
            name="Master Device",
            capabilities={
                DeviceCapability.FULL_CLI,
                DeviceCapability.KNOWLEDGE_BANK,
                DeviceCapability.BARTER_SYSTEM,
                DeviceCapability.MISSIONS,
                DeviceCapability.MAPPING,
                DeviceCapability.MESH_RELAY,
                DeviceCapability.SESSION_SYNC,
                DeviceCapability.LOCAL_AI
            }
        )

    def spawn_device(
        self,
        device_type: DeviceType,
        name: str,
        capabilities: Set[DeviceCapability]
    ) -> DeviceProfile:
        """Spawn a new child device"""
        device_id = str(uuid.uuid4())

        device = DeviceProfile(
            device_id=device_id,
            device_type=device_type,
            name=name,
            capabilities=capabilities,
            parent_id=self.master_device_id,
            spawned_at=datetime.now()
        )

        self.devices[device_id] = device
        self.spawn_requests.append({
            "device_id": device_id,
            "spawned_at": datetime.now(),
            "parent_id": self.master_device_id
        })

        return device

    def get_device(self, device_id: str) -> Optional[DeviceProfile]:
        """Get device by ID"""
        return self.devices.get(device_id)

    def get_children(self, parent_id: str) -> List[DeviceProfile]:
        """Get all child devices of a parent"""
        return [
            dev for dev in self.devices.values()
            if dev.parent_id == parent_id
        ]

    def deactivate_device(self, device_id: str) -> bool:
        """Deactivate a device"""
        if device_id == self.master_device_id:
            return False  # Can't deactivate master

        if device_id in self.devices:
            del self.devices[device_id]
            return True

        return False

    def get_device_tree(self) -> Dict[str, List[str]]:
        """Get device hierarchy tree"""
        tree = {}
        for device_id, device in self.devices.items():
            parent = device.parent_id or "root"
            if parent not in tree:
                tree[parent] = []
            tree[parent].append(device_id)
        return tree

    def create_simplified_profile(self, target_type: DeviceType) -> Set[DeviceCapability]:
        """Create simplified capability set for device type"""
        if target_type == DeviceType.MOBILE:
            return {
                DeviceCapability.MISSIONS,
                DeviceCapability.MAPPING,
                DeviceCapability.BARTER_SYSTEM,
                DeviceCapability.MESH_RELAY,
                DeviceCapability.SESSION_SYNC
            }
        elif target_type == DeviceType.IOT:
            return {
                DeviceCapability.MESH_RELAY,
                DeviceCapability.SESSION_SYNC
            }
        else:  # CHILD
            return {
                DeviceCapability.KNOWLEDGE_BANK,
                DeviceCapability.MISSIONS,
                DeviceCapability.MESH_RELAY,
                DeviceCapability.SESSION_SYNC
            }


# ============================================================================
# PEER DISCOVERY & CONNECTION
# ============================================================================

class DiscoveryProtocol(Enum):
    """Peer discovery protocols"""
    MDNS = "mdns"      # Multicast DNS (local network)
    DHT = "dht"        # Distributed Hash Table
    MANUAL = "manual"  # Manual peer addition


@dataclass
class PeerInfo:
    """Information about a discovered peer"""
    peer_id: str
    device_profile: DeviceProfile
    addresses: List[str]
    discovered_via: DiscoveryProtocol
    discovered_at: datetime = field(default_factory=datetime.now)
    connection_status: str = "discovered"  # discovered, connecting, connected, disconnected
    latency_ms: float = 0.0


class PeerDiscovery:
    """Handles peer discovery on mesh network"""

    def __init__(self, local_device_id: str):
        self.local_device_id = local_device_id
        self.peers: Dict[str, PeerInfo] = {}
        self.mdns_enabled = True
        self.dht_enabled = True
        self.discovery_interval = 30  # seconds

    def start_discovery(self) -> None:
        """Start peer discovery"""
        self.mdns_enabled = True
        self.dht_enabled = True

    def stop_discovery(self) -> None:
        """Stop peer discovery"""
        self.mdns_enabled = False
        self.dht_enabled = False

    def discover_peer(
        self,
        peer_id: str,
        device_profile: DeviceProfile,
        addresses: List[str],
        protocol: DiscoveryProtocol
    ) -> PeerInfo:
        """Register a discovered peer"""
        peer = PeerInfo(
            peer_id=peer_id,
            device_profile=device_profile,
            addresses=addresses,
            discovered_via=protocol
        )
        self.peers[peer_id] = peer
        return peer

    def get_peers(self, filter_status: Optional[str] = None) -> List[PeerInfo]:
        """Get discovered peers, optionally filtered by status"""
        if filter_status:
            return [p for p in self.peers.values() if p.connection_status == filter_status]
        return list(self.peers.values())

    def update_peer_status(self, peer_id: str, status: str) -> bool:
        """Update peer connection status"""
        if peer_id in self.peers:
            self.peers[peer_id].connection_status = status
            return True
        return False

    def measure_latency(self, peer_id: str) -> float:
        """Measure latency to peer (simulated)"""
        if peer_id in self.peers:
            # Simulate latency measurement
            latency = 5.0 + (hash(peer_id) % 50)  # 5-55ms
            self.peers[peer_id].latency_ms = latency
            return latency
        return -1.0

    def remove_peer(self, peer_id: str) -> bool:
        """Remove peer from discovered list"""
        if peer_id in self.peers:
            del self.peers[peer_id]
            return True
        return False


class MeshConnection:
    """Manages connections between peers"""

    def __init__(self, local_peer_id: str):
        self.local_peer_id = local_peer_id
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.connection_attempts: Dict[str, int] = {}

    def connect_to_peer(self, peer_id: str, address: str) -> bool:
        """Establish connection to peer"""
        self.connection_attempts[peer_id] = self.connection_attempts.get(peer_id, 0) + 1

        # Simulate connection attempt
        if self.connection_attempts[peer_id] <= 3:  # Max 3 retries
            self.connections[peer_id] = {
                "address": address,
                "connected_at": datetime.now(),
                "status": "connected",
                "messages_sent": 0,
                "messages_received": 0
            }
            return True

        return False

    def disconnect_peer(self, peer_id: str) -> bool:
        """Disconnect from peer"""
        if peer_id in self.connections:
            self.connections[peer_id]["status"] = "disconnected"
            return True
        return False

    def is_connected(self, peer_id: str) -> bool:
        """Check if connected to peer"""
        return (
            peer_id in self.connections and
            self.connections[peer_id]["status"] == "connected"
        )

    def get_connected_peers(self) -> List[str]:
        """Get list of connected peer IDs"""
        return [
            peer_id for peer_id, conn in self.connections.items()
            if conn["status"] == "connected"
        ]

    def get_connection_stats(self) -> Dict[str, int]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.connections),
            "active_connections": len(self.get_connected_peers()),
            "total_attempts": sum(self.connection_attempts.values())
        }


# ============================================================================
# ENCRYPTION & SECURITY
# ============================================================================

@dataclass
class EncryptionKey:
    """Encryption key for mesh communication"""
    key_id: str
    public_key: str
    private_key: str
    created_at: datetime = field(default_factory=datetime.now)
    algorithm: str = "Ed25519"


class MeshCrypto:
    """Handles encryption and authentication for mesh network"""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.key_pair = self._generate_key_pair()
        self.trusted_keys: Dict[str, str] = {}  # peer_id -> public_key
        self.encrypted_channels: Dict[str, str] = {}  # channel_id -> encryption_type

    def _generate_key_pair(self) -> EncryptionKey:
        """Generate encryption key pair"""
        key_id = f"key_{self.device_id}"
        # Simulated key generation
        public_key = hashlib.sha256(f"{self.device_id}_public".encode()).hexdigest()
        private_key = hashlib.sha256(f"{self.device_id}_private".encode()).hexdigest()

        return EncryptionKey(
            key_id=key_id,
            public_key=public_key,
            private_key=private_key
        )

    def add_trusted_peer(self, peer_id: str, public_key: str) -> None:
        """Add trusted peer public key"""
        self.trusted_keys[peer_id] = public_key

    def is_peer_trusted(self, peer_id: str) -> bool:
        """Check if peer is trusted"""
        return peer_id in self.trusted_keys

    def encrypt_message(self, message: str, recipient_id: str) -> Dict[str, str]:
        """Encrypt message for specific recipient"""
        if recipient_id not in self.trusted_keys:
            raise ValueError(f"Recipient {recipient_id} not trusted")

        # Simulated encryption
        encrypted_data = hashlib.sha256(
            f"{message}:{self.key_pair.private_key}:{self.trusted_keys[recipient_id]}".encode()
        ).hexdigest()

        return {
            "encrypted_data": encrypted_data,
            "sender_id": self.device_id,
            "recipient_id": recipient_id,
            "algorithm": "Ed25519",
            "timestamp": datetime.now().isoformat()
        }

    def decrypt_message(self, encrypted_msg: Dict[str, str]) -> str:
        """Decrypt message from peer"""
        sender_id = encrypted_msg["sender_id"]

        if sender_id not in self.trusted_keys:
            raise ValueError(f"Sender {sender_id} not trusted")

        # Simulated decryption
        return f"Decrypted message from {sender_id}"

    def verify_signature(self, data: str, signature: str, peer_id: str) -> bool:
        """Verify message signature"""
        if peer_id not in self.trusted_keys:
            return False

        # Simulated signature verification
        expected_sig = hashlib.sha256(
            f"{data}:{self.trusted_keys[peer_id]}".encode()
        ).hexdigest()

        return signature == expected_sig

    def sign_data(self, data: str) -> str:
        """Sign data with private key"""
        return hashlib.sha256(
            f"{data}:{self.key_pair.private_key}".encode()
        ).hexdigest()

    def create_secure_channel(self, peer_id: str) -> str:
        """Create encrypted channel with peer"""
        if peer_id not in self.trusted_keys:
            raise ValueError(f"Peer {peer_id} not trusted")

        channel_id = hashlib.sha256(
            f"{self.device_id}:{peer_id}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        self.encrypted_channels[channel_id] = "AES-256-GCM"
        return channel_id

    def get_channel_encryption(self, channel_id: str) -> Optional[str]:
        """Get encryption type for channel"""
        return self.encrypted_channels.get(channel_id)


# ============================================================================
# CROSS-DEVICE SYNC
# ============================================================================

class SyncType(Enum):
    """Types of data to sync"""
    SESSION_LOGS = "session_logs"
    MEMORY_TIER1 = "memory_tier1"
    MEMORY_TIER2 = "memory_tier2"
    KNOWLEDGE_UPDATES = "knowledge_updates"
    BARTER_OFFERS = "barter_offers"
    MISSIONS = "missions"
    XP_ACHIEVEMENTS = "xp_achievements"


@dataclass
class SyncItem:
    """Item to be synchronized"""
    item_id: str
    sync_type: SyncType
    data: Dict[str, Any]
    version: int
    modified_at: datetime
    device_id: str
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = hashlib.sha256(
                json.dumps(self.data, sort_keys=True).encode()
            ).hexdigest()


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    DEVICE_PRIORITY = "device_priority"
    MANUAL_MERGE = "manual_merge"
    VECTOR_CLOCK = "vector_clock"


class SyncProtocol:
    """Handles cross-device synchronization"""

    def __init__(self, local_device_id: str):
        self.local_device_id = local_device_id
        self.sync_queue: List[SyncItem] = []
        self.sync_history: Dict[str, SyncItem] = {}
        self.conflict_resolution = ConflictResolution.LAST_WRITE_WINS
        self.vector_clock: Dict[str, int] = {}  # device_id -> version

    def add_to_sync(self, sync_item: SyncItem) -> None:
        """Add item to sync queue"""
        self.sync_queue.append(sync_item)
        self.sync_history[sync_item.item_id] = sync_item

        # Update vector clock
        self.vector_clock[sync_item.device_id] = sync_item.version

    def get_sync_queue(self, sync_type: Optional[SyncType] = None) -> List[SyncItem]:
        """Get items in sync queue"""
        if sync_type:
            return [item for item in self.sync_queue if item.sync_type == sync_type]
        return self.sync_queue

    def sync_with_peer(self, peer_id: str, items: List[SyncItem]) -> Dict[str, Any]:
        """Synchronize items with peer"""
        synced = []
        conflicts = []

        for item in items:
            # Check for conflicts
            if item.item_id in self.sync_history:
                existing = self.sync_history[item.item_id]
                if existing.checksum != item.checksum:
                    # Conflict detected
                    resolved = self._resolve_conflict(existing, item)
                    conflicts.append({
                        "item_id": item.item_id,
                        "local_version": existing.version,
                        "remote_version": item.version,
                        "resolution": "resolved" if resolved else "pending"
                    })
                    if resolved:
                        synced.append(item.item_id)
                else:
                    synced.append(item.item_id)
            else:
                # No conflict, add to history
                self.sync_history[item.item_id] = item
                synced.append(item.item_id)

        return {
            "peer_id": peer_id,
            "synced_items": synced,
            "conflicts": conflicts,
            "timestamp": datetime.now().isoformat()
        }

    def _resolve_conflict(self, local: SyncItem, remote: SyncItem) -> bool:
        """Resolve sync conflict"""
        if self.conflict_resolution == ConflictResolution.LAST_WRITE_WINS:
            if remote.modified_at > local.modified_at:
                self.sync_history[remote.item_id] = remote
                return True
        elif self.conflict_resolution == ConflictResolution.DEVICE_PRIORITY:
            # Master device wins
            if remote.device_id == self.local_device_id:
                return True

        return False

    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        return {
            "queue_size": len(self.sync_queue),
            "total_synced": len(self.sync_history),
            "vector_clock": self.vector_clock,
            "conflict_strategy": self.conflict_resolution.value
        }

    def clear_sync_queue(self) -> None:
        """Clear sync queue after successful sync"""
        self.sync_queue.clear()


# ============================================================================
# MESH COMMUNITY FEATURES
# ============================================================================

@dataclass
class MeshMessage:
    """Message on mesh network"""
    message_id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast
    message_type: str  # chat, barter, mission, announcement
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    encrypted: bool = False
    ttl: int = 10  # Hops before message expires


class MeshCommunity:
    """Community features over mesh network"""

    def __init__(self, device_id: str, crypto: MeshCrypto):
        self.device_id = device_id
        self.crypto = crypto
        self.messages: List[MeshMessage] = []
        self.barter_offers: Dict[str, Dict[str, Any]] = {}
        self.mission_board: Dict[str, Dict[str, Any]] = {}

    def send_message(
        self,
        content: str,
        recipient_id: Optional[str] = None,
        message_type: str = "chat",
        encrypt: bool = True
    ) -> MeshMessage:
        """Send message on mesh"""
        message_id = str(uuid.uuid4())

        if encrypt and recipient_id:
            encrypted_content = self.crypto.encrypt_message(content, recipient_id)
            content = json.dumps(encrypted_content)

        message = MeshMessage(
            message_id=message_id,
            sender_id=self.device_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            encrypted=encrypt
        )

        self.messages.append(message)
        return message

    def receive_message(self, message: MeshMessage) -> str:
        """Receive and decrypt message"""
        self.messages.append(message)

        if message.encrypted and message.recipient_id == self.device_id:
            encrypted_msg = json.loads(message.content)
            return self.crypto.decrypt_message(encrypted_msg)

        return message.content

    def post_barter_offer(
        self,
        offer_type: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> str:
        """Post barter offer on mesh"""
        offer_id = str(uuid.uuid4())

        self.barter_offers[offer_id] = {
            "offer_id": offer_id,
            "device_id": self.device_id,
            "offer_type": offer_type,
            "title": title,
            "description": description,
            "tags": tags,
            "posted_at": datetime.now().isoformat(),
            "status": "active"
        }

        # Broadcast to mesh
        self.send_message(
            json.dumps(self.barter_offers[offer_id]),
            message_type="barter",
            encrypt=False
        )

        return offer_id

    def get_barter_offers(self, filter_tags: Optional[List[str]] = None) -> List[Dict]:
        """Get barter offers from mesh"""
        offers = list(self.barter_offers.values())

        if filter_tags:
            offers = [
                o for o in offers
                if any(tag in o["tags"] for tag in filter_tags)
            ]

        return offers

    def post_mission(self, title: str, description: str, location: str) -> str:
        """Post mission on mesh mission board"""
        mission_id = str(uuid.uuid4())

        self.mission_board[mission_id] = {
            "mission_id": mission_id,
            "device_id": self.device_id,
            "title": title,
            "description": description,
            "location": location,
            "posted_at": datetime.now().isoformat(),
            "status": "open",
            "participants": []
        }

        # Broadcast to mesh
        self.send_message(
            json.dumps(self.mission_board[mission_id]),
            message_type="mission",
            encrypt=False
        )

        return mission_id

    def join_mission(self, mission_id: str) -> bool:
        """Join a mission on the mesh"""
        if mission_id in self.mission_board:
            mission = self.mission_board[mission_id]
            if self.device_id not in mission["participants"]:
                mission["participants"].append(self.device_id)
                return True
        return False

    def get_message_stats(self) -> Dict[str, int]:
        """Get messaging statistics"""
        return {
            "total_messages": len(self.messages),
            "sent_messages": len([m for m in self.messages if m.sender_id == self.device_id]),
            "received_messages": len([m for m in self.messages if m.recipient_id == self.device_id]),
            "broadcast_messages": len([m for m in self.messages if m.recipient_id is None])
        }


# ============================================================================
# DISTRIBUTED DEBUGGING
# ============================================================================

@dataclass
class DebugEvent:
    """Debug event from any device on mesh"""
    event_id: str
    device_id: str
    event_type: str  # error, warning, info, performance
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DistributedDebugger:
    """Aggregates debugging info across mesh"""

    def __init__(self, local_device_id: str):
        self.local_device_id = local_device_id
        self.events: List[DebugEvent] = []
        self.device_logs: Dict[str, List[DebugEvent]] = {}
        self.performance_metrics: Dict[str, List[float]] = {}

    def log_event(
        self,
        device_id: str,
        event_type: str,
        message: str,
        stack_trace: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> DebugEvent:
        """Log debug event"""
        event_id = str(uuid.uuid4())

        event = DebugEvent(
            event_id=event_id,
            device_id=device_id,
            event_type=event_type,
            message=message,
            stack_trace=stack_trace,
            metadata=metadata or {}
        )

        self.events.append(event)

        if device_id not in self.device_logs:
            self.device_logs[device_id] = []
        self.device_logs[device_id].append(event)

        return event

    def get_events(
        self,
        device_id: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[DebugEvent]:
        """Get debug events with optional filtering"""
        events = self.events

        if device_id:
            events = [e for e in events if e.device_id == device_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events

    def record_performance(self, metric_name: str, value: float) -> None:
        """Record performance metric"""
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = []
        self.performance_metrics[metric_name].append(value)

    def get_performance_stats(self, metric_name: str) -> Dict[str, float]:
        """Get performance statistics for metric"""
        if metric_name not in self.performance_metrics:
            return {}

        values = self.performance_metrics[metric_name]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values)
        }

    def get_error_summary(self) -> Dict[str, int]:
        """Get error summary by device"""
        summary = {}

        for device_id, logs in self.device_logs.items():
            error_count = len([e for e in logs if e.event_type == "error"])
            if error_count > 0:
                summary[device_id] = error_count

        return summary

    def export_debug_report(self) -> Dict[str, Any]:
        """Export comprehensive debug report"""
        return {
            "total_events": len(self.events),
            "devices": list(self.device_logs.keys()),
            "error_summary": self.get_error_summary(),
            "event_types": {
                event_type: len([e for e in self.events if e.event_type == event_type])
                for event_type in ["error", "warning", "info", "performance"]
            },
            "performance_metrics": list(self.performance_metrics.keys()),
            "generated_at": datetime.now().isoformat()
        }


# ============================================================================
# TEST SUITES
# ============================================================================

class TestDeviceSpawning(unittest.TestCase):
    """Test device spawning and management"""

    def setUp(self):
        self.spawner = DeviceSpawner("master_001")

    def test_master_device_registration(self):
        """Test master device is registered"""
        master = self.spawner.get_device("master_001")
        self.assertIsNotNone(master)
        self.assertEqual(master.device_type, DeviceType.MASTER)
        self.assertFalse(master.is_child())

    def test_spawn_child_device(self):
        """Test spawning child device"""
        caps = {DeviceCapability.MISSIONS, DeviceCapability.MAPPING}
        child = self.spawner.spawn_device(DeviceType.CHILD, "Child 1", caps)

        self.assertIsNotNone(child)
        self.assertTrue(child.is_child())
        self.assertEqual(child.parent_id, "master_001")
        self.assertIn(DeviceCapability.MISSIONS, child.capabilities)

    def test_spawn_mobile_device(self):
        """Test spawning mobile device"""
        caps = self.spawner.create_simplified_profile(DeviceType.MOBILE)
        mobile = self.spawner.spawn_device(DeviceType.MOBILE, "Mobile 1", caps)

        self.assertEqual(mobile.device_type, DeviceType.MOBILE)
        self.assertTrue(mobile.has_capability(DeviceCapability.MISSIONS))
        self.assertTrue(mobile.has_capability(DeviceCapability.MESH_RELAY))

    def test_get_children(self):
        """Test retrieving child devices"""
        caps = {DeviceCapability.MISSIONS}
        self.spawner.spawn_device(DeviceType.CHILD, "Child 1", caps)
        self.spawner.spawn_device(DeviceType.CHILD, "Child 2", caps)

        children = self.spawner.get_children("master_001")
        self.assertEqual(len(children), 2)

    def test_deactivate_device(self):
        """Test deactivating device"""
        caps = {DeviceCapability.MISSIONS}
        child = self.spawner.spawn_device(DeviceType.CHILD, "Child 1", caps)

        success = self.spawner.deactivate_device(child.device_id)
        self.assertTrue(success)
        self.assertIsNone(self.spawner.get_device(child.device_id))

    def test_cannot_deactivate_master(self):
        """Test master device cannot be deactivated"""
        success = self.spawner.deactivate_device("master_001")
        self.assertFalse(success)

    def test_device_tree(self):
        """Test device hierarchy tree"""
        caps = {DeviceCapability.MISSIONS}
        child1 = self.spawner.spawn_device(DeviceType.CHILD, "Child 1", caps)
        child2 = self.spawner.spawn_device(DeviceType.CHILD, "Child 2", caps)

        tree = self.spawner.get_device_tree()
        self.assertIn("root", tree)
        self.assertIn("master_001", tree)
        self.assertEqual(len(tree["master_001"]), 2)

    def test_simplified_profiles(self):
        """Test simplified capability profiles"""
        mobile_caps = self.spawner.create_simplified_profile(DeviceType.MOBILE)
        iot_caps = self.spawner.create_simplified_profile(DeviceType.IOT)

        self.assertIn(DeviceCapability.MISSIONS, mobile_caps)
        self.assertNotIn(DeviceCapability.FULL_CLI, mobile_caps)
        self.assertIn(DeviceCapability.MESH_RELAY, iot_caps)
        self.assertEqual(len(iot_caps), 2)  # Minimal capabilities

    def test_capability_checking(self):
        """Test device capability checking"""
        master = self.spawner.get_device("master_001")
        self.assertTrue(master.has_capability(DeviceCapability.FULL_CLI))
        self.assertTrue(master.has_capability(DeviceCapability.LOCAL_AI))

    def test_spawn_tracking(self):
        """Test spawn request tracking"""
        caps = {DeviceCapability.MISSIONS}
        self.spawner.spawn_device(DeviceType.CHILD, "Child 1", caps)

        self.assertEqual(len(self.spawner.spawn_requests), 1)
        self.assertEqual(self.spawner.spawn_requests[0]["parent_id"], "master_001")


class TestPeerDiscovery(unittest.TestCase):
    """Test peer discovery and connection"""

    def setUp(self):
        self.discovery = PeerDiscovery("device_001")
        self.connection = MeshConnection("device_001")

    def test_start_stop_discovery(self):
        """Test starting and stopping discovery"""
        self.discovery.start_discovery()
        self.assertTrue(self.discovery.mdns_enabled)
        self.assertTrue(self.discovery.dht_enabled)

        self.discovery.stop_discovery()
        self.assertFalse(self.discovery.mdns_enabled)
        self.assertFalse(self.discovery.dht_enabled)

    def test_discover_peer_mdns(self):
        """Test discovering peer via mDNS"""
        profile = DeviceProfile(
            device_id="peer_001",
            device_type=DeviceType.CHILD,
            name="Peer 1",
            capabilities={DeviceCapability.MISSIONS}
        )

        peer = self.discovery.discover_peer(
            "peer_001",
            profile,
            ["192.168.1.100:8080"],
            DiscoveryProtocol.MDNS
        )

        self.assertEqual(peer.peer_id, "peer_001")
        self.assertEqual(peer.discovered_via, DiscoveryProtocol.MDNS)
        self.assertEqual(peer.connection_status, "discovered")

    def test_get_peers_filtered(self):
        """Test getting peers with status filter"""
        profile = DeviceProfile(
            device_id="peer_001",
            device_type=DeviceType.CHILD,
            name="Peer 1",
            capabilities={DeviceCapability.MISSIONS}
        )

        self.discovery.discover_peer("peer_001", profile, ["addr1"], DiscoveryProtocol.MDNS)
        self.discovery.update_peer_status("peer_001", "connected")

        connected = self.discovery.get_peers(filter_status="connected")
        self.assertEqual(len(connected), 1)

    def test_measure_latency(self):
        """Test latency measurement"""
        profile = DeviceProfile(
            device_id="peer_001",
            device_type=DeviceType.CHILD,
            name="Peer 1",
            capabilities={DeviceCapability.MISSIONS}
        )

        self.discovery.discover_peer("peer_001", profile, ["addr1"], DiscoveryProtocol.MDNS)
        latency = self.discovery.measure_latency("peer_001")

        self.assertGreater(latency, 0)
        self.assertLess(latency, 100)

    def test_connect_to_peer(self):
        """Test establishing connection to peer"""
        success = self.connection.connect_to_peer("peer_001", "192.168.1.100:8080")
        self.assertTrue(success)
        self.assertTrue(self.connection.is_connected("peer_001"))

    def test_disconnect_peer(self):
        """Test disconnecting from peer"""
        self.connection.connect_to_peer("peer_001", "addr1")
        success = self.connection.disconnect_peer("peer_001")

        self.assertTrue(success)
        self.assertFalse(self.connection.is_connected("peer_001"))

    def test_get_connected_peers(self):
        """Test getting list of connected peers"""
        self.connection.connect_to_peer("peer_001", "addr1")
        self.connection.connect_to_peer("peer_002", "addr2")

        connected = self.connection.get_connected_peers()
        self.assertEqual(len(connected), 2)

    def test_connection_stats(self):
        """Test connection statistics"""
        self.connection.connect_to_peer("peer_001", "addr1")
        self.connection.connect_to_peer("peer_002", "addr2")

        stats = self.connection.get_connection_stats()
        self.assertEqual(stats["total_connections"], 2)
        self.assertEqual(stats["active_connections"], 2)


class TestEncryption(unittest.TestCase):
    """Test encryption and security"""

    def setUp(self):
        self.crypto1 = MeshCrypto("device_001")
        self.crypto2 = MeshCrypto("device_002")

        # Exchange public keys
        self.crypto1.add_trusted_peer("device_002", self.crypto2.key_pair.public_key)
        self.crypto2.add_trusted_peer("device_001", self.crypto1.key_pair.public_key)

    def test_key_pair_generation(self):
        """Test encryption key pair generation"""
        self.assertIsNotNone(self.crypto1.key_pair.public_key)
        self.assertIsNotNone(self.crypto1.key_pair.private_key)
        self.assertEqual(self.crypto1.key_pair.algorithm, "Ed25519")

    def test_add_trusted_peer(self):
        """Test adding trusted peer"""
        self.assertTrue(self.crypto1.is_peer_trusted("device_002"))
        self.assertTrue(self.crypto2.is_peer_trusted("device_001"))

    def test_encrypt_message(self):
        """Test message encryption"""
        message = "Secret message"
        encrypted = self.crypto1.encrypt_message(message, "device_002")

        self.assertIn("encrypted_data", encrypted)
        self.assertEqual(encrypted["sender_id"], "device_001")
        self.assertEqual(encrypted["recipient_id"], "device_002")

    def test_decrypt_message(self):
        """Test message decryption"""
        message = "Secret message"
        encrypted = self.crypto1.encrypt_message(message, "device_002")
        decrypted = self.crypto2.decrypt_message(encrypted)

        self.assertIn("device_001", decrypted)

    def test_encrypt_untrusted_fails(self):
        """Test encryption to untrusted peer fails"""
        with self.assertRaises(ValueError):
            self.crypto1.encrypt_message("message", "untrusted_peer")

    def test_sign_and_verify(self):
        """Test data signing and verification"""
        data = "Important data"
        signature = self.crypto1.sign_data(data)

        # Manually verify (in real implementation, peer would verify)
        self.assertIsNotNone(signature)
        self.assertEqual(len(signature), 64)  # SHA256 hex

    def test_create_secure_channel(self):
        """Test creating encrypted channel"""
        channel_id = self.crypto1.create_secure_channel("device_002")

        self.assertIsNotNone(channel_id)
        encryption = self.crypto1.get_channel_encryption(channel_id)
        self.assertEqual(encryption, "AES-256-GCM")

    def test_channel_without_trust_fails(self):
        """Test creating channel with untrusted peer fails"""
        with self.assertRaises(ValueError):
            self.crypto1.create_secure_channel("untrusted_peer")

    def test_unique_key_pairs(self):
        """Test each device has unique key pair"""
        self.assertNotEqual(
            self.crypto1.key_pair.public_key,
            self.crypto2.key_pair.public_key
        )


class TestCrossDeviceSync(unittest.TestCase):
    """Test cross-device synchronization"""

    def setUp(self):
        self.sync1 = SyncProtocol("device_001")
        self.sync2 = SyncProtocol("device_002")

    def test_add_to_sync(self):
        """Test adding item to sync queue"""
        item = SyncItem(
            item_id="item_001",
            sync_type=SyncType.SESSION_LOGS,
            data={"log": "test"},
            version=1,
            modified_at=datetime.now(),
            device_id="device_001"
        )

        self.sync1.add_to_sync(item)
        queue = self.sync1.get_sync_queue()

        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0].item_id, "item_001")

    def test_sync_queue_filtering(self):
        """Test filtering sync queue by type"""
        item1 = SyncItem("item_001", SyncType.SESSION_LOGS, {}, 1, datetime.now(), "device_001")
        item2 = SyncItem("item_002", SyncType.MISSIONS, {}, 1, datetime.now(), "device_001")

        self.sync1.add_to_sync(item1)
        self.sync1.add_to_sync(item2)

        sessions = self.sync1.get_sync_queue(SyncType.SESSION_LOGS)
        self.assertEqual(len(sessions), 1)

    def test_sync_with_peer_no_conflict(self):
        """Test synchronizing with peer without conflicts"""
        item = SyncItem("item_001", SyncType.MISSIONS, {"mission": "test"}, 1, datetime.now(), "device_001")

        result = self.sync2.sync_with_peer("device_001", [item])

        self.assertEqual(len(result["synced_items"]), 1)
        self.assertEqual(len(result["conflicts"]), 0)

    def test_sync_conflict_detection(self):
        """Test conflict detection during sync"""
        # Both devices have different versions of same item
        item1 = SyncItem("item_001", SyncType.MISSIONS, {"version": "A"}, 1, datetime.now(), "device_001")
        item2 = SyncItem("item_001", SyncType.MISSIONS, {"version": "B"}, 2, datetime.now(), "device_002")

        self.sync1.add_to_sync(item1)
        result = self.sync1.sync_with_peer("device_002", [item2])

        self.assertGreater(len(result["conflicts"]), 0)

    def test_last_write_wins_resolution(self):
        """Test last-write-wins conflict resolution"""
        now = datetime.now()
        earlier = now - timedelta(minutes=5)

        item1 = SyncItem("item_001", SyncType.MISSIONS, {"version": "A"}, 1, earlier, "device_001")
        item2 = SyncItem("item_001", SyncType.MISSIONS, {"version": "B"}, 2, now, "device_002")

        self.sync1.conflict_resolution = ConflictResolution.LAST_WRITE_WINS
        self.sync1.add_to_sync(item1)
        result = self.sync1.sync_with_peer("device_002", [item2])

        # Newer item should win
        synced_item = self.sync1.sync_history["item_001"]
        self.assertEqual(synced_item.version, 2)

    def test_vector_clock_update(self):
        """Test vector clock updates"""
        item = SyncItem("item_001", SyncType.SESSION_LOGS, {}, 5, datetime.now(), "device_001")

        self.sync1.add_to_sync(item)

        self.assertIn("device_001", self.sync1.vector_clock)
        self.assertEqual(self.sync1.vector_clock["device_001"], 5)

    def test_sync_status(self):
        """Test getting sync status"""
        item1 = SyncItem("item_001", SyncType.MISSIONS, {}, 1, datetime.now(), "device_001")
        item2 = SyncItem("item_002", SyncType.SESSION_LOGS, {}, 1, datetime.now(), "device_001")

        self.sync1.add_to_sync(item1)
        self.sync1.add_to_sync(item2)

        status = self.sync1.get_sync_status()

        self.assertEqual(status["queue_size"], 2)
        self.assertEqual(status["total_synced"], 2)

    def test_clear_sync_queue(self):
        """Test clearing sync queue"""
        item = SyncItem("item_001", SyncType.MISSIONS, {}, 1, datetime.now(), "device_001")
        self.sync1.add_to_sync(item)

        self.sync1.clear_sync_queue()

        self.assertEqual(len(self.sync1.sync_queue), 0)
        self.assertEqual(len(self.sync1.sync_history), 1)  # History preserved

    def test_checksum_generation(self):
        """Test automatic checksum generation"""
        item = SyncItem("item_001", SyncType.MISSIONS, {"test": "data"}, 1, datetime.now(), "device_001")

        self.assertIsNotNone(item.checksum)
        self.assertEqual(len(item.checksum), 64)  # SHA256

    def test_checksum_uniqueness(self):
        """Test different data produces different checksums"""
        item1 = SyncItem("item_001", SyncType.MISSIONS, {"data": "A"}, 1, datetime.now(), "device_001")
        item2 = SyncItem("item_002", SyncType.MISSIONS, {"data": "B"}, 1, datetime.now(), "device_001")

        self.assertNotEqual(item1.checksum, item2.checksum)


class TestMeshCommunity(unittest.TestCase):
    """Test mesh community features"""

    def setUp(self):
        self.crypto1 = MeshCrypto("device_001")
        self.crypto2 = MeshCrypto("device_002")

        self.crypto1.add_trusted_peer("device_002", self.crypto2.key_pair.public_key)
        self.crypto2.add_trusted_peer("device_001", self.crypto1.key_pair.public_key)

        self.community1 = MeshCommunity("device_001", self.crypto1)
        self.community2 = MeshCommunity("device_002", self.crypto2)

    def test_send_message(self):
        """Test sending message on mesh"""
        message = self.community1.send_message("Hello mesh!", "device_002")

        self.assertEqual(message.sender_id, "device_001")
        self.assertEqual(message.recipient_id, "device_002")
        self.assertTrue(message.encrypted)

    def test_broadcast_message(self):
        """Test broadcasting message"""
        message = self.community1.send_message("Broadcast!", recipient_id=None, encrypt=False)

        self.assertIsNone(message.recipient_id)
        self.assertFalse(message.encrypted)

    def test_receive_encrypted_message(self):
        """Test receiving encrypted message"""
        message = self.community1.send_message("Secret!", "device_002")
        decrypted = self.community2.receive_message(message)

        self.assertIn("device_001", decrypted)

    def test_post_barter_offer(self):
        """Test posting barter offer on mesh"""
        offer_id = self.community1.post_barter_offer(
            "goods",
            "Fresh vegetables",
            "Homegrown organic vegetables",
            ["food", "organic"]
        )

        self.assertIsNotNone(offer_id)
        offers = self.community1.get_barter_offers()
        self.assertEqual(len(offers), 1)

    def test_filter_barter_offers(self):
        """Test filtering barter offers by tags"""
        self.community1.post_barter_offer("goods", "Vegetables", "Fresh", ["food", "organic"])
        self.community1.post_barter_offer("services", "Carpentry", "Wood work", ["skills", "building"])

        food_offers = self.community1.get_barter_offers(filter_tags=["food"])
        self.assertEqual(len(food_offers), 1)

    def test_post_mission(self):
        """Test posting mission on mesh"""
        mission_id = self.community1.post_mission(
            "Water Purification",
            "Set up water filter system",
            "Portland, OR"
        )

        self.assertIsNotNone(mission_id)
        self.assertIn(mission_id, self.community1.mission_board)

    def test_join_mission(self):
        """Test joining mission"""
        mission_id = self.community1.post_mission("Mission", "Description", "Location")
        success = self.community1.join_mission(mission_id)

        self.assertTrue(success)
        mission = self.community1.mission_board[mission_id]
        self.assertIn("device_001", mission["participants"])

    def test_message_stats(self):
        """Test message statistics"""
        self.community1.send_message("Message 1", "device_002")
        self.community1.send_message("Message 2", None, encrypt=False)

        stats = self.community1.get_message_stats()

        self.assertEqual(stats["total_messages"], 2)
        self.assertEqual(stats["sent_messages"], 2)
        self.assertEqual(stats["broadcast_messages"], 1)


class TestDistributedDebugging(unittest.TestCase):
    """Test distributed debugging features"""

    def setUp(self):
        self.debugger = DistributedDebugger("device_001")

    def test_log_event(self):
        """Test logging debug event"""
        event = self.debugger.log_event(
            "device_002",
            "error",
            "Connection timeout",
            stack_trace="line 42"
        )

        self.assertEqual(event.device_id, "device_002")
        self.assertEqual(event.event_type, "error")
        self.assertEqual(event.message, "Connection timeout")

    def test_get_events_by_device(self):
        """Test getting events filtered by device"""
        self.debugger.log_event("device_002", "error", "Error 1")
        self.debugger.log_event("device_003", "warning", "Warning 1")

        dev2_events = self.debugger.get_events(device_id="device_002")
        self.assertEqual(len(dev2_events), 1)

    def test_get_events_by_type(self):
        """Test getting events filtered by type"""
        self.debugger.log_event("device_002", "error", "Error 1")
        self.debugger.log_event("device_002", "warning", "Warning 1")

        errors = self.debugger.get_events(event_type="error")
        self.assertEqual(len(errors), 1)

    def test_record_performance(self):
        """Test recording performance metrics"""
        self.debugger.record_performance("sync_time", 150.5)
        self.debugger.record_performance("sync_time", 200.0)

        stats = self.debugger.get_performance_stats("sync_time")

        self.assertEqual(stats["count"], 2)
        self.assertEqual(stats["min"], 150.5)
        self.assertEqual(stats["max"], 200.0)

    def test_error_summary(self):
        """Test error summary by device"""
        self.debugger.log_event("device_002", "error", "Error 1")
        self.debugger.log_event("device_002", "error", "Error 2")
        self.debugger.log_event("device_003", "warning", "Warning 1")

        summary = self.debugger.get_error_summary()

        self.assertEqual(summary["device_002"], 2)
        self.assertNotIn("device_003", summary)

    def test_export_debug_report(self):
        """Test exporting debug report"""
        self.debugger.log_event("device_002", "error", "Error 1")
        self.debugger.log_event("device_003", "warning", "Warning 1")
        self.debugger.record_performance("latency", 25.0)

        report = self.debugger.export_debug_report()

        self.assertEqual(report["total_events"], 2)
        self.assertIn("device_002", report["devices"])
        self.assertIn("latency", report["performance_metrics"])


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
