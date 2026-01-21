#!/usr/bin/env python3
"""
MeshCore Service - Core mesh networking service for offline-first P2P communication

Provides device discovery, peer-to-peer messaging, network topology management,
and signal strength monitoring. Works entirely offline without internet.

Architecture:
- Device Discovery: Local broadcast scanning for nearby nodes
- P2P Messaging: Direct device-to-device communication
- Topology Management: Network graph, routes, and connections
- Signal Monitoring: RSSI tracking and quality metrics

Layer Integration:
- 600-609: MeshCore network layer (devices, routes)
- 610-619: Signal heatmaps (coverage)
- 620-629: Network routes (paths)
- 650-659: Device status overlays

Version: v1.3.0
Author: Fred Porter
Date: December 24, 2025
"""

import json
import time
import threading
import queue
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .device_registry import (
    DeviceRegistry,
    Device,
    DeviceType,
    DeviceStatus,
    get_device_registry,
)
from .meshcore_protocol import (
    MeshMessage,
    MessageType,
    RoutingTable,
    create_message,
    parse_message,
)


class ConnectionState(Enum):
    """Network connection state machine."""

    OFFLINE = "offline"  # No network activity
    SCANNING = "scanning"  # Discovering devices
    MESH_ONLY = "mesh_only"  # Local mesh active, no cloud
    LOCAL_WEB = "local_web"  # Mesh + local web server
    CLOUD_CONNECTED = "cloud"  # Full connectivity


class NetworkEvent(Enum):
    """Network events for callbacks."""

    DEVICE_DISCOVERED = "device_discovered"
    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    ROUTE_UPDATED = "route_updated"
    SIGNAL_CHANGED = "signal_changed"
    STATE_CHANGED = "state_changed"


@dataclass
class NetworkStats:
    """Network statistics."""

    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    devices_discovered: int = 0
    routes_computed: int = 0
    avg_latency_ms: float = 0.0
    uptime_seconds: float = 0.0
    last_scan_time: float = 0.0


