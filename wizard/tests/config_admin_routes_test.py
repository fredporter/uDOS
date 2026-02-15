from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes import config_admin_routes as routes


def _app_with_router(router):
    app = FastAPI()
    app.include_router(router)
    return app


def test_admin_token_generate_and_status_local_only(monkeypatch, tmp_path):
    monkeypatch.setattr(routes, "LOCAL_CLIENTS", {"testclient"})
    monkeypatch.setattr(routes, "get_repo_root", lambda: tmp_path)
    monkeypatch.delenv("WIZARD_KEY", raising=False)
    monkeypatch.delenv("WIZARD_ADMIN_TOKEN", raising=False)

    class FakeStore:
        def unlock(self, _key):
            return None

        def set(self, _entry):
            return None

    monkeypatch.setattr(routes, "get_secret_store", lambda: FakeStore())

    app = _app_with_router(routes.create_admin_token_routes())
    client = TestClient(app)

    res = client.post("/api/admin-token/generate")
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "success"
    assert payload["stored_in_secret_store"] is True
    assert payload["key_created"] is True

    env_path = tmp_path / ".env"
    assert env_path.exists()
    env_text = env_path.read_text()
    assert "WIZARD_KEY=" in env_text
    assert "WIZARD_ADMIN_TOKEN=" in env_text

    status_res = client.get("/api/admin-token/status")
    assert status_res.status_code == 200
    status_payload = status_res.json()
    assert status_payload["has_admin_token"] is True
    assert status_payload["has_wizard_key"] is True


def test_admin_token_generate_rejects_non_local(monkeypatch):
    monkeypatch.setattr(routes, "LOCAL_CLIENTS", {"127.0.0.1"})
    app = _app_with_router(routes.create_admin_token_routes())
    client = TestClient(app)

    res = client.post("/api/admin-token/generate")
    assert res.status_code == 403
    assert "local requests only" in res.text


def test_public_export_list_and_download(monkeypatch, tmp_path):
    monkeypatch.setattr(routes, "LOCAL_CLIENTS", {"testclient"})
    export_dir = tmp_path / "memory" / "config_exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_file = export_dir / "udos-config-export-2026-02-15T00-00-00Z.json"
    export_file.write_text('{"ok":true}', encoding="utf-8")
    monkeypatch.setattr(routes, "EXPORT_DIR", export_dir)

    app = _app_with_router(routes.create_public_export_routes())
    client = TestClient(app)

    list_res = client.get("/api/config/export/list")
    assert list_res.status_code == 200
    exports = list_res.json()["exports"]
    assert any(item["filename"] == export_file.name for item in exports)

    dl_res = client.get(f"/api/config/export/{export_file.name}")
    assert dl_res.status_code == 200
    assert dl_res.headers.get("content-type", "").startswith("application/json")


def test_public_export_download_rejects_invalid_filename(monkeypatch):
    monkeypatch.setattr(routes, "LOCAL_CLIENTS", {"testclient"})
    app = _app_with_router(routes.create_public_export_routes())
    client = TestClient(app)

    res = client.get("/api/config/export/not-an-export.json")
    assert res.status_code == 400
