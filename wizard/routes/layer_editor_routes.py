"""
Layer Editor Routes
===================

Wizard-side persistence for layer editor documents.
"""

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from wizard.services.path_utils import get_repo_root, get_memory_dir


ALLOWED_ROOTS = {
    "sandbox": "memory/sandbox",
    "core": "memory/knowledge/maps",
    "drafts": "memory/drafts",
}

CORE_MAPS_ROOT = "core/data/maps/layers"


class LayerSaveRequest(BaseModel):
    path: str
    document: dict


def _resolve_path(path: str) -> Path:
    repo_root = get_repo_root()
    candidate = (repo_root / path).resolve()
    allowed = [repo_root / rel for rel in ALLOWED_ROOTS.values()]
    if not any(str(candidate).startswith(str(root.resolve())) for root in allowed):
        raise ValueError("Path must be within allowed layer directories")
    return candidate


def create_layer_editor_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/v1/layers", tags=["layers"], dependencies=dependencies
    )

    @router.get("/roots")
    async def get_roots():
        return {"success": True, "roots": ALLOWED_ROOTS}

    @router.get("/list")
    async def list_layers(scope: str = "sandbox"):
        if scope not in ALLOWED_ROOTS:
            raise HTTPException(status_code=400, detail="Invalid scope")
        root_path = _resolve_path(ALLOWED_ROOTS[scope])
        root_path.mkdir(parents=True, exist_ok=True)
        files = sorted(
            [p.name for p in root_path.glob("*.json") if p.is_file()]
        )
        return {"success": True, "scope": scope, "files": files}

    @router.get("/core/list")
    async def list_core_layers():
        repo_root = get_repo_root()
        root_path = (repo_root / CORE_MAPS_ROOT).resolve()
        if not root_path.exists():
            return {"success": False, "files": [], "detail": "Core map layers not found"}
        files = []
        for item in sorted(root_path.glob("*.json")):
            if not item.is_file():
                continue
            stat = item.stat()
            files.append(
                {
                    "name": item.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                }
            )
        return {"success": True, "root": CORE_MAPS_ROOT, "files": files}

    @router.get("/core/load")
    async def load_core_layer(name: str):
        repo_root = get_repo_root()
        root_path = (repo_root / CORE_MAPS_ROOT).resolve()
        if not root_path.exists():
            raise HTTPException(status_code=404, detail="Core map layers not found")
        candidate = (root_path / name).resolve()
        if not str(candidate).startswith(str(root_path)):
            raise HTTPException(status_code=400, detail="Invalid core map path")
        if not candidate.exists() or not candidate.is_file():
            raise HTTPException(status_code=404, detail="Core map layer not found")
        try:
            return {"success": True, "document": json.loads(candidate.read_text())}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON document")

    @router.get("/load")
    async def load_layer(path: str):
        try:
            resolved = _resolve_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if not resolved.exists():
            raise HTTPException(status_code=404, detail="File not found")
        try:
            return {"success": True, "document": json.loads(resolved.read_text())}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON document")

    @router.post("/save")
    async def save_layer(payload: LayerSaveRequest):
        try:
            resolved = _resolve_path(payload.path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(json.dumps(payload.document, indent=2))
        return {"success": True, "path": str(resolved)}

    return router
