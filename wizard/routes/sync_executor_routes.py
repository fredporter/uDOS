"""
Sync Executor routes for Wizard Server.
"""

from typing import Callable, Awaitable, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.sync_executor import SyncExecutor

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_sync_executor_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/sync-executor", tags=["sync-executor"])
    executor = SyncExecutor()

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"status": "ok", "sync_executor": "ready"}

    @router.get("/status")
    async def sync_status(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return executor.get_status()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/execute")
    async def execute_sync(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return executor.execute_queue()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/queue")
    async def get_queue(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return executor.get_queue()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/history")
    async def get_history(request: Request, limit: int = 50):
        if auth_guard:
            await auth_guard(request)
        try:
            return executor.get_execution_history(limit)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
