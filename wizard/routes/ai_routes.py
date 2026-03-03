"""v1.5 logic-assist routes for Wizard Server."""

from typing import Awaitable, Callable, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.logic_assist_service import (
    LogicAssistRequest,
    get_logic_assist_service,
)

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_ai_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/logic", tags=["logic"])

    class CodeExplainRequest(BaseModel):
        file_path: str
        line_start: Optional[int] = None
        line_end: Optional[int] = None

    class CompleteRequest(BaseModel):
        prompt: str
        mode: Optional[str] = "conversation"
        conversation_id: Optional[str] = None
        max_tokens: Optional[int] = 512
        workspace: Optional[str] = "core"
        privacy: Optional[str] = "internal"
        tags: Optional[list[str]] = None
        force_network: Optional[bool] = False
        allow_network: Optional[bool] = True
        system_prompt: Optional[str] = ""
        temperature: Optional[float] = None
        offline_required: Optional[bool] = False
        actor: Optional[str] = None

    @router.get("/config")
    async def get_logic_config(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            status = get_logic_assist_service().get_status()
            return {
                "status": "ok",
                "schema": status["schema"],
                "profile": status["profile"],
                "default_model": status["profile"]["local_model_name"],
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/health")
    async def logic_health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            status = get_logic_assist_service().get_status()
            return {
                "status": "ok",
                "local": status["local"],
                "network": status["network"],
            }
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc))

    @router.get("/status")
    async def get_logic_status(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return get_logic_assist_service().get_status()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/models")
    async def get_logic_models(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return {"models": get_logic_assist_service().list_models()}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/complete")
    async def complete_logic(request: Request, body: CompleteRequest):
        if auth_guard:
            await auth_guard(request)
        try:
            logic_request = LogicAssistRequest(
                prompt=body.prompt,
                mode=body.mode,
                conversation_id=body.conversation_id,
                max_tokens=body.max_tokens or 512,
                workspace=body.workspace or "core",
                privacy=body.privacy or "internal",
                tags=body.tags or [],
                system_prompt=body.system_prompt or "",
                temperature=body.temperature,
                force_network=bool(body.force_network),
                allow_network=bool(body.allow_network),
                offline_required=bool(body.offline_required),
                actor=body.actor,
            )
            device_id = request.client.host if request.client else "local"
            result = await get_logic_assist_service().complete(
                logic_request, device_id=device_id
            )
            return {"status": "ok", "result": result.to_dict()}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/explain-code")
    async def explain_code(request: Request, body: CodeExplainRequest):
        if auth_guard:
            await auth_guard(request)
        try:
            line_range = None
            range_suffix = ""
            if body.line_start and body.line_end:
                line_range = (body.line_start, body.line_end)
                range_suffix = f" lines {body.line_start}-{body.line_end}"
            prompt = (
                f"Explain the code in {body.file_path}{range_suffix}. "
                "Provide purpose, key logic, risk points, and safe next steps."
            )
            result = await get_logic_assist_service().complete(
                LogicAssistRequest(prompt=prompt, mode="code", workspace="wizard"),
                device_id=request.client.host if request.client else "local",
            )
            return {
                "file_path": body.file_path,
                "line_range": line_range,
                "explanation": result.content,
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
