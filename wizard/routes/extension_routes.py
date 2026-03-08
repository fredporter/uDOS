"""Extension detection routes for Wizard Server."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Request

from core.services.container_catalog_service import get_container_catalog_service
from core.services.external_repo_service import resolve_sonic_repo_root, sonic_repo_available
from wizard.services.extension_hot_reload_service import get_extension_hot_reload_service
from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.path_utils import get_repo_root

REPO_ROOT = get_repo_root()

ICON_MAP = {
    "business": "🏛",
    "developer": "🧌",
    "audio": "🎛",
    "utilities": "🔧",
    "ui": "🖥",
    "general": "📦",
}


def _official_extensions() -> list[dict[str, Any]]:
    catalog = get_container_catalog_service(REPO_ROOT)
    items: list[dict[str, Any]] = []
    for entry in catalog.list_by_kind("extension"):
        items.append(
            {
                "id": entry.entry_id,
                "name": entry.label,
                "description": entry.summary,
                "icon": ICON_MAP.get(entry.category, "📦"),
                "path": entry.path,
                "main_file": _watch_file_for_extension(entry.entry_id, entry.path),
                "api_prefix": entry.api_prefix,
                "web_port": None,
                "category": entry.category,
                "visibility": entry.visibility,
                "runtime_owner": entry.execution.runtime_owner,
                "callable_from": entry.execution.callable_from,
                "library_refs": entry.metadata.get("library_refs", []),
                "template_workspace": entry.metadata.get("template_workspace"),
                "standalone_capable": entry.execution.standalone_capable,
                "present": entry.available,
                "lens_vars": entry.lens_vars,
                "version": entry.version,
            }
        )
    return items


def _watch_file_for_extension(entry_id: str, path: str) -> str:
    normalized = entry_id.strip().lower()
    if normalized == "sonic":
        return "README.md"
    if normalized == "thin-gui":
        return "package.json"
    if path == "dev":
        return "__init__.py"
    return "__init__.py"


def _get_extension_status(ext: Dict[str, Any]) -> Dict[str, Any]:
    """Get full status for an extension."""
    if ext["id"] == "empire":
        payload = get_empire_extension_service().status_payload()
        return {
            "id": "empire",
            "name": ext["name"],
            "description": ext["description"],
            "icon": ext["icon"],
            "category": ext["category"],
            "present": payload["installed"],
            "installed": payload["installed"],
            "available": payload["available"],
            "enabled": payload["enabled"],
            "activation_state": payload["activation_state"],
            "activation_required": payload["activation_required"],
            "configured": payload["configured"],
            "configuration_state": payload["configuration_state"],
            "healthy": payload["healthy"],
            "degraded": payload["degraded"],
            "access_error": payload["access_error"],
            "version": payload["version"],
            "path": payload["path"],
            "wizard_route": payload["wizard_route"],
            "capabilities": payload["capabilities"],
            "missing_prerequisites": payload["missing_prerequisites"],
            "api_prefix": ext["api_prefix"],
            "web_port": ext["web_port"],
            "visibility": ext.get("visibility", "official"),
            "runtime_owner": ext.get("runtime_owner", "wizard"),
            "callable_from": ext.get("callable_from", []),
            "library_refs": ext.get("library_refs", []),
            "template_workspace": ext.get("template_workspace"),
            "standalone_capable": ext.get("standalone_capable", False),
            "lens_vars": ext.get("lens_vars", {}),
        }
    if ext["id"] == "sonic":
        sonic_root = resolve_sonic_repo_root(REPO_ROOT)
        present = sonic_repo_available(REPO_ROOT)
        return {
            "id": "sonic",
            "name": ext["name"],
            "description": ext["description"],
            "icon": ext["icon"],
            "category": ext["category"],
            "present": present,
            "installed": present,
            "available": present,
            "enabled": present,
            "configured": present,
            "configuration_state": "configured" if present else "missing",
            "healthy": present,
            "degraded": False,
            "api_prefix": ext["api_prefix"],
            "web_port": ext["web_port"],
            "visibility": ext.get("visibility", "official"),
            "runtime_owner": ext.get("runtime_owner", "shared"),
            "callable_from": ext.get("callable_from", []),
            "library_refs": ext.get("library_refs", []),
            "template_workspace": ext.get("template_workspace"),
            "standalone_capable": True,
            "lens_vars": ext.get("lens_vars", {}),
            "path": str(sonic_root),
            "version": ext.get("version") or "external",
        }
    present = bool(ext.get("present"))

    result = {
        "id": ext["id"],
        "name": ext["name"],
        "description": ext["description"],
        "icon": ext["icon"],
        "category": ext["category"],
        "present": present,
        "installed": present,
        "available": present,
        "enabled": present,
        "configured": present,
        "configuration_state": "configured" if present else "missing",
        "healthy": present,
        "degraded": False,
        "api_prefix": ext["api_prefix"],
        "web_port": ext["web_port"],
        "visibility": ext.get("visibility", "official"),
        "runtime_owner": ext.get("runtime_owner", "shared"),
        "callable_from": ext.get("callable_from", []),
        "library_refs": ext.get("library_refs", []),
        "template_workspace": ext.get("template_workspace"),
        "standalone_capable": ext.get("standalone_capable", False),
        "lens_vars": ext.get("lens_vars", {}),
    }

    if present:
        result["version"] = ext.get("version") or "dev"

    return result


router = APIRouter(prefix="/api/extensions", tags=["extensions"])


@router.get("/list")
async def list_extensions(request: Request, visibility: Optional[str] = None) -> Dict[str, Any]:
    """List all official extensions and their availability."""
    extensions = []
    for ext in _official_extensions():
        ext_status = _get_extension_status(ext)
        if visibility and ext_status["visibility"] != visibility:
            continue
        extensions.append(ext_status)

    present_count = sum(1 for e in extensions if e["present"])

    return {
        "extensions": extensions,
        "summary": {
            "total": len(extensions),
            "present": present_count,
            "missing": len(extensions) - present_count,
        },
    }


@router.get("/status/{extension_id}")
async def extension_status(extension_id: str, request: Request) -> Dict[str, Any]:
    """Get detailed status for a specific extension."""
    for ext in _official_extensions():
        if ext["id"] == extension_id:
            return _get_extension_status(ext)

    return {"error": f"Unknown extension: {extension_id}", "present": False}


@router.get("/empire/token-status")
async def empire_token_status(request: Request) -> Dict[str, Any]:
    """Check if Empire token/config state is configured."""
    payload = get_empire_extension_service().status_payload()
    return {
        "present": payload["installed"],
        "enabled": payload["enabled"],
        "activation_state": payload["activation_state"],
        "activation_required": payload["activation_required"],
        "configured": payload["configured"],
        "configuration_state": payload["configuration_state"],
        "token_configured": payload["configuration_state"] == "configured",
        "healthy": payload["healthy"],
        "access_error": payload["access_error"],
    }


@router.post("/hot-reload")
async def hot_reload_extensions(request: Request) -> Dict[str, Any]:
    """Run extension hot-reload scan and emit changed extension ids."""
    svc = get_extension_hot_reload_service(repo_root=REPO_ROOT)
    result = svc.hot_reload(_official_extensions())
    return {"success": True, **result}


@router.get("/hot-reload/status")
async def hot_reload_status(request: Request, limit: int = 20) -> Dict[str, Any]:
    """Get extension hot-reload status and recent history."""
    svc = get_extension_hot_reload_service(repo_root=REPO_ROOT)
    return {"success": True, **svc.get_status(limit=limit)}
