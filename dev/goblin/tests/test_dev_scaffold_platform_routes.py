from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.platform_routes as platform_routes
from wizard.services.dev_extension_service import DevExtensionService


def _write_scaffold(repo_root, *, missing: set[str] | None = None) -> None:
    dev_root = repo_root / "dev"
    dev_root.mkdir(parents=True, exist_ok=True)
    missing = missing or set()
    for relative_path in DevExtensionService.REQUIRED_FILES:
        if relative_path in missing:
            continue
        target = dev_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
    for name in ("files", "relecs", "dev-work", "testing"):
        (dev_root / name).mkdir()


def test_platform_dev_scaffold_status_uses_v1_5_dev_root(tmp_path):
    _write_scaffold(tmp_path)

    app = FastAPI()
    app.include_router(
        platform_routes.create_platform_routes(auth_guard=None, repo_root=tmp_path)
    )
    client = TestClient(app)

    res = client.get("/api/platform/dev/scaffold")
    assert res.status_code == 200
    body = res.json()
    assert body["workspace_alias"] == "@dev"
    assert body["mode"] == "dev-extension-scaffold"
    assert body["ready"] is True
    assert body["required"]["AGENTS.md"] is True
    assert body["required"]["ops/tasks.json"] is True
    assert body["required"]["extension.json"] is True
    assert body["missing_files"] == []
    assert body["missing_count"] == 0
    assert "goblin/tests" in body["tracked_sync_paths"]
    assert body["ops_paths"]["tasks_json"].endswith("/dev/ops/tasks.json")
    assert body["local_workdirs"]["dev_work"] is True


def test_platform_dev_scaffold_status_reports_missing_required_files(tmp_path):
    _write_scaffold(tmp_path, missing={"docs/features/GITHUB-INTEGRATION.md", "goblin/tests/README.md"})

    app = FastAPI()
    app.include_router(
        platform_routes.create_platform_routes(auth_guard=None, repo_root=tmp_path)
    )
    client = TestClient(app)

    res = client.get("/api/platform/dev/scaffold")
    assert res.status_code == 200
    body = res.json()
    assert body["ready"] is False
    assert body["required"]["docs/features/GITHUB-INTEGRATION.md"] is False
    assert body["required"]["goblin/tests/README.md"] is False
    assert body["missing_count"] == 2
    assert sorted(body["missing_files"]) == [
        "docs/features/GITHUB-INTEGRATION.md",
        "goblin/tests/README.md",
    ]
