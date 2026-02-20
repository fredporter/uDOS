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
    """

    _GAMEPLAY_SUBCOMMANDS = {
        "stats",
        "map",
        "gate",
        "toybox",
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
