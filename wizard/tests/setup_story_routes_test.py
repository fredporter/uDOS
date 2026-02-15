from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.setup_story_routes import create_setup_story_routes


def _result(data=None, locked=False, error=None):
    return SimpleNamespace(data=data, locked=locked, error=error)


def _build_app(**overrides):
    calls = overrides.setdefault("calls", {})

    def save_user_profile(payload):
        calls["saved_user"] = payload
        return _result(data=payload)

    def save_install_profile(payload):
        calls["saved_install"] = payload
        return _result(data=payload)

    class SyncManager:
        def save_identity_to_env(self, payload):
            calls["env_payload"] = payload
            return True, "ok"

    router = create_setup_story_routes(
        logger=overrides.get("logger", SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None, debug=lambda *a, **k: None)),
        get_repo_root=overrides.get("get_repo_root", lambda: overrides["repo_root"]),
        get_memory_dir=overrides.get("get_memory_dir", lambda: overrides["memory_root"]),
        parse_story_document=overrides.get(
            "parse_story_document",
            lambda raw_content, required_frontmatter_keys=None: {
                "frontmatter": {"title": "Setup", "type": "wizard", "submit_endpoint": "/api/setup/story/submit"},
                "sections": [],
                "answers": {},
                "body": raw_content,
            },
        ),
        get_default_location_for_timezone=overrides.get(
            "get_default_location_for_timezone",
            lambda timezone: {"id": "LOC-1", "name": "Default City"},
        ),
        get_system_timezone_info=overrides.get(
            "get_system_timezone_info",
            lambda: {"timezone": "UTC", "local_time": "2026-01-01 10:00"},
        ),
        collect_timezone_options=overrides.get("collect_timezone_options", lambda: []),
        apply_setup_defaults=overrides.get(
            "apply_setup_defaults",
            lambda story_state, defaults, highlight_fields=None: story_state["answers"].update(defaults),
        ),
        load_env_identity=overrides.get("load_env_identity", lambda: {}),
        load_user_profile=overrides.get("load_user_profile", lambda: _result(data=None)),
        load_install_profile=overrides.get("load_install_profile", lambda: _result(data=None)),
        save_user_profile=overrides.get("save_user_profile", save_user_profile),
        save_install_profile=overrides.get("save_install_profile", save_install_profile),
        sync_metrics_from_profile=overrides.get("sync_metrics_from_profile", lambda profile: {"moves_used": 0}),
        apply_capabilities_to_wizard_config=overrides.get(
            "apply_capabilities_to_wizard_config", lambda capabilities: None
        ),
        validate_location_id=overrides.get("validate_location_id", lambda location_id: None),
        resolve_location_name=overrides.get("resolve_location_name", lambda location_id: "Resolved City"),
        is_ghost_mode=overrides.get("is_ghost_mode", lambda username, role: False),
        config_sync_manager_cls=overrides.get("config_sync_manager_cls", SyncManager),
    )

    app = FastAPI()
    app.include_router(router, prefix="/api/setup")
    return app, calls


def test_bootstrap_missing_template_returns_404(tmp_path):
    app, _calls = _build_app(repo_root=tmp_path / "repo", memory_root=tmp_path / "memory")
    client = TestClient(app)

    res = client.post("/api/setup/story/bootstrap")
    assert res.status_code == 404
    assert "template" in res.json()["detail"].lower()


def test_read_story_bootstraps_and_applies_defaults(tmp_path):
    repo_root = tmp_path / "repo"
    memory_root = tmp_path / "memory"
    template_dir = repo_root / "wizard" / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "tui-setup-story.md").write_text("story-body", encoding="utf-8")

    captured = {}

    def apply_setup_defaults(story_state, defaults, highlight_fields=None):
        captured["defaults"] = defaults
        captured["highlight"] = list(highlight_fields or [])
        story_state["answers"].update(defaults)

    app, _calls = _build_app(
        repo_root=repo_root,
        memory_root=memory_root,
        apply_setup_defaults=apply_setup_defaults,
        load_env_identity=lambda: {"user_username": "env-user"},
    )
    client = TestClient(app)

    res = client.get("/api/setup/story/read")
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "success"
    assert payload["story"]["metadata"]["system_timezone"] == "UTC"
    assert "user_timezone" in captured["defaults"]
    assert "user_local_time" in captured["defaults"]
    assert captured["highlight"] == ["user_timezone", "user_local_time"]


def test_submit_story_normalizes_username_and_syncs_env(tmp_path):
    calls = {}

    def validate_location_id(location_id):
        calls["validated_location_id"] = location_id

    def resolve_location_name(location_id):
        calls["resolved_location_id"] = location_id
        return "New York"

    app, default_calls = _build_app(
        repo_root=tmp_path / "repo",
        memory_root=tmp_path / "memory",
        calls=calls,
        validate_location_id=validate_location_id,
        resolve_location_name=resolve_location_name,
        sync_metrics_from_profile=lambda profile: {"moves_used": 1},
    )
    client = TestClient(app)

    res = client.post(
        "/api/setup/story/submit",
        json={
            "answers": {
                "user_username": "ALICE",
                "user_dob": "2000-01-01",
                "user_role": "admin",
                "user_timezone": "UTC",
                "user_local_time": "2026-01-01 10:00",
                "user_location_id": "NYC-001",
                "install_os_type": "macos",
                "capability_web_proxy": True,
            }
        },
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "success"
    assert calls["validated_location_id"] == "NYC-001"
    assert calls["saved_user"]["username"] == "alice"
    assert calls["env_payload"]["user_username"] == "alice"
    assert calls["resolved_location_id"] == "NYC-001"
    assert payload["env_sync"]["success"] is True
    assert default_calls is calls
