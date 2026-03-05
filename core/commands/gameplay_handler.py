"""PLAY command handler - progression stats, gates, TOYBOX profiles, and map runtime loop."""

from __future__ import annotations

from typing import Dict, List

from .base import BaseCommandHandler
from core.services.compact_status_service import format_compact_status
from core.services.error_contract import CommandError
from core.services.progression_contract_service import build_progression_contract


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
      PLAY GUI STATUS
      PLAY GUI OPEN [profile]
      PLAY GUI INTENT [profile]
    PLAY LENS LIST
    PLAY LENS SHOW
      PLAY LENS SET <lens>
      PLAY LENS STATUS
      PLAY LENS SCORE [lens] [--compact]
      PLAY LENS CHECKPOINTS [lens] [--compact]
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

        if sub == "gui":
            return self._handle_gui(gameplay, username, params[1:])

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

    def _handle_gui(self, gameplay, username: str, params: List[str]) -> Dict:
        from core.services.thin_gui_bridge_service import get_thin_gui_bridge_service

        bridge = get_thin_gui_bridge_service()
        action = params[0].lower() if params else "status"
        profile = params[1].lower() if len(params) > 1 and params[1].strip() else gameplay.get_active_toybox()
        launch = bridge.resolve_target(profile)
        route = bridge.wizard_route(launch)

        if action in {"status", "show"}:
            lines = [
                "PLAY GUI STATUS",
                f"Profile: {launch.profile_id}",
                f"Mode: {launch.mode}",
                f"Owner: {launch.extension_owner}",
                f"Target: {launch.target_url or '(unset)'}",
                f"Wizard route: {route}",
            ]
            if not launch.target_url:
                lines.append(
                    "Set UDOS_THINGUI_TARGET_<PROFILE> to map a runtime URL before launch."
                )
            return {
                "status": "success",
                "message": "Gameplay GUI bridge status",
                "gui": {
                    "profile": launch.profile_id,
                    "target": launch.target_url,
                    "mode": launch.mode,
                    "owner": launch.extension_owner,
                    "route": route,
                },
                "output": "\n".join(lines),
            }

        if action == "open":
            return {
                "status": "success",
                "message": f"Gameplay GUI route ready for {launch.profile_id}",
                "route": route,
                "gui": {"profile": launch.profile_id, "target": launch.target_url},
                "output": "\n".join(
                    [
                        f"PLAY GUI OPEN {launch.profile_id}",
                        f"Wizard route: {route}",
                    ]
                ),
            }

        if action == "intent":
            payload = bridge.write_intent(launch)
            return {
                "status": "success",
                "message": f"Gameplay GUI intent written for {launch.profile_id}",
                "intent": payload,
                "output": "\n".join(
                    [
                        f"PLAY GUI INTENT {launch.profile_id}",
                        f"Intent saved: {bridge.intent_path}",
                        f"Target: {launch.target_url or '(unset)'}",
                    ]
                ),
            }

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Syntax: PLAY GUI <STATUS|OPEN|INTENT> [profile]",
            recovery_hint="Usage: PLAY GUI OPEN crawler3d",
            level="INFO",
        )

    def _handle_lens(self, gameplay, username: str, role: str, params: List[str]) -> Dict:
        from core.services.map_runtime_service import get_map_runtime_service
        from core.services.lens_service import get_lens_service
        from core.services.world_lens_service import get_world_lens_service

        action = params[0].lower() if params else "status"
        runtime = get_map_runtime_service()
        lens_service = get_lens_service()
        world_lens = get_world_lens_service()

        if action in {"list", "ls"}:
            active = gameplay.get_active_toybox()
            profiles = gameplay.get_toybox_profiles()
            lines = [f"Active lens: {active}", "Available lenses:"]
            for profile_id, profile in profiles.items():
                marker = "*" if profile_id == active else " "
                lines.append(f"{marker} {profile_id} -> {profile.get('container_id')}")
            return {
                "status": "success",
                "message": "Lens profiles",
                "lens": {"active": active, "profiles": profiles},
                "output": "\n".join(lines),
            }

        if action in {"show", "info"}:
            active = gameplay.get_active_toybox()
            target = params[1].lower() if len(params) > 1 else active
            lens = lens_service.get_lens(name=target)
            meta = lens.get_metadata()
            lines = [
                f"LENS SHOW {target}",
                f"Name: {meta.get('name', target)}",
                f"Description: {meta.get('description', '')}",
                f"Supported: {meta.get('supported_variants', '')}",
            ]
            return {
                "status": "success",
                "message": f"Lens info: {target}",
                "lens": meta,
                "output": "\n".join(lines),
            }

        if action in {"set", "use"}:
            target = params[1].lower() if len(params) > 1 else ""
            if not target:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Syntax: PLAY LENS SET <lens>",
                    recovery_hint="Usage: PLAY LENS LIST to see lenses",
                    level="INFO",
                )
            if not gameplay.has_permission(role, "toybox.admin"):
                raise CommandError(
                    code="ERR_AUTH_PERMISSION_DENIED",
                    message="Permission denied: toybox.admin",
                    recovery_hint="Switch to a user with toybox admin permissions",
                    level="WARNING",
                )
            try:
                active = gameplay.set_active_toybox(target, username=username)
            except ValueError as exc:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=str(exc),
                    recovery_hint="Use PLAY LENS LIST to see lenses",
                    level="INFO",
                )
            return {
                "status": "success",
                "message": f"Active lens set to {active}",
                "lens": {"active": active},
                "output": f"Active lens: {active}",
            }

        if action == "status":
            compact = any(str(item).strip().lower() in {"--compact", "compact"} for item in params[1:])
            map_status = runtime.status(username)
            progression = gameplay.progression_snapshot(username)
            lens_status = world_lens.status(
                username=username,
                map_status=map_status,
                progression_ready=gameplay.can_proceed(),
            )
            return {
                "status": "success",
                "message": "World lens status",
                "lens": lens_status,
                "progression": progression,
                "output": self._format_lens_status(lens_status, progression, compact=compact),
            }

        if action == "score":
            compact = any(str(item).strip().lower() in {"--compact", "compact"} for item in params[1:])
            target = next(
                (
                    str(item).strip().lower()
                    for item in params[1:]
                    if str(item).strip() and str(item).strip().lower() not in {"--compact", "compact"}
                ),
                gameplay.get_active_toybox(),
            )
            score_view = gameplay.lens_score_view(username, target)
            return {
                "status": "success",
                "message": f"Lens score view: {target}",
                "lens_score": score_view,
                "output": self._format_lens_score(score_view, compact=compact),
            }

        if action == "checkpoints":
            compact = any(str(item).strip().lower() in {"--compact", "compact"} for item in params[1:])
            target = next(
                (
                    str(item).strip().lower()
                    for item in params[1:]
                    if str(item).strip() and str(item).strip().lower() not in {"--compact", "compact"}
                ),
                gameplay.get_active_toybox(),
            )
            checkpoint_view = gameplay.list_lens_checkpoints(username, target)
            return {
                "status": "success",
                "message": f"Lens checkpoints: {target}",
                "lens_checkpoints": checkpoint_view,
                "output": self._format_lens_checkpoints(checkpoint_view, compact=compact),
            }

        if action not in {"enable", "disable"}:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: PLAY LENS <STATUS|SCORE|CHECKPOINTS|ENABLE|DISABLE>",
                recovery_hint="Usage: PLAY LENS LIST",
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
        progression = gameplay.progression_snapshot(username)
        verb = "enabled" if action == "enable" else "disabled"
        return {
            "status": "success",
            "message": f"World lens {verb}",
            "lens": lens_status,
            "progression": progression,
            "output": self._format_lens_status(lens_status, progression),
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

    def _format_lens_status(
        self,
        lens_status: Dict,
        progression: Dict | None = None,
        *,
        compact: bool = False,
    ) -> str:
        lens = lens_status.get("lens", {})
        region = lens_status.get("single_region", {})
        contract = lens_status.get("slice_contract", {})
        state = "ready" if lens.get("ready") else "blocked"
        reason = lens.get("blocking_reason") or "none"
        summary_line = ""
        hint_line = ""
        readiness_line = ""
        recommendation_line = ""
        if isinstance(progression, dict):
            contract = build_progression_contract(progression)
            stats = progression.get("stats", {}) if isinstance(progression.get("stats"), dict) else {}
            p = progression.get("progress", {}) if isinstance(progression.get("progress"), dict) else {}
            summary_line = (
                f"Progression: XP={stats.get('xp', 0)} Gold={stats.get('gold', 0)} "
                f"Level={p.get('level', 1)} AchievementLevel={p.get('achievement_level', 0)}"
            )
            blocked = progression.get("blocked_requirements", [])
            if isinstance(blocked, list) and blocked:
                hint_line = f"Next unlock hints: {', '.join(str(x) for x in blocked[:3])}"
            active_lens = str(contract.get("active_lens", "")).strip().lower()
            readiness = contract.get("lens_readiness", {}).get(active_lens)
            if isinstance(readiness, dict):
                readiness_line = (
                    f"Readiness: {'ready' if readiness.get('available') else 'blocked'} "
                    f"(option={readiness.get('option_id')})"
                )
                if recommendation := readiness.get("recommendation"):
                    recommendation_line = f"Recommendation: {recommendation}"
        if compact:
            compact_fields: dict[str, object] = {
                "enabled": lens.get("enabled"),
                "slice": region.get("id"),
                "contract": contract.get("valid"),
                "reason": reason,
            }
            if isinstance(progression, dict):
                normalized = build_progression_contract(progression)
                variables = normalized.get("variables", {})
                compact_fields["xp"] = variables.get("xp", 0)
                compact_fields["gold"] = variables.get("gold", 0)
                compact_fields["ach"] = variables.get("achievement_level", 0)
                active_lens = str(normalized.get("active_lens", "")).strip().lower()
                readiness = normalized.get("lens_readiness", {}).get(active_lens)
                if isinstance(readiness, dict):
                    compact_fields["ready"] = "yes" if readiness.get("available") else "no"
                    if recommendation := readiness.get("recommendation"):
                        compact_fields["next"] = recommendation
                blocked = progression.get("blocked_requirements", [])
                if isinstance(blocked, list) and blocked:
                    compact_fields["hints"] = ",".join(str(x) for x in blocked[:3])
            return format_compact_status(
                f"LENS:{state}",
                compact_fields,
                order=["enabled", "slice", "contract", "reason", "ready", "xp", "gold", "ach", "next", "hints"],
            )
        return "\n".join(
            [
                line
                for line in [
                    "PLAY LENS STATUS",
                    f"Version: {lens_status.get('version')}",
                    f"Enabled: {lens.get('enabled')} ({lens.get('enabled_source')})",
                    f"Slice: {region.get('id')} entry={region.get('entry_place_id')} active={region.get('active')}",
                    f"Contract: valid={contract.get('valid')} places={len(contract.get('allowed_place_ids', []))}",
                    f"State: {state} reason={reason}",
                    summary_line,
                    readiness_line,
                    recommendation_line,
                    hint_line,
                ]
                if line
            ]
        )

    def _format_lens_score(self, score_view: Dict, *, compact: bool = False) -> str:
        lens = str(score_view.get("lens", "unknown"))
        score = score_view.get("score", {}) if isinstance(score_view.get("score"), dict) else {}
        variables = score_view.get("variables", {}) if isinstance(score_view.get("variables"), dict) else {}
        metrics = score_view.get("metrics", {}) if isinstance(score_view.get("metrics"), dict) else {}
        if compact:
            return format_compact_status(
                f"LENS:SCORE:{lens}",
                {
                    "total": score.get("total", 0),
                    "tier": score.get("tier", "initiate"),
                    "cp": f"{score.get('completed_checkpoints', 0)}/{score.get('total_checkpoints', 0)}",
                    "xp": variables.get("xp", 0),
                    "gold": variables.get("gold", 0),
                    "ach": variables.get("achievement_level", 0),
                },
                order=["total", "tier", "cp", "xp", "gold", "ach"],
            )
        metric_pairs = " ".join(f"{k}={v}" for k, v in sorted(metrics.items()))
        return "\n".join(
            [
                f"PLAY LENS SCORE {lens}",
                f"Total={score.get('total', 0)} Tier={score.get('tier', 'initiate')}",
                (
                    f"Checkpoints={score.get('completed_checkpoints', 0)}"
                    f"/{score.get('total_checkpoints', 0)}"
                ),
                (
                    f"XP={variables.get('xp', 0)} HP={variables.get('hp', 100)} Gold={variables.get('gold', 0)} "
                    f"Level={variables.get('level', 1)} AchievementLevel={variables.get('achievement_level', 0)}"
                ),
                f"Metrics: {metric_pairs}",
            ]
        )

    def _format_lens_checkpoints(self, checkpoint_view: Dict, *, compact: bool = False) -> str:
        lens = str(checkpoint_view.get("lens", "unknown"))
        summary = checkpoint_view.get("summary", {}) if isinstance(checkpoint_view.get("summary"), dict) else {}
        checkpoints = checkpoint_view.get("checkpoints", [])
        if compact:
            next_checkpoint = summary.get("next_checkpoint")
            next_id = (
                str(next_checkpoint.get("id", "none"))
                if isinstance(next_checkpoint, dict)
                else "none"
            )
            return format_compact_status(
                f"LENS:CHECKPOINTS:{lens}",
                {
                    "done": summary.get("completed", 0),
                    "total": summary.get("total", 0),
                    "next": next_id,
                },
                order=["done", "total", "next"],
            )
        lines = [f"PLAY LENS CHECKPOINTS {lens}"]
        lines.append(f"Completed={summary.get('completed', 0)}/{summary.get('total', 0)}")
        if isinstance(summary.get("next_checkpoint"), dict):
            next_checkpoint = summary["next_checkpoint"]
            lines.append(
                f"Next: {next_checkpoint.get('id')} ({', '.join(next_checkpoint.get('blocked_by', [])) or 'ready'})"
            )
        for row in checkpoints if isinstance(checkpoints, list) else []:
            if not isinstance(row, dict):
                continue
            status = "done" if row.get("completed") else "pending"
            blocked = ", ".join(row.get("blocked_by", []))
            suffix = f" ({blocked})" if blocked else ""
            lines.append(f"- {row.get('id')}: {status}{suffix}")
        return "\n".join(lines)
