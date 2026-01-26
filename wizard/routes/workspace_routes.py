"""
Workspace Routes
===============

Provide browser-safe access to /memory for Wizard UI.
"""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from wizard.services.path_utils import get_memory_dir

from core.services.story_service import parse_story_document


class WriteRequest(BaseModel):
    path: str
    content: str


class MkdirRequest(BaseModel):
    path: str


def _resolve_path(relative_path: str) -> Path:
    memory_root = get_memory_dir().resolve()
    candidate = (memory_root / relative_path).resolve()
    if not str(candidate).startswith(str(memory_root)):
        raise ValueError("Path must be within memory/")
    return candidate


def create_workspace_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/v1/workspace", tags=["workspace"], dependencies=dependencies)

    @router.get("/roots")
    async def get_roots():
        return {"success": True, "roots": {"memory": ""}}

    @router.get("/list")
    async def list_entries(path: str = ""):
        try:
            resolved = _resolve_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        if not resolved.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        if not resolved.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")

        entries = []
        for entry in sorted(resolved.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            rel_path = entry.relative_to(get_memory_dir()).as_posix()
            entries.append(
                {
                    "name": entry.name,
                    "path": rel_path,
                    "type": "dir" if entry.is_dir() else "file",
                    "size": entry.stat().st_size,
                    "modified": entry.stat().st_mtime,
                }
            )

        return {"success": True, "path": path, "entries": entries}

    @router.get("/read")
    async def read_file(path: str):
        try:
            resolved = _resolve_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        if not resolved.exists() or not resolved.is_file():
            raise HTTPException(status_code=404, detail="File not found")

        try:
            return {"success": True, "content": resolved.read_text()}
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File is not valid text")

    @router.get("/story/parse")
    async def parse_story(path: str):
        try:
            resolved = _resolve_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if not resolved.exists() or not resolved.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        try:
            story = parse_story_document(
                resolved.read_text(), required_frontmatter_keys=["title", "type"]
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        return {"success": True, "path": path, "story": story}

    @router.post("/write")
    async def write_file(payload: WriteRequest):
        try:
            resolved = _resolve_path(payload.path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(payload.content)
        return {"success": True, "path": payload.path}

    @router.post("/mkdir")
    async def mkdir(payload: MkdirRequest):
        try:
            resolved = _resolve_path(payload.path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        resolved.mkdir(parents=True, exist_ok=True)
        return {"success": True, "path": payload.path}

    return router
