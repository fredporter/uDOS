"""
Workspace Routes
===============

Provide browser-safe access to /memory for Wizard UI.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Tuple

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from wizard.services.path_utils import get_memory_dir, get_repo_root, get_vault_dir

from core.services.story_service import parse_story_document
from core.services.spatial_filesystem import WORKSPACE_CONFIG


class WriteRequest(BaseModel):
    path: str
    content: str


class MkdirRequest(BaseModel):
    path: str


def _resolve_workspace_root() -> Dict[str, Path]:
    env_root = os.getenv("UDOS_ROOT")
    base_root = Path(env_root).expanduser() if env_root else get_repo_root()
    root_map: Dict[str, Path] = {"memory": get_memory_dir().resolve()}

    for ws_type, config in WORKSPACE_CONFIG.items():
        rel_path = config.get("path")
        if not isinstance(rel_path, str):
            continue
        root_map[ws_type.value] = (base_root / rel_path).resolve()

    root_map["vault"] = get_vault_dir().resolve()
    return root_map


def _normalize_workspace_ref(path: str) -> str:
    raw = (path or "").strip()
    if raw.startswith("@"):
        return raw[1:]
    return raw.lstrip("/")


def _split_root(path: str) -> Tuple[str, str]:
    raw = _normalize_workspace_ref(path)
    if not raw:
        return "memory", ""
    if raw.startswith("workspace/"):
        parts = raw.split("/", 2)
        if len(parts) >= 2:
            root_key = parts[1]
            rel = parts[2] if len(parts) > 2 else ""
            if root_key in _resolve_workspace_root():
                return root_key, rel
    parts = raw.split("/", 1)
    root_key = parts[0]
    if root_key in _resolve_workspace_root():
        rel = parts[1] if len(parts) > 1 else ""
        return root_key, rel
    return "memory", raw


def _resolve_path(relative_path: str) -> Path:
    root_map = _resolve_workspace_root()
    root_key, rel = _split_root(relative_path)
    root_dir = root_map[root_key]
    candidate = (root_dir / rel).resolve()
    if not str(candidate).startswith(str(root_dir)):
        raise ValueError(f"Path must be within {root_key}/")
    return candidate


def create_workspace_routes(auth_guard=None, prefix="/api/workspace") -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix=prefix, tags=["workspace"], dependencies=dependencies)

    @router.get("/roots")
    async def get_roots():
        root_map = _resolve_workspace_root()
        roots = {
            "memory": "memory",
            "memory/sandbox": "memory/sandbox",
            "memory/inbox": "memory/inbox",
            "vault": "vault",
        }
        for key in sorted(root_map):
            roots[f"@{key}"] = f"@{key}"
            roots[f"@workspace/{key}"] = f"@workspace/{key}"
        return {
            "success": True,
            "roots": roots,
        }

    @router.get("/resolve")
    async def resolve_workspace_path(path: str = ""):
        try:
            resolved = _resolve_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        root_key, rel = _split_root(path)
        normalized_path = root_key if not rel else f"{root_key}/{rel}"
        return {
            "success": True,
            "input": path,
            "normalized": normalized_path,
            "absolute_path": str(resolved),
        }

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

        root_key, rel = _split_root(path)
        root_dir = _resolve_workspace_root()[root_key]

        entries = []
        for entry in sorted(resolved.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            rel_path = entry.relative_to(root_dir).as_posix()
            if rel_path:
                rel_path = f"{root_key}/{rel_path}"
            else:
                rel_path = root_key
            entries.append(
                {
                    "name": entry.name,
                    "path": rel_path,
                    "type": "dir" if entry.is_dir() else "file",
                    "size": entry.stat().st_size,
                    "modified": entry.stat().st_mtime,
                }
            )

        normalized_path = root_key if not rel else f"{root_key}/{rel}"
        return {"success": True, "path": normalized_path, "entries": entries}

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
