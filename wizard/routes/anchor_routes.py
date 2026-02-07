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
from core.services.anchor_registry_service import AnchorRecord
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


class AnchorRegisterRequest(BaseModel):
    anchor_id: str
    title: str
    description: Optional[str] = None
    version: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None


class AnchorInstanceRequest(BaseModel):
    anchor_id: str
    profile_id: Optional[str] = None
    space_id: Optional[str] = None
    seed: Optional[str] = None
    meta_json: Optional[Dict[str, Any]] = None


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

    @router.post("/register")
    async def register_anchor(payload: AnchorRegisterRequest = Body(...)):
        if not is_valid_anchor_id(payload.anchor_id):
            raise HTTPException(status_code=400, detail="Invalid anchor id")
        record = AnchorRecord(
            anchor_id=payload.anchor_id,
            title=payload.title,
            description=payload.description,
            version=payload.version,
            capabilities=payload.capabilities or {},
            created_at=store.utc_now(),
            updated_at=store.utc_now(),
        )
        registry.register_anchor(record)
        return {"anchor": record.__dict__}

    @router.post("/instances")
    async def create_instance(payload: AnchorInstanceRequest = Body(...)):
        if not is_valid_anchor_id(payload.anchor_id):
            raise HTTPException(status_code=400, detail="Invalid anchor id")
        instance = store.create_instance(
            anchor_id=payload.anchor_id,
            profile_id=payload.profile_id,
            space_id=payload.space_id,
            seed=payload.seed,
            meta=payload.meta_json,
        )
        return {"instance": instance.__dict__}

    @router.delete("/instances/{instance_id}")
    async def delete_instance(instance_id: str):
        store.destroy_instance(instance_id)
        return {"status": "deleted", "instance_id": instance_id}

    @router.get("/instances")
    async def list_instances(anchor_id: Optional[str] = None):
        instances = store.list_instances(anchor_id=anchor_id)
        return {"instances": [i.__dict__ for i in instances]}

    @router.get("/events")
    async def list_events(
        anchor_id: Optional[str] = None,
        instance_id: Optional[str] = None,
        limit: int = 50,
        type: Optional[str] = None,
    ):
        events = store.list_events(
            anchor_id=anchor_id,
            instance_id=instance_id,
            limit=limit,
            event_type=type,
        )
        return {"events": events}

    return router
