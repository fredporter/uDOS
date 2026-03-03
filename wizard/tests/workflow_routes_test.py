from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.workflow_routes import create_workflow_routes


def _build_app():
    app = FastAPI()
    app.include_router(create_workflow_routes())
    return app


def test_workflow_template_routes_reuse_ucode_template_flow():
    client = TestClient(_build_app())

    list_res = client.get("/api/workflows/templates")
    read_res = client.get("/api/workflows/templates/WORKFLOW-template")
    dup_res = client.post(
        "/api/workflows/templates/WORKFLOW-template/duplicate",
        json={"target_name": "workflow-copy"},
    )

    assert list_res.status_code == 200
    assert "templates" in list_res.json()

    assert read_res.status_code == 200
    assert read_res.json()["template"]["template_name"] == "WORKFLOW-template"

    assert dup_res.status_code == 200
    assert dup_res.json()["duplicate"]["target_name"] == "workflow-copy"
