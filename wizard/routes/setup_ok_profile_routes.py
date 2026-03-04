"""OK profile scaffold routes for setup/Wizard GUI."""

from __future__ import annotations

from typing import Any, Callable, Dict

from fastapi import APIRouter
from pydantic import BaseModel


class OKProfilePayload(BaseModel):
    profile: Dict[str, Any]


class OKQuestPayload(BaseModel):
    quest: Dict[str, Any]


class OKSkillPayload(BaseModel):
    skill: Dict[str, Any]


class OKKnowledgePayload(BaseModel):
    entry: Dict[str, Any]


def create_setup_ok_profile_routes(
    *,
    load_template: Callable[[], Dict[str, Any]],
    load_profile: Callable[[], Dict[str, Any]],
    save_profile: Callable[[Dict[str, Any]], Dict[str, Any]],
    add_quest: Callable[[Dict[str, Any]], Dict[str, Any]],
    add_skill: Callable[[Dict[str, Any]], Dict[str, Any]],
    add_knowledge_entry: Callable[[Dict[str, Any]], Dict[str, Any]],
    render_system_prompt: Callable[[str], str],
    mark_variable_configured: Callable[[str], None],
) -> APIRouter:
    router = APIRouter(tags=["setup"])

    @router.get("/ok-profile/template")
    async def get_ok_profile_template():
        return {"status": "success", "template": load_template()}

    @router.get("/ok-profile")
    async def get_ok_profile():
        return {"status": "success", "profile": load_profile()}

    @router.post("/ok-profile")
    async def set_ok_profile(payload: OKProfilePayload):
        profile = save_profile(payload.profile)
        mark_variable_configured("ok_profile")
        return {"status": "success", "profile": profile}

    @router.post("/ok-profile/quests")
    async def append_ok_quest(payload: OKQuestPayload):
        profile = add_quest(payload.quest)
        return {"status": "success", "profile": profile}

    @router.post("/ok-profile/skills")
    async def append_ok_skill(payload: OKSkillPayload):
        profile = add_skill(payload.skill)
        return {"status": "success", "profile": profile}

    @router.post("/ok-profile/knowledge")
    async def append_ok_knowledge(payload: OKKnowledgePayload):
        profile = add_knowledge_entry(payload.entry)
        return {"status": "success", "profile": profile}

    @router.get("/ok-profile/system-prompt")
    async def get_ok_system_prompt(mode: str = "general"):
        selected_mode = "coding" if (mode or "").strip().lower() == "coding" else "general"
        return {
            "status": "success",
            "mode": selected_mode,
            "system_prompt": render_system_prompt(selected_mode),
        }

    return router
