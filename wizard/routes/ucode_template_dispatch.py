"""Shared uCODE template command dispatch helpers for Wizard routes."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import HTTPException

from wizard.routes.ucode_dispatch_utils import dispatch_non_ok_command


@lru_cache(maxsize=1)
def _get_dispatch_runtime() -> tuple[Any, Any]:
    from core.tui.dispatcher import CommandDispatcher
    from core.tui.state import GameState

    return CommandDispatcher(), GameState()


def dispatch_ucode_template_command(
    *,
    command: str,
    logger: Any,
    corr_id: str,
) -> dict[str, Any]:
    try:
        dispatcher, game_state = _get_dispatch_runtime()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="uCODE dispatcher unavailable") from exc

    return dispatch_non_ok_command(
        command=command,
        allowlist={"UCODE"},
        dispatcher=dispatcher,
        game_state=game_state,
        renderer=None,
        load_setup_story=lambda: {},
        logger=logger,
        corr_id=corr_id,
        command_capability_check=None,
    )


def list_template_families(*, logger: Any, corr_id: str) -> dict[str, Any]:
    return dispatch_ucode_template_command(
        command="UCODE TEMPLATE LIST",
        logger=logger,
        corr_id=corr_id,
    )


def list_family_templates(*, family: str, logger: Any, corr_id: str) -> dict[str, Any]:
    return dispatch_ucode_template_command(
        command=f"UCODE TEMPLATE LIST {family}",
        logger=logger,
        corr_id=corr_id,
    )


def read_template(*, family: str, template_name: str, logger: Any, corr_id: str) -> dict[str, Any]:
    return dispatch_ucode_template_command(
        command=f"UCODE TEMPLATE READ {family} {template_name}",
        logger=logger,
        corr_id=corr_id,
    )


def duplicate_template(
    *,
    family: str,
    template_name: str,
    logger: Any,
    corr_id: str,
    target_name: str | None = None,
) -> dict[str, Any]:
    command = f"UCODE TEMPLATE DUPLICATE {family} {template_name}"
    if target_name:
        command = f"{command} {target_name}"
    return dispatch_ucode_template_command(
        command=command,
        logger=logger,
        corr_id=corr_id,
    )
