"""
Home Assistant Bridge Routes
=============================

Minimal Wizard API surface for the uDOS ↔ Home Assistant bridge.

Routes:
    GET  /api/ha/status   — bridge status + version
    GET  /api/ha/discover — available uDOS entities/services
    POST /api/ha/command  — execute an allowlisted uDOS/uHOME command

Security contract:
- /api/ha/status is unauthenticated (returns disabled when HA bridge is off).
- /api/ha/discover and /api/ha/command require auth_guard (admin token).
- Commands are validated against a strict allowlist in the service layer.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.services.template_workspace_service import get_template_workspace_service
from wizard.services.home_assistant_service import get_ha_service
from wizard.services.path_utils import get_repo_root


class HACommandRequest(BaseModel):
    command: str
    params: dict[str, Any] = {}


def create_ha_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/ha", tags=["home-assistant"])

    @router.get("/status")
    async def ha_status():
        """Return bridge status and version. Always public — returns disabled when off."""
        workspace = get_template_workspace_service(get_repo_root())
        return {
            **get_ha_service().status(),
            "template_workspace": workspace.component_contract("uhome"),
            "template_workspace_state": workspace.component_snapshot("uhome"),
        }

    @router.get("/discover", dependencies=dependencies)
    async def ha_discover():
        """Return available uDOS entities discoverable by Home Assistant."""
        svc = get_ha_service()
        if not svc.is_enabled():
            raise HTTPException(
                status_code=503,
                detail="Home Assistant bridge is disabled. Enable ha_bridge_enabled in Wizard config.",
            )
        workspace = get_template_workspace_service(get_repo_root())
        return {
            **svc.discover(),
            "template_workspace": workspace.component_contract("uhome"),
            "template_workspace_state": workspace.component_snapshot("uhome"),
        }

    @router.post("/command", dependencies=dependencies)
    async def ha_command(payload: HACommandRequest):
        """Execute an allowlisted uDOS/uHOME command."""
        svc = get_ha_service()
        if not svc.is_enabled():
            raise HTTPException(
                status_code=503,
                detail="Home Assistant bridge is disabled. Enable ha_bridge_enabled in Wizard config.",
            )
        try:
            result = svc.execute_command(payload.command, payload.params)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"success": True, "result": result}

    return router
