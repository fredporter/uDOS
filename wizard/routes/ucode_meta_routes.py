"""Metadata subroutes for uCODE bridge routes."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Set

from fastapi import APIRouter, HTTPException

from wizard.routes.command_capability_utils import (
    check_command_capabilities,
    detect_wizard_capabilities,
)


def create_ucode_meta_routes(
    allowlist: Set[str],
    wizard_required_commands: Dict[str, List[str]] | None = None,
    get_capabilities: Callable[[], Dict[str, bool]] | None = None,
) -> APIRouter:
    router = APIRouter(tags=["ucode"])
    required_map = wizard_required_commands or {}
    capability_loader = get_capabilities or detect_wizard_capabilities

    @router.get("/allowlist")
    async def get_allowlist() -> Dict[str, Any]:
        return {
            "status": "ok",
            "allowlist": sorted(allowlist),
        }

    @router.get("/commands")
    async def get_commands() -> Dict[str, Any]:
        capabilities = capability_loader()
        try:
            from core.input.command_prompt import create_default_registry

            registry = create_default_registry()
            registry_map = {
                cmd.name: {
                    "name": cmd.name,
                    "help_text": cmd.help_text,
                    "options": cmd.options,
                    "syntax": cmd.syntax,
                    "examples": cmd.examples,
                    "icon": cmd.icon,
                    "category": cmd.category,
                }
                for cmd in registry.list_all()
            }
        except Exception:
            registry_map = {}

        commands: List[Dict[str, Any]] = []
        for cmd in sorted(allowlist):
            allowed, _, requirements = check_command_capabilities(cmd, required_map, capabilities)
            if not allowed:
                continue
            base = registry_map.get(cmd) or {
                "name": cmd,
                "help_text": "Command available",
                "options": [],
                "syntax": cmd,
                "examples": [],
                "icon": "⚙️",
                "category": "General",
            }
            commands.append({**base, "allowed": True, "requirements": requirements})

        ok_meta = registry_map.get("OK")
        if ok_meta:
            commands.append({**ok_meta, "allowed": True})
        return {"status": "ok", "commands": commands}

    @router.get("/hotkeys")
    async def get_hotkeys() -> Dict[str, Any]:
        try:
            from core.services.hotkey_map import get_hotkey_map

            return {"status": "ok", "hotkeys": get_hotkey_map()}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
