"""
Workflow management routes for Wizard Server.
"""

from enum import Enum
from typing import Callable, Awaitable, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.routes.ucode_template_dispatch import (
    duplicate_template as dispatch_duplicate_template,
    list_family_templates as dispatch_list_family_templates,
    read_template as dispatch_read_template,
)
from wizard.services.logging_api import get_logger
from wizard.services.workflow_manager import TaskStatus, WorkflowManager
from wizard.services.task_scheduler import TaskScheduler

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_workflow_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/workflows", tags=["workflow-manager"])
    logger = get_logger("wizard", category="workflow", name="workflow-routes")
    manager = WorkflowManager()
    scheduler = TaskScheduler()

    class WorkflowCreate(BaseModel):
        name: str
        description: Optional[str] = None
        tasks: list[str] = []
        template_id: Optional[str] = None
        workflow_id: Optional[str] = None

    class ProjectCreate(BaseModel):
        name: str
        description: Optional[str] = None

    class ProjectTaskCreate(BaseModel):
        title: str
        project_id: int | str | None = None
        description: Optional[str] = None
        priority: int | str = 5
        tags: list[str] = []

    class ProjectTaskStatusUpdate(BaseModel):
        status: str

    class TemplateDuplicateRequest(BaseModel):
        target_name: Optional[str] = None

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"status": "ok", "workflow_manager": "ready"}

    @router.get("/projects")
    async def list_projects(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            projects = manager.list_projects()
            return {"status": "success", "projects": projects, "count": len(projects)}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/projects")
    async def create_project(request: Request, payload: ProjectCreate):
        if auth_guard:
            await auth_guard(request)
        try:
            project_id = manager.create_project(
                name=payload.name,
                description=payload.description or "",
            )
            return manager.get_workflow(project_id)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/tasks")
    async def list_project_tasks(request: Request, project_id: Optional[int] = None):
        if auth_guard:
            await auth_guard(request)
        try:
            tasks = manager.list_tasks(project_id=project_id)
            return {"status": "success", "tasks": tasks, "count": len(tasks)}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/tasks")
    async def create_project_task(request: Request, payload: ProjectTaskCreate):
        if auth_guard:
            await auth_guard(request)
        try:
            if payload.project_id is None:
                raise HTTPException(status_code=400, detail="project_id is required")

            project_id = int(str(payload.project_id).strip())
            priority_map = {"low": 7, "medium": 5, "high": 3, "urgent": 1}
            priority_raw = payload.priority
            priority = (
                priority_map.get(priority_raw.lower(), 5)
                if isinstance(priority_raw, str)
                else int(priority_raw)
            )
            task_id = manager.create_task(
                project_id=project_id,
                title=payload.title,
                description=payload.description or "",
                priority=priority,
                tags=payload.tags or [],
            )
            tasks = manager.get_project_tasks(project_id)
            task = next((item for item in tasks if int(item["id"]) == int(task_id)), None)
            return {
                "status": "success",
                "task": task,
                "workflow_id": str(project_id),
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.patch("/tasks/{task_id}/status")
    async def update_project_task_status(
        request: Request,
        task_id: int,
        payload: ProjectTaskStatusUpdate,
    ):
        if auth_guard:
            await auth_guard(request)
        try:
            normalized = (payload.status or "").strip().lower()
            status_map = {
                "not-started": TaskStatus.NOT_STARTED,
                "not_started": TaskStatus.NOT_STARTED,
                "in-progress": TaskStatus.IN_PROGRESS,
                "in_progress": TaskStatus.IN_PROGRESS,
                "completed": TaskStatus.COMPLETED,
                "blocked": TaskStatus.BLOCKED,
                "deferred": TaskStatus.DEFERRED,
            }
            status = status_map.get(normalized)
            if status is None:
                valid = ", ".join(sorted(item.value for item in TaskStatus))
                raise HTTPException(status_code=400, detail=f"Invalid status. Expected one of: {valid}")
            manager.update_task_status(task_id, status)
            return {"status": "success", "task_id": str(task_id), "task_status": status.value}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.post("/create")
    async def create_workflow(request: Request, workflow: WorkflowCreate):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.create_workflow(
                name=workflow.name,
                description=workflow.description,
                task_ids=workflow.tasks,
                template_id=workflow.template_id,
                workflow_id=workflow.workflow_id,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/list")
    async def list_workflows(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.list_runtime_workflows()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/dashboard")
    async def workflow_dashboard(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.get_runtime_dashboard()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/tasks-dashboard")
    async def workflow_tasks_dashboard(request: Request, limit: int = 20):
        """Aggregate workflow list + scheduler status + recent runs."""
        if auth_guard:
            await auth_guard(request)
        try:
            workflows = manager.list_runtime_workflows()
            return {
                "workflows": workflows.get("workflows", []),
                "scheduler": {
                    "stats": scheduler.get_stats(),
                    "queue": scheduler.get_scheduled_queue(limit=limit),
                    "runs": scheduler.get_execution_history(limit),
                    "settings": scheduler.get_settings(),
                },
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/templates")
    async def workflow_templates(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            response = dispatch_list_family_templates(
                family="workflows",
                logger=logger,
                corr_id="WORKFLOW-TEMPLATE-LIST",
            )
            return response.get("result") or response
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/templates/{template_name}")
    async def workflow_template(request: Request, template_name: str):
        if auth_guard:
            await auth_guard(request)
        try:
            response = dispatch_read_template(
                family="workflows",
                template_name=template_name,
                logger=logger,
                corr_id="WORKFLOW-TEMPLATE-READ",
            )
            return response.get("result") or response
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/templates/{template_name}/duplicate")
    async def duplicate_workflow_template(
        request: Request,
        template_name: str,
        payload: TemplateDuplicateRequest,
    ):
        if auth_guard:
            await auth_guard(request)
        try:
            response = dispatch_duplicate_template(
                family="workflows",
                template_name=template_name,
                target_name=payload.target_name,
                logger=logger,
                corr_id="WORKFLOW-TEMPLATE-DUPLICATE",
            )
            return response.get("result") or response
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/{workflow_id}")
    async def get_workflow(request: Request, workflow_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.get_runtime_workflow(workflow_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.post("/{workflow_id}/run")
    async def run_workflow(request: Request, workflow_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.run_runtime_workflow(workflow_id)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/{workflow_id}/status")
    async def workflow_status(request: Request, workflow_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.get_runtime_workflow_status(workflow_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/{workflow_id}/tasks")
    async def workflow_tasks(request: Request, workflow_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.get_workflow_tasks(workflow_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    return router
