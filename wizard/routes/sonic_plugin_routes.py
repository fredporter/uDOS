"""Sonic Plugin Routes (Modular)

NEW modular plugin-based routes replacing legacy screwdriver monolith.
Uses dynamic plugin loader from extensions/sonic_loader.py.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from core.services.sonic_device_service import get_sonic_device_service
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


class SonicSubmissionCreateRequest(BaseModel):
    device: dict[str, Any]
    submitter: str | None = None


class SonicSubmissionReviewRequest(BaseModel):
    actor: str | None = None
    reason: str | None = None


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

    # Load plugin components
    try:
        plugin = load_sonic_plugin(repo_root)
        api = plugin["api"].get_sonic_service()
        sync = plugin["sync"].get_sync_service()
        submissions = get_sonic_device_service(repo_root=repo_root)
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

    @router.get("/submissions")
    async def list_submissions(request: Request, status: str | None = Query(None)):
        """List Sonic device submissions by review state."""
        if auth_guard:
            await auth_guard(request)
        records = submissions.list_submissions(status=status)
        return {
            "count": len(records),
            "status_filter": status,
            "submissions": records,
            "runtime_contract": submissions.submission_runtime_contract(),
        }

    @router.post("/submissions")
    async def create_submission(request: Request, payload: SonicSubmissionCreateRequest):
        """Queue a local Sonic device submission for contributor review."""
        if auth_guard:
            await auth_guard(request)
        try:
            result = submissions.submit_device_submission(
                payload.device, submitter=payload.submitter
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result

    @router.post("/submissions/{submission_id}/approve")
    async def approve_submission(
        request: Request, submission_id: str, payload: SonicSubmissionReviewRequest
    ):
        """Approve a pending submission into the local Sonic user catalog."""
        if auth_guard:
            await auth_guard(request)
        result = submissions.approve_submission(
            submission_id, approved_by=payload.actor
        )
        if result["status"] != "ok":
            raise HTTPException(status_code=404, detail=result["message"])
        return result

    @router.post("/submissions/{submission_id}/reject")
    async def reject_submission(
        request: Request, submission_id: str, payload: SonicSubmissionReviewRequest
    ):
        """Reject a pending Sonic submission."""
        if auth_guard:
            await auth_guard(request)
        result = submissions.reject_submission(
            submission_id, rejected_by=payload.actor, reason=payload.reason
        )
        if result["status"] != "ok":
            raise HTTPException(status_code=404, detail=result["message"])
        return result

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
