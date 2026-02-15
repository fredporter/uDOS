"""Core setup status/configuration subroutes."""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class ConfigVariable(BaseModel):
    name: str
    value: str
    description: Optional[str] = None


class StepCompletion(BaseModel):
    step_id: int
    completed: bool = True


def create_setup_core_routes(
    *,
    get_full_config_status: Callable[[], Dict[str, Any]],
    get_status: Callable[[], Dict[str, Any]],
    get_required_variables: Callable[[], Dict[str, Dict[str, Any]]],
    mark_variable_configured: Callable[[str], None],
    mark_step_complete: Callable[[int, bool], None],
) -> APIRouter:
    router = APIRouter(tags=["setup"])

    @router.get("/status")
    async def get_setup_status():
        return get_full_config_status()

    @router.get("/progress")
    async def get_setup_progress():
        status = get_status()
        variables = get_required_variables()
        configured_count = len(status.get("variables_configured", []))
        total_required = sum(1 for v in variables.values() if v.get("required", False))
        return {
            "setup_complete": status.get("setup_complete", False),
            "initialized_at": status.get("initialized_at"),
            "progress_percent": int((configured_count / max(total_required, 1)) * 100)
            if total_required > 0
            else 0,
            "variables_configured": configured_count,
            "services_enabled": len(status.get("services_enabled", [])),
            "required_variables": total_required,
            "steps_completed": status.get("steps_completed", []),
            "steps_completed_count": len(status.get("steps_completed", [])),
            "configured_variables": variables,
        }

    @router.get("/required-variables")
    async def get_setup_variables():
        return {
            "variables": get_required_variables(),
            "instructions": {
                "github": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token",
                "mistral": "https://docs.mistral.ai/",
            },
        }

    @router.post("/configure")
    async def update_config(variable: ConfigVariable):
        try:
            os.environ[variable.name.upper()] = variable.value
            mark_variable_configured(variable.name)
            return {
                "status": "success",
                "variable": variable.name,
                "message": f"Configuration updated: {variable.name}",
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/steps/complete")
    async def mark_setup_step_complete(step: StepCompletion):
        try:
            mark_step_complete(step.step_id, step.completed)
            return {
                "status": "success",
                "step_id": step.step_id,
                "completed": step.completed,
                "steps_completed": get_status().get("steps_completed", []),
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
