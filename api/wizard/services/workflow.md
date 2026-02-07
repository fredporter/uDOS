# Service: wizard.workflow

## Purpose
Workflow orchestration (create, run, list workflows).

## UI Contract

See `workflow-ui.md` for the dashboard/UI data model.

## Endpoints (current + target)

- `GET /api/workflows/list`
- `POST /api/workflows/create`
- `POST /api/workflows/{workflow_id}/run`
- `GET /api/workflows/{workflow_id}`
- `GET /api/workflows/{workflow_id}/status`
- `GET /api/workflows/{workflow_id}/tasks`
- `GET /api/workflows/dashboard`
- `GET /api/workflows/tasks-dashboard`

## Response (example)

```json
{
  "status": "ok",
  "workflow": {
    "id": "wf-123",
    "name": "weekly-summary",
    "state": "idle"
  }
}
```

## MCP Tool Mapping

- `wizard.workflow.list`
- `wizard.workflow.get`
- `wizard.workflow.create`
- `wizard.workflow.run`
- `wizard.workflows.list`
- `wizard.workflows.create`
- `wizard.workflows.status`
- `wizard.workflows.tasks`
- `wizard.workflows.dashboard`
