"""Logic-assist subroutes for uCODE bridge routes."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class LogicModelRequest(BaseModel):
    model: str
    profile: Optional[str] = "core"


class LogicNetworkRequest(BaseModel):
    prompt: str
    mode: Optional[str] = "conversation"
    workspace: Optional[str] = "core"


def create_ucode_logic_routes(
    *,
    logger: Any,
    logic_history: Optional[List[Dict[str, Any]]] = None,
    ok_history: Optional[List[Dict[str, Any]]] = None,
    get_logic_local_status: Callable[[], Dict[str, Any]],
    get_logic_network_status: Callable[[], Dict[str, Any]],
    get_logic_context_window: Callable[[], int],
    get_logic_default_model: Optional[Callable[[], str]] = None,
    get_logic_default_models: Optional[Callable[[], Dict[str, str]]] = None,
    is_dev_mode_active: Optional[Callable[[], bool]] = None,
    logic_auto_fallback_enabled: Callable[[], bool],
    write_logic_default_model: Callable[[str, str], Dict[str, Any]],
    run_logic_network: Callable[[str], Tuple[str, str]],
) -> APIRouter:
    router = APIRouter(tags=["ucode"])
    history = logic_history if logic_history is not None else (ok_history or [])
    get_default_model = get_logic_default_model or (lambda: "gpt4all")
    get_default_models = get_logic_default_models or (
        lambda: {"core": get_default_model(), "dev": get_default_model()}
    )
    dev_active_checker = is_dev_mode_active or (lambda: False)

    @router.get("/logic/status")
    async def get_logic_status() -> Dict[str, Any]:
        status = get_logic_local_status()
        network_status = get_logic_network_status()
        default_models = get_default_models()
        dev_active = dev_active_checker()
        logger.debug(
            "Logic assist status requested",
            ctx={"model": status.get("model"), "ready": status.get("ready")},
        )
        return {
            "status": "ok",
            "logic": {
                **status,
                "context_window": get_logic_context_window(),
                "default_model": get_default_model(),
                "default_models": default_models,
                "network": network_status,
                "network_fallback": logic_auto_fallback_enabled(),
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

    @router.get("/logic/history")
    async def get_logic_history() -> Dict[str, Any]:
        return {"status": "ok", "history": list(history)}

    @router.post("/logic/model")
    async def set_logic_model(payload: LogicModelRequest) -> Dict[str, Any]:
        model = (payload.model or "").strip()
        profile = (payload.profile or "core").strip().lower()
        dev_active = dev_active_checker()
        if not model:
            logger.warn("Logic model update rejected (empty)")
            raise HTTPException(status_code=400, detail="model is required")
        if profile not in {"core", "dev"}:
            logger.warn(
                "Logic model update rejected (invalid profile)", ctx={"profile": profile}
            )
            raise HTTPException(status_code=400, detail="profile must be core or dev")
        if profile == "dev" and not dev_active:
            logger.warn("Logic model update rejected (dev inactive)")
            raise HTTPException(
                status_code=409,
                detail="Dev extension must be active to set coding profile model",
            )

        write_logic_default_model(profile, model)
        logger.info("Logic model updated", ctx={"model": model, "profile": profile})
        return {"status": "ok", "default_models": get_default_models()}

    @router.post("/logic/network")
    async def run_logic_network_route(payload: LogicNetworkRequest) -> Dict[str, Any]:
        prompt = (payload.prompt or "").strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt is required")

        status = get_logic_network_status()
        if not status.get("ready"):
            raise HTTPException(
                status_code=400,
                detail=status.get("issue") or "network assist unavailable",
            )

        try:
            response, model = run_logic_network(prompt)
        except Exception as exc:
            logger.warn("Logic network request failed", ctx={"error": str(exc)})
            raise HTTPException(status_code=500, detail=str(exc))

        return {"status": "ok", "response": response, "model": model}

    return router
