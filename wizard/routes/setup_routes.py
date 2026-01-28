"""
Setup Routes (Wizard)
=====================

First-time setup wizard endpoints for Wizard server.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Sequence, List

from wizard.services.setup_state import setup_state
from wizard.services.setup_manager import (
    get_full_config_status,
    get_required_variables,
    validate_database_paths,
    get_paths,
    search_locations,
    get_default_location_for_timezone,
)
from wizard.services.setup_profiles import (
    load_user_profile,
    load_install_profile,
    save_user_profile,
    save_install_profile,
    load_install_metrics,
    sync_metrics_from_profile,
    increment_moves,
)

from wizard.services.path_utils import get_repo_root, get_memory_dir
from wizard.services.logging_manager import get_logger
from core.location_service import LocationService
from core.services.story_service import parse_story_document
import json


logger = get_logger("wizard.setup_routes")


class ConfigVariable(BaseModel):
    name: str
    value: str
    description: Optional[str] = None


class UserProfilePayload(BaseModel):
    username: str
    date_of_birth: str
    role: str
    timezone: str
    local_time: str
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None


class InstallProfilePayload(BaseModel):
    installation_id: Optional[str] = None
    os_type: Optional[str] = None
    lifespan_mode: Optional[str] = None
    moves_limit: Optional[int] = None
    capabilities: Optional[Dict[str, bool]] = None
    permissions: Optional[Dict[str, Any]] = None


class StorySubmitPayload(BaseModel):
    answers: Dict[str, Any]


def _get_system_timezone_info() -> Dict[str, str]:
    now = datetime.now().astimezone()
    tzinfo = now.tzinfo or timezone.utc
    tz_name = getattr(tzinfo, "key", None) or tzinfo.tzname(now) or "UTC"
    return {
        "timezone": tz_name,
        "local_time": now.strftime("%Y-%m-%d %H:%M"),
    }


def _collect_timezone_options() -> List[Dict[str, Any]]:
    service = LocationService()
    mapping: Dict[str, Dict[str, Any]] = {}
    for loc in service.get_all_locations():
        tz = str(loc.get("timezone") or "").strip()
        if not tz:
            continue
        label = f"{loc.get('name')} ({loc.get('region', 'global')})"
        candidate = {
            "timezone": tz,
            "label": label,
            "location_id": loc.get("id"),
            "location_name": loc.get("name"),
        }
        existing = mapping.get(tz)
        if not existing or loc.get("type") == "major-city":
            mapping[tz] = candidate
    return sorted(mapping.values(), key=lambda item: item["label"])


def _apply_setup_defaults(
    story_state: Dict[str, Any],
    overrides: Dict[str, Any],
    highlight_fields: Optional[Sequence[str]] = None,
) -> None:
    highlight = set(highlight_fields or [])
    answers = story_state.get("answers") or {}
    for section in story_state.get("sections", []):
        for question in section.get("questions", []):
            if not question:
                continue
            name = question.get("name")
            if not name:
                continue
            if name in overrides and overrides[name] is not None:
                value = overrides[name]
                answers[name] = value
                question["value"] = value
                # Ensure meta is a dict (story parser may set it to None)
                if question.get("meta") is None:
                    question["meta"] = {}
                meta = question["meta"]
                meta["default_value"] = value
                meta["previous_value"] = value
                if name in highlight:
                    meta["show_previous_overlay"] = True
                if name == "user_timezone":
                    meta["options_endpoint"] = "/api/v1/setup/data/timezones"
            elif name in overrides and overrides[name] is None:
                answers.pop(name, None)
    story_state["answers"] = answers


def _apply_capabilities_to_wizard_config(capabilities: Dict[str, bool]) -> None:
    if not capabilities:
        return
    config_path = get_repo_root() / "wizard" / "config" / "wizard.json"
    if not config_path.exists():
        return
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        return
    mapping = {
        "web_proxy": "web_proxy_enabled",
        "gmail_relay": "gmail_relay_enabled",
        "ai_gateway": "ai_gateway_enabled",
        "github_push": "github_push_enabled",
        "notion": "notion_enabled",
        "hubspot": "hubspot_enabled",
        "icloud": "icloud_enabled",
        "plugin_repo": "plugin_repo_enabled",
        "plugin_auto_update": "plugin_auto_update",
    }
    updated = False
    for cap_key, config_key in mapping.items():
        if cap_key in capabilities:
            config[config_key] = bool(capabilities[cap_key])
            updated = True
    if updated:
        config_path.write_text(json.dumps(config, indent=2))


def _validate_location_id(location_id: Optional[str]) -> None:
    if not location_id:
        raise HTTPException(status_code=400, detail="Location must be selected")
    service = LocationService()
    if not service.get_location(location_id):
        raise HTTPException(
            status_code=400,
            detail="Location must be a valid uDOS grid code from the core dataset",
        )


def _resolve_location_name(location_id: str) -> str:
    service = LocationService()
    loc = service.get_location(location_id)
    return loc.get("name") if loc else location_id


def _is_local_request(request: Request) -> bool:
    client_host = request.client.host if request.client else ""
    return client_host in {"127.0.0.1", "::1", "localhost"}


def create_setup_routes(auth_guard=None):
    async def setup_guard(request: Request) -> None:
        if not auth_guard:
            return
        if not setup_state.get_status().get("setup_complete") and _is_local_request(
            request
        ):
            return
        await auth_guard(request)

    dependencies = [Depends(setup_guard)] if auth_guard else []
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

    class StepCompletion(BaseModel):
        step_id: int
        completed: bool = True

    @router.post("/steps/complete")
    async def mark_setup_step_complete(step: StepCompletion):
        try:
            setup_state.mark_step_complete(step.step_id, step.completed)
            return {
                "status": "success",
                "step_id": step.step_id,
                "completed": step.completed,
                "steps_completed": setup_state.get_status().get("steps_completed", []),
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

    @router.get("/profiles")
    async def get_profiles():
        user = load_user_profile()
        install = load_install_profile()
        return {
            "user_profile": user.data,
            "install_profile": install.data,
            "secret_store_locked": user.locked or install.locked,
            "errors": [e for e in [user.error, install.error] if e],
            "install_metrics": load_install_metrics(),
        }

    @router.post("/profile/user")
    async def set_user_profile(payload: UserProfilePayload):
        _validate_location_id(payload.location_id)
        payload_dict = payload.dict()
        payload_dict["location_name"] = _resolve_location_name(payload.location_id)
        result = save_user_profile(payload_dict)
        if result.locked:
            raise HTTPException(status_code=503, detail=result.error or "secret store locked")
        setup_state.mark_variable_configured("user_profile")
        return {"status": "success", "user_profile": result.data}

    @router.post("/profile/install")
    async def set_install_profile(payload: InstallProfilePayload):
        result = save_install_profile(payload.dict())
        if result.locked:
            raise HTTPException(status_code=503, detail=result.error or "secret store locked")
        capabilities = (result.data or {}).get("capabilities") or {}
        _apply_capabilities_to_wizard_config(capabilities)
        metrics = sync_metrics_from_profile(result.data or {})
        setup_state.mark_variable_configured("install_profile")
        return {"status": "success", "install_profile": result.data, "install_metrics": metrics}

    @router.get("/installation/metrics")
    async def get_install_metrics():
        return {"status": "success", "metrics": load_install_metrics()}

    @router.post("/installation/moves")
    async def add_install_move():
        return {"status": "success", "metrics": increment_moves()}

    @router.get("/locations/search")
    async def search_locations_endpoint(query: str = "", timezone: Optional[str] = None, limit: int = 10):
        return {"results": search_locations(query, timezone_hint=timezone, limit=limit)}

    @router.get("/locations/default")
    async def default_location_endpoint(timezone: Optional[str] = None):
        default = get_default_location_for_timezone(timezone)
        return {"result": default}

    @router.get("/data/timezones")
    async def timezone_options_endpoint():
        options = _collect_timezone_options()
        system_tz = _get_system_timezone_info().get("timezone")
        return {"timezones": options, "default_timezone": system_tz}

    @router.post("/story/bootstrap")
    async def bootstrap_setup_story(force: bool = False):
        repo_root = get_repo_root()
        template_path = repo_root / "wizard" / "templates" / "setup-wizard-story.md"
        if not template_path.exists():
            raise HTTPException(status_code=404, detail="Setup story template missing")
        memory_root = get_memory_dir()
        story_dir = memory_root / "story"
        story_dir.mkdir(parents=True, exist_ok=True)
        story_path = story_dir / "wizard-setup-story.md"
        if force or not story_path.exists():
            story_path.write_text(template_path.read_text())
            logger.info("Story template bootstrapped (force=%s)", force)
        return {
            "status": "success",
            "path": story_path.relative_to(memory_root).as_posix(),
            "overwritten": bool(force),
        }

    @router.get("/story/read")
    async def read_setup_story():
        memory_root = get_memory_dir()
        story_path = memory_root / "story" / "wizard-setup-story.md"
        if not story_path.exists():
            bootstrap = await bootstrap_setup_story(force=False)
            story_path = memory_root / bootstrap["path"]
        if not story_path.exists():
            raise HTTPException(status_code=404, detail="Setup story not found")
        raw_content = story_path.read_text()
        
        try:
            story_state = parse_story_document(
                raw_content,
                required_frontmatter_keys=["title", "type", "submit_endpoint"],
            )
        except ValueError as exc:
            logger.error("Story parsing failed: %s", exc, exc_info=True)
            raise HTTPException(status_code=422, detail=str(exc))
        except Exception as exc:
            logger.error("Unexpected error parsing story: %s", exc, exc_info=True)
            raise HTTPException(status_code=500, detail=f"Story parsing error: {exc}")

        system_info = _get_system_timezone_info()
        timezone_options = _collect_timezone_options()
        default_location = get_default_location_for_timezone(system_info["timezone"])
        if not default_location and timezone_options:
            # fallback to a location listed under the timezone options
            match = next(
                (opt for opt in timezone_options if opt["timezone"] == system_info["timezone"]),
                None,
            )
            if match:
                default_location = {
                    "id": match.get("location_id"),
                    "name": match.get("location_name"),
                }

        overrides = {
            "user_timezone": system_info["timezone"],
            "user_local_time": system_info["local_time"],
            "user_location_id": default_location.get("id") if default_location else None,
            "user_location_name": default_location.get("name") if default_location else None,
        }
        
        try:
            _apply_setup_defaults(
                story_state,
                overrides,
                highlight_fields=["user_timezone", "user_local_time"],
            )
        except Exception as exc:
            logger.error("Failed to apply setup defaults: %s", exc, exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to apply defaults: {exc}")
        
        story_state.setdefault("metadata", {})
        story_state["metadata"].update(
            {
                "system_timezone": system_info["timezone"],
                "timezone_options": timezone_options,
                "default_location": default_location,
            }
        )

        logger.debug(
            "Story read: title=%s sections=%d system_tz=%s",
            story_state["frontmatter"].get("title"),
            len(story_state["sections"]),
            system_info["timezone"],
        )
        return {
            "status": "success",
            "story": story_state,
            "content": raw_content,
            "frontmatter": story_state["frontmatter"],
            "body": story_state["body"],
            "path": story_path.relative_to(memory_root).as_posix(),
        }

    @router.post("/story/submit")
    async def submit_setup_story(payload: StorySubmitPayload):
        answers = payload.answers or {}

        user_profile = {
            "username": answers.get("user_username"),
            "date_of_birth": answers.get("user_dob"),
            "role": answers.get("user_role"),
            "timezone": answers.get("user_timezone"),
            "local_time": answers.get("user_local_time"),
            "location_id": answers.get("user_location_id"),
            "location_name": None,
            "permissions": answers.get("user_permissions"),
        }
        _validate_location_id(user_profile.get("location_id"))
        user_profile["location_name"] = _resolve_location_name(
            user_profile.get("location_id")
        )

        install_profile = {
            "installation_id": answers.get("install_id"),
            "os_type": answers.get("install_os_type"),
            "lifespan_mode": answers.get("install_lifespan_mode"),
            "moves_limit": answers.get("install_moves_limit"),
            "permissions": answers.get("install_permissions"),
            "capabilities": {
                "web_proxy": bool(answers.get("capability_web_proxy")),
                "gmail_relay": bool(answers.get("capability_gmail_relay")),
                "ai_gateway": bool(answers.get("capability_ai_gateway")),
                "github_push": bool(answers.get("capability_github_push")),
                "notion": bool(answers.get("capability_notion")),
                "hubspot": bool(answers.get("capability_hubspot")),
                "icloud": bool(answers.get("capability_icloud")),
                "plugin_repo": bool(answers.get("capability_plugin_repo")),
                "plugin_auto_update": bool(answers.get("capability_plugin_auto_update")),
            },
        }

        user_result = save_user_profile(user_profile)
        if user_result.locked:
            raise HTTPException(status_code=503, detail=user_result.error or "secret store locked")

        install_result = save_install_profile(install_profile)
        if install_result.locked:
            raise HTTPException(status_code=503, detail=install_result.error or "secret store locked")

        _apply_capabilities_to_wizard_config((install_result.data or {}).get("capabilities") or {})
        metrics = sync_metrics_from_profile(install_result.data or {})

        return {
            "status": "success",
            "user_profile": user_result.data,
            "install_profile": install_result.data,
            "install_metrics": metrics,
        }

    @router.get("/profile/user")
    async def get_user_profile():
        """Retrieve the stored user profile."""
        result = load_user_profile()
        if result.locked:
            raise HTTPException(status_code=503, detail=result.error or "secret store locked")
        if not result.data:
            raise HTTPException(status_code=404, detail="No user profile found. Please complete setup story first.")
        return {
            "status": "success",
            "profile": result.data,
        }

    @router.get("/profile/install")
    async def get_install_profile():
        """Retrieve the stored installation profile."""
        result = load_install_profile()
        if result.locked:
            raise HTTPException(status_code=503, detail=result.error or "secret store locked")
        if not result.data:
            raise HTTPException(status_code=404, detail="No installation profile found. Please complete setup story first.")
        metrics = load_install_metrics()
        return {
            "status": "success",
            "profile": result.data,
            "metrics": metrics,
        }

    @router.get("/profile/combined")
    async def get_combined_profile():
        """Retrieve both user and installation profiles in a single call."""
        user_result = load_user_profile()
        install_result = load_install_profile()
        
        if user_result.locked or install_result.locked:
            raise HTTPException(
                status_code=503,
                detail=user_result.error or install_result.error or "secret store locked"
            )
        
        metrics = load_install_metrics()
        
        return {
            "status": "success",
            "user_profile": user_result.data,
            "install_profile": install_result.data,
            "install_metrics": metrics,
            "setup_complete": bool(user_result.data and install_result.data),
        }

    return router
