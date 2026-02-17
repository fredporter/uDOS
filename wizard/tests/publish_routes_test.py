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
    assert payload["providers"]["wizard"]["publish_lane"] == "core"

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
    manifest = manifest_res.json()["manifest"]
    assert manifest["publish_job_id"] == job_id
    assert manifest["module"] == "wizard"
    assert manifest["publish_lane"] == "core"
    assert "source_workspace_sha256" in manifest["checksum_set"]


def test_publish_provider_registry_route():
    client = _client()

    registry_res = client.get("/api/publish/providers")
    assert registry_res.status_code == 200
    providers = registry_res.json()["providers"]
    assert "wizard" in providers
    assert providers["wizard"]["publish_lane"] == "core"
    assert providers["wizard"]["module"] == "wizard"


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

    gate_blocked = client.post(
        "/api/publish/jobs",
        json={"source_workspace": "memory/vault", "provider": "sonic"},
    )
    assert gate_blocked.status_code == 412
    assert "module-aware publish gating blocked" in gate_blocked.json()["detail"]


def test_oc_app_contract_and_render_routes():
    client = _client()

    contract_res = client.get("/api/publish/providers/oc_app/contract")
    assert contract_res.status_code == 200
    contract = contract_res.json()["contract"]
    assert contract["provider"] == "oc_app"
    assert contract["host"]["render_route"] == "/api/publish/providers/oc_app/render"
    assert "oc_app:render" in contract["session_boundary"]["required_scopes"]

    render_res = client.post(
        "/api/publish/providers/oc_app/render",
        json={
            "contract_version": "1.0.0",
            "content": "# Title",
            "content_type": "markdown",
            "entrypoint": "index",
            "render_options": {"theme": "default"},
            "assets": [
                {
                    "path": "assets/style.css",
                    "media_type": "text/css",
                    "content_sha256": "f" * 64,
                }
            ],
            "session": {
                "session_id": "sess_1",
                "principal_id": "user_1",
                "token_lease_id": "lease_1",
                "scopes": ["oc_app:render"],
            },
        },
    )
    assert render_res.status_code == 200
    render = render_res.json()["render"]
    assert render["provider"] == "oc_app"
    assert render["entrypoint"] == "index"
    assert render["assets_manifest"]["count"] == 1
    assert render["session"]["token_lease_validated"] is True


def test_oc_app_render_rejects_invalid_session_boundary():
    client = _client()

    missing_scope = client.post(
        "/api/publish/providers/oc_app/render",
        json={
            "content": "hello",
            "session": {
                "session_id": "sess_2",
                "principal_id": "user_2",
                "token_lease_id": "lease_2",
                "scopes": [],
            },
        },
    )
    assert missing_scope.status_code == 412
    assert "missing required scope" in missing_scope.json()["detail"]

    forbidden_secret = client.post(
        "/api/publish/providers/oc_app/render",
        json={
            "content": "hello",
            "render_options": {"api_key": "secret-value"},
            "session": {
                "session_id": "sess_3",
                "principal_id": "user_3",
                "token_lease_id": "lease_3",
                "scopes": ["oc_app:render"],
            },
        },
    )
    assert forbidden_secret.status_code == 400
    assert "forbidden secret keys" in forbidden_secret.json()["detail"]
