#!/usr/bin/env python3
"""
MeshCore Device Manager - Device data and state management for Layer 600-650

Manages device registry, network topology, signal metrics, and firmware status
for MeshCore networking layer (600-609) and Sonic Screwdriver provisioning (650).

Features:
- Device registration and lifecycle management
- Network topology tracking (connections, routes)
- Signal strength metrics and heatmap data
- Firmware version tracking and update status
- Real-time device state monitoring
- Persistence to JSON storage

Version: v1.2.14
Author: Fred Porter
Date: December 7, 2025
"""

import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum


class DeviceType(Enum):
    """Device types for MeshCore network."""
    NODE = "⊚"          # Primary node/hub
    GATEWAY = "⊕"       # Gateway/router
    SENSOR = "⊗"        # Sensor/monitor
    REPEATER = "⊙"      # Repeater/relay
    END_DEVICE = "⊘"    # End device/client


class DeviceStatus(Enum):
    """Device operational status."""
    ONLINE = "●"        # Active/online
    OFFLINE = "○"       # Inactive/offline
    CONNECTING = "◐"    # Transitioning/connecting
    ERROR = "◑"         # Error/warning state


class FirmwareStatus(Enum):
    """Firmware update status."""
    CURRENT = "✓"       # Up to date
    OUTDATED = "⚠"      # Needs update
    INCOMPATIBLE = "✗"  # Incompatible version
    UPDATING = "⟳"      # Update in progress


@dataclass
class Device:
    """MeshCore device representation."""
    id: str                          # Device ID (e.g., "D1")
    tile: str                        # TILE code (e.g., "AA340")
    layer: int                       # Layer number (600-650)
    type: DeviceType                 # Device type
    status: DeviceStatus             # Current status
    signal: int                      # Signal strength (0-100%)
    firmware_version: str            # Firmware version (e.g., "2.4.1")
    firmware_status: FirmwareStatus  # Firmware status
    uptime: float                    # Uptime in hours
    msgs_per_sec: int                # Message throughput
    last_seen: float                 # Unix timestamp
    connections: List[str]           # Connected device IDs
    
    @property
    def full_code(self) -> str:
        """Generate full TILE+layer+device code."""
        return f"{self.tile}-{self.layer}-{self.id}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert enums to values
        data['type'] = self.type.value
        data['status'] = self.status.value
        data['firmware_status'] = self.firmware_status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Device':
        """Create Device from dictionary."""
        # Convert enum strings back to enums
        data['type'] = DeviceType(data['type'])
        data['status'] = DeviceStatus(data['status'])
        data['firmware_status'] = FirmwareStatus(data['firmware_status'])
        return cls(**data)


