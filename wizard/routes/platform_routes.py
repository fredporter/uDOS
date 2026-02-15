"""Platform integration routes for Wizard GUI.

Exposes unified status for Sonic, Groovebox, and GUI theme/CSS extensions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from wizard.services.sonic_bridge_service import get_sonic_bridge_service
from wizard.services.theme_extension_service import get_theme_extension_service

AuthGuard = Optional[Callable]


def create_platform_routes(auth_guard: AuthGuard = None, repo_root: Optional[Path] = None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/platform", tags=["platform"], dependencies=dependencies)

    sonic = get_sonic_bridge_service(repo_root=repo_root)
    themes = get_theme_extension_service(repo_root=repo_root)

    @router.get("/sonic/status")
    async def sonic_status():
        return sonic.get_status()

    @router.get("/sonic/artifacts")
    async def sonic_artifacts(limit: int = Query(200, ge=1, le=1000)):
        return sonic.list_artifacts(limit=limit)

    @router.get("/groovebox/status")
    async def groovebox_status():
        root = (repo_root or Path(__file__).resolve().parent.parent.parent) / "groovebox"
        available = root.exists()
        return {
            "available": available,
            "root": str(root),
            "wizard_gui_hosted": True,
            "api_prefix": "/api/groovebox",
            "dashboard_route": "#groovebox",
        }

    @router.get("/themes/css-extensions")
    async def theme_css_extensions():
        return themes.list_css_extensions()

    @router.get("/dev/scaffold")
    async def dev_scaffold_status():
        root = (repo_root or Path(__file__).resolve().parent.parent.parent) / "dev" / "goblin"
        if not root.exists():
            raise HTTPException(status_code=404, detail="/dev/goblin scaffold not found")
        required = {
            "scripts": (root / "scripts").exists(),
            "tests": (root / "tests").exists(),
            "wizard_sandbox": (root / "wizard-sandbox").exists(),
        }
        return {
            "root": str(root),
            "required": required,
            "ready": all(required.values()),
        }

    return router
