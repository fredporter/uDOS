from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.settings_unified as routes


class _Venv:
    def model_dump(self):
        return {"exists": True, "path": "/tmp/.venv"}


class _WorkspaceSvc:
    last_field_write = None

    def workspace_contract(self):
        return {
            "workspace_ref": "@memory/bank/typo-workspace",
            "editor_library_ref": "typo",
        }

    def component_snapshot(self, component_id):
        return {
            "component_id": component_id,
            "settings": {"effective_source": "default", "effective_content": "# default\n"},
        }

    def read_document(self, section, component_id):
        return {
            "section": section,
            "component_id": component_id,
            "effective_source": "default",
            "effective_content": "# read\n",
        }

    def write_user_document(self, section, component_id, content):
        return {
            "section": section,
            "component_id": component_id,
            "effective_source": "user",
            "effective_content": content,
        }

    def write_user_field(self, section, component_id, field_name, value):
        self.last_field_write = {
            "section": section,
            "component_id": component_id,
            "field_name": field_name,
            "value": value,
        }
        return {
            "section": section,
            "component_id": component_id,
            "effective_source": "user",
            "effective_content": f"- {field_name}: {value}\n",
        }


def test_settings_unified_status_exposes_template_workspace(monkeypatch):
    workspace_service = _WorkspaceSvc()
    monkeypatch.setattr(routes, "get_venv_status", lambda: _Venv())
    monkeypatch.setattr(routes, "get_secrets_config", lambda: {"ok": []})
    monkeypatch.setattr(routes, "get_available_extensions", lambda: [])
    monkeypatch.setattr(
        routes,
        "get_template_workspace_service",
        lambda repo_root=None: workspace_service,
    )

    app = FastAPI()
    app.include_router(routes.create_settings_unified_router())
    client = TestClient(app)

    status = client.get("/api/settings-unified/status")
    assert status.status_code == 200
    assert status.json()["template_workspace"]["workspace_ref"] == "@memory/bank/typo-workspace"
    assert status.json()["wizard_settings_workspace"]["component_id"] == "wizard"

    workspace_response = client.get("/api/settings-unified/template-workspace")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["editor_library_ref"] == "typo"

    document = client.get("/api/settings-unified/template-workspace/sonic/settings")
    assert document.status_code == 200
    assert document.json()["component_id"] == "sonic"

    update = client.put(
        "/api/settings-unified/template-workspace/sonic/settings",
        json={"content": "# override\n"},
    )
    assert update.status_code == 200
    assert update.json()["effective_source"] == "user"
    assert update.json()["effective_content"] == "# override\n"

    field_update = client.put(
        "/api/settings-unified/template-workspace/sonic/settings/field",
        json={"field_name": "preferred-launcher", "value": "wantmymtv"},
    )
    assert field_update.status_code == 200
    assert field_update.json()["effective_source"] == "user"
    assert workspace_service.last_field_write == {
        "section": "settings",
        "component_id": "sonic",
        "field_name": "preferred-launcher",
        "value": "wantmymtv",
    }
