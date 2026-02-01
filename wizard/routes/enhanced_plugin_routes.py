"""
Enhanced Plugin Routes
======================

Extended plugin API with full discovery, git/version control, and installer pathways.

Endpoints:
- GET  /api/plugins/catalog - All plugins with metadata
- GET  /api/plugins/{id} - Specific plugin details
- GET  /api/plugins/search - Search plugins
- POST /api/plugins/{id}/install - Install/update plugin
- GET  /api/plugins/{id}/git/status - Git status
- POST /api/plugins/{id}/git/pull - Update from upstream
- POST /api/plugins/{id}/git/clone - Clone from git
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import json

from wizard.services.enhanced_plugin_discovery import (
    get_discovery_service,
    EnhancedPluginDiscovery,
)
from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("plugin-routes-enhanced")


def create_enhanced_plugin_routes(auth_guard=None):
    """Create enhanced plugin routes with discovery and git management."""

    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/plugins",
        tags=["plugins-enhanced"],
        dependencies=dependencies,
    )

    @router.get("/catalog")
    async def get_plugin_catalog(request: Request):
        """Get complete plugin catalog with all metadata."""
        try:
            discovery = get_discovery_service()
            plugins = discovery.discover_all()

            return {
                "success": True,
                "timestamp": discovery.last_scan,
                "total": len(plugins),
                "plugins": {
                    pid: p.to_dict() for pid, p in plugins.items()
                },
            }
        except Exception as e:
            logger.error(f"[CATALOG] Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/tiers")
    async def get_plugins_by_tier(request: Request):
        """Get plugins organized by tier."""
        try:
            discovery = get_discovery_service()
            discovery.discover_all()

            tiers = {}
            for tier in ["core", "library", "extension", "transport", "api"]:
                plugins = discovery.get_plugins_by_tier(tier)
                tiers[tier] = [p.to_dict() for p in plugins]

            return {
                "success": True,
                "tiers": tiers,
            }
        except Exception as e:
            logger.error(f"[TIERS] Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/categories")
    async def get_plugins_by_category(request: Request):
        """Get plugins organized by category."""
        try:
            discovery = get_discovery_service()
            discovery.discover_all()

            categories = {}
            for plugin in discovery.plugins.values():
                cat = plugin.category
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(plugin.to_dict())

            return {
                "success": True,
                "categories": categories,
            }
        except Exception as e:
            logger.error(f"[CATEGORIES] Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/search")
    async def search_plugins(q: str, request: Request):
        """Search plugins by name, description, or ID."""
        try:
            discovery = get_discovery_service()
            discovery.discover_all()

            results = discovery.search_plugins(q)

            return {
                "success": True,
                "query": q,
                "found": len(results),
                "plugins": [p.to_dict() for p in results],
            }
        except Exception as e:
            logger.error(f"[SEARCH] Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/{plugin_id}")
    async def get_plugin_details(plugin_id: str, request: Request):
        """Get detailed information about a specific plugin."""
        try:
            discovery = get_discovery_service()
            discovery.discover_all()

            plugin = discovery.get_plugin(plugin_id)
            if not plugin:
                raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

            return {
                "success": True,
                "plugin": plugin.to_dict(),
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[GET_PLUGIN] Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/{plugin_id}/git/status")
    async def get_plugin_git_status(plugin_id: str, request: Request):
        """Get git status for a plugin."""
        try:
            discovery = get_discovery_service()
            discovery.discover_all()

            plugin = discovery.get_plugin(plugin_id)
            if not plugin:
                raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

            if not plugin.git:
                return {
                    "success": True,
                    "plugin_id": plugin_id,
                    "has_git": False,
                }

            return {
                "success": True,
                "plugin_id": plugin_id,
                "git": plugin.git.to_dict(),
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[GIT_STATUS] Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/{plugin_id}/git/pull")
    async def update_plugin_from_git(
        plugin_id: str,
        request: Request,
        background_tasks: BackgroundTasks,
    ):
        """Update plugin from upstream git repository."""
        try:
            discovery = get_discovery_service()
            discovery.discover_all()

            plugin = discovery.get_plugin(plugin_id)
            if not plugin:
                raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

            if not plugin.git or not plugin.git.remote_url:
                raise HTTPException(
                    status_code=400,
                    detail=f"Plugin {plugin_id} is not git-based or has no remote",
                )

            plugin_path = discovery.udos_root / plugin.source_path

            # Run git pull in background
            background_tasks.add_task(_run_git_pull, plugin_path, plugin_id)

            logger.info(f"[UPDATE] Started git pull for {plugin_id}")

            return {
                "success": True,
                "plugin_id": plugin_id,
                "status": "updating",
                "message": f"Pulling latest changes for {plugin_id}...",
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[UPDATE] Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/{plugin_id}/git/clone")
    async def clone_plugin_from_git(
        plugin_id: str,
        git_url: str,
        request: Request,
        background_tasks: BackgroundTasks,
    ):
        """Clone plugin from git repository."""
        try:
            discovery = get_discovery_service()
            discovery.discover_all()

            # Validate git URL format
            if not (git_url.startswith("git@") or git_url.startswith("https://")):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid git URL format",
                )

            # Determine target path based on plugin_id
            target_path = discovery.udos_root / "extensions" / plugin_id

            # Run git clone in background
            background_tasks.add_task(_run_git_clone, git_url, target_path, plugin_id)

            logger.info(f"[CLONE] Started cloning {plugin_id} from {git_url}")

            return {
                "success": True,
                "plugin_id": plugin_id,
                "status": "cloning",
                "message": f"Cloning {plugin_id} from {git_url}...",
                "target_path": str(target_path),
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[CLONE] Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/{plugin_id}/install")
    async def install_plugin(
        plugin_id: str,
        request: Request,
        background_tasks: BackgroundTasks,
    ):
        """Install or update a plugin."""
        try:
            discovery = get_discovery_service()
            discovery.discover_all()

            plugin = discovery.get_plugin(plugin_id)
            if not plugin:
                raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

            if plugin.installer_type == "container":
                # Container installations use container launcher routes
                raise HTTPException(
                    status_code=400,
                    detail=f"Plugin {plugin_id} is containerized. Use /api/containers/{plugin_id}/launch instead.",
                )

            elif plugin.installer_type == "git":
                if not plugin.git or not plugin.git.remote_url:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Cannot install {plugin_id}: no git remote configured",
                    )

                plugin_path = discovery.udos_root / plugin.source_path
                if plugin_path.exists() and (plugin_path / ".git").exists():
                    # Already cloned, just update
                    background_tasks.add_task(_run_git_pull, plugin_path, plugin_id)
                    return {
                        "success": True,
                        "plugin_id": plugin_id,
                        "status": "updating",
                    }
                else:
                    # Need to clone
                    background_tasks.add_task(
                        _run_git_clone,
                        plugin.git.remote_url,
                        plugin_path,
                        plugin_id,
                    )
                    return {
                        "success": True,
                        "plugin_id": plugin_id,
                        "status": "installing",
                    }

            elif plugin.installer_script:
                # Custom installer script
                background_tasks.add_task(
                    _run_installer_script,
                    discovery.udos_root,
                    plugin.installer_script,
                    plugin_id,
                )
                return {
                    "success": True,
                    "plugin_id": plugin_id,
                    "status": "installing",
                }

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"No installer configured for {plugin_id}",
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[INSTALL] Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    return router


async def _run_git_pull(plugin_path: Path, plugin_id: str):
    """Run git pull in the plugin directory."""
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=str(plugin_path),
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            logger.error(f"[GIT_PULL] Failed for {plugin_id}: {result.stderr}")
        else:
            logger.info(f"[GIT_PULL] Successfully updated {plugin_id}")
    except Exception as e:
        logger.error(f"[GIT_PULL] Error updating {plugin_id}: {str(e)}")


async def _run_git_clone(git_url: str, target_path: Path, plugin_id: str):
    """Clone a git repository."""
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            ["git", "clone", git_url, str(target_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            logger.error(f"[GIT_CLONE] Failed for {plugin_id}: {result.stderr}")
        else:
            logger.info(f"[GIT_CLONE] Successfully cloned {plugin_id} to {target_path}")
    except Exception as e:
        logger.error(f"[GIT_CLONE] Error cloning {plugin_id}: {str(e)}")


async def _run_installer_script(repo_root: Path, script_path: str, plugin_id: str):
    """Run a custom installer script."""
    try:
        full_script_path = repo_root / script_path
        if not full_script_path.exists():
            logger.error(f"[INSTALLER] Script not found: {script_path}")
            return

        result = subprocess.run(
            ["python", str(full_script_path)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            logger.error(f"[INSTALLER] Failed for {plugin_id}: {result.stderr}")
        else:
            logger.info(f"[INSTALLER] Successfully installed {plugin_id}")
    except Exception as e:
        logger.error(f"[INSTALLER] Error installing {plugin_id}: {str(e)}")
