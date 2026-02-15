"""User-management subroutes for uCODE bridge routes."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class UserSwitchRequest(BaseModel):
    username: str


class UserRoleRequest(BaseModel):
    username: str
    role: str


def create_ucode_user_routes(logger=None) -> APIRouter:
    router = APIRouter(tags=["ucode"])

    @router.get("/user")
    async def get_current_user() -> Dict[str, Any]:
        try:
            from core.services.user_service import get_user_manager, is_ghost_mode

            user_mgr = get_user_manager()
            user = user_mgr.current()
            if not user:
                return {"status": "error", "message": "No current user"}
            return {
                "status": "ok",
                "user": user.to_dict(),
                "ghost_mode": is_ghost_mode(),
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/users")
    async def list_users() -> Dict[str, Any]:
        try:
            from core.services.user_service import get_user_manager

            user_mgr = get_user_manager()
            return {"status": "ok", "users": user_mgr.list_users()}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/user/switch")
    async def switch_user(payload: UserSwitchRequest) -> Dict[str, Any]:
        try:
            from core.services.user_service import get_user_manager

            user_mgr = get_user_manager()
            success, msg = user_mgr.switch_user(payload.username)
            if not success:
                raise HTTPException(status_code=400, detail=msg)
            return {"status": "ok", "message": msg}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/user/role")
    async def set_user_role(payload: UserRoleRequest) -> Dict[str, Any]:
        try:
            from core.services.user_service import (
                Permission,
                UserRole,
                get_user_manager,
            )

            user_mgr = get_user_manager()
            if not user_mgr.has_permission(Permission.ADMIN):
                raise HTTPException(status_code=403, detail="Admin permission required")
            try:
                role = UserRole(payload.role.lower())
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid role")
            success, msg = user_mgr.set_role(payload.username, role)
            if not success:
                raise HTTPException(status_code=400, detail=msg)
            return {"status": "ok", "message": msg}
        except HTTPException:
            raise
        except Exception as exc:
            if logger:
                logger.warn("Set user role failed", ctx={"error": str(exc)})
            raise HTTPException(status_code=500, detail=str(exc))

    return router
