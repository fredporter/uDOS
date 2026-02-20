"""MESH command handler - MeshCore P2P mesh networking integration."""

from __future__ import annotations

import shutil
import subprocess
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger
from core.services.error_contract import CommandError

logger = get_logger("command-mesh")


class MeshHandler(BaseCommandHandler):
    """Handler for MESH command - P2P mesh networking via MeshCore.

    Commands:
      MESH                          — show status / help
      MESH STATUS                   — node status, peer count, channel
      MESH NODES                    — list discovered mesh nodes
      MESH SEND <node_id> <msg>     — send a message to a node
      MESH CHANNEL <name>           — join / switch channel
      MESH PING <node_id>           — ping a mesh node
    """

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._help()

        action = params[0].lower()

        if action in {"help", "?"}:
            return self._help()
        if action == "status":
            return self._status()
        if action == "nodes":
            return self._nodes()
        if action == "send":
            return self._send(params[1:])
        if action == "channel":
            return self._channel(params[1:])
        if action == "ping":
            return self._ping(params[1:])

        raise CommandError(
            code="ERR_COMMAND_NOT_FOUND",
            message=f"Unknown MESH action '{params[0]}'. Try MESH HELP.",
            recovery_hint="Use MESH STATUS, NODES, SEND, CHANNEL, or PING",
            level="INFO",
        )

    # ------------------------------------------------------------------
    def _cli(self) -> str | None:
        return shutil.which("meshcore") or shutil.which("meshctl")

    def _run(self, args: List[str]) -> Dict:
        cli = self._cli()
        if not cli:
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message="MeshCore CLI not found. Install meshcore and ensure it is in PATH.",
                recovery_hint="Install meshcore or meshctl",
                level="ERROR",
            )
        try:
            result = subprocess.run([cli] + args, capture_output=True, text=True, timeout=15)
            if result.returncode != 0:
                raise CommandError(
                    code="ERR_RUNTIME_UNEXPECTED",
                    message=(result.stderr or result.stdout).strip()[:300],
                    recovery_hint="Check MeshCore installation and configuration",
                    level="ERROR",
                )
            return {"status": "success", "output": result.stdout.strip()}
        except subprocess.TimeoutExpired:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message="MeshCore command timed out.",
                recovery_hint="Try the command again or check MeshCore daemon status",
                level="ERROR",
            )
        except Exception as e:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(e),
                recovery_hint="Check MeshCore daemon and command syntax",
                level="ERROR",
                cause=e,
            )

    def _status(self) -> Dict:
        result = self._run(["status"])
        if result["status"] != "success":
            return result
        return {**result, "message": "MeshCore node status"}

    def _nodes(self) -> Dict:
        return self._run(["nodes", "list"])

    def _send(self, params: List[str]) -> Dict:
        if len(params) < 2:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Usage: MESH SEND <node_id> <message>",
                recovery_hint="Provide a node ID and message",
                level="INFO",
            )
        node_id = params[0]
        msg = " ".join(params[1:])
        return self._run(["send", "--to", node_id, msg])

    def _channel(self, params: List[str]) -> Dict:
        if not params:
            return self._run(["channel", "list"])
        return self._run(["channel", "join", params[0]])

    def _ping(self, params: List[str]) -> Dict:
        if not params:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Usage: MESH PING <node_id>",
                recovery_hint="Provide a node ID to ping",
                level="INFO",
            )
        return self._run(["ping", params[0]])

    def _help(self) -> Dict:
        return {
            "status": "success",
            "output": (
                "MESH - P2P mesh networking (MeshCore)\n"
                "  MESH STATUS                  Node status and peer count\n"
                "  MESH NODES                   List discovered nodes\n"
                "  MESH SEND <node> <message>   Send message to a node\n"
                "  MESH CHANNEL [name]          List or join a channel\n"
                "  MESH PING <node>             Ping a mesh node\n"
            ),
        }
