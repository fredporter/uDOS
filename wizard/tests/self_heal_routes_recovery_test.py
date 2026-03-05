from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.self_heal_routes as routes


class _PM:
    def __init__(self):
        self.services = {
            "wizard": SimpleNamespace(
                port=8765,
                process_name="python",
                startup_cmd=["python", "wizard/server.py"],
            ),
            "logic-assist": SimpleNamespace(
                port=None,
                process_name="gpt4all",
                startup_cmd=None,
            ),
        }

    def check_all_services(self):
        return None

    def get_port_occupant(self, port):
        if port == 8765:
            return {"process": "node", "pid": 123}
        return None


class _LogicAssist:
    def __init__(self, local=None, network=None):
        self._local = local or {
            "ready": False,
            "runtime": "gpt4all",
            "package_available": False,
            "model_present": False,
            "model_dir": "/tmp/models",
            "model_path": "/tmp/models/devstral-small-2.gguf",
            "guidance_path": "/tmp/models/README.md",
            "guidance_present": False,
        }
        self._network = network or {
            "ready": False,
            "issue": "no provider configured",
            "available_providers": [],
        }

    def get_status(self):
        return {"local": self._local, "network": self._network}


def _client(monkeypatch, logic=None):
    monkeypatch.setattr(routes, "get_port_manager", lambda: _PM())
    monkeypatch.setattr(
        routes,
        "get_logic_assist_service",
        lambda *_args, **_kwargs: logic or _LogicAssist(),
    )

    app = FastAPI()
    app.include_router(routes.create_self_heal_routes())
    return TestClient(app)


def test_self_heal_strategies(monkeypatch):
    client = _client(monkeypatch)
    res = client.get("/api/self-heal/strategies")
    assert res.status_code == 200
    assert res.json()["count"] >= 3
    assert "quick_recover" in res.json()["strategies"]
    assert "logic_assist_recover" in res.json()["strategies"]


def test_self_heal_recover_dry_run(monkeypatch):
    client = _client(monkeypatch)
    res = client.post(
        "/api/self-heal/recover",
        json={"strategy": "quick_recover", "dry_run": True},
    )
    assert res.status_code == 200
    assert res.json()["summary"]["dry_run"] is True
    assert any(
        action["step"] == "check_logic_assist" for action in res.json()["actions"]
    )


def test_self_heal_recover_with_execution(monkeypatch):
    logic = _LogicAssist(
        local={
            "ready": False,
            "runtime": "gpt4all",
            "package_available": True,
            "model_present": False,
            "model_dir": "/tmp/models",
            "model_path": "/tmp/models/devstral-small-2.gguf",
            "guidance_path": "/tmp/models/README.md",
            "guidance_present": True,
        }
    )
    client = _client(monkeypatch, logic=logic)
    res = client.post(
        "/api/self-heal/recover",
        json={"strategy": "logic_assist_recover", "dry_run": False},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["strategy"] == "logic_assist_recover"
    model_step = [a for a in body["actions"] if a["step"] == "check_model_assets"][0]
    assert model_step["runtime"] == "gpt4all"
    assert model_step["package_available"] is True
    assert model_step["model_present"] is False
    assert model_step["guidance_present"] is True


def test_self_heal_status_reports_next_steps(monkeypatch):
    monkeypatch.setenv("WIZARD_ADMIN_TOKEN", "token")
    logic = _LogicAssist(
        local={
            "ready": False,
            "runtime": "gpt4all",
            "package_available": False,
            "model_present": False,
            "model_dir": "/tmp/models",
            "model_path": "/tmp/models/devstral-small-2.gguf",
            "guidance_path": "/tmp/models/README.md",
            "guidance_present": False,
        }
    )
    client = _client(monkeypatch, logic=logic)
    res = client.get("/api/self-heal/status")
    assert res.status_code == 200
    payload = res.json()
    assert payload["logic_assist"]["runtime"] == "gpt4all"
    assert payload["logic_assist"]["model_present"] is False
    assert any("GPT4All" in step for step in payload["next_steps"])
    assert any("README.md" in step for step in payload["next_steps"])
