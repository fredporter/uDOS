"""Gateway configuration and status schemas."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class GatewayConfigSchema:
    """Home Assistant gateway configuration."""
    gateway_id: str
    name: str
    ha_url: str
    ha_token: str
    ws_enabled: bool = True
    rest_enabled: bool = True
    auto_discovery: bool = True
    discovery_interval: int = 60  # seconds
    heartbeat_interval: int = 30  # seconds
    max_connections: int = 100
    tls_enabled: bool = False
    tls_cert_path: Optional[str] = None
    tls_key_path: Optional[str] = None
    allowed_domains: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (security: hide token)."""
        data = asdict(self)
        data["ha_token"] = "***REDACTED***"
        return data


@dataclass
class GatewayStatusSchema:
    """Gateway operational status."""
    status: str  # 'running', 'connecting', 'error', 'stopped'
    connected: bool = False
    uptime_seconds: int = 0
    total_devices: int = 0
    available_devices: int = 0
    total_entities: int = 0
    active_connections: int = 0
    last_heartbeat: Optional[str] = None
    error_message: Optional[str] = None
    version: str = "0.1.0"
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
