"""OK subroutes for uCODE bridge routes."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class OkModelRequest(BaseModel):
    model: str
    profile: Optional[str] = "core"


class OkCloudRequest(BaseModel):
    prompt: str
    mode: Optional[str] = "conversation"
    workspace: Optional[str] = "core"


def create_ucode_ok_routes(
    *,
    logger: Any,
    ok_history: List[Dict[str, Any]],
    get_ok_local_status: Callable[[], Dict[str, Any]],
    get_ok_cloud_status: Callable[[], Dict[str, Any]],
    get_ok_context_window: Callable[[], int],
    get_ok_default_model: Optional[Callable[[], str]] = None,
    get_ok_default_models: Optional[Callable[[], Dict[str, str]]] = None,
    is_dev_mode_active: Optional[Callable[[], bool]] = None,
    ok_auto_fallback_enabled: Callable[[], bool],
    load_ai_modes_config: Callable[[], Dict[str, Any]],
    write_ok_modes_config: Callable[[Dict[str, Any]], None],
    run_ok_cloud: Callable[[str], Tuple[str, str]],
) -> APIRouter:
    router = APIRouter(tags=["ucode"])
    get_default_model = get_ok_default_model or (lambda: "mistral-small-latest")
    get_default_models = get_ok_default_models or (
        lambda: {"core": get_default_model(), "dev": get_default_model()}
    )
    dev_active_checker = is_dev_mode_active or (lambda: False)

    @router.get("/ok/status")
    async def get_ok_status() -> Dict[str, Any]:
        status = get_ok_local_status()
        cloud_status = get_ok_cloud_status()
        config = load_ai_modes_config()
        mode = (config.get("modes") or {}).get("ofvibe", {})
        declared_models = [m.get("name") for m in (mode.get("models") or []) if m.get("name")]
        default_models = get_default_models()
        dev_active = dev_active_checker()
        logger.debug(
            "OK status requested",
            ctx={"model": status.get("model"), "ready": status.get("ready")},
        )
        return {
            "status": "ok",
            "ok": {
                **status,
                "context_window": get_ok_context_window(),
                "default_model": get_default_model(),
                "default_models": default_models,
                "declared_models": declared_models,
                "cloud": cloud_status,
                "auto_fallback": ok_auto_fallback_enabled(),
                "dev_mode_active": dev_active,
                "profiles": {
                    "general": {
                        "enabled": True,
                        "model": default_models.get("core"),
                    },
                    "coding": {
                        "enabled": dev_active,
                        "model": default_models.get("dev"),
                        "requires": "dev_mode_active",
                    },
                },
            },
        }

    @router.get("/ok/history")
    async def get_ok_history() -> Dict[str, Any]:
        return {"status": "ok", "history": list(ok_history)}

    @router.post("/ok/model")
    async def set_ok_model(payload: OkModelRequest) -> Dict[str, Any]:
        model = (payload.model or "").strip()
        profile = (payload.profile or "core").strip().lower()
        dev_active = dev_active_checker()
        if not model:
            logger.warn("OK model update rejected (empty)")
            raise HTTPException(status_code=400, detail="model is required")
        if profile not in {"core", "dev"}:
            logger.warn("OK model update rejected (invalid profile)", ctx={"profile": profile})
            raise HTTPException(status_code=400, detail="profile must be core or dev")
        if profile == "dev" and not dev_active:
            logger.warn("OK model update rejected (dev inactive)")
            raise HTTPException(status_code=409, detail="Dev Mode must be active to set coding profile model")

        config = load_ai_modes_config()
        modes = config.setdefault("modes", {})
        ofvibe = modes.setdefault("ofvibe", {})
        default_models = ofvibe.setdefault("default_models", {})
        default_models[profile] = model

        models = ofvibe.setdefault("models", [])
        if model not in [m.get("name") for m in models if isinstance(m, dict)]:
            models.append({"name": model, "availability": [profile]})

        write_ok_modes_config(config)
        logger.info("OK model updated", ctx={"model": model, "profile": profile})
        return {"status": "ok", "default_models": default_models}

    @router.post("/ok/cloud")
    async def run_ok_cloud_route(payload: OkCloudRequest) -> Dict[str, Any]:
        prompt = (payload.prompt or "").strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt is required")

        status = get_ok_cloud_status()
        if not status.get("ready"):
            raise HTTPException(status_code=400, detail=status.get("issue") or "mistral unavailable")

        try:
            response, model = run_ok_cloud(prompt)
        except Exception as exc:
            logger.warn("OK cloud request failed", ctx={"error": str(exc)})
            raise HTTPException(status_code=500, detail=str(exc))

        return {"status": "ok", "response": response, "model": model}

    @router.post("/ok/setup")
    async def run_ok_setup() -> Dict[str, Any]:
        try:
            from core.services.logging_api import get_repo_root
            from core.services.ok_setup import run_ok_setup as _run_ok_setup

            result = _run_ok_setup(get_repo_root())
            return {"status": "ok", "result": result}
        except Exception as exc:
            logger.warn("OK setup failed", ctx={"error": str(exc)})
            raise HTTPException(status_code=500, detail=str(exc))

    return router
