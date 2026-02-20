"""TOKEN command handler - local token generation utilities."""

from __future__ import annotations

import secrets
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.error_contract import CommandError


class TokenHandler(BaseCommandHandler):
    """Handler for TOKEN command."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        action = params[0].upper() if params else "GEN"
        args = params[1:] if len(params) > 1 else []

        if action in {"HELP", "--HELP", "-H", "?"}:
            return {
                "status": "success",
                "output": "\n".join(
                    [
                        OutputToolkit.banner("TOKEN"),
                        "TOKEN [GEN] [--len N]   Generate a URL-safe token",
                        "TOKEN HELP              Show this help",
                    ]
                ),
            }

        if action in {"GEN", "NEW", "CREATE"}:
            nbytes = 32
            if "--len" in args:
                idx = args.index("--len")
                if idx + 1 < len(args):
                    try:
                        nbytes = max(16, min(128, int(args[idx + 1])))
                    except ValueError:
                        raise CommandError(
                            code="ERR_VALIDATION_SCHEMA",
                            message="TOKEN --len requires an integer",
                            recovery_hint="Use TOKEN --len <number> (16-128)",
                            level="INFO",
                        )

            token = secrets.token_urlsafe(nbytes)
            output = "\n".join(
                [
                    OutputToolkit.banner("TOKEN"),
                    f"Generated token ({len(token)} chars):",
                    token,
                ]
            )
            return {
                "status": "success",
                "message": "Token generated",
                "output": output,
                "token": token,
            }

        raise CommandError(
            code="ERR_COMMAND_NOT_FOUND",
            message=f"Unknown TOKEN action: {action}",
            recovery_hint="Use TOKEN or TOKEN GEN",
            level="INFO",
        )
