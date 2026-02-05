"""Entity schema definitions for Home Assistant gateway."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class EntitySchema:
    """Represents a Home Assistant entity (device interface)."""
    entity_id: str
    device_id: str
    domain: str
    name: str
    unique_id: str
    platform: str
    icon: Optional[str] = None
    entity_category: Optional[str] = None
    has_entity_name: bool = False
    enabled_by_default: bool = True
    disabled: bool = False
    state_class: Optional[str] = None
    unit_of_measurement: Optional[str] = None
    suggested_display_precision: Optional[int] = None
    capabilities: Dict[str, Any] = field(default_factory=dict)
    options: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EntityStateSchema:
    """Current state of an entity."""
    entity_id: str
    state: str  # 'on', 'off', numeric value, etc
    attributes: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    last_changed: Optional[str] = None
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
