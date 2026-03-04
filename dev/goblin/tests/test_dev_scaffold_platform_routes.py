from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.platform_routes as platform_routes


def test_platform_dev_scaffold_status_uses_v1_5_dev_root(tmp_path):
    dev_root = tmp_path / "dev"
    dev_root.mkdir(parents=True)
    for name in ("AGENTS.md", "extension.json"):
        (dev_root / name).write_text("", encoding="utf-8")
    ops_root = dev_root / "ops"
    ops_root.mkdir(parents=True)
    for name in (
        "README.md",
        "AGENTS.md",
        "DEVLOG.md",
        "project.json",
        "tasks.md",
        "tasks.json",
        "completed.json",
    ):
        (ops_root / name).write_text("", encoding="utf-8")
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
    assert body["required"]["ops"] is True
    assert body["required"]["tasks_json"] is True
    assert body["required"]["extension_manifest"] is True
    assert body["local_workdirs"]["dev_work"] is True
