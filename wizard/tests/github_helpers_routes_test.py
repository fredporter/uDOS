from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.github_helpers_routes import create_github_helpers_routes
import wizard.routes.github_helpers_routes as routes


def _client():
    app = FastAPI()
    app.include_router(create_github_helpers_routes())
    return TestClient(app)


def test_github_helpers_status(monkeypatch):
    monkeypatch.setattr(routes, "_gh_auth_status", lambda: {"available": True, "authenticated": True, "detail": "ok"})
    client = _client()
    res = client.get("/api/github/helpers/status")
    assert res.status_code == 200
    assert res.json()["gh"]["authenticated"] is True


def test_issue_and_pr_draft_dry_run():
    client = _client()

    issue = client.post(
        "/api/github/helpers/issue/draft",
        json={"repo": "owner/repo", "title": "Bug", "body": "Details", "labels": ["bug"], "dry_run": True},
    )
    assert issue.status_code == 200
    assert issue.json()["dry_run"] is True
    assert "issue" in issue.json()["command"]

    pr = client.post(
        "/api/github/helpers/pr/draft",
        json={"repo": "owner/repo", "title": "PR", "body": "Body", "dry_run": True},
    )
    assert pr.status_code == 200
    assert pr.json()["dry_run"] is True
    assert "pr" in pr.json()["command"]


def test_issue_create_exec(monkeypatch):
    monkeypatch.setattr(routes, "_gh_available", lambda: True)
    monkeypatch.setattr(
        routes.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="https://github.com/owner/repo/issues/1\n", stderr=""),
    )
    client = _client()
    res = client.post(
        "/api/github/helpers/issue/draft",
        json={"repo": "owner/repo", "title": "Bug", "body": "Details", "dry_run": False},
    )
    assert res.status_code == 200
    assert res.json()["url"].endswith("/issues/1")


def test_publish_sync_dry_run():
    client = _client()
    res = client.post(
        "/api/github/helpers/publish-sync",
        json={"repo": "owner/repo", "workflow": "publish.yml", "ref": "main", "dry_run": True},
    )
    assert res.status_code == 200
    assert res.json()["dry_run"] is True
    assert res.json()["command"][:3] == ["gh", "workflow", "run"]
