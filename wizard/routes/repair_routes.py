"""
Repair Routes
=============

Self-heal, backups, and restore operations for Wizard.
"""

from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from wizard.services.repair_service import get_repair_service
from wizard.services.task_scheduler import TaskScheduler
from core.services.maintenance_utils import (
    tidy,
    clean,
    compost,
    compost_cleanup,
    default_repo_allowlist,
    default_memory_allowlist,
    get_memory_root,
)
from wizard.services.path_utils import get_repo_root


class RepairRunRequest(BaseModel):
    action: str
    packages: Optional[list[str]] = None


class BackupRequest(BaseModel):
    target: str
    notes: Optional[str] = None
    priority: int = 5
    need: int = 5


class RestoreRequest(BaseModel):
    artifact_id: str
    target: str


class MaintenanceRequest(BaseModel):
    action: str
    scope: Optional[str] = "workspace"


class CompostCleanupRequest(BaseModel):
    days: int = 30
    dry_run: bool = True


def create_repair_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/repair", tags=["repair"], dependencies=dependencies)

    @router.get("/status")
    async def get_status():
        return {"success": True, "status": get_repair_service().status()}

    @router.post("/run")
    async def run_repair(payload: RepairRunRequest):
        service = get_repair_service()

        if payload.action == "bootstrap-venv":
            return {"success": True, "result": service.bootstrap_venv().to_dict()}
        if payload.action == "install-python-deps":
            return {"success": True, "result": service.install_python_deps().to_dict()}
        if payload.action == "install-dashboard-deps":
            return {
                "success": True,
                "result": service.install_dashboard_deps().to_dict(),
            }
        if payload.action == "build-dashboard":
            return {"success": True, "result": service.build_dashboard().to_dict()}
        if payload.action == "update-alpine-toolchain":
            return {
                "success": True,
                "result": service.update_alpine_toolchain(payload.packages),
            }

        raise HTTPException(status_code=400, detail="Unknown repair action")

    @router.post("/backup")
    async def backup_target(payload: BackupRequest):
        service = get_repair_service()
        result = service.backup_target(payload.target, payload.notes)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Backup failed"))
        return {"success": True, **result}

    @router.post("/backup/queue")
    async def queue_backup(payload: BackupRequest):
        scheduler = TaskScheduler()
        task = scheduler.create_task(
            name=f"Backup {payload.target}",
            description="Queued backup request",
            schedule="once",
            priority=payload.priority,
            need=payload.need,
            resource_cost=2,
            requires_network=False,
            kind="backup_target",
            payload={"target": payload.target, "notes": payload.notes},
        )
        if "error" in task:
            raise HTTPException(status_code=400, detail=task["error"])
        scheduled = scheduler.schedule_task(task["id"])
        if "error" in scheduled:
            raise HTTPException(status_code=400, detail=scheduled["error"])
        return {"success": True, "task": task, "scheduled": scheduled}

    @router.post("/restore")
    async def restore_target(payload: RestoreRequest):
        service = get_repair_service()
        result = service.restore_backup(payload.artifact_id, payload.target)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Restore failed"))
        return {"success": True, **result}

    @router.post("/maintenance")
    async def run_maintenance(payload: MaintenanceRequest):
        scope = (payload.scope or "workspace").lower()

        if scope == "current":
            target_root = Path.cwd()
            recursive = False
        elif scope == "+subfolders":
            target_root = Path.cwd()
            recursive = True
        elif scope == "all":
            target_root = get_repo_root()
            recursive = True
        else:
            target_root = get_memory_root()
            recursive = True

        action = payload.action.lower()
        if action == "tidy":
            moved, archive_root = tidy(target_root, recursive=recursive)
            return {
                "success": True,
                "action": "tidy",
                "moved": moved,
                "archive": str(archive_root),
            }
        if action == "clean":
            if target_root == get_repo_root():
                allowlist = default_repo_allowlist()
            elif target_root == get_memory_root():
                allowlist = default_memory_allowlist()
            else:
                allowlist = []
            moved, archive_root = clean(
                target_root,
                allowed_entries=allowlist,
                recursive=recursive,
            )
            return {
                "success": True,
                "action": "clean",
                "moved": moved,
                "archive": str(archive_root),
            }
        if action == "compost":
            moved, compost_root = compost(target_root, recursive=recursive)
            return {
                "success": True,
                "action": "compost",
                "moved": moved,
                "compost": str(compost_root),
            }

        raise HTTPException(status_code=400, detail="Unknown maintenance action")

    @router.post("/compost/cleanup")
    async def cleanup_compost(payload: CompostCleanupRequest):
        result = compost_cleanup(days=payload.days, dry_run=payload.dry_run)
        return {"success": True, "result": result}

    return router
