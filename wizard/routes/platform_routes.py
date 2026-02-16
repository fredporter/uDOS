"""Platform integration routes for Wizard GUI.

Exposes unified status for Sonic, Groovebox, and GUI theme/CSS extensions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from wizard.services.sonic_bridge_service import get_sonic_bridge_service
from wizard.services.sonic_build_service import get_sonic_build_service
from wizard.services.sonic_boot_profile_service import get_sonic_boot_profile_service
from wizard.services.sonic_device_profile_service import get_sonic_device_profile_service
from wizard.services.sonic_media_console_service import get_sonic_media_console_service
from wizard.services.sonic_plugin_service import get_sonic_service
from wizard.services.sonic_windows_launcher_service import get_sonic_windows_launcher_service
from wizard.services.theme_extension_service import get_theme_extension_service

AuthGuard = Optional[Callable]


class SonicBuildRequest(BaseModel):
    profile: str = "alpine-core+sonic"
    build_id: Optional[str] = None
    source_image: Optional[str] = None
    output_dir: Optional[str] = None


class SonicGUIActionRequest(BaseModel):
    force: bool = False
    output_path: Optional[str] = None
    profile: str = "alpine-core+sonic"
    build_id: Optional[str] = None
    source_image: Optional[str] = None
    output_dir: Optional[str] = None


class SonicBootRouteRequest(BaseModel):
    profile_id: str
    reason: Optional[str] = None


class SonicWindowsModeRequest(BaseModel):
    mode: str
    launcher: Optional[str] = None
    auto_repair: Optional[bool] = None


class SonicMediaStartRequest(BaseModel):
    launcher: str


def create_platform_routes(auth_guard: AuthGuard = None, repo_root: Optional[Path] = None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/platform", tags=["platform"], dependencies=dependencies)

    sonic = get_sonic_bridge_service(repo_root=repo_root)
    sonic_builds = get_sonic_build_service(repo_root=repo_root)
    sonic_boot = get_sonic_boot_profile_service(repo_root=repo_root)
    sonic_device_profile = get_sonic_device_profile_service(repo_root=repo_root)
    sonic_media = get_sonic_media_console_service(repo_root=repo_root)
    sonic_ops = get_sonic_service(repo_root=repo_root)
    sonic_windows = get_sonic_windows_launcher_service(repo_root=repo_root)
    themes = get_theme_extension_service(repo_root=repo_root)

    @router.get("/sonic/status")
    async def sonic_status():
        return sonic.get_status()

    @router.get("/sonic/artifacts")
    async def sonic_artifacts(limit: int = Query(200, ge=1, le=1000)):
        return sonic.list_artifacts(limit=limit)

    @router.post("/sonic/build")
    async def sonic_build(payload: SonicBuildRequest):
        try:
            return sonic_builds.start_build(
                profile=payload.profile,
                build_id=payload.build_id,
                source_image=payload.source_image,
                output_dir=payload.output_dir,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Sonic build failed: {exc}")

    @router.get("/sonic/builds")
    async def list_sonic_builds(limit: int = Query(50, ge=1, le=500)):
        return sonic_builds.list_builds(limit=limit)

    @router.get("/sonic/builds/{id}")
    async def get_sonic_build(id: str):
        try:
            return sonic_builds.get_build(id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/sonic/builds/{id}/artifacts")
    async def get_sonic_build_artifacts(id: str):
        try:
            return sonic_builds.get_build_artifacts(id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/sonic/builds/{id}/release-readiness")
    async def get_sonic_release_readiness(id: str):
        try:
            return sonic_builds.get_release_readiness(id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/sonic/gui/summary")
    async def sonic_gui_summary():
        status = sonic.get_status()
        builds = sonic_builds.list_builds(limit=5)
        latest_build = builds["builds"][0] if builds.get("builds") else None
        latest_build_id = latest_build.get("build_id") if latest_build else None

        release_readiness = None
        if latest_build_id:
            try:
                release_readiness = sonic_builds.get_release_readiness(latest_build_id)
            except FileNotFoundError:
                release_readiness = None

        sync_status = None
        if getattr(sonic_ops, "available", False):
            try:
                sync = sonic_ops.sync.get_status()
                sync_status = {
                    "db_exists": sync.db_exists,
                    "record_count": sync.record_count,
                    "needs_rebuild": sync.needs_rebuild,
                    "last_sync": sync.last_sync,
                }
            except Exception:
                sync_status = None

        return {
            "sonic": status,
            "dashboard": {"route": "#sonic", "wizard_gui_hosted": True},
            "latest_build": latest_build,
            "latest_release_readiness": release_readiness,
            "device_recommendations": sonic_device_profile.get_recommendations(),
            "media_console": sonic_media.get_status(),
            "sync_status": sync_status,
            "actions": {
                "sync": "/api/platform/sonic/gui/actions/sync",
                "rebuild": "/api/platform/sonic/gui/actions/rebuild",
                "export": "/api/platform/sonic/gui/actions/export",
                "build": "/api/platform/sonic/gui/actions/build",
            },
        }

    @router.get("/sonic/boot/profiles")
    async def sonic_boot_profiles():
        return sonic_boot.list_profiles()

    @router.get("/sonic/boot/route")
    async def sonic_boot_route_status():
        return sonic_boot.get_route_status()

    @router.post("/sonic/boot/route")
    async def sonic_boot_route(payload: SonicBootRouteRequest):
        try:
            route = sonic_boot.set_reboot_route(profile_id=payload.profile_id, reason=payload.reason)
            return {"success": True, "route": route}
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/sonic/windows/launcher")
    async def sonic_windows_launcher_status():
        return sonic_windows.get_status()

    @router.post("/sonic/windows/launcher/mode")
    async def sonic_windows_launcher_mode(payload: SonicWindowsModeRequest):
        try:
            state = sonic_windows.set_mode(
                mode=payload.mode,
                launcher=payload.launcher,
                auto_repair=payload.auto_repair,
            )
            return {"success": True, "state": state}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/sonic/device/recommendations")
    async def sonic_device_recommendations():
        return sonic_device_profile.get_recommendations()

    @router.get("/sonic/media/launchers")
    async def sonic_media_launchers():
        return sonic_media.list_launchers()

    @router.get("/sonic/media/status")
    async def sonic_media_status():
        return sonic_media.get_status()

    @router.post("/sonic/media/start")
    async def sonic_media_start(payload: SonicMediaStartRequest):
        try:
            state = sonic_media.start(payload.launcher)
            return {"success": True, "state": state}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.post("/sonic/media/stop")
    async def sonic_media_stop():
        return {"success": True, "state": sonic_media.stop()}

    @router.post("/sonic/gui/actions/sync")
    async def sonic_gui_action_sync(payload: SonicGUIActionRequest):
        if not getattr(sonic_ops, "available", False):
            raise HTTPException(status_code=503, detail="Sonic plugin not available")
        result = sonic_ops.sync.rebuild_database(force=False)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "sync failed"))
        return {"success": True, "action": "sync", "result": result}

    @router.post("/sonic/gui/actions/rebuild")
    async def sonic_gui_action_rebuild(payload: SonicGUIActionRequest):
        if not getattr(sonic_ops, "available", False):
            raise HTTPException(status_code=503, detail="Sonic plugin not available")
        result = sonic_ops.sync.rebuild_database(force=payload.force or True)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "rebuild failed"))
        return {"success": True, "action": "rebuild", "result": result}

    @router.post("/sonic/gui/actions/export")
    async def sonic_gui_action_export(payload: SonicGUIActionRequest):
        if not getattr(sonic_ops, "available", False):
            raise HTTPException(status_code=503, detail="Sonic plugin not available")
        out = Path(payload.output_path) if payload.output_path else None
        result = sonic_ops.sync.export_to_csv(output_path=out)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "export failed"))
        return {"success": True, "action": "export", "result": result}

    @router.post("/sonic/gui/actions/build")
    async def sonic_gui_action_build(payload: SonicGUIActionRequest):
        try:
            result = sonic_builds.start_build(
                profile=payload.profile,
                build_id=payload.build_id,
                source_image=payload.source_image,
                output_dir=payload.output_dir,
            )
            return {"success": True, "action": "build", "result": result}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Sonic build failed: {exc}")

    @router.get("/groovebox/status")
    async def groovebox_status():
        root = (repo_root or Path(__file__).resolve().parent.parent.parent) / "groovebox"
        available = root.exists()
        return {
            "available": available,
            "root": str(root),
            "wizard_gui_hosted": True,
            "api_prefix": "/api/groovebox",
            "dashboard_route": "#groovebox",
        }

    @router.get("/themes/css-extensions")
    async def theme_css_extensions():
        return themes.list_css_extensions()

    @router.get("/dev/scaffold")
    async def dev_scaffold_status():
        root = (repo_root or Path(__file__).resolve().parent.parent.parent) / "dev" / "goblin"
        if not root.exists():
            raise HTTPException(status_code=404, detail="/dev/goblin scaffold not found")
        required = {
            "scripts": (root / "scripts").exists(),
            "tests": (root / "tests").exists(),
            "wizard_sandbox": (root / "wizard-sandbox").exists(),
        }
        return {
            "root": str(root),
            "required": required,
            "ready": all(required.values()),
        }

    return router
