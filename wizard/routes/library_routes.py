"""Library Management API Routes

Provides REST endpoints for managing library integrations and plugins.
Migrated from Goblin to Wizard for centralized management.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import os
from pathlib import Path
import re
import shutil
from typing import Any, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel

from core.services.health_training import log_plugin_install_event
from core.services.prompt_parser_service import get_prompt_parser_service
from core.services.todo_reminder_service import get_reminder_service
from core.services.todo_service import (
    CalendarGridRenderer,
    GanttGridRenderer,
    get_service as get_todo_manager,
)
from core.services.unified_config_loader import get_bool_config
from wizard.services.library_manager_service import get_library_manager
from wizard.services.path_utils import get_repo_root
from wizard.services.plugin_factory import APKBuilder
from wizard.services.plugin_repository import PluginRepository
from wizard.services.plugin_validation import load_manifest, validate_manifest
from wizard.routes.container_launcher_routes import get_launcher
from wizard.tools.github_dev import PluginFactory

AuthGuard = Optional[Callable[[Request], Awaitable[None]]]

router = APIRouter(prefix="/api/library", tags=["library"])
_auth_guard: AuthGuard = None
_todo_manager = get_todo_manager()
_calendar_renderer = CalendarGridRenderer()
_gantt_renderer = GanttGridRenderer()
_prompt_parser = get_prompt_parser_service()
_reminder_service = get_reminder_service(_todo_manager)
_OWNER_REPO_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")


class RepoInstallWizardRequest(BaseModel):
    repo: str
    branch: str = "main"
    launch_if_runnable: bool = True
    open_thin_gui: bool = True


def _build_prompt_instruction(name: str, manifest: dict[str, Any]) -> str:
    version = manifest.get("version") or manifest.get("manifest_version") or "latest"
    description = manifest.get("description", "No description provided.")
    return (
        f"Install plugin {name} (version {version}). "
        f"Verify the manifest checksum, apply dependencies, and register the integration with Wizard, logging the outcome for operators. "
        f"Description: {description}"
    )


def _generate_prompt_payload(name: str, manifest: dict[str, Any]) -> dict[str, Any]:
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
        "tasks": [task.to_task_block() for task in tasks],
        "calendar": {
            "view": "weekly",
            "lines": calendar_lines,
            "output": "\n".join(calendar_lines),
        },
        "gantt": {
            "window_days": 30,
            "lines": gantt_lines,
            "output": "\n".join(gantt_lines),
        },
        "reminder": reminder_payload,
    }
    return payload


async def _run_guard(request: Request) -> None:
    if not _auth_guard:
        return
    result = _auth_guard(request)
    if hasattr(result, "__await__"):
        await result


def _resolve_sonic_integration_name(manager) -> str:
    status = manager.get_library_status()
    names = {integration.name for integration in status.integrations}
    for candidate in ("sonic", "sonic-screwdriver"):
        if candidate in names:
            return candidate
    return "sonic"


def _library_sonic_alias_enabled() -> bool:
    return get_bool_config("UDOS_SONIC_ENABLE_LIBRARY_ALIAS", True)


def _resolve_requested_integration_name(manager, requested_name: str) -> str:
    if requested_name == "sonic":
        if not _library_sonic_alias_enabled():
            raise HTTPException(
                status_code=410,
                detail={
                    "message": "Library Sonic alias retired",
                    "alias": "/api/library/integration/sonic",
                    "canonical": "/api/library/integration/sonic-screwdriver",
                },
            )
        return _resolve_sonic_integration_name(manager)
    return requested_name


def _normalize_repo_input(repo: str) -> dict[str, str]:
    raw = (repo or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="repo is required")

    if _OWNER_REPO_RE.fullmatch(raw):
        owner, name = raw.split("/", 1)
        return {
            "input": raw,
            "kind": "github-shorthand",
            "host": "github.com",
            "owner": owner,
            "name": name,
            "clone_target": raw,
            "canonical_url": f"https://github.com/{owner}/{name}.git",
            "display": raw,
        }

    if raw.startswith(("git@", "ssh://", "file://", "http://")):
        raise HTTPException(
            status_code=400,
            detail="Only owner/name or https repository URLs are supported",
        )

    parsed = urlparse(raw)
    if parsed.scheme != "https" or not parsed.netloc:
        raise HTTPException(
            status_code=400,
            detail="Repository must be owner/name or a valid https URL",
        )
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise HTTPException(
            status_code=400,
            detail="Repository URL must not include credentials, query params, or fragments",
        )

    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2:
        raise HTTPException(
            status_code=400,
            detail="Repository URL must include owner and repository name",
        )

    owner = path_parts[-2]
    name = path_parts[-1].removesuffix(".git")
    if not owner or not name:
        raise HTTPException(status_code=400, detail="Repository URL is missing owner or name")

    canonical_path = "/".join([*path_parts[:-1], f"{name}.git"])
    canonical_url = f"https://{parsed.netloc}/{canonical_path}"
    return {
        "input": raw,
        "kind": "https-url",
        "host": parsed.netloc.lower(),
        "owner": owner,
        "name": name,
        "clone_target": canonical_url,
        "canonical_url": canonical_url,
        "display": f"{owner}/{name}",
    }


def _repo_allowed(normalized: dict[str, str]) -> None:
    allowlist = os.environ.get("WIZARD_LIBRARY_REPO_ALLOWLIST", "").strip()
    if not allowlist:
        return
    allowed = [item.strip() for item in allowlist.split(",") if item.strip()]
    candidates = {
        normalized["input"],
        normalized["display"],
        normalized["clone_target"],
        normalized["canonical_url"],
    }
    for entry in allowed:
        prefix = entry.rstrip("*")
        if any(
            candidate == entry
            or candidate == prefix
            or candidate.startswith(prefix)
            for candidate in candidates
        ):
            return
    raise HTTPException(status_code=403, detail="Repo not allowed")


def _inventory_rows(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, details in sorted((inventory or {}).items()):
        deps = details.get("deps", {}) if isinstance(details, dict) else {}
        apk = list(deps.get("apk_dependencies") or [])
        apt = list(deps.get("apt_dependencies") or [])
        brew = list(deps.get("brew_dependencies") or [])
        pip = list(deps.get("pip_dependencies") or [])
        python_version = deps.get("python_version") or ""
        rows.append(
            {
                "name": name,
                "path": details.get("path"),
                "source": details.get("source"),
                "python_version": python_version,
                "apk_dependencies": apk,
                "apt_dependencies": apt,
                "brew_dependencies": brew,
                "pip_dependencies": pip,
                "dependency_count": len(apk) + len(apt) + len(brew) + len(pip),
            }
        )
    return rows


@router.get("/status", response_model=dict[str, Any])
async def get_library_status(request: Request):
    """Get comprehensive library status.

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
                    "container_type": integration.container_type,
                    "git_cloned": integration.git_cloned,
                    "git_source": integration.git_source,
                    "git_ref": integration.git_ref,
                    "is_running": integration.is_running,
                }
                for integration in status.integrations
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get library status: {e!s}"
        )


