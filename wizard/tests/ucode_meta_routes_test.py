import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.ucode_meta_routes import create_ucode_meta_routes


def test_meta_routes_allowlist_and_commands():
    app = FastAPI()
    app.include_router(create_ucode_meta_routes({"HELP", "STATUS"}))
    client = TestClient(app)

    res = client.get("/allowlist")
    assert res.status_code == 200
    assert "HELP" in res.json()["allowlist"]

    res = client.get("/commands")
    assert res.status_code == 200
    assert isinstance(res.json()["commands"], list)


def test_meta_routes_hotkeys_ok():
    app = FastAPI()
    app.include_router(create_ucode_meta_routes({"HELP"}))
    client = TestClient(app)

    res = client.get("/hotkeys")
    assert res.status_code == 200


def test_meta_routes_keymap_get_defaults(monkeypatch):
    monkeypatch.delenv("UDOS_KEYMAP_PROFILE", raising=False)
    monkeypatch.delenv("UDOS_KEYMAP_SELF_HEAL", raising=False)
    monkeypatch.setenv("UDOS_KEYMAP_OS", "linux")

    app = FastAPI()
    app.include_router(create_ucode_meta_routes({"HELP"}))
    client = TestClient(app)

    res = client.get("/keymap")
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "ok"
    assert "linux-default" in payload["available_profiles"]
    assert payload["detected_os"] == "linux"
    assert isinstance(payload["self_heal"], bool)


def test_meta_routes_keymap_update_persists(tmp_path, monkeypatch):
    monkeypatch.delenv("UDOS_KEYMAP_PROFILE", raising=False)
    monkeypatch.delenv("UDOS_KEYMAP_SELF_HEAL", raising=False)
    monkeypatch.delenv("UDOS_KEYMAP_OS", raising=False)

    config_path = tmp_path / "wizard.json"
    app = FastAPI()
    app.include_router(create_ucode_meta_routes({"HELP"}, wizard_config_path=config_path))
    client = TestClient(app)

    res = client.post(
        "/keymap",
        json={
            "profile": "mac-obsidian",
            "self_heal": False,
            "os_override": "mac",
        },
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["active_profile"] == "mac-obsidian"
    assert payload["self_heal"] is False
    assert payload["os_override"] == "mac"

    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["ucode_keymap_profile"] == "mac-obsidian"
    assert data["ucode_keymap_self_heal"] is False
    assert data["ucode_keymap_os"] == "mac"


def test_meta_routes_keymap_update_rejects_invalid_profile():
    app = FastAPI()
    app.include_router(create_ucode_meta_routes({"HELP"}))
    client = TestClient(app)
    res = client.post("/keymap", json={"profile": "bad-profile"})
    assert res.status_code == 422
