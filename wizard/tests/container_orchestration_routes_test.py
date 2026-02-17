from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.container_launcher_routes as routes


class _Orchestrator:
    def __init__(self):
        self.up_calls = []
        self.down_calls = []

    def up(self, profiles=None, build=False, detach=True):
        self.up_calls.append({"profiles": profiles or [], "build": build, "detach": detach})
        return {"success": True, "profiles": profiles or [], "command": ["docker", "compose", "up"]}

    def down(self, profiles=None, remove_orphans=True):
        self.down_calls.append({"profiles": profiles or [], "remove_orphans": remove_orphans})
        return {"success": True, "profiles": profiles or [], "command": ["docker", "compose", "down"]}

    def status(self):
        return {
            "success": True,
            "docker_available": True,
            "profiles": ["all", "groovebox", "homeassistant", "scheduler"],
            "running_services": ["wizard"],
        }


def _client(monkeypatch):
    orchestrator = _Orchestrator()
    monkeypatch.setattr(routes, "get_orchestrator", lambda: orchestrator)
    app = FastAPI()
    app.include_router(routes.router)
    return TestClient(app), orchestrator


def test_compose_up_down_status_routes(monkeypatch):
    client, orchestrator = _client(monkeypatch)

    up = client.post("/api/containers/compose/up", json={"profiles": ["scheduler"], "build": True})
    assert up.status_code == 200
    assert up.json()["success"] is True
    assert orchestrator.up_calls[0]["profiles"] == ["scheduler"]
    assert orchestrator.up_calls[0]["build"] is True

    down = client.post("/api/containers/compose/down", json={"profiles": ["scheduler"]})
    assert down.status_code == 200
    assert down.json()["success"] is True
    assert orchestrator.down_calls[0]["profiles"] == ["scheduler"]

    status = client.get("/api/containers/compose/status")
    assert status.status_code == 200
    assert status.json()["docker_available"] is True
    assert status.json()["running_services"] == ["wizard"]


def test_orchestrator_rejects_invalid_profiles(tmp_path):
    orchestrator = routes.ComposeOrchestrator(repo_root=tmp_path)
    try:
        orchestrator._normalize_profiles(["invalid"])
        assert False, "Expected invalid profile rejection"
    except Exception as exc:
        assert "Invalid compose profiles" in str(exc)
