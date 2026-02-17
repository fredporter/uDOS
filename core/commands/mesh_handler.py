"""MESH command handler - MeshCore P2P mesh networking integration."""

from __future__ import annotations

import shutil
import subprocess
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger

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

        return {"status": "error", "message": f"Unknown MESH action '{params[0]}'. Try MESH HELP."}

    # ------------------------------------------------------------------
    def _cli(self) -> str | None:
        return shutil.which("meshcore") or shutil.which("meshctl")

    def _run(self, args: List[str]) -> Dict:
        cli = self._cli()
        if not cli:
            return {"status": "error", "message": "MeshCore CLI not found. Install meshcore and ensure it is in PATH."}
        try:
            result = subprocess.run([cli] + args, capture_output=True, text=True, timeout=15)
            if result.returncode != 0:
                return {"status": "error", "message": (result.stderr or result.stdout).strip()[:300]}
            return {"status": "success", "output": result.stdout.strip()}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "MeshCore command timed out."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _status(self) -> Dict:
        result = self._run(["status"])
        if result["status"] != "success":
            return result
        return {**result, "message": "MeshCore node status"}

    def _nodes(self) -> Dict:
        return self._run(["nodes", "list"])

    def _send(self, params: List[str]) -> Dict:
        if len(params) < 2:
            return {"status": "error", "message": "Usage: MESH SEND <node_id> <message>"}
        node_id = params[0]
        msg = " ".join(params[1:])
        return self._run(["send", "--to", node_id, msg])

    def _channel(self, params: List[str]) -> Dict:
        if not params:
            return self._run(["channel", "list"])
        return self._run(["channel", "join", params[0]])

    def _ping(self, params: List[str]) -> Dict:
        if not params:
            return {"status": "error", "message": "Usage: MESH PING <node_id>"}
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
