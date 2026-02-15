"""
Gameplay service for user/core progression variables and gate state.

Stores per-user gameplay state (XP/HP/Gold), progression gates, TOYBOX profile
selection, and standardized progression fields in
memory/bank/private/gameplay_state.json.
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
    "rpgbbs": {
        "name": "Social Dungeon Lens (rpgbbs)",
        "container_id": "rpgbbs",
        "anchor": "EARTH:SUB",
        "runtime": "upstream-adapter",
    },
    "crawler3d": {
        "name": "Crawler Lens (crawler3d)",
        "container_id": "crawler3d",
        "anchor": "EARTH:SUB",
        "runtime": "upstream-adapter",
    },
}

DEFAULT_ROLE_PERMISSIONS = {
    "admin": {
        "gameplay.view": True,
        "gameplay.mutate": True,
        "gameplay.gate_admin": True,
        "gameplay.rule_admin": True,
        "toybox.launch": True,
        "toybox.admin": True,
    },
    "user": {
        "gameplay.view": True,
        "gameplay.mutate": True,
        "gameplay.gate_admin": False,
        "gameplay.rule_admin": True,
        "toybox.launch": True,
        "toybox.admin": False,
    },
    "guest": {
        "gameplay.view": True,
        "gameplay.mutate": False,
        "gameplay.gate_admin": False,
        "gameplay.rule_admin": False,
        "toybox.launch": False,
        "toybox.admin": False,
    },
}

DEFAULT_PROGRESS = {
    "level": 1,
    "achievement_level": 0,
    "achievements": [],
    "location": {
        "grid_id": "unknown",
        "x": None,
        "y": None,
        "z": 0,
    },
    "metrics": {
        "events_processed": 0,
        "missions_completed": 0,
        "deaths": 0,
        "elite_jumps": 0,
        "elite_docks": 0,
        "rpgbbs_sessions": 0,
        "rpgbbs_messages": 0,
        "rpgbbs_quests": 0,
        "crawler3d_floors": 0,
        "crawler3d_objectives": 0,
    },
}

PLAY_OPTIONS = {
    "dungeon": {
        "title": "Dungeon Run",
        "description": "Start dungeon progression lens.",
        "requirements": {},
    },
    "galaxy": {
        "title": "Galaxy Run",
        "description": "Enable galaxy lens mission loop.",
        "requirements": {"min_xp": 100},
    },
    "social": {
        "title": "Social Quest",
        "description": "Enable RPGBBS social quest loop.",
        "requirements": {"min_achievement_level": 1},
    },
    "ascension": {
        "title": "Ascension Gate",
        "description": "Proceed after dungeon ascension requirement.",
        "requirements": {"required_gate": "dungeon_l32_amulet", "min_achievement_level": 1},
    },
}

PLAY_UNLOCK_RULES = {
    "token.toybox.xp_100": {
        "title": "XP 100 Milestone",
        "requirements": {"min_xp": 100},
    },
    "token.toybox.achievement_l1": {
        "title": "Achievement Level I",
        "requirements": {"min_achievement_level": 1},
    },
    "token.toybox.navigator_l1": {
        "title": "Navigator I",
        "requirements": {"min_metric": {"elite_jumps": 5}},
    },
    "token.toybox.social_l1": {
        "title": "Social I",
        "requirements": {"min_metric": {"rpgbbs_quests": 1}},
    },
    "token.toybox.crawler_l1": {
        "title": "Crawler I",
        "requirements": {"min_metric": {"crawler3d_floors": 10}},
    },
    "token.toybox.ascension": {
        "title": "Dungeon Ascension",
        "requirements": {"required_gate": "dungeon_l32_amulet", "min_achievement_level": 1},
    },
}

DEFAULT_RULES = {
    "rule.play.galaxy_unlock": {
        "id": "rule.play.galaxy_unlock",
        "if": "xp>=100 and achievement_level>=1",
        "then": "TOKEN token.rule.play.galaxy; PLAY galaxy",
        "enabled": True,
        "source": "system-default",
    }
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
            "version": 2,
            "updated_at": self._now_iso(),
            "permissions": deepcopy(DEFAULT_ROLE_PERMISSIONS),
            "toybox": {
                "active_profile": "hethack",
                "profiles": deepcopy(DEFAULT_TOYBOX_PROFILES),
            },
            "gates": deepcopy(DEFAULT_GATES),
            "rules": deepcopy(DEFAULT_RULES),
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

        incoming_rules = data.get("rules", {})
        if isinstance(incoming_rules, dict):
            merged["rules"].update(incoming_rules)

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
                "progress": deepcopy(DEFAULT_PROGRESS),
                "unlock_tokens": [],
                "last_active_toybox": self.state["toybox"]["active_profile"],
                "updated_at": self._now_iso(),
            }
            users[username] = user
        user.setdefault("stats", GameplayStats().to_dict())
        user.setdefault("flags", {})
        progress = user.get("progress")
        if not isinstance(progress, dict):
            progress = deepcopy(DEFAULT_PROGRESS)
        progress.setdefault("level", 1)
        progress.setdefault("achievement_level", 0)
        achievements = progress.get("achievements")
        if not isinstance(achievements, list):
            achievements = []
        progress["achievements"] = [str(x) for x in achievements if str(x).strip()]
        location = progress.get("location")
        if not isinstance(location, dict):
            location = {}
        merged_location = deepcopy(DEFAULT_PROGRESS["location"])
        merged_location.update({k: v for k, v in location.items() if k in merged_location})
        progress["location"] = merged_location
        metrics = progress.get("metrics")
        if not isinstance(metrics, dict):
            metrics = {}
        merged_metrics = deepcopy(DEFAULT_PROGRESS["metrics"])
        for key in merged_metrics:
            merged_metrics[key] = int(metrics.get(key, merged_metrics[key]) or 0)
        progress["metrics"] = merged_metrics
        user["progress"] = progress
        tokens = user.get("unlock_tokens")
        user["unlock_tokens"] = tokens if isinstance(tokens, list) else []
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

    def get_user_progress(self, username: str) -> Dict[str, Any]:
        user = self._ensure_user(username)
        progress = user.get("progress", {})
        return deepcopy(progress) if isinstance(progress, dict) else deepcopy(DEFAULT_PROGRESS)

    def get_user_unlock_tokens(self, username: str) -> List[Dict[str, Any]]:
        user = self._ensure_user(username)
        tokens = user.get("unlock_tokens", [])
        return deepcopy(tokens) if isinstance(tokens, list) else []

    def _has_unlock_token(self, username: str, token_id: str) -> bool:
        token_id = str(token_id).strip()
        if not token_id:
            return False
        for row in self.get_user_unlock_tokens(username):
            if str(row.get("id", "")).strip() == token_id:
                return True
        return False

    def grant_unlock_token(
        self,
        username: str,
        token_id: str,
        *,
        source: str = "play",
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        token_id = str(token_id).strip()
        if not token_id:
            return None
        if self._has_unlock_token(username, token_id):
            return None
        user = self._ensure_user(username)
        row = {
            "id": token_id,
            "title": title or token_id,
            "source": source,
            "unlocked_at": self._now_iso(),
            "metadata": metadata or {},
        }
        user.setdefault("unlock_tokens", []).append(row)
        user["updated_at"] = self._now_iso()
        self._save()
        return deepcopy(row)

    def _add_achievement(self, username: str, achievement_id: str) -> bool:
        achievement_id = str(achievement_id).strip()
        if not achievement_id:
            return False
        user = self._ensure_user(username)
        progress = user.setdefault("progress", deepcopy(DEFAULT_PROGRESS))
        achievements = progress.setdefault("achievements", [])
        if achievement_id in achievements:
            return False
        achievements.append(achievement_id)
        user["updated_at"] = self._now_iso()
        return True

    def _evaluate_requirements(self, username: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        stats = self.get_user_stats(username)
        progress = self.get_user_progress(username)
        metrics = progress.get("metrics", {}) if isinstance(progress.get("metrics"), dict) else {}
        blocked: List[str] = []

        min_xp = int(requirements.get("min_xp", 0) or 0)
        if min_xp and stats.get("xp", 0) < min_xp:
            blocked.append(f"xp>={min_xp}")

        min_achievement_level = int(requirements.get("min_achievement_level", 0) or 0)
        if min_achievement_level and int(progress.get("achievement_level", 0) or 0) < min_achievement_level:
            blocked.append(f"achievement_level>={min_achievement_level}")

        min_level = int(requirements.get("min_level", 0) or 0)
        if min_level and int(progress.get("level", 1) or 1) < min_level:
            blocked.append(f"level>={min_level}")

        min_hp = int(requirements.get("min_hp", 0) or 0)
        if min_hp and int(stats.get("hp", 0) or 0) < min_hp:
            blocked.append(f"hp>={min_hp}")

        min_gold = int(requirements.get("min_gold", 0) or 0)
        if min_gold and int(stats.get("gold", 0) or 0) < min_gold:
            blocked.append(f"gold>={min_gold}")

        required_gate = str(requirements.get("required_gate", "")).strip()
        if required_gate:
            gate = self.get_gate(required_gate)
            if not gate or not gate.get("completed"):
                blocked.append(f"gate:{required_gate}")

        required_token = str(requirements.get("required_token", "")).strip()
        if required_token and not self._has_unlock_token(username, required_token):
            blocked.append(f"token:{required_token}")

        min_metric = requirements.get("min_metric", {})
        if isinstance(min_metric, dict):
            for key, raw_target in min_metric.items():
                target = int(raw_target or 0)
                current = int(metrics.get(key, 0) or 0)
                if current < target:
                    blocked.append(f"{key}>={target}")

        toybox_profile = str(requirements.get("toybox_profile", "")).strip().lower()
        if toybox_profile and self.get_active_toybox() != toybox_profile:
            blocked.append(f"toybox:{toybox_profile}")

        return {"ok": len(blocked) == 0, "blocked_by": blocked}

    def list_play_options(self, username: str) -> List[Dict[str, Any]]:
        options: List[Dict[str, Any]] = []
        for option_id, meta in PLAY_OPTIONS.items():
            requirements = meta.get("requirements", {})
            verdict = self._evaluate_requirements(username, requirements if isinstance(requirements, dict) else {})
            options.append(
                {
                    "id": option_id,
                    "title": meta.get("title", option_id),
                    "description": meta.get("description", ""),
                    "available": verdict["ok"],
                    "blocked_by": verdict["blocked_by"],
                    "requirements": requirements,
                }
            )
        return options

    def evaluate_unlock_tokens(self, username: str) -> List[Dict[str, Any]]:
        unlocked: List[Dict[str, Any]] = []
        for token_id, rule in PLAY_UNLOCK_RULES.items():
            requirements = rule.get("requirements", {})
            if not isinstance(requirements, dict):
                requirements = {}
            verdict = self._evaluate_requirements(username, requirements)
            if verdict["ok"]:
                token = self.grant_unlock_token(
                    username,
                    token_id,
                    source="play-rule",
                    title=str(rule.get("title", token_id)),
                    metadata={"requirements": requirements},
                )
                if token:
                    unlocked.append(token)
        return unlocked

    def start_play_option(self, username: str, option_id: str) -> Dict[str, Any]:
        option_id = str(option_id).strip().lower()
        option = PLAY_OPTIONS.get(option_id)
        if not option:
            raise ValueError(f"Unknown play option: {option_id}")
        verdict = self._evaluate_requirements(username, option.get("requirements", {}))
        if not verdict["ok"]:
            return {
                "status": "blocked",
                "option": option_id,
                "blocked_by": verdict["blocked_by"],
                "message": f"PLAY option blocked: {option_id}",
            }
        user = self._ensure_user(username)
        progress = user.setdefault("progress", deepcopy(DEFAULT_PROGRESS))
        progress["last_play_option"] = option_id
        progress["last_play_started_at"] = self._now_iso()
        metrics = progress.setdefault("metrics", deepcopy(DEFAULT_PROGRESS["metrics"]))
        metrics["events_processed"] = int(metrics.get("events_processed", 0) or 0)
        user["updated_at"] = self._now_iso()
        self._save()
        unlocked = self.evaluate_unlock_tokens(username)
        return {
            "status": "success",
            "option": option_id,
            "message": f"PLAY option started: {option_id}",
            "unlocked_tokens": unlocked,
        }

    def list_rules(self) -> Dict[str, Dict[str, Any]]:
        rules = self.state.get("rules", {})
        return deepcopy(rules) if isinstance(rules, dict) else {}

    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        rule_id = str(rule_id).strip()
        if not rule_id:
            return None
        rules = self.state.get("rules", {})
        if not isinstance(rules, dict):
            return None
        value = rules.get(rule_id)
        return deepcopy(value) if isinstance(value, dict) else None

    def set_rule(
        self,
        rule_id: str,
        *,
        if_expr: str,
        then_expr: str,
        enabled: bool = True,
        source: str = "rule-command",
    ) -> Dict[str, Any]:
        rid = str(rule_id).strip()
        if not rid:
            raise ValueError("Rule id is required")
        if not str(if_expr).strip():
            raise ValueError("IF expression is required")
        if not str(then_expr).strip():
            raise ValueError("THEN expression is required")
        rules = self.state.setdefault("rules", {})
        current = rules.get(rid) if isinstance(rules, dict) else None
        created_at = current.get("created_at") if isinstance(current, dict) else self._now_iso()
        row = {
            "id": rid,
            "if": str(if_expr).strip(),
            "then": str(then_expr).strip(),
            "enabled": bool(enabled),
            "source": source,
            "created_at": created_at,
            "updated_at": self._now_iso(),
        }
        rules[rid] = row
        self._save()
        return deepcopy(row)

    def delete_rule(self, rule_id: str) -> bool:
        rid = str(rule_id).strip()
        rules = self.state.get("rules", {})
        if not rid or not isinstance(rules, dict) or rid not in rules:
            return False
        del rules[rid]
        self._save()
        return True

    def set_rule_enabled(self, rule_id: str, enabled: bool) -> Optional[Dict[str, Any]]:
        rid = str(rule_id).strip()
        rules = self.state.get("rules", {})
        if not rid or not isinstance(rules, dict):
            return None
        row = rules.get(rid)
        if not isinstance(row, dict):
            return None
        row["enabled"] = bool(enabled)
        row["updated_at"] = self._now_iso()
        self._save()
        return deepcopy(row)

    def _requirements_from_if_expression(self, expression: str) -> Dict[str, Any]:
        expr = str(expression or "").strip()
        if not expr:
            return {}
        requirements: Dict[str, Any] = {}
        clauses = [c.strip() for c in expr.replace("&&", " and ").split(" and ") if c.strip()]
        for clause in clauses:
            lower = clause.lower()
            if lower.startswith("gate:"):
                requirements["required_gate"] = clause.split(":", 1)[1].strip()
                continue
            if lower.startswith("token:"):
                requirements["required_token"] = clause.split(":", 1)[1].strip()
                continue
            if lower.startswith("toybox==") or lower.startswith("toybox="):
                profile = clause.split("=", 1)[1].strip()
                requirements["toybox_profile"] = profile
                continue
            op = None
            if ">=" in clause:
                key, val = clause.split(">=", 1)
                op = ">="
            elif "==" in clause:
                key, val = clause.split("==", 1)
                op = "=="
            elif "=" in clause:
                key, val = clause.split("=", 1)
                op = "="
            else:
                continue
            key = key.strip().lower()
            val = val.strip()
            if key in {"xp", "hp", "gold", "level", "achievement_level"}:
                try:
                    n = int(val)
                except Exception:
                    continue
                if key == "xp":
                    requirements["min_xp"] = n if op in {">=", "=", "=="} else n
                elif key == "hp":
                    requirements["min_hp"] = n
                elif key == "gold":
                    requirements["min_gold"] = n
                elif key == "level":
                    requirements["min_level"] = n
                elif key == "achievement_level":
                    requirements["min_achievement_level"] = n
                continue
            if key.startswith("metric.") or key.startswith("metrics."):
                metric_key = key.split(".", 1)[1]
                try:
                    n = int(val)
                except Exception:
                    continue
                mm = requirements.setdefault("min_metric", {})
                if isinstance(mm, dict):
                    mm[metric_key] = n
        return requirements

    def _apply_then_expression(self, username: str, then_expr: str) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []
        chunks = [c.strip() for c in str(then_expr or "").split(";") if c.strip()]
        for chunk in chunks:
            parts = chunk.split()
            if not parts:
                continue
            head = parts[0].upper()
            if head == "TOKEN" and len(parts) >= 2:
                token_id = parts[1].strip()
                token = self.grant_unlock_token(username, token_id, source="rule-action", title=token_id)
                actions.append({"action": "TOKEN", "token_id": token_id, "created": bool(token)})
                continue
            if head == "PLAY" and len(parts) >= 2:
                option_id = parts[1].strip().lower()
                result = self.start_play_option(username, option_id)
                actions.append({"action": "PLAY", "option": option_id, "status": result.get("status")})
                continue
            if head == "GATE" and len(parts) >= 3 and parts[1].upper() == "COMPLETE":
                gate_id = parts[2].strip()
                gate = self.complete_gate(gate_id, source="rule-action")
                actions.append({"action": "GATE_COMPLETE", "gate_id": gate_id, "completed": bool(gate.get("completed"))})
                continue
            if head == "STAT" and len(parts) >= 4 and parts[1].upper() == "ADD":
                stat = parts[2].strip().lower()
                try:
                    delta = int(parts[3])
                    stats = self.add_user_stat(username, stat, delta)
                    actions.append({"action": "STAT_ADD", "stat": stat, "delta": delta, "stats": stats})
                except Exception:
                    actions.append({"action": "STAT_ADD", "error": "invalid stat or delta"})
                continue
            if head == "ACHIEVE" and len(parts) >= 2:
                achievement_id = parts[1].strip()
                added = self._add_achievement(username, achievement_id)
                actions.append({"action": "ACHIEVE", "achievement_id": achievement_id, "added": added})
                continue
            actions.append({"action": "UNSUPPORTED", "raw": chunk})
        return actions

    def run_rules(self, username: str, rule_id: Optional[str] = None) -> Dict[str, Any]:
        rules = self.list_rules()
        candidates = [rule_id] if rule_id else sorted(rules.keys())
        fired: List[Dict[str, Any]] = []
        blocked: List[Dict[str, Any]] = []
        for rid in candidates:
            rule = rules.get(rid)
            if not isinstance(rule, dict):
                continue
            if not bool(rule.get("enabled", True)):
                blocked.append({"id": rid, "reason": "disabled"})
                continue
            requirements = self._requirements_from_if_expression(str(rule.get("if", "")))
            verdict = self._evaluate_requirements(username, requirements)
            if not verdict["ok"]:
                blocked.append({"id": rid, "reason": "condition-failed", "blocked_by": verdict["blocked_by"]})
                continue
            actions = self._apply_then_expression(username, str(rule.get("then", "")))
            fired.append({"id": rid, "actions": actions})
        if fired:
            self._save()
        return {"fired": fired, "blocked": blocked}

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

    def _progress_metric_add(self, username: str, key: str, delta: int = 1) -> None:
        user = self._ensure_user(username)
        progress = user.setdefault("progress", deepcopy(DEFAULT_PROGRESS))
        metrics = progress.setdefault("metrics", deepcopy(DEFAULT_PROGRESS["metrics"]))
        metrics[key] = int(metrics.get(key, 0) or 0) + int(delta)
        user["updated_at"] = self._now_iso()

    def _set_progress_location(self, username: str, payload: Dict[str, Any]) -> bool:
        changed = False
        user = self._ensure_user(username)
        progress = user.setdefault("progress", deepcopy(DEFAULT_PROGRESS))
        location = progress.setdefault("location", deepcopy(DEFAULT_PROGRESS["location"]))

        for key in ("grid_id", "x", "y", "z"):
            if key not in payload:
                continue
            value = payload.get(key)
            if key in {"x", "y", "z"} and value is not None:
                try:
                    value = int(value)
                except Exception:
                    continue
            if location.get(key) != value:
                location[key] = value
                changed = True

        if changed:
            user["updated_at"] = self._now_iso()
        return changed

    def _recompute_progress(self, username: str, stats: Dict[str, int]) -> bool:
        user = self._ensure_user(username)
        progress = user.setdefault("progress", deepcopy(DEFAULT_PROGRESS))
        current_level = int(progress.get("level", 1) or 1)
        depth = int(self._flag_get(username, "hethack.max_depth", 1) or 1)
        xp_level = max(1, stats.get("xp", 0) // 100 + 1)
        depth_level = max(1, depth // 4 + 1)
        new_level = max(current_level, xp_level, depth_level)

        achievements = progress.get("achievements", [])
        if not isinstance(achievements, list):
            achievements = []
            progress["achievements"] = achievements
        gate_bonus = 1 if self.can_proceed() else 0
        new_achievement_level = max(int(progress.get("achievement_level", 0) or 0), len(achievements) + gate_bonus)

        changed = False
        if new_level != current_level:
            progress["level"] = new_level
            changed = True
        if new_achievement_level != int(progress.get("achievement_level", 0) or 0):
            progress["achievement_level"] = new_achievement_level
            changed = True
        if changed:
            user["updated_at"] = self._now_iso()
        return changed

    def _apply_event(self, username: str, event: Dict[str, Any]) -> Dict[str, Any]:
        payload = event.get("payload", {}) if isinstance(event.get("payload"), dict) else {}
        event_type = str(event.get("type", "")).upper()
        stats = self.get_user_stats(username)
        changed = False
        gate_changed = False
        notes: List[str] = []
        normalized_fields: List[str] = []

        # Standardized payload contract (optional): stats_delta/progress/location.
        stats_delta = payload.get("stats_delta")
        if isinstance(stats_delta, dict):
            for stat in ("xp", "hp", "gold"):
                if stat in stats_delta:
                    try:
                        stats[stat] += int(stats_delta.get(stat, 0) or 0)
                        changed = True
                        normalized_fields.append(f"stats_delta.{stat}")
                    except Exception:
                        continue
            stats["hp"] = max(0, int(stats.get("hp", 0)))

        progress_payload = payload.get("progress")
        if isinstance(progress_payload, dict):
            achievement_id = str(progress_payload.get("achievement_id", "")).strip()
            if achievement_id and self._add_achievement(username, achievement_id):
                changed = True
                normalized_fields.append("progress.achievement_id")
            level_hint = progress_payload.get("level")
            if level_hint is not None:
                try:
                    level_hint_int = int(level_hint)
                    user = self._ensure_user(username)
                    progress = user.setdefault("progress", deepcopy(DEFAULT_PROGRESS))
                    progress["level"] = max(int(progress.get("level", 1) or 1), level_hint_int)
                    changed = True
                    normalized_fields.append("progress.level")
                except Exception:
                    pass

        location_payload = payload.get("location")
        if isinstance(location_payload, dict) and self._set_progress_location(username, location_payload):
            changed = True
            normalized_fields.append("location")

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
                self._set_progress_location(username, {"grid_id": "dungeon:main", "z": depth})
                self._progress_metric_add(username, "events_processed", 1)

        elif event_type == "HETHACK_AMULET_RETRIEVED":
            self._flag_set(username, "hethack.amulet_retrieved", True)
            stats["xp"] += 500
            stats["gold"] += 1000
            changed = True
            notes.append("amulet")
            self._add_achievement(username, "dungeon_l32_amulet")
            self._progress_metric_add(username, "events_processed", 1)

        elif event_type == "HETHACK_DEATH":
            stats["hp"] = max(0, stats["hp"] - 25)
            changed = True
            notes.append("death")
            self._progress_metric_add(username, "deaths", 1)
            self._progress_metric_add(username, "events_processed", 1)

        elif event_type == "ELITE_HYPERSPACE_JUMP":
            stats["xp"] += 15
            changed = True
            notes.append("jump")
            self._progress_metric_add(username, "elite_jumps", 1)
            self._progress_metric_add(username, "events_processed", 1)
            self._set_progress_location(username, {"grid_id": "galaxy:chart1", "z": 0})

        elif event_type == "ELITE_DOCKED":
            stats["xp"] += 20
            changed = True
            notes.append("dock")
            self._progress_metric_add(username, "elite_docks", 1)
            self._progress_metric_add(username, "events_processed", 1)

        elif event_type == "ELITE_MISSION_COMPLETE":
            stats["xp"] += 100
            stats["gold"] += 250
            changed = True
            notes.append("mission")
            self._add_achievement(username, "elite_first_mission")
            self._progress_metric_add(username, "missions_completed", 1)
            self._progress_metric_add(username, "events_processed", 1)

        elif event_type == "ELITE_TRADE_PROFIT":
            profit = int(payload.get("profit", 0) or 0)
            if profit:
                stats["gold"] += profit
                stats["xp"] += max(1, profit // 50)
                changed = True
                notes.append(f"profit:{profit}")
                self._progress_metric_add(username, "events_processed", 1)

        elif event_type == "RPGBBS_SESSION_START":
            stats["xp"] += 5
            changed = True
            notes.append("rpgbbs:start")
            self._progress_metric_add(username, "rpgbbs_sessions", 1)
            self._progress_metric_add(username, "events_processed", 1)
            self._set_progress_location(username, {"grid_id": "bbs:lobby", "z": 0})

        elif event_type == "RPGBBS_MESSAGE_EVENT":
            stats["xp"] += 3
            changed = True
            notes.append("rpgbbs:message")
            self._progress_metric_add(username, "rpgbbs_messages", 1)
            self._progress_metric_add(username, "events_processed", 1)

        elif event_type == "RPGBBS_QUEST_COMPLETE":
            stats["xp"] += 40
            stats["gold"] += 25
            changed = True
            notes.append("rpgbbs:quest")
            self._add_achievement(username, "rpgbbs_first_quest")
            self._progress_metric_add(username, "rpgbbs_quests", 1)
            self._progress_metric_add(username, "events_processed", 1)

        elif event_type == "CRAWLER3D_FLOOR_REACHED":
            floor = int(payload.get("floor", 0) or 0)
            stats["xp"] += max(5, floor * 2)
            changed = True
            notes.append(f"crawler3d:floor:{floor}")
            self._progress_metric_add(username, "crawler3d_floors", max(1, floor))
            self._progress_metric_add(username, "events_processed", 1)
            self._set_progress_location(username, {"grid_id": "crawler3d:zone1", "z": floor})
            if floor >= 10:
                self._add_achievement(username, "crawler3d_floor_10")

        elif event_type == "CRAWLER3D_LOOT_FOUND":
            stats["gold"] += 15
            stats["xp"] += 5
            changed = True
            notes.append("crawler3d:loot")
            self._progress_metric_add(username, "events_processed", 1)

        elif event_type == "CRAWLER3D_OBJECTIVE_COMPLETE":
            stats["gold"] += 75
            stats["xp"] += 50
            changed = True
            notes.append("crawler3d:objective")
            self._add_achievement(username, "crawler3d_objective_clear")
            self._progress_metric_add(username, "crawler3d_objectives", 1)
            self._progress_metric_add(username, "events_processed", 1)

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
            self._recompute_progress(username, stats)
            newly_unlocked = self.evaluate_unlock_tokens(username)
            if newly_unlocked:
                notes.extend([f"token:{row.get('id')}" for row in newly_unlocked])
            self._save()

        return {
            "event_type": event_type,
            "changed": changed,
            "gate_changed": gate_changed,
            "notes": notes,
            "normalized_fields": normalized_fields,
            "stats": self.get_user_stats(username),
            "progress": self.get_user_progress(username),
        }

    def tick(self, username: str, max_events: int = 128) -> Dict[str, Any]:
        """Ingest external TOYBOX events and apply to gameplay state."""
        if not self.events_file.exists():
            rules = self.run_rules(username)
            return {
                "processed": 0,
                "stats": self.get_user_stats(username),
                "gate_changed": False,
                "events": [],
                "rules": rules,
            }

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

        rule_result = self.run_rules(username)

        return {
            "processed": processed,
            "stats": self.get_user_stats(username),
            "gate_changed": gate_changed,
            "events": applied,
            "rules": rule_result,
        }

    def snapshot(self, username: str, role: str) -> Dict[str, Any]:
        return {
            "username": username,
            "role": role,
            "stats": self.get_user_stats(username),
            "progress": self.get_user_progress(username),
            "unlock_tokens": self.get_user_unlock_tokens(username),
            "gates": self.list_gates(),
            "can_proceed": self.can_proceed(),
            "toybox": {
                "active_profile": self.get_active_toybox(),
                "profiles": self.get_toybox_profiles(),
            },
            "play_options": self.list_play_options(username),
            "rules": self.list_rules(),
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
