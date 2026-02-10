# Tasks UI Data Model

Contract for the scheduler UI (queue, runs, and indexer summary).

## Data Sources

- `GET /api/tasks/status`
- `GET /api/tasks/queue`
- `GET /api/tasks/runs`
- `GET /api/tasks/task/{task_id}`
- `GET /api/tasks/calendar`
- `GET /api/tasks/gantt`
- `GET /api/tasks/indexer/summary`
- `GET /api/tasks/indexer/search`
- `GET /api/tasks/dashboard`

## UI Model

```json
{
  "stats": {
    "total": 0,
    "enabled": 0,
    "disabled": 0,
    "last_tick": "timestamp|null"
  },
  "queue": [
    {
      "id": "task-id",
      "name": "string",
      "next_run": "timestamp",
      "enabled": true
    }
  ],
  "runs": [
    {
      "id": "run-id",
      "task_id": "task-id",
      "status": "success|failed",
      "started_at": "timestamp",
      "completed_at": "timestamp|null"
    }
  ],
  "indexer_summary": {
    "counts": {},
    "overdue": [],
    "high_priority": []
  }
}
```

## UI Notes

- `GET /api/tasks/dashboard` should drive the main scheduler view.
- Use `/api/tasks/indexer/search` for filtered queries (status, due, tag, priority).
