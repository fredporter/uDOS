from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.system_info_routes as routes


def test_system_info_routes_expose_template_workspace(tmp_path, monkeypatch):
    seed_root = tmp_path / "core" / "framework" / "seed" / "bank" / "typo-workspace"
    (seed_root / "settings").mkdir(parents=True)
    (seed_root / "instructions").mkdir(parents=True)
    (seed_root / "settings" / "shared.md").write_text("# shared\n", encoding="utf-8")
    (seed_root / "instructions" / "shared.md").write_text("# shared\n", encoding="utf-8")

    monkeypatch.setattr(routes, "get_repo_root", lambda: tmp_path)

    router = routes.create_system_info_routes(prefix="/api/test-system")
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.get("/api/test-system/template-workspace")
    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace_ref"] == "@memory/bank/typo-workspace"
    assert payload["components"]["shared"]["settings"]["seeded"].endswith(
        "settings/shared.md"
    )
