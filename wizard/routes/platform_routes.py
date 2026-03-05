"""Platform integration routes for Wizard GUI.

Exposes unified status for Sonic, Groovebox, and GUI theme/CSS extensions.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sonic.core.verify import verify_sonic_ready

from core.services.template_workspace_service import get_template_workspace_service
from wizard.services.launch_adapters import LaunchAdapterExecution
from wizard.services.launch_orchestrator import LaunchIntent, get_launch_orchestrator
from wizard.services.launch_session_service import get_launch_session_service
from wizard.services.dev_extension_service import get_dev_extension_service
from wizard.services.sonic_adapters import to_sync_status_payload
from wizard.services.sonic_bridge_service import get_sonic_bridge_service
from wizard.services.sonic_build_service import get_sonic_build_service
from wizard.services.sonic_boot_profile_service import get_sonic_boot_profile_service
from wizard.services.sonic_device_profile_service import get_sonic_device_profile_service
from wizard.services.sonic_linux_launcher_service import get_sonic_linux_launcher_service
from wizard.services.sonic_media_console_service import get_sonic_media_console_service
from wizard.services.sonic_plugin_service import get_sonic_service
from wizard.services.sonic_windows_gaming_profile_service import (
    get_sonic_windows_gaming_profile_service,
)
from wizard.services.sonic_windows_launcher_service import get_sonic_windows_launcher_service
from wizard.services.theme_extension_service import get_theme_extension_service
from wizard.services.uhome_presentation_service import get_uhome_presentation_service

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


class UHomePresentationStartRequest(BaseModel):
    presentation: str = ""


class SonicLinuxLauncherActionRequest(BaseModel):
    action: str
    workspace: Optional[str] = None
    protocol: str = "openrc"
    execute: bool = False


class SonicGamingProfileRequest(BaseModel):
    profile_id: str
    extra: dict = Field(default_factory=dict)


class GenericLaunchRequest(BaseModel):
    target: str
    mode: str
    launcher: Optional[str] = None
    workspace: Optional[str] = None
    profile_id: Optional[str] = None
    auth: dict = Field(default_factory=dict)
    portal_class: Optional[str] = None
    library_kind: Optional[str] = None


class _GenericLaunchAdapter:
    def __init__(self, payload: GenericLaunchRequest):
        self.payload = payload

    def starting_state(self, intent: LaunchIntent) -> str:
        return "starting"

    def execute(self, intent: LaunchIntent) -> LaunchAdapterExecution:
        return LaunchAdapterExecution(
            final_state="ready",
            state_payload={
                "target": intent.target,
                "mode": intent.mode,
                "launcher": intent.launcher,
                "workspace": intent.workspace,
                "profile_id": intent.profile_id,
                "portal_class": self.payload.portal_class,
                "library_kind": self.payload.library_kind,
                "auth": dict(intent.auth),
                "updated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            },
        )


def _build_release_signing_alert(release_readiness: Optional[dict]) -> Optional[dict]:
    if not release_readiness:
        return None

    signing = release_readiness.get("signing") or {}
    if signing.get("ready"):
        return None

    manifest = signing.get("manifest") or {}
    checksums = signing.get("checksums") or {}
    details = [str(item).strip() for item in {manifest.get("detail"), checksums.get("detail")} if str(item).strip()]
    issue_text = " ".join(str(item) for item in release_readiness.get("issues") or [])
    combined = " ".join(details + [issue_text]).lower()
    manifest_present = signing.get("manifest_signature_present")
    checksums_present = signing.get("checksums_signature_present")
    if manifest_present is False or checksums_present is False:
        return {
            "severity": "error",
            "code": "sonic_signing_signature_missing",
            "title": "Sonic release signatures are missing",
            "detail": details[0] if details else "Release bundle signatures are missing from the latest build.",
            "action": "Generate detached signatures for build-manifest.json and checksums.txt, then verify again.",
        }

    if "public key not found" in combined or "not configured" in combined:
        return {
            "severity": "error",
            "code": "sonic_signing_pubkey_missing",
            "title": "Sonic release signing key is not configured",
            "detail": details[0] if details else "Configure WIZARD_SONIC_SIGN_PUBKEY so Wizard can verify Sonic release signatures.",
            "action": "Set WIZARD_SONIC_SIGN_PUBKEY to the release verification public key and rebuild the readiness view.",
        }

    if "signature missing" in combined:
        return {
            "severity": "error",
            "code": "sonic_signing_signature_missing",
            "title": "Sonic release signatures are missing",
            "detail": details[0] if details else "Release bundle signatures are missing from the latest build.",
            "action": "Generate detached signatures for build-manifest.json and checksums.txt, then verify again.",
        }

    if not release_readiness.get("release_ready"):
        return {
            "severity": "warning",
            "code": "sonic_signing_unverified",
            "title": "Sonic release bundle is present but not verified",
            "detail": details[0] if details else "Signing checks did not complete successfully for the latest Sonic build.",
            "action": "Review the release-readiness issues and correct signing or checksum failures before distribution.",
        }

    return None


def _extract_dataset_contract_summary(verification: dict) -> dict:
    media_policy = verification.get("media_policy") or {}
    device_policy = next(
        (item for item in media_policy.get("policies") or [] if item.get("policy_id") == "device-database"),
        None,
    )
    contract = (device_policy or {}).get("contract") or {}
    version = contract.get("version") or {}
    return {
        "available": device_policy is not None,
        "ok": bool(contract.get("ok")) if device_policy else False,
        "level": (device_policy or {}).get("level"),
        "detail": (device_policy or {}).get("detail"),
        "version": version.get("version"),
        "schema_version": version.get("schema_version"),
        "updated": version.get("updated"),
        "errors": contract.get("errors") or [],
        "warnings": contract.get("warnings") or [],
        "seed_rows": ((contract.get("sql") or {}).get("seed_rows") or []),
        "diff": contract.get("diff") or {},
    }


def create_platform_routes(auth_guard: AuthGuard = None, repo_root: Optional[Path] = None) -> APIRouter:
    resolved_repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/platform", tags=["platform"], dependencies=dependencies)

    sonic = get_sonic_bridge_service(repo_root=repo_root)
    sonic_builds = get_sonic_build_service(repo_root=repo_root)
    sonic_boot = get_sonic_boot_profile_service(repo_root=repo_root)
    sonic_device_profile = get_sonic_device_profile_service(repo_root=repo_root)
    sonic_media = get_sonic_media_console_service(repo_root=repo_root)
    sonic_ops = get_sonic_service(repo_root=repo_root)
    sonic_linux = get_sonic_linux_launcher_service(repo_root=repo_root)
    sonic_gaming = get_sonic_windows_gaming_profile_service(repo_root=repo_root)
    sonic_windows = get_sonic_windows_launcher_service(repo_root=repo_root)
    themes = get_theme_extension_service(repo_root=repo_root)
    uhome_presentation = get_uhome_presentation_service(repo_root=repo_root)
    launch_sessions = get_launch_session_service(repo_root=repo_root)
    launch_orchestrator = get_launch_orchestrator(repo_root=repo_root)

    @router.post("/launch")
    async def launch_generic_surface(payload: GenericLaunchRequest):
        intent = LaunchIntent(
            target=payload.target,
            mode=payload.mode,
            launcher=payload.launcher,
            workspace=payload.workspace,
            profile_id=payload.profile_id,
            auth=payload.auth,
        )
        adapter = _GenericLaunchAdapter(payload)
        return {"success": True, **launch_orchestrator.execute(intent, adapter)}

    @router.get("/sonic/status")
    async def sonic_status():
        workspace = get_template_workspace_service(resolved_repo_root)
        default_profile = getattr(sonic_builds, "default_profile", "alpine-core+sonic")
        return {
            **sonic.get_status(),
            "default_build_profile": default_profile,
            "default_build_profile_source": getattr(
                sonic_builds, "default_profile_source", "packaging_manifest"
            ),
            "template_workspace": workspace.component_contract("sonic"),
            "template_workspace_state": workspace.component_snapshot("sonic"),
        }

    @router.get("/sonic/artifacts")
    async def sonic_artifacts(limit: int = Query(200, ge=1, le=1000)):
        return sonic.list_artifacts(limit=limit)

    @router.get("/sonic/verify")
    async def sonic_verify(
        manifest: str = Query("config/sonic-manifest.json"),
        build_id: Optional[str] = Query(None),
        build_dir: Optional[str] = Query(None),
        flash_pack: Optional[str] = Query(None),
    ):
        sonic_root = resolved_repo_root / "sonic"
        manifest_path = Path(manifest)
        if not manifest_path.is_absolute():
            manifest_path = sonic_root / manifest_path
        resolved_build_dir = None
        if build_dir:
            resolved_build_dir = Path(build_dir)
            if not resolved_build_dir.is_absolute():
                resolved_build_dir = resolved_repo_root / resolved_build_dir
        elif build_id:
            builds_root = getattr(sonic_builds, "builds_root", resolved_repo_root / "distribution" / "builds")
            resolved_build_dir = Path(builds_root) / build_id

        verification = verify_sonic_ready(
            sonic_root,
            manifest_path=manifest_path,
            build_dir=resolved_build_dir,
            flash_pack=flash_pack,
        )
        return {
            "manifest_path": str(manifest_path),
            "build_dir": str(resolved_build_dir) if resolved_build_dir else None,
            "verification": verification,
        }

    @router.get("/sonic/dataset-contract")
    async def sonic_dataset_contract(manifest: str = Query("config/sonic-manifest.json")):
        sonic_root = resolved_repo_root / "sonic"
        manifest_path = Path(manifest)
        if not manifest_path.is_absolute():
            manifest_path = sonic_root / manifest_path

        verification = verify_sonic_ready(
            sonic_root,
            manifest_path=manifest_path,
        )
        return {
            "manifest_path": str(manifest_path),
            "checked_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "dataset_contract": _extract_dataset_contract_summary(verification),
        }

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
            readiness = sonic_builds.get_release_readiness(id)
            return {
                **readiness,
                "release_signing_alert": _build_release_signing_alert(readiness),
            }
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
        release_signing_alert = _build_release_signing_alert(release_readiness)
        builds_root = Path(getattr(sonic_builds, "builds_root", resolved_repo_root / "distribution" / "builds"))
        verification = verify_sonic_ready(
            resolved_repo_root / "sonic",
            manifest_path=(resolved_repo_root / "sonic" / "config" / "sonic-manifest.json"),
            build_dir=(builds_root / latest_build_id) if latest_build_id else None,
        )

        sync_status = None
        if getattr(sonic_ops, "available", False):
            try:
                sync_status = to_sync_status_payload(sonic_ops.sync.get_status())
            except Exception:
                sync_status = None

        workspace = get_template_workspace_service(resolved_repo_root)
        default_profile = getattr(sonic_builds, "default_profile", "alpine-core+sonic")
        return {
            "sonic": status,
            "default_build_profile": default_profile,
            "default_build_profile_source": getattr(
                sonic_builds, "default_profile_source", "packaging_manifest"
            ),
            "template_workspace": workspace.component_contract("sonic"),
            "template_workspace_state": workspace.component_snapshot("sonic"),
            "dashboard": {"route": "#sonic", "wizard_gui_hosted": True},
            "latest_build": latest_build,
            "latest_release_readiness": release_readiness,
            "release_signing_alert": release_signing_alert,
            "dataset_contract": _extract_dataset_contract_summary(verification),
            "verification": verification,
            "device_recommendations": sonic_device_profile.get_recommendations(),
            "media_console": sonic_media.get_status(),
            "windows_gaming_profiles": sonic_gaming.list_profiles(),
            "sync_status": sync_status,
            "actions": {
                "sync": "/api/platform/sonic/gui/actions/sync",
                "rebuild": "/api/platform/sonic/gui/actions/rebuild",
                "export": "/api/platform/sonic/gui/actions/export",
                "bootstrap": "/api/platform/sonic/gui/actions/bootstrap",
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

    @router.post("/sonic/boot/route/default")
    async def sonic_boot_route_default():
        try:
            route = sonic_boot.apply_default_route()
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

    @router.get("/uhome/status")
    async def uhome_status():
        workspace = get_template_workspace_service(resolved_repo_root)
        return {
            "presentation": uhome_presentation.get_status(),
            "template_workspace": workspace.component_contract("uhome"),
            "template_workspace_state": workspace.component_snapshot("uhome"),
        }

    @router.get("/uhome/presentation/status")
    async def uhome_presentation_status():
        return uhome_presentation.get_status()

    @router.post("/uhome/presentation/start")
    async def uhome_presentation_start(payload: UHomePresentationStartRequest):
        try:
            state = uhome_presentation.start(payload.presentation)
            return {"success": True, "state": state}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.post("/uhome/presentation/stop")
    async def uhome_presentation_stop():
        return {"success": True, "state": uhome_presentation.stop()}

    @router.get("/launch/sessions")
    async def list_launch_sessions(
        target: Optional[str] = Query(None),
        limit: int = Query(50, ge=1, le=500),
    ):
        sessions = launch_sessions.list_sessions(target=target, limit=limit)
        return {"count": len(sessions), "sessions": sessions}

    @router.get("/launch/sessions/{session_id}")
    async def get_launch_session(session_id: str):
        try:
            return launch_sessions.get_session(session_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/launch/sessions/{session_id}/stream")
    async def stream_launch_session(session_id: str, timeout_seconds: int = Query(30, ge=1, le=300)):
        try:
            launch_sessions.get_session(session_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

        terminal_states = {"ready", "stopped", "error"}

        async def event_stream():
            elapsed_seconds = 0.0
            last_updated_at: str | None = None
            while elapsed_seconds < timeout_seconds:
                try:
                    session = launch_sessions.get_session(session_id)
                except FileNotFoundError:
                    yield "event: end\ndata: {\"reason\":\"missing\"}\n\n"
                    return

                updated_at = str(session.get("updated_at") or "")
                if updated_at != last_updated_at:
                    last_updated_at = updated_at
                    yield f"event: session\ndata: {json.dumps(session)}\n\n"

                if str(session.get("state") or "").strip().lower() in terminal_states:
                    yield "event: end\ndata: {\"reason\":\"terminal\"}\n\n"
                    return

                await asyncio.sleep(0.5)
                elapsed_seconds += 0.5

            yield "event: end\ndata: {\"reason\":\"timeout\"}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    @router.get("/sonic/linux/launcher")
    async def sonic_linux_launcher_status():
        return sonic_linux.get_status()

    @router.post("/sonic/linux/launcher/action")
    async def sonic_linux_launcher_action(payload: SonicLinuxLauncherActionRequest):
        try:
            state = sonic_linux.apply_action(
                action=payload.action,
                workspace=payload.workspace,
                protocol=payload.protocol,
                execute=payload.execute,
            )
            return {"success": True, "state": state}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except FileNotFoundError as exc:
            raise HTTPException(status_code=503, detail=str(exc))

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

    @router.get("/sonic/windows/gaming/profiles")
    async def sonic_windows_gaming_profiles():
        return sonic_gaming.list_profiles()

    @router.post("/sonic/windows/gaming/profiles/apply")
    async def sonic_windows_gaming_apply(payload: SonicGamingProfileRequest):
        try:
            applied = sonic_gaming.apply_profile(payload.profile_id, extra=payload.extra)
            return {"success": True, "profile": applied}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

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
        force = payload.force if "force" in payload.model_fields_set else True
        result = sonic_ops.sync.rebuild_database(force=force)
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

    @router.post("/sonic/gui/actions/bootstrap")
    async def sonic_gui_action_bootstrap(payload: SonicGUIActionRequest):
        if not getattr(sonic_ops, "available", False):
            raise HTTPException(status_code=503, detail="Sonic plugin not available")
        result = sonic_ops.sync.bootstrap_current_machine(overwrite=payload.force if "force" in payload.model_fields_set else True)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "bootstrap failed"))
        return {"success": True, "action": "bootstrap", "result": result}

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
        dev_extension = get_dev_extension_service(repo_root=repo_root)
        status = dev_extension.framework_status()
        root = Path(status["dev_root"])
        if not root.exists():
            raise HTTPException(status_code=404, detail="/dev extension scaffold not found")

        required = {
            relative_path: (root / relative_path).exists()
            for relative_path in status["required_files"]
        }
        local_workdirs = {
            "files": (root / "files").exists(),
            "relecs": (root / "relecs").exists(),
            "dev_work": (root / "dev-work").exists(),
            "testing": (root / "testing").exists(),
        }
        return {
            "workspace_alias": status["workspace_alias"],
            "root": str(root),
            "mode": "dev-extension-scaffold",
            "required": required,
            "required_files": status["required_files"],
            "missing_files": status["missing_files"],
            "missing_count": len(status["missing_files"]),
            "framework_manifest_path": status["framework_manifest_path"],
            "framework_manifest_present": status["framework_manifest_present"],
            "tracked_sync_paths": status["tracked_sync_paths"],
            "goblin_layers": status["goblin_layers"],
            "ops_paths": status["ops_paths"],
            "local_workdirs": local_workdirs,
            "ready": status["framework_ready"],
        }

    return router
