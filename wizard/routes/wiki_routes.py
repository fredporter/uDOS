"""
Wiki Routes - Public Wiki Management

Provides API endpoints for:
- Wiki structure and metadata
- Browsing wiki categories and pages
- Wiki provisioning and setup
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Callable, Optional

from wizard.services.wiki_provisioning_service import get_wiki_service
import os
from pathlib import Path
from wizard.services.path_utils import get_repo_root


def create_wiki_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    """Create wiki routes."""
    router = APIRouter(prefix="/api/wiki", tags=["wiki"])

    env_root = os.getenv("UDOS_ROOT")
    base_root = Path(env_root).expanduser() if env_root else get_repo_root()
    wiki_root = base_root / "wiki"
    wiki_service = get_wiki_service(wiki_root)

    @router.get("/")
    async def get_wiki_index(request: Request):
        """Get wiki index and structure."""
        if auth_guard:
            await auth_guard(request)

        return wiki_service.get_structure()

    @router.get("/structure")
    async def get_wiki_structure(request: Request):
        """Get complete wiki structure."""
        if auth_guard:
            await auth_guard(request)

        return wiki_service.get_structure()

    @router.get("/categories")
    async def list_wiki_categories(request: Request):
        """List all wiki categories."""
        if auth_guard:
            await auth_guard(request)

        structure = wiki_service.get_structure()
        return {"categories": structure["categories"]}

    @router.get("/categories/{category_slug}")
    async def get_wiki_category(category_slug: str, request: Request):
        """Get specific wiki category with pages."""
        if auth_guard:
            await auth_guard(request)

        category = wiki_service.get_category(category_slug)
        if not category:
            raise HTTPException(
                status_code=404, detail=f"Category not found: {category_slug}"
            )

        pages = wiki_service.get_pages_by_category(category_slug)

        return {
            "category": category.to_dict(),
            "pages": [p.to_dict() for p in pages],
        }

    @router.get("/pages")
    async def list_wiki_pages(request: Request):
        """List all wiki pages."""
        if auth_guard:
            await auth_guard(request)

        structure = wiki_service.get_structure()
        return {"pages": structure["pages"]}

    @router.get("/pages/{page_slug}")
    async def get_wiki_page(page_slug: str, request: Request):
        """Get specific wiki page metadata."""
        if auth_guard:
            await auth_guard(request)

        page = wiki_service.get_page(page_slug)
        if not page:
            raise HTTPException(status_code=404, detail=f"Page not found: {page_slug}")

        return page.to_dict()

    @router.get("/files")
    async def list_wiki_files(request: Request):
        """List markdown files under /wiki."""
        if auth_guard:
            await auth_guard(request)

        if not wiki_root.exists():
            return {"files": []}

        files = []
        for path in wiki_root.rglob("*.md"):
            rel = path.relative_to(wiki_root).as_posix()
            files.append({"path": rel, "name": path.name})
        files.sort(key=lambda item: item["path"])
        return {"files": files}

    @router.get("/file")
    async def read_wiki_file(path: str, request: Request):
        """Read a specific wiki markdown file."""
        if auth_guard:
            await auth_guard(request)

        candidate = (wiki_root / path).resolve()
        if not str(candidate).startswith(str(wiki_root.resolve())):
            raise HTTPException(status_code=400, detail="Invalid wiki path")
        if not candidate.exists() or not candidate.is_file():
            raise HTTPException(status_code=404, detail="Wiki file not found")
        return candidate.read_text()

    @router.post("/provision")
    async def provision_wiki(request: Request):
        """Provision wiki directories and structure."""
        if auth_guard:
            await auth_guard(request)

        try:
            wiki_service.provision()
            return {
                "status": "success",
                "message": "Wiki provisioned successfully",
                "wiki_root": str(wiki_root),
                "structure": wiki_service.get_structure(),
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Wiki provisioning failed: {str(e)}"
            )

    return router
