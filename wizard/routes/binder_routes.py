"""
Binder compilation routes for Wizard Server.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Awaitable, Dict, List, Optional, Tuple

import yaml

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from core.binder.compiler import BinderCompiler
from core.binder.manager import BinderManager, BinderWorkspace, BinderLocation

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]

binder_manager = BinderManager()
binder_compiler = BinderCompiler()


def _parse_workspace(value: str) -> BinderWorkspace:
    normalized = value[1:] if value.startswith("@") else value
    try:
        return BinderWorkspace(normalized)
    except ValueError as exc:
        allowed = ", ".join([w.value for w in BinderWorkspace])
        raise HTTPException(
            status_code=400,
            detail=f"Invalid workspace '{value}'. Allowed: {allowed}",
        ) from exc


def _resolve_binder_path(
    binder_id: str, workspace: Optional[str] = None
) -> Tuple[BinderWorkspace, Path]:
    if workspace:
        ws = _parse_workspace(workspace)
        path = binder_manager.get_workspace_dir(ws) / binder_id
        if not path.exists():
            raise HTTPException(status_code=404, detail="Binder not found")
        return ws, path

    for ws in BinderWorkspace:
        path = binder_manager.get_workspace_dir(ws) / binder_id
        if path.exists():
            return ws, path

    raise HTTPException(status_code=404, detail="Binder not found")


def _split_frontmatter(content: str) -> Tuple[Dict[str, object], str]:
    if not content.startswith("---"):
        return {}, content

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, content

    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            fm_text = "\n".join(lines[1:idx])
            body = "\n".join(lines[idx + 1 :])
            try:
                meta = yaml.safe_load(fm_text) or {}
                if not isinstance(meta, dict):
                    meta = {}
            except yaml.YAMLError:
                meta = {}
            return meta, body

    return {}, content


def _build_frontmatter(meta: Dict[str, object]) -> str:
    fm_text = yaml.safe_dump(meta, sort_keys=False).strip()
    return f"---\n{fm_text}\n---\n"


def _extract_title(body: str) -> Optional[str]:
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\\s_-]", "", value)
    value = re.sub(r"[\\s_-]+", "-", value)
    return value.strip("-") or "chapter"


def _chapter_sort_key(chapter: Dict[str, object]) -> Tuple[int, object]:
    order = chapter.get("order")
    if isinstance(order, int):
        return (0, order)
    return (1, str(chapter.get("filename", "")))


def _load_chapters_from_files(
    binder_path: Path, include_content: bool = False
) -> List[Dict[str, object]]:
    base_dir = binder_path / "docs"
    md_files = list(base_dir.glob("*.md")) if base_dir.exists() else []
    if not md_files:
        base_dir = binder_path
        md_files = list(base_dir.glob("*.md"))

    chapters: List[Dict[str, object]] = []
    for file_path in md_files:
        if file_path.name in {"index.md", "binder.md"}:
            continue
        content = file_path.read_text(encoding="utf-8")
        meta, body = _split_frontmatter(content)

        title = (
            str(meta.get("title")).strip()
            if meta.get("title")
            else _extract_title(body)
        )
        if not title:
            title = file_path.stem.replace("_", " ").replace("-", " ").title()

        order = meta.get("chapter") or meta.get("order") or meta.get("chapter_num")
        try:
            order = int(order) if order is not None else None
        except (TypeError, ValueError):
            order = None

        chapter_id = meta.get("chapter_id") or file_path.stem

        chapter: Dict[str, object] = {
            "chapter_id": chapter_id,
            "title": title,
            "order": order,
            "filename": file_path.name,
            "path": str(file_path),
        }
        if include_content:
            chapter["content"] = body
        chapters.append(chapter)

    chapters.sort(key=_chapter_sort_key)
    for idx, chapter in enumerate(chapters, 1):
        if chapter.get("order") is None:
            chapter["order"] = idx

    return chapters


def _ensure_binder(
    binder_id: str, workspace: Optional[str], title: Optional[str]
) -> Tuple[BinderWorkspace, Path, bool]:
    if workspace:
        ws = _parse_workspace(workspace)
        binder_root = binder_manager.get_workspace_dir(ws) / binder_id
        created = not binder_root.exists()
        if created:
            binder_manager.create_binder(binder_id, title, ws)
        return ws, binder_root, created

    for ws in BinderWorkspace:
        binder_root = binder_manager.get_workspace_dir(ws) / binder_id
        if binder_root.exists():
            return ws, binder_root, False

    ws = BinderWorkspace.SANDBOX
    binder_root = binder_manager.get_workspace_dir(ws) / binder_id
    binder_manager.create_binder(binder_id, title, ws)
    return ws, binder_root, True


def create_binder_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/binder", tags=["binder"])
    compiler = binder_compiler

    class BinderCreateRequest(BaseModel):
        binder_id: str = Field(..., min_length=1)
        title: Optional[str] = None
        workspace: str = "sandbox"

    class ChapterCreateRequest(BaseModel):
        title: str = Field(..., min_length=1)
        content: str = ""
        order: int = 1
        chapter_id: Optional[str] = None

    class CompileRequest(BaseModel):
        binder_id: str
        formats: Optional[List[str]] = None
        format: Optional[str] = None

    class ChapterUpdate(BaseModel):
        title: Optional[str] = None
        content: Optional[str] = None
        order: Optional[int] = None
        status: Optional[str] = None

    @router.get("/workspaces")
    async def list_binder_workspaces(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"workspaces": binder_manager.describe_workspaces()}

    @router.get("")
    async def list_binders(request: Request, workspace: str = Query("sandbox")):
        if auth_guard:
            await auth_guard(request)
        ws = _parse_workspace(workspace)
        binders = binder_manager.list_binders(ws)
        return {
            "workspace": ws.value,
            "count": len(binders),
            "binders": [{"id": p.name, "path": str(p)} for p in binders],
        }

    @router.get("/summary")
    async def list_binder_summaries(request: Request):
        if auth_guard:
            await auth_guard(request)
        summaries = await compiler.get_binders()
        return {"count": len(summaries), "binders": summaries}

    @router.post("")
    async def create_binder(request: Request, payload: BinderCreateRequest):
        if auth_guard:
            await auth_guard(request)
        ws = _parse_workspace(payload.workspace)
        binder_root = binder_manager.get_workspace_dir(ws) / payload.binder_id
        created = not binder_root.exists()
        if created:
            location = binder_manager.create_binder(
                payload.binder_id, payload.title, ws
            )
        else:
            location = BinderLocation(workspace=ws, path=binder_root)

        db_status = await compiler.ensure_binder(
            payload.binder_id, payload.title
        )
        return {
            "status": "created" if created else "exists",
            "binder_id": payload.binder_id,
            "workspace": ws.value,
            "path": str(location.path),
            "db": db_status,
        }

    @router.post("/compile")
    async def compile_binder(
        request: Request,
        body: CompileRequest,
        workspace: Optional[str] = Query(None),
    ) -> Dict[str, Any]:
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
        ws, binder_path = _resolve_binder_path(body.binder_id, workspace)
        chapters = _load_chapters_from_files(binder_path, include_content=True)
        if chapters:
            await compiler.sync_chapters(body.binder_id, chapters)
            result = await compiler.compile_chapters(
                body.binder_id, chapters, formats
            )
            result["source"] = "files"
            result["workspace"] = ws.value
            return result

        result = await compiler.compile_binder(
            binder_id=body.binder_id, formats=formats
        )
        result["source"] = "db"
        result["workspace"] = ws.value
        return result

    @router.post("/{binder_id}/compile")
    async def compile_binder_id(
        binder_id: str,
        request: Request,
        body: CompileRequest,
        workspace: Optional[str] = Query(None),
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
        ws, binder_path = _resolve_binder_path(binder_id, workspace)
        chapters = _load_chapters_from_files(binder_path, include_content=True)
        if chapters:
            await compiler.sync_chapters(binder_id, chapters)
            result = await compiler.compile_chapters(binder_id, chapters, formats)
            result["source"] = "files"
            result["workspace"] = ws.value
            return result

        result = await compiler.compile_binder(binder_id=binder_id, formats=formats)
        result["source"] = "db"
        result["workspace"] = ws.value
        return result

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
        binder_id: str,
        request: Request,
        include_content: bool = Query(False),
        workspace: Optional[str] = Query(None),
    ) -> Dict[str, Any]:
        if auth_guard:
            await auth_guard(request)
        ws, binder_path = _resolve_binder_path(binder_id, workspace)
        chapters = _load_chapters_from_files(
            binder_path, include_content=include_content
        )
        if chapters:
            return {
                "binder_id": binder_id,
                "workspace": ws.value,
                "source": "files",
                "total": len(chapters),
                "chapters": chapters,
                "include_content": include_content,
            }

        chapters = await compiler.get_chapters(binder_id)
        return {
            "binder_id": binder_id,
            "workspace": ws.value,
            "source": "db",
            "total": len(chapters),
            "chapters": chapters,
            "include_content": include_content,
        }

    @router.post("/{binder_id}/chapters")
    async def add_chapter(
        binder_id: str,
        request: Request,
        chapter: ChapterCreateRequest,
        workspace: Optional[str] = Query(None),
    ):
        if auth_guard:
            await auth_guard(request)
        ws, binder_path, created = _ensure_binder(
            binder_id, workspace, None
        )
        docs_dir = binder_path / "docs"
        target_dir = docs_dir if docs_dir.exists() else binder_path
        target_dir.mkdir(parents=True, exist_ok=True)

        chapter_id = chapter.chapter_id or _slugify(chapter.title)
        chapter_stem = Path(chapter_id).stem
        filename = f"{chapter_stem}.md"
        file_path = target_dir / filename

        file_existed = file_path.exists()
        existing_meta: Dict[str, object] = {}
        existing_body = ""
        if file_existed:
            existing_meta, existing_body = _split_frontmatter(
                file_path.read_text(encoding="utf-8")
            )

        meta, body = _split_frontmatter(chapter.content)
        if not body:
            body = chapter.content
        if not body.strip() and existing_body:
            body = existing_body

        now = datetime.utcnow().isoformat() + "Z"
        merged_meta: Dict[str, object] = {}
        merged_meta.update(existing_meta)
        merged_meta.update(meta)
        merged_meta.setdefault("created_at", existing_meta.get("created_at") or now)
        merged_meta.update(
            {
                "binder_id": binder_id,
                "chapter_id": chapter_stem,
                "chapter": chapter.order,
                "title": chapter.title,
                "updated_at": now,
            }
        )

        file_contents = _build_frontmatter(merged_meta) + "\n" + body.lstrip("\n")
        file_path.write_text(file_contents, encoding="utf-8")

        sync_result = await compiler.upsert_chapter(
            binder_id,
            {
                "chapter_id": chapter_stem,
                "title": chapter.title,
                "content": body,
                "order": chapter.order,
            },
        )

        return {
            "status": "created" if not file_existed else "updated",
            "binder_id": binder_id,
            "workspace": ws.value,
            "path": str(file_path),
            "db": sync_result,
            "binder_created": created,
        }

    @router.put("/{binder_id}/chapters/{chapter_id}")
    async def update_chapter(
        binder_id: str,
        chapter_id: str,
        request: Request,
        update: ChapterUpdate,
        workspace: Optional[str] = Query(None),
    ):
        if auth_guard:
            await auth_guard(request)
        if update.status and update.status not in {"draft", "review", "complete"}:
            raise HTTPException(
                status_code=400, detail="status must be draft|review|complete"
            )
        ws, binder_path = _resolve_binder_path(binder_id, workspace)
        chapters = _load_chapters_from_files(
            binder_path, include_content=True
        )
        if chapters:
            match = next(
                (
                    c
                    for c in chapters
                    if c.get("chapter_id") == chapter_id
                    or Path(str(c.get("filename", ""))).stem == chapter_id
                ),
                None,
            )
            if not match:
                raise HTTPException(status_code=404, detail="Chapter not found")

            file_path = Path(match["path"])
            meta, body = _split_frontmatter(
                file_path.read_text(encoding="utf-8")
            )
            if update.title:
                meta["title"] = update.title
            if update.order is not None:
                meta["chapter"] = update.order
            if update.content is not None:
                body = update.content

            meta.setdefault("binder_id", binder_id)
            meta.setdefault("chapter_id", chapter_id)
            meta["updated_at"] = datetime.utcnow().isoformat() + "Z"

            file_contents = _build_frontmatter(meta) + "\n" + body.lstrip("\n")
            file_path.write_text(file_contents, encoding="utf-8")

            sync_result = await compiler.upsert_chapter(
                binder_id,
                {
                    "chapter_id": chapter_id,
                    "title": meta.get("title") or update.title or "Untitled",
                    "content": body,
                    "order": meta.get("chapter") or update.order or 1,
                },
            )
            return {
                "status": "updated",
                "binder_id": binder_id,
                "chapter_id": chapter_id,
                "workspace": ws.value,
                "path": str(file_path),
                "db": sync_result,
            }

        return await compiler.update_chapter(
            binder_id=binder_id, chapter_id=chapter_id, content=update.content or ""
        )

    @router.post("/{binder_id}/export")
    async def export_binder(
        binder_id: str,
        request: Request,
        format: str = Query("markdown"),
        workspace: Optional[str] = Query(None),
    ):
        if auth_guard:
            await auth_guard(request)
        valid_formats = {"markdown", "pdf", "json", "brief"}
        if format not in valid_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Valid: {', '.join(valid_formats)}",
            )
        ws, binder_path = _resolve_binder_path(binder_id, workspace)
        chapters = _load_chapters_from_files(binder_path, include_content=True)
        if chapters:
            await compiler.sync_chapters(binder_id, chapters)
            result = await compiler.compile_chapters(binder_id, chapters, [format])
            source = "files"
        else:
            result = await compiler.compile_binder(binder_id=binder_id, formats=[format])
            source = "db"
        return {
            "status": "exported",
            "binder_id": binder_id,
            "format": format,
            "outputs": result.get("outputs", []),
            "compiled_at": result.get("compiled_at"),
            "workspace": ws.value,
            "source": source,
        }

    return router
