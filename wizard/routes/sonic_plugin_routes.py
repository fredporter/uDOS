"""
Sonic Plugin Routes (Modular)

NEW modular plugin-based routes replacing legacy screwdriver monolith.
Uses dynamic plugin loader from extensions/sonic_loader.py.
"""

from pathlib import Path
from typing import Callable, Awaitable, Optional, List, Dict, Any
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel

from extensions.sonic_loader import load_sonic_plugin

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_sonic_plugin_routes(auth_guard: AuthGuard = None, repo_root: Optional[Path] = None) -> APIRouter:
    """
    Create Sonic plugin routes using modular system.

    This replaces the legacy screwdriver routes with dynamic plugin loading.

    Args:
        auth_guard: Optional authentication guard
        repo_root: Repository root (auto-detected if None)

    Returns:
        FastAPI router with Sonic endpoints
    """
    router = APIRouter(prefix="/api/sonic", tags=["sonic"])

    # Load plugin components
    try:
        plugin = load_sonic_plugin(repo_root)
        api = plugin['api'].get_sonic_service()
        sync = plugin['sync'].get_sync_service()
        schemas = plugin['schemas']
    except Exception as e:
        # Fallback: plugin not available
        @router.get("/health")
        async def health_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            return {
                "status": "error",
                "message": f"Sonic plugin not available: {e}",
                "installed": False,
            }

        @router.get("/devices")
        async def devices_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(status_code=503, detail=f"Sonic plugin not available: {e}")

        @router.post("/rescan")
        async def rescan_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(status_code=503, detail=f"Sonic plugin not available: {e}")

        @router.post("/rebuild")
        async def rebuild_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(status_code=503, detail=f"Sonic plugin not available: {e}")

        @router.get("/export")
        async def export_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(status_code=503, detail=f"Sonic plugin not available: {e}")

        @router.post("/sync")
        async def sync_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(status_code=503, detail=f"Sonic plugin not available: {e}")

        @router.get("/db/status")
        async def db_status_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(status_code=503, detail=f"Sonic plugin not available: {e}")

        @router.post("/db/rebuild")
        async def db_rebuild_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(status_code=503, detail=f"Sonic plugin not available: {e}")

        @router.get("/db/export")
        async def db_export_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(status_code=503, detail=f"Sonic plugin not available: {e}")
        return router

    # Health endpoint
    @router.get("/health")
    async def sonic_health(request: Request):
        """Check Sonic plugin health and availability."""
        if auth_guard:
            await auth_guard(request)

        return api.health()

    # Schema endpoint
    @router.get("/schema")
    async def get_schema(request: Request):
        """Get JSON Schema for device records."""
        if auth_guard:
            await auth_guard(request)

        try:
            return api.get_schema()
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # Device query endpoint
    @router.get("/devices")
    async def list_devices(
        request: Request,
        vendor: Optional[str] = Query(None),
        reflash_potential: Optional[str] = Query(None),
        usb_boot: Optional[str] = Query(None),
        uefi_native: Optional[str] = Query(None),
        windows10_boot: Optional[str] = Query(None),
        media_mode: Optional[str] = Query(None),
        udos_launcher: Optional[str] = Query(None),
        year_min: Optional[int] = Query(None),
        year_max: Optional[int] = Query(None),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
    ):
        """
        Query devices from catalog with filters.

        Filters:
        - vendor: Vendor name substring
        - reflash_potential: high, medium, low, unknown
        - usb_boot: native, uefi_only, legacy_only, mixed, none
        - uefi_native: works, issues, unknown
        - windows10_boot: none, install, wtg, unknown
        - media_mode: none, htpc, retro, unknown
        - udos_launcher: none, basic, advanced, unknown
        - year_min/year_max: Year range
        """
        if auth_guard:
            await auth_guard(request)

        # Build query
        from library.sonic.schemas import ReflashPotential, USBBootSupport

        query = schemas.DeviceQuery(
            vendor=vendor,
            reflash_potential=ReflashPotential(reflash_potential) if reflash_potential else None,
            usb_boot=USBBootSupport(usb_boot) if usb_boot else None,
            uefi_native=uefi_native,
            windows10_boot=windows10_boot,
            media_mode=media_mode,
            udos_launcher=udos_launcher,
            year_min=year_min,
            year_max=year_max,
            limit=limit,
            offset=offset,
        )

        try:
            devices = api.query_devices(query)
            return {
                "total": len(devices),
                "limit": limit,
                "offset": offset,
                "devices": [d.to_dict() for d in devices],
            }
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))

    # Device detail endpoint
    @router.get("/devices/{device_id}")
    async def get_device(request: Request, device_id: str):
        """Get device details by ID."""
        if auth_guard:
            await auth_guard(request)

        try:
            device = api.get_device(device_id)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            return device.to_dict()
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))

    # Stats endpoint
    @router.get("/stats")
    async def get_stats(request: Request):
        """Get device catalog statistics."""
        if auth_guard:
            await auth_guard(request)

        try:
            stats = api.get_stats()
            return {
                "total_devices": stats.total_devices,
                "by_vendor": stats.by_vendor,
                "by_reflash_potential": stats.by_reflash_potential,
                "by_windows10_boot": stats.by_windows10_boot,
                "by_media_mode": stats.by_media_mode,
                "usb_boot_capable": stats.usb_boot_capable,
                "uefi_native_capable": stats.uefi_native_capable,
                "last_updated": stats.last_updated,
            }
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))

    # Database sync endpoints
    @router.get("/sync/status")
    async def sync_status(request: Request):
        """Get database sync status."""
        if auth_guard:
            await auth_guard(request)

        status = sync.get_status()
        return {
            "last_sync": status.last_sync,
            "db_path": status.db_path,
            "db_exists": status.db_exists,
            "record_count": status.record_count,
            "schema_version": status.schema_version,
            "needs_rebuild": status.needs_rebuild,
            "errors": status.errors,
        }

    @router.get("/db/status")
    async def db_status(request: Request):
        """Alias for device database sync status."""
        if auth_guard:
            await auth_guard(request)
        status = sync.get_status()
        return {
            "last_sync": status.last_sync,
            "db_path": status.db_path,
            "db_exists": status.db_exists,
            "record_count": status.record_count,
            "schema_version": status.schema_version,
            "needs_rebuild": status.needs_rebuild,
            "errors": status.errors,
        }

    @router.post("/sync/rebuild")
    async def sync_rebuild(request: Request, force: bool = Query(False)):
        """Rebuild device database from SQL source."""
        if auth_guard:
            await auth_guard(request)

        result = sync.rebuild_database(force=force)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    @router.post("/db/rebuild")
    async def db_rebuild(request: Request, force: bool = Query(False)):
        """Alias for rebuilding the device database."""
        if auth_guard:
            await auth_guard(request)
        result = sync.rebuild_database(force=force)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    @router.post("/rescan")
    async def rescan(request: Request):
        """Alias for non-destructive sync/rebuild operation."""
        if auth_guard:
            await auth_guard(request)
        result = sync.rebuild_database(force=False)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    @router.post("/rebuild")
    async def rebuild(request: Request):
        """Alias for full rebuild operation."""
        if auth_guard:
            await auth_guard(request)
        result = sync.rebuild_database(force=True)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    @router.post("/sync")
    async def sync_alias(request: Request):
        """Alias for sync operation used by Wizard GUI entry points."""
        if auth_guard:
            await auth_guard(request)
        result = sync.rebuild_database(force=False)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    @router.post("/sync/export")
    async def sync_export(request: Request, output_path: Optional[str] = Query(None)):
        """Export database to CSV."""
        if auth_guard:
            await auth_guard(request)

        result = sync.export_to_csv(
            output_path=Path(output_path) if output_path else None
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    @router.get("/db/export")
    async def db_export(request: Request, output_path: Optional[str] = Query(None)):
        """Alias for exporting the device database to CSV."""
        if auth_guard:
            await auth_guard(request)
        result = sync.export_to_csv(
            output_path=Path(output_path) if output_path else None
        )
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    @router.get("/export")
    async def export_alias(request: Request, output_path: Optional[str] = Query(None)):
        """Alias for export operation."""
        if auth_guard:
            await auth_guard(request)
        result = sync.export_to_csv(output_path=Path(output_path) if output_path else None)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    # Flash pack endpoints
    @router.get("/flash-packs")
    async def list_flash_packs(request: Request):
        """List available flash packs."""
        if auth_guard:
            await auth_guard(request)

        packs = api.list_flash_packs()
        return {
            "count": len(packs),
            "packs": packs,
        }

    @router.get("/flash-packs/{pack_id}")
    async def get_flash_pack(request: Request, pack_id: str):
        """Get flash pack by ID."""
        if auth_guard:
            await auth_guard(request)

        try:
            pack = api.get_flash_pack(pack_id)
            if not pack:
                raise HTTPException(status_code=404, detail="Flash pack not found")

            return {
                "pack_id": pack.pack_id,
                "name": pack.name,
                "version": pack.version,
                "description": pack.description,
                "created_at": pack.created_at,
                "target": pack.target,
                "metadata": pack.metadata,
            }
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router

__all__ = [
    "create_sonic_plugin_routes",
]
