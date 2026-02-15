from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.publish_routes import create_publish_routes
from wizard.services.publish_service import PublishService


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(create_publish_routes(publish_service=PublishService()))
    return TestClient(app)


def test_publish_capabilities_and_job_lifecycle():
    client = _client()

    caps = client.get("/api/publish/capabilities")
    assert caps.status_code == 200
    payload = caps.json()
    assert payload["publish_routes_enabled"] is True
    assert payload["providers"]["wizard"]["available"] is True

    create_res = client.post(
        "/api/publish/jobs",
        json={
            "source_workspace": "memory/vault",
            "provider": "wizard",
            "options": {"mode": "snapshot"},
        },
    )
    assert create_res.status_code == 200
    job = create_res.json()["job"]
    job_id = job["publish_job_id"]
    manifest_id = job["manifest_id"]

    status_res = client.get(f"/api/publish/jobs/{job_id}")
    assert status_res.status_code == 200
    assert status_res.json()["job"]["publish_job_id"] == job_id

    cancel_res = client.post(f"/api/publish/jobs/{job_id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["job"]["status"] == "cancelled"

    manifest_res = client.get(f"/api/publish/manifests/{manifest_id}")
    assert manifest_res.status_code == 200
    assert manifest_res.json()["manifest"]["publish_job_id"] == job_id


def test_publish_provider_validation():
    client = _client()

    missing = client.post(
        "/api/publish/jobs",
        json={"source_workspace": "memory/vault", "provider": "unknown"},
    )
    assert missing.status_code == 404

    sync_missing = client.post("/api/publish/providers/unknown/sync")
    assert sync_missing.status_code == 404

    unavailable = client.post(
        "/api/publish/jobs",
        json={"source_workspace": "memory/vault", "provider": "oc_app"},
    )
    assert unavailable.status_code == 412
