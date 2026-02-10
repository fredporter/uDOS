# Workflow UI Data Model

Contract for workflow UI (projects + tasks dashboard).

## Data Sources

- `GET /api/workflows/list`
- `GET /api/workflows/{workflow_id}`
- `GET /api/workflows/{workflow_id}/status`
- `GET /api/workflows/{workflow_id}/tasks`
- `GET /api/workflows/dashboard`
- `GET /api/workflows/tasks-dashboard`

## UI Model

```json
{
  "summary": {
    "projects": 0,
    "tasks": 0,
    "by_status": {
      "not-started": 0,
      "in-progress": 0,
      "completed": 0,
      "blocked": 0,
      "deferred": 0
    }
  },
  "projects": [
    {
      "id": 1,
      "name": "string",
      "description": "string",
      "status": "active",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ],
  "tasks": [
    {
      "id": 1,
      "project_id": 1,
      "project_name": "string",
      "title": "string",
      "description": "string",
      "status": "not-started",
      "priority": 5,
      "depends_on": "1,2",
      "file_refs": "string|null",
      "tags": "string",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "completed_at": "timestamp|null"
    }
  ]
}
```

## UI Notes

- Use `/api/workflows/dashboard` as the primary load for the Workflow landing page.
- Filter by `project_id`, `status`, or `priority`.
