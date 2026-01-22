"""
Dev Mode routes for Wizard Server.
"""

from typing import Callable, Awaitable, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.dev_mode_service import DevModeService

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_dev_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/dev", tags=["dev-mode"])
    dev_mode = DevModeService()

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        return dev_mode.get_health()

    @router.get("/status")
    async def get_status(request: Request):
        if auth_guard:
            await auth_guard(request)
        return dev_mode.get_status()

    @router.post("/activate")
    async def activate_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        return dev_mode.activate()

    @router.post("/deactivate")
    async def deactivate_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        return dev_mode.deactivate()

    @router.post("/restart")
    async def restart_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        return dev_mode.restart()

    @router.get("/logs")
    async def get_dev_logs(request: Request, lines: int = 50):
        if auth_guard:
            await auth_guard(request)
        try:
            return dev_mode.get_logs(lines)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
