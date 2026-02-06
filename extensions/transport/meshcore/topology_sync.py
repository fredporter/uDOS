"""
MeshCore Topology Sync Service

Creates snapshots of relay + device topology for monitoring and coverage planning.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from extensions.transport.meshcore.device_registry import get_device_registry
from extensions.transport.meshcore.relay_daemon import MeshRelayDaemon


@dataclass
class TopologySnapshot:
    nodes: List[Dict[str, object]]
    edges: List[Dict[str, object]]
    updated_at: str


class TopologySyncService:
    def __init__(self, data_dir: Optional[Path] = None) -> None:
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "meshcore"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.topology_path = self.data_dir / "topology.json"
        self.relay_daemon = MeshRelayDaemon(self.data_dir)

    def build_snapshot(self) -> TopologySnapshot:
        device_registry = get_device_registry()
        devices = device_registry.list_devices() if device_registry else []
        relays = self.relay_daemon.list_relays()

        nodes: List[Dict[str, object]] = []
        edges: List[Dict[str, object]] = []

        for relay in relays:
            nodes.append(
                {
                    "id": relay.relay_id,
                    "name": relay.name,
                    "type": "relay",
                    "status": relay.status,
                    "location": relay.location,
                    "lat": relay.lat,
                    "lon": relay.lon,
                    "last_seen": relay.last_seen,
                }
            )

        for device in devices:
            nodes.append(
                {
                    "id": device.device_id,
                    "name": device.name,
                    "type": "device",
                    "status": device.status.value if hasattr(device.status, "value") else device.status,
                    "last_seen": device.last_seen,
                }
            )

        # Basic edges: attach each device to the most recent relay (placeholder policy)
        if relays:
            anchor = relays[0].relay_id
            for device in devices:
                edges.append(
                    {
                        "from": device.device_id,
                        "to": anchor,
                        "type": "uplink",
                    }
                )

        snapshot = TopologySnapshot(nodes=nodes, edges=edges, updated_at=self._now())
        self._save_snapshot(snapshot)
        return snapshot

    def get_snapshot(self) -> TopologySnapshot:
        if not self.topology_path.exists():
            return self.build_snapshot()
        try:
            payload = json.loads(self.topology_path.read_text())
            return TopologySnapshot(**payload)
        except Exception:
            return self.build_snapshot()

    def _save_snapshot(self, snapshot: TopologySnapshot) -> None:
        self.topology_path.write_text(json.dumps(asdict(snapshot), indent=2))

    def _now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"