@router.get("/aliases/status", response_model=dict[str, Any])
async def get_library_alias_status(request: Request):
    """Return compatibility status for Sonic library integration alias."""
    try:
        await _run_guard(request)
        return {
            "sonic_library_alias_enabled": _library_sonic_alias_enabled(),
            "retirement_target": "v1.5",
            "alias": "/api/library/integration/sonic",
            "canonical": "/api/library/integration/sonic-screwdriver",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get alias status: {e!s}"
        )


@router.get("/integration/{name}", response_model=dict[str, Any])
async def get_integration(name: str, request: Request):
    """Get specific integration details.

    Args:
        name: Integration name

    Returns:
        Integration details or 404 if not found
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        resolved_name = _resolve_requested_integration_name(manager, name)
        integration = manager.get_integration(resolved_name)

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
                "container_type": integration.container_type,
                "git_cloned": integration.git_cloned,
                "git_source": integration.git_source,
                "git_ref": integration.git_ref,
                "is_running": integration.is_running,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get integration: {e!s}")


@router.get("/integration/{name}/versions", response_model=dict[str, Any])
async def get_integration_versions(name: str, request: Request):
    try:
        await _run_guard(request)
        manager = get_library_manager()
        resolved_name = _resolve_requested_integration_name(manager, name)
        payload = manager.get_integration_versions(resolved_name)
        if not payload.get("found"):
            raise HTTPException(
                status_code=404, detail=f"Integration not found: {name}"
            )
        return {"success": True, **payload}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get integration versions: {e!s}"
        )


@router.get("/integration/{name}/dependencies", response_model=dict[str, Any])
async def get_integration_dependencies(name: str, request: Request):
    try:
        await _run_guard(request)
        manager = get_library_manager()
        resolved_name = _resolve_requested_integration_name(manager, name)
        payload = manager.resolve_integration_dependencies(resolved_name)
        if not payload.get("found"):
            raise HTTPException(
                status_code=404, detail=f"Integration not found: {name}"
            )
        return {"success": True, **payload}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get integration dependencies: {e!s}"
        )


@router.post("/integration/{name}/install", response_model=dict[str, Any])
async def install_integration(
    name: str, background_tasks: BackgroundTasks, request: Request
):
    """Install an integration from /library or /dev/library.

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
        resolved_name = _resolve_requested_integration_name(manager, name)

        # Check if integration exists
        integration = manager.get_integration(resolved_name)
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
        validation = validate_manifest(manifest_data, resolved_name, repo_entry_dict)

        prompt_payload = _generate_prompt_payload(resolved_name, manifest_data)
        if integration.installed:
            log_plugin_install_event(
                resolved_name,
                "wizard-api",
                {"success": True, "action": "install", "message": "Already installed"},
                manifest=manifest_data,
                validation=validation,
            )
            return {
                "success": True,
                "result": {
                    "success": True,
                    "plugin_name": resolved_name,
                    "action": "install",
                    "message": "Already installed",
                },
                "prompt": prompt_payload,
            }

        # Perform installation
        result = manager.install_integration(resolved_name)
        log_plugin_install_event(
            resolved_name,
            "wizard-api",
            result,
            manifest=manifest_data,
            validation=validation,
        )

        steps_out = []
        if result.steps:
            for s in result.steps:
                steps_out.append({
                    "n": s.n,
                    "total": s.total,
                    "name": s.name,
                    "ok": s.ok,
                    "detail": s.detail,
                })

        return {
            "success": result.success,
            "result": {
                "success": result.success,
                "plugin_name": result.plugin_name,
                "action": result.action,
                "message": result.message,
                "error": result.error,
                "steps": steps_out,
                "steps_total": len(steps_out),
            },
            "prompt": prompt_payload,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to install integration: {e!s}"
        )


