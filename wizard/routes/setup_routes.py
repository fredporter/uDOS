"""
Setup Routes (Wizard)
=====================

First-time setup wizard endpoints for Wizard server.
"""

from fastapi import APIRouter, Depends, Request

from wizard.services.setup_state import setup_state
from core.services.config_sync_service import ConfigSyncManager
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
from wizard.services.ai_profile_service import (
    add_knowledge_entry as _add_ai_knowledge_entry,
    add_quest as _add_ai_quest,
    add_skill as _add_ai_skill,
    load_profile as _load_ai_profile,
    load_template as _load_ai_profile_template,
    render_system_prompt as _render_ai_system_prompt,
    save_profile as _save_ai_profile,
)

from wizard.services.path_utils import get_repo_root, get_memory_dir
from wizard.services.logging_api import get_logger
from wizard.routes.setup_core_routes import create_setup_core_routes
from wizard.routes.setup_location_routes import create_setup_location_routes
from wizard.routes.setup_path_routes import create_setup_path_routes
from wizard.routes.setup_wizard_routes import create_setup_wizard_routes
from core.services.story_service import parse_story_document
from wizard.routes.setup_profile_routes import create_setup_profile_routes
from wizard.routes.setup_story_routes import create_setup_story_routes
from wizard.routes.setup_ai_profile_routes import create_setup_ai_profile_routes
from wizard.routes.setup_route_utils import (
    apply_capabilities_to_wizard_config as _apply_capabilities_to_wizard_config,
    apply_setup_defaults as _apply_setup_defaults,
    collect_timezone_options as _collect_timezone_options,
    get_system_timezone_info as _get_system_timezone_info,
    is_ghost_mode as _is_ghost_mode,
    is_local_request as _is_local_request,
    load_env_identity as _load_env_identity,
    resolve_location_name as _resolve_location_name,
    validate_location_id as _validate_location_id,
)


logger = get_logger("wizard.setup_routes")


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
    router = APIRouter(prefix="/api/setup", tags=["setup"], dependencies=dependencies)

    router.include_router(
        create_setup_core_routes(
            get_full_config_status=get_full_config_status,
            get_status=setup_state.get_status,
            get_required_variables=get_required_variables,
            mark_variable_configured=setup_state.mark_variable_configured,
            mark_step_complete=setup_state.mark_step_complete,
        )
    )

    router.include_router(
        create_setup_wizard_routes(
            get_status=setup_state.get_status,
            mark_setup_complete=setup_state.mark_setup_complete,
            validate_database_paths=validate_database_paths,
            load_user_profile=load_user_profile,
            is_ghost_mode=_is_ghost_mode,
        )
    )

    router.include_router(
        create_setup_path_routes(
            get_paths=get_paths,
        )
    )

    router.include_router(
        create_setup_location_routes(
            search_locations=search_locations,
            get_default_location_for_timezone=get_default_location_for_timezone,
            collect_timezone_options=_collect_timezone_options,
            get_system_timezone_info=_get_system_timezone_info,
        )
    )

    router.include_router(
        create_setup_story_routes(
            logger=logger,
            get_repo_root=get_repo_root,
            get_memory_dir=get_memory_dir,
            parse_story_document=parse_story_document,
            get_default_location_for_timezone=get_default_location_for_timezone,
            get_system_timezone_info=_get_system_timezone_info,
            collect_timezone_options=_collect_timezone_options,
            apply_setup_defaults=_apply_setup_defaults,
            load_env_identity=_load_env_identity,
            load_user_profile=load_user_profile,
            load_install_profile=load_install_profile,
            save_user_profile=save_user_profile,
            save_install_profile=save_install_profile,
            sync_metrics_from_profile=sync_metrics_from_profile,
            apply_capabilities_to_wizard_config=_apply_capabilities_to_wizard_config,
            validate_location_id=_validate_location_id,
            resolve_location_name=_resolve_location_name,
            is_ghost_mode=_is_ghost_mode,
            config_sync_manager_cls=ConfigSyncManager,
        )
    )

    router.include_router(
        create_setup_profile_routes(
            load_user_profile=load_user_profile,
            load_install_profile=load_install_profile,
            save_user_profile=save_user_profile,
            save_install_profile=save_install_profile,
            load_install_metrics=load_install_metrics,
            sync_metrics_from_profile=sync_metrics_from_profile,
            increment_moves=increment_moves,
            mark_variable_configured=setup_state.mark_variable_configured,
            apply_capabilities_to_wizard_config=_apply_capabilities_to_wizard_config,
            validate_location_id=_validate_location_id,
            resolve_location_name=_resolve_location_name,
            is_ghost_mode=_is_ghost_mode,
        )
    )

    router.include_router(
        create_setup_ai_profile_routes(
            load_template=_load_ai_profile_template,
            load_profile=_load_ai_profile,
            save_profile=_save_ai_profile,
            add_quest=_add_ai_quest,
            add_skill=_add_ai_skill,
            add_knowledge_entry=_add_ai_knowledge_entry,
            render_system_prompt=_render_ai_system_prompt,
            mark_variable_configured=setup_state.mark_variable_configured,
        )
    )

    return router
