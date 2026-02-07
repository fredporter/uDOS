"""
Anchor Runtime Stub (Core)

Minimal runtime for GAME:NETHACK with event log scaffolding.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.services.anchor_store import AnchorStore
from core.services.anchor_validation import is_valid_locid


@dataclass
class StubInstance:
    instance_id: str
    anchor_id: str
    created_at: str
    updated_at: str
    meta: Dict[str, Any]


class NethackAnchorRuntime:
    """Minimal GAME:NETHACK runtime stub."""

    def __init__(self, store: Optional[AnchorStore] = None):
        self.store = store or AnchorStore()
        self.anchor_id = "GAME:NETHACK"
        self.instances: Dict[str, StubInstance] = {}
        self.event_log: List[Dict[str, Any]] = []

    def meta(self) -> Dict[str, Any]:
        return {
            "id": self.anchor_id,
            "title": "NetHack (stub)",
            "description": "Minimal anchor runtime stub (no real game IO).",
            "capabilities": {
                "terminal": True,
                "framebuffer": False,
                "tiles": False,
                "saveState": False,
                "deterministicSeed": True,
                "questEvents": True,
                "locidReverseLookup": False,
                "networkAllowed": False,
            },
        }

    def create_instance(self, seed: Optional[str] = None) -> StubInstance:
        instance_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        instance = StubInstance(
            instance_id=instance_id,
            anchor_id=self.anchor_id,
            created_at=now,
            updated_at=now,
            meta={"seed": seed} if seed else {},
        )
        self.instances[instance_id] = instance
        self.store.create_instance(anchor_id=self.anchor_id, seed=seed)
        return instance

    def destroy_instance(self, instance_id: str) -> None:
        self.instances.pop(instance_id, None)
        self.store.destroy_instance(instance_id)

    def emit_event(self, instance_id: str, event_type: str, locid: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
        if locid and not is_valid_locid(locid):
            locid = None
        event = {
            "ts": int(datetime.utcnow().timestamp() * 1000),
            "anchor_id": self.anchor_id,
            "instance_id": instance_id,
            "type": event_type,
            "locid": locid,
            "data": data or {},
        }
        self.event_log.append(event)
        return self.store.add_event(
            anchor_id=self.anchor_id,
            instance_id=instance_id,
            event_type=event_type,
            locid=locid,
            data_payload=data,
        )
