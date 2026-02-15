"""Story-related setup subroutes."""

from __future__ import annotations

from typing import Any, Callable, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class StorySubmitPayload(BaseModel):
    answers: Dict[str, Any]


def create_setup_story_routes(
    *,
    logger,
    get_repo_root: Callable[[], Any],
    get_memory_dir: Callable[[], Any],
    parse_story_document: Callable[..., Dict[str, Any]],
    get_default_location_for_timezone: Callable[[str | None], Dict[str, Any] | None],
    get_system_timezone_info: Callable[[], Dict[str, str]],
    collect_timezone_options: Callable[[], list[Dict[str, Any]]],
    apply_setup_defaults: Callable[..., None],
    load_env_identity: Callable[[], Dict[str, Any]],
    load_user_profile: Callable[[], Any],
    load_install_profile: Callable[[], Any],
    save_user_profile: Callable[[Dict[str, Any]], Any],
    save_install_profile: Callable[[Dict[str, Any]], Any],
    sync_metrics_from_profile: Callable[[Dict[str, Any]], Dict[str, Any]],
    apply_capabilities_to_wizard_config: Callable[[Dict[str, bool]], None],
    validate_location_id: Callable[[str | None], None],
    resolve_location_name: Callable[[str], str],
    is_ghost_mode: Callable[[str | None, str | None], bool],
    config_sync_manager_cls,
) -> APIRouter:
    router = APIRouter(tags=["setup"])

    @router.post("/story/bootstrap")
    async def bootstrap_setup_story(force: bool = False):
        repo_root = get_repo_root()
        template_candidates = [
            repo_root / "core" / "tui" / "setup-story.md",
            repo_root / "core" / "framework" / "seed" / "bank" / "system" / "tui-setup-story.md",
            repo_root / "wizard" / "templates" / "tui-setup-story.md",
            # Deprecated (fallback only)
            repo_root / "wizard" / "templates" / "setup-wizard-story.md",
        ]
        template_path = next((p for p in template_candidates if p.exists()), None)
        if not template_path:
            raise HTTPException(status_code=404, detail="Setup story template missing")
        memory_root = get_memory_dir()
        story_dir = memory_root / "story"
        story_dir.mkdir(parents=True, exist_ok=True)
        story_path = story_dir / "tui-setup-story.md"
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
        story_path = memory_root / "story" / "tui-setup-story.md"
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

        system_info = get_system_timezone_info()
        timezone_options = collect_timezone_options()
        default_location = get_default_location_for_timezone(system_info["timezone"])
        if not default_location and timezone_options:
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

        env_identity = load_env_identity()
        if env_identity:
            overrides.update(env_identity)
            logger.debug("[SETUP] Loaded identity from .env: %s", list(env_identity.keys()))

        user_result = load_user_profile()
        install_result = load_install_profile()
        if user_result.data:
            overrides.update(
                {
                    "user_username": user_result.data.get("username"),
                    "user_dob": user_result.data.get("date_of_birth"),
                    "user_role": user_result.data.get("role"),
                    "user_permissions": user_result.data.get("permissions"),
                    "user_timezone": user_result.data.get("timezone") or overrides.get("user_timezone"),
                    "user_local_time": user_result.data.get("local_time") or overrides.get("user_local_time"),
                    "user_location_id": user_result.data.get("location_id") or overrides.get("user_location_id"),
                    "user_location_name": user_result.data.get("location_name") or overrides.get("user_location_name"),
                }
            )
        if install_result.data:
            overrides.update(
                {
                    "install_id": install_result.data.get("installation_id"),
                    "install_os_type": install_result.data.get("os_type"),
                    "install_lifespan_mode": install_result.data.get("lifespan_mode"),
                    "install_moves_limit": install_result.data.get("moves_limit"),
                    "install_permissions": install_result.data.get("permissions"),
                }
            )
            capabilities = install_result.data.get("capabilities") or {}
            overrides.update(
                {
                    "capability_web_proxy": capabilities.get("web_proxy"),
                    "capability_ok_gateway": capabilities.get("ok_gateway"),
                    "capability_github_push": capabilities.get("github_push"),
                    "capability_icloud": capabilities.get("icloud"),
                    "capability_plugin_repo": capabilities.get("plugin_repo"),
                    "capability_plugin_auto_update": capabilities.get("plugin_auto_update"),
                }
            )

        try:
            apply_setup_defaults(
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

        username = answers.get("user_username")
        if username:
            username = username.lower()

        user_profile = {
            "username": username,
            "date_of_birth": answers.get("user_dob"),
            "role": answers.get("user_role"),
            "timezone": answers.get("user_timezone"),
            "local_time": answers.get("user_local_time"),
            "location_id": answers.get("user_location_id"),
            "location_name": None,
            "permissions": answers.get("user_permissions"),
        }
        validate_location_id(user_profile.get("location_id"))
        user_profile["location_name"] = resolve_location_name(user_profile.get("location_id"))
        ghost_mode = is_ghost_mode(user_profile.get("username"), user_profile.get("role"))
        user_profile["ghost_mode"] = ghost_mode

        install_profile = {
            "installation_id": answers.get("install_id"),
            "os_type": answers.get("install_os_type"),
            "lifespan_mode": answers.get("install_lifespan_mode"),
            "moves_limit": answers.get("install_moves_limit"),
            "permissions": answers.get("install_permissions"),
            "capabilities": {
                "web_proxy": bool(answers.get("capability_web_proxy")),
                "ok_gateway": bool(answers.get("capability_ok_gateway")),
                "github_push": bool(answers.get("capability_github_push")),
                "icloud": bool(answers.get("capability_icloud")),
                "plugin_repo": bool(answers.get("capability_plugin_repo")),
                "plugin_auto_update": bool(answers.get("capability_plugin_auto_update")),
            },
            "ghost_mode": ghost_mode,
        }

        user_result = save_user_profile(user_profile)
        if user_result.locked:
            raise HTTPException(status_code=503, detail=user_result.error or "secret store locked")

        install_result = save_install_profile(install_profile)
        if install_result.locked:
            raise HTTPException(status_code=503, detail=install_result.error or "secret store locked")

        apply_capabilities_to_wizard_config((install_result.data or {}).get("capabilities") or {})
        metrics = sync_metrics_from_profile(install_result.data or {})

        sync_manager = config_sync_manager_cls()
        env_payload = {
            "user_username": user_profile.get("username"),
            "user_dob": user_profile.get("date_of_birth"),
            "user_role": user_profile.get("role"),
            "user_password": answers.get("user_password"),
            "user_timezone": user_profile.get("timezone"),
            "user_location": user_profile.get("location_name")
            or answers.get("user_location_name")
            or answers.get("user_location_id"),
            "install_os_type": install_profile.get("os_type"),
        }
        env_ok, env_msg = sync_manager.save_identity_to_env(env_payload)

        return {
            "status": "success",
            "user_profile": user_result.data,
            "install_profile": install_result.data,
            "install_metrics": metrics,
            "env_sync": {"success": env_ok, "message": env_msg},
        }

    return router