@router.post("/integration/{name}/enable", response_model=dict[str, Any])
async def enable_integration(name: str, request: Request):
    """Enable an installed integration.

    Adds to plugins.enabled config file.

    Args:
        name: Integration name to enable

    Returns:
        Enable result
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        resolved_name = _resolve_requested_integration_name(manager, name)
        result = manager.enable_integration(resolved_name)

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
            status_code=500, detail=f"Failed to enable integration: {e!s}"
        )


@router.post("/integration/{name}/disable", response_model=dict[str, Any])
async def disable_integration(name: str, request: Request):
    """Disable an integration.

    Removes from plugins.enabled config file.

    Args:
        name: Integration name to disable

    Returns:
        Disable result
    """
    try:
        await _run_guard(request)
        manager = get_library_manager()
        resolved_name = _resolve_requested_integration_name(manager, name)
        result = manager.disable_integration(resolved_name)

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
            status_code=500, detail=f"Failed to disable integration: {e!s}"
        )


@router.delete("/integration/{name}", response_model=dict[str, Any])
async def uninstall_integration(
    name: str, background_tasks: BackgroundTasks, request: Request
):
    """Uninstall an integration.

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
        resolved_name = _resolve_requested_integration_name(manager, name)
        result = manager.uninstall_integration(resolved_name)

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
            status_code=500, detail=f"Failed to uninstall integration: {e!s}"
        )


@router.get("/integration/sonic", response_model=dict[str, Any])
async def get_sonic_integration(request: Request):
    await _run_guard(request)
    manager = get_library_manager()
    sonic_name = _resolve_sonic_integration_name(manager)
    integration = manager.get_integration(sonic_name)
    if not integration:
        raise HTTPException(status_code=404, detail="Sonic integration not found")
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


@router.post("/integration/sonic/install", response_model=dict[str, Any])
async def install_sonic_integration(
    background_tasks: BackgroundTasks, request: Request
):
    manager = get_library_manager()
    sonic_name = _resolve_sonic_integration_name(manager)
    return await install_integration(sonic_name, background_tasks, request)


