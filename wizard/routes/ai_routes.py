"""
AI Routes (Vibe/Mistral) for Wizard Server.
"""

from typing import Callable, Awaitable, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.mistral_vibe import MistralVibeIntegration
from wizard.services.ok_gateway import OKGateway, OKRequest

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_ai_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/ai", tags=["ai"])
    ai_instance: Optional[MistralVibeIntegration] = None

    def get_ai() -> MistralVibeIntegration:
        nonlocal ai_instance
        if ai_instance is None:
            ai_instance = MistralVibeIntegration()
        return ai_instance

    class QueryRequest(BaseModel):
        prompt: str
        include_context: bool = True
        model: str = "devstral-small"

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
        cloud_sanity: Optional[bool] = False
        force_cloud: Optional[bool] = False
        allow_cloud: Optional[bool] = True
        system_prompt: Optional[str] = ""
        temperature: Optional[float] = None
        offline_required: Optional[bool] = False
        ghost_mode: Optional[bool] = False
        task_hint: Optional[str] = None

    @router.get("/config")
    async def get_ai_config(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            ai = get_ai()
            return {
                "status": "ok",
                "vibe_cli_installed": True,
                "vibe_config_path": str(ai.vibe_config) if ai.vibe_config else None,
                "default_model": "devstral-small",
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            ai = get_ai()
            context = ai.get_context_files()
            return {
                "status": "ok",
                "vibe_cli_installed": True,
                "context_files_loaded": len(context),
            }
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc))

    @router.post("/query")
    async def query_ai(request: Request, body: QueryRequest):
        if auth_guard:
            await auth_guard(request)
        try:
            ai = get_ai()
            response = ai.query_vibe(
                body.prompt, include_context=body.include_context, model=body.model
            )
            return {"response": response, "model": body.model}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/complete")
    async def complete_ai(request: Request, body: CompleteRequest):
        if auth_guard:
            await auth_guard(request)
        try:
            gateway = OKGateway()
            ok_request = OKRequest(
                prompt=body.prompt,
                mode=body.mode,
                conversation_id=body.conversation_id,
                max_tokens=body.max_tokens or 512,
                workspace=body.workspace or "core",
                privacy=body.privacy or "internal",
                tags=body.tags or [],
                system_prompt=body.system_prompt or "",
                temperature=body.temperature,
                cloud_sanity=bool(body.cloud_sanity),
                force_cloud=bool(body.force_cloud),
                allow_cloud=bool(body.allow_cloud),
                offline_required=bool(body.offline_required),
                ghost_mode=bool(body.ghost_mode),
                task_hint=body.task_hint,
            )
            device_id = request.client.host if request.client else "local"
            result = await gateway.complete(ok_request, device_id=device_id)
            return {
                "status": "ok",
                "result": result.to_dict(),
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/context")
    async def get_context(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            ai = get_ai()
            context = ai.get_context_files()
            return {
                "files": list(context.keys()),
                "total_files": len(context),
                "total_chars": sum(len(c) for c in context.values()),
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/analyze-logs")
    async def analyze_logs(request: Request, log_type: str = "error"):
        if auth_guard:
            await auth_guard(request)
        try:
            ai = get_ai()
            analysis = ai.analyze_logs(log_type)
            return {"log_type": log_type, "analysis": analysis}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/suggest-next")
    async def suggest_next_steps(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            ai = get_ai()
            suggestions = ai.suggest_next_steps()
            return {"suggestions": suggestions}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/explain-code")
    async def explain_code(request: Request, body: CodeExplainRequest):
        if auth_guard:
            await auth_guard(request)
        try:
            ai = get_ai()
            line_range = None
            if body.line_start and body.line_end:
                line_range = (body.line_start, body.line_end)
            explanation = ai.explain_code(body.file_path, line_range)
            return {
                "file_path": body.file_path,
                "line_range": line_range,
                "explanation": explanation,
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
