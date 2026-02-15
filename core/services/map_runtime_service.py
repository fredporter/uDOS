"""Map runtime service for deterministic traversal and map action events."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from core.services.chunking_contract import describe_chunk_shape, derive_chunk2d_id
from core.services.logging_api import get_repo_root


class MapRuntimeService:
    """Owns deterministic 2D traversal loop and emits canonical map events."""

    def __init__(
        self,
        *,
        seed_file: Optional[Path] = None,
        state_file: Optional[Path] = None,
        events_file: Optional[Path] = None,
    ) -> None:
        repo_root = get_repo_root()
        self.seed_file = seed_file or repo_root / "core" / "src" / "spatial" / "locations-seed.default.json"
        private_root = repo_root / "memory" / "bank" / "private"
        private_root.mkdir(parents=True, exist_ok=True)
        self.state_file = state_file or private_root / "map_runtime_state.json"
        self.events_file = events_file or private_root / "gameplay_events.ndjson"

        self._places = self._load_places()
        self._state = self._load_state()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_places(self) -> Dict[str, Dict[str, Any]]:
        try:
            raw = json.loads(self.seed_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
        out: Dict[str, Dict[str, Any]] = {}
        for row in raw.get("locations", []):
            if not isinstance(row, dict):
                continue
            place_id = str(row.get("placeId") or "").strip()
            if not place_id:
                continue
            out[place_id] = row
        return out

    def _default_state(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "updated_at": self._now_iso(),
            "users": {},
        }

    def _load_state(self) -> Dict[str, Any]:
        if not self.state_file.exists():
            state = self._default_state()
            self._write_state(state)
            return state
        try:
            parsed = json.loads(self.state_file.read_text(encoding="utf-8"))
            if not isinstance(parsed, dict):
                raise ValueError("state file is not an object")
            state = self._default_state()
            state.update({k: v for k, v in parsed.items() if k in {"version", "updated_at"}})
            users = parsed.get("users")
            if isinstance(users, dict):
                state["users"] = users
            return state
        except Exception:
            state = self._default_state()
            self._write_state(state)
            return state

    def _write_state(self, state: Dict[str, Any]) -> None:
        self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def _save(self) -> None:
        self._state["updated_at"] = self._now_iso()
        self._write_state(self._state)

    def _default_place_id(self) -> Optional[str]:
        if not self._places:
            return None
        return sorted(self._places.keys())[0]

    def _ensure_user(self, username: str) -> Dict[str, Any]:
        users = self._state.setdefault("users", {})
        row = users.get(username)
        if not isinstance(row, dict):
            row = {
                "current_place_id": self._default_place_id(),
                "tick_counter": 0,
                "npc_phase": 0,
                "world_phase": 0,
                "updated_at": self._now_iso(),
            }
            users[username] = row
        row.setdefault("current_place_id", self._default_place_id())
        row.setdefault("tick_counter", 0)
        row.setdefault("npc_phase", 0)
        row.setdefault("world_phase", 0)
        row.setdefault("updated_at", self._now_iso())
        return row

    def _place(self, place_id: str) -> Optional[Dict[str, Any]]:
        row = self._places.get(str(place_id or "").strip())
        return deepcopy(row) if isinstance(row, dict) else None

    def _event_payload_location(self, place: Dict[str, Any]) -> Dict[str, Any]:
        place_ref = str(place.get("placeRef") or "")
        return {
            "grid_id": place_ref,
            "x": None,
            "y": None,
            "z": int(place.get("z", 0) or 0),
        }

    def _append_event(self, username: str, event_type: str, payload: Dict[str, Any]) -> None:
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "ts": self._now_iso(),
            "source": "core:map-runtime",
            "username": username,
            "type": event_type,
            "payload": payload,
        }
        with self.events_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")

    def _chunk_meta(self, place: Dict[str, Any]) -> Dict[str, Any]:
        place_ref = str(place.get("placeRef") or "")
        parsed = describe_chunk_shape(place_ref) or {}
        metadata = place.get("metadata") if isinstance(place.get("metadata"), dict) else {}
        return {
            "chunk2d_id": metadata.get("chunk") or derive_chunk2d_id(place_ref),
            "shape": parsed.get("reserved3d", {}),
        }

    def status(self, username: str) -> Dict[str, Any]:
        user = self._ensure_user(username)
        current_place = self._place(str(user.get("current_place_id") or ""))
        if not current_place:
            return {
                "ok": False,
                "error": "No map seed places available",
            }
        chunk_meta = self._chunk_meta(current_place)
        return {
            "ok": True,
            "current_place_id": current_place.get("placeId"),
            "label": current_place.get("label"),
            "place_ref": current_place.get("placeRef"),
            "z": int(current_place.get("z", 0) or 0),
            "links": list(current_place.get("links", [])),
            "portals": list(current_place.get("portals", [])),
            "interaction_points": list(current_place.get("interaction_points", [])),
            "quest_ids": list(current_place.get("quest_ids", [])),
            "hazards": list(current_place.get("hazards", [])),
            "chunk": chunk_meta,
            "tick_counter": int(user.get("tick_counter", 0) or 0),
            "npc_phase": int(user.get("npc_phase", 0) or 0),
            "world_phase": int(user.get("world_phase", 0) or 0),
        }

    def enter(self, username: str, place_id: str) -> Dict[str, Any]:
        user = self._ensure_user(username)
        target = self._place(place_id)
        if not target:
            return {"ok": False, "error": f"Unknown place: {place_id}"}

        user["current_place_id"] = target.get("placeId")
        user["updated_at"] = self._now_iso()
        self._save()

        payload = {
            "action": "ENTER",
            "place_id": target.get("placeId"),
            "place_ref": target.get("placeRef"),
            "chunk2d_id": self._chunk_meta(target).get("chunk2d_id"),
            "location": self._event_payload_location(target),
        }
        self._append_event(username, "MAP_ENTER", payload)
        return {"ok": True, "action": "ENTER", "place": target}

    def move(self, username: str, target_place_id: str) -> Dict[str, Any]:
        user = self._ensure_user(username)
        current = self._place(str(user.get("current_place_id") or ""))
        target = self._place(target_place_id)
        if not current or not target:
            return {"ok": False, "error": "Current/target place is unavailable"}

        current_id = str(current.get("placeId") or "")
        target_id = str(target.get("placeId") or "")
        links = {str(x) for x in current.get("links", [])}
        if target_id not in links:
            return {
                "ok": False,
                "error": f"Blocked edge: {current_id} -> {target_id} is not linked",
                "blocked": "edge",
            }

        current_z = int(current.get("z", 0) or 0)
        target_z = int(target.get("z", 0) or 0)
        z_delta = abs(target_z - current_z)
        requires_portal = z_delta >= 2
        current_portals = list(current.get("portals", []))
        target_portals = list(target.get("portals", []))
        if requires_portal and not current_portals and not target_portals:
            return {
                "ok": False,
                "error": "Blocked traversal: portal transition required for vertical move",
                "blocked": "portal",
            }

        terrain_cost = 1 + len(list(target.get("hazards", []))) + max(0, z_delta - 1)
        mode = "portal" if requires_portal else "walk"

        user["current_place_id"] = target_id
        user["updated_at"] = self._now_iso()
        self._save()

        payload = {
            "action": "ENTER",
            "from_place_id": current_id,
            "to_place_id": target_id,
            "from_place_ref": current.get("placeRef"),
            "to_place_ref": target.get("placeRef"),
            "terrain_cost": int(terrain_cost),
            "mode": mode,
            "z_delta": int(z_delta),
            "chunk2d_id": self._chunk_meta(target).get("chunk2d_id"),
            "location": self._event_payload_location(target),
        }
        self._append_event(username, "MAP_TRAVERSE", payload)
        return {"ok": True, "action": "MOVE", "mode": mode, "terrain_cost": terrain_cost, "place": target}

    def inspect(self, username: str) -> Dict[str, Any]:
        user = self._ensure_user(username)
        current = self._place(str(user.get("current_place_id") or ""))
        if not current:
            return {"ok": False, "error": "No current place"}
        payload = {
            "action": "INSPECT",
            "place_id": current.get("placeId"),
            "place_ref": current.get("placeRef"),
            "interaction_points": list(current.get("interaction_points", [])),
            "npc_spawn": list(current.get("npc_spawn", [])),
            "hazards": list(current.get("hazards", [])),
            "location": self._event_payload_location(current),
        }
        self._append_event(username, "MAP_INSPECT", payload)
        return {
            "ok": True,
            "action": "INSPECT",
            "place": current,
            "inspection": {
                "interaction_points": payload["interaction_points"],
                "npc_spawn": payload["npc_spawn"],
                "hazards": payload["hazards"],
            },
        }

    def interact(self, username: str, interaction_id: str) -> Dict[str, Any]:
        user = self._ensure_user(username)
        current = self._place(str(user.get("current_place_id") or ""))
        if not current:
            return {"ok": False, "error": "No current place"}
        point = str(interaction_id or "").strip()
        if not point:
            return {"ok": False, "error": "Interaction id is required"}
        points = [str(x) for x in current.get("interaction_points", [])]
        if point not in points:
            return {"ok": False, "error": f"Unknown interaction point at {current.get('placeId')}: {point}"}

        payload = {
            "action": "INTERACT",
            "place_id": current.get("placeId"),
            "place_ref": current.get("placeRef"),
            "interaction_id": point,
            "location": self._event_payload_location(current),
        }
        self._append_event(username, "MAP_INTERACT", payload)
        return {"ok": True, "action": "INTERACT", "interaction_id": point, "place": current}

    def complete(self, username: str, objective_id: str) -> Dict[str, Any]:
        user = self._ensure_user(username)
        current = self._place(str(user.get("current_place_id") or ""))
        if not current:
            return {"ok": False, "error": "No current place"}
        objective = str(objective_id or "").strip()
        if not objective:
            return {"ok": False, "error": "Objective id is required"}
        valid_objectives = [str(x) for x in current.get("quest_ids", [])]
        if objective not in valid_objectives:
            return {
                "ok": False,
                "error": f"Objective not available at {current.get('placeId')}: {objective}",
            }

        payload = {
            "action": "COMPLETE",
            "place_id": current.get("placeId"),
            "place_ref": current.get("placeRef"),
            "objective_id": objective,
            "location": self._event_payload_location(current),
        }
        self._append_event(username, "MAP_COMPLETE", payload)
        return {"ok": True, "action": "COMPLETE", "objective_id": objective, "place": current}

    def tick(self, username: str, steps: int = 1) -> Dict[str, Any]:
        user = self._ensure_user(username)
        current = self._place(str(user.get("current_place_id") or ""))
        if not current:
            return {"ok": False, "error": "No current place"}

        safe_steps = max(1, int(steps or 1))
        user["tick_counter"] = int(user.get("tick_counter", 0) or 0) + safe_steps
        user["npc_phase"] = (int(user.get("npc_phase", 0) or 0) + safe_steps) % 8
        user["world_phase"] = (int(user.get("world_phase", 0) or 0) + safe_steps) % 16
        user["updated_at"] = self._now_iso()
        self._save()

        payload = {
            "action": "TICK",
            "steps": safe_steps,
            "tick_counter": user["tick_counter"],
            "npc_phase": user["npc_phase"],
            "world_phase": user["world_phase"],
            "place_id": current.get("placeId"),
            "place_ref": current.get("placeRef"),
            "location": self._event_payload_location(current),
        }
        self._append_event(username, "MAP_TICK", payload)
        return {
            "ok": True,
            "action": "TICK",
            "steps": safe_steps,
            "tick_counter": user["tick_counter"],
            "npc_phase": user["npc_phase"],
            "world_phase": user["world_phase"],
            "place": current,
        }


_map_runtime_service: Optional[MapRuntimeService] = None


def get_map_runtime_service() -> MapRuntimeService:
    global _map_runtime_service
    if _map_runtime_service is None:
        _map_runtime_service = MapRuntimeService()
    return _map_runtime_service
