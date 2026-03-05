CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    schedule TEXT DEFAULT 'daily',
    state TEXT DEFAULT 'plant',
    provider TEXT,
    enabled INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 5,
    need INTEGER DEFAULT 5,
    mission TEXT,
    objective TEXT,
    resource_cost INTEGER DEFAULT 1,
    requires_network INTEGER DEFAULT 0,
    kind TEXT,
    payload TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS task_runs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    state TEXT NOT NULL,
    result TEXT,
    output TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS task_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    state TEXT NOT NULL,
    scheduled_for TEXT NOT NULL,
    processed_at TEXT,
    created_at TEXT NOT NULL,
    priority INTEGER DEFAULT 5,
    need INTEGER DEFAULT 5,
    resource_cost INTEGER DEFAULT 1,
    requires_network INTEGER DEFAULT 0,
    defer_reason TEXT,
    defer_count INTEGER DEFAULT 0,
    backoff_seconds INTEGER DEFAULT 0,
    last_deferred_at TEXT,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scheduler_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_task_runs_task_id ON task_runs(task_id);
CREATE INDEX IF NOT EXISTS idx_task_runs_state ON task_runs(state);
CREATE INDEX IF NOT EXISTS idx_task_queue_state ON task_queue(state);
CREATE INDEX IF NOT EXISTS idx_task_queue_task_id ON task_queue(task_id);
