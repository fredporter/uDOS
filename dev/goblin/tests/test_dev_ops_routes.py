from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.dev_routes import create_dev_routes


def _client(monkeypatch, repo_root: Path) -> TestClient:
    from core.services import user_service
    from core.services.permission_handler import Permission
    import wizard.routes.dev_routes as dev_routes

    class _UserManager:
        def has_permission(self, permission):
            return permission in {Permission.ADMIN, Permission.DEV_MODE}

    monkeypatch.setattr(dev_routes, "get_repo_root", lambda: repo_root)
    monkeypatch.setattr(user_service, "get_user_manager", lambda: _UserManager())
    monkeypatch.setattr(dev_routes, "get_user_manager", lambda: _UserManager())

    app = FastAPI()
    app.include_router(create_dev_routes())
    return TestClient(app)


def _scaffold_dev_root(repo_root: Path) -> None:
    dev_root = repo_root / "dev"
    (dev_root / "docs" / "specs").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "howto").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "features").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "decisions").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "devlog").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "tests").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "server").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "seed").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "scenarios").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "test-vault").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "templates").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "scheduler").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "workflows").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "utils").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "workspace").mkdir(parents=True, exist_ok=True)

    files = {
        "AGENTS.md": "# dev\n",
        "README.md": "# dev\n",
        "extension.json": "{}\n",
        "docs/README.md": "# docs\n",
        "docs/DEV-MODE-POLICY.md": "# policy\n",
        "docs/specs/DEV-WORKSPACE-SPEC.md": "# spec\n",
        "docs/howto/GETTING-STARTED.md": "# start\n",
        "docs/howto/VIBE-Setup-Guide.md": "# vibe\n",
        "docs/features/GITHUB-INTEGRATION.md": "# github\n",
        "docs/decisions/README.md": "# decisions\n",
        "docs/devlog/README.md": "# devlog\n",
        "docs/roadmap/ROADMAP.md": "# roadmap\n",
        "docs/tasks/README.md": "# tasks\n",
        "goblin/README.md": "# goblin\n",
        "goblin/tests/README.md": "# goblin tests\n",
        "ops/README.md": "# ops\n",
        "ops/AGENTS.md": "# ops agents\n",
        "ops/DEVLOG.md": "# ops devlog\n",
        "ops/project.json": "{}\n",
        "ops/tasks.md": "# tasks\n",
        "ops/tasks.json": "{}\n",
        "ops/completed.json": "{}\n",
        "ops/templates/uDOS-dev.code-workspace": "{}\n",
        "ops/templates/copilot-instructions.md": "# copilot\n",
    }
    for rel, content in files.items():
        path = dev_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def test_dev_ops_endpoint_returns_canonical_ops_paths(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    client = _client(monkeypatch, tmp_path)

    response = client.get("/api/dev/ops")

    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace_alias"] == "@dev"
    assert payload["ops"]["root"].endswith("/dev/ops")
    assert payload["ops"]["files"]["tasks_json"]["present"] is True
    assert payload["ops"]["files"]["workspace"]["path"].endswith(
        "/dev/ops/templates/uDOS-dev.code-workspace"
    )
    assert payload["ops"]["files"]["copilot"]["path"].endswith(
        "/dev/ops/templates/copilot-instructions.md"
    )


def test_dev_ops_browser_endpoints_list_and_read_files(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    client = _client(monkeypatch, tmp_path)

    list_response = client.get("/api/dev/ops/files", params={"area": "ops"})
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["area"] == "ops"
    assert any(entry["name"] == "AGENTS.md" for entry in list_payload["entries"])

    read_response = client.get(
        "/api/dev/ops/read", params={"area": "ops", "path": "AGENTS.md"}
    )
    assert read_response.status_code == 200
    read_payload = read_response.json()
    assert read_payload["area"] == "ops"
    assert "ops agents" in read_payload["content"]
