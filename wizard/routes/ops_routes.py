from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from core.services.time_utils import render_utc_as_local, utc_from_timestamp, utc_now_iso_z
from core.services.prompt_parser_service import get_prompt_parser_service
from core.workflows.scheduler import WorkflowScheduler
from wizard.services.deploy_mode import get_deploy_mode, is_managed_mode
from wizard.services.logging_api import get_log_stats, get_logger, get_logs_root
from wizard.services.markdown_job_service import MarkdownJobService
from wizard.services.monitoring_manager import AlertSeverity, AlertType, MonitoringManager
from wizard.services.ops_workspace_service import OpsWorkspaceService
from wizard.services.ops_role_service import load_ops_role_contract
from wizard.services.path_utils import get_repo_root
from wizard.services.setup_manager import get_full_config_status
from wizard.services.task_scheduler import TaskScheduler
from wizard.routes.ucode_template_dispatch import (
    list_family_templates as dispatch_list_family_templates,
    list_template_families as dispatch_list_template_families,
)

AuthGuard = Optional[Callable[[Request], Awaitable[None]]]
SessionResolver = Optional[Callable[[Request], dict[str, object]]]


def _tail_lines(path: Path, lines: int) -> list[str]:
    data = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return data[-lines:]


def _server_time_metadata() -> dict[str, str]:
    rendered = render_utc_as_local((os.environ.get("TZ") or "").strip() or None)
    return {
        "iana_name": rendered["timezone"],
        "label": rendered["label"],
        "offset": rendered["offset"],
        "local_time": rendered["local_time"],
        "utc_time": rendered["utc_time"],
    }


def _coerce_role(value: object) -> str:
    role = str(value or "guest").strip().lower()
    if role in {"admin", "operator"}:
        return role
    return "guest"


def _validate_auto_retry_policy(
    policy: dict[str, dict[str, Any]] | None,
) -> dict[str, dict[str, Any]] | None:
    if policy is None:
        return None
    validated: dict[str, dict[str, Any]] = {}
    for reason, entry in policy.items():
        if not isinstance(reason, str) or not reason.strip():
            raise HTTPException(status_code=400, detail="Maintenance retry policy reason must be a non-empty string")
        if not isinstance(entry, dict):
            raise HTTPException(status_code=400, detail=f"Maintenance retry policy for '{reason}' must be an object")
        if "enabled" in entry and not isinstance(entry["enabled"], bool):
            raise HTTPException(status_code=400, detail=f"Maintenance retry policy for '{reason}' has invalid enabled flag")
        if "dry_run" in entry and not isinstance(entry["dry_run"], bool):
            raise HTTPException(status_code=400, detail=f"Maintenance retry policy for '{reason}' has invalid dry_run flag")
        if "window" in entry and not isinstance(entry["window"], str):
            raise HTTPException(status_code=400, detail=f"Maintenance retry policy for '{reason}' has invalid window")
        limit = entry.get("limit", 0)
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            raise HTTPException(status_code=400, detail=f"Maintenance retry policy for '{reason}' has invalid limit")
        window = str(entry.get("window", "") or "").strip()
        if window:
            try:
                start_raw, end_raw = window.split("-", 1)
                from datetime import datetime

                datetime.strptime(start_raw, "%H:%M")
                datetime.strptime(end_raw, "%H:%M")
            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=f"Maintenance retry policy for '{reason}' has invalid window",
                ) from exc
        validated[reason.strip()] = {
            "enabled": bool(entry.get("enabled", True)),
            "limit": int(limit),
            "dry_run": bool(entry.get("dry_run", False)),
            "window": window,
        }
    return validated


class OpsJobCreate(BaseModel):
    name: str | None = None
    description: str | None = None
    schedule: str = "daily"
    kind: str | None = None
    payload: dict[str, Any] | None = None
    provider: str | None = None
    enabled: bool = True
    priority: int = 5
    need: int = 5
    mission: str | None = None
    objective: str | None = None
    project: str | None = None
    resource_cost: int = 1
    requires_network: bool = False
    window: str | None = None
    budget_units: int | None = None
    prompt_text: str | None = None
    source_path: str | None = None