@router.post("/integration/sonic/enable", response_model=dict[str, Any])
async def enable_sonic_integration(request: Request):
    manager = get_library_manager()
    sonic_name = _resolve_sonic_integration_name(manager)
    return await enable_integration(sonic_name, request)


@router.post("/integration/sonic/disable", response_model=dict[str, Any])
async def disable_sonic_integration(request: Request):
    manager = get_library_manager()
    sonic_name = _resolve_sonic_integration_name(manager)
    return await disable_integration(sonic_name, request)


@router.delete("/integration/sonic", response_model=dict[str, Any])
async def uninstall_sonic_integration(
    background_tasks: BackgroundTasks, request: Request
):
    manager = get_library_manager()
    sonic_name = _resolve_sonic_integration_name(manager)
    return await uninstall_integration(sonic_name, background_tasks, request)


@router.get("/enabled", response_model=dict[str, Any])
async def get_enabled_integrations(request: Request):
    """Get list of enabled integrations.

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
            status_code=500, detail=f"Failed to get enabled integrations: {e!s}"
        )


@router.get("/available", response_model=dict[str, Any])
async def get_available_integrations(request: Request):
    """Get list of integrations available for installation.

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
            status_code=500, detail=f"Failed to get available integrations: {e!s}"
        )


@router.post("/refresh", response_model=dict[str, Any])
async def refresh_library_status(request: Request):
    """Refresh library status by rescanning directories.

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
            status_code=500, detail=f"Failed to refresh library status: {e!s}"
        )


@router.get("/stats", response_model=dict[str, Any])
async def get_library_stats(request: Request):
    """Get library statistics summary.

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
                "available_count": len([
                    i for i in status.integrations if i.can_install and not i.installed
                ]),
                "sources": {
                    "library": len([
                        i for i in status.integrations if i.source == "library"
                    ]),
                    "dev_library": len([
                        i for i in status.integrations if i.source == "dev_library"
                    ]),
                },
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get library stats: {e!s}"
        )


