"""
Task scheduling routes for Wizard Server.
"""

from typing import Callable, Awaitable, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.task_scheduler import TaskScheduler

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_task_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/tasks", tags=["task-scheduler"])
    scheduler = TaskScheduler()

    class TaskCreate(BaseModel):
        name: str
        description: Optional[str] = None
        cron_expression: str
        provider: Optional[str] = None
        enabled: bool = True

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"status": "ok", "scheduler": "ready"}

    @router.post("/schedule")
    async def schedule_task(request: Request, task: TaskCreate):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.create_task(
                name=task.name,
                description=task.description,
                cron=task.cron_expression,
                provider=task.provider,
                enabled=task.enabled,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/queue")
    async def get_queue(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.get_scheduled_queue()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/runs")
    async def get_runs(request: Request, limit: int = 50):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.get_execution_history(limit)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/runs/{task_id}")
    async def get_task_runs(request: Request, task_id: str, limit: int = 20):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.get_task_runs(task_id, limit)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/execute/{task_id}")
    async def execute_task(request: Request, task_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.execute_task(task_id)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
