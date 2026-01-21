"""
MeshCore Device Registry - Basic device tracking for P2P networking

Provides lightweight device registration for mesh networking without
firmware management (which is in wizard/tools/screwdriver/).

Version: v1.0.0.32
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import time
import json
from pathlib import Path


class DeviceType(Enum):
    """Device types for MeshCore network."""

    NODE = "⊚"  # Primary node/hub
    GATEWAY = "⊕"  # Gateway/router
    SENSOR = "⊗"  # Sensor/monitor
    REPEATER = "⊙"  # Repeater/relay
    END_DEVICE = "⊘"  # End device/client


class DeviceStatus(Enum):
    """Device operational status."""

    ONLINE = "●"  # Active/online
    OFFLINE = "○"  # Inactive/offline
    CONNECTING = "◐"  # Transitioning/connecting
    ERROR = "◑"  # Error/warning state


@dataclass
class Device:
    """Basic MeshCore device representation."""

    id: str  # Device ID (e.g., "D1")
    type: DeviceType  # Device type
    status: DeviceStatus  # Current status
    signal: int  # Signal strength (0-100%)
    last_seen: float  # Unix timestamp
    connections: List[str]  # Connected device IDs

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["type"] = self.type.value
        data["status"] = self.status.value
        return data


class DeviceRegistry:
    """
    Basic device registry for mesh networking.

    For firmware management and advanced device features,
    see wizard/tools/screwdriver/meshcore_device_manager.py
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize device registry."""
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.devices: Dict[str, Device] = {}
        self._load_devices()

    def _load_devices(self):
        """Load devices from storage."""
        devices_file = self.data_dir / "devices.json"
        if devices_file.exists():
            try:
                data = json.loads(devices_file.read_text())
                for d in data.get("devices", []):
                    device = Device(
                        id=d["id"],
                        type=DeviceType(d["type"]),
                        status=DeviceStatus(d["status"]),
                        signal=d.get("signal", 0),
                        last_seen=d.get("last_seen", 0),
                        connections=d.get("connections", []),
                    )
                    self.devices[device.id] = device
            except Exception:
                pass

    def save_devices(self):
        """Save devices to storage."""
        devices_file = self.data_dir / "devices.json"
        data = {
            "devices": [d.to_dict() for d in self.devices.values()],
            "saved_at": time.time(),
        }
        devices_file.write_text(json.dumps(data, indent=2))

    def register_device(
        self, device_id: str, device_type: DeviceType = DeviceType.END_DEVICE
    ) -> Device:
        """Register a new device."""
        device = Device(
            id=device_id,
            type=device_type,
            status=DeviceStatus.ONLINE,
            signal=100,
            last_seen=time.time(),
            connections=[],
        )
        self.devices[device_id] = device
        self.save_devices()
        return device

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID."""
        return self.devices.get(device_id)

    def list_devices(self, status: Optional[DeviceStatus] = None) -> List[Device]:
        """List all devices, optionally filtered by status."""
        if status:
            return [d for d in self.devices.values() if d.status == status]
        return list(self.devices.values())

    def update_status(self, device_id: str, status: DeviceStatus):
        """Update device status."""
        if device_id in self.devices:
            self.devices[device_id].status = status
            self.devices[device_id].last_seen = time.time()
            self.save_devices()

    def remove_device(self, device_id: str) -> bool:
        """Remove device from registry."""
        if device_id in self.devices:
            del self.devices[device_id]
            self.save_devices()
            return True
        return False


# Singleton instance
_registry = None


def get_device_registry() -> DeviceRegistry:
    """Get or create device registry singleton."""
    global _registry
    if _registry is None:
        _registry = DeviceRegistry()
    return _registry
