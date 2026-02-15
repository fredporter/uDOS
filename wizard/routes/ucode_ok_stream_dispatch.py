"""Streamed OK command dispatch helpers for uCODE routes."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from fastapi import HTTPException

from wizard.routes.ucode_command_utils import normalize_ok_command
from wizard.routes.ucode_ok_execution import run_ok_stream_with_fallback
from wizard.routes.ucode_route_utils import (
    build_ok_file_prompt,
    load_ok_file_content,
    parse_ok_file_args,
)


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
    working_command = normalize_ok_command(command)
    upper = working_command.upper()
    if not (upper == "OK" or upper.startswith("OK ")):
        return None

    ok_args = working_command[2:].strip()
    ok_tokens = ok_args.split() if ok_args else []
    ok_mode = (ok_tokens[0].upper() if ok_tokens else "LOCAL")
    if ok_mode not in {"EXPLAIN", "DIFF", "PATCH"}:
        return None
    if not is_dev_mode_active():
        raise HTTPException(
            status_code=409,
            detail="OK coding commands require active Dev Mode (DEV ON).",
        )

    parsed = parse_ok_file_args(" ".join(ok_tokens[1:]))
    if parsed.get("error"):
        logger.warn(
            "OK stream rejected",
            ctx={"corr_id": corr_id, "error": parsed.get("error")},
        )
        raise HTTPException(status_code=400, detail=parsed.get("error"))

    path = parsed["path"]
    try:
        content = load_ok_file_content(
            path,
            line_start=parsed.get("line_start"),
            line_end=parsed.get("line_end"),
        )
    except HTTPException:
        logger.warn(
            "OK stream file missing",
            ctx={"corr_id": corr_id, "path": str(path)},
        )
        raise

    prompt = build_ok_file_prompt(ok_mode, path, content)
    model = resolve_ok_model(ok_model, "coding")
    emitted_chunks: List[str] = []
    response_text, model, source = run_ok_stream_with_fallback(
        prompt=prompt,
        model=model,
        use_cloud=bool(parsed.get("use_cloud")),
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
            "message": f"OK {ok_mode} complete",
            "output": response_text,
        },
        "ok": entry,
    }
    return {"chunks": emitted_chunks, "response": response}
