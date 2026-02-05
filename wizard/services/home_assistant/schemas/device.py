"""Device schema definitions for Home Assistant gateway."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class DeviceType(str, Enum):
    """Supported device types."""
    LIGHT = "light"
    SWITCH = "switch"
    TEMPLATE = "template"
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    CLIMATE = "climate"
    LOCK = "lock"
    COVER = "cover"
    CAMERA = "camera"
    MEDIA_PLAYER = "media_player"
    CUSTOM = "custom"


@dataclass
class DeviceSchema:
    """Represents a Home Assistant device."""
    id: str
    name: str
    type: DeviceType
    model: str
    manufacturer: str
    hw_version: Optional[str] = None
    sw_version: Optional[str] = None
    via_device_id: Optional[str] = None
    suggested_area: Optional[str] = None
    config_entries: List[str] = field(default_factory=list)
    connections: Dict[str, str] = field(default_factory=dict)
    identifiers: List[tuple] = field(default_factory=list)
    disabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DeviceStateSchema:
    """Device state and status information."""
    device_id: str
    is_available: bool = True
    last_seen: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    state_attributes: Dict[str, Any] = field(default_factory=dict)
    connection_status: str = "unknown"  # connected, disconnected, error
    signal_strength: Optional[int] = None
    battery_level: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, serializing datetime objects."""
        data = asdict(self)
        if self.last_seen:
            data["last_seen"] = self.last_seen.isoformat()
        if self.last_updated:
            data["last_updated"] = self.last_updated.isoformat()
        return data
