"""Synchronous logic-assist command dispatch core for uCODE routes."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from fastapi import HTTPException

from wizard.routes.ucode_command_utils import (
    parse_logic_command,
    prepare_logic_coding_request,
)
from wizard.routes.ucode_ok_execution import run_ok_with_fallback


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
    parsed = parse_logic_command(command)
    if parsed is None:
        return None

    command = parsed.command
    ok_args = parsed.logic_args
    ok_tokens = parsed.logic_tokens
    ok_mode = parsed.logic_mode

    if ok_mode in {"LOCAL", "VIBE"}:
        logger.info(
            "Logic local history request",
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
                "message": "LOGIC LOCAL history",
                "output": "",
            },
            "ok_history": entries,
        }

    if ok_mode == "FALLBACK":
        toggle = ok_tokens[1].lower() if len(ok_tokens) > 1 else ""
        config = load_ai_modes_config()
        modes = config.setdefault("modes", {})
        ofvibe = modes.setdefault("logic_assist", {})
        if toggle in {"on", "true", "yes"}:
            ofvibe["auto_fallback"] = True
            write_ok_modes_config(config)
            return {
                "status": "ok",
                "command": command,
                "result": {
                    "status": "success",
                    "message": "LOGIC network fallback set to auto (on)",
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
                    "message": "LOGIC network fallback set to manual (off)",
                    "output": "",
                },
            }
        current = "on" if ok_auto_fallback_enabled() else "off"
        return {
            "status": "ok",
            "command": command,
            "result": {
                "status": "success",
                "message": f"LOGIC network fallback is {current}",
                "output": "Usage: LOGIC FALLBACK on|off",
            },
        }

    if ok_mode in {"EXPLAIN", "DIFF", "PATCH"}:
        coding_request = prepare_logic_coding_request(
            parsed=parsed,
            is_dev_mode_active=is_dev_mode_active,
            logger=logger,
            corr_id=corr_id,
            rejected_log_message="Logic command rejected",
            missing_file_log_message="Logic file missing",
        )
        path = coding_request.path
        prompt = coding_request.prompt

        model = resolve_ok_model(ok_model, "coding")
        try:
            response_text, model, source = run_ok_with_fallback(
                prompt=prompt,
                model=model,
                use_cloud=coding_request.use_cloud,
                auto_fallback=ok_auto_fallback_enabled(),
                run_local=run_ok_local,
                run_cloud=run_ok_cloud,
                cloud_available=ok_cloud_available,
                local_failure_detail="Logic local failed",
            )
        except HTTPException as exc:
            if exc.status_code == 400:
                logger.warn(
                    "Logic network rejected (missing provider key)",
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
            "Logic command completed",
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
                "message": f"LOGIC {ok_mode} complete",
                "output": response_text,
            },
            "ok": entry,
        }

    prompt = ok_args.strip()
    if not prompt:
        logger.warn(
            "Logic command not recognized", ctx={"corr_id": corr_id, "mode": ok_mode}
        )
        raise HTTPException(status_code=400, detail="LOGIC command not recognized")

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
            local_failure_detail="Logic prompt failed",
        )
    except HTTPException as exc:
        if exc.status_code == 400:
            logger.warn(
                "Logic network rejected (missing provider key)",
                ctx={"corr_id": corr_id},
            )
        else:
            logger.warn(
                "Logic prompt failed",
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
        "Logic prompt completed",
        ctx={"corr_id": corr_id, "model": model, "source": source},
    )
    return {
        "status": "ok",
        "command": command,
        "result": {
            "status": "success",
            "message": "LOGIC prompt complete",
            "output": response_text,
        },
        "ok": entry,
    }
