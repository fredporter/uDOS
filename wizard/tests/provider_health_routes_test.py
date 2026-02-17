from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.provider_routes as provider_routes


class _StubProviderHealthService:
    def get_summary(self, auto_check_if_stale=True, stale_seconds=300):
        return {
            "checked_at": "2026-02-17T00:00:00Z",
            "total": 2,
            "healthy": 1,
            "degraded": 1,
            "checks": [
                {"provider_id": "ollama", "available": True, "status": "healthy"},
                {"provider_id": "openai", "available": False, "status": "degraded"},
            ],
        }

    def run_checks(self):
        return self.get_summary()

    def get_history(self, limit=20):
        return {"count": 1, "history": [self.get_summary()]}


def _client(monkeypatch):
    monkeypatch.setattr(
        provider_routes,
        "get_provider_health_service",
        lambda: _StubProviderHealthService(),
    )
    app = FastAPI()
    app.include_router(provider_routes.create_provider_routes(auth_guard=None))
    return TestClient(app)


def test_provider_health_monitoring_routes(monkeypatch):
    client = _client(monkeypatch)

    summary = client.get("/api/providers/health/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["success"] is True
    assert payload["summary"]["total"] == 2

    check = client.post("/api/providers/health/check")
    assert check.status_code == 200
    assert check.json()["success"] is True
    assert check.json()["snapshot"]["healthy"] == 1

    history = client.get("/api/providers/health/history?limit=10")
    assert history.status_code == 200
    assert history.json()["success"] is True
    assert history.json()["count"] == 1
