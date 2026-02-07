from __future__ import annotations

"""
Anchor Routes
=============

Expose gameplay anchors + bindings for Sonic UI.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from core.services.anchor_registry_service import AnchorRegistryService
from core.services.anchor_store import AnchorStore
from core.services.anchor_validation import is_valid_anchor_id, is_valid_locid


class AnchorBindRequest(BaseModel):
    locid: str
    anchor_id: str
    coord_kind: str
    coord_json: Dict[str, Any]
    instance_id: Optional[str] = None
    label: Optional[str] = None
    tags: Optional[str] = None


def create_anchor_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/anchors", tags=["anchors"], dependencies=dependencies)

    registry = AnchorRegistryService()
    store = AnchorStore()

    @router.get("")
    async def list_anchors():
        anchors = registry.list_anchors()
        return {"anchors": [a.__dict__ for a in anchors]}

    @router.get("/{anchor_id}")
    async def get_anchor(anchor_id: str):
        if not is_valid_anchor_id(anchor_id):
            raise HTTPException(status_code=400, detail="Invalid anchor id")
        anchor = registry.get_anchor(anchor_id)
        if not anchor:
            raise HTTPException(status_code=404, detail="Anchor not found")
        return {"anchor": anchor.__dict__}

    @router.post("/bind")
    async def bind_anchor(payload: AnchorBindRequest = Body(...)):
        if not is_valid_locid(payload.locid):
            raise HTTPException(status_code=400, detail="Invalid LocId")
        if not is_valid_anchor_id(payload.anchor_id):
            raise HTTPException(status_code=400, detail="Invalid anchor id")
        binding_id = store.add_binding(
            locid=payload.locid,
            anchor_id=payload.anchor_id,
            coord_kind=payload.coord_kind,
            coord_payload=payload.coord_json,
            instance_id=payload.instance_id,
            label=payload.label,
            tags=payload.tags,
        )
        return {"binding_id": binding_id}

    return router
