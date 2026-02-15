"""PLAY command handler - conditional gameplay options and token unlocks."""

from __future__ import annotations

from typing import Dict, List

from .base import BaseCommandHandler


class PlayHandler(BaseCommandHandler):
    """Handle PLAY command surface.

    Commands:
      PLAY
      PLAY STATUS
      PLAY OPTIONS
      PLAY START <option_id>
      PLAY TOKENS
      PLAY CLAIM
    """

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        from core.services.gameplay_service import get_gameplay_service
        from core.services.user_service import get_user_manager

        current_user = get_user_manager().current()
        if not current_user:
            return {"status": "error", "message": "No active user"}

        gameplay = get_gameplay_service()
        username = current_user.username
        role = current_user.role.value
        gameplay.tick(username)

        if not params:
            return self._status(gameplay, username, role)

        sub = params[0].lower()
        if sub in {"status", "show"}:
            return self._status(gameplay, username, role)
        if sub in {"options", "list"}:
            return self._options(gameplay, username)
        if sub in {"tokens", "token"}:
            return self._tokens(gameplay, username)
        if sub == "claim":
            unlocked = gameplay.evaluate_unlock_tokens(username)
            if unlocked:
                out = ["PLAY CLAIM", "New unlock tokens:"]
                for row in unlocked:
                    out.append(f"- {row.get('id')}")
                return {
                    "status": "success",
                    "message": "PLAY tokens unlocked",
                    "unlocked_tokens": unlocked,
                    "output": "\n".join(out),
                }
            return {
                "status": "success",
                "message": "No new PLAY unlock tokens",
                "unlocked_tokens": [],
                "output": "PLAY CLAIM: no new unlock tokens.",
            }
        if sub == "start":
            if len(params) < 2:
                return {"status": "error", "message": "Syntax: PLAY START <option_id>"}
            option_id = params[1].lower()
            try:
                result = gameplay.start_play_option(username, option_id)
            except ValueError as exc:
                return {"status": "error", "message": str(exc)}
            if result.get("status") == "blocked":
                return {
                    "status": "blocked",
                    "message": result.get("message", f"PLAY option blocked: {option_id}"),
                    "blocked_by": result.get("blocked_by", []),
                    "output": "Blocked: " + ", ".join(result.get("blocked_by", [])),
                }
            unlocked = result.get("unlocked_tokens", [])
            output = [f"PLAY START {option_id}", "Started."]
            if unlocked:
                output.append("Unlock tokens:")
                for row in unlocked:
                    output.append(f"- {row.get('id')}")
            return {
                "status": "success",
                "message": result.get("message", f"PLAY option started: {option_id}"),
                "play": result,
                "output": "\n".join(output),
            }
        if sub in {"help", "-h", "--help"}:
            return {
                "status": "success",
                "message": self.__doc__ or "PLAY help",
                "output": (self.__doc__ or "PLAY help").strip(),
            }
        return {"status": "error", "message": f"Unknown PLAY subcommand: {sub}"}

    def _status(self, gameplay, username: str, role: str) -> Dict:
        snapshot = gameplay.snapshot(username, role)
        stats = snapshot.get("stats", {})
        progress = snapshot.get("progress", {})
        lines = [
            "PLAY STATUS",
            f"XP={stats.get('xp', 0)} HP={stats.get('hp', 100)} Gold={stats.get('gold', 0)}",
            f"Level={progress.get('level', 1)} AchievementLevel={progress.get('achievement_level', 0)}",
            f"UnlockTokens={len(snapshot.get('unlock_tokens', []))}",
        ]
        return {
            "status": "success",
            "message": "PLAY status",
            "play": {
                "stats": stats,
                "progress": progress,
                "unlock_tokens": snapshot.get("unlock_tokens", []),
                "options": snapshot.get("play_options", []),
            },
            "output": "\n".join(lines),
        }

    def _options(self, gameplay, username: str) -> Dict:
        options = gameplay.list_play_options(username)
        lines = ["PLAY OPTIONS"]
        for row in options:
            state = "open" if row.get("available") else "locked"
            line = f"- {row.get('id')}: {state}"
            if not row.get("available"):
                blocked = ", ".join(row.get("blocked_by", []))
                line += f" ({blocked})"
            lines.append(line)
        return {
            "status": "success",
            "message": "PLAY options",
            "options": options,
            "output": "\n".join(lines),
        }

    def _tokens(self, gameplay, username: str) -> Dict:
        tokens = gameplay.get_user_unlock_tokens(username)
        lines = ["PLAY TOKENS"]
        if not tokens:
            lines.append("- none")
        for row in tokens:
            lines.append(f"- {row.get('id')} ({row.get('source')})")
        return {
            "status": "success",
            "message": "PLAY unlock tokens",
            "unlock_tokens": tokens,
            "output": "\n".join(lines),
        }
