from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.platform_routes as platform_routes


class _StubBuildService:
    def start_build(self, profile="alpine-core+sonic", build_id=None, source_image=None, output_dir=None):
        return {
            "success": True,
            "build_id": build_id or "stub-build",
            "profile": profile,
            "build_dir": output_dir or "distribution/builds/stub-build",
        }

    def list_builds(self, limit=50):
        return {
            "count": 1,
            "total_found": 1,
            "builds": [
                {
                    "build_id": "stub-build",
                    "profile": "alpine-core+sonic",
                    "artifact_count": 2,
                }
            ],
        }

    def get_build(self, build_id):
        return {"build_id": build_id, "manifest": {"build_id": build_id}}

    def get_build_artifacts(self, build_id):
        return {
            "build_id": build_id,
            "artifacts": [{"name": "stub.img", "path": "stub.img", "exists": True}],
        }


def _client(monkeypatch):
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _StubBuildService())

    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    return TestClient(app)


def test_platform_sonic_build_endpoints(monkeypatch):
    client = _client(monkeypatch)

    create_res = client.post("/api/platform/sonic/build", json={"profile": "alpine-core+sonic"})
    assert create_res.status_code == 200
    assert create_res.json()["success"] is True

    list_res = client.get("/api/platform/sonic/builds")
    assert list_res.status_code == 200
    assert list_res.json()["count"] == 1

    detail_res = client.get("/api/platform/sonic/builds/stub-build")
    assert detail_res.status_code == 200
    assert detail_res.json()["build_id"] == "stub-build"

    artifacts_res = client.get("/api/platform/sonic/builds/stub-build/artifacts")
    assert artifacts_res.status_code == 200
    assert artifacts_res.json()["build_id"] == "stub-build"
