"""Metadata subroutes for uCODE bridge routes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from fastapi import APIRouter, HTTPException

from wizard.routes.command_capability_utils import (
    check_command_capabilities,
    detect_wizard_capabilities,
)
from wizard.services.keymap_config import (
    VALID_OS_OVERRIDES,
    apply_keymap_update,
    resolve_effective_keymap_state,
)
from wizard.services.wizard_config import load_wizard_config_data, save_wizard_config_data


def create_ucode_meta_routes(
    allowlist: Set[str],
    wizard_required_commands: Dict[str, List[str]] | None = None,
    get_capabilities: Callable[[], Dict[str, bool]] | None = None,
    wizard_config_path: Optional[Path] = None,
) -> APIRouter:
    router = APIRouter(tags=["ucode"])
    required_map = wizard_required_commands or {}
    capability_loader = get_capabilities or detect_wizard_capabilities

    def _load_effective_keymap_state() -> Dict[str, Any]:
        try:
            config = load_wizard_config_data(path=wizard_config_path, defaults={})
            return resolve_effective_keymap_state(config=config, env=os.environ)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

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

    @router.get("/keymap")
    async def get_keymap() -> Dict[str, Any]:
        return {"status": "ok", **_load_effective_keymap_state()}

    @router.post("/keymap")
    async def update_keymap(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="payload must be an object")

        profile = payload.get("profile")
        self_heal = payload.get("self_heal")
        os_override = payload.get("os_override")

        if self_heal is not None and not isinstance(self_heal, bool):
            raise HTTPException(status_code=422, detail="self_heal must be boolean")

        config = load_wizard_config_data(path=wizard_config_path, defaults={})
        try:
            apply_keymap_update(
                config=config,
                env=os.environ,
                profile=profile,
                self_heal=self_heal,
                os_override=os_override,
            )
        except ValueError as exc:
            detail = str(exc)
            if "os_override" in detail and os_override is not None:
                allowed = "|".join(sorted(VALID_OS_OVERRIDES))
                detail = f"{detail} (expected one of: {allowed})"
            raise HTTPException(status_code=422, detail=detail)

        save_wizard_config_data(config, path=wizard_config_path)
        return {"status": "ok", **_load_effective_keymap_state()}

    return router
