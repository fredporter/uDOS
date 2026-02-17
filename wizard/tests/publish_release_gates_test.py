from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.publish_routes import create_publish_routes
from wizard.services.publish_service import PublishService


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(create_publish_routes(publish_service=PublishService()))
    return TestClient(app)


def test_release_gate_publish_lifecycle_contract():
    client = _client()

    created = client.post(
        "/api/publish/jobs",
        json={"source_workspace": "memory/vault", "provider": "wizard"},
    )
    assert created.status_code == 200
    job = created.json()["job"]
    assert job["status"] == "queued"
    assert job["module"] == "wizard"
    assert job["publish_lane"] == "core"
    assert job["manifest_id"]

    fetched = client.get(f"/api/publish/jobs/{job['publish_job_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["job"]["publish_job_id"] == job["publish_job_id"]

    cancelled = client.post(f"/api/publish/jobs/{job['publish_job_id']}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["job"]["status"] == "cancelled"


def test_release_gate_manifest_integrity_contract():
    client = _client()
    created = client.post(
        "/api/publish/jobs",
        json={"source_workspace": "memory/vault", "provider": "wizard"},
    )
    assert created.status_code == 200
    manifest_id = created.json()["job"]["manifest_id"]

    manifest_res = client.get(f"/api/publish/manifests/{manifest_id}")
    assert manifest_res.status_code == 200
    manifest = manifest_res.json()["manifest"]

    required_keys = {
        "manifest_id",
        "publish_job_id",
        "contract_version",
        "provider",
        "source_workspace",
        "module",
        "publish_lane",
        "artifact_manifest",
        "checksum_set",
        "created_at",
    }
    assert required_keys.issubset(set(manifest.keys()))
    assert "source_workspace_sha256" in manifest["checksum_set"]
