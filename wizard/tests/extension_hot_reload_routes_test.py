from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.extension_routes as extension_routes


def test_extension_hot_reload_routes(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True)

    (repo_root / "dev").mkdir(parents=True)
    (repo_root / "dev" / "__init__.py").write_text("# dev", encoding="utf-8")
    (repo_root / "sonic").mkdir(parents=True)
    (repo_root / "sonic" / "__init__.py").write_text("# sonic", encoding="utf-8")

    monkeypatch.setattr(extension_routes, "REPO_ROOT", repo_root)
    monkeypatch.setattr(
        extension_routes,
        "OFFICIAL_EXTENSIONS",
        [
            {
                "id": "dev",
                "name": "Dev",
                "description": "dev",
                "icon": "d",
                "path": "dev",
                "main_file": "__init__.py",
                "api_prefix": "/api/dev",
                "web_port": None,
                "category": "developer",
                "visibility": "public",
            },
            {
                "id": "sonic",
                "name": "Sonic",
                "description": "sonic",
                "icon": "s",
                "path": "sonic",
                "main_file": "__init__.py",
                "api_prefix": "/api/sonic",
                "web_port": None,
                "category": "utilities",
                "visibility": "public",
            },
        ],
    )

    app = FastAPI()
    app.include_router(extension_routes.router)
    client = TestClient(app)

    first = client.post("/api/extensions/hot-reload")
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["success"] is True
    assert set(first_payload["changed_extensions"]) == {"dev", "sonic"}

    second = client.post("/api/extensions/hot-reload")
    assert second.status_code == 200
    assert second.json()["changed_count"] == 0

    status = client.get("/api/extensions/hot-reload/status")
    assert status.status_code == 200
    status_payload = status.json()
    assert status_payload["success"] is True
    assert status_payload["history_count"] >= 1
    assert Path(status_payload["state_path"]).name == "hot_reload_state.json"