class MeshCoreDeviceManager:
    """
    Manages MeshCore device registry and network topology.
    
    Handles device lifecycle, state tracking, signal metrics,
    and firmware management for Layer 600-650.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize device manager.
        
        Args:
            data_dir: Directory for device data storage
        """
        if data_dir is None:
            data_dir = Path(__file__).parent / "data" / "meshcore"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.devices: Dict[str, Device] = {}
        self.topology: Dict[str, List[str]] = {}  # device_id -> [connected_ids]
        self.signal_map: Dict[str, Dict[str, int]] = {}  # tile -> {device_id: signal}
        
        self._load_devices()
    
    def _get_device_file(self) -> Path:
        """Get path to device registry file."""
        return self.data_dir / "devices.json"
    
    def _load_devices(self) -> None:
        """Load devices from storage."""
        device_file = self._get_device_file()
        
        if device_file.exists():
            try:
                with open(device_file, 'r') as f:
                    data = json.load(f)
                    
                for device_id, device_data in data.get('devices', {}).items():
                    self.devices[device_id] = Device.from_dict(device_data)
                
                self.topology = data.get('topology', {})
                self.signal_map = data.get('signal_map', {})
                
            except Exception as e:
                print(f"Warning: Failed to load devices: {e}")
    
    def _save_devices(self) -> None:
        """Save devices to storage."""
        device_file = self._get_device_file()
        
        data = {
            'devices': {
                device_id: device.to_dict()
                for device_id, device in self.devices.items()
            },
            'topology': self.topology,
            'signal_map': self.signal_map,
            'last_updated': time.time()
        }
        
        with open(device_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_device(
        self,
        device_id: str,
        tile: str,
        layer: int,
        device_type: DeviceType,
        firmware_version: str = "2.4.1"
    ) -> Device:
        """
        Register new device in MeshCore network.
        
        Args:
            device_id: Unique device identifier
            tile: TILE code
            layer: Layer number (600-650)
            device_type: Type of device
            firmware_version: Initial firmware version
            
        Returns:
            Registered Device instance
        """
        device = Device(
            id=device_id,
            tile=tile,
            layer=layer,
            type=device_type,
            status=DeviceStatus.CONNECTING,
            signal=0,
            firmware_version=firmware_version,
            firmware_status=FirmwareStatus.CURRENT,
            uptime=0.0,
            msgs_per_sec=0,
            last_seen=time.time(),
            connections=[]
        )
        
        self.devices[device_id] = device
        self.topology[device_id] = []
        
        # Initialize signal map for this tile
        if tile not in self.signal_map:
            self.signal_map[tile] = {}
        self.signal_map[tile][device_id] = 0
        
        self._save_devices()
        return device
    
    def update_device_status(
        self,
        device_id: str,
        status: Optional[DeviceStatus] = None,
        signal: Optional[int] = None,
        uptime: Optional[float] = None,
        msgs_per_sec: Optional[int] = None
    ) -> bool:
        """
        Update device operational status.
        
        Args:
            device_id: Device to update
            status: New status
            signal: Signal strength (0-100)
            uptime: Uptime in hours
            msgs_per_sec: Message throughput
            
        Returns:
            True if updated successfully
        """
        if device_id not in self.devices:
            return False
        
        device = self.devices[device_id]
        
        if status is not None:
            device.status = status
        
        if signal is not None:
            device.signal = max(0, min(100, signal))
            self.signal_map[device.tile][device_id] = device.signal
        
        if uptime is not None:
            device.uptime = uptime
        
        if msgs_per_sec is not None:
            device.msgs_per_sec = msgs_per_sec
        
        device.last_seen = time.time()
        
        self._save_devices()
        return True
    
    def connect_devices(self, device_a: str, device_b: str) -> bool:
        """
        Establish connection between two devices.
        
        Args:
            device_a: First device ID
            device_b: Second device ID
            
        Returns:
            True if connection established
        """
        if device_a not in self.devices or device_b not in self.devices:
            return False
        
        # Add bidirectional connections
        if device_b not in self.topology[device_a]:
            self.topology[device_a].append(device_b)
            self.devices[device_a].connections.append(device_b)
        
        if device_a not in self.topology[device_b]:
            self.topology[device_b].append(device_a)
            self.devices[device_b].connections.append(device_a)
        
        self._save_devices()
        return True
    
    def disconnect_devices(self, device_a: str, device_b: str) -> bool:
        """
        Remove connection between two devices.
        
        Args:
            device_a: First device ID
            device_b: Second device ID
            
        Returns:
            True if connection removed
        """
        if device_a not in self.devices or device_b not in self.devices:
            return False
        
        # Remove bidirectional connections
        if device_b in self.topology[device_a]:
            self.topology[device_a].remove(device_b)
            self.devices[device_a].connections.remove(device_b)
        
        if device_a in self.topology[device_b]:
            self.topology[device_b].remove(device_a)
            self.devices[device_b].connections.remove(device_a)
        
        self._save_devices()
        return True
    
    def update_firmware_status(
        self,
        device_id: str,
        version: Optional[str] = None,
        status: Optional[FirmwareStatus] = None
    ) -> bool:
        """
        Update device firmware version and status.
        
        Args:
            device_id: Device to update
            version: New firmware version
            status: Firmware status
            
        Returns:
            True if updated successfully
        """
        if device_id not in self.devices:
            return False
        
        device = self.devices[device_id]
        
        if version is not None:
            device.firmware_version = version
        
        if status is not None:
            device.firmware_status = status
        
        self._save_devices()
        return True
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID."""
        return self.devices.get(device_id)
    
    def list_devices(
        self,
        tile: Optional[str] = None,
        layer: Optional[int] = None,
        status: Optional[DeviceStatus] = None
    ) -> List[Device]:
        """
        List devices with optional filters.
        
        Args:
            tile: Filter by TILE code
            layer: Filter by layer
            status: Filter by status
            
        Returns:
            List of matching devices
        """
        devices = list(self.devices.values())
        
        if tile is not None:
            devices = [d for d in devices if d.tile == tile]
        
        if layer is not None:
            devices = [d for d in devices if d.layer == layer]
        
        if status is not None:
            devices = [d for d in devices if d.status == status]
        
        return devices
    
    def get_network_stats(self) -> Dict:
        """
        Get network-wide statistics.
        
        Returns:
            Dictionary with network metrics
        """
        total = len(self.devices)
        online = sum(1 for d in self.devices.values() if d.status == DeviceStatus.ONLINE)
        offline = sum(1 for d in self.devices.values() if d.status == DeviceStatus.OFFLINE)
        connecting = sum(1 for d in self.devices.values() if d.status == DeviceStatus.CONNECTING)
        
        avg_signal = 0
        if total > 0:
            avg_signal = sum(d.signal for d in self.devices.values()) / total
        
        return {
            'total_devices': total,
            'online': online,
            'offline': offline,
            'connecting': connecting,
            'avg_signal': round(avg_signal, 1),
            'total_connections': sum(len(conns) for conns in self.topology.values()) // 2
        }
    
    def get_signal_heatmap(self, tile: str, width: int = 6, height: int = 4) -> List[List[int]]:
        """
        Generate signal strength heatmap for a tile area.
        
        Args:
            tile: Base TILE code
            width: Grid width in cells
            height: Grid height in rows
            
        Returns:
            2D array of signal values (0-100)
        """
        # For now, generate synthetic heatmap based on device positions
        # In production, this would use actual signal propagation modeling
        
        heatmap = [[0 for _ in range(width)] for _ in range(height)]
        
        # Get devices in this tile
        tile_devices = self.signal_map.get(tile, {})
        
        if not tile_devices:
            # Generate default gradient pattern
            for row in range(height):
                for col in range(width):
                    # Diagonal gradient from top-left
                    distance = ((row / height) + (col / width)) / 2
                    heatmap[row][col] = int(100 * (1 - distance))
        else:
            # Use actual device signals to generate heatmap
            for device_id, signal in tile_devices.items():
                # Simplified: spread signal in area
                center_row = hash(device_id) % height
                center_col = hash(device_id) % width
                
                for row in range(height):
                    for col in range(height):
                        distance = abs(row - center_row) + abs(col - center_col)
                        falloff = max(0, signal - (distance * 15))
                        heatmap[row][col] = max(heatmap[row][col], falloff)
        
        return heatmap
    
    def find_route(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find route between two devices using BFS.
        
        Args:
            source: Source device ID
            target: Target device ID
            
        Returns:
            List of device IDs forming route, or None if no route
        """
        if source not in self.devices or target not in self.devices:
            return None
        
        if source == target:
            return [source]
        
        # BFS to find shortest path
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            current, path = queue.pop(0)
            
            for neighbor in self.topology.get(current, []):
                if neighbor == target:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def remove_device(self, device_id: str) -> bool:
        """
        Remove device from network.
        
        Args:
            device_id: Device to remove
            
        Returns:
            True if removed successfully
        """
        if device_id not in self.devices:
            return False
        
        device = self.devices[device_id]
        
        # Remove all connections
        for connected_id in list(self.topology.get(device_id, [])):
            self.disconnect_devices(device_id, connected_id)
        
        # Remove from signal map
        if device.tile in self.signal_map:
            self.signal_map[device.tile].pop(device_id, None)
        
        # Remove from topology
        self.topology.pop(device_id, None)
        
        # Remove device
        del self.devices[device_id]
        
        self._save_devices()
        return True


def demo_device_manager():
    """Demonstrate device manager functionality."""
    
    print("=" * 80)
    print("MeshCore Device Manager Demo - v1.2.14")
    print("=" * 80)
    print()
    
    # Create manager with temp directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MeshCoreDeviceManager(Path(tmpdir))
        
        # Register devices
        print("Registering devices...")
        d1 = manager.register_device("D1", "AA340", 600, DeviceType.NODE, "2.4.1")
        d2 = manager.register_device("D2", "AA340", 600, DeviceType.GATEWAY, "2.4.1")
        d3 = manager.register_device("D3", "AA340", 600, DeviceType.SENSOR, "2.4.1")
        d4 = manager.register_device("D4", "AA340", 600, DeviceType.REPEATER, "2.3.0")
        d5 = manager.register_device("D5", "AA340", 600, DeviceType.END_DEVICE, "2.4.1")
        print(f"  ✓ Registered 5 devices")
        print()
        
        # Update device status
        print("Updating device status...")
        manager.update_device_status("D1", DeviceStatus.ONLINE, signal=82, uptime=24.0, msgs_per_sec=145)
        manager.update_device_status("D2", DeviceStatus.ONLINE, signal=76, uptime=18.0, msgs_per_sec=203)
        manager.update_device_status("D3", DeviceStatus.ONLINE, signal=91, uptime=36.0, msgs_per_sec=87)
        manager.update_device_status("D4", DeviceStatus.OFFLINE, signal=0, uptime=0.0, msgs_per_sec=0)
        manager.update_device_status("D5", DeviceStatus.ONLINE, signal=68, uptime=12.0, msgs_per_sec=54)
        print(f"  ✓ Updated 5 device statuses")
        print()
        
        # Connect devices
        print("Establishing connections...")
        manager.connect_devices("D1", "D2")
        manager.connect_devices("D1", "D3")
        manager.connect_devices("D2", "D5")
        manager.connect_devices("D3", "D5")
        print(f"  ✓ Created 4 connections")
        print()
        
        # Network stats
        print("Network Statistics:")
        stats = manager.get_network_stats()
        print(f"  Total Devices: {stats['total_devices']}")
        print(f"  Online: {stats['online']} | Offline: {stats['offline']} | Connecting: {stats['connecting']}")
        print(f"  Average Signal: {stats['avg_signal']}%")
        print(f"  Total Connections: {stats['total_connections']}")
        print()
        
        # List online devices
        print("Online Devices:")
        for device in manager.list_devices(status=DeviceStatus.ONLINE):
            print(f"  {device.type.value} {device.id:3} | Signal: {device.signal:3}% | "
                  f"Uptime: {device.uptime:5.1f}h | Msgs/s: {device.msgs_per_sec:3}")
        print()
        
        # Find route
        print("Route Finding:")
        route = manager.find_route("D1", "D5")
        if route:
            print(f"  Route D1 → D5: {' → '.join(route)}")
        print()
        
        # Signal heatmap
        print("Signal Heatmap (AA340):")
        heatmap = manager.get_signal_heatmap("AA340", width=6, height=4)
        for row in heatmap:
            bars = '  '
            for signal in row:
                if signal >= 88:
                    bars += '█'
                elif signal >= 63:
                    bars += '▓'
                elif signal >= 38:
                    bars += '▒'
                elif signal > 0:
                    bars += '░'
                else:
                    bars += ' '
            print(bars)
        print()
        
        print("✅ Device manager demo complete!")


if __name__ == "__main__":
    demo_device_manager()
