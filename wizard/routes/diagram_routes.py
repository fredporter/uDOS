"""
Diagram Template Routes
=======================

Expose seeded diagram templates for SVG tooling.
"""

from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse

from wizard.services.path_utils import get_repo_root


ALLOWED_EXTENSIONS = {".txt", ".json", ".md", ".svg"}


def _diagrams_root() -> Path:
    return (
        get_repo_root()
        / "core"
        / "framework"
        / "seed"
        / "bank"
        / "graphics"
        / "diagrams"
    )


def _is_allowed(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS


def _safe_resolve(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    if not str(candidate).startswith(str(root.resolve())):
        raise HTTPException(status_code=400, detail="Invalid template path")
    if not _is_allowed(candidate):
        raise HTTPException(status_code=404, detail="Template not found")
    return candidate


def create_diagram_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/diagrams", tags=["diagrams"], dependencies=dependencies
    )

    @router.get("/templates")
    async def list_templates():
        root = _diagrams_root()
        if not root.exists():
            raise HTTPException(status_code=404, detail="Diagrams root not found")

        entries: List[dict] = []
        for path in root.rglob("*"):
            if not _is_allowed(path):
                continue
            rel = path.relative_to(root).as_posix()
            entries.append(
                {
                    "path": rel,
                    "name": path.stem.replace("_", " "),
                    "ext": path.suffix.lower().lstrip("."),
                }
            )

        entries.sort(key=lambda item: item["path"])
        return {"root": str(root), "templates": entries}

    @router.get("/template")
    async def get_template(path: str):
        root = _diagrams_root()
        if not root.exists():
            raise HTTPException(status_code=404, detail="Diagrams root not found")
        file_path = _safe_resolve(root, path)
        return PlainTextResponse(file_path.read_text(encoding="utf-8"))

    return router
