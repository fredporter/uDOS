"""
Diagram Template Routes
=======================

Expose seeded diagram templates for SVG tooling.
"""

from pathlib import Path
from typing import List, Optional
import tempfile
import subprocess
import shutil

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from wizard.services.path_utils import get_repo_root, get_memory_dir


ALLOWED_EXTENSIONS = {".txt", ".json", ".md", ".svg"}
ALLOWED_RENDER_ENGINES = {"mermaid"}


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

    class RenderRequest(BaseModel):
        source: str
        engine: str = "mermaid"
        output_file: Optional[str] = None

    def _render_mermaid(source: str) -> str:
        mmdc = shutil.which("mmdc")
        if not mmdc:
            raise HTTPException(
                status_code=503,
                detail="Mermaid renderer unavailable (mmdc not installed)",
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            in_file = tmp / "diagram.mmd"
            out_file = tmp / "diagram.svg"
            in_file.write_text(source, encoding="utf-8")
            proc = subprocess.run(
                [mmdc, "-i", str(in_file), "-o", str(out_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode != 0 or not out_file.exists():
                detail = (proc.stderr or proc.stdout or "diagram render failed").strip()
                raise HTTPException(status_code=500, detail=detail[:4000])
            return out_file.read_text(encoding="utf-8")

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

    @router.get("/health")
    async def diagram_health():
        return {
            "success": True,
            "engines": {
                "mermaid": {
                    "available": shutil.which("mmdc") is not None,
                }
            },
        }

    @router.post("/render")
    async def render_diagram(payload: RenderRequest):
        engine = (payload.engine or "").strip().lower()
        if engine not in ALLOWED_RENDER_ENGINES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported engine: {payload.engine}",
            )
        if not (payload.source or "").strip():
            raise HTTPException(status_code=400, detail="source is required")

        if engine == "mermaid":
            svg = _render_mermaid(payload.source)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported engine: {payload.engine}")

        output_path = None
        if payload.output_file:
            out_root = get_memory_dir() / "diagrams"
            out_root.mkdir(parents=True, exist_ok=True)
            candidate = (out_root / payload.output_file).resolve()
            if not str(candidate).startswith(str(out_root.resolve())):
                raise HTTPException(status_code=400, detail="Invalid output file path")
            if candidate.suffix.lower() != ".svg":
                raise HTTPException(status_code=400, detail="output_file must end with .svg")
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text(svg, encoding="utf-8")
            output_path = str(candidate)

        return {
            "success": True,
            "engine": engine,
            "svg": svg,
            "output_file": output_path,
        }

    return router
