"""
Device Authentication Service
=============================

Manages device pairing, authentication, and trust levels for mesh network.

Features:
- Device pairing via QR/code/NFC
- Trust levels (Admin, Standard, Guest)
- Session management
- Device sync tracking

Version: v1.0.0.0
Date: 2026-01-06
"""

import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading

from wizard.services.logging_manager import get_logger

logger = get_logger("wizard-device-auth")

# Paths
WIZARD_DATA = Path(__file__).parent.parent.parent / "memory" / "wizard"
DEVICES_FILE = WIZARD_DATA / "devices.json"
SESSIONS_FILE = WIZARD_DATA / "sessions.json"


class TrustLevel(Enum):
    """Device trust levels."""

    ADMIN = "admin"  # Full access to Wizard Server
    STANDARD = "standard"  # Normal mesh device
    GUEST = "guest"  # Limited, read-only access
    PENDING = "pending"  # Awaiting approval


class DeviceStatus(Enum):
    """Device connection status."""

    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"


@dataclass
class Device:
    """Paired device record."""

    id: str
    name: str
    device_type: str  # desktop, mobile, tinycore
    trust_level: TrustLevel = TrustLevel.STANDARD
    status: DeviceStatus = DeviceStatus.OFFLINE
    transport: str = "meshcore"
    paired_at: str = ""
    last_seen: str = ""
    last_sync: str = ""
    sync_version: int = 0
    public_key: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["trust_level"] = self.trust_level.value
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Device":
        data["trust_level"] = TrustLevel(data.get("trust_level", "standard"))
        data["status"] = DeviceStatus(data.get("status", "offline"))
        return cls(**data)


@dataclass
class PairingRequest:
    """Pending pairing request."""

    code: str
    qr_data: str
    expires_at: datetime
    device_name: Optional[str] = None


