from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.workspace_routes import create_workspace_routes
from wizard.services.path_utils import get_repo_root


def build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(create_workspace_routes(auth_guard=None))
    return app


def test_workspace_route_accepts_at_workspace_refs():
    app = build_app()
    client = TestClient(app)

    marker = f"workspace-routes-{uuid4().hex[:8]}.md"
    repo_root = get_repo_root()
    vault_file = repo_root / "memory" / "vault" / marker
    vault_file.parent.mkdir(parents=True, exist_ok=True)
    vault_file.write_text("# Workspace Route Test\n", encoding="utf-8")

    try:
        res = client.get("/api/workspace/read", params={"path": f"@vault/{marker}"})
        assert res.status_code == 200
        assert "Workspace Route Test" in res.json().get("content", "")

        res = client.get("/api/workspace/list", params={"path": "@vault"})
        assert res.status_code == 200
        assert res.json().get("success") is True
    finally:
        if vault_file.exists():
            vault_file.unlink()


def test_workspace_roots_include_aliases():
    app = build_app()
    client = TestClient(app)

    res = client.get("/api/workspace/roots")
    assert res.status_code == 200
    roots = res.json().get("roots", {})
    assert "@vault" in roots
    assert "@sandbox" in roots
