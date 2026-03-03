"""Sonic Plugin Routes (Modular)

NEW modular plugin-based routes replacing legacy screwdriver monolith.
Uses dynamic plugin loader from extensions/sonic_loader.py.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request

from core.services.unified_config_loader import get_bool_config
from extensions.sonic_loader import load_sonic_plugin
from wizard.services.sonic_adapters import (
    build_device_query,
    to_device_list_payload,
    to_device_payload,
    to_stats_payload,
    to_sync_status_payload,
)
from wizard.services.sonic_schema_contract import evaluate_sonic_schema_contract

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def _alias_notice(
    payload: dict[str, Any], *, alias: str, canonical: str
) -> dict[str, Any]:
    """Annotate alias responses with canonical route metadata."""
    return {
        **payload,
        "deprecated_alias": {
            "alias": alias,
            "canonical": canonical,
            "removal_target": "v1.5",
        },
    }


def _legacy_aliases_enabled() -> bool:
    return get_bool_config("UDOS_SONIC_ENABLE_LEGACY_ALIASES", False)


def _raise_alias_retired(*, alias: str, canonical: str) -> None:
    raise HTTPException(
        status_code=410,
        detail={
            "message": "Sonic legacy alias retired",
            "alias": alias,
            "canonical": canonical,
        },
    )


def create_sonic_plugin_routes(
    auth_guard: AuthGuard = None, repo_root: Path | None = None
) -> APIRouter:
    """Create Sonic plugin routes using modular system.

    This replaces the legacy screwdriver routes with dynamic plugin loading.

    Args:
        auth_guard: Optional authentication guard
        repo_root: Repository root (auto-detected if None)

    Returns:
        FastAPI router with Sonic endpoints
    """
    router = APIRouter(prefix="/api/sonic", tags=["sonic"])
    aliases_enabled = _legacy_aliases_enabled()

    # Load plugin components
    try:
        plugin = load_sonic_plugin(repo_root)
        api = plugin["api"].get_sonic_service()
        sync = plugin["sync"].get_sync_service()
    except Exception as exc:
        # Fallback: plugin not available
        @router.get("/health")
        async def health_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            return {
                "status": "error",
                "message": f"Sonic plugin not available: {exc}",
                "installed": False,
            }

        @router.get("/devices")
        async def devices_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.post("/rescan")
        async def rescan_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.post("/rebuild")
        async def rebuild_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.get("/export")
        async def export_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.post("/sync")
        async def sync_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.get("/sync/status")
        async def sync_status_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.post("/sync/rebuild")
        async def sync_rebuild_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.post("/sync/export")
        async def sync_export_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.get("/db/status")
        async def db_status_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.post("/db/rebuild")
        async def db_rebuild_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

        @router.get("/db/export")
        async def db_export_unavailable(request: Request):
            if auth_guard:
                await auth_guard(request)
            raise HTTPException(
                status_code=503, detail=f"Sonic plugin not available: {exc}"
            )

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

    @router.get("/schema/contract")
    async def get_schema_contract(request: Request):
        """Validate SQL/JSON/Python Sonic schema contract parity."""
        if auth_guard:
            await auth_guard(request)
        return evaluate_sonic_schema_contract(repo_root=repo_root)

    # Device query endpoint
    @router.get("/devices")
    async def list_devices(
        request: Request,
        vendor: str | None = Query(None),
        reflash_potential: str | None = Query(None),
        usb_boot: str | None = Query(None),
        uefi_native: str | None = Query(None),
        windows10_boot: str | None = Query(None),
        media_mode: str | None = Query(None),
        udos_launcher: str | None = Query(None),
        year_min: int | None = Query(None),
        year_max: int | None = Query(None),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
    ):
        """Query devices from catalog with filters.

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
        query = build_device_query(
            vendor=vendor,
            reflash_potential=reflash_potential,
            usb_boot=usb_boot,
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
            return to_device_list_payload(devices=devices, limit=limit, offset=offset)
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
            return to_device_payload(device)
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
            return to_stats_payload(stats)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))

    # Database sync endpoints
    async def _sync_status_handler(request: Request) -> dict[str, Any]:
        """Get database sync status."""
        if auth_guard:
            await auth_guard(request)

        status = sync.get_status()
        return to_sync_status_payload(status)

    @router.get("/sync/status")
    async def sync_status(request: Request):
        """Get database sync status."""
        return await _sync_status_handler(request)

    @router.get("/aliases/status")
    async def aliases_status(request: Request):
        """Report legacy alias compatibility mode for Sonic endpoints."""
        if auth_guard:
            await auth_guard(request)
        return {
            "legacy_aliases_enabled": aliases_enabled,
            "status": "compatibility_override" if aliases_enabled else "retired",
            "retired_in": "v1.5",
        }

    @router.get("/db/status")
    async def db_status(request: Request):
        """Alias for device database sync status."""
        if not aliases_enabled:
            _raise_alias_retired(
                alias="/api/sonic/db/status", canonical="/api/sonic/sync/status"
            )
        payload = await _sync_status_handler(request)
        return _alias_notice(
            payload, alias="/api/sonic/db/status", canonical="/api/sonic/sync/status"
        )

    async def _sync_rebuild_handler(request: Request, *, force: bool) -> dict[str, Any]:
        """Rebuild device database from SQL source."""
        if auth_guard:
            await auth_guard(request)

        result = sync.rebuild_database(force=force)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    @router.post("/sync/rebuild")
    async def sync_rebuild(request: Request, force: bool = Query(False)):
        """Rebuild device database from SQL source."""
        return await _sync_rebuild_handler(request, force=force)

    @router.post("/db/rebuild")
    async def db_rebuild(request: Request, force: bool = Query(False)):
        """Alias for rebuilding the device database."""
        if not aliases_enabled:
            _raise_alias_retired(
                alias="/api/sonic/db/rebuild", canonical="/api/sonic/sync/rebuild"
            )
        payload = await _sync_rebuild_handler(request, force=force)
        return _alias_notice(
            payload, alias="/api/sonic/db/rebuild", canonical="/api/sonic/sync/rebuild"
        )

    @router.post("/rescan")
    async def rescan(request: Request):
        """Alias for non-destructive sync/rebuild operation."""
        if not aliases_enabled:
            _raise_alias_retired(
                alias="/api/sonic/rescan",
                canonical="/api/sonic/sync/rebuild?force=false",
            )
        payload = await _sync_rebuild_handler(request, force=False)
        return _alias_notice(
            payload,
            alias="/api/sonic/rescan",
            canonical="/api/sonic/sync/rebuild?force=false",
        )

    @router.post("/rebuild")
    async def rebuild(request: Request):
        """Alias for full rebuild operation."""
        if not aliases_enabled:
            _raise_alias_retired(
                alias="/api/sonic/rebuild",
                canonical="/api/sonic/sync/rebuild?force=true",
            )
        payload = await _sync_rebuild_handler(request, force=True)
        return _alias_notice(
            payload,
            alias="/api/sonic/rebuild",
            canonical="/api/sonic/sync/rebuild?force=true",
        )

    @router.post("/sync")
    async def sync_alias(request: Request):
        """Alias for sync operation used by Wizard GUI entry points."""
        if not aliases_enabled:
            _raise_alias_retired(
                alias="/api/sonic/sync", canonical="/api/sonic/sync/rebuild?force=false"
            )
        payload = await _sync_rebuild_handler(request, force=False)
        return _alias_notice(
            payload,
            alias="/api/sonic/sync",
            canonical="/api/sonic/sync/rebuild?force=false",
        )

    async def _sync_export_handler(
        request: Request, output_path: str | None
    ) -> dict[str, Any]:
        """Export database to CSV."""
        if auth_guard:
            await auth_guard(request)

        result = sync.export_to_csv(
            output_path=Path(output_path) if output_path else None
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    @router.post("/sync/export")
    async def sync_export(request: Request, output_path: str | None = Query(None)):
        """Export database to CSV."""
        return await _sync_export_handler(request, output_path=output_path)

    @router.post("/bootstrap/current")
    async def bootstrap_current_machine(request: Request, overwrite: bool = Query(True)):
        """Register the current machine in the local Sonic user catalog."""
        if auth_guard:
            await auth_guard(request)
        result = sync.bootstrap_current_machine(overwrite=overwrite)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    @router.get("/db/export")
    async def db_export(request: Request, output_path: str | None = Query(None)):
        """Alias for exporting the device database to CSV."""
        if not aliases_enabled:
            _raise_alias_retired(
                alias="/api/sonic/db/export", canonical="/api/sonic/sync/export"
            )
        payload = await _sync_export_handler(request, output_path=output_path)
        return _alias_notice(
            payload, alias="/api/sonic/db/export", canonical="/api/sonic/sync/export"
        )

    @router.get("/export")
    async def export_alias(request: Request, output_path: str | None = Query(None)):
        """Alias for export operation."""
        if not aliases_enabled:
            _raise_alias_retired(
                alias="/api/sonic/export", canonical="/api/sonic/sync/export"
            )
        payload = await _sync_export_handler(request, output_path=output_path)
        return _alias_notice(
            payload, alias="/api/sonic/export", canonical="/api/sonic/sync/export"
        )

    # Flash pack endpoints
    @router.get("/flash-packs")
    async def list_flash_packs(request: Request):
        """List available flash packs."""
        if auth_guard:
            await auth_guard(request)

        packs = api.list_flash_packs()
        return {"count": len(packs), "packs": packs}

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


__all__ = ["create_sonic_plugin_routes"]
