"""
Artifact Store Routes
=====================

Manage Wizard-local installers, downloads, upgrades, and backups.
"""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from wizard.services.artifact_store import get_artifact_store
from wizard.services.path_utils import get_repo_root


class ArtifactAddRequest(BaseModel):
    kind: str
    source_path: str
    notes: Optional[str] = None


def create_artifact_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/v1/artifacts", tags=["artifacts"], dependencies=dependencies
    )

    @router.get("")
    async def list_artifacts(kind: Optional[str] = None):
        store = get_artifact_store()
        entries = store.list(kind=kind)
        return {"success": True, "entries": [e.to_dict() for e in entries]}

    @router.post("/add")
    async def add_artifact(payload: ArtifactAddRequest):
        repo_root = get_repo_root()
        source_path = Path(payload.source_path).expanduser().resolve()
        if repo_root not in source_path.parents and source_path != repo_root:
            raise HTTPException(
                status_code=400,
                detail="source_path must be within repo",
            )
        if not source_path.exists() or not source_path.is_file():
            raise HTTPException(
                status_code=404, detail="source_path does not exist or is not a file"
            )

        store = get_artifact_store()
        try:
            entry = store.add(source_path, payload.kind, payload.notes)
            return {"success": True, "entry": entry.to_dict()}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.delete("/{artifact_id}")
    async def delete_artifact(artifact_id: str):
        store = get_artifact_store()
        if not store.remove(artifact_id):
            raise HTTPException(status_code=404, detail="Artifact not found")
        return {"success": True, "deleted": artifact_id}

    return router
