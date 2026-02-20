"""
Vibe Device Service

Manages device listing, status checks, updates, and registration.
Integrates with device database and health monitoring systems.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from core.services.logging_manager import get_logger
from core.services.persistence_service import get_persistence_service


@dataclass
class Device:
    """Device representation."""
    id: str
    name: str
    type: str  # "server", "workstation", "container", "vm"
    location: str
    status: str  # "online", "offline", "maintenance", "degraded"
    last_seen: str
    version: Optional[str] = None
    tags: Optional[List[str]] = None


class VibeDeviceService:
    """Manage devices and hardware inventory."""

    _DATA_FILE = "devices"

    def __init__(self):
        """Initialize device service."""
        self.logger = get_logger("vibe-device-service")
        self.persistence_service = get_persistence_service()
        self.devices: Dict[str, Device] = {}
        self._load_devices()

    def _load_devices(self) -> None:
        """Load device inventory from persistent storage."""
        self.logger.debug("Loading device inventory from persistence...")
        data = self.persistence_service.read_data(self._DATA_FILE)
        if data and "devices" in data:
            self.devices = {
                dev_id: Device(**dev_data)
                for dev_id, dev_data in data["devices"].items()
            }
            self.logger.info(f"Loaded {len(self.devices)} devices.")
        else:
            self.logger.warning("No persistent device data found.")

    def _save_devices(self) -> None:
        """Save devices to persistent storage."""
        self.logger.debug("Saving devices to persistence...")
        data = {
            "devices": {
                dev_id: asdict(dev) for dev_id, dev in self.devices.items()
            }
        }
        self.persistence_service.write_data(self._DATA_FILE, data)

    def list_devices(
        self,
        filter_name: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List all devices with optional filtering.

        Args:
            filter_name: Filter by device name (substring match)
            location: Filter by location
            status: Filter by status (online|offline|maintenance|degraded)

        Returns:
            Dict with status, device list, and count
        """
        devices = list(self.devices.values())

        if filter_name:
            devices = [d for d in devices if filter_name.lower() in d.name.lower()]

        if location:
            devices = [d for d in devices if d.location == location]

        if status:
            devices = [d for d in devices if d.status == status]

        return {
            "status": "success",
            "devices": [asdict(d) for d in devices],
            "count": len(devices),
            "total": len(self.devices),
        }

    def device_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get detailed status for a specific device.

        Args:
            device_id: Device ID

        Returns:
            Dict with device details, health metrics, and status
        """
        device = self.devices.get(device_id)
        if not device:
            return {
                "status": "error",
                "message": f"Device not found: {device_id}",
            }

        return {
            "status": "success",
            "device": asdict(device),
            "health": {
                "uptime_hours": 24,  # Phase 4: Actual uptime
                "cpu_usage": 45.2,   # Phase 4: Actual metrics
                "memory_usage": 62.1,
                "disk_usage": 38.7,
            },
            "alerts": [],  # Phase 4: Fetch actual alerts
        }

    def add_device(
        self,
        name: str,
        device_type: str,
        location: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Register a new device.

        Args:
            name: Device name
            device_type: Device type (server|workstation|container|vm)
            location: Physical or logical location
            **kwargs: Additional metadata (version, tags, etc.)

        Returns:
            Dict with success status and device ID
        """
        if not name or not device_type or not location:
            return {
                "status": "error",
                "message": "Missing required fields: name, device_type, location",
            }

        # Generate device ID (Phase 4: use proper UUID)
        device_id = f"{location.lower()}/{name.lower().replace(' ', '_')}"

        device = Device(
            id=device_id,
            name=name,
            type=device_type,
            location=location,
            status="online",
            last_seen=datetime.now().isoformat(),
            version=kwargs.get("version"),
            tags=kwargs.get("tags", []),
        )

        self.devices[device_id] = device
        self._save_devices()
        self.logger.info(f"Registered device: {device_id}")

        return {
            "status": "success",
            "message": f"Device registered: {device_id}",
            "device_id": device_id,
            "device": asdict(device),
        }

    def update_device(
        self,
        device_id: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Update device configuration or status.

        Args:
            device_id: Device ID
            **kwargs: Fields to update (name, location, tags, etc.)

        Returns:
            Dict with success status and updated device
        """
        device = self.devices.get(device_id)
        if not device:
            return {
                "status": "error",
                "message": f"Device not found: {device_id}",
            }

        # Update allowed fields
        if "name" in kwargs:
            device.name = kwargs["name"]
        if "location" in kwargs:
            device.location = kwargs["location"]
        if "tags" in kwargs:
            device.tags = kwargs["tags"]
        if "status" in kwargs:
            device.status = kwargs["status"]

        device.last_seen = datetime.now().isoformat()
        self._save_devices()

        self.logger.info(f"Updated device: {device_id}")

        return {
            "status": "success",
            "message": f"Device updated: {device_id}",
            "device": asdict(device),
        }


# Global singleton
_device_service: Optional[VibeDeviceService] = None


def get_device_service() -> VibeDeviceService:
    """Get or create the global device service."""
    global _device_service
    if _device_service is None:
        _device_service = VibeDeviceService()
    return _device_service
