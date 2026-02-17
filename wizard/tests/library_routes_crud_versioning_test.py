from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.library_routes as library_routes


class _Manager:
    def get_library_status(self):
        return SimpleNamespace(integrations=[])

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
