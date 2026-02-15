"""
Gameplay service for user/core progression variables and gate state.

Stores per-user gameplay state (XP/HP/Gold), progression gates, and
TOYBOX profile selection in memory/bank/private/gameplay_state.json.
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.logging_api import get_repo_root


DEFAULT_GATES = {
    "dungeon_l32_amulet": {
        "title": "Complete dungeon level 32 and retrieve the Amulet of Yendor",
        "lens": "hethack",
        "completed": False,
        "completed_at": None,
    }
}

DEFAULT_TOYBOX_PROFILES = {
    "hethack": {
        "name": "Dungeon Lens (hethack)",
        "container_id": "hethack",
        "anchor": "EARTH:SUB",
        "runtime": "upstream-adapter",
    },
    "elite": {
        "name": "Galaxy Lens (elite)",
        "container_id": "elite",
        "anchor": "CATALOG:SUR",
        "runtime": "upstream-adapter",
    },
}

DEFAULT_ROLE_PERMISSIONS = {
    "admin": {
        "gameplay.view": True,
        "gameplay.mutate": True,
        "gameplay.gate_admin": True,
        "toybox.launch": True,
        "toybox.admin": True,
    },
    "user": {
        "gameplay.view": True,
        "gameplay.mutate": True,
        "gameplay.gate_admin": False,
        "toybox.launch": True,
        "toybox.admin": False,
    },
    "guest": {
        "gameplay.view": True,
        "gameplay.mutate": False,
        "gameplay.gate_admin": False,
        "toybox.launch": False,
        "toybox.admin": False,
    },
}


@dataclass
class GameplayStats:
    xp: int = 0
    hp: int = 100
    gold: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {"xp": int(self.xp), "hp": int(self.hp), "gold": int(self.gold)}


class GameplayService:
    """Persistent gameplay state for uDOS Core."""

    def __init__(
        self,
        state_file: Optional[Path] = None,
        events_file: Optional[Path] = None,
        cursor_file: Optional[Path] = None,
    ) -> None:
        repo_root = get_repo_root()
        self.state_file = state_file or repo_root / "memory" / "bank" / "private" / "gameplay_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        private_root = self.state_file.parent
        self.events_file = events_file or private_root / "gameplay_events.ndjson"
        self.cursor_file = cursor_file or private_root / "gameplay_event_cursor.json"
        self.state = self._load_state()

    def _default_state(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "updated_at": self._now_iso(),
            "permissions": deepcopy(DEFAULT_ROLE_PERMISSIONS),
            "toybox": {
                "active_profile": "hethack",
                "profiles": deepcopy(DEFAULT_TOYBOX_PROFILES),
            },
            "gates": deepcopy(DEFAULT_GATES),
            "users": {},
        }

    def _load_state(self) -> Dict[str, Any]:
        if not self.state_file.exists():
            state = self._default_state()
            self._write_state(state)
            return state
        try:
            data = json.loads(self.state_file.read_text())
            return self._merge_defaults(data)
        except Exception:
            state = self._default_state()
            self._write_state(state)
            return state

    def _merge_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        merged = self._default_state()
        if not isinstance(data, dict):
            return merged

        merged.update({k: v for k, v in data.items() if k in {"version", "updated_at"}})

        incoming_users = data.get("users", {})
        if isinstance(incoming_users, dict):
            merged["users"] = incoming_users

        incoming_gates = data.get("gates", {})
        if isinstance(incoming_gates, dict):
            merged["gates"].update(incoming_gates)

        incoming_permissions = data.get("permissions", {})
        if isinstance(incoming_permissions, dict):
            merged["permissions"].update(incoming_permissions)

        incoming_toybox = data.get("toybox", {})
        if isinstance(incoming_toybox, dict):
            merged["toybox"].update({k: v for k, v in incoming_toybox.items() if k in {"active_profile"}})
            profiles = incoming_toybox.get("profiles", {})
            if isinstance(profiles, dict):
                merged["toybox"]["profiles"].update(profiles)

        return merged

    def _write_state(self, state: Dict[str, Any]) -> None:
        self.state_file.write_text(json.dumps(state, indent=2))

    def _save(self) -> None:
        self.state["updated_at"] = self._now_iso()
        self._write_state(self.state)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_cursor(self) -> int:
        if not self.cursor_file.exists():
            return 0
        try:
            data = json.loads(self.cursor_file.read_text())
            return int(data.get("offset", 0))
        except Exception:
            return 0

    def _save_cursor(self, offset: int) -> None:
        self.cursor_file.parent.mkdir(parents=True, exist_ok=True)
        self.cursor_file.write_text(json.dumps({"offset": int(offset)}, indent=2))

    def _ensure_user(self, username: str) -> Dict[str, Any]:
        users = self.state.setdefault("users", {})
        user = users.get(username)
        if not isinstance(user, dict):
            user = {
                "stats": GameplayStats().to_dict(),
                "flags": {},
                "last_active_toybox": self.state["toybox"]["active_profile"],
                "updated_at": self._now_iso(),
            }
            users[username] = user
        user.setdefault("stats", GameplayStats().to_dict())
        user.setdefault("flags", {})
        user.setdefault("last_active_toybox", self.state["toybox"]["active_profile"])
        user.setdefault("updated_at", self._now_iso())
        return user

    def get_user_stats(self, username: str) -> Dict[str, int]:
        user = self._ensure_user(username)
        stats = user.get("stats", {})
        return {
            "xp": int(stats.get("xp", 0)),
            "hp": int(stats.get("hp", 100)),
            "gold": int(stats.get("gold", 0)),
        }

    def set_user_stat(self, username: str, stat: str, value: int) -> Dict[str, int]:
        if stat not in {"xp", "hp", "gold"}:
            raise ValueError(f"Unknown stat: {stat}")
        user = self._ensure_user(username)
        stats = self.get_user_stats(username)
        stats[stat] = int(value)
        user["stats"] = stats
        user["updated_at"] = self._now_iso()
        self._save()
        return stats

    def add_user_stat(self, username: str, stat: str, delta: int) -> Dict[str, int]:
        stats = self.get_user_stats(username)
        return self.set_user_stat(username, stat, stats[stat] + int(delta))

    def get_gate(self, gate_id: str) -> Optional[Dict[str, Any]]:
        gates = self.state.get("gates", {})
        value = gates.get(gate_id)
        return deepcopy(value) if isinstance(value, dict) else None

    def list_gates(self) -> Dict[str, Dict[str, Any]]:
        gates = self.state.get("gates", {})
        if not isinstance(gates, dict):
            return {}
        return deepcopy(gates)

    def complete_gate(self, gate_id: str, source: str = "manual") -> Dict[str, Any]:
        gates = self.state.setdefault("gates", {})
        gate = gates.get(gate_id)
        if not isinstance(gate, dict):
            gate = {"title": gate_id, "lens": source}
            gates[gate_id] = gate
        gate["completed"] = True
        gate["completed_at"] = self._now_iso()
        gate["completed_source"] = source
        self._save()
        return deepcopy(gate)

    def reset_gate(self, gate_id: str) -> Dict[str, Any]:
        gates = self.state.setdefault("gates", {})
        gate = gates.get(gate_id)
        if not isinstance(gate, dict):
            gate = {"title": gate_id, "lens": "unknown"}
            gates[gate_id] = gate
        gate["completed"] = False
        gate["completed_at"] = None
        gate["completed_source"] = None
        self._save()
        return deepcopy(gate)

    def can_proceed(self) -> bool:
        gate = self.get_gate("dungeon_l32_amulet")
        return bool(gate and gate.get("completed"))

    def get_toybox_profiles(self) -> Dict[str, Dict[str, Any]]:
        toybox = self.state.get("toybox", {})
        profiles = toybox.get("profiles", {})
        if not isinstance(profiles, dict):
            return {}
        return deepcopy(profiles)

    def get_active_toybox(self) -> str:
        return str(self.state.get("toybox", {}).get("active_profile", "hethack"))

    def set_active_toybox(self, profile_id: str, username: Optional[str] = None) -> str:
        profiles = self.get_toybox_profiles()
        if profile_id not in profiles:
            raise ValueError(f"Unknown TOYBOX profile: {profile_id}")
        self.state.setdefault("toybox", {})["active_profile"] = profile_id
        if username:
            user = self._ensure_user(username)
            user["last_active_toybox"] = profile_id
            user["updated_at"] = self._now_iso()
        self._save()
        return profile_id

    def has_permission(self, role: str, permission_id: str) -> bool:
        perms = self.state.get("permissions", {})
        role_perms = perms.get(role, {}) if isinstance(perms, dict) else {}
        if not isinstance(role_perms, dict):
            return False
        return bool(role_perms.get(permission_id, False))

    def _flag_get(self, username: str, key: str, default: Any = None) -> Any:
        user = self._ensure_user(username)
        return user.get("flags", {}).get(key, default)

    def _flag_set(self, username: str, key: str, value: Any) -> None:
        user = self._ensure_user(username)
        user.setdefault("flags", {})[key] = value
        user["updated_at"] = self._now_iso()

    def _apply_event(self, username: str, event: Dict[str, Any]) -> Dict[str, Any]:
        payload = event.get("payload", {}) if isinstance(event.get("payload"), dict) else {}
        event_type = str(event.get("type", "")).upper()
        stats = self.get_user_stats(username)
        changed = False
        gate_changed = False
        notes: List[str] = []

        if event_type == "HETHACK_LEVEL_REACHED":
            depth = int(payload.get("depth", 0) or 0)
            prev_depth = int(self._flag_get(username, "hethack.max_depth", 1) or 1)
            if depth > prev_depth:
                self._flag_set(username, "hethack.max_depth", depth)
                changed = True
            if depth > 0:
                stats["xp"] += 10
                changed = True
                notes.append(f"depth:{depth}")

        elif event_type == "HETHACK_AMULET_RETRIEVED":
            self._flag_set(username, "hethack.amulet_retrieved", True)
            stats["xp"] += 500
            stats["gold"] += 1000
            changed = True
            notes.append("amulet")

        elif event_type == "HETHACK_DEATH":
            stats["hp"] = max(0, stats["hp"] - 25)
            changed = True
            notes.append("death")

        elif event_type == "ELITE_HYPERSPACE_JUMP":
            stats["xp"] += 15
            changed = True
            notes.append("jump")

        elif event_type == "ELITE_DOCKED":
            stats["xp"] += 20
            changed = True
            notes.append("dock")

        elif event_type == "ELITE_MISSION_COMPLETE":
            stats["xp"] += 100
            stats["gold"] += 250
            changed = True
            notes.append("mission")

        elif event_type == "ELITE_TRADE_PROFIT":
            profit = int(payload.get("profit", 0) or 0)
            if profit:
                stats["gold"] += profit
                stats["xp"] += max(1, profit // 50)
                changed = True
                notes.append(f"profit:{profit}")

        depth = int(self._flag_get(username, "hethack.max_depth", 1) or 1)
        has_amulet = bool(self._flag_get(username, "hethack.amulet_retrieved", False))
        gate = self.get_gate("dungeon_l32_amulet")
        if gate and not gate.get("completed") and depth >= 32 and has_amulet:
            self.complete_gate("dungeon_l32_amulet", source="toybox-event")
            gate_changed = True

        if changed:
            self.set_user_stat(username, "xp", stats["xp"])
            self.set_user_stat(username, "hp", stats["hp"])
            self.set_user_stat(username, "gold", stats["gold"])
            self._save()

        return {
            "event_type": event_type,
            "changed": changed,
            "gate_changed": gate_changed,
            "notes": notes,
            "stats": self.get_user_stats(username),
        }

    def tick(self, username: str, max_events: int = 128) -> Dict[str, Any]:
        """Ingest external TOYBOX events and apply to gameplay state."""
        if not self.events_file.exists():
            return {"processed": 0, "stats": self.get_user_stats(username), "gate_changed": False, "events": []}

        offset = self._load_cursor()
        processed = 0
        gate_changed = False
        applied: List[Dict[str, Any]] = []
        new_offset = offset

        with self.events_file.open("r", encoding="utf-8") as fh:
            fh.seek(offset)
            while processed < max_events:
                line = fh.readline()
                if not line:
                    break
                new_offset = fh.tell()
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except Exception:
                    continue
                target_user = str(event.get("username") or username)
                result = self._apply_event(target_user, event)
                processed += 1
                if result.get("gate_changed"):
                    gate_changed = True
                applied.append(result)

        if new_offset != offset:
            self._save_cursor(new_offset)

        return {
            "processed": processed,
            "stats": self.get_user_stats(username),
            "gate_changed": gate_changed,
            "events": applied,
        }

    def snapshot(self, username: str, role: str) -> Dict[str, Any]:
        return {
            "username": username,
            "role": role,
            "stats": self.get_user_stats(username),
            "gates": self.list_gates(),
            "can_proceed": self.can_proceed(),
            "toybox": {
                "active_profile": self.get_active_toybox(),
                "profiles": self.get_toybox_profiles(),
            },
            "permissions": self.state.get("permissions", {}).get(role, {}),
            "updated_at": self.state.get("updated_at"),
        }


_gameplay_service: Optional[GameplayService] = None


def get_gameplay_service() -> GameplayService:
    """Get global gameplay service singleton."""
    global _gameplay_service
    if _gameplay_service is None:
        _gameplay_service = GameplayService()
    return _gameplay_service
