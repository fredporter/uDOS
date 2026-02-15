"""AI profile scaffold routes for setup/Wizard GUI."""

from __future__ import annotations

from typing import Any, Callable, Dict

from fastapi import APIRouter
from pydantic import BaseModel


class AIProfilePayload(BaseModel):
    profile: Dict[str, Any]


class AIQuestPayload(BaseModel):
    quest: Dict[str, Any]


class AISkillPayload(BaseModel):
    skill: Dict[str, Any]


class AIKnowledgePayload(BaseModel):
    entry: Dict[str, Any]


def create_setup_ai_profile_routes(
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

    @router.get("/ai-profile/template")
    async def get_ai_profile_template():
        return {"status": "success", "template": load_template()}

    @router.get("/ai-profile")
    async def get_ai_profile():
        return {"status": "success", "profile": load_profile()}

    @router.post("/ai-profile")
    async def set_ai_profile(payload: AIProfilePayload):
        profile = save_profile(payload.profile)
        mark_variable_configured("ai_profile")
        return {"status": "success", "profile": profile}

    @router.post("/ai-profile/quests")
    async def append_ai_quest(payload: AIQuestPayload):
        profile = add_quest(payload.quest)
        return {"status": "success", "profile": profile}

    @router.post("/ai-profile/skills")
    async def append_ai_skill(payload: AISkillPayload):
        profile = add_skill(payload.skill)
        return {"status": "success", "profile": profile}

    @router.post("/ai-profile/knowledge")
    async def append_ai_knowledge(payload: AIKnowledgePayload):
        profile = add_knowledge_entry(payload.entry)
        return {"status": "success", "profile": profile}

    @router.get("/ai-profile/system-prompt")
    async def get_ai_system_prompt(mode: str = "general"):
        selected_mode = "coding" if (mode or "").strip().lower() == "coding" else "general"
        return {
            "status": "success",
            "mode": selected_mode,
            "system_prompt": render_system_prompt(selected_mode),
        }

    return router
