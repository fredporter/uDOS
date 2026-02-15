from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.setup_ai_profile_routes import create_setup_ai_profile_routes


def _build_app():
    state = {
        "profile": {
            "profile_name": "uDOS Local AI Profile",
            "user_quests": [],
            "local_skills": [],
            "knowledge_library": [],
        },
        "marked": [],
    }

    def load_template():
        return {"schema_version": "1.3", "profile_name": "Template"}

    def load_profile():
        return state["profile"]

    def save_profile(payload):
        state["profile"] = {**state["profile"], **payload}
        return state["profile"]

    def add_quest(quest):
        state["profile"].setdefault("user_quests", []).append(quest)
        return state["profile"]

    def add_skill(skill):
        state["profile"].setdefault("local_skills", []).append(skill)
        return state["profile"]

    def add_knowledge_entry(entry):
        state["profile"].setdefault("knowledge_library", []).append(entry)
        return state["profile"]

    def render_system_prompt(mode):
        return f"prompt:{mode}"

    app = FastAPI()
    app.include_router(
        create_setup_ai_profile_routes(
            load_template=load_template,
            load_profile=load_profile,
            save_profile=save_profile,
            add_quest=add_quest,
            add_skill=add_skill,
            add_knowledge_entry=add_knowledge_entry,
            render_system_prompt=render_system_prompt,
            mark_variable_configured=lambda key: state["marked"].append(key),
        ),
        prefix="/api/setup",
    )
    return app, state


def test_ai_profile_template_and_get():
    app, _state = _build_app()
    client = TestClient(app)

    res = client.get("/api/setup/ai-profile/template")
    assert res.status_code == 200
    assert res.json()["template"]["schema_version"] == "1.3"

    res = client.get("/api/setup/ai-profile")
    assert res.status_code == 200
    assert res.json()["profile"]["profile_name"] == "uDOS Local AI Profile"


def test_ai_profile_mutation_routes():
    app, state = _build_app()
    client = TestClient(app)

    res = client.post("/api/setup/ai-profile", json={"profile": {"profile_name": "Custom"}})
    assert res.status_code == 200
    assert state["profile"]["profile_name"] == "Custom"
    assert state["marked"] == ["ai_profile"]

    res = client.post("/api/setup/ai-profile/quests", json={"quest": {"id": "q1"}})
    assert res.status_code == 200
    assert state["profile"]["user_quests"][0]["id"] == "q1"

    res = client.post("/api/setup/ai-profile/skills", json={"skill": {"id": "s1"}})
    assert res.status_code == 200
    assert state["profile"]["local_skills"][0]["id"] == "s1"

    res = client.post("/api/setup/ai-profile/knowledge", json={"entry": {"id": "k1"}})
    assert res.status_code == 200
    assert state["profile"]["knowledge_library"][0]["id"] == "k1"

    res = client.get("/api/setup/ai-profile/system-prompt?mode=coding")
    assert res.status_code == 200
    assert res.json()["system_prompt"] == "prompt:coding"
