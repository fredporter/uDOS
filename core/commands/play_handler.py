"""PLAY command handler - conditional gameplay options and token unlocks."""

from __future__ import annotations

from typing import Dict, List

from .base import BaseCommandHandler
from .gameplay_handler import GameplayHandler
from core.services.error_contract import CommandError


class PlayHandler(BaseCommandHandler):
    """Handle PLAY command surface.

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
            PLAY LENS ENABLE
            PLAY LENS DISABLE
      PLAY PROCEED
      PLAY NEXT
      PLAY UNLOCK
      PLAY OPTIONS
      PLAY START <option_id>
      PLAY TOKENS
      PLAY CLAIM
      PLAY PROFILE STATUS [--group <group_id>] [--session <session_id>]
      PLAY PROFILE GROUP SET <group_id> <variable> <value>
      PLAY PROFILE GROUP CLEAR <group_id> [variable]
      PLAY PROFILE SESSION SET <session_id> <variable> <value>
      PLAY PROFILE SESSION CLEAR <session_id> [variable]
    """

    _GAMEPLAY_SUBCOMMANDS = {
        "stats",
        "map",
        "gate",
        "toybox",
        "gui",
        "lens",
        "proceed",
        "next",
        "unlock",
    }

    def __init__(self) -> None:
        super().__init__()
        self._gameplay = GameplayHandler()

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        from core.services.gameplay_service import get_gameplay_service
        from core.services.user_service import get_user_manager

        current_user = get_user_manager().current()
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
        canonical = "PLAY"

        if not params:
            return self._status(gameplay, username, role, cmd_name=canonical)

        sub = params[0].lower()
        if sub in {"status", "show"}:
            return self._status(gameplay, username, role, cmd_name=canonical)

        if sub in self._GAMEPLAY_SUBCOMMANDS:
            return self._gameplay.handle("PLAY", params, grid=grid, parser=parser)
        if sub == "profile":
            return self._profile(gameplay, username, role, params[1:], cmd_name=canonical)

        if sub in {"options", "list"}:
            return self._options(gameplay, username, cmd_name=canonical)
        if sub in {"tokens", "token"}:
            return self._tokens(gameplay, username, cmd_name=canonical)
        if sub == "claim":
            unlocked = gameplay.evaluate_unlock_tokens(username)
            if unlocked:
                out = [f"{canonical} CLAIM", "New unlock tokens:"]
                for row in unlocked:
                    out.append(f"- {row.get('id')}")
                return {
                    "status": "success",
                    "message": f"{canonical} tokens unlocked",
                    "unlocked_tokens": unlocked,
                    "output": "\n".join(out),
                }
            return {
                "status": "success",
                "message": f"No new {canonical} unlock tokens",
                "unlocked_tokens": [],
                "output": f"{canonical} CLAIM: no new unlock tokens.",
            }
        if sub == "start":
            if len(params) < 2:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=f"Syntax: {canonical} START <option_id>",
                    recovery_hint=f"Usage: {canonical} START <option_id>",
                    level="INFO",
                )
            option_id = params[1].lower()
            try:
                result = gameplay.start_play_option(username, option_id)
            except ValueError as exc:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=str(exc),
                    recovery_hint=f"Use {canonical} OPTIONS to list available options",
                    level="INFO",
                )
            if result.get("status") == "blocked":
                return {
                    "status": "blocked",
                    "message": result.get("message", f"{canonical} option blocked: {option_id}"),
                    "blocked_by": result.get("blocked_by", []),
                    "output": "Blocked: " + ", ".join(result.get("blocked_by", [])),
                }
            unlocked = result.get("unlocked_tokens", [])
            output = [f"{canonical} START {option_id}", "Started."]
            if unlocked:
                output.append("Unlock tokens:")
                for row in unlocked:
                    output.append(f"- {row.get('id')}")
            return {
                "status": "success",
                "message": result.get("message", f"{canonical} option started: {option_id}"),
                "play": result,
                "output": "\n".join(output),
            }
        if sub in {"help", "-h", "--help"}:
            return {
                "status": "success",
                "message": self.__doc__ or f"{canonical} help",
                "output": (self.__doc__ or f"{canonical} help").strip(),
            }
        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message=f"Unknown {canonical} subcommand: {sub}",
            recovery_hint=f"Use {canonical} --help to see available subcommands",
            level="INFO",
        )

    def _status(self, gameplay, username: str, role: str, cmd_name: str = "PLAY") -> Dict:
        snapshot = gameplay.snapshot(username, role)
        stats = snapshot.get("stats", {})
        progress = snapshot.get("progress", {})
        toybox = snapshot.get("toybox", {}).get("active_profile", "hethack")
        gate = snapshot.get("gates", {}).get("dungeon_l32_amulet", {})
        gate_state = "done" if gate.get("completed") else "pending"
        lines = [
            f"{cmd_name} STATUS",
            f"XP={stats.get('xp', 0)} HP={stats.get('hp', 100)} Gold={stats.get('gold', 0)}",
            f"Level={progress.get('level', 1)} AchievementLevel={progress.get('achievement_level', 0)}",
            f"UnlockTokens={len(snapshot.get('unlock_tokens', []))}",
            f"TOYBOX={toybox}",
            f"Gate dungeon_l32_amulet={gate_state}",
        ]
        return {
            "status": "success",
            "message": f"{cmd_name} status",
            "play": {
                "stats": stats,
                "progress": progress,
                "unlock_tokens": snapshot.get("unlock_tokens", []),
                "options": snapshot.get("play_options", []),
            },
            "output": "\n".join(lines),
        }

    def _options(self, gameplay, username: str, cmd_name: str = "PLAY") -> Dict:
        options = gameplay.list_play_options(username)
        lines = [f"{cmd_name} OPTIONS"]
        for row in options:
            state = "open" if row.get("available") else "locked"
            line = f"- {row.get('id')}: {state}"
            if not row.get("available"):
                blocked = ", ".join(row.get("blocked_by", []))
                line += f" ({blocked})"
            lines.append(line)
        return {
            "status": "success",
            "message": f"{cmd_name} options",
            "options": options,
            "output": "\n".join(lines),
        }

    def _tokens(self, gameplay, username: str, cmd_name: str = "PLAY") -> Dict:
        tokens = gameplay.get_user_unlock_tokens(username)
        lines = [f"{cmd_name} TOKENS"]
        if not tokens:
            lines.append("- none")
        for row in tokens:
            lines.append(f"- {row.get('id')} ({row.get('source')})")
        return {
            "status": "success",
            "message": f"{cmd_name} unlock tokens",
            "unlock_tokens": tokens,
            "output": "\n".join(lines),
        }

    def _profile(self, gameplay, username: str, role: str, params: List[str], cmd_name: str = "PLAY") -> Dict:
        if not params or params[0].lower() in {"status", "show"}:
            group_id, session_id = self._profile_context(
                params[1:] if params and params[0].lower() in {"status", "show"} else params
            )
            profile = gameplay.resolve_profile_variables(
                username,
                group_id=group_id,
                session_id=session_id,
            )
            return {
                "status": "success",
                "message": f"{cmd_name} profile status",
                "profile": profile,
                "output": self._format_profile(profile, cmd_name=cmd_name),
            }

        if not gameplay.has_permission(role, "gameplay.mutate"):
            raise CommandError(
                code="ERR_AUTH_PERMISSION_DENIED",
                message="Permission denied: gameplay.mutate",
                recovery_hint="Switch to a user with gameplay permissions",
                level="WARNING",
            )

        scope = params[0].lower()
        if scope not in {"group", "session"}:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message=f"Syntax: {cmd_name} PROFILE <STATUS|GROUP|SESSION> ...",
                recovery_hint=f"Usage: {cmd_name} PROFILE STATUS --group alpha --session run-1",
                level="INFO",
            )
        if len(params) < 2:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message=f"Syntax: {cmd_name} PROFILE {scope.upper()} <SET|CLEAR> ...",
                recovery_hint=f"Usage: {cmd_name} PROFILE {scope.upper()} SET <id> xp 10",
                level="INFO",
            )
        action = params[1].lower()

        if action == "set":
            if len(params) < 5:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=f"Syntax: {cmd_name} PROFILE {scope.upper()} SET <id> <variable> <value>",
                    recovery_hint=f"Usage: {cmd_name} PROFILE {scope.upper()} SET alpha xp 10",
                    level="INFO",
                )
            overlay_id = params[2]
            variable = params[3]
            try:
                value = int(params[4])
            except ValueError:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Overlay value must be an integer",
                    recovery_hint=f"Usage: {cmd_name} PROFILE {scope.upper()} SET alpha xp 10",
                    level="INFO",
                )
            try:
                overlay = gameplay.set_profile_overlay(scope, overlay_id, variable, value)
            except ValueError as exc:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=str(exc),
                    recovery_hint=f"Usage: {cmd_name} PROFILE {scope.upper()} SET alpha xp 10",
                    level="INFO",
                )
            profile = gameplay.resolve_profile_variables(
                username,
                group_id=overlay_id if scope == "group" else None,
                session_id=overlay_id if scope == "session" else None,
            )
            return {
                "status": "success",
                "message": f"{cmd_name} profile overlay updated",
                "overlay": overlay,
                "profile": profile,
                "output": self._format_profile(profile, cmd_name=cmd_name),
            }

        if action == "clear":
            if len(params) < 3:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=f"Syntax: {cmd_name} PROFILE {scope.upper()} CLEAR <id> [variable]",
                    recovery_hint=f"Usage: {cmd_name} PROFILE {scope.upper()} CLEAR alpha xp",
                    level="INFO",
                )
            overlay_id = params[2]
            variable = params[3] if len(params) > 3 else None
            try:
                overlay = gameplay.clear_profile_overlay(scope, overlay_id, variable)
            except ValueError as exc:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=str(exc),
                    recovery_hint=f"Usage: {cmd_name} PROFILE {scope.upper()} CLEAR alpha xp",
                    level="INFO",
                )
            profile = gameplay.resolve_profile_variables(
                username,
                group_id=overlay_id if scope == "group" else None,
                session_id=overlay_id if scope == "session" else None,
            )
            return {
                "status": "success",
                "message": f"{cmd_name} profile overlay cleared",
                "overlay": overlay,
                "profile": profile,
                "output": self._format_profile(profile, cmd_name=cmd_name),
            }

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message=f"Syntax: {cmd_name} PROFILE {scope.upper()} <SET|CLEAR> ...",
            recovery_hint=f"Usage: {cmd_name} PROFILE {scope.upper()} SET <id> xp 10",
            level="INFO",
        )

    def _profile_context(self, params: List[str]) -> tuple[str | None, str | None]:
        group_id: str | None = None
        session_id: str | None = None
        index = 0
        while index < len(params):
            token = str(params[index]).strip().lower()
            if token in {"--group", "group"}:
                if index + 1 < len(params):
                    group_id = str(params[index + 1]).strip()
                    index += 2
                    continue
                break
            if token in {"--session", "session"}:
                if index + 1 < len(params):
                    session_id = str(params[index + 1]).strip()
                    index += 2
                    continue
                break
            index += 1
        return group_id, session_id

    def _format_profile(self, profile: Dict, *, cmd_name: str = "PLAY") -> str:
        user = profile.get("user", {}) if isinstance(profile.get("user"), dict) else {}
        overlays = profile.get("overlays", {}) if isinstance(profile.get("overlays"), dict) else {}
        effective = profile.get("effective", {}) if isinstance(profile.get("effective"), dict) else {}
        user_variables = user.get("variables", {}) if isinstance(user.get("variables"), dict) else {}
        effective_variables = effective.get("variables", {}) if isinstance(effective.get("variables"), dict) else {}
        group_row = overlays.get("group")
        session_row = overlays.get("session")

        lines = [f"{cmd_name} PROFILE STATUS"]
        lines.append(
            f"User: XP={user_variables.get('xp', 0)} HP={user_variables.get('hp', 100)} "
            f"Gold={user_variables.get('gold', 0)} Level={user_variables.get('level', 1)} "
            f"AchievementLevel={user_variables.get('achievement_level', 0)}"
        )
        if isinstance(group_row, dict):
            lines.append(f"Group overlay: {group_row.get('id')}")
        if isinstance(session_row, dict):
            lines.append(f"Session overlay: {session_row.get('id')}")
        lines.append(
            f"Effective: XP={effective_variables.get('xp', 0)} HP={effective_variables.get('hp', 100)} "
            f"Gold={effective_variables.get('gold', 0)} Level={effective_variables.get('level', 1)} "
            f"AchievementLevel={effective_variables.get('achievement_level', 0)}"
        )
        return "\n".join(lines)
