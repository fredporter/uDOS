from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from core.services.prompt_parser_service import get_prompt_parser_service
from core.workflows.scheduler import WorkflowScheduler
from wizard.services.deploy_mode import get_deploy_mode, is_managed_mode
from wizard.services.logging_api import get_log_stats, get_logs_root
from wizard.services.markdown_job_service import MarkdownJobService
from wizard.services.monitoring_manager import AlertSeverity, AlertType, MonitoringManager
from wizard.services.ops_workspace_service import OpsWorkspaceService
from wizard.services.path_utils import get_repo_root
from wizard.services.setup_manager import get_full_config_status
from wizard.services.task_scheduler import TaskScheduler

AuthGuard = Optional[Callable[[Request], Awaitable[None]]]
SessionResolver = Optional[Callable[[Request], dict[str, object]]]


def _tail_lines(path: Path, lines: int) -> list[str]:
    data = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return data[-lines:]


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
    resource_cost: int = 1
    requires_network: bool = False
    prompt_text: str | None = None
    source_path: str | None = None


def create_ops_routes(
    auth_guard: AuthGuard = None,
    session_resolver: SessionResolver = None,
) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/ops", tags=["ops"], dependencies=dependencies)
    scheduler = TaskScheduler()
    monitoring = MonitoringManager()
    parser = get_prompt_parser_service()
    workflow_scheduler = WorkflowScheduler(Path(get_repo_root()))
    workspace_service = OpsWorkspaceService()
    markdown_jobs = MarkdownJobService()

    @router.get("/session")
    async def get_session(request: Request) -> dict[str, Any]:
        if not session_resolver:
            return {"authenticated": False, "deploy_mode": get_deploy_mode()}
        try:
            session = session_resolver(request)
        except Exception as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        return {"authenticated": True, "deploy_mode": get_deploy_mode(), "session": session}

    @router.get("/summary")
    async def get_summary() -> dict[str, Any]:
        monitoring.run_default_checks()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "deploy_mode": get_deploy_mode(),
            "jobs": {
                "stats": scheduler.get_stats(),
                "queue": scheduler.get_scheduled_queue(limit=10),
                "runs": scheduler.get_execution_history(limit=10),
            },
            "health": monitoring.get_health_summary(),
            "config": {
                "managed": is_managed_mode(),
                "status": get_full_config_status(),
            },
            "workflow_templates": workflow_scheduler.list_templates(),
            "workflow_runs": workflow_scheduler.list_workflows(),
            "workspace_sources": workspace_service.list_sources(limit=50),
            "logs": get_log_stats(),
        }

    @router.get("/health")
    async def get_health() -> dict[str, Any]:
        monitoring.run_default_checks()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "health": monitoring.get_health_summary(),
            "alerts": [alert.to_dict() for alert in monitoring.get_alerts(limit=20)],
        }

    @router.get("/jobs")
    async def list_jobs(limit: int = Query(50, ge=1, le=500)) -> dict[str, Any]:
        return {
            "tasks": scheduler.list_tasks(limit=limit),
            "queue": scheduler.get_scheduled_queue(limit=limit),
            "runs": scheduler.get_execution_history(limit=min(limit, 100)),
            "settings": scheduler.get_settings(),
            "workflow_templates": workflow_scheduler.list_templates(),
            "workflow_runs": workflow_scheduler.list_workflows(),
            "workspace_sources": workspace_service.list_sources(limit=100),
        }

    @router.post("/jobs")
    async def create_job(payload: OpsJobCreate) -> dict[str, Any]:
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
                            "tags": task.tags,
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
            payload=payload.payload,
        )
        return {"created": [created]}

    @router.post("/jobs/{job_id}/run")
    async def run_job(job_id: str) -> dict[str, Any]:
        return scheduler.execute_task(job_id)

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

    @router.get("/logs")
    async def list_logs(lines: int = Query(100, ge=10, le=1000)) -> dict[str, Any]:
        log_dir = get_logs_root()
        entries = []
        for log_path in sorted(log_dir.rglob("*.jsonl")):
            try:
                stat = log_path.stat()
                entries.append(
                    {
                        "name": str(log_path.relative_to(log_dir)),
                        "updated_at": datetime.utcfromtimestamp(stat.st_mtime).isoformat() + "Z",
                        "tail": _tail_lines(log_path, lines),
                    }
                )
            except FileNotFoundError:
                continue
        return {"count": len(entries), "logs": entries}

    @router.get("/config-status")
    async def config_status() -> dict[str, Any]:
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

    @router.get("/releases")
    async def releases() -> dict[str, Any]:
        workflow_dir = Path(get_repo_root()) / ".github" / "workflows"
        workflows = sorted(path.name for path in workflow_dir.glob("*.yml"))
        return {
            "deploy_mode": get_deploy_mode(),
            "workflows": workflows,
            "render_blueprint_present": (Path(get_repo_root()) / "render.yaml").exists(),
        }

    return router
