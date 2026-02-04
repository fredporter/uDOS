"""
Plugin Registry Routes
======================

Manifest registry endpoints backed by distribution/plugins.
"""

from typing import Any, Dict, Optional

import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from wizard.services.plugin_registry import get_registry


class RegistryRefreshRequest(BaseModel):
    write_index: bool = False


def create_plugin_registry_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/plugins/registry",
        tags=["plugins-registry"],
        dependencies=dependencies,
    )

    @router.get("")
    async def list_registry(refresh: bool = False, include_manifests: bool = True) -> Dict[str, Any]:
        registry = get_registry().build_registry(refresh=refresh, include_manifests=include_manifests)
        return {
            "success": True,
            "count": len(registry),
            "registry": registry,
        }

    @router.post("/refresh")
    async def refresh_registry(payload: RegistryRefreshRequest) -> Dict[str, Any]:
        result = get_registry().refresh_index(write=payload.write_index)
        return {"success": True, "result": result}

    @router.get("/schema")
    async def get_schema() -> Dict[str, Any]:
        registry = get_registry()
        if not registry.schema_path.exists():
            raise HTTPException(status_code=404, detail="plugin.schema.json not found")
        return {
            "success": True,
            "schema_path": str(registry.schema_path),
            "schema": json.loads(registry.schema_path.read_text(encoding="utf-8")),
        }

    @router.get("/{plugin_id}")
    async def get_registry_entry(plugin_id: str, include_manifest: bool = True) -> Dict[str, Any]:
        registry = get_registry().build_registry(refresh=False, include_manifests=include_manifest)
        entry = registry.get(plugin_id)
        if not entry:
            raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")
        return {"success": True, "entry": entry}

    return router
