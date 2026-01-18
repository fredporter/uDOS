"""
Node Discovery Service
======================

Handles discovery and pairing of uDOS nodes in the mesh network.

Discovery Methods:
1. QR Code - Visual pairing with code scan
2. Manual Code - 8-character pairing code
3. Bluetooth Beacon - Nearby device discovery (signal only)
4. mDNS/Bonjour - Local network discovery (when enabled)
5. NFC - Physical tap to pair

Trust Model:
- Pending: Awaiting approval
- Guest: Limited read-only access
- Standard: Full mesh participant
- Admin: Can manage other devices

Version: v1.0.0.0
Date: 2026-01-06
"""

import json
import secrets
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import threading

from core.services.logging_manager import get_logger

logger = get_logger("node-discovery")


class DiscoveryMethod(Enum):
    """Methods for discovering other nodes."""

    QR_CODE = "qr"
    MANUAL_CODE = "code"
    BLUETOOTH = "bluetooth"
    MDNS = "mdns"
    NFC = "nfc"
    DIRECT = "direct"  # Known address


class PairingState(Enum):
    """States of the pairing process."""

    IDLE = "idle"
    ADVERTISING = "advertising"  # Broadcasting presence
    SCANNING = "scanning"  # Looking for devices
    PAIRING = "pairing"  # Active pairing handshake
    CONFIRMING = "confirming"  # Awaiting user confirmation
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class DiscoveredNode:
    """A discovered node in the network."""

    node_id: str
    name: str
    device_type: str
    discovery_method: DiscoveryMethod
    address: Optional[str] = None  # IP, BT address, etc.
    signal_strength: int = 0  # For wireless discovery
    discovered_at: str = ""
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["discovery_method"] = self.discovery_method.value
        return d


@dataclass
class PairingSession:
    """Active pairing session."""

    session_id: str
    local_node_id: str
    remote_node_id: Optional[str] = None
    method: DiscoveryMethod = DiscoveryMethod.QR_CODE
    state: PairingState = PairingState.IDLE
    pairing_code: str = ""
    qr_data: str = ""
    expires_at: Optional[datetime] = None
    public_key_local: str = ""
    public_key_remote: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["method"] = self.method.value
        d["state"] = self.state.value
        d["expires_at"] = self.expires_at.isoformat() if self.expires_at else None
        return d


