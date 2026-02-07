"""
uCODE Bridge Routes
===================

Expose a minimal, allowlisted uCODE command dispatch endpoint for Vibe/MCP.
"""

from __future__ import annotations

import os
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends
import subprocess
from pydantic import BaseModel


class DispatchRequest(BaseModel):
    command: str


def _default_allowlist() -> set[str]:
    return {
        "HELP",
        "MAP",
        "PANEL",
        "FIND",
        "TELL",
        "GOTO",
        "BAG",
        "GRAB",
        "SPAWN",
        "STORY",
        "RUN",
        "BINDER",
        "DATASET",
        "USER",
        "UID",
        "DEV",
        "WIZARD",
        "CONFIG",
        "SAVE",
        "LOAD",
        "FILE",
        "NEW",
        "EDIT",
        "NPC",
        "TALK",
        "REPLY",
        "LOGS",
    }


def _load_allowlist() -> set[str]:
    raw = os.getenv("UCODE_API_ALLOWLIST", "").strip()
    if not raw:
        return _default_allowlist()
    return {item.strip().upper() for item in raw.split(",") if item.strip()}


def _shell_allowed() -> bool:
    return os.getenv("UCODE_API_ALLOW_SHELL", "").strip().lower() in {"1", "true", "yes"}


def _shell_safe(command: str) -> bool:
    destructive_keywords = {"rm", "mv", ">", "|", "sudo", "rmdir", "dd", "format"}
    cmd_lower = command.lower()
    return not any(kw in cmd_lower for kw in destructive_keywords)


def create_ucode_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/ucode", tags=["ucode"], dependencies=dependencies)

    allowlist = _load_allowlist()

    # Lazy imports to keep wizard usable without core in some deployments.
    try:
        from core.tui.dispatcher import CommandDispatcher
        from core.tui.state import GameState
        from core.tui.renderer import GridRenderer

        dispatcher = CommandDispatcher()
        game_state = GameState()
        renderer = GridRenderer()
    except Exception:  # pragma: no cover
        dispatcher = None
        game_state = None
        renderer = None

    @router.get("/allowlist")
    async def get_allowlist() -> Dict[str, Any]:
        return {
            "status": "ok",
            "allowlist": sorted(allowlist),
        }

    @router.post("/dispatch")
    async def dispatch_command(payload: DispatchRequest) -> Dict[str, Any]:
        if not dispatcher:
            raise HTTPException(status_code=500, detail="uCODE dispatcher unavailable")

        command = (payload.command or "").strip()
        if not command:
            raise HTTPException(status_code=400, detail="command is required")

        # Normalize uCODE-style prefixes (case-insensitive)
        if command.lower().startswith("ok "):
            command = command[3:].strip()
        if command.startswith(":"):
            command = command[1:].strip()

        # Slash-prefixed shell command
        if command.startswith("/"):
            if not _shell_allowed():
                raise HTTPException(status_code=403, detail="shell commands disabled")
            shell_cmd = command[1:].strip()
            if not shell_cmd:
                raise HTTPException(status_code=400, detail="shell command is required")
            if not _shell_safe(shell_cmd):
                raise HTTPException(status_code=403, detail="shell command blocked (destructive)")
            try:
                result = subprocess.run(
                    shell_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            except subprocess.TimeoutExpired:
                raise HTTPException(status_code=408, detail="shell command timed out")
            output = result.stdout or result.stderr
            return {
                "status": "ok",
                "command": f"/{shell_cmd}",
                "result": {
                    "status": "success" if result.returncode == 0 else "error",
                    "message": output or f"exit code {result.returncode}",
                    "shell_output": output,
                },
            }

        cmd_name = command.split()[0].upper()
        if cmd_name not in allowlist:
            raise HTTPException(status_code=403, detail=f"command not allowed: {cmd_name}")

        result = dispatcher.dispatch(command, game_state=game_state)
        response: Dict[str, Any] = {
            "status": "ok",
            "command": command,
            "result": result,
        }
        if renderer:
            try:
                response["rendered"] = renderer.render(result)
            except Exception:
                pass
        return response

    return router
