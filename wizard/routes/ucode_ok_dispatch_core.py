"""Synchronous OK command dispatch core for uCODE routes."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from fastapi import HTTPException

from wizard.routes.ucode_command_utils import normalize_ok_command
from wizard.routes.ucode_ok_execution import run_ok_with_fallback
from wizard.routes.ucode_route_utils import (
    build_ok_file_prompt,
    load_ok_file_content,
    parse_ok_file_args,
)


def dispatch_ok_command(
    *,
    command: str,
    corr_id: str,
    logger: Any,
    ok_history: List[Dict[str, Any]],
    ok_model: Optional[str],
    load_ai_modes_config: Callable[[], Dict[str, Any]],
    write_ok_modes_config: Callable[[Dict[str, Any]], None],
    ok_auto_fallback_enabled: Callable[[], bool],
    get_ok_default_model: Callable[[], str],
    run_ok_local: Callable[[str, Optional[str]], str],
    run_ok_cloud: Callable[[str], tuple[str, str]],
    ok_cloud_available: Callable[[], bool],
    record_ok_output: Callable[..., Dict[str, Any]],
    is_dev_mode_active: Callable[[], bool],
    resolve_ok_model: Callable[[Optional[str], str], str],
) -> Optional[Dict[str, Any]]:
    command = normalize_ok_command(command)

    upper = command.upper()
    if not (upper == "OK" or upper.startswith("OK ")):
        return None

    ok_args = command[2:].strip()
    ok_tokens = ok_args.split() if ok_args else []
    ok_mode = (ok_tokens[0].upper() if ok_tokens else "LOCAL")

    if ok_mode in {"LOCAL", "VIBE"}:
        logger.info(
            "OK local history request",
            ctx={"corr_id": corr_id, "mode": ok_mode},
        )
        limit = 5
        if len(ok_tokens) >= 2 and ok_tokens[1].isdigit():
            limit = max(1, int(ok_tokens[1]))
        entries = ok_history[-limit:] if ok_history else []
        return {
            "status": "ok",
            "command": command,
            "result": {
                "status": "success",
                "message": "OK LOCAL history",
                "output": "",
            },
            "ok_history": entries,
        }

    if ok_mode == "FALLBACK":
        toggle = ok_tokens[1].lower() if len(ok_tokens) > 1 else ""
        config = load_ai_modes_config()
        modes = config.setdefault("modes", {})
        ofvibe = modes.setdefault("ofvibe", {})
        if toggle in {"on", "true", "yes"}:
            ofvibe["auto_fallback"] = True
            write_ok_modes_config(config)
            return {
                "status": "ok",
                "command": command,
                "result": {
                    "status": "success",
                    "message": "OK fallback set to auto (on)",
                    "output": "",
                },
            }
        if toggle in {"off", "false", "no"}:
            ofvibe["auto_fallback"] = False
            write_ok_modes_config(config)
            return {
                "status": "ok",
                "command": command,
                "result": {
                    "status": "success",
                    "message": "OK fallback set to manual (off)",
                    "output": "",
                },
            }
        current = "on" if ok_auto_fallback_enabled() else "off"
        return {
            "status": "ok",
            "command": command,
            "result": {
                "status": "success",
                "message": f"OK fallback is {current}",
                "output": "Usage: OK FALLBACK on|off",
            },
        }

    if ok_mode in {"EXPLAIN", "DIFF", "PATCH"}:
        if not is_dev_mode_active():
            raise HTTPException(
                status_code=409,
                detail="OK coding commands require active Dev Mode (DEV ON).",
            )
        parsed = parse_ok_file_args(" ".join(ok_tokens[1:]))
        if parsed.get("error"):
            logger.warn(
                "OK command rejected",
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
                "OK file missing",
                ctx={"corr_id": corr_id, "path": str(path)},
            )
            raise
        prompt = build_ok_file_prompt(ok_mode, path, content)

        model = resolve_ok_model(ok_model, "coding")
        try:
            response_text, model, source = run_ok_with_fallback(
                prompt=prompt,
                model=model,
                use_cloud=bool(parsed.get("use_cloud")),
                auto_fallback=ok_auto_fallback_enabled(),
                run_local=run_ok_local,
                run_cloud=run_ok_cloud,
                cloud_available=ok_cloud_available,
                local_failure_detail="OK local failed",
            )
        except HTTPException as exc:
            if exc.status_code == 400:
                logger.warn(
                    "OK cloud rejected (missing Mistral key)",
                    ctx={"corr_id": corr_id},
                )
            raise

        entry = record_ok_output(
            prompt=prompt,
            response=response_text,
            model=model,
            source=source,
            mode=ok_mode,
            file_path=str(path),
        )
        logger.info(
            "OK command completed",
            ctx={
                "corr_id": corr_id,
                "mode": ok_mode,
                "model": model,
                "source": source,
                "file": str(path),
            },
        )
        return {
            "status": "ok",
            "command": command,
            "result": {
                "status": "success",
                "message": f"OK {ok_mode} complete",
                "output": response_text,
            },
            "ok": entry,
        }

    prompt = ok_args.strip()
    if not prompt:
        logger.warn("OK command not recognized", ctx={"corr_id": corr_id, "mode": ok_mode})
        raise HTTPException(status_code=400, detail="OK command not recognized")

    model = resolve_ok_model(ok_model, "general")
    try:
        response_text, model, source = run_ok_with_fallback(
            prompt=prompt,
            model=model,
            use_cloud=False,
            auto_fallback=ok_auto_fallback_enabled(),
            run_local=run_ok_local,
            run_cloud=run_ok_cloud,
            cloud_available=ok_cloud_available,
            local_failure_detail="OK prompt failed",
        )
    except HTTPException as exc:
        if exc.status_code == 400:
            logger.warn(
                "OK cloud rejected (missing Mistral key)",
                ctx={"corr_id": corr_id},
            )
        else:
            logger.warn(
                "OK prompt failed",
                ctx={"corr_id": corr_id, "mode": ok_mode},
            )
        raise

    entry = record_ok_output(
        prompt=prompt,
        response=response_text,
        model=model,
        source=source,
        mode="LOCAL",
        file_path=None,
    )
    logger.info(
        "OK prompt completed",
        ctx={"corr_id": corr_id, "model": model, "source": source},
    )
    return {
        "status": "ok",
        "command": command,
        "result": {
            "status": "success",
            "message": "OK prompt complete",
            "output": response_text,
        },
        "ok": entry,
    }
