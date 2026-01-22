"""
Workflow management routes for Wizard Server.
"""

from typing import Callable, Awaitable, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.workflow_manager import WorkflowManager

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_workflow_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/workflows", tags=["workflow-manager"])
    manager = WorkflowManager()

    class WorkflowCreate(BaseModel):
        name: str
        description: Optional[str] = None
        tasks: list[str] = []

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"status": "ok", "workflow_manager": "ready"}

    @router.post("/create")
    async def create_workflow(request: Request, workflow: WorkflowCreate):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.create_workflow(
                name=workflow.name,
                description=workflow.description,
                task_ids=workflow.tasks,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/list")
    async def list_workflows(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.get_workflows()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/{workflow_id}")
    async def get_workflow(request: Request, workflow_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.get_workflow(workflow_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.post("/{workflow_id}/run")
    async def run_workflow(request: Request, workflow_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.run_workflow(workflow_id)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/{workflow_id}/status")
    async def workflow_status(request: Request, workflow_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return manager.get_workflow_status(workflow_id)
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
