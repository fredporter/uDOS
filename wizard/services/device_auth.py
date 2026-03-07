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

import json
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import threading

from core.services.time_utils import utc_now, utc_now_iso_z
from wizard.services.logging_api import get_logger
from wizard.services.deploy_mode import is_managed_mode
from wizard.services.store import get_wizard_store
from wizard.services.store.base import WizardStore

logger = get_logger("wizard", category="device-auth", name="device-auth")

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
    device_type: str  # desktop, mobile, alpine
    trust_level: TrustLevel = TrustLevel.STANDARD
    status: DeviceStatus = DeviceStatus.OFFLINE
    transport: str = "meshcore"
    paired_at: str = ""
    last_seen: str = ""
    last_sync: str = ""
    sync_version: int = 0
    public_key: str = ""
    token_hash: str = ""
    token_last_rotated_at: str = ""

    def to_dict(self, *, include_sensitive: bool = False) -> Dict[str, Any]:
        d = asdict(self)
        d["trust_level"] = self.trust_level.value
        d["status"] = self.status.value
        if not include_sensitive:
            d.pop("token_hash", None)
            d.pop("token_last_rotated_at", None)
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

    def __init__(self, *, store: WizardStore | None = None):
        self._managed = is_managed_mode()
        self.store = store or get_wizard_store()

        if not self._managed:
            WIZARD_DATA.mkdir(parents=True, exist_ok=True)

        # Load devices
        self.devices: Dict[str, Device] = {}
        self._load_devices()

        # Active pairing requests
        self.pairing_requests: Dict[str, PairingRequest] = {}

        # Active sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}

        logger.info(
            "[WIZ] DeviceAuthService initialized with %s devices",
            len(self.devices),
        )

    def _load_devices(self):
        """Load devices from persistent storage."""
        if self._managed:
            try:
                for device_data in self.store.list_device_records():
                    device = Device.from_dict(device_data)
                    self.devices[device.id] = device
            except Exception as e:
                logger.error("[WIZ] Failed to load managed devices: %s", e)
            return
        if DEVICES_FILE.exists():
            try:
                with open(DEVICES_FILE) as f:
                    data = json.load(f)
                    for device_data in data.get("devices", []):
                        device = Device.from_dict(device_data)
                        self.devices[device.id] = device
            except Exception as e:
                logger.error("[WIZ] Failed to load devices: %s", e)

    def _save_devices(self):
        """Save devices to persistent storage."""
        if self._managed:
            try:
                for device in self.devices.values():
                    self.store.upsert_device_record(
                        device.to_dict(include_sensitive=True)
                    )
            except Exception as e:
                logger.error("[WIZ] Failed to save managed devices: %s", e)
            return
        try:
            data = {
                "devices": [
                    d.to_dict(include_sensitive=True) for d in self.devices.values()
                ],
                "updated_at": utc_now_iso_z(),
            }
            with open(DEVICES_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("[WIZ] Failed to save devices: %s", e)

    def _persist_device(self, device: Device) -> None:
        if self._managed:
            try:
                self.store.upsert_device_record(device.to_dict(include_sensitive=True))
                return
            except Exception as e:
                logger.error("[WIZ] Failed to persist managed device %s: %s", device.id, e)
        self._save_devices()

    def _delete_device(self, device_id: str) -> None:
        if self._managed:
            try:
                self.store.delete_device_record(device_id)
                return
            except Exception as e:
                logger.error("[WIZ] Failed to delete managed device %s: %s", device_id, e)
        self._save_devices()

    def _hash_device_secret(self, secret: str) -> str:
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    def _issue_device_token(self, device: Device) -> str:
        secret = secrets.token_urlsafe(32)
        now = utc_now_iso_z()
        device.token_hash = self._hash_device_secret(secret)
        device.token_last_rotated_at = now
        self._persist_device(device)
        return f"{device.id}:{secret}"

    # =========================================================================
    # Pairing
    # =========================================================================

    def create_pairing_request(
        self, ttl_minutes: int = 5, wizard_address: Optional[str] = None
    ) -> PairingRequest:
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
                "wizard": wizard_address or "127.0.0.1:8080",
                "expires": (
                    utc_now() + timedelta(minutes=ttl_minutes)
                ).isoformat(),
            }
        )

        request = PairingRequest(
            code=f"{code[:4]} {code[4:]}",  # Format: XXXX XXXX
            qr_data=qr_data,
            expires_at=utc_now() + timedelta(minutes=ttl_minutes),
        )

        self.pairing_requests[code] = request

        logger.info("[WIZ] Created pairing request: %s****", code[:4])

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
            device_type: Type of device (desktop, mobile, alpine)
            public_key: Device's public key for encryption

        Returns:
            Device if successful, None if code invalid/expired
        """
        # Normalize code
        code = code.replace(" ", "").upper()

        # Find matching request
        request = self.pairing_requests.get(code)
        if not request:
            logger.warning("[WIZ] Invalid pairing code: %s****", code[:4])
            return None

        # Check expiration
        if utc_now() > request.expires_at:
            logger.warning("[WIZ] Expired pairing code: %s****", code[:4])
            del self.pairing_requests[code]
            return None

        # Create device
        device = Device(
            id=device_id,
            name=device_name,
            device_type=device_type,
            trust_level=TrustLevel.STANDARD,
            status=DeviceStatus.ONLINE,
            paired_at=utc_now_iso_z(),
            last_seen=utc_now_iso_z(),
            public_key=public_key,
        )

        self.devices[device_id] = device
        self._persist_device(device)

        # Clean up pairing request
        del self.pairing_requests[code]

        logger.info("[WIZ] Device paired: %s (%s)", device_name, device_id)

        return device

    def rotate_device_token(self, device_id: str) -> Optional[str]:
        device = self.devices.get(device_id)
        if not device:
            return None
        return self._issue_device_token(device)

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
            device.last_seen = utc_now_iso_z()
            self._persist_device(device)

    def update_device_sync(self, device_id: str, sync_version: int):
        """Update device sync version after successful sync."""
        device = self.devices.get(device_id)
        if device:
            device.last_sync = utc_now_iso_z()
            device.sync_version = sync_version
            self._persist_device(device)

    def remove_device(self, device_id: str) -> bool:
        """Remove device from mesh."""
        if device_id in self.devices:
            device = self.devices[device_id]
            del self.devices[device_id]
            self._delete_device(device_id)
            logger.info("[WIZ] Device removed: %s (%s)", device.name, device_id)
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

        if not token or ":" not in token:
            return False
        token_device_id, secret = token.split(":", 1)
        if token_device_id != device_id or not secret or not device.token_hash:
            return False
        if not hmac.compare_digest(
            device.token_hash,
            self._hash_device_secret(secret),
        ):
            return False

        device.last_seen = utc_now_iso_z()
        device.status = DeviceStatus.ONLINE
        self._persist_device(device)

        return True

    def authenticate_bearer_token(self, token: str) -> Optional[Device]:
        if not token or ":" not in token:
            return None
        device_id = token.split(":", 1)[0].strip()
        if not device_id or not self.authenticate(device_id, token):
            return None
        return self.devices.get(device_id)

    def get_trust_level(self, device_id: str) -> TrustLevel:
        """Get device trust level."""
        device = self.devices.get(device_id)
        return device.trust_level if device else TrustLevel.GUEST


# Singleton accessor
_device_auth: Optional[DeviceAuthService] = None
_device_auth_lock = threading.Lock()


def get_device_auth() -> DeviceAuthService:
    """Get device authentication service instance."""
    global _device_auth
    if _device_auth is None:
        with _device_auth_lock:
            if _device_auth is None:
                _device_auth = DeviceAuthService()
    return _device_auth
