from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.dev_routes import create_dev_routes


def _client(monkeypatch, repo_root: Path) -> TestClient:
    from core.services import user_service
    from core.services.permission_handler import Permission
    import wizard.routes.dev_routes as dev_routes
    import wizard.services.workflow_manager as workflow_manager
    import wizard.services.task_scheduler as task_scheduler

    class _UserManager:
        def has_permission(self, permission):
            return permission in {Permission.ADMIN, Permission.DEV_MODE}

    monkeypatch.setattr(dev_routes, "get_repo_root", lambda: repo_root)
    monkeypatch.setattr(workflow_manager, "get_repo_root", lambda: repo_root)
    monkeypatch.setattr(task_scheduler, "get_repo_root", lambda: repo_root)
    monkeypatch.setattr(user_service, "get_user_manager", lambda: _UserManager())
    monkeypatch.setattr(dev_routes, "get_user_manager", lambda: _UserManager())

    app = FastAPI()
    app.include_router(create_dev_routes())
    return TestClient(app)


def _scaffold_dev_root(repo_root: Path) -> None:
    dev_root = repo_root / "dev"
    (dev_root / "docs" / "specs").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "howto").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "features").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "decisions").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "devlog").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
    (dev_root / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "tests").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "server").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "seed").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "scenarios").mkdir(parents=True, exist_ok=True)
    (dev_root / "goblin" / "test-vault").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "templates").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "scheduler").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "workflows").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "utils").mkdir(parents=True, exist_ok=True)
    (dev_root / "ops" / "workspace").mkdir(parents=True, exist_ok=True)

    files = {
        "AGENTS.md": "# dev\n",
        "README.md": "# dev\n",
        "extension.json": "{}\n",
        "docs/README.md": "# docs\n",
        "docs/DEV-MODE-POLICY.md": "# policy\n",
        "docs/specs/DEV-WORKSPACE-SPEC.md": "# spec\n",
        "docs/howto/GETTING-STARTED.md": "# start\n",
        "docs/howto/VIBE-Setup-Guide.md": "# vibe\n",
        "docs/features/GITHUB-INTEGRATION.md": "# github\n",
        "docs/decisions/README.md": "# decisions\n",
        "docs/devlog/README.md": "# devlog\n",
        "docs/roadmap/ROADMAP.md": "# roadmap\n",
        "docs/tasks/README.md": "# tasks\n",
        "goblin/README.md": "# goblin\n",
        "goblin/tests/README.md": "# goblin tests\n",
        "ops/README.md": "# ops\n",
        "ops/AGENTS.md": "# ops agents\n",
        "ops/DEVLOG.md": "# ops devlog\n",
        "ops/project.json": "{}\n",
        "ops/tasks.md": "# tasks\n",
        "ops/tasks.json": "{}\n",
        "ops/completed.json": "{}\n",
        "ops/templates/uDOS-dev.code-workspace": "{}\n",
        "ops/templates/copilot-instructions.md": "# copilot\n",
    }
    for rel, content in files.items():
        path = dev_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def test_dev_ops_endpoint_returns_canonical_ops_paths(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    client = _client(monkeypatch, tmp_path)

    response = client.get("/api/dev/ops")

    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace_alias"] == "@dev"
    assert payload["ops"]["root"].endswith("/dev/ops")
    assert payload["ops"]["files"]["tasks_json"]["present"] is True
    assert payload["ops"]["files"]["workspace"]["path"].endswith(
        "/dev/ops/templates/uDOS-dev.code-workspace"
    )
    assert payload["ops"]["files"]["copilot"]["path"].endswith(
        "/dev/ops/templates/copilot-instructions.md"
    )


def test_dev_ops_browser_endpoints_list_and_read_files(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    client = _client(monkeypatch, tmp_path)

    list_response = client.get("/api/dev/ops/files", params={"area": "ops"})
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["area"] == "ops"
    assert any(entry["name"] == "AGENTS.md" for entry in list_payload["entries"])

    read_response = client.get(
        "/api/dev/ops/read", params={"area": "ops", "path": "AGENTS.md"}
    )
    assert read_response.status_code == 200
    read_payload = read_response.json()
    assert read_payload["area"] == "ops"
    assert "ops agents" in read_payload["content"]
    assert read_payload["format_helper"]["format"] == "markdown"
    assert read_payload["format_helper"]["helper_action"] == "normalize"
    assert read_payload["format_helper"]["save_normalized_label"] == "Save normalized Markdown"


def test_dev_ops_write_endpoint_updates_tracked_text_file(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    client = _client(monkeypatch, tmp_path)

    write_response = client.post(
        "/api/dev/ops/write",
        json={"area": "ops", "path": "AGENTS.md", "content": "# rewritten ops agents\n"},
    )
    assert write_response.status_code == 200
    write_payload = write_response.json()
    assert write_payload["saved"] is True
    assert write_payload["area"] == "ops"
    assert "# rewritten ops agents" in write_payload["content"]
    assert write_payload["normalized"] is False
    assert write_payload["format_helper"]["format"] == "markdown"

    read_response = client.get(
        "/api/dev/ops/read", params={"area": "ops", "path": "AGENTS.md"}
    )
    assert read_response.status_code == 200
    assert "# rewritten ops agents" in read_response.json()["content"]


def test_dev_ops_write_endpoint_rejects_invalid_json(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    client = _client(monkeypatch, tmp_path)

    write_response = client.post(
        "/api/dev/ops/write",
        json={"area": "ops", "path": "project.json", "content": "{\n"},
    )
    assert write_response.status_code == 400
    assert "Invalid JSON" in write_response.json()["detail"]


def test_dev_ops_write_endpoint_rejects_invalid_toml(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    config_path = tmp_path / "dev" / "ops" / "utils" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('title = "ok"\n', encoding="utf-8")
    client = _client(monkeypatch, tmp_path)

    write_response = client.post(
        "/api/dev/ops/write",
        json={"area": "ops", "path": "utils/config.toml", "content": "title = \n"},
    )
    assert write_response.status_code == 400
    assert "Invalid TOML" in write_response.json()["detail"]


def test_dev_ops_write_endpoint_rejects_invalid_yaml(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    yaml_path = tmp_path / "dev" / "goblin" / "seed" / "fixture.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text("name: ok\n", encoding="utf-8")
    client = _client(monkeypatch, tmp_path)

    write_response = client.post(
        "/api/dev/ops/write",
        json={"area": "goblin", "path": "seed/fixture.yaml", "content": "name: [\n"},
    )
    assert write_response.status_code == 400
    detail = write_response.json()["detail"]
    assert "Invalid YAML" in detail or "YAML validation unavailable" in detail


def test_dev_ops_write_endpoint_rejects_invalid_python(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    py_path = tmp_path / "dev" / "goblin" / "tests" / "test_sample.py"
    py_path.write_text("print('ok')\n", encoding="utf-8")
    client = _client(monkeypatch, tmp_path)

    write_response = client.post(
        "/api/dev/ops/write",
        json={"area": "goblin", "path": "tests/test_sample.py", "content": "def broken(:\n    pass\n"},
    )
    assert write_response.status_code == 400
    assert "Invalid Python syntax" in write_response.json()["detail"]


def test_dev_ops_write_endpoint_rejects_invalid_shell(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    sh_path = tmp_path / "dev" / "goblin" / "server" / "check.sh"
    sh_path.parent.mkdir(parents=True, exist_ok=True)
    sh_path.write_text("#!/bin/bash\necho ok\n", encoding="utf-8")
    client = _client(monkeypatch, tmp_path)

    write_response = client.post(
        "/api/dev/ops/write",
        json={"area": "goblin", "path": "server/check.sh", "content": "if then\n  echo broken\nfi\n"},
    )
    assert write_response.status_code == 400
    assert "Invalid shell syntax" in write_response.json()["detail"]


def test_dev_ops_write_endpoint_rejects_unbalanced_markdown_fences(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    md_path = tmp_path / "dev" / "docs" / "notes.md"
    md_path.write_text("# note\n", encoding="utf-8")
    client = _client(monkeypatch, tmp_path)

    write_response = client.post(
        "/api/dev/ops/write",
        json={"area": "docs", "path": "notes.md", "content": "# note\n```python\nprint('hi')\n"},
    )
    assert write_response.status_code == 400
    assert "Markdown fenced code blocks are unbalanced" in write_response.json()["detail"]


def test_dev_ops_normalize_endpoint_formats_structured_and_text_files(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    toml_path = tmp_path / "dev" / "ops" / "utils" / "config.toml"
    toml_path.parent.mkdir(parents=True, exist_ok=True)
    toml_path.write_text('title = "ok"\n', encoding="utf-8")
    yaml_path = tmp_path / "dev" / "goblin" / "seed" / "fixture.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text("name: ok\n", encoding="utf-8")
    md_path = tmp_path / "dev" / "docs" / "notes.md"
    md_path.write_text("# note\n", encoding="utf-8")
    client = _client(monkeypatch, tmp_path)

    json_res = client.post(
        "/api/dev/ops/normalize",
        json={"area": "ops", "path": "project.json", "content": "{\"b\":2,\"a\":1}"},
    )
    assert json_res.status_code == 200
    assert json_res.json()["content"] == '{\n  "b": 2,\n  "a": 1\n}\n'

    toml_res = client.post(
        "/api/dev/ops/normalize",
        json={"area": "ops", "path": "utils/config.toml", "content": 'title="ok"'},
    )
    assert toml_res.status_code == 200
    assert toml_res.json()["content"] == 'title = "ok"\n'

    yaml_res = client.post(
        "/api/dev/ops/normalize",
        json={"area": "goblin", "path": "seed/fixture.yaml", "content": "name: ok"},
    )
    assert yaml_res.status_code == 200
    assert yaml_res.json()["content"] == "name: ok\n"

    md_res = client.post(
        "/api/dev/ops/normalize",
        json={"area": "docs", "path": "notes.md", "content": "# note  \n\n\ntext\n"},
    )
    assert md_res.status_code == 200
    assert md_res.json()["content"] == "# note\n\ntext\n"


def test_dev_ops_write_endpoint_can_save_normalized_content(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    client = _client(monkeypatch, tmp_path)

    write_response = client.post(
        "/api/dev/ops/write",
        json={
            "area": "ops",
            "path": "project.json",
            "content": "{\"b\":2,\"a\":1}",
            "normalize": True,
        },
    )
    assert write_response.status_code == 200
    payload = write_response.json()
    assert payload["saved"] is True
    assert payload["normalized"] is True
    assert payload["changed"] is True
    assert payload["content"] == '{\n  "b": 2,\n  "a": 1\n}\n'
    assert payload["format_helper"]["save_normalized_label"] == "Save formatted JSON"


def test_dev_ops_helpers_identify_contributor_tasks_and_workflow_files(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    workflow_path = tmp_path / "dev" / "ops" / "workflows" / "contributor-cycle.workflow.json"
    workflow_path.write_text(
        '{"steps":[{"action":"implement","step_id":"implement"}],"name":"Contributor Cycle","id":"contributor-cycle"}',
        encoding="utf-8",
    )
    tasks_path = tmp_path / "dev" / "ops" / "tasks.json"
    tasks_path.write_text(
        '{"updated":"2026-03-04","active_missions":[{"title":"Tracked editor","status":"done","id":"tracked-editor"}],"version":"1.0"}',
        encoding="utf-8",
    )
    client = _client(monkeypatch, tmp_path)

    tasks_res = client.get("/api/dev/ops/read", params={"area": "ops", "path": "tasks.json"})
    workflow_res = client.get(
        "/api/dev/ops/read",
        params={"area": "ops", "path": "workflows/contributor-cycle.workflow.json"},
    )

    assert tasks_res.status_code == 200
    assert tasks_res.json()["format_helper"]["profile"] == "tasks-ledger"
    assert tasks_res.json()["format_helper"]["format_label"] == "Contributor tasks JSON"
    assert workflow_res.status_code == 200
    assert workflow_res.json()["format_helper"]["profile"] == "workflow-plan"
    assert workflow_res.json()["format_helper"]["format_label"] == "Workflow plan JSON"


def test_dev_ops_normalize_endpoint_formats_workflow_helper_payload(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    workflow_path = tmp_path / "dev" / "ops" / "workflows" / "contributor-cycle.workflow.json"
    workflow_path.write_text('{"id":"contributor-cycle"}\n', encoding="utf-8")
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/api/dev/ops/normalize",
        json={
            "area": "ops",
            "path": "workflows/contributor-cycle.workflow.json",
            "content": '{"steps":[{"action":"implement","step_id":"implement"}],"name":"Contributor Cycle","id":"contributor-cycle"}',
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["format_helper"]["profile"] == "workflow-plan"
    assert payload["content"].index('"id"') < payload["content"].index('"name"')


def test_dev_ops_planning_endpoint_reports_tracked_and_runtime_handoff(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    tasks_path = tmp_path / "dev" / "ops" / "tasks.json"
    tasks_path.write_text(
        '{"version":"1.0","updated":"2026-03-04","active_missions":[{"id":"phase-1","title":"Self-hosted loop","status":"in_progress","lane":"runtime","priority":"high"}]}',
        encoding="utf-8",
    )
    workflow_path = tmp_path / "dev" / "ops" / "workflows" / "contributor-cycle.workflow.json"
    workflow_path.write_text(
        '{"id":"contributor-cycle","name":"Contributor Cycle","workspace":"@dev","steps":["read-governance","implement","validate"],"artifacts":["dev/ops/tasks.json"]}',
        encoding="utf-8",
    )
    scheduler_template = tmp_path / "dev" / "ops" / "scheduler" / "weekly-dev-cycle.template.json"
    scheduler_template.write_text(
        '{"id":"weekly-dev-cycle","workspace":"@dev","windows":["plan","implement"],"sources":["dev/ops/tasks.json"]}',
        encoding="utf-8",
    )
    client = _client(monkeypatch, tmp_path)

    response = client.get("/api/dev/ops/planning")

    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace_alias"] == "@dev"
    assert payload["tasks_ledger"]["mission_count"] == 1
    assert payload["tasks_ledger"]["status_counts"]["in_progress"] == 1
    assert payload["workflow_plans"][0]["id"] == "contributor-cycle"
    assert payload["workflow_plans"][0]["step_count"] == 3
    assert payload["workflow_plans"][0]["runtime_project"] is None
    assert payload["scheduler_templates"][0]["id"] == "weekly-dev-cycle"
    assert "DEV PLAN" in payload["ucode_handoff"]


def test_dev_ops_workflow_sync_promotes_workflow_plan_into_runtime_project(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    workflow_path = tmp_path / "dev" / "ops" / "workflows" / "contributor-cycle.workflow.json"
    workflow_path.write_text(
        '{"id":"contributor-cycle","name":"Contributor Cycle","workspace":"@dev","steps":["read-governance",{"step_id":"implement","title":"implement","description":"write code"},"validate"]}',
        encoding="utf-8",
    )
    client = _client(monkeypatch, tmp_path)

    activate_response = client.post("/api/dev/activate")
    assert activate_response.status_code == 200

    response = client.post(
        "/api/dev/ops/workflows/sync",
        json={"path": "contributor-cycle.workflow.json"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["plan"]["id"] == "contributor-cycle"
    assert payload["created_tasks"] == 3
    assert payload["runtime_project"]["name"].startswith("@dev workflow:contributor-cycle:")
    assert payload["runtime_project"]["task_count"] == 3

    planning_response = client.get("/api/dev/ops/planning")
    assert planning_response.status_code == 200
    planning_payload = planning_response.json()
    assert planning_payload["workflow_plans"][0]["runtime_project"]["task_count"] == 3


def test_dev_ops_scheduler_register_binds_template_to_runtime_project(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    workflow_path = tmp_path / "dev" / "ops" / "workflows" / "contributor-cycle.workflow.json"
    workflow_path.write_text(
        '{"id":"contributor-cycle","name":"Contributor Cycle","workspace":"@dev","steps":["implement"]}',
        encoding="utf-8",
    )
    scheduler_template = tmp_path / "dev" / "ops" / "scheduler" / "weekly-dev-cycle.template.json"
    scheduler_template.write_text(
        '{"id":"weekly-dev-cycle","workspace":"@dev","windows":["plan","implement"],"sources":["dev/ops/tasks.json"]}',
        encoding="utf-8",
    )
    client = _client(monkeypatch, tmp_path)

    activate_response = client.post("/api/dev/activate")
    assert activate_response.status_code == 200

    response = client.post(
        "/api/dev/ops/scheduler/register",
        json={
            "path": "weekly-dev-cycle.template.json",
            "workflow_path": "contributor-cycle.workflow.json",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["created"] is True
    assert payload["scheduler_template"]["id"] == "weekly-dev-cycle"
    assert payload["runtime_project"]["name"].startswith("@dev workflow:contributor-cycle:")
    assert payload["task"]["kind"].startswith("dev_scheduler:weekly-dev-cycle:")


def test_dev_ops_workflow_run_starts_next_runtime_task(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    workflow_path = tmp_path / "dev" / "ops" / "workflows" / "contributor-cycle.workflow.json"
    workflow_path.write_text(
        '{"id":"contributor-cycle","name":"Contributor Cycle","workspace":"@dev","steps":["read-governance","implement"]}',
        encoding="utf-8",
    )
    client = _client(monkeypatch, tmp_path)

    activate_response = client.post("/api/dev/activate")
    assert activate_response.status_code == 200

    response = client.post(
        "/api/dev/ops/workflows/run",
        json={"path": "contributor-cycle.workflow.json"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["plan"]["id"] == "contributor-cycle"
    assert payload["run"]["task_title"] == "read-governance"
    assert payload["run"]["task_status"] == "in-progress"


def test_dev_ops_workflow_task_status_endpoint_updates_synced_task(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    workflow_path = tmp_path / "dev" / "ops" / "workflows" / "contributor-cycle.workflow.json"
    workflow_path.write_text(
        '{"id":"contributor-cycle","name":"Contributor Cycle","workspace":"@dev","steps":["read-governance","implement"]}',
        encoding="utf-8",
    )
    client = _client(monkeypatch, tmp_path)

    activate_response = client.post("/api/dev/activate")
    assert activate_response.status_code == 200

    sync_response = client.post(
        "/api/dev/ops/workflows/sync",
        json={"path": "contributor-cycle.workflow.json"},
    )
    assert sync_response.status_code == 200
    sync_payload = sync_response.json()
    task_id = sync_payload["project"]["tasks"][0]["id"]

    response = client.post(
        "/api/dev/ops/workflows/task-status",
        json={
            "path": "contributor-cycle.workflow.json",
            "task_id": task_id,
            "status": "completed",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["task"]["id"] == task_id
    assert payload["task"]["status"] == "completed"


def test_dev_ops_read_endpoint_reports_cleanup_helper_for_python(tmp_path, monkeypatch) -> None:
    _scaffold_dev_root(tmp_path)
    py_path = tmp_path / "dev" / "goblin" / "tests" / "test_sample.py"
    py_path.write_text("print('ok')  \n", encoding="utf-8")
    client = _client(monkeypatch, tmp_path)

    read_response = client.get(
        "/api/dev/ops/read", params={"area": "goblin", "path": "tests/test_sample.py"}
    )
    assert read_response.status_code == 200
    payload = read_response.json()
    assert payload["format_helper"]["format"] == "python"
    assert payload["format_helper"]["helper_action"] == "cleanup"
    assert payload["format_helper"]["normalize_label"] == "Clean up Python"
    assert payload["format_helper"]["save_normalized_label"] == "Save cleaned Python"
