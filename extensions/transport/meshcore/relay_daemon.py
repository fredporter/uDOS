"""
MeshCore Relay Daemon

Maintains relay node registry and heartbeat tracking.
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RelayNode:
    relay_id: str
    name: str
    location: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    status: str = "offline"
    last_seen: Optional[str] = None
    created_at: Optional[str] = None


class MeshRelayDaemon:
    def __init__(self, data_dir: Optional[Path] = None) -> None:
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "meshcore"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.relays_path = self.data_dir / "relays.json"

    def register_relay(
        self, name: str, location: str, lat: Optional[float] = None, lon: Optional[float] = None
    ) -> RelayNode:
        relay = RelayNode(
            relay_id=f"relay-{secrets.token_hex(4)}",
            name=name,
            location=location,
            lat=lat,
            lon=lon,
            status="online",
            last_seen=self._now(),
            created_at=self._now(),
        )
        relays = self._load_relays()
        relays.append(relay)
        self._save_relays(relays)
        return relay

    def list_relays(self) -> List[RelayNode]:
        return self._load_relays()

    def get_relay(self, relay_id: str) -> Optional[RelayNode]:
        relays = self._load_relays()
        for relay in relays:
            if relay.relay_id == relay_id:
                return relay
        return None

    def heartbeat(self, relay_id: str) -> Optional[RelayNode]:
        relays = self._load_relays()
        for relay in relays:
            if relay.relay_id == relay_id:
                relay.status = "online"
                relay.last_seen = self._now()
                self._save_relays(relays)
                return relay
        return None

    def evaluate_status(self, relay_id: str) -> Optional[RelayNode]:
        relays = self._load_relays()
        for relay in relays:
            if relay.relay_id == relay_id:
                if relay.last_seen and self._is_stale(relay.last_seen):
                    relay.status = "offline"
                    self._save_relays(relays)
                return relay
        return None

    def _load_relays(self) -> List[RelayNode]:
        if not self.relays_path.exists():
            return []
        try:
            raw = json.loads(self.relays_path.read_text())
            return [RelayNode(**item) for item in raw]
        except Exception:
            return []

    def _save_relays(self, relays: List[RelayNode]) -> None:
        payload = [asdict(relay) for relay in relays]
        self.relays_path.write_text(json.dumps(payload, indent=2))

    def _now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _is_stale(self, iso_ts: str, minutes: int = 10) -> bool:
        try:
            ts = datetime.fromisoformat(iso_ts.replace("Z", ""))
        except Exception:
            return True
        return datetime.utcnow() - ts > timedelta(minutes=minutes)
