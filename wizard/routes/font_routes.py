"""
Font Routes
===========

Serve font manifests and font files for Wizard tools.
"""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from wizard.services.path_utils import get_repo_root


def _resolve_fonts_root() -> Optional[Path]:
    repo_root = get_repo_root()
    candidates = [
        repo_root / "wizard" / "font-manager" / "fonts",
        repo_root / "dev" / "goblin" / "fonts",
        repo_root / "library" / "fonts",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def create_font_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/fonts", tags=["fonts"], dependencies=dependencies)

    @router.get("/manifest")
    async def get_manifest():
        fonts_root = _resolve_fonts_root()
        if not fonts_root:
            raise HTTPException(status_code=404, detail="Fonts root not found")
        manifest_path = fonts_root / "manifest.json"
        if not manifest_path.exists():
            raise HTTPException(status_code=404, detail="manifest.json missing")
        return FileResponse(str(manifest_path))

    @router.get("/sample")
    async def get_sample():
        fonts_root = _resolve_fonts_root()
        if not fonts_root:
            raise HTTPException(status_code=404, detail="Fonts root not found")
        sample_path = fonts_root / "font-test.md"
        if not sample_path.exists():
            # Fallback to goblin static if present
            sample_path = (
                get_repo_root()
                / "dev"
                / "goblin"
                / "static"
                / "font-test.md"
            )
        if not sample_path.exists():
            raise HTTPException(status_code=404, detail="font-test.md missing")
        return FileResponse(str(sample_path))

    @router.get("/file")
    async def get_font_file(path: str):
        fonts_root = _resolve_fonts_root()
        if not fonts_root:
            raise HTTPException(status_code=404, detail="Fonts root not found")
        safe_path = (fonts_root / path).resolve()
        if not str(safe_path).startswith(str(fonts_root.resolve())):
            raise HTTPException(status_code=400, detail="Invalid font path")
        if not safe_path.exists() or not safe_path.is_file():
            raise HTTPException(status_code=404, detail="Font file not found")
        if safe_path.suffix.lower() not in {".ttf", ".otf", ".woff", ".woff2"}:
            raise HTTPException(status_code=400, detail="Unsupported font type")
        return FileResponse(str(safe_path))

    return router
