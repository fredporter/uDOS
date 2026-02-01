"""
Library Management API Routes

Provides REST endpoints for managing library integrations and plugins.
Migrated from Goblin to Wizard for centralized management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Dict, Any, List, Optional
from pathlib import Path
from typing import Callable, Awaitable

from core.services.prompt_parser_service import get_prompt_parser_service
from core.services.todo_service import (
    CalendarGridRenderer,
    GanttGridRenderer,
    get_service as get_todo_manager,
)
from core.services.todo_reminder_service import get_reminder_service

from core.services.health_training import log_plugin_install_event
from wizard.services.library_manager_service import get_library_manager, InstallResult
from wizard.services.system_info_service import LibraryStatus, LibraryIntegration
from wizard.services.plugin_repository import PluginRepository
from wizard.services.plugin_validation import load_manifest, validate_manifest
from wizard.services.path_utils import get_repo_root
from wizard.tools.github_dev import PluginFactory
from wizard.services.plugin_factory import APKBuilder
import shutil
import os


AuthGuard = Optional[Callable[[Request], Awaitable[None]]]

router = APIRouter(prefix="/api/library", tags=["library"])
_auth_guard: AuthGuard = None
_todo_manager = get_todo_manager()
_calendar_renderer = CalendarGridRenderer()
_gantt_renderer = GanttGridRenderer()
_prompt_parser = get_prompt_parser_service()
_reminder_service = get_reminder_service(_todo_manager)


def _build_prompt_instruction(name: str, manifest: Dict[str, Any]) -> str:
    version = manifest.get("version") or manifest.get("manifest_version") or "latest"
    description = manifest.get("description", "No description provided.")
    return (
        f"Install plugin {name} (version {version}). "
        f"Verify the manifest checksum, apply dependencies, and register the integration with Wizard, logging the outcome for operators. "
        f"Description: {description}"
    )


def _generate_prompt_payload(name: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
    instruction_text = _build_prompt_instruction(name, manifest)
    parsed = _prompt_parser.parse(instruction_text)
    tasks = parsed.get("tasks", [])
    for task in tasks:
        _todo_manager.add(task)

    calendar_lines = _calendar_renderer.render_calendar(
        _todo_manager.list_pending(), view="weekly"
    )
    gantt_lines = _gantt_renderer.render_gantt(
        _todo_manager.list_pending(), window_days=30
    )
    reminder_payload = _reminder_service.log_reminder(
        horizon_hours=parsed.get("reminder", {}).get("horizon_hours")
    )

    payload = {
        "instruction": {
            "id": parsed["instruction_id"],
            "label": parsed["instruction_label"],
            "description": parsed["instruction_description"],
            "story_guidance": parsed.get("story_guidance", ""),
            "reference_links": parsed.get("reference_links", []),
        },
        "tasks": [task.to_notion_block() for task in tasks],
        "calendar": {"view": "weekly", "lines": calendar_lines, "output": "\n".join(calendar_lines)},
        "gantt": {"window_days": 30, "lines": gantt_lines, "output": "\n".join(gantt_lines)},
        "reminder": reminder_payload,
    }
    return payload


async def _run_guard(request: Request) -> None:
    if not _auth_guard:
        return
    result = _auth_guard(request)
    if hasattr(result, "__await__"):
        await result


@router.get("/status", response_model=Dict[str, Any])
async def get_library_status(request: Request):
    """
    Get comprehensive library status.

    Returns:
        LibraryStatus with all integrations and their states
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        status = manager.get_library_status()

        return {
            "success": True,
            "library_root": str(status.library_root),
            "dev_library_root": str(status.dev_library_root),
            "total_integrations": status.total_integrations,
            "installed_count": status.installed_count,
            "enabled_count": status.enabled_count,
            "integrations": [
                {
                    "name": integration.name,
                    "path": str(integration.path),
                    "source": integration.source,
                    "has_container": integration.has_container,
                    "version": integration.version,
                    "description": integration.description,
                    "installed": integration.installed,
                    "enabled": integration.enabled,
                    "can_install": integration.can_install,
                }
                for integration in status.integrations
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get library status: {str(e)}"
        )


@router.get("/integration/{name}", response_model=Dict[str, Any])
async def get_integration(name: str, request: Request):
    """
    Get specific integration details.

    Args:
        name: Integration name

    Returns:
        Integration details or 404 if not found
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        integration = manager.get_integration(name)

        if not integration:
            raise HTTPException(
                status_code=404, detail=f"Integration not found: {name}"
            )

        return {
            "success": True,
            "integration": {
                "name": integration.name,
                "path": str(integration.path),
                "source": integration.source,
                "has_container": integration.has_container,
                "version": integration.version,
                "description": integration.description,
                "installed": integration.installed,
                "enabled": integration.enabled,
                "can_install": integration.can_install,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get integration: {str(e)}"
        )


@router.post("/integration/{name}/install", response_model=Dict[str, Any])
async def install_integration(
    name: str, background_tasks: BackgroundTasks, request: Request
):
    """
    Install an integration from /library or /dev/library.

    Steps:
    1. Run setup.sh if present
    2. Build APK package if APKBUILD exists
    3. Install via package manager

    Args:
        name: Integration name to install

    Returns:
        Installation result
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()

        # Check if integration exists
        integration = manager.get_integration(name)
        if not integration:
            raise HTTPException(
                status_code=404, detail=f"Integration not found: {name}"
            )

        if not integration.can_install:
            raise HTTPException(
                status_code=400,
                detail="Integration cannot be installed (missing container.json)",
            )

        manifest_data = load_manifest(Path(integration.path))
        repo = PluginRepository(
            base_dir=get_repo_root() / "wizard" / "distribution" / "plugins"
        )
        repo_entry = repo.get_plugin(name)
        repo_entry_dict = repo_entry.to_dict() if repo_entry else {}
        validation = validate_manifest(manifest_data, name, repo_entry_dict)

        prompt_payload = _generate_prompt_payload(name, manifest_data)
        if integration.installed:
            log_plugin_install_event(
                name,
                "wizard-api",
                {"success": True, "action": "install", "message": "Already installed"},
                manifest=manifest_data,
                validation=validation,
            )
            return {
                "success": True,
                "result": {
                    "success": True,
                    "plugin_name": name,
                    "action": "install",
                    "message": "Already installed",
                },
                "prompt": prompt_payload,
            }

        # Perform installation
        result = manager.install_integration(name)
        log_plugin_install_event(
            name,
            "wizard-api",
            result,
            manifest=manifest_data,
            validation=validation,
        )

        return {
            "success": result.success,
            "result": {
                "success": result.success,
                "plugin_name": result.plugin_name,
                "action": result.action,
                "message": result.message,
                "error": result.error,
            },
            "prompt": prompt_payload,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to install integration: {str(e)}"
        )


@router.post("/integration/{name}/enable", response_model=Dict[str, Any])
async def enable_integration(name: str, request: Request):
    """
    Enable an installed integration.

    Adds to plugins.enabled config file.

    Args:
        name: Integration name to enable

    Returns:
        Enable result
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        result = manager.enable_integration(name)

        return {
            "success": result.success,
            "result": {
                "success": result.success,
                "plugin_name": result.plugin_name,
                "action": result.action,
                "message": result.message,
                "error": result.error,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to enable integration: {str(e)}"
        )


@router.post("/integration/{name}/disable", response_model=Dict[str, Any])
async def disable_integration(name: str, request: Request):
    """
    Disable an integration.

    Removes from plugins.enabled config file.

    Args:
        name: Integration name to disable

    Returns:
        Disable result
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        result = manager.disable_integration(name)

        return {
            "success": result.success,
            "result": {
                "success": result.success,
                "plugin_name": result.plugin_name,
                "action": result.action,
                "message": result.message,
                "error": result.error,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to disable integration: {str(e)}"
        )


@router.delete("/integration/{name}", response_model=Dict[str, Any])
async def uninstall_integration(
    name: str, background_tasks: BackgroundTasks, request: Request
):
    """
    Uninstall an integration.

    1. Disable if enabled
    2. Remove via package manager
    3. Clean up build artifacts

    Args:
        name: Integration name to uninstall

    Returns:
        Uninstall result
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        result = manager.uninstall_integration(name)

        return {
            "success": result.success,
            "result": {
                "success": result.success,
                "plugin_name": result.plugin_name,
                "action": result.action,
                "message": result.message,
                "error": result.error,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to uninstall integration: {str(e)}"
        )


@router.get("/enabled", response_model=Dict[str, Any])
async def get_enabled_integrations(request: Request):
    """
    Get list of enabled integrations.

    Returns:
        List of enabled integration names
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        status = manager.get_library_status()

        enabled_integrations = [
            integration for integration in status.integrations if integration.enabled
        ]

        return {
            "success": True,
            "enabled_count": len(enabled_integrations),
            "enabled_integrations": [
                {
                    "name": integration.name,
                    "version": integration.version,
                    "description": integration.description,
                    "source": integration.source,
                }
                for integration in enabled_integrations
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get enabled integrations: {str(e)}"
        )


@router.get("/available", response_model=Dict[str, Any])
async def get_available_integrations(request: Request):
    """
    Get list of integrations available for installation.

    Returns:
        List of integrations that can be installed
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        status = manager.get_library_status()

        available_integrations = [
            integration
            for integration in status.integrations
            if integration.can_install and not integration.installed
        ]

        return {
            "success": True,
            "available_count": len(available_integrations),
            "available_integrations": [
                {
                    "name": integration.name,
                    "version": integration.version,
                    "description": integration.description,
                    "source": integration.source,
                    "path": str(integration.path),
                }
                for integration in available_integrations
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get available integrations: {str(e)}"
        )


@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_library_status(request: Request):
    """
    Refresh library status by rescanning directories.

    Returns:
        Updated library status
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        # Just getting fresh status will trigger rescan
        status = manager.get_library_status()

        return {
            "success": True,
            "message": "Library status refreshed",
            "total_integrations": status.total_integrations,
            "installed_count": status.installed_count,
            "enabled_count": status.enabled_count,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to refresh library status: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_library_stats(request: Request):
    """
    Get library statistics summary.

    Returns:
        High-level stats for dashboard display
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        status = manager.get_library_status()

        return {
            "success": True,
            "stats": {
                "total_integrations": status.total_integrations,
                "installed_count": status.installed_count,
                "enabled_count": status.enabled_count,
                "available_count": len(
                    [
                        i
                        for i in status.integrations
                        if i.can_install and not i.installed
                    ]
                ),
                "sources": {
                    "library": len(
                        [i for i in status.integrations if i.source == "library"]
                    ),
                    "dev_library": len(
                        [i for i in status.integrations if i.source == "dev_library"]
                    ),
                },
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get library stats: {str(e)}"
        )


# Add router to main server
@router.get("/inventory", response_model=Dict[str, Any])
async def get_library_inventory(request: Request):
    """
    Get dependency inventory for all integrations.
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        inventory = manager.get_dependency_inventory()
        return {"success": True, "inventory": inventory}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get inventory: {str(e)}"
        )


@router.post("/toolchain/update", response_model=Dict[str, Any])
async def update_toolchain(request: Request, packages: Optional[List[str]] = None):
    """
    Update Alpine toolchain packages (python3, py3-pip, etc.).
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        result = manager.update_alpine_toolchain(packages=packages)
        return {"success": result["success"], "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update toolchain: {str(e)}"
        )


@router.get("/repos", response_model=Dict[str, Any])
async def list_repos(request: Request):
    """
    List cloned library repos (library/containers).
    """
    try:
        await _run_guard(request)
        if repo.startswith("http") and "github.com" not in repo:
            raise HTTPException(status_code=400, detail="Only GitHub repos supported")

        factory = PluginFactory()
        return {"success": True, "repos": factory.list_repos()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list repos: {str(e)}")


@router.post("/repos/clone", response_model=Dict[str, Any])
async def clone_repo(request: Request, repo: str, branch: str = "main"):
    """
    Clone a repo into library/containers.
    """
    try:
        await _run_guard(request)
        allowlist = os.environ.get("WIZARD_LIBRARY_REPO_ALLOWLIST", "").strip()
        if allowlist:
            allowed = [item.strip() for item in allowlist.split(",") if item.strip()]
            if not any(
                repo == entry
                or repo.startswith(entry.rstrip("*"))
                or repo == entry.rstrip("*")
                for entry in allowed
            ):
                raise HTTPException(status_code=403, detail="Repo not allowed")

        factory = PluginFactory()
        cloned = factory.clone(repo, branch=branch)
        if not cloned:
            raise HTTPException(status_code=400, detail="Clone failed")
        return {"success": True, "repo": cloned.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone repo: {str(e)}")


@router.post("/repos/{name}/update", response_model=Dict[str, Any])
async def update_repo(name: str, request: Request):
    """
    Update a cloned repo (fast-forward).
    """
    try:
        await _run_guard(request)
        factory = PluginFactory()
        ok = factory.update(name)
        if not ok:
            raise HTTPException(status_code=400, detail="Update failed")
        return {"success": True, "name": name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update repo: {str(e)}")


@router.post("/repos/{name}/build", response_model=Dict[str, Any])
async def build_repo(name: str, request: Request, format: str = "tar.gz"):
    """
    Build a distribution package from a cloned repo.
    """
    try:
        await _run_guard(request)
        if format not in ("tar.gz", "zip", "tcz"):
            raise HTTPException(status_code=400, detail="Unsupported format")
        factory = PluginFactory()
        result = factory.build(name, format=format)
        return {"success": result.success, "result": result.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build repo: {str(e)}")


@router.get("/packages", response_model=Dict[str, Any])
async def list_packages(request: Request):
    """
    List built packages in library/packages.
    """
    try:
        await _run_guard(request)
        factory = PluginFactory()
        return {"success": True, "packages": factory.list_packages()}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list packages: {str(e)}"
        )


@router.post("/repos/{name}/build-apk", response_model=Dict[str, Any])
async def build_repo_apk(name: str, request: Request, arch: str = "x86_64"):
    """
    Build an Alpine APK from a cloned repo in library/containers.
    """
    try:
        await _run_guard(request)
        repo_root = get_repo_root()
        container_path = repo_root / "library" / "containers" / name
        builder = APKBuilder()
        result = builder.build_apk(name, container_path=container_path, arch=arch)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error or "APK build failed")
        return {"success": True, "result": {"package_path": str(result.package_path)}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build APK: {str(e)}")


@router.post("/apk/index", response_model=Dict[str, Any])
async def generate_apk_index(request: Request):
    """
    Generate APKINDEX for distribution/plugins.
    """
    try:
        await _run_guard(request)
        builder = APKBuilder()
        ok, message = builder.generate_apkindex()
        if not ok:
            raise HTTPException(status_code=400, detail=message)
        return {"success": True, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate APKINDEX: {str(e)}"
        )


@router.get("/apk/status", response_model=Dict[str, Any])
async def get_apk_status(request: Request):
    """
    Get APK toolchain and signing status.
    """
    try:
        await _run_guard(request)
        builder = APKBuilder()
        abuild_ok = shutil.which("abuild") is not None
        apk_ok = shutil.which("apk") is not None
        key_ok, key_msg = builder._check_abuild_key()
        return {
            "success": True,
            "abuild": abuild_ok,
            "apk": apk_ok,
            "signing": {"ok": key_ok, "detail": key_msg},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get APK status: {str(e)}")


def get_library_router(auth_guard: AuthGuard = None):
    """Get the library management router."""
    global _auth_guard
    _auth_guard = auth_guard
    return router
