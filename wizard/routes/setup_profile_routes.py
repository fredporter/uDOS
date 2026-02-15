"""Profile and installation setup subroutes."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class UserProfilePayload(BaseModel):
    username: str
    date_of_birth: str
    role: str
    timezone: str
    local_time: str
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None


class InstallProfilePayload(BaseModel):
    installation_id: Optional[str] = None
    os_type: Optional[str] = None
    lifespan_mode: Optional[str] = None
    moves_limit: Optional[int] = None
    capabilities: Optional[Dict[str, bool]] = None
    permissions: Optional[Dict[str, Any]] = None


def create_setup_profile_routes(
    *,
    load_user_profile: Callable[[], Any],
    load_install_profile: Callable[[], Any],
    save_user_profile: Callable[[Dict[str, Any]], Any],
    save_install_profile: Callable[[Dict[str, Any]], Any],
    load_install_metrics: Callable[[], Dict[str, Any]],
    sync_metrics_from_profile: Callable[[Dict[str, Any]], Dict[str, Any]],
    increment_moves: Callable[[], Dict[str, Any]],
    mark_variable_configured: Callable[[str], None],
    apply_capabilities_to_wizard_config: Callable[[Dict[str, bool]], None],
    validate_location_id: Callable[[str | None], None],
    resolve_location_name: Callable[[str], str],
    is_ghost_mode: Callable[[str | None, str | None], bool],
) -> APIRouter:
    router = APIRouter(tags=["setup"])

    def _payload_to_dict(payload: BaseModel) -> Dict[str, Any]:
        if hasattr(payload, "model_dump"):
            return payload.model_dump()
        return payload.dict()

    @router.get("/profiles")
    async def get_profiles():
        user = load_user_profile()
        install = load_install_profile()
        return {
            "user_profile": user.data,
            "install_profile": install.data,
            "ghost_mode": is_ghost_mode(
                (user.data or {}).get("username"),
                (user.data or {}).get("role"),
            ),
            "secret_store_locked": user.locked or install.locked,
            "errors": [e for e in [user.error, install.error] if e],
            "install_metrics": load_install_metrics(),
        }

    @router.post("/profile/user")
    async def set_user_profile(payload: UserProfilePayload):
        validate_location_id(payload.location_id)
        payload_dict = _payload_to_dict(payload)
        payload_dict["location_name"] = resolve_location_name(payload.location_id)
        payload_dict["ghost_mode"] = is_ghost_mode(
            payload_dict.get("username"),
            payload_dict.get("role"),
        )
        result = save_user_profile(payload_dict)
        if result.locked:
            raise HTTPException(status_code=503, detail=result.error or "secret store locked")
        mark_variable_configured("user_profile")
        return {"status": "success", "user_profile": result.data}

    @router.post("/profile/install")
    async def set_install_profile(payload: InstallProfilePayload):
        result = save_install_profile(_payload_to_dict(payload))
        if result.locked:
            raise HTTPException(status_code=503, detail=result.error or "secret store locked")
        capabilities = (result.data or {}).get("capabilities") or {}
        apply_capabilities_to_wizard_config(capabilities)
        metrics = sync_metrics_from_profile(result.data or {})
        mark_variable_configured("install_profile")
        return {"status": "success", "install_profile": result.data, "install_metrics": metrics}

    @router.get("/installation/metrics")
    async def get_install_metrics():
        return {"status": "success", "metrics": load_install_metrics()}

    @router.post("/installation/moves")
    async def add_install_move():
        return {"status": "success", "metrics": increment_moves()}

    @router.get("/profile/user")
    async def get_user_profile():
        result = load_user_profile()
        if result.locked:
            raise HTTPException(status_code=503, detail=result.error or "secret store locked")
        if not result.data:
            raise HTTPException(status_code=404, detail="No user profile found. Please complete setup story first.")
        return {"status": "success", "profile": result.data}

    @router.get("/profile/install")
    async def get_install_profile():
        result = load_install_profile()
        if result.locked:
            raise HTTPException(status_code=503, detail=result.error or "secret store locked")
        if not result.data:
            raise HTTPException(status_code=404, detail="No installation profile found. Please complete setup story first.")
        metrics = load_install_metrics()
        return {"status": "success", "profile": result.data, "metrics": metrics}

    @router.get("/profile/combined")
    async def get_combined_profile():
        user_result = load_user_profile()
        install_result = load_install_profile()
        if user_result.locked or install_result.locked:
            raise HTTPException(
                status_code=503,
                detail=user_result.error or install_result.error or "secret store locked",
            )
        metrics = load_install_metrics()
        return {
            "status": "success",
            "user_profile": user_result.data,
            "install_profile": install_result.data,
            "install_metrics": metrics,
            "setup_complete": bool(user_result.data and install_result.data),
        }

    return router
