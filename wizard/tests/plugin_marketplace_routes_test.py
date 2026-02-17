from types import SimpleNamespace
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.enhanced_plugin_routes as routes


def _app(monkeypatch):
    class _Discovery:
        udos_root = Path("/tmp")

        def discover_all(self):
            plugin = SimpleNamespace(
                installed=False,
                update_available=False,
                installer_type="git",
                git=SimpleNamespace(remote_url="https://example.com/repo.git"),
                source_path="extensions/demo",
                installer_script=None,
            )
            return {"demo": plugin}

        def get_plugin(self, plugin_id):
            if plugin_id != "demo":
                return None
            return self.discover_all()["demo"]

    class _Registry:
        def build_registry(self, refresh=False, include_manifests=False):
            _ = (refresh, include_manifests)
            return {
                "demo": {
                    "name": "Demo Plugin",
                    "description": "Demo",
                    "version": "1.0.0",
                    "packages": [],
                    "manifest_report": {"validation_status": "valid"},
                }
            }

    monkeypatch.setattr(routes, "get_discovery_service", lambda: _Discovery())
    monkeypatch.setattr(routes, "get_registry", lambda: _Registry())

    app = FastAPI()
    app.include_router(routes.create_enhanced_plugin_routes())
    return TestClient(app)


def test_marketplace_list_and_get(monkeypatch):
    client = _app(monkeypatch)
    listing = client.get("/api/plugins/marketplace")
    assert listing.status_code == 200
    assert listing.json()["count"] == 1
    assert listing.json()["plugins"][0]["id"] == "demo"

    detail = client.get("/api/plugins/marketplace/demo")
    assert detail.status_code == 200
    assert detail.json()["entry"]["name"] == "Demo Plugin"


def test_marketplace_install_update_uninstall(monkeypatch):
    client = _app(monkeypatch)

    install = client.post("/api/plugins/marketplace/demo/install")
    assert install.status_code == 200
    assert install.json()["success"] is True

    update = client.post("/api/plugins/marketplace/demo/update")
    assert update.status_code == 200
    assert update.json()["success"] is True

    uninstall = client.post("/api/plugins/marketplace/demo/uninstall")
    assert uninstall.status_code == 200
    assert uninstall.json()["success"] is True
