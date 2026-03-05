from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.library_routes as library_routes


class _Result(SimpleNamespace):
    pass


class _Manager:
    def __init__(self):
        self.integration = SimpleNamespace(
            name="sonic-screwdriver",
            path="/tmp/sonic",
            source="library",
            has_container=True,
            version="1.0.0",
            description="Sonic",
            installed=False,
            enabled=False,
            can_install=True,
            container_type=None,
            git_cloned=False,
            git_source=None,
            git_ref=None,
            is_running=False,
        )
        self.last_action_name = None

    def get_library_status(self):
        return SimpleNamespace(integrations=[self.integration])

    def get_integration(self, name):
        if name in {"sonic", "sonic-screwdriver"}:
            return self.integration
        return None

    def install_integration(self, name):
        self.last_action_name = name
        return _Result(success=True, plugin_name=name, action="install", message="ok", error=None, steps=[])

    def enable_integration(self, name):
        self.last_action_name = name
        return _Result(success=True, plugin_name=name, action="enable", message="ok", error=None)

    def disable_integration(self, name):
        self.last_action_name = name
        return _Result(success=True, plugin_name=name, action="disable", message="ok", error=None)

    def uninstall_integration(self, name):
        self.last_action_name = name
        return _Result(success=True, plugin_name=name, action="uninstall", message="ok", error=None)



def _client(monkeypatch):
    manager = _Manager()
    monkeypatch.setattr(library_routes, "get_library_manager", lambda: manager)
    monkeypatch.setattr(library_routes, "load_manifest", lambda _path: {"id": "sonic-screwdriver", "version": "1.0.0"})
    monkeypatch.setattr(library_routes, "validate_manifest", lambda *_args, **_kwargs: {"valid": True, "issues": []})
    monkeypatch.setattr(library_routes, "_generate_prompt_payload", lambda *_args, **_kwargs: {"instruction": {"id": "x"}})
    monkeypatch.setattr(library_routes, "log_plugin_install_event", lambda *_args, **_kwargs: None)

    app = FastAPI()
    app.include_router(library_routes.router)
    return TestClient(app), manager


def test_sonic_library_alias_routes_are_removed(monkeypatch):
    monkeypatch.delenv("UDOS_SONIC_ENABLE_LIBRARY_ALIAS", raising=False)
    client, manager = _client(monkeypatch)

    alias_status = client.get("/api/library/aliases/status")
    assert alias_status.status_code == 404

    status_res = client.get("/api/library/integration/sonic")
    assert status_res.status_code == 404

    canonical = client.get("/api/library/integration/sonic-screwdriver")
    assert canonical.status_code == 200
    assert canonical.json()["integration"]["name"] == "sonic-screwdriver"
    assert manager.last_action_name is None


def test_sonic_library_alias_ignores_compatibility_override(monkeypatch):
    monkeypatch.setenv("UDOS_SONIC_ENABLE_LIBRARY_ALIAS", "1")
    client, _manager = _client(monkeypatch)

    alias_status = client.get("/api/library/aliases/status")
    assert alias_status.status_code == 404

    status_res = client.get("/api/library/integration/sonic")
    assert status_res.status_code == 404