# Add router to main server
@router.get("/inventory", response_model=dict[str, Any])
async def get_library_inventory(request: Request):
    """Get dependency inventory for all integrations."""
    try:
        await _run_guard(request)
        manager = get_library_manager()
        inventory = manager.get_dependency_inventory()
        return {
            "success": True,
            "inventory": inventory,
            "rows": _inventory_rows(inventory),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get inventory: {e!s}")


@router.post("/inventory/{name}/install", response_model=dict[str, Any])
async def install_inventory_dependencies(name: str, request: Request):
    """Install declared package dependencies for one inventory row."""
    try:
        await _run_guard(request)
        manager = get_library_manager()
        result = manager.install_inventory_dependencies(name)
        if not result.get("success"):
            detail = result.get("message") or "Dependency install failed"
            status = 404 if detail == "Integration not found" else 400
            raise HTTPException(status_code=status, detail=detail)
        return {"success": True, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to install inventory dependencies: {e!s}"
        )


@router.post("/toolchain/update", response_model=dict[str, Any])
async def update_toolchain(request: Request, packages: list[str] | None = None):
    """Update Alpine toolchain packages (python3, py3-pip, etc.)."""
    try:
        await _run_guard(request)
        manager = get_library_manager()
        result = manager.update_alpine_toolchain(packages=packages)
        return {"success": result["success"], "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update toolchain: {e!s}"
        )


@router.get("/repos", response_model=dict[str, Any])
async def list_repos(request: Request):
    """List cloned library repos (library/containers)."""
    try:
        await _run_guard(request)
        factory = PluginFactory()
        return {"success": True, "repos": factory.list_repos()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list repos: {e!s}")


@router.post("/repos/clone", response_model=dict[str, Any])
async def clone_repo(request: Request, repo: str, branch: str = "main"):
    """Clone a repo into library/containers."""
    try:
        await _run_guard(request)
        normalized = _normalize_repo_input(repo)
        _repo_allowed(normalized)

        factory = PluginFactory()
        cloned = factory.clone(normalized["clone_target"], branch=branch)
        if not cloned:
            raise HTTPException(status_code=400, detail="Clone failed")
        return {
            "success": True,
            "repo": cloned.to_dict(),
            "normalized_repo": normalized,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone repo: {e!s}")


@router.post("/repos/install-wizard", response_model=dict[str, Any])
async def install_repo_wizard(
    request: Request,
    payload: RepoInstallWizardRequest,
    background_tasks: BackgroundTasks,
):
    """Clone a repo, then launch/open it when a runnable container is detected."""
    try:
        await _run_guard(request)
        normalized = _normalize_repo_input(payload.repo)
        _repo_allowed(normalized)

        factory = PluginFactory()
        cloned = factory.clone(normalized["clone_target"], branch=payload.branch.strip() or "main")
        if not cloned:
            raise HTTPException(status_code=400, detail="Clone failed")

        launcher = get_launcher()
        container_config = launcher.get_container_config(cloned.name)
        container_result: dict[str, Any] = {
            "detected": bool(container_config),
            "launch_requested": bool(payload.launch_if_runnable),
            "launched": False,
            "launch_result": None,
            "thin_gui": None,
        }
        if container_config and payload.launch_if_runnable:
            launch_result = await launcher.launch_container(cloned.name, background_tasks)
            container_result["launched"] = bool(launch_result.get("success"))
            container_result["launch_result"] = launch_result
            if payload.open_thin_gui:
                container_result["thin_gui"] = {
                    "target_url": f"http://localhost:{container_config['port']}{container_config['browser_route']}",
                    "target_label": cloned.name,
                    "title": container_config["name"],
                }

        return {
            "success": True,
            "repo": cloned.to_dict(),
            "normalized_repo": normalized,
            "container": container_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run install wizard: {e!s}")


@router.post("/repos/{name}/update", response_model=dict[str, Any])
async def update_repo(name: str, request: Request):
    """Update a cloned repo (fast-forward)."""
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
        raise HTTPException(status_code=500, detail=f"Failed to update repo: {e!s}")


@router.delete("/repos/{name}", response_model=dict[str, Any])
async def delete_repo(name: str, request: Request, remove_packages: bool = False):
    """Delete a cloned repo from library/containers."""
    try:
        await _run_guard(request)
        factory = PluginFactory()
        ok = factory.remove(name, remove_packages=remove_packages)
        if not ok:
            raise HTTPException(status_code=400, detail="Delete failed")
        return {"success": True, "name": name, "remove_packages": remove_packages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete repo: {e!s}")


@router.post("/repos/{name}/build", response_model=dict[str, Any])
async def build_repo(name: str, request: Request, format: str = "tar.gz"):
    """Build a distribution package from a cloned repo."""
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
        raise HTTPException(status_code=500, detail=f"Failed to build repo: {e!s}")


@router.get("/packages", response_model=dict[str, Any])
async def list_packages(request: Request):
    """List built packages in library/packages."""
    try:
        await _run_guard(request)
        factory = PluginFactory()
        return {"success": True, "packages": factory.list_packages()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list packages: {e!s}")


@router.post("/repos/{name}/build-apk", response_model=dict[str, Any])
async def build_repo_apk(name: str, request: Request, arch: str = "x86_64"):
    """Build an Alpine APK from a cloned repo in library/containers."""
    try:
        await _run_guard(request)
        repo_root = get_repo_root()
        container_path = repo_root / "library" / "containers" / name
        builder = APKBuilder()
        result = builder.build_apk(name, container_path=container_path, arch=arch)
        if not result.success:
            raise HTTPException(
                status_code=400, detail=result.error or "APK build failed"
            )
        return {"success": True, "result": {"package_path": str(result.package_path)}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build APK: {e!s}")


@router.post("/apk/index", response_model=dict[str, Any])
async def generate_apk_index(request: Request):
    """Generate APKINDEX for distribution/plugins."""
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
            status_code=500, detail=f"Failed to generate APKINDEX: {e!s}"
        )


@router.get("/apk/status", response_model=dict[str, Any])
async def get_apk_status(request: Request):
    """Get APK toolchain and signing status."""
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
        raise HTTPException(status_code=500, detail=f"Failed to get APK status: {e!s}")


def get_library_router(auth_guard: AuthGuard = None):
    """Get the library management router."""
    global _auth_guard
    _auth_guard = auth_guard
    return router
