"""
Wizard Networking Service

Implements Wizard Networking Standard:
- Local pairing flow (QR/NFC)
- Ed25519 peering handshake
- WireGuard tunnel automation + key rotation
- RadioLink (MeshCore) integration hooks
"""

from __future__ import annotations

import base64
import json
import secrets
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
)

from wizard.services.path_utils import get_repo_root
from wizard.services.logging_manager import get_logger

logger = get_logger("wizard-networking")


DEFAULT_WIZARD_URL = "http://wizard.local"
DEFAULT_WIZARD_IP = "192.168.1.10"
DEFAULT_WG_LISTEN_PORT = 51820
DEFAULT_WG_INTERFACE_ADDR = "10.64.1.1/32"
DEFAULT_ALLOWED_IPS = ["10.64.2.0/24"]


@dataclass
class WizardIdentity:
    public_key: str
    private_key: str
    created_at: str


@dataclass
class PairingSession:
    token: str
    challenge: str
    channel: str
    created_at: str
    expires_at: str
    wizard_signature: str


@dataclass
class PeerRecord:
    peer_id: str
    name: str
    public_key: str
    paired_at: str
    last_seen: Optional[str] = None


@dataclass
class WireGuardPeer:
    peer_id: str
    wizard_private_key: str
    wizard_public_key: str
    peer_public_key: str
    interface_address: str
    listen_port: int
    allowed_ips: List[str]
    rotated_at: str


@dataclass
class RadioLinkState:
    enabled: bool
    last_started: Optional[str] = None
    last_stopped: Optional[str] = None