class MeshCoreService:
    """
    Core mesh networking service.

    Manages device discovery, messaging, and network topology
    for offline-first P2P communication.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize mesh service.

        Args:
            data_dir: Directory for network data storage
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "meshcore"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Core components
        self.device_registry = DeviceRegistry(data_dir)
        self.routing_table = RoutingTable()

        # State
        self.state = ConnectionState.OFFLINE
        self.local_device_id: Optional[str] = None
        self._running = False
        self._start_time = 0.0

        # Statistics
        self.stats = NetworkStats()

        # Message queues
        self._outbound_queue: queue.Queue = queue.Queue()
        self._inbound_queue: queue.Queue = queue.Queue()

        # Event callbacks
        self._event_callbacks: Dict[NetworkEvent, List[Callable]] = {
            event: [] for event in NetworkEvent
        }

        # Threading
        self._scan_thread: Optional[threading.Thread] = None
        self._message_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Load saved state
        self._load_state()

    def _load_state(self) -> None:
        """Load saved network state."""
        state_file = self.data_dir / "network_state.json"

        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                    self.local_device_id = data.get("local_device_id")
                    self.routing_table.load(data.get("routing_table", {}))
            except Exception as e:
                print(f"Warning: Failed to load network state: {e}")

    def _save_state(self) -> None:
        """Save network state to disk."""
        state_file = self.data_dir / "network_state.json"

        try:
            data = {
                "local_device_id": self.local_device_id,
                "routing_table": self.routing_table.to_dict(),
                "saved_at": time.time(),
            }
            with open(state_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save network state: {e}")

    # ─────────────────────────────────────────────────────────────
    # Service Lifecycle
    # ─────────────────────────────────────────────────────────────

    def start(self, device_id: Optional[str] = None) -> bool:
        """
        Start the mesh service.

        Args:
            device_id: Local device identifier (auto-generated if None)

        Returns:
            True if started successfully
        """
        if self._running:
            return True

        self.local_device_id = device_id or self._generate_device_id()
        self._running = True
        self._start_time = time.time()

        # Start background threads
        self._scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._message_thread = threading.Thread(target=self._message_loop, daemon=True)

        self._scan_thread.start()
        self._message_thread.start()

        self._set_state(ConnectionState.MESH_ONLY)

        return True

    def stop(self) -> bool:
        """
        Stop the mesh service.

        Returns:
            True if stopped successfully
        """
        if not self._running:
            return True

        self._running = False
        self._save_state()

        # Wait for threads to finish
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join(timeout=2.0)
        if self._message_thread and self._message_thread.is_alive():
            self._message_thread.join(timeout=2.0)

        self._set_state(ConnectionState.OFFLINE)

        return True

    def _generate_device_id(self) -> str:
        """Generate a unique device identifier."""
        import uuid

        return f"D{uuid.uuid4().hex[:6].upper()}"

    def _set_state(self, new_state: ConnectionState) -> None:
        """Update connection state and notify listeners."""
        old_state = self.state
        self.state = new_state

        if old_state != new_state:
            self._emit_event(
                NetworkEvent.STATE_CHANGED,
                {"old_state": old_state.value, "new_state": new_state.value},
            )

    # ─────────────────────────────────────────────────────────────
    # Device Discovery
    # ─────────────────────────────────────────────────────────────

    def scan(self, tile: Optional[str] = None, timeout: float = 5.0) -> List[Device]:
        """
        Scan for nearby devices.

        Args:
            tile: TILE code to scan (None for current location)
            timeout: Scan timeout in seconds

        Returns:
            List of discovered devices
        """
        self._set_state(ConnectionState.SCANNING)
        discovered = []

        try:
            # In simulation mode, return registered devices
            # In real implementation, this would broadcast discovery packets
            devices = self.device_registry.list_devices(tile=tile)

            for device in devices:
                if device.id != self.local_device_id:
                    discovered.append(device)
                    self._emit_event(
                        NetworkEvent.DEVICE_DISCOVERED,
                        {
                            "device_id": device.id,
                            "tile": device.tile,
                            "signal": device.signal,
                        },
                    )

            self.stats.devices_discovered += len(discovered)
            self.stats.last_scan_time = time.time()

        finally:
            self._set_state(ConnectionState.MESH_ONLY)

        return discovered

    def pair(self, device_id: str) -> bool:
        """
        Pair with a device.

        Args:
            device_id: Device to pair with

        Returns:
            True if pairing successful
        """
        device = self.device_registry.get_device(device_id)

        if not device:
            return False

        # Add bidirectional connection
        if self.local_device_id:
            local_device = self.device_registry.get_device(self.local_device_id)

            if local_device:
                if device_id not in local_device.connections:
                    local_device.connections.append(device_id)
                if self.local_device_id not in device.connections:
                    device.connections.append(self.local_device_id)

                self.device_registry._save_devices()

                # Update routing table
                self.routing_table.add_direct_route(
                    self.local_device_id, device_id, device.signal
                )

                self._emit_event(
                    NetworkEvent.DEVICE_CONNECTED, {"device_id": device_id}
                )

                return True

        return False

    def unpair(self, device_id: str) -> bool:
        """
        Unpair from a device.

        Args:
            device_id: Device to unpair from

        Returns:
            True if unpairing successful
        """
        device = self.device_registry.get_device(device_id)

        if not device:
            return False

        if self.local_device_id:
            local_device = self.device_registry.get_device(self.local_device_id)

            if local_device:
                if device_id in local_device.connections:
                    local_device.connections.remove(device_id)
                if self.local_device_id in device.connections:
                    device.connections.remove(self.local_device_id)

                self.device_registry._save_devices()

                # Update routing table
                self.routing_table.remove_route(self.local_device_id, device_id)

                self._emit_event(
                    NetworkEvent.DEVICE_DISCONNECTED, {"device_id": device_id}
                )

                return True

        return False

    # ─────────────────────────────────────────────────────────────
    # Messaging
    # ─────────────────────────────────────────────────────────────

    def send(
        self, target: str, payload: str, msg_type: MessageType = MessageType.DATA
    ) -> bool:
        """
        Send a message to a target device.

        Args:
            target: Target device ID
            payload: Message content
            msg_type: Message type

        Returns:
            True if message queued successfully
        """
        if not self.local_device_id:
            return False

        message = create_message(
            source=self.local_device_id,
            target=target,
            payload=payload,
            msg_type=msg_type,
        )

        self._outbound_queue.put(message)
        self.stats.messages_sent += 1
        self.stats.bytes_sent += len(payload)

        return True

    def broadcast(
        self, payload: str, msg_type: MessageType = MessageType.BROADCAST
    ) -> int:
        """
        Broadcast a message to all connected devices.

        Args:
            payload: Message content
            msg_type: Message type

        Returns:
            Number of devices messaged
        """
        if not self.local_device_id:
            return 0

        local_device = self.device_registry.get_device(self.local_device_id)

        if not local_device:
            return 0

        count = 0
        for device_id in local_device.connections:
            if self.send(device_id, payload, msg_type):
                count += 1

        return count

    def receive(self, timeout: float = 0.0) -> Optional[MeshMessage]:
        """
        Receive a message from the inbound queue.

        Args:
            timeout: Wait timeout (0 for non-blocking)

        Returns:
            Received message or None
        """
        try:
            message = self._inbound_queue.get(
                timeout=timeout if timeout > 0 else None, block=timeout > 0
            )
            self.stats.messages_received += 1
            self.stats.bytes_received += len(message.payload)
            return message
        except queue.Empty:
            return None

    # ─────────────────────────────────────────────────────────────
    # Routing
    # ─────────────────────────────────────────────────────────────

    def find_route(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find route between two devices.

        Args:
            source: Source device ID
            target: Target device ID

        Returns:
            List of device IDs in route, or None if no route
        """
        route = self.routing_table.find_route(source, target)

        if route:
            self.stats.routes_computed += 1
            self._emit_event(
                NetworkEvent.ROUTE_UPDATED,
                {"source": source, "target": target, "route": route},
            )

        return route

    def get_topology(self, tile: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get network topology graph.

        Args:
            tile: TILE code to filter by (None for all)

        Returns:
            Dictionary mapping device IDs to connected device IDs
        """
        devices = self.device_registry.list_devices(tile=tile)
        topology = {}

        for device in devices:
            topology[device.id] = device.connections.copy()

        return topology

    # ─────────────────────────────────────────────────────────────
    # Signal Monitoring
    # ─────────────────────────────────────────────────────────────

    def get_signal_heatmap(self, tile: str, layer: int = 610) -> Dict[str, int]:
        """
        Get signal strength heatmap for a tile.

        Args:
            tile: TILE code
            layer: Map layer (default: 610 for signal heatmap)

        Returns:
            Dictionary mapping device IDs to signal strength
        """
        devices = self.device_registry.list_devices(tile=tile)
        return {d.id: d.signal for d in devices}

    def get_coverage_area(self) -> List[str]:
        """
        Get list of tiles with mesh coverage.

        Returns:
            List of TILE codes with active devices
        """
        devices = self.device_registry.list_devices()
        return list(set(d.tile for d in devices if d.status == DeviceStatus.ONLINE))

    # ─────────────────────────────────────────────────────────────
    # Event System
    # ─────────────────────────────────────────────────────────────

    def on(self, event: NetworkEvent, callback: Callable[[Dict], None]) -> None:
        """
        Register event callback.

        Args:
            event: Event type
            callback: Callback function (receives event data dict)
        """
        self._event_callbacks[event].append(callback)

    def off(self, event: NetworkEvent, callback: Callable[[Dict], None]) -> None:
        """
        Unregister event callback.

        Args:
            event: Event type
            callback: Callback function to remove
        """
        if callback in self._event_callbacks[event]:
            self._event_callbacks[event].remove(callback)

    def _emit_event(self, event: NetworkEvent, data: Dict) -> None:
        """Emit event to all registered callbacks."""
        for callback in self._event_callbacks[event]:
            try:
                callback(data)
            except Exception as e:
                print(f"Warning: Event callback error: {e}")

    # ─────────────────────────────────────────────────────────────
    # Background Tasks
    # ─────────────────────────────────────────────────────────────

    def _scan_loop(self) -> None:
        """Background thread for periodic device scanning."""
        while self._running:
            time.sleep(30.0)  # Scan every 30 seconds

            try:
                self.scan(timeout=5.0)
            except Exception as e:
                print(f"Warning: Scan error: {e}")

    def _message_loop(self) -> None:
        """Background thread for message processing."""
        while self._running:
            try:
                # Process outbound messages
                try:
                    message = self._outbound_queue.get(timeout=0.1)
                    self._process_outbound(message)
                except queue.Empty:
                    pass

            except Exception as e:
                print(f"Warning: Message loop error: {e}")

    def _process_outbound(self, message: MeshMessage) -> None:
        """Process outbound message (simulation or real transport)."""
        # In simulation mode, directly deliver to target
        # In real implementation, this would use network transport

        target_device = self.device_registry.get_device(message.target)

        if target_device and target_device.status == DeviceStatus.ONLINE:
            # Simulate delivery
            self._inbound_queue.put(message)

            self._emit_event(
                NetworkEvent.MESSAGE_SENT,
                {"message_id": message.id, "target": message.target},
            )

    # ─────────────────────────────────────────────────────────────
    # Status & Statistics
    # ─────────────────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """
        Get service status.

        Returns:
            Status dictionary
        """
        uptime = time.time() - self._start_time if self._running else 0.0
        self.stats.uptime_seconds = uptime

        return {
            "running": self._running,
            "state": self.state.value,
            "local_device_id": self.local_device_id,
            "uptime_seconds": uptime,
            "stats": {
                "messages_sent": self.stats.messages_sent,
                "messages_received": self.stats.messages_received,
                "bytes_sent": self.stats.bytes_sent,
                "bytes_received": self.stats.bytes_received,
                "devices_discovered": self.stats.devices_discovered,
                "routes_computed": self.stats.routes_computed,
            },
        }

    def get_network_stats(self) -> NetworkStats:
        """Get network statistics."""
        self.stats.uptime_seconds = (
            time.time() - self._start_time if self._running else 0.0
        )
        return self.stats


# Singleton instance
_service_instance: Optional[MeshCoreService] = None


def get_mesh_service() -> MeshCoreService:
    """Get or create the mesh service singleton."""
    global _service_instance

    if _service_instance is None:
        _service_instance = MeshCoreService()

    return _service_instance
