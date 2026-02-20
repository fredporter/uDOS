"""PLAY command handler - progression stats, gates, TOYBOX profiles, and map runtime loop."""

from __future__ import annotations

from typing import Dict, List

from .base import BaseCommandHandler
from core.services.error_contract import CommandError


class GameplayHandler(BaseCommandHandler):
    """Handle gameplay scaffolding commands.

    Commands:
      PLAY
      PLAY STATUS
      PLAY STATS
      PLAY STATS SET <xp|hp|gold> <value>
      PLAY STATS ADD <xp|hp|gold> <delta>
      PLAY MAP STATUS
      PLAY MAP ENTER <place_id>
      PLAY MAP MOVE <target_place_id>
      PLAY MAP INSPECT
      PLAY MAP INTERACT <interaction_id>
      PLAY MAP COMPLETE <objective_id>
      PLAY MAP TICK [steps]
      PLAY GATE STATUS
      PLAY GATE COMPLETE <gate_id>
      PLAY GATE RESET <gate_id>
      PLAY TOYBOX LIST
      PLAY TOYBOX SET <hethack|elite|rpgbbs|crawler3d>
      PLAY LENS STATUS
      PLAY LENS ENABLE
      PLAY LENS DISABLE
      PLAY PROCEED
      PLAY NEXT
      PLAY UNLOCK
    """

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        from core.services.gameplay_service import get_gameplay_service
        from core.services.user_service import get_user_manager

        user_mgr = get_user_manager()
        current_user = user_mgr.current()
        if not current_user:
            raise CommandError(
                code="ERR_AUTH_REQUIRED",
                message="No active user",
                recovery_hint="Run SETUP to create a user profile",
                level="INFO",
            )

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

        if sub == "map":
            return self._handle_map(gameplay, username, role, params[1:])

        if sub == "gate":
            return self._handle_gate(gameplay, role, params[1:])

        if sub == "toybox":
            return self._handle_toybox(gameplay, username, role, params[1:])

        if sub == "lens":
            return self._handle_lens(gameplay, username, role, params[1:])

        if sub in {"proceed", "unlock", "next"}:
            return self._handle_proceed(gameplay)

        if sub in {"help", "-h", "--help"}:
            return {
                "status": "success",
                "message": self.__doc__ or "PLAY help",
                "output": (self.__doc__ or "PLAY help").strip(),
            }

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message=f"Unknown PLAY subcommand: {sub}",
            recovery_hint="Use PLAY --help to see available subcommands",
            level="INFO",
        )

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
            raise CommandError(
                code="ERR_AUTH_PERMISSION_DENIED",
                message="Permission denied: gameplay.mutate",
                recovery_hint="Switch to a user with gameplay permissions",
                level="WARNING",
            )

        action = params[0].lower()
        if len(params) < 3:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: PLAY STATS <SET|ADD> <xp|hp|gold> <value>",
                recovery_hint="Usage: PLAY STATS SET xp 10",
                level="INFO",
            )
        stat = params[1].lower()
        try:
            value = int(params[2])
        except ValueError:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Value must be an integer",
                recovery_hint="Use a numeric value, e.g., PLAY STATS ADD gold 5",
                level="INFO",
            )

        if action == "set":
            stats = gameplay.set_user_stat(username, stat, value)
        elif action == "add":
            stats = gameplay.add_user_stat(username, stat, value)
        else:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Use SET or ADD",
                recovery_hint="Usage: PLAY STATS SET xp 10",
                level="INFO",
            )

        self.set_state("player_stats", stats)
        return {
            "status": "success",
            "message": f"Updated {stat}",
            "player_stats": stats,
            "output": f"XP={stats['xp']} HP={stats['hp']} Gold={stats['gold']}",
        }

    def _handle_map(self, gameplay, username: str, role: str, params: List[str]) -> Dict:
        from core.services.map_runtime_service import get_map_runtime_service

        runtime = get_map_runtime_service()
        action = params[0].lower() if params else "status"

        if action in {"status", "show"}:
            status = runtime.status(username)
            if not status.get("ok"):
                raise CommandError(
                    code="ERR_SERVICE_UNAVAILABLE",
                    message=status.get("error", "Map runtime unavailable"),
                    recovery_hint="Start required services or run HEALTH for diagnostics",
                    level="ERROR",
                )
            snapshot = gameplay.snapshot(username, role)
            return {
                "status": "success",
                "message": "Map runtime status",
                "map": status,
                "progress": snapshot.get("progress", {}),
                "output": self._format_map_status(status, snapshot),
            }

        if not gameplay.has_permission(role, "gameplay.mutate"):
            raise CommandError(
                code="ERR_AUTH_PERMISSION_DENIED",
                message="Permission denied: gameplay.mutate",
                recovery_hint="Switch to a user with gameplay permissions",
                level="WARNING",
            )

        if action == "enter":
            target = self._require_arg(params, 1, "PLAY MAP ENTER <place_id>")
            result = runtime.enter(username, target)
        elif action == "move":
            target = self._require_arg(params, 1, "PLAY MAP MOVE <target_place_id>")
            result = runtime.move(username, target)
        elif action == "inspect":
            result = runtime.inspect(username)
        elif action == "interact":
            point = self._require_arg(params, 1, "PLAY MAP INTERACT <interaction_id>")
            result = runtime.interact(username, point)
        elif action == "complete":
            objective = self._require_arg(params, 1, "PLAY MAP COMPLETE <objective_id>")
            result = runtime.complete(username, objective)
        elif action == "tick":
            steps = 1
            if len(params) >= 2:
                try:
                    steps = int(params[1])
                except ValueError:
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="Steps must be an integer",
                        recovery_hint="Usage: PLAY MAP TICK 1",
                        level="INFO",
                    )
            result = runtime.tick(username, steps)
        else:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: PLAY MAP <STATUS|ENTER|MOVE|INSPECT|INTERACT|COMPLETE|TICK>",
                recovery_hint="Use PLAY MAP STATUS to see map state",
                level="INFO",
            )

        if not result.get("ok"):
            return {
                "status": "blocked",
                "message": result.get("error", "Map action blocked"),
                "map_action": result,
            }

        tick_result = gameplay.tick(username)
        status = runtime.status(username)
        snapshot = gameplay.snapshot(username, role)
        return {
            "status": "success",
            "message": f"Map action complete: {result.get('action', action).lower()}",
            "map": status,
            "map_action": result,
            "tick": tick_result,
            "progress": snapshot.get("progress", {}),
            "player_stats": snapshot.get("stats", {}),
            "output": self._format_map_action(result, status, snapshot),
        }

    def _require_arg(self, params: List[str], index: int, syntax: str) -> str:
        if len(params) <= index:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message=f"Syntax: {syntax}",
                recovery_hint=f"Usage: {syntax}",
                level="INFO",
            )
        value = str(params[index]).strip()
        if not value:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message=f"Syntax: {syntax}",
                recovery_hint=f"Usage: {syntax}",
                level="INFO",
            )
        return value

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
            raise CommandError(
                code="ERR_AUTH_PERMISSION_DENIED",
                message="Permission denied: gameplay.gate_admin",
                recovery_hint="Switch to a user with gate admin permissions",
                level="WARNING",
            )
        if len(params) < 2:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: PLAY GATE <COMPLETE|RESET> <gate_id>",
                recovery_hint="Usage: PLAY GATE STATUS or PLAY GATE COMPLETE <gate_id>",
                level="INFO",
            )

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
        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Use STATUS, COMPLETE, or RESET",
            recovery_hint="Usage: PLAY GATE STATUS",
            level="INFO",
        )

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
            raise CommandError(
                code="ERR_AUTH_PERMISSION_DENIED",
                message="Permission denied: toybox.admin",
                recovery_hint="Switch to a user with toybox admin permissions",
                level="WARNING",
            )

        action = params[0].lower()
        if action != "set" or len(params) < 2:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: PLAY TOYBOX SET <profile_id>",
                recovery_hint="Usage: PLAY TOYBOX LIST to see profiles",
                level="INFO",
            )
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
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message=str(exc),
                recovery_hint="Use PLAY TOYBOX LIST to see profiles",
                level="INFO",
            )

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

    def _handle_lens(self, gameplay, username: str, role: str, params: List[str]) -> Dict:
        from core.services.map_runtime_service import get_map_runtime_service
        from core.services.world_lens_service import get_world_lens_service

        action = params[0].lower() if params else "status"
        runtime = get_map_runtime_service()
        world_lens = get_world_lens_service()

        if action in {"status", "show"}:
            map_status = runtime.status(username)
            lens_status = world_lens.status(
                username=username,
                map_status=map_status,
                progression_ready=gameplay.can_proceed(),
            )
            return {
                "status": "success",
                "message": "World lens status",
                "lens": lens_status,
                "output": self._format_lens_status(lens_status),
            }

        if action not in {"enable", "disable"}:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: PLAY LENS <STATUS|ENABLE|DISABLE>",
                recovery_hint="Usage: PLAY LENS STATUS",
                level="INFO",
            )

        if not gameplay.has_permission(role, "gameplay.gate_admin"):
            raise CommandError(
                code="ERR_AUTH_PERMISSION_DENIED",
                message="Permission denied: gameplay.gate_admin",
                recovery_hint="Switch to a user with gate admin permissions",
                level="WARNING",
            )

        world_lens.set_enabled(action == "enable", actor=f"gplay:{username}")
        map_status = runtime.status(username)
        lens_status = world_lens.status(
            username=username,
            map_status=map_status,
            progression_ready=gameplay.can_proceed(),
        )
        verb = "enabled" if action == "enable" else "disabled"
        return {
            "status": "success",
            "message": f"World lens {verb}",
            "lens": lens_status,
            "output": self._format_lens_status(lens_status),
        }

    def _status_block(self, snapshot: Dict) -> Dict:
        stats = snapshot.get("stats", {})
        active = snapshot.get("toybox", {}).get("active_profile", "hethack")
        gate = snapshot.get("gates", {}).get("dungeon_l32_amulet", {})
        gate_state = "done" if gate.get("completed") else "pending"

        output = "\n".join(
            [
                "PLAY STATUS",
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

    def _format_map_status(self, status: Dict, snapshot: Dict) -> str:
        progress = snapshot.get("progress", {})
        metrics = progress.get("metrics", {})
        return "\n".join(
            [
                "PLAY MAP STATUS",
                f"Place: {status.get('current_place_id')} ({status.get('label')})",
                f"Loc: {status.get('place_ref')} z={status.get('z')}",
                f"Chunk2D: {status.get('chunk', {}).get('chunk2d_id')}",
                f"Links: {len(status.get('links', []))} Portals: {len(status.get('portals', []))}",
                f"Tick={status.get('tick_counter')} NPC={status.get('npc_phase')} World={status.get('world_phase')}",
                f"Metrics moves={metrics.get('map_moves', 0)} inspects={metrics.get('map_inspects', 0)} interactions={metrics.get('map_interactions', 0)} completions={metrics.get('map_completions', 0)}",
            ]
        )

    def _format_map_action(self, action_result: Dict, status: Dict, snapshot: Dict) -> str:
        stats = snapshot.get("stats", {})
        progress = snapshot.get("progress", {})
        return "\n".join(
            [
                f"PLAY MAP {action_result.get('action', 'ACTION')}",
                f"Place: {status.get('current_place_id')} ({status.get('label')})",
                f"Chunk2D: {status.get('chunk', {}).get('chunk2d_id')}",
                f"XP={stats.get('xp', 0)} HP={stats.get('hp', 100)} Gold={stats.get('gold', 0)}",
                f"Level={progress.get('level', 1)} AchievementLevel={progress.get('achievement_level', 0)}",
            ]
        )

    def _format_lens_status(self, lens_status: Dict) -> str:
        lens = lens_status.get("lens", {})
        region = lens_status.get("single_region", {})
        contract = lens_status.get("slice_contract", {})
        state = "ready" if lens.get("ready") else "blocked"
        reason = lens.get("blocking_reason") or "none"
        return "\n".join(
            [
                "PLAY LENS STATUS",
                f"Version: {lens_status.get('version')}",
                f"Enabled: {lens.get('enabled')} ({lens.get('enabled_source')})",
                f"Slice: {region.get('id')} entry={region.get('entry_place_id')} active={region.get('active')}",
                f"Contract: valid={contract.get('valid')} places={len(contract.get('allowed_place_ids', []))}",
                f"State: {state} reason={reason}",
            ]
        )
