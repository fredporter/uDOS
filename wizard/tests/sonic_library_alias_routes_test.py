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
        return _Result(success=True, plugin_name=name, action="install", message="ok", error=None)

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


def test_sonic_library_routes_resolve_alias(monkeypatch):
    client, manager = _client(monkeypatch)

    status_res = client.get("/api/library/integration/sonic")
    assert status_res.status_code == 200
    assert status_res.json()["integration"]["name"] == "sonic-screwdriver"

    install_res = client.post("/api/library/integration/sonic/install")
    assert install_res.status_code == 200
    assert install_res.json()["result"]["plugin_name"] == "sonic-screwdriver"

    enable_res = client.post("/api/library/integration/sonic/enable")
    assert enable_res.status_code == 200
    assert enable_res.json()["result"]["plugin_name"] == "sonic-screwdriver"

    disable_res = client.post("/api/library/integration/sonic/disable")
    assert disable_res.status_code == 200
    assert disable_res.json()["result"]["plugin_name"] == "sonic-screwdriver"

    uninstall_res = client.delete("/api/library/integration/sonic")
    assert uninstall_res.status_code == 200
    assert uninstall_res.json()["result"]["plugin_name"] == "sonic-screwdriver"

    assert manager.last_action_name == "sonic-screwdriver"
