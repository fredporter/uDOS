"""
Setup Routes (Wizard)
=====================

First-time setup wizard endpoints for Wizard server.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any

from wizard.services.setup_state import setup_state
from wizard.services.setup_manager import (
    get_full_config_status,
    get_required_variables,
    validate_database_paths,
    get_paths,
)


class ConfigVariable(BaseModel):
    name: str
    value: str
    description: Optional[str] = None


def create_setup_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/v1/setup", tags=["setup"], dependencies=dependencies)

    @router.get("/status")
    async def get_setup_status():
        return get_full_config_status()

    @router.get("/progress")
    async def get_setup_progress():
        status = setup_state.get_status()
        variables = get_required_variables()
        configured_count = len(status.get("variables_configured", []))
        total_required = sum(1 for v in variables.values() if v.get("required", False))
        return {
            "setup_complete": status.get("setup_complete", False),
            "initialized_at": status.get("initialized_at"),
            "progress_percent": int(
                (configured_count / max(total_required, 1)) * 100
            )
            if total_required > 0
            else 0,
            "variables_configured": configured_count,
            "services_enabled": len(status.get("services_enabled", [])),
            "required_variables": total_required,
            "configured_variables": variables,
        }

    @router.get("/required-variables")
    async def get_setup_variables():
        return {
            "variables": get_required_variables(),
            "instructions": {
                "github": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token",
                "notion": "https://developers.notion.com/docs/getting-started",
                "mistral": "https://docs.mistral.ai/",
                "hubspot": "https://developers.hubspot.com/docs/api/overview",
            },
        }

    @router.post("/configure")
    async def update_config(variable: ConfigVariable):
        try:
            import os

            os.environ[variable.name.upper()] = variable.value
            setup_state.mark_variable_configured(variable.name)
            return {
                "status": "success",
                "variable": variable.name,
                "message": f"Configuration updated: {variable.name}",
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/wizard/start")
    async def start_setup_wizard():
        if setup_state.get_status().get("setup_complete"):
            return {
                "status": "already_complete",
                "message": "Setup has already been completed",
                "initialized_at": setup_state.get_status().get("initialized_at"),
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
                    "name": "Notion Integration",
                    "description": "Configure Notion API access (optional)",
                },
                {
                    "step": 4,
                    "name": "AI Features",
                    "description": "Set up AI/Mistral features (optional)",
                },
                {
                    "step": 5,
                    "name": "HubSpot CRM",
                    "description": "Configure CRM integration (optional)",
                },
                {"step": 6, "name": "Complete", "description": "Finish setup"},
            ],
            "current_progress": setup_state.get_status(),
        }

    @router.post("/wizard/complete")
    async def complete_setup_wizard():
        db_validation = validate_database_paths()
        all_ready = all(db["writable"] for db in db_validation.values())
        if not all_ready:
            raise HTTPException(status_code=400, detail="Database paths not writable")
        setup_state.mark_setup_complete()
        return {
            "status": "complete",
            "message": "Setup wizard completed successfully!",
            "next_steps": [
                "Open Wizard dashboard at /",
                "Check /api/v1/setup/status for configuration overview",
                "Review docs in /docs",
            ],
        }

    @router.get("/paths")
    async def get_path_map():
        return get_paths()

    @router.post("/paths/initialize")
    async def initialize_paths():
        paths = get_paths()
        created = []
        errors = []
        for group in ("data", "installation"):
            for _name, path in paths.get(group, {}).items():
                try:
                    from pathlib import Path

                    Path(path).mkdir(parents=True, exist_ok=True)
                    created.append(path)
                except Exception as exc:
                    errors.append({"path": path, "error": str(exc)})
        return {"status": "complete", "created_directories": created, "errors": errors or None}

    return router
