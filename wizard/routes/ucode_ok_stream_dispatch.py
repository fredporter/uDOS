"""Streamed logic-assist command dispatch helpers for uCODE routes."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from fastapi import HTTPException

from wizard.routes.ucode_command_utils import (
    LOGIC_CODING_MODES,
    parse_logic_command,
    prepare_logic_coding_request,
)
from wizard.routes.ucode_ok_execution import run_ok_stream_with_fallback


def dispatch_ok_stream_command(
    *,
    command: str,
    corr_id: str,
    logger: Any,
    ok_model: Optional[str],
    is_dev_mode_active: Callable[[], bool],
    resolve_ok_model: Callable[[Optional[str], str], str],
    ok_auto_fallback_enabled: Callable[[], bool],
    run_ok_local_stream: Callable[[str, str], Any],
    run_ok_cloud: Callable[[str], tuple[str, str]],
    ok_cloud_available: Callable[[], bool],
    record_ok_output: Callable[..., Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    parsed = parse_logic_command(command)
    if parsed is None:
        return None

    working_command = parsed.command
    if parsed.logic_mode not in LOGIC_CODING_MODES:
        return None
    coding_request = prepare_logic_coding_request(
        parsed=parsed,
        is_dev_mode_active=is_dev_mode_active,
        logger=logger,
        corr_id=corr_id,
        rejected_log_message="Logic stream rejected",
        missing_file_log_message="Logic stream file missing",
    )
    ok_mode = coding_request.mode
    path = coding_request.path
    prompt = coding_request.prompt
    model = resolve_ok_model(ok_model, "coding")
    emitted_chunks: List[str] = []
    response_text, model, source = run_ok_stream_with_fallback(
        prompt=prompt,
        model=model,
        use_cloud=coding_request.use_cloud,
        auto_fallback=ok_auto_fallback_enabled(),
        run_local_stream=run_ok_local_stream,
        run_cloud=run_ok_cloud,
        cloud_available=ok_cloud_available,
        emit_chunk=emitted_chunks.append,
    )

    entry = record_ok_output(
        prompt=prompt,
        response=response_text,
        model=model,
        source=source,
        mode=ok_mode,
        file_path=str(path),
    )
    response = {
        "status": "ok",
        "command": working_command,
        "result": {
            "status": "success",
            "message": f"LOGIC {ok_mode} complete",
            "output": response_text,
        },
        "ok": entry,
    }
    return {"chunks": emitted_chunks, "response": response}