class WizardNetworkingService:
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        repo_root = get_repo_root()
        self.base_dir = base_dir or (repo_root / "memory" / "wizard" / "networking")
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.identity_path = self.base_dir / "identity.json"
        self.pairing_path = self.base_dir / "pairing.json"
        self.peers_path = self.base_dir / "peers.json"
        self.wireguard_path = self.base_dir / "wireguard.json"
        self.radiolink_path = self.base_dir / "radiolink.json"

        self.identity = self._load_identity()

    # ---------------------------------------------------------------------
    # Identity
    # ---------------------------------------------------------------------
    def _load_identity(self) -> WizardIdentity:
        if self.identity_path.exists():
            payload = json.loads(self.identity_path.read_text())
            return WizardIdentity(**payload)

        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        identity = WizardIdentity(
            public_key=self._b64(public_key.public_bytes_raw()),
            private_key=self._b64(private_key.private_bytes_raw()),
            created_at=self._now(),
        )
        self.identity_path.write_text(json.dumps(asdict(identity), indent=2))
        return identity

    def get_identity(self) -> Dict[str, Any]:
        return {
            "wizard_url": DEFAULT_WIZARD_URL,
            "wizard_ip": DEFAULT_WIZARD_IP,
            "public_key": self.identity.public_key,
            "created_at": self.identity.created_at,
        }

    # ---------------------------------------------------------------------
    # Pairing
    # ---------------------------------------------------------------------
    def start_pairing(self, channel: str = "qr") -> PairingSession:
        token = secrets.token_urlsafe(24)
        challenge = secrets.token_urlsafe(32)
        created_at = self._now()
        expires_at = self._iso_in_minutes(15)

        wizard_signature = self._sign_challenge(challenge)

        session = PairingSession(
            token=token,
            challenge=challenge,
            channel=channel,
            created_at=created_at,
            expires_at=expires_at,
            wizard_signature=wizard_signature,
        )

        payload = self._load_list(self.pairing_path)
        payload.append(asdict(session))
        self.pairing_path.write_text(json.dumps(payload, indent=2))
        return session

    def complete_pairing(
        self,
        token: str,
        peer_name: str,
        peer_public_key: str,
        signature: str,
    ) -> PeerRecord:
        sessions = self._load_list(self.pairing_path)
        session = next((s for s in sessions if s.get("token") == token), None)
        if not session:
            raise ValueError("Invalid pairing token")
        if self._is_expired(session.get("expires_at")):
            raise ValueError("Pairing token expired")

        challenge = session.get("challenge")
        if not self._verify_signature(peer_public_key, challenge, signature):
            raise ValueError("Invalid signature")

        peer_id = f"peer-{secrets.token_hex(6)}"
        peer = PeerRecord(
            peer_id=peer_id,
            name=peer_name,
            public_key=peer_public_key,
            paired_at=self._now(),
        )

        peers = self._load_list(self.peers_path)
        peers.append(asdict(peer))
        self.peers_path.write_text(json.dumps(peers, indent=2))

        # Remove token once used
        sessions = [s for s in sessions if s.get("token") != token]
        self.pairing_path.write_text(json.dumps(sessions, indent=2))

        return peer

    def list_peers(self) -> List[Dict[str, Any]]:
        return self._load_list(self.peers_path)

    def get_pairing_payload(self, session: PairingSession) -> Dict[str, Any]:
        return {
            "wizard_url": DEFAULT_WIZARD_URL,
            "wizard_ip": DEFAULT_WIZARD_IP,
            "wizard_public_key": self.identity.public_key,
            "pairing_token": session.token,
            "challenge": session.challenge,
            "wizard_signature": session.wizard_signature,
            "channel": session.channel,
            "expires_at": session.expires_at,
        }

    def create_peering_capsule(self, peer_id: str, ttl_minutes: int = 60) -> Dict[str, Any]:
        payload = {
            "peer_id": peer_id,
            "issued_at": self._now(),
            "expires_at": self._iso_in_minutes(ttl_minutes),
            "wizard_public_key": self.identity.public_key,
        }
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        private = Ed25519PrivateKey.from_private_bytes(self._b64d(self.identity.private_key))
        signature = private.sign(body)
        return {
            "payload": payload,
            "signature": self._b64(signature),
        }

    def verify_peering_capsule(self, capsule: Dict[str, Any]) -> bool:
        payload = capsule.get("payload")
        signature = capsule.get("signature")
        if not payload or not signature:
            return False
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        try:
            public = Ed25519PublicKey.from_public_bytes(self._b64d(payload["wizard_public_key"]))
            public.verify(self._b64d(signature), body)
        except Exception:
            return False
        return not self._is_expired(payload.get("expires_at"))

    # ---------------------------------------------------------------------
    # WireGuard
    # ---------------------------------------------------------------------
    def register_wireguard_peer(
        self, peer_id: str, peer_public_key: str, allowed_ips: Optional[List[str]] = None
    ) -> WireGuardPeer:
        allowed = allowed_ips or DEFAULT_ALLOWED_IPS
        wg_private = X25519PrivateKey.generate()
        wg_public = wg_private.public_key()
        record = WireGuardPeer(
            peer_id=peer_id,
            wizard_private_key=self._b64(wg_private.private_bytes_raw()),
            wizard_public_key=self._b64(wg_public.public_bytes_raw()),
            peer_public_key=peer_public_key,
            interface_address=DEFAULT_WG_INTERFACE_ADDR,
            listen_port=DEFAULT_WG_LISTEN_PORT,
            allowed_ips=allowed,
            rotated_at=self._now(),
        )

        data = self._load_dict(self.wireguard_path)
        data[peer_id] = asdict(record)
        self.wireguard_path.write_text(json.dumps(data, indent=2))
        return record

    def rotate_wireguard_keys(self, peer_id: str) -> WireGuardPeer:
        data = self._load_dict(self.wireguard_path)
        existing = data.get(peer_id)
        if not existing:
            raise ValueError("WireGuard peer not found")

        peer_public_key = existing.get("peer_public_key")
        allowed_ips = existing.get("allowed_ips", DEFAULT_ALLOWED_IPS)
        return self.register_wireguard_peer(peer_id, peer_public_key, allowed_ips)

    def get_wireguard_config(self, peer_id: str) -> str:
        data = self._load_dict(self.wireguard_path)
        record = data.get(peer_id)
        if not record:
            raise ValueError("WireGuard peer not found")

        return (
            "[Interface]\n"
            f"Address = {record['interface_address']}\n"
            f"ListenPort = {record['listen_port']}\n"
            f"PrivateKey = {record['wizard_private_key']}\n\n"
            "[Peer]\n"
            f"PublicKey = {record['peer_public_key']}\n"
            f"AllowedIPs = {', '.join(record['allowed_ips'])}\n"
        )

    # ---------------------------------------------------------------------
    # RadioLink (MeshCore)
    # ---------------------------------------------------------------------
    def radiolink_status(self) -> Dict[str, Any]:
        state = self._load_radiolink_state()
        transport_available = False
        try:
            from extensions.transport.meshcore import get_mesh_transport

            transport_available = get_mesh_transport() is not None
        except Exception:
            transport_available = False

        return {
            "enabled": state.enabled,
            "transport_available": transport_available,
            "last_started": state.last_started,
            "last_stopped": state.last_stopped,
        }

    def radiolink_start(self) -> Dict[str, Any]:
        state = self._load_radiolink_state()
        state.enabled = True
        state.last_started = self._now()
        self._save_radiolink_state(state)
        return self.radiolink_status()

    def radiolink_stop(self) -> Dict[str, Any]:
        state = self._load_radiolink_state()
        state.enabled = False
        state.last_stopped = self._now()
        self._save_radiolink_state(state)
        return self.radiolink_status()

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _load_list(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text())
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _load_dict(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text())
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _load_radiolink_state(self) -> RadioLinkState:
        if self.radiolink_path.exists():
            payload = json.loads(self.radiolink_path.read_text())
            return RadioLinkState(**payload)
        state = RadioLinkState(enabled=False)
        self._save_radiolink_state(state)
        return state

    def _save_radiolink_state(self, state: RadioLinkState) -> None:
        self.radiolink_path.write_text(json.dumps(asdict(state), indent=2))

    def _sign_challenge(self, challenge: str) -> str:
        private = Ed25519PrivateKey.from_private_bytes(self._b64d(self.identity.private_key))
        signature = private.sign(challenge.encode("utf-8"))
        return self._b64(signature)

    def _verify_signature(self, public_key_b64: str, challenge: str, signature_b64: str) -> bool:
        try:
            public = Ed25519PublicKey.from_public_bytes(self._b64d(public_key_b64))
            public.verify(self._b64d(signature_b64), challenge.encode("utf-8"))
            return True
        except Exception:
            return False

    def _b64(self, raw: bytes) -> str:
        return base64.b64encode(raw).decode("utf-8")

    def _b64d(self, b64: str) -> bytes:
        return base64.b64decode(b64.encode("utf-8"))

    def _now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _iso_in_minutes(self, minutes: int) -> str:
        return (datetime.utcnow() + timedelta(minutes=minutes)).isoformat() + "Z"

    def _is_expired(self, iso_ts: Optional[str]) -> bool:
        if not iso_ts:
            return True
        try:
            expires = datetime.fromisoformat(iso_ts.replace("Z", ""))
            return datetime.utcnow() > expires
        except Exception:
            return True


_networking_service: Optional[WizardNetworkingService] = None


def get_wizard_networking_service() -> WizardNetworkingService:
    global _networking_service
    if _networking_service is None:
        _networking_service = WizardNetworkingService()
    return _networking_service
