"""
Library Management API Routes

Provides REST endpoints for managing library integrations and plugins.
Migrated from Goblin to Wizard for centralized management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pathlib import Path

from wizard.services.library_manager_service import get_library_manager, InstallResult
from wizard.services.system_info_service import LibraryStatus, LibraryIntegration


router = APIRouter(prefix="/api/v1/library", tags=["library"])


@router.get("/status", response_model=Dict[str, Any])
async def get_library_status():
    """
    Get comprehensive library status.

    Returns:
        LibraryStatus with all integrations and their states
    """
    try:
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
async def get_integration(name: str):
    """
    Get specific integration details.

    Args:
        name: Integration name

    Returns:
        Integration details or 404 if not found
    """
    try:
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
async def install_integration(name: str, background_tasks: BackgroundTasks):
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

        if integration.installed:
            return {
                "success": True,
                "result": {
                    "success": True,
                    "plugin_name": name,
                    "action": "install",
                    "message": "Already installed",
                },
            }

        # Perform installation
        result = manager.install_integration(name)

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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to install integration: {str(e)}"
        )


@router.post("/integration/{name}/enable", response_model=Dict[str, Any])
async def enable_integration(name: str):
    """
    Enable an installed integration.

    Adds to plugins.enabled config file.

    Args:
        name: Integration name to enable

    Returns:
        Enable result
    """
    try:
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
async def disable_integration(name: str):
    """
    Disable an integration.

    Removes from plugins.enabled config file.

    Args:
        name: Integration name to disable

    Returns:
        Disable result
    """
    try:
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
async def uninstall_integration(name: str, background_tasks: BackgroundTasks):
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
async def get_enabled_integrations():
    """
    Get list of enabled integrations.

    Returns:
        List of enabled integration names
    """
    try:
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
async def get_available_integrations():
    """
    Get list of integrations available for installation.

    Returns:
        List of integrations that can be installed
    """
    try:
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
async def refresh_library_status():
    """
    Refresh library status by rescanning directories.

    Returns:
        Updated library status
    """
    try:
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
async def get_library_stats():
    """
    Get library statistics summary.

    Returns:
        High-level stats for dashboard display
    """
    try:
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
def get_library_router():
    """Get the library management router."""
    return router