class OpsSettingsUpdate(BaseModel):
    max_tasks_per_tick: int | None = None
    tick_seconds: int | None = None
    allow_network: bool | None = None
    off_peak_start_hour: int | None = None
    off_peak_end_hour: int | None = None
    api_budget_daily: int | None = None
    api_budget_used: int | None = None
    defer_alert_threshold: int | None = None
    backoff_alert_minutes: int | None = None
    auto_retry_deferred_reasons: list[str] | None = None
    auto_retry_deferred_limit: int | None = None
    maintenance_retry_dry_run: bool | None = None
    auto_retry_deferred_policy: dict[str, dict[str, Any]] | None = None
    backoff_policy: dict[str, dict[str, int]] | None = None


def create_ops_routes(
    auth_guard: AuthGuard = None,
    session_resolver: SessionResolver = None,
) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/ops", tags=["ops"], dependencies=dependencies)
    logger = get_logger("wizard", category="ops", name="ops-routes")
    scheduler = TaskScheduler()
    monitoring = MonitoringManager()
    parser = get_prompt_parser_service()
    workflow_scheduler = WorkflowScheduler(Path(get_repo_root()))
    workspace_service = OpsWorkspaceService()
    markdown_jobs = MarkdownJobService()
    role_contract = load_ops_role_contract()

    def _template_families() -> dict[str, Any]:
        return dispatch_list_template_families(
            logger=logger,
            corr_id="OPS-TEMPLATE-LIST",
        )

    def _workflow_templates() -> list[str]:
        response = dispatch_list_family_templates(
            family="workflows",
            logger=logger,
            corr_id="OPS-WORKFLOW-TEMPLATES",
        )
        result = response.get("result") or {}
        return result.get("templates") or []

    def _resolve_session_payload(request: Request) -> dict[str, Any]:
        if not session_resolver:
            return {
                "authenticated": False,
                "deploy_mode": get_deploy_mode(),
                "session": {"role": "guest"},
            }
        try:
            session = session_resolver(request)
        except Exception as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        return {
            "authenticated": True,
            "deploy_mode": get_deploy_mode(),
            "session": session,
        }

    def _switchboard_payload(request: Request) -> dict[str, Any]:
        session_payload = _resolve_session_payload(request)
        session = session_payload.get("session") or {}
        role = _coerce_role((session or {}).get("role"))
        role_payload = role_contract.for_role(role)
        capabilities = role_payload["capabilities"]
        sections = [
            {
                "id": "planning",
                "label": "Planning",
                "path": "/api/ops/planning/overview",
                "capabilities": ["view_planning"],
            },
            {
                "id": "automation",
                "label": "Automation",
                "path": "/api/ops/automation/overview",
                "capabilities": ["view_automation"],
            },
            {
                "id": "config",
                "label": "Config",
                "path": "/api/ops/config/status",
                "capabilities": ["manage_settings"],
            },
            {
                "id": "releases",
                "label": "Releases",
                "path": "/api/ops/releases/overview",
                "capabilities": ["view_releases"],
            },
            {
                "id": "logs",
                "label": "Logs",
                "path": "/api/ops/logs/files",
                "capabilities": ["view_logs"],
            },
        ]
        visible_sections = [
            section["id"]
            for section in sections
            if all(capability in capabilities for capability in section["capabilities"])
        ]
        return {
            "role": role,
            "role_name": role_payload["role_name"],
            "capabilities": capabilities,
            "permission_grid": role_payload["permission_grid"],
            "role_template": role_payload["source"],
            "default_section": visible_sections[0] if visible_sections else "planning",
            "sections": [
                {
                    **section,
                    "enabled": section["id"] in visible_sections,
                }
                for section in sections
            ],
        }

    def _require_capability(request: Request, capability: str) -> None:
        if not session_resolver:
            return
        switchboard = _switchboard_payload(request)
        if capability not in switchboard["capabilities"]:
            raise HTTPException(status_code=403, detail=f"Missing capability: {capability}")

    def _workflow_states(limit: int) -> list[dict[str, Any]]:
        workflow_ids = workflow_scheduler.list_workflows()[:limit]
        workflows = []
        for workflow_id in workflow_ids:
            try:
                workflows.append(workflow_scheduler.status(workflow_id))
            except FileNotFoundError:
                continue
        return workflows

    def _planning_project_label(item: dict[str, Any]) -> str:
        payload = item.get("payload") or {}
        spec = item.get("spec") or {}
        direct = str(
            payload.get("project")
            or item.get("project")
            or item.get("mission")
            or spec.get("project")
            or spec.get("workflow_id")
            or ""
        ).strip()
        if direct:
            return direct
        source_path = str(payload.get("source_path") or spec.get("source_path") or "").strip()
        if source_path:
            parts = [part for part in source_path.split("/") if part]
            if len(parts) >= 2:
                return parts[-2]
            if parts:
                return parts[0]
        return "General"

    def _planning_window_label(item: dict[str, Any]) -> str:
        payload = item.get("payload") or {}
        value = str(payload.get("window") or item.get("window") or item.get("schedule") or "").strip()
        return value or "unspecified"

    def _planning_items(
        workflow_items: list[dict[str, Any]],
        task_items: list[dict[str, Any]],
        workflows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for item in workflow_items:
            items.append(
                {
                    **item,
                    "planning_type": "workflow_queue",
                    "project": _planning_project_label(item),
                    "window": _planning_window_label(item),
                }
            )
        for item in task_items:
            items.append(
                {
                    **item,
                    "planning_type": "task_queue",
                    "project": _planning_project_label(item),
                    "window": _planning_window_label(item),
                }
            )
        for workflow in workflows:
            state = workflow.get("state") or {}
            items.append(
                {
                    **workflow,
                    "scheduled_for": state.get("next_run_at"),
                    "planning_type": "workflow_run",
                    "project": _planning_project_label(workflow),
                    "window": _planning_window_label(workflow),
                    "defer_reason": "",
                }
            )
        return items

    def _planning_filters(items: list[dict[str, Any]]) -> dict[str, list[str]]:
        def _sorted_values(field: str) -> list[str]:
            return sorted(
                {
                    str(item.get(field) or "").strip()
                    for item in items
                    if str(item.get(field) or "").strip()
                }
            )

        return {
            "projects": _sorted_values("project"),
            "windows": _sorted_values("window"),
            "defer_reasons": _sorted_values("defer_reason"),
        }

    def _jobs_payload(limit: int) -> dict[str, Any]:
        return {
            "runtime": {
                "server_time": _server_time_metadata(),
            },
            "tasks": scheduler.list_tasks(limit=limit),
            "queue": scheduler.get_scheduled_queue(limit=limit),
            "runs": scheduler.get_execution_history(limit=min(limit, 100)),
            "settings": scheduler.get_settings(),
            "stats": scheduler.get_stats(),
            "template_families": (_template_families().get("result") or {}).get("families", []),
            "workflow_templates": _workflow_templates(),
            "workflow_runs": workflow_scheduler.list_workflows(),
            "workspace_sources": workspace_service.list_sources(limit=max(limit, 100)),
        }

    def _planning_overview(limit: int) -> dict[str, Any]:
        jobs_payload = _jobs_payload(limit)
        queue = jobs_payload["queue"]
        workflow_states = _workflow_states(limit)
        planning_items = _planning_items(
            [item for item in queue if item.get("kind") == "workflow_phase"],
            [item for item in queue if item.get("kind") != "workflow_phase"],
            workflow_states,
        )
        return {
            "timestamp": utc_now_iso_z(),
            "deploy_mode": get_deploy_mode(),
            "runtime": jobs_payload["runtime"],
            "jobs": {
                "stats": jobs_payload["stats"],
                "settings": jobs_payload["settings"],
                "tasks": jobs_payload["tasks"],
                "queue": jobs_payload["queue"],
                "runs": jobs_payload["runs"],
            },
            "template_families": jobs_payload["template_families"],
            "workflow_templates": jobs_payload["workflow_templates"],
            "workflow_runs": jobs_payload["workflow_runs"],
            "workflow_states": workflow_states,
            "workspace_sources": jobs_payload["workspace_sources"],
            "planning": {
                "items": planning_items,
                "filters": _planning_filters(planning_items),
            },
        }

    def _automation_overview(alert_limit: int = 100, recent_run_limit: int = 20) -> dict[str, Any]:
        monitoring.run_default_checks()
        alerts = monitoring.get_alerts(limit=alert_limit)
        return {
            "timestamp": utc_now_iso_z(),
            "deploy_mode": get_deploy_mode(),
            "runtime": {
                "server_time": _server_time_metadata(),
            },
            "health": monitoring.get_health_summary(),
            "alerts": [alert.to_dict() for alert in alerts],
            "recent_runs": monitoring.get_recent_automation_runs(limit=recent_run_limit),
            "status": monitoring.get_automation_status(),
        }

    def _logs_payload(lines: int) -> dict[str, Any]:
        log_dir = get_logs_root()
        entries = []
        for log_path in sorted(log_dir.rglob("*.jsonl")):
            try:
                stat = log_path.stat()
                entries.append(
                    {
                        "name": str(log_path.relative_to(log_dir)),
                        "updated_at": utc_from_timestamp(stat.st_mtime).isoformat().replace("+00:00", "Z"),
                        "tail": _tail_lines(log_path, lines),
                    }
                )
            except FileNotFoundError:
                continue
        return {"root": str(log_dir), "count": len(entries), "logs": entries}

    def _config_status_payload() -> dict[str, Any]:
        status = get_full_config_status()
        managed_contract = {
            key: bool((os.environ.get(key) or "").strip())
            for key in (
                "SUPABASE_URL",
                "SUPABASE_ANON_KEY",
                "SUPABASE_JWT_SECRET",
                "SUPABASE_JWT_ISSUER",
                "SUPABASE_JWT_AUDIENCE",
                "SUPABASE_DB_DSN",
                "BETTERSTACK_SOURCE_TOKEN",
                "BETTERSTACK_INGESTING_HOST",
                "RENDER_EXTERNAL_URL",
            )
        }
        return {"deploy_mode": get_deploy_mode(), "managed_contract": managed_contract, "status": status}

    def _releases_payload() -> dict[str, Any]:
        workflow_dir = Path(get_repo_root()) / ".github" / "workflows"
        workflows = sorted(path.name for path in workflow_dir.glob("*.yml"))
        return {
            "deploy_mode": get_deploy_mode(),
            "workflows": workflows,
            "render_blueprint_present": (Path(get_repo_root()) / "render.yaml").exists(),
        }

    def _system_overview() -> dict[str, Any]:
        return {
            "timestamp": utc_now_iso_z(),
            "deploy_mode": get_deploy_mode(),
            "runtime": {
                "server_time": _server_time_metadata(),
            },
            "logs": {
                "root": str(get_logs_root()),
                "stats": get_log_stats(),
            },
            "config": _config_status_payload(),
            "releases": _releases_payload(),
        }

    @router.get("/session")
    async def get_session(request: Request) -> dict[str, Any]:
        return _resolve_session_payload(request)

    @router.get("/switchboard")
    async def get_switchboard(request: Request) -> dict[str, Any]:
        return {
            "timestamp": utc_now_iso_z(),
            "deploy_mode": get_deploy_mode(),
            "runtime": {
                "server_time": _server_time_metadata(),
            },
            "switchboard": _switchboard_payload(request),
        }

    @router.get("/planning/overview")
    async def get_planning_overview(limit: int = Query(200, ge=1, le=500)) -> dict[str, Any]:
        return _planning_overview(limit)

    @router.get("/planning/jobs")
    async def list_planning_jobs(limit: int = Query(200, ge=1, le=500)) -> dict[str, Any]:
        return _jobs_payload(limit)

    @router.post("/planning/jobs")
    async def create_planning_job(payload: OpsJobCreate) -> dict[str, Any]:
        if payload.source_path:
            imported = markdown_jobs.import_source(payload.source_path)
            created = [
                scheduler.create_task(
                    name=item["name"],
                    description=item["description"],
                    schedule=item["schedule"],
                    provider=item.get("provider"),
                    enabled=payload.enabled,
                    priority=item.get("priority", payload.priority),
                    need=item.get("need", payload.need),
                    mission=item.get("mission"),
                    objective=item.get("objective"),
                    resource_cost=item.get("resource_cost", payload.resource_cost),
                    requires_network=item.get("requires_network", payload.requires_network),
                    kind=item.get("kind"),
                    payload=item.get("payload"),
                )
                for item in imported
            ]
            return {"created": created, "source_path": payload.source_path}
        if payload.prompt_text:
            parsed = parser.parse(payload.prompt_text)
            created = []
            for task in parsed.get("tasks", []):
                created.append(
                    scheduler.create_task(
                        name=task.title,
                        description=task.description,
                        schedule=payload.schedule,
                        provider=payload.provider,
                        enabled=payload.enabled,
                        priority=payload.priority,
                        need=payload.need,
                        mission=payload.mission,
                        objective=payload.objective,
                        resource_cost=payload.resource_cost,
                        requires_network=payload.requires_network,
                        kind=payload.kind or "prompt_task",
                        payload={
                            "prompt_text": payload.prompt_text,
                            "instruction_id": parsed.get("instruction_id"),
                            "project": payload.project,
                            "tags": task.tags,
                            "window": payload.window,
                            "budget_units": payload.budget_units or payload.resource_cost,
                            **(payload.payload or {}),
                        },
                    )
                )
            return {"created": created, "instruction": parsed}
        if not payload.name:
            raise HTTPException(status_code=400, detail="Job name or prompt_text required")
        created = scheduler.create_task(
            name=payload.name,
            description=payload.description or "",
            schedule=payload.schedule,
            provider=payload.provider,
            enabled=payload.enabled,
            priority=payload.priority,
            need=payload.need,
            mission=payload.mission,
            objective=payload.objective,
            resource_cost=payload.resource_cost,
            requires_network=payload.requires_network,
            kind=payload.kind,
            payload={
                **(payload.payload or {}),
                "project": payload.project,
                "window": payload.window,
                "budget_units": payload.budget_units or payload.resource_cost,
            },
        )
        return {"created": [created]}

    @router.post("/planning/jobs/{job_id}/run")
    async def run_planning_job(job_id: str) -> dict[str, Any]:
        return scheduler.execute_task(job_id)

    @router.get("/planning/templates")
    async def list_planning_templates() -> dict[str, Any]:
        response = _template_families()
        return response.get("result") or response

    @router.get("/planning/templates/{family}")
    async def list_planning_templates_by_family(family: str) -> dict[str, Any]:
        response = dispatch_list_family_templates(
            family=family,
            logger=logger,
            corr_id=f"OPS-TEMPLATE-{family.upper()}",
        )
        return response.get("result") or response

    @router.get("/planning/workflows")
    async def list_planning_workflows(limit: int = Query(200, ge=1, le=500)) -> dict[str, Any]:
        workflows = _workflow_states(limit)
        return {"count": len(workflows), "workflows": workflows}

    @router.post("/planning/workflows/{workflow_id}/approve")
    async def approve_workflow_phase(workflow_id: str) -> dict[str, Any]:
        try:
            state = workflow_scheduler.approve_phase(workflow_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"success": True, "workflow_id": workflow_id, "state": state.status}

    @router.post("/planning/workflows/{workflow_id}/escalate")
    async def escalate_workflow_phase(workflow_id: str) -> dict[str, Any]:
        try:
            state = workflow_scheduler.escalate_phase(workflow_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"success": True, "workflow_id": workflow_id, "state": state.status}

    @router.post("/planning/queue/{queue_id}/retry")
    async def retry_queue_item(queue_id: int) -> dict[str, Any]:
        retried = scheduler.retry_queue_item(queue_id)
        if not retried:
            raise HTTPException(status_code=404, detail="Queued job not found")
        monitoring.check_scheduler_queue()
        return {"success": True, "queue_item": retried}

    @router.post("/planning/deferred/retry")
    async def retry_deferred_jobs(
        reason: str | None = Query(None),
        limit: int = Query(50, ge=1, le=500),
    ) -> dict[str, Any]:
        retried = scheduler.retry_deferred_items(reason=reason, limit=limit)
        monitoring.check_scheduler_queue()
        return {"success": True, "count": len(retried), "queue_items": retried, "reason": reason}

    @router.get("/planning/deferred/preview")
    async def preview_deferred_jobs(
        reason: str | None = Query(None),
        limit: int = Query(20, ge=1, le=200),
    ) -> dict[str, Any]:
        items = scheduler.list_deferred_items(reason=reason, limit=limit)
        return {"count": len(items), "queue_items": items, "reason": reason}

    @router.get("/alerts")
    async def list_alerts(
        severity: Optional[str] = None,
        type: Optional[str] = None,
        service: Optional[str] = None,
        unacknowledged_only: bool = False,
        limit: int = Query(100, ge=1, le=500),
    ) -> dict[str, Any]:
        sev_enum = AlertSeverity(severity) if severity else None
        type_enum = AlertType(type) if type else None
        alerts = monitoring.get_alerts(
            severity=sev_enum,
            type=type_enum,
            service=service,
            unacknowledged_only=unacknowledged_only,
            limit=limit,
        )
        return {"count": len(alerts), "alerts": [alert.to_dict() for alert in alerts]}

    @router.post("/alerts/{alert_id}/ack")
    async def acknowledge_alert(alert_id: str) -> dict[str, Any]:
        if not monitoring.acknowledge_alert(alert_id):
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"success": True, "alert_id": alert_id, "acknowledged": True}

    @router.post("/alerts/{alert_id}/resolve")
    async def resolve_alert(alert_id: str) -> dict[str, Any]:
        if not monitoring.resolve_alert(alert_id):
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"success": True, "alert_id": alert_id, "resolved": True}

    @router.get("/automation/overview")
    async def get_automation_overview(limit: int = Query(100, ge=1, le=500)) -> dict[str, Any]:
        return _automation_overview(alert_limit=limit, recent_run_limit=min(limit, 100))

    @router.get("/config/status")
    async def config_status(request: Request) -> dict[str, Any]:
        _require_capability(request, "view_config")
        return _config_status_payload()

    @router.post("/config/settings")
    async def update_config_settings(request: Request, payload: OpsSettingsUpdate) -> dict[str, Any]:
        _require_capability(request, "manage_settings")
        updates = payload.model_dump(exclude_none=True)
        if "auto_retry_deferred_policy" in updates:
            updates["auto_retry_deferred_policy"] = _validate_auto_retry_policy(updates["auto_retry_deferred_policy"])
        return {"settings": scheduler.update_settings(updates)}

    @router.get("/logs/files")
    async def list_logs(request: Request, lines: int = Query(100, ge=10, le=1000)) -> dict[str, Any]:
        _require_capability(request, "view_logs")
        return _logs_payload(lines)

    @router.get("/releases/overview")
    async def releases_overview(request: Request) -> dict[str, Any]:
        _require_capability(request, "view_releases")
        return {
            "timestamp": utc_now_iso_z(),
            "deploy_mode": get_deploy_mode(),
            "runtime": {
                "server_time": _server_time_metadata(),
            },
            "releases": _releases_payload(),
        }

    return router
