"""Wizard lifecycle setup subroutes."""

from __future__ import annotations

from typing import Any, Callable, Dict

from fastapi import APIRouter, HTTPException


def create_setup_wizard_routes(
    *,
    get_status: Callable[[], Dict[str, Any]],
    mark_setup_complete: Callable[[], None],
    validate_database_paths: Callable[[], Dict[str, Dict[str, Any]]],
    load_user_profile: Callable[[], Any],
    is_ghost_mode: Callable[[str, str], bool],
) -> APIRouter:
    router = APIRouter(tags=["setup"])

    @router.post("/wizard/start")
    async def start_setup_wizard():
        status = get_status()
        if status.get("setup_complete"):
            return {
                "status": "already_complete",
                "message": "Setup has already been completed",
                "initialized_at": status.get("initialized_at"),
            }
        return {
            "status": "started",
            "steps": [
                {
                    "step": 1,
                    "name": "Database Setup",
                    "description": "Verify database paths and create directories",
                },
                {
                    "step": 2,
                    "name": "GitHub Integration",
                    "description": "Configure GitHub API access (optional)",
                },
                {
                    "step": 3,
                    "name": "AI Features",
                    "description": "Set up AI/Mistral features (optional)",
                },
                {
                    "step": 4,
                    "name": "HubSpot CRM",
                    "description": "Configure CRM integration (optional)",
                },
                {
                    "step": 5,
                    "name": "Complete",
                    "description": "Finish setup",
                },
            ],
            "current_progress": status,
        }

    @router.post("/wizard/complete")
    async def complete_setup_wizard():
        user_result = load_user_profile()
        if user_result.data and is_ghost_mode(
            user_result.data.get("username"),
            user_result.data.get("role"),
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Ghost Mode is active. Run the setup story to select Admin or User "
                    "and change the username from Ghost to exit Ghost/test mode."
                ),
            )
        db_validation = validate_database_paths()
        all_ready = all(db["writable"] for db in db_validation.values())
        if not all_ready:
            raise HTTPException(status_code=400, detail="Database paths not writable")
        mark_setup_complete()
        return {
            "status": "complete",
            "message": "Setup wizard completed successfully!",
            "next_steps": [
                "Open Wizard dashboard at /",
                "Check /api/setup/status for configuration overview",
                "Review docs in /docs",
            ],
        }

    return router
