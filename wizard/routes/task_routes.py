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
        priority: int = 5
        need: int = 5
        mission: Optional[str] = None
        objective: Optional[str] = None
        resource_cost: int = 1
        requires_network: bool = False
        kind: Optional[str] = None
        payload: Optional[dict] = None

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
                schedule=task.cron_expression,
                provider=task.provider,
                enabled=task.enabled,
                priority=task.priority,
                need=task.need,
                mission=task.mission,
                objective=task.objective,
                resource_cost=task.resource_cost,
                requires_network=task.requires_network,
                kind=task.kind,
                payload=task.payload,
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

    @router.get("/status")
    async def get_status(request: Request, limit: int = 20):
        if auth_guard:
            await auth_guard(request)
        try:
            return {
                "stats": scheduler.get_stats(),
                "queue": scheduler.get_scheduled_queue(limit=limit),
                "settings": scheduler.get_settings(),
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    class SchedulerSettings(BaseModel):
        max_tasks_per_tick: Optional[int] = None
        tick_seconds: Optional[int] = None
        allow_network: Optional[bool] = None

    @router.post("/settings")
    async def update_settings(request: Request, payload: SchedulerSettings):
        if auth_guard:
            await auth_guard(request)
        try:
            updates = payload.dict(exclude_unset=True)
            return {"success": True, "settings": scheduler.update_settings(updates)}
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

    @router.get("/task/{task_id}")
    async def get_task(request: Request, task_id: str):
        if auth_guard:
            await auth_guard(request)
        task = scheduler.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    @router.post("/execute/{task_id}")
    async def execute_task(request: Request, task_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.execute_task(task_id)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
