"""
Binder compilation routes for Wizard Server.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Awaitable, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Query, Request
from pydantic import BaseModel

from core.binder.compiler import BinderCompiler
from wizard.services.path_utils import get_repo_root

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def _load_wizard_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent.parent / "config" / "wizard.json"
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def _build_binder_config() -> Dict[str, Any]:
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    memory_root = locations.get("memory_root", "memory")
    memory_path = Path(memory_root)
    if not memory_path.is_absolute():
        memory_path = get_repo_root() / memory_path

    binder_dir = memory_path / "binders"
    return {"db_path": binder_dir / "binders.db", "output_dir": binder_dir}


def create_binder_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/binder", tags=["binder"])
    compiler = BinderCompiler(
        config=_build_binder_config(), command_runner=subprocess.run
    )

    class ChapterCreate(BaseModel):
        chapter_id: str
        title: str
        content: Optional[str] = ""
        order: int = 1

    class ChapterUpdate(BaseModel):
        title: Optional[str] = None
        content: Optional[str] = None
        order: Optional[int] = None
        status: Optional[str] = None

    class CompileRequest(BaseModel):
        binder_id: str
        formats: Optional[List[str]] = ["markdown", "json"]
        include_toc: bool = True
        format: Optional[str] = None

    @router.post("/compile")
    async def compile_binder(request: Request, body: CompileRequest) -> Dict[str, Any]:
        if auth_guard:
            await auth_guard(request)
        if not body.binder_id:
            raise HTTPException(status_code=400, detail="binder_id required")
        formats = body.formats
        if body.format:
            formats = [body.format]
        if not formats:
            raise HTTPException(status_code=400, detail="At least one format required")
        valid_formats = {"markdown", "pdf", "json", "brief"}
        invalid = set(formats) - valid_formats
        if invalid:
            raise HTTPException(
                status_code=400, detail=f"Invalid formats: {', '.join(invalid)}"
            )
        return await compiler.compile_binder(
            binder_id=body.binder_id, formats=formats
        )

    @router.post("/{binder_id}/compile")
    async def compile_binder_id(
        binder_id: str, request: Request, body: CompileRequest
    ) -> Dict[str, Any]:
        if auth_guard:
            await auth_guard(request)
        if not binder_id:
            raise HTTPException(status_code=400, detail="binder_id required")
        formats = body.formats
        if body.format:
            formats = [body.format]
        if not formats:
            raise HTTPException(status_code=400, detail="At least one format required")
        valid_formats = {"markdown", "pdf", "json", "brief"}
        invalid = set(formats) - valid_formats
        if invalid:
            raise HTTPException(
                status_code=400, detail=f"Invalid formats: {', '.join(invalid)}"
            )
        return await compiler.compile_binder(binder_id=binder_id, formats=formats)

    @router.get("/all")
    async def list_binders(request: Request) -> List[Dict[str, Any]]:
        if auth_guard:
            await auth_guard(request)
        binders = await compiler.get_binders()
        return [
            {
                "id": b.get("id"),
                "name": b.get("name") or b.get("id"),
                "description": b.get("description"),
                "status": b.get("status"),
                "chapter_count": b.get("total_chapters", 0),
                "word_count": b.get("total_words", 0),
                "created_at": b.get("created_at"),
                "updated_at": b.get("updated_at"),
                "outputs": b.get("outputs", []),
            }
            for b in binders
        ]

    @router.get("/{binder_id}/chapters")
    async def get_chapters(
        binder_id: str, request: Request, include_content: bool = Query(False)
    ) -> Dict[str, Any]:
        if auth_guard:
            await auth_guard(request)
        chapters = await compiler.get_chapters(binder_id)
        return {
            "binder_id": binder_id,
            "total": len(chapters),
            "chapters": chapters,
            "include_content": include_content,
        }

    @router.post("/{binder_id}/chapters")
    async def add_chapter(binder_id: str, request: Request, chapter: ChapterCreate):
        if auth_guard:
            await auth_guard(request)
        return await compiler.add_chapter(
            binder_id=binder_id, chapter=chapter.model_dump()
        )

    @router.put("/{binder_id}/chapters/{chapter_id}")
    async def update_chapter(
        binder_id: str, chapter_id: str, request: Request, update: ChapterUpdate
    ):
        if auth_guard:
            await auth_guard(request)
        if update.status and update.status not in {"draft", "review", "complete"}:
            raise HTTPException(
                status_code=400, detail="status must be draft|review|complete"
            )
        return await compiler.update_chapter(
            binder_id=binder_id, chapter_id=chapter_id, content=update.content or ""
        )

    @router.post("/{binder_id}/export")
    async def export_binder(
        binder_id: str, request: Request, format: str = Query("markdown")
    ):
        if auth_guard:
            await auth_guard(request)
        valid_formats = {"markdown", "pdf", "json", "brief"}
        if format not in valid_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Valid: {', '.join(valid_formats)}",
            )
        result = await compiler.compile_binder(binder_id=binder_id, formats=[format])
        return {
            "status": "exported",
            "binder_id": binder_id,
            "format": format,
            "outputs": result.get("outputs", []),
            "compiled_at": result.get("compiled_at"),
        }

    return router
