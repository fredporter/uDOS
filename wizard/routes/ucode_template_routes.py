"""Template subroutes for the uCODE bridge."""

from __future__ import annotations

from typing import Any, Callable, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from wizard.routes.ucode_template_dispatch import dispatch_ucode_template_command


class TemplateDuplicateRequest(BaseModel):
    target_name: str | None = None


def create_ucode_template_routes(
    *,
    logger: Any,
    dispatcher: Any,
    new_corr_id: Callable[[str], str],
    set_corr_id: Callable[[str], Any],
    reset_corr_id: Callable[[Any], None],
    dispatch_core: Callable[..., Dict[str, Any]],
) -> APIRouter:
    router = APIRouter(prefix="/templates", tags=["ucode"])

    def _dispatch(command: str) -> Dict[str, Any]:
        corr_id = new_corr_id("C")
        token = set_corr_id(corr_id)
        try:
            logger.info(
                "Template route dispatch",
                ctx={"corr_id": corr_id, "command": command},
            )
            return dispatch_ucode_template_command(
                command=command,
                logger=logger,
                corr_id=corr_id,
            )
        finally:
            reset_corr_id(token)

    @router.get("")
    async def list_template_families() -> Dict[str, Any]:
        return _dispatch("UCODE TEMPLATE LIST")

    @router.get("/{family}")
    async def list_family_templates(family: str) -> Dict[str, Any]:
        return _dispatch(f"UCODE TEMPLATE LIST {family}")

    @router.get("/{family}/{template_name}")
    async def read_template(family: str, template_name: str) -> Dict[str, Any]:
        return _dispatch(f"UCODE TEMPLATE READ {family} {template_name}")

    @router.post("/{family}/{template_name}/duplicate")
    async def duplicate_template(
        family: str,
        template_name: str,
        payload: TemplateDuplicateRequest,
    ) -> Dict[str, Any]:
        command = f"UCODE TEMPLATE DUPLICATE {family} {template_name}"
        if payload.target_name:
            command = f"{command} {payload.target_name}"
        return _dispatch(command)

    return router
