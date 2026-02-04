"""
Catalog Routes
==============

Expose the Wizard plugin repository catalog.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from wizard.services.plugin_repository import get_repository
from wizard.services.path_utils import get_repo_root


def create_catalog_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/catalog", tags=["catalog"], dependencies=dependencies)

    @router.get("/stats")
    async def get_stats():
        repo = get_repository()
        return {"success": True, "stats": repo.get_stats()}

    @router.get("/categories")
    async def get_categories():
        repo = get_repository()
        return {"success": True, "categories": repo.get_categories()}

    @router.get("/plugins")
    async def list_plugins(category: Optional[str] = None, installed_only: bool = False):
        repo = get_repository()
        plugins = repo.list_plugins(category=category, installed_only=installed_only)
        return {"success": True, "plugins": [p.to_dict() for p in plugins]}

    @router.get("/search")
    async def search_plugins(q: str):
        repo = get_repository()
        plugins = repo.search_plugins(q)
        return {"success": True, "plugins": [p.to_dict() for p in plugins]}

    @router.post("/updates/refresh")
    async def refresh_updates():
        repo = get_repository()
        result = repo.refresh_update_flags()
        return {"success": True, "result": result}

    @router.get("/plugins/{plugin_id}")
    async def get_plugin(plugin_id: str):
        repo = get_repository()
        plugin = repo.get_plugin(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
        return {"success": True, "plugin": plugin.to_dict()}

    @router.post("/plugins/{plugin_id}/verify")
    async def verify_plugin(plugin_id: str):
        repo = get_repository()
        plugin = repo.get_plugin(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")

        if not plugin.package_file:
            raise HTTPException(status_code=400, detail="Plugin has no package file")

        package_path = (
            get_repo_root()
            / "distribution"
            / "plugins"
            / "packages"
            / plugin.id
            / plugin.package_file
        )
        return {
            "success": True,
            "verified": repo.verify_package(package_path),
            "path": str(package_path),
        }

    @router.post("/plugins/{plugin_id}/enable")
    async def enable_plugin(plugin_id: str):
        """Enable a plugin in the catalog."""
        repo = get_repository()
        plugin = repo.get_plugin(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")

        try:
            result = repo.enable_plugin(plugin_id)
            return {
                "success": result,
                "message": f"Plugin {plugin_id} enabled" if result else "Failed to enable plugin",
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/plugins/{plugin_id}/disable")
    async def disable_plugin(plugin_id: str):
        """Disable a plugin in the catalog."""
        repo = get_repository()
        plugin = repo.get_plugin(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")

        try:
            result = repo.disable_plugin(plugin_id)
            return {
                "success": result,
                "message": f"Plugin {plugin_id} disabled" if result else "Failed to disable plugin",
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
