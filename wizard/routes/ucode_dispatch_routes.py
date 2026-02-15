"""Dispatch subroutes for uCODE bridge routes."""

from __future__ import annotations

from typing import Any, Callable, Dict, Generator, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from wizard.routes.ucode_stream_utils import iter_text_chunks, sse_event


class DispatchRequest(BaseModel):
    command: str
    ok_model: Optional[str] = None
    ok_context_window: Optional[int] = None


def create_ucode_dispatch_routes(
    *,
    logger,
    dispatcher,
    new_corr_id: Callable[[str], str],
    set_corr_id: Callable[[str], Any],
    reset_corr_id: Callable[[Any], None],
    dispatch_core: Callable[[str, DispatchRequest, str], Dict[str, Any]],
    dispatch_ok_stream_command: Callable[..., Optional[Dict[str, Any]]],
    is_dev_mode_active: Callable[[], bool],
    resolve_ok_model: Callable[[Optional[str], str], str],
    ok_auto_fallback_enabled: Callable[[], bool],
    run_ok_local_stream: Callable[[str, str], Any],
    run_ok_cloud: Callable[[str], Any],
    ok_cloud_available: Callable[[], bool],
    record_ok_output: Callable[..., Dict[str, Any]],
) -> APIRouter:
    router = APIRouter(tags=["ucode"])

    def _extract_output(result: Dict[str, Any], rendered_text: Optional[str]) -> str:
        if result.get("output"):
            return result["output"]
        if result.get("help"):
            return result["help"]
        if result.get("text"):
            return result["text"]
        if result.get("message"):
            return result["message"]
        return rendered_text or ""

    @router.post("/dispatch")
    async def dispatch_command(payload: DispatchRequest) -> Dict[str, Any]:
        if not dispatcher:
            raise HTTPException(status_code=500, detail="uCODE dispatcher unavailable")

        corr_id = new_corr_id("C")
        token = set_corr_id(corr_id)
        try:
            command = (payload.command or "").strip()
            return dispatch_core(command, payload, corr_id)
        finally:
            reset_corr_id(token)

    @router.post("/dispatch/stream")
    async def dispatch_command_stream(payload: DispatchRequest) -> StreamingResponse:
        if not dispatcher:
            raise HTTPException(status_code=500, detail="uCODE dispatcher unavailable")

        corr_id = new_corr_id("C")
        token = set_corr_id(corr_id)
        command = (payload.command or "").strip()
        if not command:
            logger.warn("Empty stream command rejected", ctx={"corr_id": corr_id})
            reset_corr_id(token)
            raise HTTPException(status_code=400, detail="command is required")

        async def event_stream() -> Generator[bytes, None, None]:
            yield sse_event("start", {"command": command})
            try:
                logger.info(
                    "Stream dispatch",
                    ctx={"corr_id": corr_id, "raw": command},
                )
                stream_ok = dispatch_ok_stream_command(
                    command=command,
                    corr_id=corr_id,
                    logger=logger,
                    ok_model=payload.ok_model,
                    is_dev_mode_active=is_dev_mode_active,
                    resolve_ok_model=resolve_ok_model,
                    ok_auto_fallback_enabled=ok_auto_fallback_enabled,
                    run_ok_local_stream=run_ok_local_stream,
                    run_ok_cloud=run_ok_cloud,
                    ok_cloud_available=ok_cloud_available,
                    record_ok_output=record_ok_output,
                )
                if stream_ok is not None:
                    for piece in stream_ok.get("chunks") or []:
                        yield sse_event("chunk", {"text": piece})
                    yield sse_event("result", stream_ok["response"])
                    return
                response = dispatch_core(command, payload, corr_id)
                rendered_text = response.get("rendered")
                output_text = _extract_output(response.get("result") or {}, rendered_text)
                for text_piece in iter_text_chunks(output_text):
                    yield sse_event("chunk", {"text": text_piece})
                yield sse_event("result", response)
            except HTTPException as exc:
                yield sse_event("error", {"error": exc.detail})
            except Exception as exc:
                yield sse_event("error", {"error": str(exc)})
            finally:
                reset_corr_id(token)

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return router
