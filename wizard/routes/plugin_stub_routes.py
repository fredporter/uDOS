"""
Plugin CLI Stub Routes
======================

Provides a placeholder endpoint for plugin CLI migration into Wizard.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel


class PluginCommandRequest(BaseModel):
    command: str


def create_plugin_stub_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/plugin", tags=["plugin"], dependencies=dependencies)

    @router.post("/command")
    async def plugin_command(payload: PluginCommandRequest) -> Dict[str, Any]:
        return {
            "status": "stub",
            "message": "Plugin CLI migrated to Wizard distribution; use /api/plugins/registry.",
            "command": payload.command,
        }

    return router

