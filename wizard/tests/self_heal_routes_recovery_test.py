from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.self_heal_routes as routes


class _PM:
    def __init__(self):
        self.services = {
            "wizard": SimpleNamespace(port=8765, process_name="python", startup_cmd=["python", "wizard/server.py"]),
            "ollama": SimpleNamespace(port=11434, process_name="ollama", startup_cmd=["ollama", "serve"]),
        }

    def check_all_services(self):
        return None

    def get_port_occupant(self, port):
        if port == 8765:
            return {"process": "node", "pid": 123}
        return None


def _client(monkeypatch):
    monkeypatch.setattr(routes, "get_port_manager", lambda: _PM())
    monkeypatch.setattr(routes, "_ollama_models", lambda: ["mistral:latest"])
    monkeypatch.setattr(routes, "_ensure_ollama_running", lambda: {"started": True, "method": "ollama-serve"})

    app = FastAPI()
    app.include_router(routes.create_self_heal_routes())
    return TestClient(app)


def test_self_heal_strategies(monkeypatch):
    client = _client(monkeypatch)
    res = client.get("/api/self-heal/strategies")
    assert res.status_code == 200
    assert res.json()["count"] >= 3
    assert "quick_recover" in res.json()["strategies"]


def test_self_heal_recover_dry_run(monkeypatch):
    client = _client(monkeypatch)
    res = client.post("/api/self-heal/recover", json={"strategy": "quick_recover", "dry_run": True})
    assert res.status_code == 200
    assert res.json()["summary"]["dry_run"] is True
    assert any(action["step"] == "check_ollama" for action in res.json()["actions"])


def test_self_heal_recover_with_execution(monkeypatch):
    client = _client(monkeypatch)
    res = client.post("/api/self-heal/recover", json={"strategy": "ollama_recover", "dry_run": False})
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["strategy"] == "ollama_recover"
    model_step = [a for a in body["actions"] if a["step"] == "check_models"][0]
    assert "devstral-small-2" in model_step["missing"]
