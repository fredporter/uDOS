"""uCODE Bridge Routes
===================

Expose a minimal, allowlisted uCODE command dispatch endpoint for the Dev Mode tool lane and MCP.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from core.services.logging_api import reset_corr_id, set_corr_id
from core.services.path_service import get_repo_root
from core.services.unified_config_loader import get_bool_config, get_config
from wizard.routes.command_capability_utils import (
    check_command_capabilities,
    detect_wizard_capabilities,
    load_wizard_required_commands,
)
from wizard.routes.ucode_contract_utils import (
    load_ucode_allowlist_from_contract,
)
from wizard.routes.ucode_dispatch_routes import (
    DispatchRequest,
    create_ucode_dispatch_routes,
)
from wizard.routes.ucode_dispatch_utils import (
    dispatch_non_ok_command,
    handle_slash_command,
)
from wizard.routes.ucode_meta_routes import create_ucode_meta_routes
from wizard.routes.ucode_ok_dispatch_core import dispatch_ok_command
from wizard.routes.ucode_logic_mode_utils import (
    get_logic_context_window as _get_logic_context_window,
    get_logic_default_model as _get_logic_default_model,
    get_logic_default_models as _get_logic_default_models,
    get_logic_local_status as _get_logic_local_status,
    get_logic_network_status as _get_logic_network_status,
    is_dev_mode_active as _is_dev_mode_active,
    load_logic_modes_config as _load_logic_modes_config,
    logic_auto_fallback_enabled as _logic_auto_fallback_enabled,
    resolve_logic_model as _resolve_logic_model,
    write_logic_default_model as _write_logic_default_model,
    write_logic_modes_config as _write_logic_modes_config,
)
from wizard.routes.ucode_logic_routes import create_ucode_logic_routes
from wizard.routes.ucode_ok_stream_dispatch import dispatch_ok_stream_command
from wizard.routes.ucode_command_utils import shell_safe
from wizard.routes.ucode_setup_story_utils import load_setup_story as _load_setup_story
from wizard.routes.ucode_template_routes import create_ucode_template_routes
from wizard.routes.ucode_user_routes import create_ucode_user_routes
from wizard.services.logging_api import get_logger, new_corr_id


def _build_local_logic_assist(profile, model: str | None = None):
    from wizard.services.local_model_gpt4all import GPT4AllLocalAssist
    from wizard.services.logic_assist_profile import load_logic_assist_profile

    resolved_profile = profile or load_logic_assist_profile()
    if model:
        payload = resolved_profile.to_dict()
        payload["local_model_name"] = model
        resolved_profile = resolved_profile.__class__(**payload)
    return GPT4AllLocalAssist(resolved_profile, get_repo_root())


def _default_allowlist() -> set[str]:
    base = set(load_ucode_allowlist_from_contract())
    try:
        from core.input.command_prompt import create_default_registry

        registry = create_default_registry()
        # Contract is authoritative: only keep commands present in contract.
        registry_names = {cmd.name.upper() for cmd in registry.list_all()}
        base.intersection_update(registry_names)
    except Exception:
        pass
    return base


def _load_allowlist() -> set[str]:
    raw = get_config("UCODE_API_ALLOWLIST", "").strip()
    if not raw:
        return _default_allowlist()
    return {item.strip().upper() for item in raw.split(",") if item.strip()}


def _shell_allowed() -> bool:
    return get_bool_config("UCODE_API_ALLOW_SHELL", False)


def create_ucode_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/ucode", tags=["ucode"], dependencies=dependencies)
    logger = get_logger("wizard", category="ucode", name="ucode")

    allowlist = _load_allowlist()
    wizard_required_commands = load_wizard_required_commands()
    ok_history: list[dict[str, Any]] = []
    ok_counter = 0
    ok_limit = 50

    def _command_capabilities() -> dict[str, bool]:
        return detect_wizard_capabilities()

    def _check_command_capability(
        command_name: str,
    ) -> tuple[bool, str | None, list[str]]:
        capabilities = _command_capabilities()
        return check_command_capabilities(
            command_name, wizard_required_commands, capabilities
        )

    router.include_router(
        create_ucode_meta_routes(
            allowlist,
            wizard_required_commands=wizard_required_commands,
            get_capabilities=_command_capabilities,
        )
    )
    router.include_router(create_ucode_user_routes(logger=logger))

    def _run_ok_cloud(prompt: str) -> tuple[str, str]:
        from wizard.services.cloud_provider_executor import run_cloud_with_fallback

        return run_cloud_with_fallback(prompt)

    def _run_ok_local(prompt: str, model: str | None = None) -> str:
        from wizard.services.ok_profile_service import render_system_prompt
        from wizard.services.logic_assist_profile import load_logic_assist_profile

        prompt_upper = (prompt or "").strip().upper()
        mode = (
            "coding"
            if (
                prompt_upper.startswith("EXPLAIN THIS CODE FROM")
                or prompt_upper.startswith("PROPOSE A UNIFIED DIFF")
                or prompt_upper.startswith("DRAFT A PATCH")
            )
            else "general"
        )
        profile = load_logic_assist_profile()
        local_assist = _build_local_logic_assist(profile, model=model)
        return local_assist.generate(prompt, system=render_system_prompt(mode))

    def _ok_cloud_available() -> bool:
        from wizard.services.cloud_provider_executor import get_cloud_availability

        return get_cloud_availability()["ready"]

    def _run_ok_local_stream(prompt: str, model: str):
        raise RuntimeError("Streaming local assist is unavailable in the v1.5 GPT4All lane")

    router.include_router(
        create_ucode_logic_routes(
            logger=logger,
            logic_history=ok_history,
            get_logic_local_status=_get_logic_local_status,
            get_logic_network_status=_get_logic_network_status,
            get_logic_context_window=_get_logic_context_window,
            get_logic_default_models=_get_logic_default_models,
            get_logic_default_model=_get_logic_default_model,
            is_dev_mode_active=_is_dev_mode_active,
            logic_auto_fallback_enabled=_logic_auto_fallback_enabled,
            write_logic_default_model=_write_logic_default_model,
            run_logic_network=_run_ok_cloud,
        )
    )

    def _record_ok_output(
        prompt: str,
        response: str,
        model: str,
        source: str,
        mode: str,
        file_path: str | None = None,
    ) -> dict[str, Any]:
        nonlocal ok_counter
        ok_counter += 1
        entry = {
            "id": ok_counter,
            "mode": mode,
            "prompt": prompt,
            "response": response,
            "model": model,
            "source": source,
            "file_path": file_path,
            "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        ok_history.append(entry)
        if len(ok_history) > ok_limit:
            ok_history[:] = ok_history[-ok_limit:]
        return entry

    # Lazy imports to keep wizard usable without core in some deployments.
    try:
        from core.tui.dispatcher import CommandDispatcher
        from core.tui.renderer import GridRenderer
        from core.tui.state import GameState

        dispatcher = CommandDispatcher()
        game_state = GameState()
        renderer = GridRenderer()
    except Exception:  # pragma: no cover
        dispatcher = None
        game_state = None
        renderer = None

    def _dispatch_core(
        command: str, payload: DispatchRequest, corr_id: str
    ) -> dict[str, Any]:
        if not command:
            logger.warn("Empty command rejected", ctx={"corr_id": corr_id})
            raise HTTPException(status_code=400, detail="command is required")

        ok_response = dispatch_ok_command(
            command=command,
            corr_id=corr_id,
            logger=logger,
            ok_history=ok_history,
            ok_model=payload.ok_model,
            load_ok_modes_config=_load_logic_modes_config,
            write_ok_modes_config=_write_logic_modes_config,
            ok_auto_fallback_enabled=_logic_auto_fallback_enabled,
            get_ok_default_model=_get_logic_default_model,
            run_ok_local=_run_ok_local,
            run_ok_cloud=_run_ok_cloud,
            ok_cloud_available=_ok_cloud_available,
            record_ok_output=_record_ok_output,
            is_dev_mode_active=_is_dev_mode_active,
            resolve_ok_model=_resolve_logic_model,
        )
        if ok_response is not None:
            return ok_response

        command, shell_response = handle_slash_command(
            command=command,
            allowlist=allowlist,
            shell_allowed=_shell_allowed,
            shell_safe=shell_safe,
            logger=logger,
            corr_id=corr_id,
        )
        if shell_response is not None:
            return shell_response

        return dispatch_non_ok_command(
            command=command,
            allowlist=allowlist,
            dispatcher=dispatcher,
            game_state=game_state,
            renderer=renderer,
            load_setup_story=_load_setup_story,
            logger=logger,
            corr_id=corr_id,
            command_capability_check=_check_command_capability,
        )

    router.include_router(
        create_ucode_dispatch_routes(
            logger=logger,
            dispatcher=dispatcher,
            new_corr_id=new_corr_id,
            set_corr_id=set_corr_id,
            reset_corr_id=reset_corr_id,
            dispatch_core=_dispatch_core,
            dispatch_ok_stream_command=dispatch_ok_stream_command,
            is_dev_mode_active=_is_dev_mode_active,
            resolve_ok_model=_resolve_logic_model,
            ok_auto_fallback_enabled=_logic_auto_fallback_enabled,
            run_ok_local_stream=_run_ok_local_stream,
            run_ok_cloud=_run_ok_cloud,
            ok_cloud_available=_ok_cloud_available,
            record_ok_output=_record_ok_output,
        )
    )
    router.include_router(
        create_ucode_template_routes(
            logger=logger,
            dispatcher=dispatcher,
            new_corr_id=new_corr_id,
            set_corr_id=set_corr_id,
            reset_corr_id=reset_corr_id,
            dispatch_core=_dispatch_core,
        )
    )

    return router
