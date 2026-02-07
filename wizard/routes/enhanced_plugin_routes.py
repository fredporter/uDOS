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
from wizard.services.plugin_registry import get_registry
from wizard.services.plugin_repository import get_repository

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

    @router.get("/dashboard")
    async def get_plugins_dashboard(request: Request):
        """Aggregate registry + catalog + discovery into a dashboard payload."""
        try:
            discovery = get_discovery_service()
            discovery_plugins = discovery.discover_all()
            catalog_repo = get_repository()
            catalog_plugins = {p.id: p for p in catalog_repo.list_plugins()}
            registry = get_registry().build_registry(refresh=False, include_manifests=False)

            all_ids = set(discovery_plugins.keys()) | set(catalog_plugins.keys()) | set(registry.keys())
            items: Dict[str, Any] = {}

            for plugin_id in sorted(all_ids):
                discovery_item = discovery_plugins.get(plugin_id)
                catalog_item = catalog_plugins.get(plugin_id)
                registry_item = registry.get(plugin_id) or {}
                manifest_report = (registry_item.get("manifest_report") or {})

                item = {
                    "id": plugin_id,
                    "name": (discovery_item.name if discovery_item else None)
                    or (catalog_item.name if catalog_item else plugin_id),
                    "description": (discovery_item.description if discovery_item else None)
                    or (catalog_item.description if catalog_item else ""),
                    "category": (discovery_item.category if discovery_item else None)
                    or (catalog_item.category if catalog_item else "plugin"),
                    "tier": (discovery_item.tier if discovery_item else None) or "core",
                    "version": (discovery_item.version if discovery_item else None)
                    or (catalog_item.version if catalog_item else "0.0.0"),
                    "installed": (discovery_item.installed if discovery_item else False)
                    or (catalog_item.installed if catalog_item else False),
                    "installed_version": (discovery_item.installed_version if discovery_item else None)
                    or (catalog_item.installed_version if catalog_item else None),
                    "update_available": (discovery_item.update_available if discovery_item else False)
                    or (catalog_item.update_available if catalog_item else False),
                    "enabled": (catalog_item.enabled if catalog_item else False),
                    "license": (discovery_item.license if discovery_item else None)
                    or (catalog_item.license if catalog_item else "MIT"),
                    "author": (discovery_item.author if discovery_item else None)
                    or (catalog_item.author if catalog_item else ""),
                    "homepage": (discovery_item.homepage if discovery_item else None)
                    or (catalog_item.homepage if catalog_item else ""),
                    "documentation": (discovery_item.documentation if discovery_item else None)
                    or (catalog_item.documentation if catalog_item else ""),
                    "source_path": (discovery_item.source_path if discovery_item else None),
                    "config_path": (discovery_item.config_path if discovery_item else None),
                    "installer_type": (discovery_item.installer_type if discovery_item else "manual"),
                    "installer_script": (discovery_item.installer_script if discovery_item else None),
                    "package_file": (discovery_item.package_file if discovery_item else None)
                    or (catalog_item.package_file if catalog_item else None),
                    "dependencies": (discovery_item.dependencies if discovery_item else [])
                    or (catalog_item.dependencies if catalog_item else []),
                    "health_check_url": (discovery_item.health_check_url if discovery_item else None),
                    "running": (discovery_item.running if discovery_item else False),
                    "git": (discovery_item.git.to_dict() if discovery_item and discovery_item.git else None),
                    "registry": {
                        "registered": bool(registry_item),
                        "manifest_type": manifest_report.get("manifest_type"),
                        "validation_status": manifest_report.get("validation_status"),
                        "issues": manifest_report.get("issues", []),
                        "packages": registry_item.get("packages", []),
                    },
                }
                items[plugin_id] = item

            summary = {
                "total": len(items),
                "installed": len([p for p in items.values() if p.get("installed")]),
                "enabled": len([p for p in items.values() if p.get("enabled")]),
                "updates": len([p for p in items.values() if p.get("update_available")]),
            }

            return {
                "success": True,
                "summary": summary,
                "plugins": items,
            }
        except Exception as e:
            logger.error(f"[DASHBOARD] Error: {str(e)}")
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

    @router.post("/{plugin_id}/uninstall")
    async def uninstall_plugin(plugin_id: str, request: Request):
        """Uninstall a plugin by removing its source directory."""
        try:
            discovery = get_discovery_service()
            discovery.discover_all()
            plugin = discovery.get_plugin(plugin_id)
            if not plugin:
                raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")
            plugin_path = discovery.udos_root / plugin.source_path
            if not plugin_path.exists():
                return {
                    "success": True,
                    "plugin_id": plugin_id,
                    "status": "not_installed",
                    "message": "Plugin path not found",
                }
            # Safety: only remove known plugin paths
            plugin_path = plugin_path.resolve()
            if discovery.udos_root not in plugin_path.parents:
                raise HTTPException(status_code=400, detail="Invalid plugin path")
            import shutil
            shutil.rmtree(plugin_path)
            return {
                "success": True,
                "plugin_id": plugin_id,
                "status": "uninstalled",
                "message": "Plugin removed",
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[UNINSTALL] Error: {str(e)}")
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
