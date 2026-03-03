from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.platform_routes as platform_routes


class _StubBuildService:
    builds_root = "distribution/builds"
    default_profile = "workspace-profile"
    default_profile_source = "template_workspace"

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
    monkeypatch.setattr(
        platform_routes,
        "get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "component_contract": lambda self, component_id: {
                    "component_id": component_id,
                    "workspace_ref": "@memory/bank/typo-workspace",
                },
                "component_snapshot": lambda self, component_id: {
                    "component_id": component_id,
                    "settings": {"effective_source": "default"},
                },
            },
        )(),
    )

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

    verify_res = client.get("/api/platform/sonic/verify")
    assert verify_res.status_code == 200
    assert "verification" in verify_res.json()

    dataset_res = client.get("/api/platform/sonic/dataset-contract")
    assert dataset_res.status_code == 200
    assert "dataset_contract" in dataset_res.json()
    assert "checked_at" in dataset_res.json()

    status_res = client.get("/api/platform/sonic/status")
    assert status_res.status_code == 200
    assert status_res.json()["template_workspace"]["component_id"] == "sonic"
    assert status_res.json()["template_workspace_state"]["component_id"] == "sonic"
    assert status_res.json()["default_build_profile"] == "workspace-profile"
    assert status_res.json()["default_build_profile_source"] == "template_workspace"


def test_platform_dev_scaffold_status_uses_v1_5_dev_root(monkeypatch, tmp_path):
    client = _client(monkeypatch)

    dev_root = tmp_path / "dev"
    dev_root.mkdir(parents=True)
    for name in (
        "AGENTS.md",
        "DEVLOG.md",
        "project.json",
        "tasks.md",
        "completed.json",
        "extension.json",
    ):
        (dev_root / name).write_text("", encoding="utf-8")
    for name in ("files", "relecs", "dev-work", "testing"):
        (dev_root / name).mkdir()

    app = FastAPI()
    app.include_router(
        platform_routes.create_platform_routes(auth_guard=None, repo_root=tmp_path)
    )
    client = TestClient(app)

    res = client.get("/api/platform/dev/scaffold")
    assert res.status_code == 200
    body = res.json()
    assert body["mode"] == "dev-extension-scaffold"
    assert body["ready"] is True
    assert body["required"]["agents"] is True
    assert body["required"]["extension_manifest"] is True
    assert body["local_workdirs"]["dev_work"] is True