class NodeDiscoveryService:
    """
    Node discovery and pairing orchestration.

    Coordinates discovery across multiple transport methods
    and manages the pairing handshake.
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

        # Local node identity
        self.local_node_id: str = self._get_or_create_node_id()
        self.local_node_name: str = "uDOS Node"

        # Discovery state
        self.discovered_nodes: Dict[str, DiscoveredNode] = {}
        self.active_sessions: Dict[str, PairingSession] = {}

        # Callbacks
        self._on_node_discovered: List[Callable] = []
        self._on_pairing_complete: List[Callable] = []
        self._on_pairing_request: List[Callable] = []

        # Scanning state
        self._scanning = False
        self._advertising = False

        logger.info(f"[MESH] NodeDiscovery initialized: {self.local_node_id}")

    def _get_or_create_node_id(self) -> str:
        """Get or create persistent node ID."""
        node_file = (
            Path(__file__).parent.parent.parent.parent / "memory" / "mesh" / "node_id"
        )
        node_file.parent.mkdir(parents=True, exist_ok=True)

        if node_file.exists():
            return node_file.read_text().strip()

        node_id = f"node-{secrets.token_hex(8)}"
        node_file.write_text(node_id)
        return node_id

    # =========================================================================
    # Discovery
    # =========================================================================

    async def start_scanning(self, methods: Optional[List[DiscoveryMethod]] = None):
        """
        Start scanning for nearby nodes.

        Args:
            methods: Discovery methods to use (default: all available)
        """
        if self._scanning:
            return

        self._scanning = True
        methods = methods or [DiscoveryMethod.BLUETOOTH, DiscoveryMethod.MDNS]

        logger.info(f"[MESH] Starting node scan via {[m.value for m in methods]}")

        # Start discovery on each method
        tasks = []
        if DiscoveryMethod.BLUETOOTH in methods:
            tasks.append(self._scan_bluetooth())
        if DiscoveryMethod.MDNS in methods:
            tasks.append(self._scan_mdns())

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_scanning(self):
        """Stop active node scanning."""
        self._scanning = False
        logger.info("[MESH] Node scan stopped")

    async def _scan_bluetooth(self):
        """Scan for nodes via Bluetooth."""
        # This would integrate with the Bluetooth transport
        # For now, placeholder
        logger.debug("[MESH] Bluetooth scan started")
        while self._scanning:
            await asyncio.sleep(5)
            # Check for Bluetooth beacons

    async def _scan_mdns(self):
        """Scan for nodes via mDNS/Bonjour."""
        # This would use zeroconf library
        # For now, placeholder
        logger.debug("[MESH] mDNS scan started")
        while self._scanning:
            await asyncio.sleep(10)
            # Query _udos._tcp.local

    def add_discovered_node(self, node: DiscoveredNode):
        """Add a discovered node to the list."""
        self.discovered_nodes[node.node_id] = node

        logger.info(
            f"[MESH] Node discovered: {node.name} ({node.node_id}) via {node.discovery_method.value}"
        )

        # Notify callbacks
        for callback in self._on_node_discovered:
            try:
                callback(node)
            except Exception as e:
                logger.error(f"[MESH] Discovery callback error: {e}")

    # =========================================================================
    # Pairing
    # =========================================================================

    def create_pairing_session(
        self, method: DiscoveryMethod = DiscoveryMethod.QR_CODE, ttl_minutes: int = 5
    ) -> PairingSession:
        """
        Create a new pairing session.

        Args:
            method: Pairing method to use
            ttl_minutes: Session timeout

        Returns:
            New pairing session with code/QR data
        """
        session_id = secrets.token_urlsafe(12)
        pairing_code = secrets.token_hex(4).upper()

        # Generate QR data
        qr_data = json.dumps(
            {
                "type": "udos-pair",
                "version": 1,
                "session_id": session_id,
                "node_id": self.local_node_id,
                "node_name": self.local_node_name,
                "code": pairing_code,
                "expires": (
                    datetime.now() + timedelta(minutes=ttl_minutes)
                ).isoformat(),
            }
        )

        session = PairingSession(
            session_id=session_id,
            local_node_id=self.local_node_id,
            method=method,
            state=PairingState.ADVERTISING,
            pairing_code=f"{pairing_code[:4]} {pairing_code[4:]}",
            qr_data=qr_data,
            expires_at=datetime.now() + timedelta(minutes=ttl_minutes),
        )

        self.active_sessions[session_id] = session

        logger.info(f"[MESH] Pairing session created: {session_id}")

        return session

    async def initiate_pairing(
        self, target_node: DiscoveredNode, method: Optional[DiscoveryMethod] = None
    ) -> PairingSession:
        """
        Initiate pairing with a discovered node.

        Args:
            target_node: Node to pair with
            method: Override discovery method

        Returns:
            Active pairing session
        """
        session = self.create_pairing_session(
            method=method or target_node.discovery_method
        )
        session.remote_node_id = target_node.node_id
        session.state = PairingState.PAIRING

        logger.info(f"[MESH] Initiating pairing with {target_node.name}")

        # Send pairing request via transport
        await self._send_pairing_request(session, target_node)

        return session

    async def respond_to_pairing(
        self, session_id: str, approve: bool, trust_level: str = "standard"
    ) -> bool:
        """
        Respond to an incoming pairing request.

        Args:
            session_id: Session to respond to
            approve: Whether to approve pairing
            trust_level: Trust level to assign

        Returns:
            True if pairing completed
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return False

        if approve:
            session.state = PairingState.COMPLETE

            # Register device with auth service
            from wizard.services.device_auth import get_device_auth, TrustLevel

            auth = get_device_auth()

            trust = TrustLevel.STANDARD
            if trust_level == "admin":
                trust = TrustLevel.ADMIN
            elif trust_level == "guest":
                trust = TrustLevel.GUEST

            # Create device entry
            device = auth.complete_pairing(
                code=session.pairing_code.replace(" ", ""),
                device_id=session.remote_node_id,
                device_name=f"Node {session.remote_node_id[:8]}",
                device_type="mesh",
            )

            if device:
                logger.info(f"[MESH] Pairing approved: {session.remote_node_id}")

                # Notify callbacks
                for callback in self._on_pairing_complete:
                    try:
                        callback(session, device)
                    except Exception as e:
                        logger.error(f"[MESH] Pairing callback error: {e}")

                return True
        else:
            session.state = PairingState.FAILED
            logger.info(f"[MESH] Pairing rejected: {session.remote_node_id}")

        return False

    async def _send_pairing_request(
        self, session: PairingSession, target: DiscoveredNode
    ):
        """Send pairing request to target node."""
        # Would use the appropriate transport based on discovery method
        logger.debug(f"[MESH] Sending pairing request to {target.node_id}")

        # For now, just update state
        session.state = PairingState.CONFIRMING

    def verify_pairing_code(self, code: str) -> Optional[PairingSession]:
        """
        Verify a pairing code entered manually.

        Args:
            code: Pairing code (with or without space)

        Returns:
            Matching session if valid
        """
        code = code.replace(" ", "").upper()

        for session in self.active_sessions.values():
            if session.pairing_code.replace(" ", "") == code:
                if session.expires_at and datetime.now() > session.expires_at:
                    return None  # Expired
                return session

        return None

    # =========================================================================
    # Advertising
    # =========================================================================

    async def start_advertising(self, methods: Optional[List[DiscoveryMethod]] = None):
        """
        Start advertising this node for discovery.

        Args:
            methods: Methods to advertise on
        """
        if self._advertising:
            return

        self._advertising = True
        methods = methods or [DiscoveryMethod.BLUETOOTH]

        logger.info(
            f"[MESH] Starting node advertising via {[m.value for m in methods]}"
        )

        if DiscoveryMethod.BLUETOOTH in methods:
            await self._advertise_bluetooth()

    async def stop_advertising(self):
        """Stop advertising."""
        self._advertising = False
        logger.info("[MESH] Node advertising stopped")

    async def _advertise_bluetooth(self):
        """Advertise via Bluetooth beacon."""
        # Would integrate with Bluetooth transport
        while self._advertising:
            # Broadcast beacon (signal only, no data per policy)
            await asyncio.sleep(2)

    # =========================================================================
    # Callbacks
    # =========================================================================

    def on_node_discovered(self, callback: Callable[[DiscoveredNode], None]):
        """Register callback for node discovery."""
        self._on_node_discovered.append(callback)

    def on_pairing_complete(self, callback: Callable):
        """Register callback for successful pairing."""
        self._on_pairing_complete.append(callback)

    def on_pairing_request(self, callback: Callable):
        """Register callback for incoming pairing requests."""
        self._on_pairing_request.append(callback)

    # =========================================================================
    # Status
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get discovery service status."""
        return {
            "local_node_id": self.local_node_id,
            "local_node_name": self.local_node_name,
            "scanning": self._scanning,
            "advertising": self._advertising,
            "discovered_nodes": len(self.discovered_nodes),
            "active_sessions": len(self.active_sessions),
        }


# Singleton accessor
_discovery: Optional[NodeDiscoveryService] = None


def get_node_discovery() -> NodeDiscoveryService:
    """Get node discovery service instance."""
    global _discovery
    if _discovery is None:
        _discovery = NodeDiscoveryService()
    return _discovery
