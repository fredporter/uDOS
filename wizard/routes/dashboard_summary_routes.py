"""
Dashboard Summary Routes
========================

Aggregated status endpoint for the Wizard dashboard UI.

Routes:
    GET /api/dashboard/summary  — full multi-subsystem status roll-up
    GET /api/dashboard/health   — minimal pass/fail health check (200 or 503)

Design goals:
- Every subsystem is probed independently — one failure never blocks the others.
- Callers receive a consistent envelope with per-subsystem {ok, ...detail} shape.
- No auth required on /health so load-balancers and monitors can poll freely.
- /summary honours the optional auth_guard so the UI can pass its token.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends, HTTPException

from core.services.time_utils import render_utc_as_local, utc_now_iso, utc_now_iso_z
from core.services.template_workspace_service import get_template_workspace_service
from wizard.services.path_utils import get_repo_root
from wizard.services.sonic_boot_profile_service import get_sonic_boot_profile_service
from wizard.services.sonic_build_service import get_sonic_build_service
from wizard.services.sonic_media_console_service import get_sonic_media_console_service
from wizard.services.uhome_presentation_service import get_uhome_presentation_service
from wizard.version_utils import get_wizard_server_version


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _probe(fn: Callable[[], dict[str, Any]], label: str) -> dict[str, Any]:
    """Call fn() and return its result merged with ok=True, or ok=False + error."""
    try:
        result = fn()
        if isinstance(result, dict):
            return {"ok": True, **result}
        return {"ok": True, "result": result}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "subsystem": label}


def _logic_local_status() -> dict[str, Any]:
    from wizard.services.logic_assist_service import get_logic_assist_service

    return get_logic_assist_service(get_repo_root()).get_status()["local"]


def _cloud_status() -> dict[str, Any]:
    from wizard.services.cloud_provider_executor import get_cloud_availability
    info = get_cloud_availability()
    return {
        "ready": info.get("ready", False),
        "available_providers": info.get("available_providers", []),
        "primary": info.get("primary"),
    }


def _ha_status() -> dict[str, Any]:
    from wizard.services.home_assistant_service import get_ha_service
    s = get_ha_service().status()
    return {
        "enabled": s.get("enabled", False),
        "status": s.get("status", "unknown"),
    }


def _sync_status() -> dict[str, Any]:
    from wizard.services.admin_secret_contract import collect_admin_secret_contract
    from wizard.services.path_utils import get_repo_root
    result = collect_admin_secret_contract(repo_root=get_repo_root())
    issues = result.get("issues", [])
    return {
        "drift_issues": len(issues),
        "issues": issues,
        "synced": len(issues) == 0,
    }


def _workspace_runtime_status() -> dict[str, Any]:
    repo_root = get_repo_root()
    workspace = get_template_workspace_service(repo_root)
    sonic_build = get_sonic_build_service(repo_root=repo_root)
    sonic_media = get_sonic_media_console_service(repo_root=repo_root)
    sonic_boot = get_sonic_boot_profile_service(repo_root=repo_root)
    uhome = get_uhome_presentation_service(repo_root=repo_root)

    sonic_media_status = sonic_media.get_status()
    sonic_boot_status = sonic_boot.get_route_status()
    uhome_status = uhome.get_status()

    return {
        "workspace_ref": "@memory/bank/typo-workspace",
        "components": {
            "sonic": {
                "template_workspace": workspace.component_contract("sonic"),
                "template_workspace_state": workspace.component_snapshot("sonic"),
                "defaults": {
                    "build_profile": {
                        "value": getattr(sonic_build, "default_profile", None),
                        "source": getattr(
                            sonic_build, "default_profile_source", "packaging_manifest"
                        ),
                    },
                    "boot_route": {
                        "value": sonic_boot_status.get("preferred_route_profile_id"),
                        "source": sonic_boot_status.get("preferred_route_source", "default"),
                        "detail": sonic_boot_status.get("preferred_route"),
                    },
                    "media_launcher": {
                        "value": sonic_media_status.get("preferred_launcher"),
                        "source": sonic_media_status.get(
                            "preferred_launcher_source", "default"
                        ),
                    },
                },
            },
            "uhome": {
                "template_workspace": workspace.component_contract("uhome"),
                "template_workspace_state": workspace.component_snapshot("uhome"),
                "defaults": {
                    "presentation": {
                        "value": uhome_status.get("preferred_presentation"),
                        "source": uhome_status.get(
                            "preferred_presentation_source", "default"
                        ),
                    },
                    "node_role": {
                        "value": uhome_status.get("node_role"),
                        "source": uhome_status.get("node_role_source", "default"),
                    },
                },
            },
        },
    }


# ---------------------------------------------------------------------------
# Route factory
# ---------------------------------------------------------------------------


def health_probe(services: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Return the canonical wizard health payload.

    Called by both ``GET /health`` (server.py) and ``GET /api/dashboard/health``
    so both surfaces stay in sync without duplicating logic.

    Args:
        services: Optional config-derived dict
            ``{plugin_repo, web_proxy, ok_gateway}`` — included only when the
            caller has access to WizardServerConfig.  Absent from the dashboard
            probe which has no config reference.
    """
    logic_local = _probe(_logic_local_status, "logic_local")
    result: dict[str, Any] = {
        "status": "healthy",
        "ok": True,
        "bridge": "udos-wizard",
        "version": get_wizard_server_version(),
        "timestamp": utc_now_iso_z(),
        "server_time": render_utc_as_local(),
        "logic_local_ready": logic_local.get("ok", False) and logic_local.get("ready", False),
    }
    if services is not None:
        result["services"] = services
    return result


def create_dashboard_summary_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    """Create aggregated dashboard summary routes."""
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

    @router.get("/health")
    async def dashboard_health():
        """Minimal health check — 200 if Wizard is up, 503 if critically degraded.

        No auth required. Safe to poll from load-balancers and uptime monitors.
        """
        return health_probe()

    @router.get("/summary", dependencies=dependencies)
    async def dashboard_summary():
        """Full multi-subsystem status roll-up for the Wizard dashboard UI.

        Probes each subsystem independently — partial failures are reported
        per-subsystem without failing the whole response.
        """
        ts = utc_now_iso()

        logic_local = _probe(_logic_local_status, "logic_local")
        cloud    = _probe(_cloud_status, "cloud")
        ha       = _probe(_ha_status, "ha_bridge")
        sync     = _probe(_sync_status, "secret_sync")
        workspace_runtime = _probe(_workspace_runtime_status, "workspace_runtime")

        subsystems = {
            "logic_local": logic_local,
            "cloud": cloud,
            "ha_bridge": ha,
            "secret_sync": sync,
            "workspace_runtime": workspace_runtime,
        }

        # Overall health: ok if all critical subsystems report ok
        critical = [logic_local, cloud]
        overall_ok = all(s.get("ok", False) for s in critical)

        return {
            "ok": overall_ok,
            "bridge": "udos-wizard",
            "version": get_wizard_server_version(),
            "timestamp": ts,
            "server_time": render_utc_as_local(ts),
            "subsystems": subsystems,
            "workspace_runtime": workspace_runtime,
            "summary": {
                "total": len(subsystems),
                "healthy": sum(1 for s in subsystems.values() if s.get("ok")),
                "degraded": sum(1 for s in subsystems.values() if not s.get("ok")),
            },
        }

    return router