class DeviceAuthService:
    """
    Device authentication and pairing service.

    Manages the mesh network device registry.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        # Ensure data directory exists
        WIZARD_DATA.mkdir(parents=True, exist_ok=True)

        # Load devices
        self.devices: Dict[str, Device] = {}
        self._load_devices()

        # Active pairing requests
        self.pairing_requests: Dict[str, PairingRequest] = {}

        # Active sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}

        logger.info(
            f"[WIZ] DeviceAuthService initialized with {len(self.devices)} devices"
        )

    def _load_devices(self):
        """Load devices from persistent storage."""
        if DEVICES_FILE.exists():
            try:
                with open(DEVICES_FILE) as f:
                    data = json.load(f)
                    for device_data in data.get("devices", []):
                        device = Device.from_dict(device_data)
                        self.devices[device.id] = device
            except Exception as e:
                logger.error(f"[WIZ] Failed to load devices: {e}")

    def _save_devices(self):
        """Save devices to persistent storage."""
        try:
            data = {
                "devices": [d.to_dict() for d in self.devices.values()],
                "updated_at": datetime.now().isoformat(),
            }
            with open(DEVICES_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"[WIZ] Failed to save devices: {e}")

    # =========================================================================
    # Pairing
    # =========================================================================

    def create_pairing_request(self, ttl_minutes: int = 5) -> PairingRequest:
        """
        Create a new pairing request with code and QR data.

        Returns:
            PairingRequest with code and QR data
        """
        # Generate 8-character pairing code
        code = secrets.token_hex(4).upper()

        # Generate unique request ID
        request_id = secrets.token_urlsafe(16)

        # QR data contains the request ID and Wizard Server address
        qr_data = json.dumps(
            {
                "type": "udos-pair",
                "request_id": request_id,
                "code": code,
                "wizard": "localhost:8080",  # TODO: Get actual address
                "expires": (
                    datetime.now() + timedelta(minutes=ttl_minutes)
                ).isoformat(),
            }
        )

        request = PairingRequest(
            code=f"{code[:4]} {code[4:]}",  # Format: XXXX XXXX
            qr_data=qr_data,
            expires_at=datetime.now() + timedelta(minutes=ttl_minutes),
        )

        self.pairing_requests[code] = request

        logger.info(f"[WIZ] Created pairing request: {code[:4]}****")

        return request

    def complete_pairing(
        self,
        code: str,
        device_id: str,
        device_name: str,
        device_type: str = "desktop",
        public_key: str = "",
    ) -> Optional[Device]:
        """
        Complete device pairing with code.

        Args:
            code: Pairing code (with or without space)
            device_id: Unique device identifier
            device_name: Human-readable device name
            device_type: Type of device (desktop, mobile, tinycore)
            public_key: Device's public key for encryption

        Returns:
            Device if successful, None if code invalid/expired
        """
        # Normalize code
        code = code.replace(" ", "").upper()

        # Find matching request
        request = self.pairing_requests.get(code)
        if not request:
            logger.warning(f"[WIZ] Invalid pairing code: {code[:4]}****")
            return None

        # Check expiration
        if datetime.now() > request.expires_at:
            logger.warning(f"[WIZ] Expired pairing code: {code[:4]}****")
            del self.pairing_requests[code]
            return None

        # Create device
        device = Device(
            id=device_id,
            name=device_name,
            device_type=device_type,
            trust_level=TrustLevel.STANDARD,
            status=DeviceStatus.ONLINE,
            paired_at=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat(),
            public_key=public_key,
        )

        self.devices[device_id] = device
        self._save_devices()

        # Clean up pairing request
        del self.pairing_requests[code]

        logger.info(f"[WIZ] Device paired: {device_name} ({device_id})")

        return device

    # =========================================================================
    # Device Management
    # =========================================================================

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID."""
        return self.devices.get(device_id)

    def list_devices(self, status: Optional[str] = None) -> List[Device]:
        """
        List all devices, optionally filtered by status.

        Args:
            status: Filter by status (online, offline, all)

        Returns:
            List of devices
        """
        devices = list(self.devices.values())

        if status and status != "all":
            devices = [d for d in devices if d.status.value == status]

        return devices

    def update_device_status(self, device_id: str, status: DeviceStatus):
        """Update device connection status."""
        device = self.devices.get(device_id)
        if device:
            device.status = status
            device.last_seen = datetime.now().isoformat()
            self._save_devices()

    def update_device_sync(self, device_id: str, sync_version: int):
        """Update device sync version after successful sync."""
        device = self.devices.get(device_id)
        if device:
            device.last_sync = datetime.now().isoformat()
            device.sync_version = sync_version
            self._save_devices()

    def remove_device(self, device_id: str) -> bool:
        """Remove device from mesh."""
        if device_id in self.devices:
            device = self.devices[device_id]
            del self.devices[device_id]
            self._save_devices()
            logger.info(f"[WIZ] Device removed: {device.name} ({device_id})")
            return True
        return False

    # =========================================================================
    # Authentication
    # =========================================================================

    def authenticate(self, device_id: str, token: str) -> bool:
        """
        Authenticate a device request.

        Args:
            device_id: Device identifier
            token: Authentication token

        Returns:
            True if authenticated
        """
        device = self.devices.get(device_id)
        if not device:
            return False

        # TODO: Implement proper token validation
        # For now, just check device exists and update last_seen
        device.last_seen = datetime.now().isoformat()
        device.status = DeviceStatus.ONLINE

        return True

    def get_trust_level(self, device_id: str) -> TrustLevel:
        """Get device trust level."""
        device = self.devices.get(device_id)
        return device.trust_level if device else TrustLevel.GUEST


# Singleton accessor
_device_auth: Optional[DeviceAuthService] = None


def get_device_auth() -> DeviceAuthService:
    """Get device authentication service instance."""
    global _device_auth
    if _device_auth is None:
        _device_auth = DeviceAuthService()
    return _device_auth
