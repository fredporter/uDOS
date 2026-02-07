"""
Dev Mode routes for Wizard Server.
"""

from typing import Callable, Awaitable, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.dev_mode_service import get_dev_mode_service
from wizard.services.logging_api import get_logger, new_corr_id

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_dev_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/dev", tags=["dev-mode"])
    dev_mode = get_dev_mode_service()
    logger = get_logger("wizard", category="dev-mode", name="dev")

    def _ensure_admin_dev_access():
        try:
            from core.services.user_service import get_user_manager, Permission

            user_mgr = get_user_manager()
            if not user_mgr.has_permission(Permission.ADMIN):
                raise HTTPException(status_code=403, detail="Admin role required for dev mode")
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    def _ensure_dev_submodule():
        message = dev_mode.ensure_requirements()
        if message:
            raise HTTPException(status_code=412, detail=message)

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        logger.debug("Dev health check requested")
        return dev_mode.get_health()

    @router.get("/status")
    async def get_status(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        logger.debug("Dev status requested")
        return dev_mode.get_status()

    @router.post("/activate")
    async def activate_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        corr_id = new_corr_id("C")
        logger.info("Dev mode activate requested", ctx={"corr_id": corr_id})
        return dev_mode.activate()

    @router.post("/deactivate")
    async def deactivate_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        corr_id = new_corr_id("C")
        logger.info("Dev mode deactivate requested", ctx={"corr_id": corr_id})
        return dev_mode.deactivate()

    @router.post("/restart")
    async def restart_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        corr_id = new_corr_id("C")
        logger.info("Dev mode restart requested", ctx={"corr_id": corr_id})
        return dev_mode.restart()

    @router.post("/clear")
    async def clear_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        corr_id = new_corr_id("C")
        logger.info("Dev mode clear requested", ctx={"corr_id": corr_id})
        return dev_mode.clear()

    @router.get("/logs")
    async def get_dev_logs(request: Request, lines: int = 50):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        try:
            return dev_mode.get_logs(lines)
        except Exception as exc:
            logger.error("Dev logs fetch failed", err=exc)
            raise HTTPException(status_code=500, detail=str(exc))

    return router
