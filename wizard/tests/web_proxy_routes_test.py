from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.web_proxy_routes as web_proxy_routes


class _StubProxyService:
    def list_targets(self):
        return {"count": 2, "targets": [{"id": "home-assistant", "port": 8123}, {"id": "songscribe", "port": 3000}]}

    async def proxy_request(self, *, target_id, path, method, headers, body=None):
        if target_id == "missing":
            raise KeyError("Unknown proxy target: missing")
        return {
            "status_code": 200,
            "headers": {"content-type": "application/json"},
            "content": b'{"ok":true}',
            "media_type": "application/json",
            "target_url": f"http://127.0.0.1:1234{path}",
        }


def _client(monkeypatch):
    monkeypatch.setattr(web_proxy_routes, "get_container_reverse_proxy_service", lambda: _StubProxyService())
    app = FastAPI()
    app.include_router(web_proxy_routes.create_web_proxy_routes(auth_guard=None))
    return TestClient(app)


def test_web_proxy_targets_and_proxy(monkeypatch):
    client = _client(monkeypatch)

    targets = client.get("/api/web/proxy/targets")
    assert targets.status_code == 200
    payload = targets.json()
    assert payload["success"] is True
    assert payload["count"] == 2

    proxied = client.get("/api/web/proxy/home-assistant/api")
    assert proxied.status_code == 200
    assert proxied.json()["ok"] is True

    missing = client.get("/api/web/proxy/missing")
    assert missing.status_code == 404
