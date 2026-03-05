from fastapi import FastAPI
from fastapi.testclient import TestClient
from uuid import uuid4

from wizard.routes.workflow_routes import create_workflow_routes


class _WorkflowManagerStub:
    def create_workflow(
        self,
        name,
        description=None,
        task_ids=None,
        template_id=None,
        workflow_id=None,
    ):
        return {
            "status": "success",
            "workflow": {"id": workflow_id or "wf-001", "template_id": template_id},
        }

    def list_runtime_workflows(self):
        return {"status": "success", "workflows": [{"id": "wf-001", "status": "ready"}]}

    def get_runtime_dashboard(self):
        return {"status": "success", "summary": {"runs": 1, "awaiting_approval": 0}}

    def get_runtime_workflow(self, workflow_id):
        return {"status": "success", "workflow": {"id": workflow_id, "status": "ready"}}

    def run_runtime_workflow(self, workflow_id):
        return {"status": "success", "workflow_id": workflow_id, "run": {"state": "awaiting_approval"}}

    def get_runtime_workflow_status(self, workflow_id):
        return {"status": "success", "workflow_id": workflow_id, "summary": {"status": "ready"}}

    def get_workflow_tasks(self, workflow_id):
        return {"status": "success", "workflow_id": workflow_id, "tasks": []}


class _SchedulerStub:
    def get_stats(self):
        return {"pending": 0}

    def get_scheduled_queue(self, limit=20):
        return []

    def get_execution_history(self, limit=20):
        return []

    def get_settings(self):
        return {"enabled": True}


def _build_app(monkeypatch=None):
    if monkeypatch is not None:
        monkeypatch.setattr("wizard.routes.workflow_routes.WorkflowManager", _WorkflowManagerStub)
        monkeypatch.setattr("wizard.routes.workflow_routes.TaskScheduler", _SchedulerStub)
    app = FastAPI()
    app.include_router(create_workflow_routes())
    return app


def test_workflow_template_routes_reuse_ucode_template_flow():
    client = TestClient(_build_app())
    target_name = f"workflow-copy-{uuid4().hex[:8]}"

    list_res = client.get("/api/workflows/templates")
    read_res = client.get("/api/workflows/templates/WORKFLOW-template")
    dup_res = client.post(
        "/api/workflows/templates/WORKFLOW-template/duplicate",
        json={"target_name": target_name},
    )

    assert list_res.status_code == 200
    assert "templates" in list_res.json()

    assert read_res.status_code == 200
    assert read_res.json()["template"]["template_name"] == "WORKFLOW-template"

    assert dup_res.status_code == 200
    assert dup_res.json()["duplicate"]["target_template"] == target_name


def test_workflow_routes_use_runtime_workflow_contract(monkeypatch):
    client = TestClient(_build_app(monkeypatch))

    create_res = client.post(
        "/api/workflows/create",
        json={
            "name": "Release note workflow",
            "template_id": "WRITING-article",
            "workflow_id": "wf-001",
            "tasks": [],
        },
    )
    list_res = client.get("/api/workflows/list")
    dash_res = client.get("/api/workflows/dashboard")
    detail_res = client.get("/api/workflows/wf-001")
    run_res = client.post("/api/workflows/wf-001/run")
    status_res = client.get("/api/workflows/wf-001/status")
    tasks_res = client.get("/api/workflows/tasks-dashboard")

    assert create_res.status_code == 200
    assert create_res.json()["workflow"]["template_id"] == "WRITING-article"
    assert list_res.status_code == 200
    assert list_res.json()["workflows"][0]["id"] == "wf-001"
    assert dash_res.status_code == 200
    assert dash_res.json()["summary"]["runs"] == 1
    assert detail_res.status_code == 200
    assert detail_res.json()["workflow"]["id"] == "wf-001"
    assert run_res.status_code == 200
    assert run_res.json()["run"]["state"] == "awaiting_approval"
    assert status_res.status_code == 200
    assert status_res.json()["summary"]["status"] == "ready"
    assert tasks_res.status_code == 200
    assert tasks_res.json()["workflows"][0]["id"] == "wf-001"


def test_workflow_format_route_formats_workflow_plan(monkeypatch):
    client = TestClient(_build_app(monkeypatch))

    response = client.post(
        "/api/workflows/format",
        json={
            "path": "dev/ops/workflows/contributor-cycle.workflow.json",
            "content": '{"steps":[{"action":"implement","step_id":"implement"}],"name":"Contributor Cycle","id":"contributor-cycle"}',
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["format_helper"]["profile"] == "workflow-plan"
    assert payload["content"].index('"id"') < payload["content"].index('"name"')
