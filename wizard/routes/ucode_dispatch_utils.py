"""Non-OK dispatch helpers for uCODE routes."""

from __future__ import annotations

import subprocess
from typing import Any, Callable, Dict, Optional, Set, Tuple, List

from fastapi import HTTPException
from core.services.command_catalog import (
    parse_slash_command,
    resolve_allowlisted_slash_command,
)
from core.services.command_dispatch_service import (
    DISPATCH_CONTRACT_VERSION,
    DISPATCH_ROUTE_ORDER,
)


def _routing_contract() -> Dict[str, Any]:
    return {
        "interactive_owner": "dev-mode-tool",
        "tool_gateway": "wizard-mcp",
        "dispatch_contract_version": DISPATCH_CONTRACT_VERSION,
        "dispatch_route_order": list(DISPATCH_ROUTE_ORDER),
    }


def handle_slash_command(
    *,
    command: str,
    allowlist: Set[str],
    shell_allowed: Callable[[], bool],
    shell_safe: Callable[[str], bool],
    logger: Any,
    corr_id: str,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Resolve slash-prefixed commands; return updated command or immediate response."""
    if not (parsed := parse_slash_command(command)):
        return command, None

    if allowlisted_command := resolve_allowlisted_slash_command(parsed, allowlist):
        return allowlisted_command, None

    if not shell_allowed():
        logger.warn("Shell command blocked", ctx={"corr_id": corr_id})
        raise HTTPException(status_code=403, detail="shell commands disabled")

    shell_cmd = parsed.body
    if not shell_cmd:
        logger.warn("Shell command rejected (empty)", ctx={"corr_id": corr_id})
        raise HTTPException(status_code=400, detail="shell command is required")

    if not shell_safe(shell_cmd):
        logger.warn(
            "Shell command failed safety check",
            ctx={"corr_id": corr_id, "command": shell_cmd},
        )
        raise HTTPException(status_code=403, detail="shell command blocked (destructive)")

    try:
        logger.info(
            "Shell command dispatch",
            ctx={"corr_id": corr_id, "command": shell_cmd},
        )
        result = subprocess.run(
            shell_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        logger.warn("Shell command timeout", ctx={"corr_id": corr_id})
        raise HTTPException(status_code=408, detail="shell command timed out")

    output = result.stdout or result.stderr
    response = {
        "status": "ok",
        "command": f"/{shell_cmd}",
        "routing_contract": _routing_contract(),
        "result": {
            "status": "success" if result.returncode == 0 else "error",
            "message": output or f"exit code {result.returncode}",
            "shell_output": output,
            "exit_code": result.returncode,
        },
    }
    return command, response


def dispatch_non_ok_command(
    *,
    command: str,
    allowlist: Set[str],
    dispatcher: Any,
    game_state: Any,
    renderer: Any,
    load_setup_story: Callable[[], Dict[str, Any]],
    logger: Any,
    corr_id: str,
    command_capability_check: Optional[Callable[[str], Tuple[bool, Optional[str], List[str]]]] = None,
    deprecated_aliases: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Dispatch non-OK allowlisted commands, including setup story shortcut."""
    cmd_name = command.split()[0].upper()
    if deprecated_aliases and cmd_name in deprecated_aliases:
        canonical = deprecated_aliases[cmd_name]
        raise HTTPException(
            status_code=410,
            detail=f"Legacy command alias removed in v1.3: {cmd_name}. Use {canonical}.",
        )
    if command_capability_check:
        available, reason, _ = command_capability_check(cmd_name)
        if not available:
            logger.warn(
                "Command blocked by missing capabilities",
                ctx={"corr_id": corr_id, "command": cmd_name, "reason": reason},
            )
            raise HTTPException(status_code=412, detail=reason or f"command unavailable: {cmd_name}")

    if cmd_name == "SETUP" and len(command.split()) == 1:
        story_state = load_setup_story()
        logger.info("Setup story served", ctx={"corr_id": corr_id})
        return {
            "status": "ok",
            "command": command,
            "routing_contract": _routing_contract(),
            "result": {
                "status": "success",
                "message": "Setup story ready",
                "frontmatter": story_state.get("frontmatter"),
                "sections": story_state.get("sections"),
            },
        }

    if cmd_name not in allowlist:
        logger.warn(
            "Command blocked by allowlist",
            ctx={"corr_id": corr_id, "command": cmd_name},
        )
        raise HTTPException(status_code=403, detail=f"command not allowed: {cmd_name}")

    logger.info(
        "Dispatch command",
        ctx={"corr_id": corr_id, "command": cmd_name, "raw": command},
    )
    result = dispatcher.dispatch(command, game_state=game_state)
    logger.info(
        "Dispatch result",
        ctx={
            "corr_id": corr_id,
            "status": result.get("status") if isinstance(result, dict) else None,
        },
    )
    response: Dict[str, Any] = {
        "status": "ok",
        "command": command,
        "routing_contract": _routing_contract(),
        "result": result,
    }
    if renderer:
        try:
            response["rendered"] = renderer.render(result)
        except Exception:
            pass
    return response
