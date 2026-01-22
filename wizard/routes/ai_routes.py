"""
AI Routes (Vibe/Mistral) for Wizard Server.
"""

from typing import Callable, Awaitable, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.mistral_vibe import MistralVibeIntegration

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_ai_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/ai", tags=["ai"])
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
