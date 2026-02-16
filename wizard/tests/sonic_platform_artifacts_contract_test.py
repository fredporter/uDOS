from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.platform_routes as platform_routes


class _BuildSvc:
    def get_build_artifacts(self, build_id):
        if build_id == "missing":
            raise FileNotFoundError("Build not found: missing")
        return {
            "build_id": build_id,
            "artifacts": [
                {
                    "name": "sonic-stick-v1.3.17-b42.img",
                    "path": "sonic-stick-v1.3.17-b42.img",
                    "exists": True,
                    "size_bytes": 1024,
                    "sha256": "abc",
                }
            ],
            "checksums": "/tmp/checksums.txt",
            "manifest": "/tmp/build-manifest.json",
        }

    def start_build(self, **_kwargs):
        return {"success": True}

    def list_builds(self, limit=50):
        return {"count": 0, "total_found": 0, "builds": []}

    def get_build(self, build_id):
        return {"build_id": build_id}

    def get_release_readiness(self, build_id):
        if build_id == "missing":
            raise FileNotFoundError("Build not found: missing")
        return {
            "build_id": build_id,
            "release_ready": False,
            "checksums": {"present": True, "verified": True, "entries_checked": 3},
            "signing": {"manifest_signature_present": False, "checksums_signature_present": False, "ready": False},
            "artifacts": [],
            "issues": ["release signatures incomplete"],
        }



def _client(monkeypatch):
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    return TestClient(app)



def test_platform_build_artifacts_contract_and_not_found(monkeypatch):
    client = _client(monkeypatch)

    ok_res = client.get("/api/platform/sonic/builds/b42/artifacts")
    assert ok_res.status_code == 200
    payload = ok_res.json()

    assert payload["build_id"] == "b42"
    assert isinstance(payload["artifacts"], list)
    assert payload["artifacts"][0]["name"].endswith(".img")
    assert "checksums" in payload
    assert "manifest" in payload

    missing_res = client.get("/api/platform/sonic/builds/missing/artifacts")
    assert missing_res.status_code == 404


def test_platform_release_readiness_contract_and_not_found(monkeypatch):
    client = _client(monkeypatch)

    ok_res = client.get("/api/platform/sonic/builds/b42/release-readiness")
    assert ok_res.status_code == 200
    payload = ok_res.json()
    assert payload["build_id"] == "b42"
    assert "release_ready" in payload
    assert "checksums" in payload
    assert "signing" in payload
    assert isinstance(payload["issues"], list)

    missing_res = client.get("/api/platform/sonic/builds/missing/release-readiness")
    assert missing_res.status_code == 404
