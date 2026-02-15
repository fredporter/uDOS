"""GPLAY command handler - progression stats, gates, and TOYBOX profiles."""

from __future__ import annotations

from typing import Dict, List

from .base import BaseCommandHandler


class GameplayHandler(BaseCommandHandler):
    """Handle gameplay scaffolding commands.

    Commands:
      GPLAY
      GPLAY STATUS
      GPLAY STATS
      GPLAY STATS SET <xp|hp|gold> <value>
      GPLAY STATS ADD <xp|hp|gold> <delta>
      GPLAY GATE STATUS
      GPLAY GATE COMPLETE <gate_id>
      GPLAY GATE RESET <gate_id>
      GPLAY TOYBOX LIST
      GPLAY TOYBOX SET <hethack|elite|rpgbbs|crawler3d>
      GPLAY PROCEED
      GPLAY NEXT
      GPLAY UNLOCK
    """

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        from core.services.gameplay_service import get_gameplay_service
        from core.services.user_service import get_user_manager

        user_mgr = get_user_manager()
        current_user = user_mgr.current()
        if not current_user:
            return {"status": "error", "message": "No active user"}

        gameplay = get_gameplay_service()
        username = current_user.username
        role = current_user.role.value
        gameplay.tick(username)

        if not params:
            return self._status_block(gameplay.snapshot(username, role))

        sub = params[0].lower()
        if sub in {"status", "show"}:
            return self._status_block(gameplay.snapshot(username, role))

        if sub == "stats":
            return self._handle_stats(gameplay, username, role, params[1:])

        if sub == "gate":
            return self._handle_gate(gameplay, role, params[1:])

        if sub == "toybox":
            return self._handle_toybox(gameplay, username, role, params[1:])

        if sub in {"proceed", "unlock", "next"}:
            return self._handle_proceed(gameplay)

        if sub in {"help", "-h", "--help"}:
            return {
                "status": "success",
                "message": self.__doc__ or "GPLAY help",
                "output": (self.__doc__ or "GPLAY help").strip(),
            }

        return {
            "status": "error",
            "message": f"Unknown GPLAY subcommand: {sub}",
        }

    def _handle_stats(self, gameplay, username: str, role: str, params: List[str]) -> Dict:
        stats = gameplay.get_user_stats(username)
        if not params:
            return {
                "status": "success",
                "message": "Gameplay stats",
                "player_stats": stats,
                "output": f"XP={stats['xp']} HP={stats['hp']} Gold={stats['gold']}",
            }

        if not gameplay.has_permission(role, "gameplay.mutate"):
            return {"status": "error", "message": "Permission denied: gameplay.mutate"}

        action = params[0].lower()
        if len(params) < 3:
            return {
                "status": "error",
                "message": "Syntax: GPLAY STATS <SET|ADD> <xp|hp|gold> <value>",
            }
        stat = params[1].lower()
        try:
            value = int(params[2])
        except ValueError:
            return {"status": "error", "message": "Value must be an integer"}

        if action == "set":
            stats = gameplay.set_user_stat(username, stat, value)
        elif action == "add":
            stats = gameplay.add_user_stat(username, stat, value)
        else:
            return {"status": "error", "message": "Use SET or ADD"}

        self.set_state("player_stats", stats)
        return {
            "status": "success",
            "message": f"Updated {stat}",
            "player_stats": stats,
            "output": f"XP={stats['xp']} HP={stats['hp']} Gold={stats['gold']}",
        }

    def _handle_gate(self, gameplay, role: str, params: List[str]) -> Dict:
        if not params or params[0].lower() == "status":
            gates = gameplay.list_gates()
            lines = ["Gameplay gates:"]
            for gate_id, gate in gates.items():
                done = "done" if gate.get("completed") else "pending"
                lines.append(f"- {gate_id}: {done}")
            return {
                "status": "success",
                "message": "Gameplay gates",
                "gates": gates,
                "output": "\n".join(lines),
            }

        action = params[0].lower()
        if action in {"complete", "reset"} and not gameplay.has_permission(role, "gameplay.gate_admin"):
            return {"status": "error", "message": "Permission denied: gameplay.gate_admin"}
        if len(params) < 2:
            return {"status": "error", "message": "Syntax: GPLAY GATE <COMPLETE|RESET> <gate_id>"}

        gate_id = params[1]
        if action == "complete":
            gate = gameplay.complete_gate(gate_id, source="gameplay-command")
            return {
                "status": "success",
                "message": f"Gate completed: {gate_id}",
                "gate": gate,
                "output": f"Gate {gate_id} completed.",
            }
        if action == "reset":
            gate = gameplay.reset_gate(gate_id)
            return {
                "status": "success",
                "message": f"Gate reset: {gate_id}",
                "gate": gate,
                "output": f"Gate {gate_id} reset.",
            }
        return {"status": "error", "message": "Use STATUS, COMPLETE, or RESET"}

    def _handle_toybox(self, gameplay, username: str, role: str, params: List[str]) -> Dict:
        if not params or params[0].lower() == "list":
            active = gameplay.get_active_toybox()
            profiles = gameplay.get_toybox_profiles()
            lines = [f"Active TOYBOX: {active}", "Profiles:"]
            for profile_id, profile in profiles.items():
                marker = "*" if profile_id == active else " "
                lines.append(f"{marker} {profile_id} -> {profile.get('container_id')}")
            return {
                "status": "success",
                "message": "TOYBOX profiles",
                "toybox": {"active_profile": active, "profiles": profiles},
                "output": "\n".join(lines),
            }

        if not gameplay.has_permission(role, "toybox.admin"):
            return {"status": "error", "message": "Permission denied: toybox.admin"}

        action = params[0].lower()
        if action != "set" or len(params) < 2:
            return {"status": "error", "message": "Syntax: GPLAY TOYBOX SET <profile_id>"}
        profile_id = params[1].lower()
        try:
            active = gameplay.set_active_toybox(profile_id, username=username)
            return {
                "status": "success",
                "message": f"Active TOYBOX set to {active}",
                "toybox": {"active_profile": active},
                "output": f"Active TOYBOX: {active}",
            }
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}

    def _handle_proceed(self, gameplay) -> Dict:
        if gameplay.can_proceed():
            return {
                "status": "success",
                "message": "Gameplay gate satisfied. Next step unlocked.",
                "can_proceed": True,
                "output": "UNLOCK/PROCEED/NEXT STEP available: dungeon gate complete.",
            }
        return {
            "status": "blocked",
            "message": "Gate not satisfied: complete dungeon_l32_amulet first.",
            "can_proceed": False,
            "required_gate": "dungeon_l32_amulet",
            "output": "Blocked: complete dungeon level 32 and retrieve the Amulet of Yendor.",
        }

    def _status_block(self, snapshot: Dict) -> Dict:
        stats = snapshot.get("stats", {})
        active = snapshot.get("toybox", {}).get("active_profile", "hethack")
        gate = snapshot.get("gates", {}).get("dungeon_l32_amulet", {})
        gate_state = "done" if gate.get("completed") else "pending"

        output = "\n".join(
            [
                "GPLAY STATUS",
                f"User: {snapshot.get('username')} ({snapshot.get('role')})",
                f"TOYBOX: {active}",
                f"XP={stats.get('xp', 0)} HP={stats.get('hp', 100)} Gold={stats.get('gold', 0)}",
                f"Level={snapshot.get('progress', {}).get('level', 1)} AchievementLevel={snapshot.get('progress', {}).get('achievement_level', 0)}",
                f"Gate dungeon_l32_amulet: {gate_state}",
            ]
        )

        return {
            "status": "success",
            "message": "Gameplay status",
            "output": output,
            "player_stats": stats,
            "gameplay": snapshot,
        }
