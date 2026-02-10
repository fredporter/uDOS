# Service: wizard.tasks

## Purpose
Task scheduling and execution for Wizard workflows.

## UI Contract

See `tasks-ui.md` for the dashboard/UI data model.

## Endpoints (current + target)

- `GET /api/tasks/status`
- `GET /api/tasks/queue`
- `GET /api/tasks/runs`
- `GET /api/tasks/task/{task_id}`
- `POST /api/tasks/schedule`
- `POST /api/tasks/execute/{task_id}`
- `GET /api/tasks/calendar`
- `GET /api/tasks/gantt`
- `GET /api/tasks/indexer/summary`
- `GET /api/tasks/indexer/search`
- `GET /api/tasks/dashboard`

## Response (example)

```json
{
  "status": "ok",
  "task": {
    "id": "task-001",
    "name": "sync-catalog",
    "state": "queued"
  }
}
```

## MCP Tool Mapping

- `wizard.tasks.list`
- `wizard.tasks.get`
- `wizard.tasks.create`
- `wizard.tasks.run`
- `wizard.tasks.status`
- `wizard.tasks.queue`
- `wizard.tasks.runs`
- `wizard.tasks.task`
- `wizard.tasks.schedule`
- `wizard.tasks.execute`
- `wizard.tasks.calendar`
- `wizard.tasks.gantt`
- `wizard.tasks.indexer.summary`
- `wizard.tasks.indexer.search`
- `wizard.tasks.dashboard`
