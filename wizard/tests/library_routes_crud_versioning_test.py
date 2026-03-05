from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.library_routes as library_routes


class _Manager:
    def get_library_status(self):
        return SimpleNamespace(integrations=[])

    def install_inventory_dependencies(self, name):
        if name == "demo":
            return {
                "success": True,
                "integration": "demo",
                "message": "Installed APK packages: bash",
                "installed_groups": {"apk_dependencies": ["bash"]},
            }
        return {
            "success": False,
            "integration": name,
            "message": "Integration not found",
        }

    def get_integration_versions(self, name):
        if name == "demo":
            return {
                "integration": "demo",
                "found": True,
                "current_version": "1.0.0",
                "available_versions": ["1.0.0", "1.1.0"],
            }
        return {"integration": name, "found": False, "current_version": None, "available_versions": []}

    def resolve_integration_dependencies(self, name):
        if name == "demo":
            return {
                "integration": "demo",
                "found": True,
                "direct_integrations": ["base"],
                "install_order": ["base"],
                "missing_integrations": [],
                "cycle_detected": False,
                "package_dependencies": {"apk_dependencies": ["bash"]},
            }
        return {
            "integration": name,
            "found": False,
            "direct_integrations": [],
            "install_order": [],
            "missing_integrations": [],
            "package_dependencies": {},
        }


def _client(monkeypatch):
    monkeypatch.setattr(library_routes, "get_library_manager", lambda: _Manager())
    app = FastAPI()
    app.include_router(library_routes.router)
    return TestClient(app)


def test_library_versions_and_dependencies_routes(monkeypatch):
    client = _client(monkeypatch)

    versions = client.get("/api/library/integration/demo/versions")
    assert versions.status_code == 200
    assert versions.json()["current_version"] == "1.0.0"
    assert versions.json()["available_versions"] == ["1.0.0", "1.1.0"]

    deps = client.get("/api/library/integration/demo/dependencies")
    assert deps.status_code == 200
    assert deps.json()["install_order"] == ["base"]
    assert deps.json()["package_dependencies"]["apk_dependencies"] == ["bash"]

    missing = client.get("/api/library/integration/missing/versions")
    assert missing.status_code == 404


def test_delete_repo_route(monkeypatch):
    called = {}

    class _Factory:
        def remove(self, name, remove_packages=False):
            called["name"] = name
            called["remove_packages"] = remove_packages
            return True

    monkeypatch.setattr(library_routes, "PluginFactory", lambda: _Factory())
    client = _client(monkeypatch)

    resp = client.delete("/api/library/repos/demo-repo?remove_packages=true")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert called == {"name": "demo-repo", "remove_packages": True}


def test_clone_repo_rejects_non_https_non_shorthand(monkeypatch):
    client = _client(monkeypatch)
    res = client.post("/api/library/repos/clone?repo=git@github.com:owner/repo.git")
    assert res.status_code == 400
    assert "https repository URLs" in res.json()["detail"]


def test_clone_repo_normalizes_https_url(monkeypatch):
    called = {}

    class _Cloned:
        def to_dict(self):
            return {"name": "repo", "url": "https://git.example.com/team/repo.git"}

    class _Factory:
        def clone(self, repo, branch="main"):
            called["repo"] = repo
            called["branch"] = branch
            return _Cloned()

    monkeypatch.setattr(library_routes, "PluginFactory", lambda: _Factory())
    client = _client(monkeypatch)

    res = client.post("/api/library/repos/clone?repo=https://git.example.com/team/repo&branch=stable")
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert called == {"repo": "https://git.example.com/team/repo.git", "branch": "stable"}
    assert payload["normalized_repo"]["canonical_url"] == "https://git.example.com/team/repo.git"
    assert payload["normalized_repo"]["display"] == "team/repo"


def test_install_repo_wizard_clones_and_returns_thin_gui(monkeypatch):
    class _Cloned:
        name = "demo"

        def to_dict(self):
            return {"name": "demo", "url": "https://github.com/example/demo.git"}

    class _Factory:
        def clone(self, repo, branch="main"):
            return _Cloned()

    class _Launcher:
        def get_container_config(self, container_id):
            assert container_id == "demo"
            return {
                "name": "Demo App",
                "port": 4321,
                "browser_route": "/app",
            }

        async def launch_container(self, container_id, background_tasks):
            return {
                "success": True,
                "status": "launching",
                "container_id": container_id,
            }

    monkeypatch.setattr(library_routes, "PluginFactory", lambda: _Factory())
    monkeypatch.setattr(library_routes, "get_launcher", lambda: _Launcher())
    client = _client(monkeypatch)

    res = client.post(
        "/api/library/repos/install-wizard",
        json={
            "repo": "example/demo",
            "branch": "main",
            "launch_if_runnable": True,
            "open_thin_gui": True,
        },
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["container"]["detected"] is True
    assert payload["container"]["launched"] is True
    assert payload["container"]["thin_gui"]["target_url"] == "http://127.0.0.1:4321/app"


def test_inventory_install_route(monkeypatch):
    client = _client(monkeypatch)
    res = client.post("/api/library/inventory/demo/install")
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["result"]["integration"] == "demo"
    assert payload["result"]["installed_groups"]["apk_dependencies"] == ["bash"]


def test_inventory_install_route_returns_not_found(monkeypatch):
    client = _client(monkeypatch)
    res = client.post("/api/library/inventory/missing/install")
    assert res.status_code == 404
    assert res.json()["detail"] == "Integration not found"
